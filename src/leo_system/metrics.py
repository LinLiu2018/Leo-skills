#!/usr/bin/env python3
"""
Leo System - 性能监控模块

提供性能追踪和监控功能。
"""
import functools
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, Optional

from .logger import get_logger

# 性能数据存储目录
METRICS_DIR = Path(__file__).parent.parent / "logs" / "metrics"
METRICS_DIR.mkdir(parents=True, exist_ok=True)

# 日志记录器
logger = get_logger(__name__)


class PerformanceMetrics:
    """性能指标收集器（带环形缓冲区，防止内存无限增长）"""

    MAX_RECORDS_PER_METRIC = 1000

    def __init__(self):
        self.metrics: Dict[str, list] = {}

    def record(self, name: str, duration: float, metadata: Optional[Dict] = None):
        """
        记录性能指标

        Args:
            name: 指标名称
            duration: 执行时长（秒）
            metadata: 额外的元数据
        """
        if name not in self.metrics:
            self.metrics[name] = []

        record = {
            "timestamp": datetime.now().isoformat(),
            "duration": duration,
            "metadata": metadata or {},
        }
        self.metrics[name].append(record)

        # 环形缓冲区：超过上限时截断旧记录
        if len(self.metrics[name]) > self.MAX_RECORDS_PER_METRIC:
            self.metrics[name] = self.metrics[name][-self.MAX_RECORDS_PER_METRIC:]

    def get_stats(self, name: str) -> Dict[str, Any]:
        """
        获取指标统计信息

        Args:
            name: 指标名称

        Returns:
            统计信息字典（平均值、最小值、最大值等）
        """
        if name not in self.metrics or not self.metrics[name]:
            return {}

        durations = [m["duration"] for m in self.metrics[name]]
        return {
            "count": len(durations),
            "avg": sum(durations) / len(durations),
            "min": min(durations),
            "max": max(durations),
            "total": sum(durations),
        }

    def save_to_file(self, filename: Optional[str] = None):
        """
        保存指标到文件

        Args:
            filename: 文件名（默认使用时间戳）
        """
        if not filename:
            filename = f"metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        filepath = METRICS_DIR / filename
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.metrics, f, indent=2, ensure_ascii=False)

        logger.info(f"Metrics saved to {filepath}")

    def clear(self):
        """清空所有指标"""
        self.metrics.clear()


# 全局指标收集器
_global_metrics = PerformanceMetrics()


def get_metrics() -> PerformanceMetrics:
    """获取全局指标收集器"""
    return _global_metrics


def track_time(func: Optional[Callable] = None, *, name: Optional[str] = None):
    """
    装饰器：追踪函数执行时间

    Args:
        func: 被装饰的函数
        name: 自定义指标名称（默认使用函数名）

    Usage:
        @track_time
        def my_function():
            pass

        @track_time(name="custom_name")
        def my_function():
            pass
    """

    def decorator(f: Callable) -> Callable:
        metric_name = name or f"{f.__module__}.{f.__name__}"

        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = f(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                _global_metrics.record(metric_name, duration)
                logger.debug(f"{metric_name} took {duration:.4f}s")

        return wrapper

    # 支持 @track_time 和 @track_time() 两种用法
    if func is None:
        return decorator
    else:
        return decorator(func)


class Timer:
    """
    上下文管理器：测量代码块执行时间

    Usage:
        with Timer("my_operation"):
            # 执行代码
            pass
    """

    def __init__(self, name: str, log_result: bool = True):
        """
        初始化计时器

        Args:
            name: 操作名称
            log_result: 是否记录到日志
        """
        self.name = name
        self.log_result = log_result
        self.start_time = None
        self.duration = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.duration = time.time() - self.start_time
        _global_metrics.record(self.name, self.duration)

        if self.log_result:
            logger.info(f"{self.name} took {self.duration:.4f}s")


def measure_time(name: str) -> Timer:
    """
    创建一个计时器上下文管理器

    Args:
        name: 操作名称

    Returns:
        Timer 实例

    Usage:
        with measure_time("my_operation"):
            # 执行代码
            pass
    """
    return Timer(name)


def get_performance_report() -> Dict[str, Any]:
    """
    获取性能报告

    Returns:
        包含所有指标统计信息的字典
    """
    metrics = get_metrics()
    report = {}

    for name in metrics.metrics.keys():
        report[name] = metrics.get_stats(name)

    return report


def print_performance_report():
    """打印性能报告到控制台"""
    report = get_performance_report()

    if not report:
        print("No performance metrics recorded.")
        return

    print("\n" + "=" * 80)
    print("Performance Report")
    print("=" * 80)

    for name, stats in sorted(report.items()):
        print(f"\n{name}:")
        print(f"  Count: {stats['count']}")
        print(f"  Avg:   {stats['avg']:.4f}s")
        print(f"  Min:   {stats['min']:.4f}s")
        print(f"  Max:   {stats['max']:.4f}s")
        print(f"  Total: {stats['total']:.4f}s")

    print("\n" + "=" * 80)
