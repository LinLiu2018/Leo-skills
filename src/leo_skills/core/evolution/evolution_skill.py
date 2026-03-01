# -*- coding: utf-8 -*-
"""
evolution_skill - 技能进化管理技能

支持技能的自我学习和进化，自动记录经验、优化策略和性能改进。
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum

from leo_skills.base import BaseSkill, SkillResult


class EvolutionStage(Enum):
    """进化阶段"""
    INITIAL = "initial"
    LEARNING = "learning"
    OPTIMIZING = "optimizing"
    MATURE = "mature"
    ADAPTIVE = "adaptive"


@dataclass
class EvolutionTip:
    """进化经验"""
    tip: str
    context: str
    timestamp: str
    success_count: int = 0
    failure_count: int = 0


@dataclass
class PerformanceMetric:
    """性能指标"""
    metric_name: str
    value: float
    timestamp: str
    unit: str = ""


class EvolutionSkill(BaseSkill):
    """
    技能进化管理技能

    功能：
    - 自动加载和保存进化数据
    - 记录和累积经验
    - 跟踪性能指标
    - 管理进化历史
    - 提供上下文优化

    使用场景：
    - 技能自我改进
    - 经验知识积累
    - 性能调优
    - 策略优化
    """
    supports_direct_execution = True
    default_schedule = "0 */4 * * *"

    def __init__(
        self,
        skill_name: str = "evolution_skill",
        evolution_path: str = None,
        config_path: str = None
    ):
        self._name = skill_name
        self.version = "1.0.0"
        self.description = "技能进化管理技能 - 支持自我学习和进化"

        self.evolution_path = Path(evolution_path) if evolution_path else Path(f"evolution_{skill_name}.json")
        self.config_path = config_path

        # 初始化进化数据
        self.experience_data = self._load_experience()

    @property
    def name(self) -> str:
        return self._name

    def get_actions(self) -> List[str]:
        return ["learn", "get_tips", "record_metric", "get_metrics",
                "get_stage", "evolve", "history", "reset", "health_check"]

    def _load_experience(self) -> Dict[str, Any]:
        """加载进化数据"""
        if self.evolution_path.exists():
            try:
                with open(self.evolution_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[Warning] Failed to load evolution data: {e}")
                return self._get_default_data()
        return self._get_default_data()

    def _get_default_data(self) -> Dict[str, Any]:
        """获取默认数据"""
        return {
            "version": 1,
            "stage": EvolutionStage.INITIAL.value,
            "tips": [],
            "history": [],
            "metrics": [],
            "config": {},
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

    def _save_experience(self):
        """保存进化数据"""
        self.experience_data["updated_at"] = datetime.now().isoformat()
        try:
            with open(self.evolution_path, 'w', encoding='utf-8') as f:
                json.dump(self.experience_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[Error] Failed to save evolution data: {e}")

    def execute(
        self,
        action: str = "learn",
        context: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> SkillResult:
        """
        执行进化操作

        Args:
            action: 操作类型
                - learn: 学习新经验
                - get_tips: 获取经验提示
                - record_metric: 记录性能指标
                - get_metrics: 获取性能指标
                - get_stage: 获取当前阶段
                - evolve: 执行进化
                - history: 获取历史记录
                - reset: 重置进化数据
                - health_check: 系统健康检查（定时直连场景）

        Returns:
            SkillResult 标准结果
        """
        params: Dict[str, Any] = {}
        if isinstance(context, dict):
            context_params = context.get("params")
            if isinstance(context_params, dict):
                params.update(context_params)
            params.update(context)
        if isinstance(kwargs.get("params"), dict):
            params.update(kwargs.pop("params"))
        params.update(kwargs)

        requested_action = str(params.get("action", action))
        if context is not None and requested_action == "learn" and not params.get("tip"):
            requested_action = "health_check"

        try:
            if requested_action == "learn":
                data = self._learn(params)
            elif requested_action == "get_tips":
                data = self._get_tips()
            elif requested_action == "record_metric":
                data = self._record_metric(params)
            elif requested_action == "get_metrics":
                data = self._get_metrics(params)
            elif requested_action == "get_stage":
                data = self._get_stage()
            elif requested_action == "evolve":
                data = self._evolve(params)
            elif requested_action == "history":
                data = self._get_history(params.get("limit", 50))
            elif requested_action == "reset":
                data = self._reset()
            elif requested_action == "health_check":
                data = self._health_check()
            else:
                return SkillResult.fail(f"Unknown action: {requested_action}")

            if data.get("status") == "error":
                return SkillResult.fail(data.get("message", data.get("error", "")))
            return SkillResult.ok(data=data)

        except Exception as e:
            return SkillResult.fail(str(e))

    def _health_check(self) -> Dict[str, Any]:
        """健康检查：返回当前阶段、经验数量和指标数量。"""
        tips_count = len(self.experience_data.get("tips", []))
        metrics_count = len(self.experience_data.get("metrics", []))
        stage_info = self._get_stage()
        return {
            "status": "success",
            "skill": self.name,
            "health": "ok",
            "stage": stage_info.get("stage"),
            "tips_count": tips_count,
            "metrics_count": metrics_count,
            "updated_at": self.experience_data.get("updated_at"),
        }

    def _learn(self, kwargs: Dict) -> Dict[str, Any]:
        """学习新经验"""
        tip = kwargs.get("tip", "")
        context = kwargs.get("context", "")
        success = kwargs.get("success", True)

        if not tip:
            return {"status": "error", "message": "Tip is required"}

        # 检查是否已存在
        for existing_tip in self.experience_data["tips"]:
            if existing_tip.get("tip") == tip:
                if success:
                    existing_tip["success_count"] += 1
                else:
                    existing_tip["failure_count"] += 1
                self._save_experience()
                return {
                    "status": "success",
                    "skill": self.name,
                    "action": "updated",
                    "tip": tip
                }

        # 添加新经验
        entry = {
            "tip": tip,
            "context": context,
            "timestamp": datetime.now().isoformat(),
            "success_count": 1 if success else 0,
            "failure_count": 0 if success else 1
        }

        self.experience_data["tips"].append(entry)
        self.experience_data["history"].append(entry)
        self._save_experience()

        return {
            "status": "success",
            "skill": self.name,
            "action": "learned",
            "tip": tip
        }

    def _get_tips(self) -> Dict[str, Any]:
        """获取经验提示"""
        tips = self.experience_data.get("tips", [])
        # 按成功率排序
        sorted_tips = sorted(
            tips,
            key=lambda x: (x.get("success_count", 0) - x.get("failure_count", 0)),
            reverse=True
        )

        return {
            "status": "success",
            "skill": self.name,
            "tips": [t["tip"] for t in sorted_tips],
            "count": len(sorted_tips)
        }

    def _record_metric(self, kwargs: Dict) -> Dict[str, Any]:
        """记录性能指标"""
        metric_name = kwargs.get("metric_name", "")
        value = kwargs.get("value", 0)
        unit = kwargs.get("unit", "")

        if not metric_name:
            return {"status": "error", "message": "Metric name is required"}

        metric = PerformanceMetric(
            metric_name=metric_name,
            value=value,
            timestamp=datetime.now().isoformat(),
            unit=unit
        )

        self.experience_data["metrics"].append(metric.__dict__)

        # 保留最近100个指标
        if len(self.experience_data["metrics"]) > 100:
            self.experience_data["metrics"] = self.experience_data["metrics"][-100:]

        self._save_experience()

        return {
            "status": "success",
            "skill": self.name,
            "metric": metric_name,
            "value": value
        }

    def _get_metrics(self, kwargs: Dict) -> Dict[str, Any]:
        """获取性能指标"""
        metric_name = kwargs.get("metric_name")
        limit = kwargs.get("limit", 10)

        metrics = self.experience_data.get("metrics", [])

        if metric_name:
            metrics = [m for m in metrics if m.get("metric_name") == metric_name]

        # 返回最近的指标
        recent_metrics = metrics[-limit:]

        # 计算统计
        if recent_metrics:
            values = [m.get("value", 0) for m in recent_metrics]
            stats = {
                "count": len(values),
                "avg": sum(values) / len(values) if values else 0,
                "min": min(values) if values else 0,
                "max": max(values) if values else 0
            }
        else:
            stats = {"count": 0, "avg": 0, "min": 0, "max": 0}

        return {
            "status": "success",
            "skill": self.name,
            "metrics": recent_metrics,
            "statistics": stats
        }

    def _get_stage(self) -> Dict[str, Any]:
        """获取当前进化阶段"""
        stage = self.experience_data.get("stage", EvolutionStage.INITIAL.value)

        # 根据经验数量更新阶段
        tips_count = len(self.experience_data.get("tips", []))

        if tips_count < 5:
            current_stage = EvolutionStage.INITIAL
        elif tips_count < 20:
            current_stage = EvolutionStage.LEARNING
        elif tips_count < 50:
            current_stage = EvolutionStage.OPTIMIZING
        elif tips_count < 100:
            current_stage = EvolutionStage.MATURE
        else:
            current_stage = EvolutionStage.ADAPTIVE

        # 更新阶段
        if current_stage.value != stage:
            self.experience_data["stage"] = current_stage.value
            self._save_experience()

        stage_info = {
            EvolutionStage.INITIAL: "初始阶段 - 正在积累初始经验",
            EvolutionStage.LEARNING: "学习阶段 - 正在快速积累经验",
            EvolutionStage.OPTIMIZING: "优化阶段 - 正在精细化经验",
            EvolutionStage.MATURE: "成熟阶段 - 经验已趋于稳定",
            EvolutionStage.ADAPTIVE: "自适应阶段 - 能够自我调整和适应"
        }

        return {
            "status": "success",
            "skill": self.name,
            "stage": current_stage.value,
            "description": stage_info.get(current_stage, ""),
            "tips_count": tips_count
        }

    def _evolve(self, kwargs: Dict) -> Dict[str, Any]:
        """执行进化"""
        strategy = kwargs.get("strategy", "auto")

        # 基于当前状态决定进化方向
        stage_info = self._get_stage()
        tips = self._get_tips()

        suggestions = []

        # 根据阶段提供进化建议
        if stage_info["tips_count"] < 5:
            suggestions.append("继续积累更多初始经验")
            suggestions.append("关注核心场景的经验记录")
        elif stage_info["tips_count"] < 20:
            suggestions.append("开始整理和归类经验")
            suggestions.append("识别重复的模式和最佳实践")
        else:
            suggestions.append("基于历史优化策略")
            suggestions.append("建立经验之间的关联")

        return {
            "status": "success",
            "skill": self.name,
            "current_stage": stage_info["stage"],
            "suggestions": suggestions,
            "top_tips": tips["tips"][:5]
        }

    def _get_history(self, limit: int) -> Dict[str, Any]:
        """获取进化历史"""
        history = self.experience_data.get("history", [])
        recent = history[-limit:] if len(history) > limit else history

        return {
            "status": "success",
            "skill": self.name,
            "history": recent,
            "total_count": len(history)
        }

    def _reset(self) -> Dict[str, Any]:
        """重置进化数据"""
        self.experience_data = self._get_default_data()
        self._save_experience()

        return {
            "status": "success",
            "skill": self.name,
            "message": "Evolution data reset successfully"
        }

    def learn_from_result(self, tip: str, context: str = "", success: bool = True):
        """从结果中学习"""
        return self.execute(
            action="learn",
            tip=tip,
            context=context,
            success=success
        )
    def get_experience_context(self) -> str:
        """获取用于Prompt的经验上下文"""
        tips = [t["tip"] for t in self.experience_data.get("tips", [])]
        if not tips:
            return ""

        return "\n".join([f"- {tip}" for tip in tips[:10]])

    def record_performance(self, operation: str, duration_ms: float):
        """记录性能"""
        return self.execute(
            action="record_metric",
            metric_name=operation,
            value=duration_ms,
            unit="ms"
        )

    def get_capabilities(self) -> Dict[str, Any]:
        """获取技能能力信息"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "features": [
                "experience_learning",
                "performance_tracking",
                "evolution_stages",
                "history_management",
                "context_generation",
                "strategy_suggestion"
            ],
            "stages": [s.value for s in EvolutionStage],
            "evolution_file": str(self.evolution_path)
        }


# 向后兼容
Evolution_Skill = EvolutionSkill


def main():
    """入口函数 - 演示用法"""
    print("=" * 60)
    print("Evolution Skill - 演示")
    print("=" * 60)

    skill = EvolutionSkill(skill_name="demo_skill")

    # 演示1: 学习经验
    print("\n1. 学习经验")
    print("-" * 40)
    result = skill.execute(
        action="learn",
        tip="使用JSON格式返回结果更易于解析",
        context="API响应处理",
        success=True
    )
    print(f"结果: {result}")

    result = skill.execute(
        action="learn",
        tip="在处理用户输入前先验证格式",
        context="输入验证",
        success=True
    )
    print(f"结果: {result}")

    # 演示2: 获取当前阶段
    print("\n2. 获取进化阶段")
    print("-" * 40)
    result = skill.execute(action="get_stage")
    print(f"当前阶段: {result.data['stage']}")
    print(f"描述: {result.data['description']}")

    # 演示3: 获取经验提示
    print("\n3. 获取经验提示")
    print("-" * 40)
    result = skill.execute(action="get_tips")
    print(f"经验数: {result.data['count']}")
    for tip in result.data['tips']:
        print(f"  - {tip}")

    # 演示4: 记录性能指标
    print("\n4. 记录性能指标")
    print("-" * 40)
    result = skill.execute(
        action="record_metric",
        metric_name="database_query",
        value=45.6,
        unit="ms"
    )
    print(f"结果: {result}")

    # 演示5: 执行进化
    print("\n5. 执行进化")
    print("-" * 40)
    result = skill.execute(action="evolve")
    print(f"进化建议:")
    for s in result.data['suggestions']:
        print(f"  - {s}")

    # 演示6: 获取历史
    print("\n6. 获取历史记录")
    print("-" * 40)
    result = skill.execute(action="history")
    print(f"历史总数: {result.data['total_count']}")

    print("\n" + "=" * 60)
    print("演示完成！")
    print("=" * 60)

    return skill


if __name__ == "__main__":
    main()
