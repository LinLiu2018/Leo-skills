# -*- coding: utf-8 -*-
"""
long_context_handler - 长上下文处理技能

处理长上下文窗口的最佳实践，包括信息提取、摘要生成和关键内容识别。
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class ContentType(Enum):
    """内容类型"""
    CODE = "code"
    DOCS = "docs"
    LOG = "log"
    CONVERSATION = "conversation"
    MIXED = "mixed"


@dataclass
class ExtractedContent:
    """提取的内容"""
    type: ContentType
    content: str
    importance: str  # high, medium, low
    position: str  # start, middle, end


@dataclass
class ContextSummary:
    """上下文摘要"""
    total_length: int
    extracted_items: List[ExtractedContent] = field(default_factory=list)
    key_topics: List[str] = field(default_factory=list)
    action_items: List[str] = field(default_factory=list)


class LongContextHandlerSkill:
    """
    长上下文处理技能

    处理长上下文窗口的最佳实践：
    1. 信息提取：从长上下文中提取关键信息
    2. 摘要生成：生成压缩摘要
    3. 关键内容识别：识别重要代码/文档片段
    """

    def __init__(self):
        self.name = "long_context_handler_skill"
        self.version = "1.0.0"
        self.description = "长上下文窗口处理和优化"
        self.category = "prompt_engineering"

    def execute(
        self,
        context: str,
        max_length: int = 32000,
        extract_topics: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        执行长上下文处理

        Args:
            context: 原始上下文
            max_length: 最大长度
            extract_topics: 是否提取主题

        Returns:
            处理结果
        """
        try:
            length = len(context)

            if length <= max_length:
                return {
                    "status": "success",
                    "needs_truncation": False,
                    "message": "上下文长度在限制内，无需处理"
                }

            # 提取关键内容
            extracted = self._extract_key_content(context)

            # 生成摘要
            summary = self._generate_summary(context, extracted)

            return {
                "status": "success",
                "needs_truncation": True,
                "original_length": length,
                "max_length": max_length,
                "extracted": [
                    {"type": e.type.value, "content": e.content[:200], "importance": e.importance}
                    for e in extracted
                ],
                "summary": summary,
                "truncated_context": self._create_truncated_context(context, extracted, max_length)
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "skill": self.name
            }

    def _extract_key_content(self, context: str) -> List[ExtractedContent]:
        """提取关键内容"""
        extracted = []

        # 识别代码块
        if "```" in context:
            extracted.append(ExtractedContent(
                type=ContentType.CODE,
                content="代码块已识别",
                importance="high",
                position="distributed"
            ))

        # 识别文档
        if "# " in context or "## " in context:
            extracted.append(ExtractedContent(
                type=ContentType.DOCS,
                content="文档结构已识别",
                importance="high",
                position="start"
            ))

        return extracted

    def _generate_summary(self, context: str, extracted: List[ExtractedContent]) -> str:
        """生成摘要"""
        topics = []
        if "问题" in context or "bug" in context.lower():
            topics.append("问题修复")
        if "功能" in context or "feature" in context.lower():
            topics.append("功能开发")
        if "测试" in context or "test" in context.lower():
            topics.append("测试相关")

        return f"上下文包含 {len(topics)} 个主要主题: {', '.join(topics)}"

    def _create_truncated_context(
        self,
        context: str,
        extracted: List[ExtractedContent],
        max_length: int
    ) -> str:
        """创建截断的上下文"""
        # 保留开头和结尾，中间截断
        head_size = max_length // 3
        tail_size = max_length // 3

        head = context[:head_size]
        tail = context[-tail_size:] if len(context) > head_size else ""

        truncated = head + "\n\n[...上下文已截断...]\n\n" + tail

        return truncated[:max_length]


def main():
    """入口函数"""
    return LongContextHandlerSkill()


if __name__ == "__main__":
    skill = main()

