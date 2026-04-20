"""
Execution layer - Enhanced auto-evolution pipeline with feedback loop.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional

from .intent_parser import IntentParser, get_intent_parser
from .monitor import MetricsCollector, SystemMetrics
from .strategy_engine import StrategyEngine


@dataclass
class EvolutionResult:
    """进化执行结果"""
    status: str
    intent: Dict[str, Any]
    metrics: SystemMetrics
    strategy: Dict[str, Any]
    execution_plan: Dict[str, Any]
    recommendations: list = None


class AutoEvolutionPipeline:
    """
    自动进化流水线 - 四层架构

    层次:
    1. Intent (意图层) - 解析用户意图
    2. Perception (感知层) - 监控系统状态
    3. Cognition (认知层) - 生成执行策略
    4. Execution (执行层) - 协调执行

    特性:
    - LLM 增强意图解析
    - 实时系统指标监控
    - 反馈学习机制
    - 自动优化建议
    """

    def __init__(
        self,
        use_llm_intent: bool = False,
        enable_system_metrics: bool = True,
        enable_feedback_learning: bool = True
    ):
        """
        初始化进化流水线

        Args:
            use_llm_intent: 使用 LLM 增强意图解析
            enable_system_metrics: 启用系统指标监控
            enable_feedback_learning: 启用反馈学习
        """
        # 初始化各层
        self.intent_parser = get_intent_parser(use_llm=use_llm_intent)
        self.monitor = MetricsCollector(enable_system_metrics=enable_system_metrics)
        self.strategy_engine = StrategyEngine(enable_learning=enable_feedback_learning)

        # 执行统计
        self.execution_count = 0
        self.success_count = 0

    def run_cycle(
        self,
        request_text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> EvolutionResult:
        """
        执行一个进化周期

        Args:
            request_text: 用户请求
            context: 上下文信息

        Returns:
            EvolutionResult: 执行结果
        """
        context = context or {}
        start_time = datetime.now()

        # Layer 1: Intent Parsing (意图解析)
        parsed = self.intent_parser.parse(request_text)

        self.monitor.record_event(
            event_type="intent_parsed",
            status="success",
            latency_ms=80,
            detail={"category": parsed.category}
        )

        # Layer 2: Perception (感知) - 获取系统指标
        metrics = self.monitor.get_metrics()

        # Layer 3: Cognition (认知) - 生成策略
        strategy = self.strategy_engine.generate_strategy(
            intent={
                "category": parsed.category,
                "confidence": parsed.confidence,
                "goals": parsed.goals,
                "entities": parsed.entities,
            },
            metrics={
                "event_count": metrics.event_count,
                "error_rate": metrics.error_rate,
                "avg_latency_ms": metrics.avg_latency_ms,
            }
        )

        self.monitor.record_event(
            event_type="strategy_generated",
            status="success",
            latency_ms=60,
            detail={"mode": strategy["mode"]}
        )

        # Layer 4: Execution Planning (执行计划)
        execution_plan = {
            "request": request_text,
            "category": parsed.category,
            "goals": parsed.goals,
            "entities": parsed.entities,
            "strategy": strategy,
            "context": context,
            "timestamp": start_time.isoformat(),
        }

        # 更新统计
        self.execution_count += 1

        # 获取优化建议
        recommendations = self.strategy_engine.get_recommendations()

        return EvolutionResult(
            status="success",
            intent={
                "category": parsed.category,
                "confidence": parsed.confidence,
                "goals": parsed.goals,
                "entities": parsed.entities,
            },
            metrics=metrics,
            strategy=strategy,
            execution_plan=execution_plan,
            recommendations=recommendations,
        )

    def record_outcome(
        self,
        strategy_id: str,
        outcome: str,
        latency_ms: int = 0
    ) -> None:
        """
        记录执行结果（用于反馈学习）

        Args:
            strategy_id: 策略 ID
            outcome: 执行结果 (success/failure)
            latency_ms: 执行延迟
        """
        if outcome == "success":
            self.success_count += 1

        # 记录事件
        self.monitor.record_event(
            event_type="execution_completed",
            status=outcome,
            latency_ms=latency_ms,
            detail={"strategy_id": strategy_id}
        )

        # 反馈学习
        self.strategy_engine.record_outcome(
            strategy={"strategy_id": strategy_id, "category": "general", "mode": "expand"},
            outcome=outcome,
            latency_ms=latency_ms
        )

    def get_status(self) -> Dict[str, Any]:
        """获取流水线状态"""
        metrics = self.monitor.get_metrics()
        health = self.monitor.get_health_status()

        return {
            "execution_count": self.execution_count,
            "success_count": self.success_count,
            "success_rate": self.success_count / self.execution_count if self.execution_count > 0 else 0.0,
            "health": health,
            "metrics": {
                "event_count": metrics.event_count,
                "error_rate": metrics.error_rate,
                "avg_latency_ms": metrics.avg_latency_ms,
                "cpu_percent": metrics.cpu_percent,
                "memory_percent": metrics.memory_percent,
            },
            "event_breakdown": self.monitor.get_event_breakdown(),
            "latency_percentiles": self.monitor.get_latency_percentiles(),
        }

    def get_recommendations(self) -> list:
        """获取优化建议"""
        return self.strategy_engine.get_recommendations()

    def reset_stats(self) -> None:
        """重置统计信息"""
        self.execution_count = 0
        self.success_count = 0


# 便捷函数
def get_evolution_pipeline(**kwargs) -> AutoEvolutionPipeline:
    """获取进化流水线实例"""
    return AutoEvolutionPipeline(**kwargs)
