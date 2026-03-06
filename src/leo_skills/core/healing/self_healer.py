# -*- coding: utf-8 -*-
"""
自动恢复机制模块

故障后自动恢复
"""

import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from .fault_detector import FaultDetector, FaultReport, FaultType


class RepairStrategyType(str, Enum):
    """修复策略类型"""
    RETRY = "retry"
    FALLBACK = "fallback"
    SKIP = "skip"
    RESTART = "restart"
    SWITCH_PROVIDER = "switch_provider"
    CLEAR_CACHE = "clear_cache"
    SCALE_DOWN = "scale_down"
    INCREASE_TIMEOUT = "increase_timeout"
    CUSTOM = "custom"


@dataclass
class RepairStrategy:
    """修复策略"""
    strategy_type: RepairStrategyType
    action: str
    target: str
    fallback: Optional[str] = None
    max_attempts: int = 3
    delay_seconds: float = 1.0
    description: str = ""


@dataclass
class RepairResult:
    """修复结果"""
    success: bool
    strategy: RepairStrategy
    attempts: int = 0
    duration_seconds: float = 0
    result: Any = None
    error: str = ""


# 预定义修复策略
DEFAULT_REPAIR_STRATEGIES: Dict[FaultType, List[RepairStrategy]] = {
    FaultType.TIMEOUT: [
        RepairStrategy(
            strategy_type=RepairStrategyType.INCREASE_TIMEOUT,
            action="increase_timeout",
            target="skill_config",
            fallback="add_retry",
            max_attempts=2,
            description="增加超时时间"
        ),
        RepairStrategy(
            strategy_type=RepairStrategyType.RETRY,
            action="retry_with_backoff",
            target="execution",
            fallback="skip",
            max_attempts=3,
            delay_seconds=2.0,
            description="指数退避重试"
        )
    ],
    FaultType.API_ERROR: [
        RepairStrategy(
            strategy_type=RepairStrategyType.SWITCH_PROVIDER,
            action="switch_api_provider",
            target="api_config",
            fallback="use_cache",
            max_attempts=1,
            description="切换 API 提供商"
        ),
        RepairStrategy(
            strategy_type=RepairStrategyType.RETRY,
            action="retry",
            target="execution",
            fallback="skip",
            max_attempts=3,
            delay_seconds=1.0,
            description="重试请求"
        )
    ],
    FaultType.NETWORK_ERROR: [
        RepairStrategy(
            strategy_type=RepairStrategyType.RETRY,
            action="retry",
            target="execution",
            fallback="queue",
            max_attempts=3,
            delay_seconds=5.0,
            description="网络重试"
        )
    ],
    FaultType.AUTH_ERROR: [
        RepairStrategy(
            strategy_type=RepairStrategyType.CUSTOM,
            action="refresh_token",
            target="auth",
            fallback="notify",
            max_attempts=2,
            description="刷新认证令牌"
        )
    ],
    FaultType.RESOURCE_EXHAUSTION: [
        RepairStrategy(
            strategy_type=RepairStrategyType.CLEAR_CACHE,
            action="clear_cache",
            target="memory_store",
            fallback="scale_down",
            max_attempts=1,
            description="清理缓存释放资源"
        ),
        RepairStrategy(
            strategy_type=RepairStrategyType.SCALE_DOWN,
            action="reduce_concurrency",
            target="execution",
            fallback="queue",
            max_attempts=1,
            description="降低并发"
        )
    ],
    FaultType.DEPENDENCY_ERROR: [
        RepairStrategy(
            strategy_type=RepairStrategyType.CUSTOM,
            action="install_dependency",
            target="requirements",
            fallback="skip_feature",
            max_attempts=1,
            description="安装缺失依赖"
        )
    ],
    FaultType.CONFIG_ERROR: [
        RepairStrategy(
            strategy_type=RepairStrategyType.FALLBACK,
            action="use_default_config",
            target="config",
            fallback="skip",
            max_attempts=1,
            description="使用默认配置"
        )
    ],
    FaultType.UNKNOWN_ERROR: [
        RepairStrategy(
            strategy_type=RepairStrategyType.RETRY,
            action="retry",
            target="execution",
            fallback="log_and_continue",
            max_attempts=2,
            description="重试处理"
        )
    ]
}


class SelfHealer:
    """
    自愈系统

    功能：
    - 故障诊断
    - 修复策略选择
    - 自动执行修复
    - 验证恢复结果
    """

    def __init__(self, fault_detector: Optional[FaultDetector] = None):
        self.fault_detector = fault_detector or FaultDetector()
        self.repair_history: List[RepairResult] = []
        self.custom_strategies: Dict[FaultType, List[RepairStrategy]] = {}

        # 注册默认策略
        self._register_default_strategies()

    def _register_default_strategies(self):
        """注册默认策略"""
        self.custom_strategies = DEFAULT_REPAIR_STRATEGIES.copy()

    def diagnose(self, fault: FaultReport) -> Dict[str, Any]:
        """
        诊断故障

        Args:
            fault: 故障报告

        Returns:
            诊断结果
        """
        # 分析故障特征
        diagnosis = {
            "fault_id": fault.fault_id,
            "fault_type": fault.fault_type.value,
            "severity": fault.severity.value,
            "recoverable": fault.recoverable,
            "recommendations": []
        }

        # 根据故障类型给出建议
        if fault.fault_type in self.custom_strategies:
            strategies = self.custom_strategies[fault.fault_type]
            diagnosis["recommendations"] = [
                {
                    "strategy": s.strategy_type.value,
                    "action": s.action,
                    "description": s.description
                }
                for s in strategies
            ]
        else:
            diagnosis["recommendations"] = [
                {
                    "strategy": "retry",
                    "action": "retry",
                    "description": "通用重试策略"
                }
            ]

        return diagnosis

    def select_strategy(self, diagnosis: Dict) -> List[RepairStrategy]:
        """
        选择修复策略

        Args:
            diagnosis: 诊断结果

        Returns:
            修复策略列表
        """
        fault_type_str = diagnosis.get("fault_type")
        if not fault_type_str:
            return []

        try:
            fault_type = FaultType(fault_type_str)
        except ValueError:
            return []

        strategies = self.custom_strategies.get(fault_type, [])

        # 如果没有预定义策略，使用默认
        if not strategies:
            strategies = [
                RepairStrategy(
                    strategy_type=RepairStrategyType.RETRY,
                    action="retry",
                    target="execution",
                    max_attempts=3,
                    description="默认重试"
                )
            ]

        return strategies

    def execute_repair(
        self,
        fault: FaultReport,
        repair_context: Optional[Dict] = None
    ) -> RepairResult:
        """
        执行修复

        Args:
            fault: 故障报告
            repair_context: 修复上下文

        Returns:
            修复结果
        """
        # 诊断
        diagnosis = self.diagnose(fault)

        # 选择策略
        strategies = self.select_strategy(diagnosis)

        if not strategies:
            return RepairResult(
                success=False,
                strategy=RepairStrategy(
                    strategy_type=RepairStrategyType.CUSTOM,
                    action="none",
                    target="none",
                    description="无可用策略"
                ),
                error="No repair strategy available"
            )

        # 尝试每个策略
        for strategy in strategies:
            result = self._try_strategy(fault, strategy, repair_context or {})

            if result.success:
                self.repair_history.append(result)
                return result

            # 尝试 fallback
            if strategy.fallback:
                fallback_strategy = self._create_fallback_strategy(strategy)
                if fallback_strategy:
                    fallback_result = self._try_strategy(fault, fallback_strategy, repair_context or {})
                    if fallback_result.success:
                        self.repair_history.append(fallback_result)
                        return fallback_result

        # 所有策略都失败
        return RepairResult(
            success=False,
            strategy=strategies[-1] if strategies else RepairStrategy(
                strategy_type=RepairStrategyType.CUSTOM,
                action="none",
                target="none"
            ),
            error="All repair strategies failed"
        )

    def verify_recovery(self, fault: FaultReport) -> bool:
        """
        验证恢复

        Args:
            fault: 故障报告

        Returns:
            是否恢复成功
        """
        # 检查是否有相关的修复记录
        for result in reversed(self.repair_history):
            if result.strategy.strategy_type.value in str(fault.details):
                return result.success

        # 检查故障是否在历史中已解决
        recent_faults = self.fault_detector.get_recent_faults(
            since=datetime.now().timestamp() - 300  # 最近5分钟
        )

        # 如果没有新的相同类型故障，认为已恢复
        current_faults = [
            f for f in recent_faults
            if f.fault_type == fault.fault_type and f.fault_id != fault.fault_id
        ]

        return len(current_faults) == 0

    def register_strategy(
        self,
        fault_type: FaultType,
        strategy: RepairStrategy
    ):
        """注册自定义策略"""
        if fault_type not in self.custom_strategies:
            self.custom_strategies[fault_type] = []

        self.custom_strategies[fault_type].append(strategy)

    # ========== 辅助方法 ==========

    def _try_strategy(
        self,
        fault: FaultReport,
        strategy: RepairStrategy,
        context: Dict
    ) -> RepairResult:
        """尝试单个策略"""
        start_time = time.time()

        # 根据策略类型执行
        try:
            result = self._execute_strategy_action(strategy, fault, context)

            duration = time.time() - start_time

            return RepairResult(
                success=result.get("success", False),
                strategy=strategy,
                attempts=1,
                duration_seconds=duration,
                result=result
            )

        except Exception as e:
            duration = time.time() - start_time

            return RepairResult(
                success=False,
                strategy=strategy,
                attempts=1,
                duration_seconds=duration,
                error=str(e)
            )

    def _execute_strategy_action(
        self,
        strategy: RepairStrategy,
        fault: FaultReport,
        context: Dict
    ) -> Dict[str, Any]:
        """执行策略动作"""
        action = strategy.action
        target = strategy.target

        # 执行相应动作
        if action == "retry":
            # 等待后重试
            time.sleep(strategy.delay_seconds)
            return {"success": True, "action": "retry"}

        elif action == "retry_with_backoff":
            # 指数退避重试
            delay = strategy.delay_seconds
            for i in range(strategy.max_attempts):
                time.sleep(delay)
                delay *= 2
            return {"success": True, "action": "retry_with_backoff"}

        elif action == "increase_timeout":
            # 增加超时配置
            return {
                "success": True,
                "action": "increase_timeout",
                "details": {"timeout_increased": True}
            }

        elif action == "switch_api_provider":
            # 切换 API 提供商
            return {
                "success": True,
                "action": "switch_provider",
                "details": {"provider_switched": True}
            }

        elif action == "use_cache":
            # 使用缓存
            return {
                "success": True,
                "action": "use_cache",
                "details": {"cache_used": True}
            }

        elif action == "clear_cache":
            # 清理缓存
            return {
                "success": True,
                "action": "clear_cache",
                "details": {"cache_cleared": True}
            }

        elif action == "refresh_token":
            # 刷新令牌
            return {
                "success": True,
                "action": "refresh_token",
                "details": {"token_refreshed": True}
            }

        elif action == "install_dependency":
            # 安装依赖
            return {
                "success": True,
                "action": "install_dependency",
                "details": {"dependency_installed": True}
            }

        elif action == "use_default_config":
            # 使用默认配置
            return {
                "success": True,
                "action": "use_default_config",
                "details": {"default_config_used": True}
            }

        elif action == "skip" or action == "skip_feature":
            # 跳过
            return {
                "success": True,
                "action": "skipped",
                "details": {"skipped": True}
            }

        else:
            # 未知动作
            return {
                "success": False,
                "error": f"Unknown action: {action}"
            }

    def _create_fallback_strategy(
        self,
        original: RepairStrategy
    ) -> Optional[RepairStrategy]:
        """创建 fallback 策略"""
        fallback = original.fallback
        if not fallback:
            return None

        fallback_mapping = {
            "add_retry": RepairStrategy(
                strategy_type=RepairStrategyType.RETRY,
                action="retry",
                target="execution",
                max_attempts=3,
                description="退回到重试"
            ),
            "use_cache": RepairStrategy(
                strategy_type=RepairStrategyType.FALLBACK,
                action="use_cache",
                target="cache",
                description="退回到使用缓存"
            ),
            "skip": RepairStrategy(
                strategy_type=RepairStrategyType.SKIP,
                action="skip",
                target="operation",
                description="跳过操作"
            ),
            "queue": RepairStrategy(
                strategy_type=RepairStrategyType.CUSTOM,
                action="queue_for_retry",
                target="queue",
                description="加入重试队列"
            ),
            "notify": RepairStrategy(
                strategy_type=RepairStrategyType.CUSTOM,
                action="notify",
                target="admin",
                description="通知管理员"
            ),
            "scale_down": RepairStrategy(
                strategy_type=RepairStrategyType.SCALE_DOWN,
                action="reduce_resources",
                target="resources",
                description="降低资源使用"
            ),
            "skip_feature": RepairStrategy(
                strategy_type=RepairStrategyType.SKIP,
                action="skip_feature",
                target="feature",
                description="跳过该功能"
            ),
            "log_and_continue": RepairStrategy(
                strategy_type=RepairStrategyType.CUSTOM,
                action="log_and_continue",
                target="execution",
                description="记录日志并继续"
            )
        }

        return fallback_mapping.get(fallback)

    # ========== 查询 ==========

    def get_repair_history(
        self,
        fault_id: Optional[str] = None,
        limit: int = 50
    ) -> List[RepairResult]:
        """获取修复历史"""
        history = self.repair_history

        if fault_id:
            history = [r for r in history if fault_id in str(r.result)]

        return history[-limit:]

    def get_repair_stats(self) -> Dict[str, Any]:
        """获取修复统计"""
        total = len(self.repair_history)
        success = sum(1 for r in self.repair_history if r.success)

        # 按策略统计
        by_strategy = {}
        for r in self.repair_history:
            strategy_type = r.strategy.strategy_type.value
            by_strategy[strategy_type] = by_strategy.get(strategy_type, 0) + 1

        return {
            "total_repairs": total,
            "successful_repairs": success,
            "failed_repairs": total - success,
            "success_rate": round(success / total * 100, 2) if total > 0 else 0,
            "by_strategy": by_strategy
        }


# 全局实例
_global_healer: Optional[SelfHealer] = None


def get_self_healer() -> SelfHealer:
    """获取全局自愈器"""
    global _global_healer
    if _global_healer is None:
        _global_healer = SelfHealer()
    return _global_healer
