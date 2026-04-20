"""
Perception/monitoring layer - Enhanced with real system metrics.
"""

from __future__ import annotations

import os
import time
import psutil
import logging
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Callable

logger = logging.getLogger(__name__)


@dataclass
class EventRecord:
    """事件记录"""
    ts: str
    event_type: str
    status: str
    latency_ms: int = 0
    detail: Dict[str, str] = field(default_factory=dict)


@dataclass
class SystemMetrics:
    """系统指标"""
    event_count: int = 0
    error_rate: float = 0.0
    avg_latency_ms: float = 0.0
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    active_agents: int = 0
    queue_size: int = 0


class MetricsCollector:
    """
    指标收集器 - 支持多种数据源

    功能:
    - 基础事件追踪
    - 系统资源监控
    - 自定义指标钩子
    """

    def __init__(
        self,
        enable_system_metrics: bool = True,
        enable_external_hook: bool = False,
        external_hook_url: Optional[str] = None
    ):
        """
        初始化指标收集器

        Args:
            enable_system_metrics: 是否收集系统指标
            enable_external_hook: 是否启用外部钩子
            external_hook_url: 外部钩子 URL
        """
        self.enable_system_metrics = enable_system_metrics
        self.enable_external_hook = enable_external_hook
        self.external_hook_url = external_hook_url or os.getenv("METRICS_WEBHOOK_URL")

        self.events: deque = deque(maxlen=1000)
        self.custom_metrics: Dict[str, Any] = {}
        self.external_hook = None

        if self.enable_external_hook and self.external_hook_url:
            self._init_external_hook()

    def _init_external_hook(self):
        """初始化外部钩子"""
        try:
            import requests
            self.external_hook = requests.post
            logger.info(f"Initialized external metrics hook: {self.external_hook_url}")
        except ImportError:
            logger.warning("requests not installed, external hook disabled")

    def record_event(
        self,
        event_type: str,
        status: str,
        latency_ms: int = 0,
        detail: Optional[Dict[str, str]] = None
    ) -> None:
        """
        记录事件

        Args:
            event_type: 事件类型
            status: 状态 (success/error/timeout)
            latency_ms: 延迟 (毫秒)
            detail: 详细信息
        """
        event = EventRecord(
            ts=datetime.now(timezone.utc).isoformat(),
            event_type=event_type,
            status=status,
            latency_ms=latency_ms,
            detail=detail or {},
        )

        self.events.append(event)

        # 发送到外部钩子
        if self.external_hook:
            try:
                self.external_hook(
                    self.external_hook_url,
                    json={
                        "event_type": event_type,
                        "status": status,
                        "latency_ms": latency_ms,
                        "timestamp": event.ts
                    },
                    timeout=1
                )
            except Exception as e:
                logger.debug(f"External hook failed: {e}")

    def record_custom_metric(self, name: str, value: Any) -> None:
        """
        记录自定义指标

        Args:
            name: 指标名称
            value: 指标值
        """
        self.custom_metrics[name] = {
            "value": value,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    def get_metrics(self) -> SystemMetrics:
        """
        获取综合指标

        Returns:
            SystemMetrics: 系统指标
        """
        metrics = SystemMetrics()

        # 事件统计
        if self.events:
            events_list = list(self.events)
            count = len(events_list)
            errors = sum(1 for e in events_list if e.status != "success")
            total_latency = sum(e.latency_ms for e in events_list)

            metrics.event_count = count
            metrics.error_rate = errors / count if count > 0 else 0.0
            metrics.avg_latency_ms = total_latency / count if count > 0 else 0.0

        # 系统资源
        if self.enable_system_metrics:
            try:
                metrics.cpu_percent = psutil.cpu_percent(interval=0.1)
                metrics.memory_percent = psutil.virtual_memory().percent
            except Exception as e:
                logger.debug(f"Failed to get system metrics: {e}")

        # 自定义指标
        for name, data in self.custom_metrics.items():
            if name == "active_agents":
                metrics.active_agents = data.get("value", 0)
            elif name == "queue_size":
                metrics.queue_size = data.get("value", 0)

        return metrics

    def get_event_breakdown(self) -> Dict[str, int]:
        """获取事件类型分布"""
        breakdown: Dict[str, int] = defaultdict(int)
        for event in self.events:
            breakdown[event.event_type] += 1
        return dict(breakdown)

    def get_error_breakdown(self) -> Dict[str, int]:
        """获取错误类型分布"""
        errors = [e for e in self.events if e.status == "error"]
        breakdown: Dict[str, int] = defaultdict(int)
        for event in errors:
            error_type = event.detail.get("error_type", "unknown")
            breakdown[error_type] += 1
        return dict(breakdown)

    def get_latency_percentiles(self) -> Dict[str, float]:
        """获取延迟百分位"""
        if not self.events:
            return {"p50": 0.0, "p90": 0.0, "p99": 0.0}

        latencies = sorted([e.latency_ms for e in self.events])
        n = len(latencies)

        return {
            "p50": latencies[int(n * 0.5)] if n > 0 else 0.0,
            "p90": latencies[int(n * 0.9)] if n > 0 else 0.0,
            "p99": latencies[int(n * 0.99)] if n > 0 else 0.0,
        }

    def get_health_status(self) -> Dict[str, Any]:
        """获取健康状态"""
        metrics = self.get_metrics()

        # 简单的健康检查规则
        health = "healthy"
        issues = []

        if metrics.error_rate > 0.2:
            health = "unhealthy"
            issues.append(f"High error rate: {metrics.error_rate:.1%}")

        if metrics.avg_latency_ms > 3000:
            health = "degraded" if health == "healthy" else health
            issues.append(f"High latency: {metrics.avg_latency_ms:.0f}ms")

        if metrics.cpu_percent > 90:
            health = "degraded" if health == "healthy" else health
            issues.append(f"High CPU: {metrics.cpu_percent:.1f}%")

        if metrics.memory_percent > 90:
            health = "degraded" if health == "healthy" else health
            issues.append(f"High memory: {metrics.memory_percent:.1f}%")

        return {
            "status": health,
            "issues": issues,
            "metrics": {
                "error_rate": metrics.error_rate,
                "avg_latency_ms": metrics.avg_latency_ms,
                "cpu_percent": metrics.cpu_percent,
                "memory_percent": metrics.memory_percent,
            }
        }

    def clear_old_events(self, hours: int = 24) -> int:
        """清理旧事件"""
        cutoff = datetime.now(timezone.utc).timestamp() - hours * 3600
        original_count = len(self.events)

        while self.events and self.events[0].ts:
            try:
                event_ts = datetime.fromisoformat(self.events[0].ts).timestamp()
                if event_ts < cutoff:
                    self.events.popleft()
                else:
                    break
            except:
                self.events.popleft()

        cleared = original_count - len(self.events)
        if cleared > 0:
            logger.info(f"Cleared {cleared} old events")

        return cleared


# 保留向后兼容的别名
SystemMonitor = MetricsCollector
