# -*- coding: utf-8 -*-
"""
故障自动检测模块

实时检测系统异常
"""

import traceback
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


class FaultType(str, Enum):
    """故障类型"""
    TIMEOUT = "timeout"
    API_ERROR = "api_error"
    NETWORK_ERROR = "network_error"
    AUTH_ERROR = "auth_error"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    CONFIG_ERROR = "config_error"
    DEPENDENCY_ERROR = "dependency_error"
    UNKNOWN_ERROR = "unknown_error"


class FaultSeverity(str, Enum):
    """故障严重程度"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class FaultReport:
    """故障报告"""
    fault_id: str
    fault_type: FaultType
    severity: FaultSeverity
    message: str
    source: str
    timestamp: datetime = field(default_factory=datetime.now)
    details: Dict[str, Any] = field(default_factory=dict)
    stack_trace: str = ""
    recoverable: bool = True

    def to_dict(self) -> Dict:
        return {
            "fault_id": self.fault_id,
            "fault_type": self.fault_type.value,
            "severity": self.severity.value,
            "message": self.message,
            "source": self.source,
            "timestamp": self.timestamp.isoformat(),
            "details": self.details,
            "stack_trace": self.stack_trace,
            "recoverable": self.recoverable
        }


class FaultDetector:
    """
    故障检测器

    功能：
    - 异常模式识别
    - 阈值监控
    - 趋势预测
    - 故障分类
    """

    def __init__(self):
        self.fault_history: List[FaultReport] = []
        self.fault_count = 0
        self.fault_handlers: Dict[FaultType, Callable] = {}

    # ========== 故障检测 ==========

    def detect_execution_failure(
        self,
        result: Any,
        context: Optional[Dict] = None
    ) -> Optional[FaultReport]:
        """
        检测执行失败

        Args:
            result: 执行结果
            context: 上下文信息

        Returns:
            故障报告，如果没有问题则返回 None
        """
        # 检查是否为异常
        if isinstance(result, Exception):
            return self._create_fault_report(
                fault_type=self._classify_exception(result),
                message=str(result),
                source=context.get("source", "unknown") if context else "unknown",
                details=context or {},
                exception=result
            )

        # 检查错误结果
        if isinstance(result, dict):
            if result.get("status") == "error":
                error_msg = result.get("error", "Unknown error")
                return self._create_fault_report(
                    fault_type=FaultType.API_ERROR,
                    message=error_msg,
                    source=context.get("source", "api") if context else "api",
                    details=context or {}
                )

        return None

    def detect_timeout(
        self,
        operation: str,
        duration_ms: int,
        threshold_ms: int = 30000
    ) -> Optional[FaultReport]:
        """检测超时"""
        if duration_ms > threshold_ms:
            return self._create_fault_report(
                fault_type=FaultType.TIMEOUT,
                message=f"Operation '{operation}' timeout after {duration_ms}ms",
                source=operation,
                details={
                    "duration_ms": duration_ms,
                    "threshold_ms": threshold_ms
                }
            )

        return None

    def detect_performance_degradation(
        self,
        current_metrics: Dict[str, float],
        baseline_metrics: Dict[str, float],
        threshold_percent: float = 20.0
    ) -> List[FaultReport]:
        """
        检测性能下降

        Args:
            current_metrics: 当前指标
            baseline_metrics: 基准指标
            threshold_percent: 下降阈值百分比

        Returns:
            故障报告列表
        """
        faults = []

        for metric_name in current_metrics:
            if metric_name not in baseline_metrics:
                continue

            current = current_metrics[metric_name]
            baseline = baseline_metrics[metric_name]

            if baseline == 0:
                continue

            # 计算下降百分比
            degradation = ((baseline - current) / baseline) * 100

            # 判断是否超过阈值
            # 某些指标下降是问题（如成功率），某些指标上升是问题（如延迟）
            is_problem = False
            if "rate" in metric_name or "success" in metric_name:
                # 成功率下降是问题
                is_problem = degradation > threshold_percent
            elif "time" in metric_name or "latency" in metric_name:
                # 延迟上升是问题
                is_problem = degradation < -threshold_percent

            if is_problem:
                fault = self._create_fault_report(
                    fault_type=FaultType.RESOURCE_EXHAUSTION,
                    message=f"Performance degradation detected for {metric_name}: {degradation:.1f}%",
                    source=metric_name,
                    details={
                        "metric": metric_name,
                        "current": current,
                        "baseline": baseline,
                        "degradation_percent": degradation
                    }
                )
                faults.append(fault)

        return faults

    def detect_resource_exhaustion(
        self,
        cpu_percent: float,
        memory_percent: float,
        disk_percent: float
    ) -> List[FaultReport]:
        """检测资源耗尽"""
        faults = []

        if cpu_percent > 90:
            faults.append(self._create_fault_report(
                fault_type=FaultType.RESOURCE_EXHAUSTION,
                severity=FaultSeverity.HIGH,
                message=f"CPU usage critical: {cpu_percent}%",
                source="system",
                details={"cpu_percent": cpu_percent}
            ))

        if memory_percent > 90:
            faults.append(self._create_fault_report(
                fault_type=FaultType.RESOURCE_EXHAUSTION,
                severity=FaultSeverity.CRITICAL,
                message=f"Memory usage critical: {memory_percent}%",
                source="system",
                details={"memory_percent": memory_percent}
            ))

        if disk_percent > 95:
            faults.append(self._create_fault_report(
                fault_type=FaultType.RESOURCE_EXHAUSTION,
                severity=FaultSeverity.CRITICAL,
                message=f"Disk space critical: {disk_percent}%",
                source="system",
                details={"disk_percent": disk_percent}
            ))

        return faults

    def predict_failure(
        self,
        metric_history: List[Dict[str, float]],
        threshold: float = 2.0
    ) -> Optional[FaultReport]:
        """
        预测潜在故障

        Args:
            metric_history: 指标历史
            threshold: 异常阈值（标准差倍数）

        Returns:
            预测的故障报告
        """
        if len(metric_history) < 5:
            return None

        # 提取错误率
        error_rates = [
            m.get("error_rate", 0)
            for m in metric_history
        ]

        # 计算均值和标准差
        mean = sum(error_rates) / len(error_rates)
        variance = sum((x - mean) ** 2 for x in error_rates) / len(error_rates)
        std = variance ** 0.5

        # 预测趋势
        recent = error_rates[-3:]
        trend = sum(recent) / len(recent) - mean

        # 如果趋势上升且超过阈值
        if trend > threshold * std:
            return self._create_fault_report(
                fault_type=FaultType.UNKNOWN_ERROR,
                severity=FaultSeverity.MEDIUM,
                message=f"Failure rate trend increasing: +{trend:.2f} errors/hour",
                source="prediction",
                details={
                    "mean_error_rate": mean,
                    "trend": trend,
                    "std": std,
                    "recent_rates": recent
                },
                recoverable=True
            )

        return None

    # ========== 异常分类 ==========

    def _classify_exception(self, error: Exception) -> FaultType:
        """分类异常类型"""
        error_msg = str(error).lower()
        error_type = type(error).__name__

        # 根据错误类型和消息分类
        if "timeout" in error_msg or error_type == "TimeoutError":
            return FaultType.TIMEOUT

        if "api" in error_msg or "request" in error_msg:
            return FaultType.API_ERROR

        if "network" in error_msg or "connection" in error_msg:
            return FaultType.NETWORK_ERROR

        if "auth" in error_msg or "unauthorized" in error_msg or "401" in error_msg:
            return FaultType.AUTH_ERROR

        if "import" in error_msg or "module" in error_msg or "no module" in error_msg:
            return FaultType.DEPENDENCY_ERROR

        if "config" in error_msg or "setting" in error_msg:
            return FaultType.CONFIG_ERROR

        if "memory" in error_msg or "out of memory" in error_msg:
            return FaultType.RESOURCE_EXHAUSTION

        return FaultType.UNKNOWN_ERROR

    def _create_fault_report(
        self,
        fault_type: FaultType,
        message: str,
        source: str,
        details: Dict[str, Any],
        severity: FaultSeverity = FaultSeverity.MEDIUM,
        exception: Optional[Exception] = None,
        recoverable: bool = True
    ) -> FaultReport:
        """创建故障报告"""
        self.fault_count += 1

        stack_trace = ""
        if exception:
            try:
                stack_trace = "".join(traceback.format_exception(
                    type(exception), exception, exception.__traceback__
                ))
            except:
                pass

        fault = FaultReport(
            fault_id=f"fault_{self.fault_count:08d}",
            fault_type=fault_type,
            severity=severity,
            message=message,
            source=source,
            details=details,
            stack_trace=stack_trace,
            recoverable=recoverable
        )

        # 保存到历史
        self.fault_history.append(fault)

        # 限制历史大小
        if len(self.fault_history) > 1000:
            self.fault_history = self.fault_history[-500:]

        return fault

    # ========== 查询 ==========

    def get_recent_faults(
        self,
        since: Optional[datetime] = None,
        fault_type: Optional[FaultType] = None,
        limit: int = 100
    ) -> List[FaultReport]:
        """查询最近的故障"""
        faults = self.fault_history

        if since:
            faults = [f for f in faults if f.timestamp >= since]

        if fault_type:
            faults = [f for f in faults if f.fault_type == fault_type]

        return faults[-limit:]

    def get_fault_stats(
        self,
        since: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """获取故障统计"""
        faults = self.fault_history
        if since:
            faults = [f for f in faults if f.timestamp >= since]

        total = len(faults)

        # 按类型统计
        by_type = {}
        for ft in FaultType:
            count = sum(1 for f in faults if f.fault_type == ft)
            by_type[ft.value] = count

        # 按严重程度统计
        by_severity = {}
        for sev in FaultSeverity:
            count = sum(1 for f in faults if f.severity == sev)
            by_severity[sev.value] = count

        # 恢复率
        recoverable = sum(1 for f in faults if f.recoverable)

        return {
            "total": total,
            "by_type": by_type,
            "by_severity": by_severity,
            "recoverable_count": recoverable,
            "recovery_rate": round(recoverable / total * 100, 2) if total > 0 else 0
        }

    # ========== 处理器 ==========

    def register_handler(
        self,
        fault_type: FaultType,
        handler: Callable[[FaultReport], Any]
    ):
        """注册故障处理器"""
        self.fault_handlers[fault_type] = handler

    def handle_fault(self, fault: FaultReport):
        """处理故障"""
        handler = self.fault_handlers.get(fault.fault_type)
        if handler:
            try:
                handler(fault)
            except Exception as e:
                print(f"[FaultDetector] Handler error: {e}")


# 全局实例
_global_detector: Optional[FaultDetector] = None


def get_fault_detector() -> FaultDetector:
    """获取全局故障检测器"""
    global _global_detector
    if _global_detector is None:
        _global_detector = FaultDetector()
    return _global_detector
