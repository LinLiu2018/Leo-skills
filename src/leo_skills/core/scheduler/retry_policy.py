# -*- coding: utf-8 -*-
"""
重试策略模块

定义各种重试策略和退避算法
"""

import time
import random
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Optional


class RetryStrategy(ABC):
    """重试策略基类"""

    @abstractmethod
    def should_retry(self, attempt: int, error: Exception) -> bool:
        """判断是否应该重试"""
        pass

    @abstractmethod
    def get_delay(self, attempt: int) -> float:
        """获取延迟时间(秒)"""
        pass


@dataclass
class RetryPolicy:
    """重试策略配置"""
    enabled: bool = True
    max_retries: int = 3
    backoff_multiplier: float = 2.0
    initial_delay: float = 1.0
    max_delay: float = 60.0
    jitter: bool = True
    retry_on_exceptions: tuple = (Exception,)

    def should_retry(self, attempt: int, error: Exception) -> bool:
        """判断是否应该重试"""
        if not self.enabled:
            return False

        if attempt >= self.max_retries:
            return False

        # 检查异常类型
        if not isinstance(error, self.retry_on_exceptions):
            return False

        return True

    def get_delay(self, attempt: int) -> float:
        """计算延迟时间"""
        delay = min(
            self.initial_delay * (self.backoff_multiplier ** attempt),
            self.max_delay
        )

        # 添加随机抖动
        if self.jitter:
            delay = delay * (0.5 + random.random() * 0.5)

        return delay


class ExponentialBackoff(RetryStrategy):
    """指数退避策略"""

    def __init__(
        self,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        multiplier: float = 2.0,
        jitter: bool = True
    ):
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.multiplier = multiplier
        self.jitter = jitter

    def should_retry(self, attempt: int, error: Exception) -> bool:
        """最多重试5次"""
        return attempt < 5

    def get_delay(self, attempt: int) -> float:
        """计算延迟: base * multiplier^attempt"""
        delay = min(
            self.base_delay * (self.multiplier ** attempt),
            self.max_delay
        )

        if self.jitter:
            delay = delay * (0.5 + random.random() * 0.5)

        return delay


class LinearBackoff(RetryStrategy):
    """线性退避策略"""

    def __init__(self, increment: float = 1.0, max_delay: float = 30.0):
        self.increment = increment
        self.max_delay = max_delay

    def should_retry(self, attempt: int, error: Exception) -> bool:
        return attempt < 10

    def get_delay(self, attempt: int) -> float:
        return min(self.increment * attempt, self.max_delay)


class ConstantBackoff(RetryStrategy):
    """固定延迟策略"""

    def __init__(self, delay: float = 1.0):
        self.delay = delay

    def should_retry(self, attempt: int, error: Exception) -> bool:
        return attempt < 3

    def get_delay(self, attempt: int) -> float:
        return self.delay


class FibonacciBackoff(RetryStrategy):
    """斐波那契退避策略"""

    def __init__(self, base: float = 1.0, max_delay: float = 60.0):
        self.base = base
        self.max_delay = max_delay
        self._fib_cache = {0: 1, 1: 1}

    def _fib(self, n: int) -> int:
        """计算斐波那契数"""
        if n in self._fib_cache:
            return self._fib_cache[n]
        self._fib_cache[n] = self._fib(n - 1) + self._fib(n - 2)
        return self._fib_cache[n]

    def should_retry(self, attempt: int, error: Exception) -> bool:
        return attempt < 8

    def get_delay(self, attempt: int) -> float:
        fib_val = self._fib(attempt)
        delay = min(self.base * fib_val, self.max_delay)
        return delay * (0.5 + random.random() * 0.5)


class RetryExecutor:
    """重试执行器"""

    def __init__(self, strategy: RetryStrategy = None):
        self.strategy = strategy or ExponentialBackoff()

    def execute(
        self,
        func: Callable,
        *args,
        attempt: int = 0,
        **kwargs
    ) -> Any:
        """
        执行函数，支持重试

        Args:
            func: 要执行的函数
            attempt: 当前重试次数
            *args, **kwargs: 函数参数

        Returns:
            函数返回值

        Raises:
            最后一次执行的异常
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if not self.strategy.should_retry(attempt, e):
                raise

            delay = self.strategy.get_delay(attempt)
            print(f"[Retry] Attempt {attempt + 1} failed: {e}. Retrying in {delay:.2f}s...")

            time.sleep(delay)
            return self.execute(func, *args, attempt=attempt + 1, **kwargs)

    async def execute_async(
        self,
        func: Callable,
        *args,
        attempt: int = 0,
        **kwargs
    ) -> Any:
        """异步版本"""
        import asyncio

        try:
            return await func(*args, **kwargs)
        except Exception as e:
            if not self.strategy.should_retry(attempt, e):
                raise

            delay = self.strategy.get_delay(attempt)
            print(f"[Retry] Attempt {attempt + 1} failed: {e}. Retrying in {delay:.2f}s...")

            await asyncio.sleep(delay)
            return await self.execute_async(func, *args, attempt=attempt + 1, **kwargs)


class CircuitBreaker:
    """熔断器"""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = "closed"  # closed, open, half_open

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """执行函数，带熔断保护"""
        if self.state == "open":
            if self._should_attempt_reset():
                self.state = "half_open"
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise

    def _should_attempt_reset(self) -> bool:
        """检查是否应该尝试恢复"""
        if self.last_failure_time:
            elapsed = (datetime.now() - self.last_failure_time).total_seconds()
            return elapsed >= self.recovery_timeout
        return False

    def _on_success(self) -> None:
        """成功回调"""
        self.failure_count = 0
        self.state = "closed"

    def _on_failure(self) -> None:
        """失败回调"""
        self.failure_count += 1
        self.last_failure_time = datetime()

        if self.failure_count >= self.failure_threshold:
            self.state = "open"


class RetryContext:
    """重试上下文"""

    def __init__(
        self,
        max_retries: int = 3,
        strategy: RetryStrategy = None
    ):
        self.max_retries = max_retries
        self.strategy = strategy or ExponentialBackoff()
        self.attempt = 0
        self.errors = []
        self.start_time: Optional[datetime] = None

    def __enter__(self):
        self.start_time = datetime.now()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val:
            self.errors.append({
                "attempt": self.attempt,
                "error": str(exc_val),
                "time": datetime.now().isoformat()
            })

    def retry(self, func: Callable, *args, **kwargs) -> Any:
        """执行重试"""
        self.attempt += 1

        try:
            return func(*args, **kwargs)
        except Exception as e:
            if not self.strategy.should_retry(self.attempt, e):
                raise

            delay = self.strategy.get_delay(self.attempt)
            print(f"[RetryContext] Attempt {self.attempt} failed. Retrying in {delay:.2f}s...")
            time.sleep(delay)

            return self.retry(func, *args, **kwargs)

    def get_report(self) -> dict:
        """获取重试报告"""
        return {
            "total_attempts": self.attempt,
            "errors": self.errors,
            "duration_seconds": (
                (datetime.now() - self.start_time).total_seconds()
                if self.start_time else 0
            )
        }
