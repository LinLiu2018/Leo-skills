"""
Leo Core Performance - 性能监控模块

提供性能指标收集、追踪功能。
"""

from __future__ import annotations

import asyncio
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, List, Optional
from uuid import uuid4

from leo_core.logging import get_logger

logger = get_logger(__name__)


# ============================================================
# 指标类型
# ============================================================

class MetricType(str, Enum):
    """指标类型"""
    COUNTER = "counter"           # 计数器
    GAUGE = "gauge"               # 仪表（当前值）
    HISTOGRAM = "histogram"       # 直方图
    TIMER = "timer"               # 计时器


# ============================================================
# 指标定义
# ============================================================

@dataclass
class Metric:
    """指标基类"""
    name: str
    description: str = ""
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class Counter(Metric):
    """计数器"""
    value: int = 0

    def increment(self, value: int = 1) -> None:
        self.value += value


@dataclass
class Gauge(Metric):
    """仪表"""
    value: float = 0.0

    def set(self, value: float) -> None:
        self.value = value

    def increment(self, value: float = 1.0) -> None:
        self.value += value

    def decrement(self, value: float = 1.0) -> None:
        self.value -= value


@dataclass
class Histogram(Metric):
    """直方图"""
    values: List[float] = field(default_factory=list)
    max_size: int = 1000

    def observe(self, value: float) -> None:
        self.values.append(value)
        if len(self.values) > self.max_size:
            self.values = self.values[-self.max_size:]

    @property
    def count(self) -> int:
        return len(self.values)

    @property
    def sum(self) -> float:
        return sum(self.values)

    @property
    def avg(self) -> float:
        return self.sum / self.count if self.count > 0 else 0

    @property
    def min(self) -> float:
        return min(self.values) if self.values else 0

    @property
    def max(self) -> float:
        return max(self.values) if self.values else 0


# ============================================================
# 性能监控器
# ============================================================

class PerformanceMonitor:
    """性能监控器"""

    def __init__(self):
        self._counters: Dict[str, Counter] = {}
        self._gauges: Dict[str, Gauge] = {}
        self._histograms: Dict[str, Histogram] = {}
        self._timers: Dict[str, List[float]] = defaultdict(list)

    # ---------- Counter 操作 ----------

    def counter(self, name: str, description: str = "", tags: Optional[Dict[str, str]] = None) -> Counter:
        """获取或创建计数器"""
        key = self._make_key(name, tags)
        if key not in self._counters:
            self._counters[key] = Counter(
                name=name,
                description=description,
                tags=tags or {}
            )
        return self._counters[key]

    def increment(self, name: str, value: int = 1, tags: Optional[Dict[str, str]] = None) -> None:
        """增加计数器"""
        counter = self.counter(name, tags=tags)
        counter.increment(value)

    # ---------- Gauge 操作 ----------

    def gauge(self, name: str, description: str = "", tags: Optional[Dict[str, str]] = None) -> Gauge:
        """获取或创建仪表"""
        key = self._make_key(name, tags)
        if key not in self._gauges:
            self._gauges[key] = Gauge(
                name=name,
                description=description,
                tags=tags or {}
            )
        return self._gauges[key]

    def set_gauge(self, name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        """设置仪表值"""
        gauge = self.gauge(name, tags=tags)
        gauge.set(value)

    # ---------- Histogram 操作 ----------

    def histogram(self, name: str, description: str = "", tags: Optional[Dict[str, str]] = None) -> Histogram:
        """获取或创建直方图"""
        key = self._make_key(name, tags)
        if key not in self._histograms:
            self._histograms[key] = Histogram(
                name=name,
                description=description,
                tags=tags or {}
            )
        return self._histograms[key]

    def observe(self, name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        """记录观测值"""
        hist = self.histogram(name, tags=tags)
        hist.observe(value)

    # ---------- Timer 操作 ----------

    def timer(self, name: str) -> float:
        """开始计时（返回装饰器）"""
        def decorator(func: Callable):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                start = time.perf_counter()
                try:
                    result = await func(*args, **kwargs)
                    duration = time.perf_counter() - start
                    self.record_duration(name, duration)
                    return result
                except Exception:
                    duration = time.perf_counter() - start
                    self.record_duration(name, duration)
                    raise

            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                start = time.perf_counter()
                try:
                    result = func(*args, **kwargs)
                    duration = time.perf_counter() - start
                    self.record_duration(name, duration)
                    return result
                except Exception:
                    duration = time.perf_counter() - start
                    self.record_duration(name, duration)
                    raise

            import asyncio
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            return sync_wrapper
        return decorator

    def record_duration(self, name: str, duration: float) -> None:
        """记录执行时间"""
        self._timers[name].append(duration)
        # 保持最大1000条
        if len(self._timers[name]) > 1000:
            self._timers[name] = self._timers[name][-1000:]
        self.observe(name, duration)

    # ---------- 统计操作 ----------

    def get_stats(self, name: Optional[str] = None) -> Dict[str, Any]:
        """获取统计信息"""
        if name:
            return self._get_metric_stats(name)

        # 汇总所有
        stats = {
            "counters": {},
            "gauges": {},
            "histograms": {},
            "timers": {},
        }

        for key, counter in self._counters.items():
            stats["counters"][key] = {"value": counter.value}

        for key, gauge in self._gauges.items():
            stats["gauges"][key] = {"value": gauge.value}

        for key, hist in self._histograms.items():
            if hist.count > 0:
                stats["histograms"][key] = {
                    "count": hist.count,
                    "sum": hist.sum,
                    "avg": hist.avg,
                    "min": hist.min,
                    "max": hist.max,
                }

        for name, durations in self._timers.items():
            if durations:
                stats["timers"][name] = {
                    "count": len(durations),
                    "avg": sum(durations) / len(durations),
                    "min": min(durations),
                    "max": max(durations),
                }

        return stats

    def _get_metric_stats(self, name: str) -> Dict[str, Any]:
        """获取指定指标统计"""
        result = {}

        # 检查 histogram
        for key, hist in self._histograms.items():
            if name in key and hist.count > 0:
                result["histogram"] = {
                    "count": hist.count,
                    "avg": hist.avg,
                    "min": hist.min,
                    "max": hist.max,
                }

        # 检查 timer
        if name in self._timers:
            durations = self._timers[name]
            result["timer"] = {
                "count": len(durations),
                "avg": sum(durations) / len(durations),
                "min": min(durations),
                "max": max(durations),
            }

        return result

    def reset(self) -> None:
        """重置所有指标"""
        self._counters.clear()
        self._gauges.clear()
        self._histograms.clear()
        self._timers.clear()

    # ---------- 辅助方法 ----------

    def _make_key(self, name: str, tags: Optional[Dict[str, str]] = None) -> str:
        """生成指标键"""
        if not tags:
            return name
        tag_str = ",".join(f"{k}={v}" for k, v in sorted(tags.items()))
        return f"{name}{{{tag_str}}}"


# ============================================================
# 性能追踪器
# ============================================================

@dataclass
class Trace:
    """追踪记录"""
    trace_id: str
    name: str
    start_time: float
    end_time: float = 0
    duration: float = 0
    status: str = "pending"
    tags: Dict[str, Any] = field(default_factory=dict)
    spans: List["Span"] = field(default_factory=list)


@dataclass
class Span:
    """跨度"""
    span_id: str
    name: str
    start_time: float
    end_time: float = 0
    duration: float = 0
    tags: Dict[str, Any] = field(default_factory=dict)


class Tracer:
    """追踪器"""

    def __init__(self, max_traces: int = 1000):
        self.max_traces = max_traces
        self._traces: Dict[str, Trace] = {}
        self._current_spans: Dict[str, Span] = {}

    def start_trace(self, name: str, tags: Optional[Dict[str, Any]] = None) -> str:
        """开始追踪"""
        trace_id = str(uuid4())
        self._traces[trace_id] = Trace(
            trace_id=trace_id,
            name=name,
            start_time=time.perf_counter(),
            tags=tags or {}
        )
        return trace_id

    def end_trace(self, trace_id: str, status: str = "ok") -> None:
        """结束追踪"""
        if trace_id not in self._traces:
            return

        trace = self._traces[trace_id]
        trace.end_time = time.perf_counter()
        trace.duration = trace.end_time - trace.start_time
        trace.status = status

    def start_span(self, trace_id: str, name: str, tags: Optional[Dict[str, Any]] = None) -> str:
        """开始跨度"""
        span_id = str(uuid4())
        self._current_spans[span_id] = Span(
            span_id=span_id,
            name=name,
            start_time=time.perf_counter(),
            tags=tags or {}
        )
        return span_id

    def end_span(self, span_id: str) -> None:
        """结束跨度"""
        if span_id not in self._current_spans:
            return

        span = self._current_spans[span_id]
        span.end_time = time.perf_counter()
        span.duration = span.end_time - span.start_time

        # 找到对应的 trace
        for trace in self._traces.values():
            if trace.trace_id == span_id:
                trace.spans.append(span)
                break

        del self._current_spans[span_id]

    def get_trace(self, trace_id: str) -> Optional[Trace]:
        """获取追踪"""
        return self._traces.get(trace_id)

    def get_traces(self, limit: int = 50) -> List[Trace]:
        """获取追踪列表"""
        traces = list(self._traces.values())
        traces.sort(key=lambda t: t.start_time, reverse=True)
        return traces[:limit]


# ============================================================
# 上下文管理器
# ============================================================

class TimerContext:
    """计时上下文管理器"""

    def __init__(self, monitor: PerformanceMonitor, name: str, tags: Optional[Dict[str, str]] = None):
        self.monitor = monitor
        self.name = name
        self.tags = tags
        self.start_time = 0

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.perf_counter() - self.start_time
        self.monitor.record_duration(self.name, duration)

    async def __aenter__(self):
        self.start_time = time.perf_counter()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        duration = time.perf_counter() - self.start_time
        self.monitor.record_duration(self.name, duration)


# ============================================================
# 全局实例
# ============================================================

_performance_monitor: Optional[PerformanceMonitor] = None
_tracer: Optional[Tracer] = None


def get_performance_monitor() -> PerformanceMonitor:
    """获取全局性能监控器"""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor


def get_tracer() -> Tracer:
    """获取全局追踪器"""
    global _tracer
    if _tracer is None:
        _tracer = Tracer()
    return _tracer


# ============================================================
# 便捷装饰器
# ============================================================

def track_performance(name: str, tags: Optional[Dict[str, str]] = None):
    """性能追踪装饰器"""
    def decorator(func: Callable):
        monitor = get_performance_monitor()

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start = time.perf_counter()
            try:
                result = await func(*args, **kwargs)
                duration = time.perf_counter() - start
                monitor.record_duration(name, duration)
                monitor.increment(f"{name}.success", tags=tags)
                return result
            except Exception as e:
                duration = time.perf_counter() - start
                monitor.record_duration(name, duration)
                monitor.increment(f"{name}.error", tags=tags)
                raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                duration = time.perf_counter() - start
                monitor.record_duration(name, duration)
                monitor.increment(f"{name}.success", tags=tags)
                return result
            except Exception as e:
                duration = time.perf_counter() - start
                monitor.record_duration(name, duration)
                monitor.increment(f"{name}.error", tags=tags)
                raise

        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator
