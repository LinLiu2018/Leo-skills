# -*- coding: utf-8 -*-
"""
Leo AI System - 统一自管理系统入口

整合所有自管理模块，提供统一 API：
- 调度中心
- 监控系统
- 日志系统
- 进化系统
- 修复系统
- 部署系统
"""

from typing import Any, Dict, List, Optional

from .scheduler import UnifiedScheduler
from .monitoring import SystemMonitor, MetricsCollector, AlertManager, HealthChecker
from .logging import UnifiedLogger, LogAnalyzer
from .evolution import LLMAnalyzer, CodeGenerator, EvolutionExecutor
from .healing import FaultDetector, SelfHealer, CompensationManager
from .deployment import BlueGreenDeployment, AutoRollback, EffectTracker


class LeoSelfManagementSystem:
    """
    Leo AI 自管理系统

    统一入口，整合所有自管理能力
    """

    def __init__(self):
        # 核心子系统
        self.scheduler: Optional[UnifiedScheduler] = None
        self.monitor: Optional[SystemMonitor] = None
        self.logger: Optional[UnifiedLogger] = None
        self.log_analyzer: Optional[LogAnalyzer] = None
        self.evolution_executor: Optional[EvolutionExecutor] = None
        self.code_generator: Optional[CodeGenerator] = None
        self.llm_analyzer: Optional[LLMAnalyzer] = None
        self.fault_detector: Optional[FaultDetector] = None
        self.self_healer: Optional[SelfHealer] = None
        self.compensation: Optional[CompensationManager] = None
        self.deployment: Optional[BlueGreenDeployment] = None
        self.auto_rollback: Optional[AutoRollback] = None
        self.effect_tracker: Optional[EffectTracker] = None

        # 初始化状态
        self._initialized = False

    # ========== 初始化 ==========

    def initialize(self) -> Dict[str, Any]:
        """初始化所有子系统"""
        results = {}

        try:
            # 1. 调度中心
            self.scheduler = UnifiedScheduler()
            results["scheduler"] = "ok"
        except Exception as e:
            results["scheduler"] = f"error: {e}"

        try:
            # 2. 监控系统
            self.monitor = SystemMonitor()
            results["monitor"] = "ok"
        except Exception as e:
            results["monitor"] = f"error: {e}"

        try:
            # 3. 日志系统
            self.logger = UnifiedLogger()
            self.log_analyzer = LogAnalyzer(self.logger)
            results["logger"] = "ok"
        except Exception as e:
            results["logger"] = f"error: {e}"

        try:
            # 4. 进化系统
            self.llm_analyzer = LLMAnalyzer()
            self.code_generator = CodeGenerator()
            self.evolution_executor = EvolutionExecutor()
            results["evolution"] = "ok"
        except Exception as e:
            results["evolution"] = f"error: {e}"

        try:
            # 5. 修复系统
            self.fault_detector = FaultDetector()
            self.self_healer = SelfHealer(self.fault_detector)
            self.compensation = CompensationManager()
            results["healing"] = "ok"
        except Exception as e:
            results["healing"] = f"error: {e}"

        try:
            # 6. 部署系统
            self.deployment = BlueGreenDeployment()
            self.auto_rollback = AutoRollback()
            self.effect_tracker = EffectTracker()
            results["deployment"] = "ok"
        except Exception as e:
            results["deployment"] = f"error: {e}"

        self._initialized = True

        return {
            "status": "success" if all("ok" in v for v in results.values()) else "partial",
            "components": results,
            "initialized": self._initialized
        }

    # ========== 统一 API ==========

    def get_system_status(self) -> Dict[str, Any]:
        """获取系统整体状态"""
        if not self._initialized:
            self.initialize()

        status = {
            "initialized": self._initialized,
            "components": {}
        }

        # 调度器状态
        if self.scheduler:
            try:
                scheduler_status = self.scheduler.get_status()
                status["components"]["scheduler"] = scheduler_status
            except:
                status["components"]["scheduler"] = {"error": "failed"}

        # 监控状态
        if self.monitor:
            try:
                monitor_status = self.monitor.get_status()
                status["components"]["monitor"] = monitor_status
            except:
                status["components"]["monitor"] = {"error": "failed"}

        # 日志统计
        if self.logger:
            try:
                log_stats = self.logger.get_stats()
                status["components"]["logger"] = log_stats
            except:
                status["components"]["logger"] = {"error": "failed"}

        # 健康检查
        if self.fault_detector:
            try:
                fault_stats = self.fault_detector.get_fault_stats()
                status["components"]["faults"] = fault_stats
            except:
                status["components"]["faults"] = {"error": "failed"}

        return status

    def run_health_check(self) -> Dict[str, Any]:
        """运行健康检查"""
        if not self._initialized:
            self.initialize()

        results = {}

        # 1. 健康检查
        if self.monitor:
            results["health"] = self.monitor.check_health()

        # 2. 调度器检查
        if self.scheduler:
            results["scheduler"] = self.scheduler.get_status()

        # 3. 故障统计
        if self.fault_detector:
            results["faults"] = self.fault_detector.get_fault_stats()

        # 4. 部署状态
        if self.deployment:
            results["deployment"] = {
                "status": "available"
            }

        return results

    def execute_self_optimization(self) -> Dict[str, Any]:
        """执行自我优化"""
        if not self._initialized:
            self.initialize()

        improvements = []

        # 1. 自动优化调度器
        if self.scheduler:
            try:
                # 发现技能并注册
                result = self.scheduler.discover_skills()
                if result.get("new_skills"):
                    self.scheduler.register_discovered()
                    improvements.append({
                        "type": "scheduler",
                        "action": "auto_register",
                        "count": len(result.get("new_skills", []))
                    })
            except Exception as e:
                improvements.append({
                    "type": "scheduler",
                    "action": "error",
                    "error": str(e)
                })

        # 2. 清理日志
        if self.logger:
            try:
                self.logger._persist_logs()
                improvements.append({
                    "type": "logger",
                    "action": "persist_logs"
                })
            except Exception as e:
                improvements.append({
                    "type": "logger",
                    "action": "error",
                    "error": str(e)
                })

        # 3. 记录优化历史
        if self.effect_tracker:
            try:
                self.effect_tracker.record_change(
                    skill_path="system",
                    change_id="self_optimization",
                    change_type="auto_optimization",
                    description="System self-optimization",
                    before={},
                    after={"improvements": improvements}
                )
                improvements.append({
                    "type": "tracker",
                    "action": "recorded"
                })
            except:
                pass

        return {
            "status": "success",
            "improvements": improvements,
            "count": len(improvements)
        }

    def get_dashboard(self) -> Dict[str, Any]:
        """获取管理仪表板"""
        if not self._initialized:
            self.initialize()

        return {
            "system_status": self.get_system_status(),
            "health_check": self.run_health_check(),
            "components": {
                "scheduler": self.scheduler is not None,
                "monitor": self.monitor is not None,
                "logger": self.logger is not None,
                "evolution": self.llm_analyzer is not None,
                "healing": self.fault_detector is not None,
                "deployment": self.deployment is not None
            }
        }


# 全局实例
_global_system: Optional[LeoSelfManagementSystem] = None


def get_self_management_system() -> LeoSelfManagementSystem:
    """获取全局自管理系统实例"""
    global _global_system
    if _global_system is None:
        _global_system = LeoSelfManagementSystem()
    return _global_system


# 便捷函数
def initialize_system() -> Dict[str, Any]:
    """初始化系统"""
    system = get_self_management_system()
    return system.initialize()


def get_status() -> Dict[str, Any]:
    """获取系统状态"""
    system = get_self_management_system()
    return system.get_system_status()


def run_check() -> Dict[str, Any]:
    """运行检查"""
    system = get_self_management_system()
    return system.run_health_check()


def optimize() -> Dict[str, Any]:
    """执行优化"""
    system = get_self_management_system()
    return system.execute_self_optimization()


def get_dashboard() -> Dict[str, Any]:
    """获取仪表板"""
    system = get_self_management_system()
    return system.get_dashboard()
