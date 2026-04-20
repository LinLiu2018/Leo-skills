"""
Cognition/strategy layer - Enhanced with feedback learning.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np


@dataclass
class StrategyFeedback:
    """策略反馈"""
    strategy_id: str
    outcome: str  # success/failure
    metrics: Dict[str, float]
    timestamp: str
    user_satisfaction: Optional[int] = None  # 1-5


class FeedbackLearner:
    """
    反馈学习器 - 从历史策略执行中学习

    功能:
    - 记录策略执行结果
    - 分析成功/失败模式
    - 优化策略选择
    """

    def __init__(self, storage_path: Optional[Path] = None):
        """
        初始化反馈学习器

        Args:
            storage_path: 反馈数据存储路径
        """
        if storage_path is None:
            project_root = Path(__file__).parent.parent.parent.parent
            self.storage_path = project_root / "data" / "evolution" / "feedback"
        else:
            self.storage_path = Path(storage_path)

        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.feedback_history: List[StrategyFeedback] = []
        self.category_outcomes: Dict[str, Dict[str, int]] = {}
        self.mode_outcomes: Dict[str, Dict[str, int]] = {}

        self._load_history()

    def _get_feedback_file(self) -> Path:
        """获取反馈数据文件"""
        return self.storage_path / "feedback_history.json"

    def _load_history(self):
        """加载历史反馈"""
        feedback_file = self._get_feedback_file()
        if not feedback_file.exists():
            return

        try:
            with open(feedback_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            for item in data:
                feedback = StrategyFeedback(
                    strategy_id=item["strategy_id"],
                    outcome=item["outcome"],
                    metrics=item["metrics"],
                    timestamp=item["timestamp"],
                    user_satisfaction=item.get("user_satisfaction")
                )
                self.feedback_history.append(feedback)

            self._recalculate_outcomes()
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Failed to load feedback: {e}")

    def _save_history(self):
        """保存反馈历史"""
        try:
            data = [
                {
                    "strategy_id": f.strategy_id,
                    "outcome": f.outcome,
                    "metrics": f.metrics,
                    "timestamp": f.timestamp,
                    "user_satisfaction": f.user_satisfaction
                }
                for f in self.feedback_history
            ]

            with open(self._get_feedback_file(), "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Failed to save feedback: {e}")

    def _recalculate_outcomes(self):
        """重新计算结果统计"""
        self.category_outcomes = {}
        self.mode_outcomes = {}

        for feedback in self.feedback_history:
            category = feedback.metrics.get("category", "unknown")
            mode = feedback.metrics.get("mode", "unknown")

            if category not in self.category_outcomes:
                self.category_outcomes[category] = {"success": 0, "failure": 0}
            self.category_outcomes[category][feedback.outcome] += 1

            if mode not in self.mode_outcomes:
                self.mode_outcomes[mode] = {"success": 0, "failure": 0}
            self.mode_outcomes[mode][feedback.outcome] += 1

    def record_feedback(
        self,
        strategy_id: str,
        outcome: str,
        metrics: Dict[str, Any],
        user_satisfaction: Optional[int] = None
    ) -> None:
        """
        记录策略反馈

        Args:
            strategy_id: 策略 ID
            outcome: 执行结果 (success/failure)
            metrics: 相关指标
            user_satisfaction: 用户满意度 (1-5)
        """
        feedback = StrategyFeedback(
            strategy_id=strategy_id,
            outcome=outcome,
            metrics=metrics,
            timestamp=datetime.now().isoformat(),
            user_satisfaction=user_satisfaction
        )

        self.feedback_history.append(feedback)
        self._recalculate_outcomes()
        self._save_history()

    def get_category_success_rate(self, category: str) -> float:
        """获取分类成功率"""
        if category not in self.category_outcomes:
            return 0.5  # 默认值

        outcomes = self.category_outcomes[category]
        total = outcomes.get("success", 0) + outcomes.get("failure", 0)
        if total == 0:
            return 0.5

        return outcomes.get("success", 0) / total

    def get_mode_success_rate(self, mode: str) -> float:
        """获取模式成功率"""
        if mode not in self.mode_outcomes:
            return 0.5

        outcomes = self.mode_outcomes[mode]
        total = outcomes.get("success", 0) + outcomes.get("failure", 0)
        if total == 0:
            return 0.5

        return outcomes.get("success", 0) / total

    def get_optimal_mode(self, category: str) -> str:
        """获取最优模式"""
        modes = ["stabilize", "optimize", "expand"]
        best_mode = "expand"  # 默认
        best_rate = 0.0

        for mode in modes:
            rate = self.get_mode_success_rate(mode)
            if rate > best_rate:
                best_rate = rate
                best_mode = mode

        return best_mode

    def get_recommendations(self) -> List[str]:
        """获取优化建议"""
        recommendations = []

        # 分析错误率高的分类
        for category, outcomes in self.category_outcomes.items():
            total = outcomes.get("success", 0) + outcomes.get("failure", 0)
            if total > 5:  # 至少5次记录
                success_rate = outcomes.get("success", 0) / total
                if success_rate < 0.5:
                    recommendations.append(
                        f"分类 '{category}' 成功率较低 ({success_rate:.1%})，建议优化"
                    )

        # 分析延迟
        if self.feedback_history:
            latencies = [
                f.metrics.get("latency_ms", 0)
                for f in self.feedback_history[-10:]
            ]
            avg_latency = sum(latencies) / len(latencies) if latencies else 0
            if avg_latency > 3000:
                recommendations.append(
                    f"近期平均延迟较高 ({avg_latency:.0f}ms)，建议优化"
                )

        return recommendations


class StrategyEngine:
    """
    策略引擎 - 支持反馈学习的自适应策略生成

    功能:
    - 基于指标生成策略
    - 结合反馈学习优化策略
    - 多维度策略评估
    """

    def __init__(self, enable_learning: bool = True):
        """
        初始化策略引擎

        Args:
            enable_learning: 是否启用反馈学习
        """
        self.enable_learning = enable_learning
        self.feedback_learner = FeedbackLearner() if enable_learning else None

    def generate_strategy(
        self,
        intent: Dict[str, Any],
        metrics: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        生成执行策略

        Args:
            intent: 解析后的意图
            metrics: 系统指标

        Returns:
            策略字典
        """
        category = intent.get("category", "general")
        error_rate = float(metrics.get("error_rate", 0.0))
        avg_latency = float(metrics.get("avg_latency_ms", 0.0))

        # 确定模式
        if error_rate > 0.2:
            mode = "stabilize"
            actions = [
                "reduce concurrent workload",
                "route critical tasks to known stable agents",
                "send warning report",
            ]
        elif avg_latency > 3000:
            mode = "optimize"
            actions = [
                "enable cached paths",
                "prefer lightweight models",
                "defer low-priority tasks",
            ]
        else:
            # 使用反馈学习优化
            if self.enable_learning and self.feedback_learner:
                suggested_mode = self.feedback_learner.get_optimal_mode(category)
                mode = suggested_mode
            else:
                mode = "expand"

            actions = [
                "run standard pipeline",
                "apply domain-specific automation",
                "log outcomes for iterative improvement",
            ]

        # 生成策略 ID
        import hashlib
        strategy_id = hashlib.md5(
            f"{category}{mode}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:12]

        # 置信度
        confidence = intent.get("confidence", 0.5)
        if self.enable_learning and self.feedback_learner:
            category_rate = self.feedback_learner.get_category_success_rate(category)
            confidence = (confidence + category_rate) / 2

        return {
            "strategy_id": strategy_id,
            "mode": mode,
            "category": category,
            "actions": actions,
            "confidence": confidence,
            "error_rate": error_rate,
            "avg_latency": avg_latency,
        }

    def record_outcome(
        self,
        strategy: Dict[str, Any],
        outcome: str,
        latency_ms: int = 0
    ) -> None:
        """
        记录策略执行结果

        Args:
            strategy: 策略字典
            outcome: 执行结果 (success/failure)
            latency_ms: 执行延迟
        """
        if not self.enable_learning or not self.feedback_learner:
            return

        self.feedback_learner.record_feedback(
            strategy_id=strategy.get("strategy_id", ""),
            outcome=outcome,
            metrics={
                "category": strategy.get("category", "unknown"),
                "mode": strategy.get("mode", "unknown"),
                "latency_ms": latency_ms,
                "confidence": strategy.get("confidence", 0.5),
            }
        )

    def get_recommendations(self) -> List[str]:
        """获取优化建议"""
        if self.enable_learning and self.feedback_learner:
            return self.feedback_learner.get_recommendations()
        return []
