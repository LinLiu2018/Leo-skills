# -*- coding: utf-8 -*-
"""
brainstorming_skill - 头脑风暴协作技能

在实现之前探索用户意图、需求和设计。
通过自然协作对话帮助将想法转化为完全形成的设计和规范。
基于 obra/superpowers 的 brainstorming 技能。
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from enum import Enum


class BrainstormingPhase(Enum):
    """头脑风暴阶段"""
    UNDERSTANDING = "understanding"  # 理解想法
    EXPLORING = "exploring"          # 探索方法
    PRESENTING = "presenting"        # 呈现设计
    DOCUMENTING = "documenting"      # 文档化


@dataclass
class DesignSection:
    """设计小节"""
    title: str
    content: str
    word_count: int = 0
    validated: bool = False


@dataclass
class BrainstormingResult:
    """头脑风暴结果"""
    status: str
    phase: str
    message: str
    design_sections: List[DesignSection] = field(default_factory=list)
    questions_asked: List[str] = field(default_factory=list)
    design_doc_path: Optional[str] = None
    error: Optional[str] = None


class BrainstormingSkill:
    """
    头脑风暴技能 - 创造性设计探索

    功能：
    - 理解用户意图和需求
    - 探索多种设计方案
    - 分节呈现设计并验证
    - 生成设计文档

    流程：
    1. 理解想法 → 2. 探索方法 → 3. 呈现设计 → 4. 文档化
    """

    def __init__(self, docs_dir: str = "docs/plans"):
        self.name = "brainstorming_skill"
        self.version = "1.0.0"
        self.description = "头脑风暴协作技能 - 将想法转化为设计"
        self.docs_dir = Path(docs_dir)
        self.current_phase = BrainstormingPhase.UNDERSTANDING
        self.session_data = {
            "purpose": "",
            "constraints": [],
            "success_criteria": [],
            "approaches": [],
            "selected_approach": None
        }

    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        执行技能主入口

        Args:
            action: 动作类型 (understand/explore/present/document)
            topic: 讨论主题
            question: 要问的问题
            answer: 用户回答
            approach_options: 可选方案
            selected: 选中的方案
            design_section: 设计小节内容
            validated: 是否已验证

        Returns:
            Dict 包含执行结果
        """
        action = kwargs.get("action", "understand")

        try:
            if action == "understand":
                result = self.understand_idea(
                    topic=kwargs.get("topic", ""),
                    question=kwargs.get("question", ""),
                    answer=kwargs.get("answer", "")
                )
            elif action == "explore":
                result = self.explore_approaches(
                    approaches=kwargs.get("approach_options", [])
                )
            elif action == "select":
                result = self.select_approach(
                    selected=kwargs.get("selected", ""),
                    reason=kwargs.get("reason", "")
                )
            elif action == "present":
                result = self.present_design(
                    section_title=kwargs.get("section_title", ""),
                    content=kwargs.get("design_section", ""),
                    validated=kwargs.get("validated", False)
                )
            elif action == "document":
                result = self.document_design(
                    topic=kwargs.get("topic", ""),
                    sections=kwargs.get("sections", [])
                )
            else:
                return {
                    "status": "error",
                    "skill": self.name,
                    "error": f"Unknown action: {action}"
                }

            return {
                "status": result.status,
                "skill": self.name,
                "action": action,
                "result": result
            }

        except Exception as e:
            return {
                "status": "error",
                "skill": self.name,
                "action": action,
                "error": str(e)
            }

    def understand_idea(
        self,
        topic: str,
        question: str = "",
        answer: str = ""
    ) -> BrainstormingResult:
        """
        理解想法阶段 - 一次问一个问题

        Args:
            topic: 讨论主题
            question: 要问的问题
            answer: 用户回答

        Returns:
            BrainstormingResult 理解结果
        """
        self.current_phase = BrainstormingPhase.UNDERSTANDING

        questions_to_ask = []

        if not question:
            # 初始问题
            questions_to_ask = [
                "这个功能的目的是什么？（解决什么问题）",
                "用户是谁？他们的主要痛点是什么？",
                "有什么约束条件吗？（技术、时间、资源）",
                "成功标准是什么？如何知道这个功能完成了？"
            ]
        else:
            # 记录答案
            if "目的" in question or "解决" in question:
                self.session_data["purpose"] = answer
            elif "约束" in question:
                self.session_data["constraints"].append(answer)
            elif "成功" in question:
                self.session_data["success_criteria"].append(answer)

            # 根据已有信息决定下一个问题
            if not self.session_data["purpose"]:
                questions_to_ask = ["这个功能的目的是什么？（解决什么问题）"]
            elif len(self.session_data["constraints"]) < 2:
                questions_to_ask = ["还有其他约束条件吗？"]
            elif len(self.session_data["success_criteria"]) < 2:
                questions_to_ask = ["还有其他成功标准吗？"]
            else:
                return BrainstormingResult(
                    status="success",
                    phase="understanding_complete",
                    message="已充分理解需求，可以进入探索阶段",
                    questions_asked=[question] if question else []
                )

        return BrainstormingResult(
            status="in_progress",
            phase="understanding",
            message="继续了解需求",
            questions_asked=questions_to_ask[:1]  # 一次只问一个问题
        )

    def explore_approaches(
        self,
        approaches: List[Dict[str, Any]]
    ) -> BrainstormingResult:
        """
        探索方法阶段 - 提出 2-3 种不同的方法及权衡

        Args:
            approaches: 可选方案列表

        Returns:
            BrainstormingResult 探索结果
        """
        self.current_phase = BrainstormingPhase.EXPLORING

        if not approaches:
            # 生成默认的方案建议
            default_approaches = [
                {
                    "name": "简洁方案",
                    "description": "实现核心功能，保持简单",
                    "pros": ["开发快", "易维护", "风险低"],
                    "cons": ["功能有限", "扩展性一般"],
                    "recommended": True
                },
                {
                    "name": "完整方案",
                    "description": "实现所有功能，包括高级特性",
                    "pros": ["功能完整", "扩展性好"],
                    "cons": ["开发时间长", "复杂度高"],
                    "recommended": False
                },
                {
                    "name": "渐进方案",
                    "description": "先实现MVP，再迭代增强",
                    "pros": ["快速上线", "可收集反馈", "风险可控"],
                    "cons": ["初期功能简单", "需要多轮迭代"],
                    "recommended": False
                }
            ]

            return BrainstormingResult(
                status="in_progress",
                phase="exploring",
                message="建议以下3种方案，请选择一个",
                questions_asked=[
                    "您倾向于哪种方案？（请输入方案名称）"
                ]
            )

        self.session_data["approaches"] = approaches

        return BrainstormingResult(
            status="success",
            phase="exploring_complete",
            message=f"已记录 {len(approaches)} 种方案",
            questions_asked=[]
        )

    def select_approach(
        self,
        selected: str,
        reason: str = ""
    ) -> BrainstormingResult:
        """
        选择方案

        Args:
            selected: 选中的方案名称
            reason: 选择理由

        Returns:
            BrainstormingResult 选择结果
        """
        self.session_data["selected_approach"] = {
            "name": selected,
            "reason": reason
        }

        return BrainstormingResult(
            status="success",
            phase="approach_selected",
            message=f"已选择方案: {selected}",
            questions_asked=["准备好呈现详细设计了吗？"]
        )

    def present_design(
        self,
        section_title: str,
        content: str,
        validated: bool = False
    ) -> BrainstormingResult:
        """
        呈现设计阶段 - 分节呈现，每节验证

        Args:
            section_title: 小节标题
            content: 内容
            validated: 是否已验证

        Returns:
            BrainstormingResult 呈现结果
        """
        self.current_phase = BrainstormingPhase.PRESENTING

        section = DesignSection(
            title=section_title,
            content=content,
            word_count=len(content),
            validated=validated
        )

        if not validated:
            return BrainstormingResult(
                status="in_progress",
                phase="presenting",
                message=f"请审阅 '{section_title}' 小节（{len(content)} 字）",
                design_sections=[section],
                questions_asked=["这部分看起来正确吗？需要修改吗？"]
            )

        return BrainstormingResult(
            status="success",
            phase="section_validated",
            message=f"'{section_title}' 已确认",
            design_sections=[section]
        )

    def document_design(
        self,
        topic: str,
        sections: List[Dict[str, str]]
    ) -> BrainstormingResult:
        """
        文档化设计阶段 - 写入设计文档

        Args:
            topic: 主题
            sections: 设计小节列表

        Returns:
            BrainstormingResult 文档化结果
        """
        self.current_phase = BrainstormingPhase.DOCUMENTING

        # 创建文档目录
        self.docs_dir.mkdir(parents=True, exist_ok=True)

        # 生成文件名
        date_str = datetime.now().strftime("%Y-%m-%d")
        topic_slug = topic.lower().replace(" ", "-").replace("_", "-")[:30]
        filename = f"{date_str}-{topic_slug}-design.md"
        filepath = self.docs_dir / filename

        # 生成文档内容
        doc_content = self._generate_design_doc(topic, sections)

        # 写入文件
        filepath.write_text(doc_content, encoding="utf-8")

        return BrainstormingResult(
            status="success",
            phase="documenting_complete",
            message=f"设计文档已保存: {filepath}",
            design_doc_path=str(filepath)
        )

    def _generate_design_doc(
        self,
        topic: str,
        sections: List[Dict[str, str]]
    ) -> str:
        """生成设计文档内容"""
        content_lines = [
            f"# 设计文档: {topic}",
            "",
            f"**创建时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"**方案**: {self.session_data.get('selected_approach', {}).get('name', '未指定')}",
            "",
            "## 概述",
            "",
            f"**目的**: {self.session_data.get('purpose', '待补充')}",
            "",
            "## 设计详情",
            ""
        ]

        for section in sections:
            content_lines.append(f"### {section.get('title', '未命名')}")
            content_lines.append("")
            content_lines.append(section.get('content', ''))
            content_lines.append("")

        content_lines.extend([
            "## 约束与假设",
            ""
        ])
        for constraint in self.session_data.get("constraints", []):
            content_lines.append(f"- {constraint}")

        content_lines.extend([
            "",
            "## 成功标准",
            ""
        ])
        for criterion in self.session_data.get("success_criteria", []):
            content_lines.append(f"- [ ] {criterion}")

        content_lines.extend([
            "",
            "## 后续步骤",
            "",
            "- [ ] 创建实现计划",
            "- [ ] 设置开发环境",
            "- [ ] 开始编码实现",
            "",
            "---",
            "",
            "*此文档由头脑风暴技能生成*"
        ])

        return "\n".join(content_lines)

    def get_session_summary(self) -> Dict[str, Any]:
        """获取会话摘要"""
        return {
            "phase": self.current_phase.value,
            "data": self.session_data,
            "ready_for_implementation": (
                self.current_phase == BrainstormingPhase.DOCUMENTING and
                self.session_data.get("selected_approach") is not None
            )
        }

    def get_capabilities(self) -> Dict[str, Any]:
        """获取技能能力信息"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "phases": [p.value for p in BrainstormingPhase],
            "output": "design_document"
        }


# 向后兼容
Brainstorming_Skill = BrainstormingSkill


def main():
    """入口函数 - 演示用法"""
    print("=" * 60)
    print("Brainstorming Skill - 演示")
    print("=" * 60)

    skill = BrainstormingSkill()

    # 演示1: 理解阶段
    print("\n1. 理解阶段")
    print("-" * 40)
    result = skill.understand_idea(topic="开发一个待办事项应用")
    print(f"问题: {result.questions_asked[0] if result.questions_asked else '无'}")

    # 模拟回答后继续
    result = skill.understand_idea(
        topic="开发一个待办事项应用",
        question="这个功能的目的是什么？",
        answer="帮助用户管理日常任务，提高效率"
    )
    print(f"状态: {result.phase}")

    # 演示2: 探索阶段
    print("\n2. 探索阶段")
    print("-" * 40)
    result = skill.explore_approaches(approaches=[])
    print(f"建议方案数: 3")
    print(f"消息: {result.message}")

    # 演示3: 选择方案
    print("\n3. 选择方案")
    print("-" * 40)
    result = skill.select_approach(
        selected="渐进方案",
        reason="可以快速上线并获得用户反馈"
    )
    print(f"消息: {result.message}")

    # 演示4: 呈现设计
    print("\n4. 呈现设计")
    print("-" * 40)
    result = skill.present_design(
        section_title="架构设计",
        content="采用前后端分离架构，前端使用 React，后端使用 FastAPI...",
        validated=True
    )
    print(f"消息: {result.message}")

    print("\n" + "=" * 60)
    print("演示完成！")
    print("=" * 60)

    return skill


if __name__ == "__main__":
    main()
