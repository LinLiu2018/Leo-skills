# -*- coding: utf-8 -*-
"""
健康检查模块

提供系统健康检查能力
"""

import psutil
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


class HealthStatus(str, Enum):
    """健康状态"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """健康检查结果"""
    component: str
    status: HealthStatus
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict:
        return {
            "component": self.component,
            "status": self.status.value,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp.isoformat()
        }


class HealthChecker:
    """
    健康检查器

    提供系统各组件的健康检查
    """

    def __init__(self):
        self.checks: Dict[str, Callable] = {}
        self._register_default_checks()

    def _register_default_checks(self):
        """注册默认检查"""
        # 系统资源检查
        self.register("cpu", self._check_cpu)
        self.register("memory", self._check_memory)
        self.register("disk", self._check_disk)

        # 技能检查
        self.register("skills", self._check_skills)

        # 调度器检查
        self.register("scheduler", self._check_scheduler)

    def register(self, name: str, check_func: Callable[[], HealthCheckResult]):
        """注册健康检查"""
        self.checks[name] = check_func

    def check(self, component: Optional[str] = None) -> Dict[str, HealthCheckResult]:
        """
        执行健康检查

        Args:
            component: 可选的组件名称

        Returns:
            检查结果字典
        """
        if component:
            check_func = self.checks.get(component)
            if not check_func:
                return {component: HealthCheckResult(
                    component=component,
                    status=HealthStatus.UNKNOWN,
                    message=f"No check registered for {component}"
                )}

            return {component: check_func()}

        # 执行所有检查
        results = {}
        for name, check_func in self.checks.items():
            try:
                results[name] = check_func()
            except Exception as e:
                results[name] = HealthCheckResult(
                    component=name,
                    status=HealthStatus.UNKNOWN,
                    message=f"Check failed: {str(e)}"
                )

        return results

    def get_overall_status(self) -> HealthStatus:
        """获取整体健康状态"""
        results = self.check()

        # 统计各状态数量
        healthy = sum(1 for r in results.values() if r.status == HealthStatus.HEALTHY)
        degraded = sum(1 for r in results.values() if r.status == HealthStatus.DEGRADED)
        unhealthy = sum(1 for r in results.values() if r.status == HealthStatus.UNHEALTHY)
        unknown = sum(1 for r in results.values() if r.status == HealthStatus.UNKNOWN)

        total = len(results)

        if unhealthy > 0 or (unknown == total and total > 0):
            return HealthStatus.UNHEALTHY
        elif degraded > 0:
            return HealthStatus.DEGRADED
        elif healthy == total:
            return HealthStatus.HEALTHY
        else:
            return HealthStatus.UNKNOWN

    # ========== 默认检查实现 ==========

    def _check_cpu(self) -> HealthCheckResult:
        """检查CPU使用率"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()

            # 判断阈值
            if cpu_percent > 90:
                status = HealthStatus.UNHEALTHY
                message = f"CPU使用率过高: {cpu_percent}%"
            elif cpu_percent > 80:
                status = HealthStatus.DEGRADED
                message = f"CPU使用率较高: {cpu_percent}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"CPU使用率正常: {cpu_percent}%"

            return HealthCheckResult(
                component="cpu",
                status=status,
                message=message,
                details={
                    "cpu_percent": cpu_percent,
                    "cpu_count": cpu_count
                }
            )
        except Exception as e:
            return HealthCheckResult(
                component="cpu",
                status=HealthStatus.UNKNOWN,
                message=f"检查失败: {str(e)}"
            )

    def _check_memory(self) -> HealthCheckResult:
        """检查内存使用"""
        try:
            memory = psutil.virtual_memory()

            # 判断阈值
            if memory.percent > 95:
                status = HealthStatus.UNHEALTHY
                message = f"内存使用率过高: {memory.percent}%"
            elif memory.percent > 85:
                status = HealthStatus.DEGRADED
                message = f"内存使用率较高: {memory.percent}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"内存使用率正常: {memory.percent}%"

            return HealthCheckResult(
                component="memory",
                status=status,
                message=message,
                details={
                    "total_gb": round(memory.total / (1024**3), 2),
                    "available_gb": round(memory.available / (1024**3), 2),
                    "used_gb": round(memory.used / (1024**3), 2),
                    "percent": memory.percent
                }
            )
        except Exception as e:
            return HealthCheckResult(
                component="memory",
                status=HealthStatus.UNKNOWN,
                message=f"检查失败: {str(e)}"
            )

    def _check_disk(self) -> HealthCheckResult:
        """检查磁盘使用"""
        try:
            disk = psutil.disk_usage('/')

            # 判断阈值
            if disk.percent > 95:
                status = HealthStatus.UNHEALTHY
                message = f"磁盘使用率过高: {disk.percent}%"
            elif disk.percent > 85:
                status = HealthStatus.DEGRADED
                message = f"磁盘使用率较高: {disk.percent}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"磁盘使用率正常: {disk.percent}%"

            return HealthCheckResult(
                component="disk",
                status=status,
                message=message,
                details={
                    "total_gb": round(disk.total / (1024**3), 2),
                    "free_gb": round(disk.free / (1024**3), 2),
                    "used_gb": round(disk.used / (1024**3), 2),
                    "percent": disk.percent
                }
            )
        except Exception as e:
            return HealthCheckResult(
                component="disk",
                status=HealthStatus.UNKNOWN,
                message=f"检查失败: {str(e)}"
            )

    def _check_skills(self) -> HealthCheckResult:
        """检查技能目录"""
        try:
            skills_path = Path("src/leo_skills")
            if not skills_path.exists():
                return HealthCheckResult(
                    component="skills",
                    status=HealthStatus.UNHEALTHY,
                    message="技能目录不存在"
                )

            # 统计技能数量
            categories = [d for d in skills_path.iterdir() if d.is_dir()]
            skills_count = 0
            for category in categories:
                skills_count += len([d for d in category.iterdir() if d.is_dir()])

            if skills_count > 0:
                status = HealthStatus.HEALTHY
                message = f"技能系统正常: {skills_count}个技能"
            else:
                status = HealthStatus.DEGRADED
                message = "未发现技能"

            return HealthCheckResult(
                component="skills",
                status=status,
                message=message,
                details={
                    "categories": len(categories),
                    "skills_count": skills_count
                }
            )
        except Exception as e:
            return HealthCheckResult(
                component="skills",
                status=HealthStatus.UNKNOWN,
                message=f"检查失败: {str(e)}"
            )

    def _check_scheduler(self) -> HealthCheckResult:
        """检查调度器"""
        try:
            # 尝试导入调度器
            try:
                from ..scheduler import UnifiedScheduler
                scheduler = UnifiedScheduler()
                status = HealthStatus.HEALTHY
                message = "调度器正常"
            except Exception:
                status = HealthStatus.DEGRADED
                message = "调度器未初始化"

            return HealthCheckResult(
                component="scheduler",
                status=status,
                message=message,
                details={}
            )
        except Exception as e:
            return HealthCheckResult(
                component="scheduler",
                status=HealthStatus.UNKNOWN,
                message=f"检查失败: {str(e)}"
            )

    # ========== 便捷方法 ==========

    def check_all(self) -> Dict[str, Any]:
        """检查所有组件并返回完整报告"""
        results = self.check()
        overall = self.get_overall_status()

        return {
            "overall_status": overall.value,
            "timestamp": datetime.now().isoformat(),
            "components": {
                name: result.to_dict()
                for name, result in results.items()
            }
        }


# 全局健康检查器
_global_health_checker: Optional[HealthChecker] = None


def get_health_checker() -> HealthChecker:
    """获取全局健康检查器"""
    global _global_health_checker
    if _global_health_checker is None:
        _global_health_checker = HealthChecker()
    return _global_health_checker
