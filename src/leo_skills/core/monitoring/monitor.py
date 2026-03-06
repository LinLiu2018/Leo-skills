# -*- coding: utf-8 -*-
"""
系统监控核心模块

整合指标收集、健康检查和告警
"""

import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from ...base import BaseSkill, SkillResult

from .metrics import MetricsCollector, MetricType
from .alerter import AlertManager, AlertLevel, AlertChannel
from .health import HealthChecker, HealthStatus, HealthCheckResult


class MonitorInterval(str, Enum):
    """监控间隔"""
    REAL_TIME = "realtime"      # 实时
    MINUTE = "minute"          # 每分钟
    HOURLY = "hourly"          # 每小时
    DAILY = "daily"             # 每天


@dataclass
class MonitorConfig:
    """监控配置"""
    interval: MonitorInterval = MonitorInterval.HOURLY
    alert_channels: List[AlertChannel] = field(default_factory=lambda: [AlertChannel.CONSOLE])
    cpu_threshold: float = 80.0
    memory_threshold: float = 85.0
    disk_threshold: float = 90.0
    success_rate_threshold: float = 95.0
    response_time_threshold: float = 30.0
    alert_on_degraded: bool = True
    auto_fix_enabled: bool = False


class SystemMonitor:
    """
    系统监控器

    整合以下能力：
    - 指标收集
    - 健康检查
    - 告警通知
    - 自动监控
    """

    def __init__(self, config: Optional[MonitorConfig] = None):
        self.config = config or MonitorConfig()

        # 子系统
        self.metrics = MetricsCollector()
        self.alerts = AlertManager()
        self.health = HealthChecker()

        # 监控线程
        self._monitor_thread: Optional[threading.Thread] = None
        self._running = False

        # 回调
        self._on_alert: Optional[Callable] = None
        self._on_health_change: Optional[Callable] = None

        # 状态
        self._last_health_status = HealthStatus.HEALTHY
        self._consecutive_failures = 0

    def get_actions(self) -> List[str]:
        """获取可用动作"""
        return [
            "health",           # 健康检查
            "metrics",          # 指标查询
            "alerts",           # 告警查询
            "send_alert",       # 发送告警
            "start",            # 启动监控
            "stop",             # 停止监控
            "status",          # 获取状态
            "configure",        # 配置监控
            "test_alerts",     # 测试告警通道
        ]

    def execute(
        self,
        action: str = "health",
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> SkillResult:
        """执行监控动作"""
        params = self._merge_params(action, context, kwargs)

        try:
            if action == "health":
                data = self.check_health()
            elif action == "metrics":
                data = self.get_metrics(**params)
            elif action == "alerts":
                data = self.get_alerts(**params)
            elif action == "send_alert":
                data = self.send_alert(**params)
            elif action == "start":
                data = self.start()
            elif action == "stop":
                data = self.stop()
            elif action == "status":
                data = self.get_status()
            elif action == "configure":
                data = self.configure(**params)
            elif action == "test_alerts":
                data = self.test_alerts()
            else:
                return SkillResult.fail(f"Unknown action: {action}")

            return SkillResult.ok(data=data)

        except Exception as e:
            return SkillResult.fail(str(e))

    def _merge_params(
        self,
        action: str,
        context: Optional[Dict],
        kwargs: Dict
    ) -> Dict:
        """合并参数"""
        params = {}

        if isinstance(context, dict):
            params.update(context.get("params", {}))
            params.update(context)

        params.update(kwargs)

        if "action" not in params:
            params["action"] = action

        return params

    # ========== 健康检查 ==========

    def check_health(self, component: Optional[str] = None) -> Dict[str, Any]:
        """执行健康检查"""
        results = self.health.check(component)

        # 检查状态变化
        overall = self.health.get_overall_status()
        if overall != self._last_health_status:
            self._on_health_status_change(overall)
            self._last_health_status = overall

        return {
            "overall_status": overall.value,
            "components": {
                name: result.to_dict()
                for name, result in results.items()
            }
        }

    def _on_health_status_change(self, new_status: HealthStatus):
        """健康状态变化回调"""
        if new_status == HealthStatus.UNHEALTHY:
            self.alerts.critical(
                title="系统健康状态异常",
                message=f"系统健康状态变为: {new_status.value}",
                source="SystemMonitor"
            )

        elif new_status == HealthStatus.DEGRADED and self.config.alert_on_degraded:
            self.alerts.warning(
                title="系统健康状态降级",
                message=f"系统健康状态变为: {new_status.value}",
                source="SystemMonitor"
            )

        # 触发回调
        if self._on_health_change:
            try:
                self._on_health_change(new_status)
            except Exception as e:
                print(f"[Monitor] Health change callback error: {e}")

    # ========== 指标 ==========

    def get_metrics(
        self,
        name: Optional[str] = None,
        metric_type: Optional[MetricType] = None,
        since_hours: int = 24,
        limit: int = 1000
    ) -> Dict[str, Any]:
        """查询指标"""
        since = datetime.now() - timedelta(hours=since_hours)

        metrics = self.metrics.query(
            name=name,
            metric_type=metric_type,
            since=since,
            limit=limit
        )

        return {
            "metrics": [m.to_dict() for m in metrics],
            "count": len(metrics),
            "since_hours": since_hours
        }

    def record_metric(self, name: str, value: float, metric_type: str = "gauge", **kwargs):
        """记录指标"""
        if metric_type == "counter":
            self.metrics.increment(name, value, kwargs.get("tags"))
        elif metric_type == "histogram":
            self.metrics.histogram(name, value, kwargs.get("tags"))
        else:
            self.metrics.gauge(name, value, kwargs.get("tags"), kwargs.get("unit", ""))

    # ========== 告警 ==========

    def get_alerts(
        self,
        level: Optional[str] = None,
        unresolved_only: bool = False,
        limit: int = 100
    ) -> Dict[str, Any]:
        """查询告警"""
        alert_level = None
        if level:
            alert_level = AlertLevel(level)

        alerts = self.alerts.get_alerts(
            level=alert_level,
            unresolved_only=unresolved_only,
            limit=limit
        )

        return {
            "alerts": [a.to_dict() for a in alerts],
            "count": len(alerts),
            "stats": self.alerts.get_stats()
        }

    def send_alert(
        self,
        level: str,
        title: str,
        message: str,
        source: str = "",
        channels: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """发送告警"""
        alert_level = AlertLevel(level)

        # 转换通道
        alert_channels = None
        if channels:
            alert_channels = [AlertChannel(c) for c in channels]

        alert = self.alerts.send_alert(
            level=alert_level,
            title=title,
            message=message,
            source=source,
            channels=alert_channels
        )

        # 触发回调
        if self._on_alert:
            try:
                self._on_alert(alert)
            except Exception as e:
                print(f"[Monitor] Alert callback error: {e}")

        return {
            "status": "success",
            "alert_id": alert.alert_id
        }

    # ========== 自动监控 ==========

    def start(self) -> Dict[str, Any]:
        """启动自动监控"""
        if self._running:
            return {"status": "warning", "message": "Monitor already running"}

        self._running = True

        # 启动监控线程
        interval_map = {
            MonitorInterval.REAL_TIME: 5,
            MonitorInterval.MINUTE: 60,
            MonitorInterval.HOURLY: 3600,
            MonitorInterval.DAILY: 86400
        }

        interval = interval_map.get(self.config.interval, 3600)

        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval,),
            daemon=True
        )
        self._monitor_thread.start()

        return {
            "status": "success",
            "message": "Monitor started",
            "interval_seconds": interval
        }

    def stop(self) -> Dict[str, Any]:
        """停止自动监控"""
        if not self._running:
            return {"status": "warning", "message": "Monitor not running"}

        self._running = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)

        return {"status": "success", "message": "Monitor stopped"}

    def _monitor_loop(self, interval: int):
        """监控循环"""
        while self._running:
            try:
                # 健康检查
                self.check_health()

                # 记录系统指标
                self._record_system_metrics()

                # 检查执行指标
                self._check_execution_metrics()

            except Exception as e:
                print(f"[Monitor] Monitor loop error: {e}")

            time.sleep(interval)

    def _record_system_metrics(self):
        """记录系统指标"""
        import psutil

        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        self.metrics.gauge("system.cpu_percent", cpu_percent, unit="%")

        if cpu_percent > self.config.cpu_threshold:
            self.alerts.warning(
                title="CPU使用率过高",
                message=f"CPU使用率为 {cpu_percent}%",
                source="SystemMonitor"
            )

        # 内存
        memory = psutil.virtual_memory()
        self.metrics.gauge("system.memory_percent", memory.percent, unit="%")

        if memory.percent > self.config.memory_threshold:
            self.alerts.warning(
                title="内存使用率过高",
                message=f"内存使用率为 {memory.percent}%",
                source="SystemMonitor"
            )

        # 磁盘
        disk = psutil.disk_usage('/')
        self.metrics.gauge("system.disk_percent", disk.percent, unit="%")

        if disk.percent > self.config.disk_threshold:
            self.alerts.critical(
                title="磁盘使用率过高",
                message=f"磁盘使用率为 {disk.percent}%",
                source="SystemMonitor"
            )

    def _check_execution_metrics(self):
        """检查执行指标"""
        # 检查成功率
        # 这里可以集成调度器的执行历史

        pass

    # ========== 配置 ==========

    def configure(
        self,
        interval: Optional[str] = None,
        cpu_threshold: Optional[float] = None,
        memory_threshold: Optional[float] = None,
        disk_threshold: Optional[float] = None,
        alert_on_degraded: Optional[bool] = None
    ) -> Dict[str, Any]:
        """配置监控"""
        if interval:
            self.config.interval = MonitorInterval(interval)
        if cpu_threshold:
            self.config.cpu_threshold = cpu_threshold
        if memory_threshold:
            self.config.memory_threshold = memory_threshold
        if disk_threshold:
            self.config.disk_threshold = disk_threshold
        if alert_on_degraded is not None:
            self.config.alert_on_degraded = alert_on_degraded

        return {
            "status": "success",
            "config": {
                "interval": self.config.interval.value,
                "cpu_threshold": self.config.cpu_threshold,
                "memory_threshold": self.config.memory_threshold,
                "disk_threshold": self.config.disk_threshold,
                "alert_on_degraded": self.config.alert_on_degraded
            }
        }

    # ========== 状态 ==========

    def get_status(self) -> Dict[str, Any]:
        """获取监控状态"""
        health = self.health.check()

        return {
            "status": "success",
            "running": self._running,
            "health": {
                "overall": self.health.get_overall_status().value,
                "components": len(health)
            },
            "alerts": self.alerts.get_stats(),
            "config": {
                "interval": self.config.interval.value,
                "cpu_threshold": self.config.cpu_threshold,
                "memory_threshold": self.config.memory_threshold,
                "disk_threshold": self.config.disk_threshold
            }
        }

    def test_alerts(self) -> Dict[str, Any]:
        """测试告警通道"""
        # 发送测试告警
        self.alerts.send_alert(
            level=AlertLevel.INFO,
            title="测试告警",
            message="这是一条测试告警，用于验证告警通道",
            source="SystemMonitor"
        )

        # 测试通道
        results = self.alerts.test_channels()

        return {
            "status": "success",
            "test_results": results
        }

    # ========== 回调设置 ==========

    def on_alert(self, callback: Callable):
        """设置告警回调"""
        self._on_alert = callback

    def on_health_change(self, callback: Callable):
        """设置健康状态变化回调"""
        self._on_health_change = callback
