# -*- coding: utf-8 -*-
"""
Continuous Learning Skill
========================

参考 ECC Continuous Learning v2 设计
自动从交互中提取模式并学习

Author: Leo AI System
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import logging

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from base import BaseSkill, SkillResult

logger = logging.getLogger(__name__)


@dataclass
class LearnedPattern:
    """学习到的模式"""
    id: str
    trigger: str  # 触发条件
    action: str    # 执行动作
    success_count: int = 0
    failure_count: int = 0
    confidence: float = 0.0
    last_used: str = ""
    examples: List[str] = None
    created_at: str = ""

    def __post_init__(self):
        if self.examples is None:
            self.examples = []
        if not self.created_at:
            self.created_at = datetime.now().isoformat()

    def update_confidence(self):
        """更新置信度"""
        total = self.success_count + self.failure_count
        if total > 0:
            self.confidence = self.success_count / total
            # 考虑使用次数的衰减
            self.confidence *= min(1.0, total / 10)


@dataclass
class InteractionRecord:
    """交互记录"""
    timestamp: str
    trigger: str  # 触发输入
    action: str    # 执行的操作
    skill_used: str
    success: bool
    duration_ms: float
    error: str = ""


class ContinuousLearningSkill(BaseSkill):
    """
    Continuous Learning Skill

    持续学习系统 - 从交互中自动学习
    """

    def __init__(self):
        super().__init__()
        self.storage_dir = Path("leo_knowledge/learning")
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.patterns_file = self.storage_dir / "learned_patterns.json"
        self.history_file = self.storage_dir / "interaction_history.json"
        self.patterns: Dict[str, LearnedPattern] = {}
        self.history: List[InteractionRecord] = []
        self._load()

    def _load(self):
        """加载已有数据"""
        # 加载模式
        if self.patterns_file.exists():
            try:
                with open(self.patterns_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for p in data:
                        pattern = LearnedPattern(**p)
                        self.patterns[pattern.id] = pattern
            except Exception as e:
                logger.warning(f"加载模式失败: {e}")

        # 加载历史
        if self.history_file.exists():
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for h in data:
                        self.history.append(InteractionRecord(**h))
            except Exception as e:
                logger.warning(f"加载历史失败: {e}")

    def _save(self):
        """保存数据"""
        # 保存模式
        patterns_data = [asdict(p) for p in self.patterns.values()]
        with open(self.patterns_file, "w", encoding="utf-8") as f:
            json.dump(patterns_data, f, ensure_ascii=False, indent=2)

        # 保存历史（只保留最近1000条）
        recent_history = self.history[-1000:]
        history_data = [asdict(h) for h in recent_history]
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(history_data, f, ensure_ascii=False, indent=2)

    @property
    def name(self) -> str:
        return "continuous_learning"

    @property
    def description(self) -> str:
        return "持续学习系统 - 从交互中自动提取模式"

    def execute(self, action: str = "default", **kwargs) -> SkillResult:
        """
        执行学习操作

        Actions:
            record: 记录一次交互
            analyze: 分析历史提取模式
            suggest: 获取学习建议
            patterns: 查看已学模式
            evolve: 演化本能
        """
        if action == "record":
            return self._record_interaction(**kwargs)
        elif action == "analyze":
            return self._analyze_and_learn()
        elif action == "suggest":
            return self._get_suggestions(kwargs.get("current_input", ""))
        elif action == "patterns":
            return self._show_patterns()
        elif action == "evolve":
            return self._evolve_to_instincts()
        else:
            return self._show_patterns()

    def _record_interaction(
        self,
        trigger: str,
        action: str,
        skill_used: str,
        success: bool,
        duration_ms: float = 0,
        error: str = ""
    ) -> SkillResult:
        """记录一次交互"""
        record = InteractionRecord(
            timestamp=datetime.now().isoformat(),
            trigger=trigger,
            action=action,
            skill_used=skill_used,
            success=success,
            duration_ms=duration_ms,
            error=error
        )

        self.history.append(record)

        # 如果成功，尝试学习模式
        if success and len(trigger) > 5:
            self._learn_from_interaction(trigger, action, skill_used)

        self._save()

        return SkillResult.ok(
            data={"record_id": len(self.history)},
            message=f"记录交互: {action[:30]}... (成功: {success})"
        )

    def _learn_from_interaction(self, trigger: str, action: str, skill: str) -> Optional[LearnedPattern]:
        """从交互中学习"""
        # 生成模式ID
        pattern_key = f"{skill}:{action[:20]}"
        pattern_id = hashlib.md5(pattern_key.encode()).hexdigest()[:8]

        if pattern_id in self.patterns:
            # 更新已有模式
            pattern = self.patterns[pattern_id]
            pattern.success_count += 1
            pattern.last_used = datetime.now().isoformat()
            if trigger not in pattern.examples:
                pattern.examples.append(trigger[:50])
                pattern.examples = pattern.examples[-5:]  # 只保留5个例子
            pattern.update_confidence()
        else:
            # 创建新模式
            pattern = LearnedPattern(
                id=pattern_id,
                trigger=trigger[:50],
                action=action[:30],
                success_count=1,
                examples=[trigger[:50]]
            )
            self.patterns[pattern_id] = pattern

        return self.patterns.get(pattern_id)

    def _analyze_and_learn(self) -> SkillResult:
        """分析历史并学习"""
        if len(self.history) < 5:
            return SkillResult.ok(
                data={"learned": 0},
                message="历史记录太少，无法学习"
            )

        # 分析成功模式
        skill_success = Counter()
        skill_usage = Counter()

        for record in self.history[-100:]:
            skill_usage[record.skill_used] += 1
            if record.success:
                skill_success[record.skill_used] += 1

        # 生成分析报告
        analysis = {
            "total_interactions": len(self.history),
            "skill_success_rate": {},
            "high_confidence_patterns": [],
            "suggestions": []
        }

        for skill, count in skill_usage.items():
            success_count = skill_success[skill]
            rate = success_count / count if count > 0 else 0
            analysis["skill_success_rate"][skill] = {
                "total": count,
                "success": success_count,
                "rate": round(rate, 2)
            }

        # 找出高置信度模式
        for pattern in self.patterns.values():
            if pattern.confidence >= 0.8 and pattern.success_count >= 3:
                analysis["high_confidence_patterns"].append({
                    "id": pattern.id,
                    "action": pattern.action,
                    "confidence": pattern.confidence,
                    "successes": pattern.success_count,
                    "examples": pattern.examples
                })

        # 生成建议
        if skill_usage:
            best_skill = skill_success.most_common(1)[0] if skill_success else None
            if best_skill:
                analysis["suggestions"].append(f"'{best_skill[0]}' 成功率最高，建议优先使用")

        return SkillResult.ok(
            data=analysis,
            message=f"分析完成 | 模式数: {len(self.patterns)}"
        )

    def _get_suggestions(self, current_input: str) -> SkillResult:
        """获取学习建议"""
        suggestions = []

        # 查找相关模式
        if current_input:
            input_lower = current_input.lower()
            for pattern in self.patterns.values():
                if pattern.action.lower() in input_lower or any(
                    w in input_lower for w in pattern.trigger.lower().split()[:3]
                ):
                    if pattern.confidence >= 0.6:
                        suggestions.append({
                            "type": "pattern_match",
                            "action": pattern.action,
                            "skill": pattern.skill_used if hasattr(pattern, 'skill_used') else "unknown",
                            "confidence": pattern.confidence,
                            "message": f"建议使用 '{pattern.action}' (置信度: {pattern.confidence:.0%})"
                        })

        # 基于历史的建议
        if len(self.history) >= 10:
            recent_success_rate = sum(1 for h in self.history[-10:] if h.success) / 10
            if recent_success_rate < 0.5:
                suggestions.append({
                    "type": "warning",
                    "message": "最近10次交互成功率较低，建议检查系统状态"
                })

        return SkillResult.ok(
            data={"suggestions": suggestions[:5]},
            message=f"生成 {len(suggestions)} 条建议"
        )

    def _show_patterns(self) -> SkillResult:
        """显示已学模式"""
        patterns_list = [
            {
                "id": p.id,
                "action": p.action,
                "confidence": round(p.confidence, 2),
                "successes": p.success_count,
                "failures": p.failure_count,
                "examples": p.examples[:2]
            }
            for p in sorted(self.patterns.values(), key=lambda x: x.confidence, reverse=True)
        ]

        return SkillResult.ok(
            data={"patterns": patterns_list, "total": len(patterns_list)},
            message=f"已学习 {len(patterns_list)} 个模式"
        )

    def _evolve_to_instincts(self) -> SkillResult:
        """将高置信度模式演化为本能"""
        try:
            from leo_skills.core.instincts_skill import get_instinct_registry
            registry = get_instinct_registry()

            evolved = []
            for pattern in self.patterns.values():
                if pattern.confidence >= 0.9 and pattern.success_count >= 5:
                    instinct = registry.learn(
                        name=f"learned_{pattern.id}",
                        trigger_pattern=pattern.trigger[:30],
                        action_skill=pattern.action,
                        description=f"从历史学习中提取: {pattern.action}",
                        examples=pattern.examples
                    )
                    evolved.append(instinct.id)

            self._save()

            return SkillResult.ok(
                data={"evolved": evolved, "count": len(evolved)},
                message=f"已演化 {len(evolved)} 个本能"
            )
        except Exception as e:
            return SkillResult.fail(f"演化失败: {e}")

    def get_actions(self) -> List[str]:
        return ["default", "record", "analyze", "suggest", "patterns", "evolve"]


# 全局实例
_learning_skill: Optional[ContinuousLearningSkill] = None


def get_learning_skill() -> ContinuousLearningSkill:
    """获取学习实例"""
    global _learning_skill
    if _learning_skill is None:
        _learning_skill = ContinuousLearningSkill()
    return _learning_skill


def record_interaction(**kwargs) -> SkillResult:
    """快捷记录交互"""
    return get_learning_skill().execute(action="record", **kwargs)


if __name__ == "__main__":
    skill = ContinuousLearningSkill()
    print(skill.execute("patterns"))
