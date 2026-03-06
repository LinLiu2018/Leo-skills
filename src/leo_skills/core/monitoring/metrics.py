# -*- coding: utf-8 -*-
"""
指标收集模块

收集和管理系统指标
"""

import json
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class MetricType(str, Enum):
    """指标类型"""
    COUNTER = "counter"           # 计数器
    GAUGE = "gauge"               # 仪表值
    HISTOGRAM = "histogram"       # 直方图
    TIMER = "timer"                # 计时器


@dataclass
class Metric:
    """指标数据"""
    name: str
    value: float
    metric_type: MetricType
    timestamp: datetime = field(default_factory=datetime.now)
    unit: str = ""
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "value": self.value,
            "type": self.metric_type.value,
            "timestamp": self.timestamp.isoformat(),
            "unit": self.unit,
            "tags": self.tags,
            "metadata": self.metadata
        }


class MetricsCollector:
    """
    指标收集器

    收集和存储各类指标数据
    """

    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = storage_path or ".leo_monitor/metrics"
        self._metrics: List[Metric] = []
        self._counters: Dict[str, float] = {}
        self._gauges: Dict[str, float] = {}
        self._timers: Dict[str, List[float]] = {}

        # 确保存储目录存在
        Path(self.storage_path).mkdir(parents=True, exist_ok=True)

    # ========== 指标收集 ==========

    def increment(self, name: str, value: float = 1, tags: Optional[Dict] = None):
        """增加计数器"""
        key = self._make_key(name, tags)
        self._counters[key] = self._counters.get(key, 0) + value

        metric = Metric(
            name=name,
            value=self._counters[key],
            metric_type=MetricType.COUNTER,
            tags=tags or {}
        )
        self._metrics.append(metric)

    def decrement(self, name: str, value: float = 1, tags: Optional[Dict] = None):
        """减少计数器"""
        self.increment(name, -value, tags)

    def gauge(self, name: str, value: float, tags: Optional[Dict] = None, unit: str = ""):
        """设置仪表值"""
        key = self._make_key(name, tags)
        self._gauges[key] = value

        metric = Metric(
            name=name,
            value=value,
            metric_type=MetricType.GAUGE,
            tags=tags or {},
            unit=unit
        )
        self._metrics.append(metric)

    def histogram(self, name: str, value: float, tags: Optional[Dict] = None):
        """记录直方图值"""
        key = self._make_key(name, tags)
        if key not in self._timers:
            self._timers[key] = []
        self._timers[key].append(value)

        metric = Metric(
            name=name,
            value=value,
            metric_type=MetricType.HISTOGRAM,
            tags=tags or {}
        )
        self._metrics.append(metric)

    def timing(self, name: str, duration_ms: float, tags: Optional[Dict] = None):
        """记录计时"""
        self.histogram(name, duration_ms, tags)

    def timing_start(self, name: str) -> str:
        """开始计时"""
        return f"{name}:{time.time()}"

    def timing_end(self, timer_id: str):
        """结束计时"""
        name, start_time = timer_id.rsplit(":", 1)
        duration_ms = (time.time() - float(start_time)) * 1000
        self.timing(name, duration_ms)

    # ========== 上下文管理器 ==========

    def timer(self, name: str, tags: Optional[Dict] = None):
        """计时上下文管理器"""
        return TimerContext(self, name, tags)

    # ========== 查询 ==========

    def get_counter(self, name: str, tags: Optional[Dict] = None) -> float:
        """获取计数器值"""
        key = self._make_key(name, tags)
        return self._counters.get(key, 0)

    def get_gauge(self, name: str, tags: Optional[Dict] = None) -> float:
        """获取仪表值"""
        key = self._make_key(name, tags)
        return self._gauges.get(key, 0)

    def get_histogram_stats(self, name: str, tags: Optional[Dict] = None) -> Dict:
        """获取直方图统计"""
        key = self._make_key(name, tags)
        values = self._timers.get(key, [])

        if not values:
            return {"count": 0, "sum": 0, "avg": 0, "min": 0, "max": 0}

        return {
            "count": len(values),
            "sum": sum(values),
            "avg": sum(values) / len(values),
            "min": min(values),
            "max": max(values),
            "p50": self._percentile(values, 50),
            "p95": self._percentile(values, 95),
            "p99": self._percentile(values, 99)
        }

    def query(
        self,
        name: Optional[str] = None,
        metric_type: Optional[MetricType] = None,
        since: Optional[datetime] = None,
        limit: int = 1000
    ) -> List[Metric]:
        """查询指标"""
        results = self._metrics

        if name:
            results = [m for m in results if m.name == name]
        if metric_type:
            results = [m for m in results if m.metric_type == metric_type]
        if since:
            results = [m for m in results if m.timestamp >= since]

        return results[-limit:]

    def get_recent(self, limit: int = 100) -> List[Metric]:
        """获取最近的指标"""
        return self._metrics[-limit:]

    # ========== 持久化 ==========

    def save(self):
        """保存指标到文件"""
        if not self._metrics:
            return

        # 按日期保存
        date_str = datetime.now().strftime("%Y%m%d")
        file_path = Path(self.storage_path) / f"metrics_{date_str}.json"

        # 读取现有数据
        existing = []
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    existing = json.load(f)
            except:
                pass

        # 添加新指标
        existing.extend([m.to_dict() for m in self._metrics[-100:]])

        # 保存
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(existing[-10000:], f, indent=2, ensure_ascii=False)

        # 清理旧文件
        self._cleanup_old_files()

    def load(self, date: Optional[str] = None):
        """加载指定日期的指标"""
        date_str = date or datetime.now().strftime("%Y%m%d")
        file_path = Path(self.storage_path) / f"metrics_{date_str}.json"

        if not file_path.exists():
            return []

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return [
            Metric(
                name=m["name"],
                value=m["value"],
                metric_type=MetricType(m["type"]),
                timestamp=datetime.fromisoformat(m["timestamp"]),
                unit=m.get("unit", ""),
                tags=m.get("tags", {}),
                metadata=m.get("metadata", {})
            )
            for m in data
        ]

    # ========== 辅助方法 ==========

    def _make_key(self, name: str, tags: Optional[Dict]) -> str:
        """生成指标键"""
        if not tags:
            return name
        tag_str = ",".join(f"{k}={v}" for k, v in sorted(tags.items()))
        return f"{name}{{{tag_str}}}"

    def _percentile(self, values: List[float], p: int) -> float:
        """计算百分位数"""
        if not values:
            return 0
        sorted_values = sorted(values)
        index = int(len(sorted_values) * p / 100)
        return sorted_values[min(index, len(sorted_values) - 1)]

    def _cleanup_old_files(self):
        """清理旧的指标文件"""
        metrics_dir = Path(self.storage_path)
        if not metrics_dir.exists():
            return

        # 保留最近7天
        import time
        cutoff = time.time() - (7 * 24 * 60 * 60)

        for file in metrics_dir.glob("metrics_*.json"):
            if file.stat().st_mtime < cutoff:
                try:
                    file.unlink()
                except:
                    pass

    def clear(self):
        """清空内存指标"""
        self._metrics.clear()
        self._counters.clear()
        self._gauges.clear()
        self._timers.clear()


class TimerContext:
    """计时上下文管理器"""

    def __init__(self, collector: MetricsCollector, name: str, tags: Optional[Dict]):
        self.collector = collector
        self.name = name
        self.tags = tags
        self.start_time = time.time()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration_ms = (time.time() - self.start_time) * 1000
        self.collector.timing(self.name, duration_ms, self.tags)


# 全局指标收集器
_global_collector: Optional[MetricsCollector] = None


def get_metrics_collector() -> MetricsCollector:
    """获取全局指标收集器"""
    global _global_collector
    if _global_collector is None:
        _global_collector = MetricsCollector()
    return _global_collector
