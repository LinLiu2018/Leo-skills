# -*- coding: utf-8 -*-
"""
receiving_code_review_skill - 接收代码审查技能

基于 obra/superpowers 的 receiving-code-review 技能。
验证后再实现。询问后再假设。技术正确性高于社交舒适度。
"""
from leo_skills.core.base_executor import BaseExecutor

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class FeedbackType(Enum):
    """反馈类型"""
    CRITICAL = "critical"      # 阻塞问题（破坏、安全）
    IMPORTANT = "important"    # 重要问题
    MINOR = "minor"            # 次要问题
    SUGGESTION = "suggestion"  # 建议


class FeedbackSource(Enum):
    """反馈来源"""
    HUMAN = "human"
    EXTERNAL = "external"
    SUBAGENT = "subagent"


class ResponseAction(Enum):
    """响应动作"""
    IMPLEMENT = "implement"
    CLARIFY = "clarify"
    REFUTE = "refute"
    DEFER = "defer"


@dataclass
class ReviewFeedback:
    """审查反馈项"""
    id: str
    description: str
    feedback_type: FeedbackType
    source: FeedbackSource
    location: Optional[str] = None
    suggestion: str = ""
    action_taken: str = ""
    status: str = "pending"  # pending, clarified, implemented, refuted, deferred


@dataclass
class CodeReviewResult:
    """代码审查结果"""
    status: str
    feedback_items: List[ReviewFeedback] = field(default_factory=list)
    implemented: int = 0
    refuted: int = 0
    deferred: int = 0
    needs_clarification: int = 0
    message: str = ""


class ReceivingCodeReviewSkill(BaseExecutor):
    """
    接收代码审查技能

    核心理念：验证后再实现。询问后再假设。技术正确性高于社交舒适度。
    """

    def __init__(self):
        self.name = "receiving_code_review_skill"
        self.version = "1.0.0"
        self.description = "接收代码审查反馈，技术验证后实施"
        self.category = "collaboration"

    def execute(
        self,
        feedback: List[Dict[str, Any]],
        source: str = "external",
        project_context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        执行接收代码审查技能

        Args:
            feedback: 反馈项列表
            source: 反馈来源 (human/external/subagent)
            project_context: 项目上下文

        Returns:
            处理结果
        """
        try:
            source_enum = FeedbackSource(source)
            items = self._parse_feedback(feedback, source_enum)

            # 分类反馈
            categorized = self._categorize_feedback(items)

            # 处理每类反馈
            result = self._process_feedback(items, source_enum, project_context)

            return {
                "status": "success",
                "result": result,
                "summary": {
                    "total": len(items),
                    "critical": len(categorized["critical"]),
                    "important": len(categorized["important"]),
                    "minor": len(categorized["minor"]),
                    "implemented": result.implemented,
                    "refuted": result.refuted,
                    "needs_clarification": result.needs_clarification
                }
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "skill": self.name
            }

    def _parse_feedback(
        self,
        feedback: List[Dict[str, Any]],
        source: FeedbackSource
    ) -> List[ReviewFeedback]:
        """解析反馈列表"""
        items = []
        for i, item in enumerate(feedback, 1):
            items.append(ReviewFeedback(
                id=f"F-{i:03d}",
                description=item.get("description", ""),
                feedback_type=FeedbackType(item.get("type", "suggestion")),
                source=source,
                location=item.get("location"),
                suggestion=item.get("suggestion", "")
            ))
        return items

    def _categorize_feedback(
        self,
        items: List[ReviewFeedback]
    ) -> Dict[str, List[ReviewFeedback]]:
        """分类反馈"""
        return {
            "critical": [i for i in items if i.feedback_type == FeedbackType.CRITICAL],
            "important": [i for i in items if i.feedback_type == FeedbackType.IMPORTANT],
            "minor": [i for i in items if i.feedback_type in (FeedbackType.MINOR, FeedbackType.SUGGESTION)]
        }

    def _process_feedback(
        self,
        items: List[ReviewFeedback],
        source: FeedbackSource,
        project_context: Optional[Dict[str, Any]]
    ) -> CodeReviewResult:
        """处理反馈"""
        result = CodeReviewResult(status="processing")

        for item in items:
            action = self._determine_action(item, source)

            if action == ResponseAction.CLARIFY:
                item.status = "needs_clarification"
                result.needs_clarification += 1
            elif action == ResponseAction.IMPLEMENT:
                item.status = "implemented"
                item.action_taken = self._generate_implementation_note(item)
                result.implemented += 1
            elif action == ResponseAction.REFUTE:
                item.status = "refuted"
                item.action_taken = self._generate_refutation_note(item)
                result.refuted += 1
            else:
                item.status = "deferred"
                result.deferred += 1

            result.feedback_items.append(item)

        result.status = "completed"
        result.message = self._generate_summary(result)
        return result

    def _determine_action(
        self,
        item: ReviewFeedback,
        source: FeedbackSource
    ) -> ResponseAction:
        """确定响应动作"""
        # 关键问题必须处理
        if item.feedback_type == FeedbackType.CRITICAL:
            return ResponseAction.IMPLEMENT

        # 外部审查者需要验证
        if source == FeedbackSource.EXTERNAL:
            # 如果建议看起来可疑，需要澄清
            if self._is_suspicious(item):
                return ResponseAction.CLARIFY

        # 不清楚的项需要澄清
        if self._is_unclear(item):
            return ResponseAction.CLARIFY

        # 重要问题建议实现
        if item.feedback_type == FeedbackType.IMPORTANT:
            return ResponseAction.IMPLEMENT

        # 次要问题可以延后
        return ResponseAction.DEFER

    def _is_suspicious(self, item: ReviewFeedback) -> bool:
        """检查建议是否可疑"""
        suspicious_keywords = [
            "完全重写", "大规模重构", "改变架构",
            "delete all", "rewrite", "redesign everything"
        ]
        desc_lower = item.description.lower()
        return any(kw in desc_lower for kw in suspicious_keywords)

    def _is_unclear(self, item: ReviewFeedback) -> bool:
        """检查项是否不清楚"""
        # 如果描述少于5个字或缺少具体位置
        return len(item.description) < 10 or not item.location

    def _generate_implementation_note(self, item: ReviewFeedback) -> str:
        """生成实现说明"""
        return f"已修复: {item.description[:50]}..."

    def _generate_refutation_note(self, item: ReviewFeedback) -> str:
        """生成反驳说明"""
        return f"经检查，此建议不适用: {item.description[:50]}..."

    def _generate_summary(self, result: CodeReviewResult) -> str:
        """生成总结"""
        return (
            f"代码审查处理完成: "
            f"已实施 {result.implemented}, "
            f"已反驳 {result.refuted}, "
            f"需澄清 {result.needs_clarification}, "
            f"延后 {result.deferred}"
        )

    def generate_response_guidelines(self) -> str:
        """生成响应指南"""
        return """
接收代码审查指南:

1. 阅读完整反馈，不做反应
2. 理解：用自己的话重述要求（或询问）
3. 验证：检查代码库实际情况
4. 评估：技术上看对 THIS 代码库是否合理？
5. 响应：技术确认或合理的反驳
6. 实现：一次一项，测试每个

禁止的响应:
- "你完全正确！"（明确违反规则）
- "说得好！" / "优秀的反馈！"（表演性）
- "我现在就实现"（验证之前）

应该:
- 重述技术要求
- 询问澄清问题
- 如果错误则用技术推理反驳
- 直接开始工作（行动 > 语言）
        """.strip()


def main():
    """入口函数"""
    return ReceivingCodeReviewSkill()


if __name__ == "__main__":
    skill = main()
