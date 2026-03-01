# -*- coding: utf-8 -*-
"""
list_todos_skill - 列出TODO技能

分析并优先处理 TODOS.md 中的TODO项，提供实现指导。
基于 obra/superpowers 的 list-todos 技能实现。
"""
from leo_skills.core.base_executor import BaseExecutor

import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class Clarity(Enum):
    """需求清晰度"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3


class ImplementationEase(Enum):
    """实现难度"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3


class ProjectValue(Enum):
    """项目价值"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3


@dataclass
class TodoAnalysis:
    """TODO分析结果"""
    title: str
    priority: str
    effort: str
    multiplier: float
    clarity: Clarity
    ease: ImplementationEase
    value: ProjectValue
    clarity_reason: str = ""
    ease_reason: str = ""
    value_reason: str = ""
    priority_score: float = 0.0
    next_action: str = ""


class ListTodosSkill(BaseExecutor):
    """
    列出TODO技能

    功能：
    - 解析 TODOS.md 中的所有TODO项
    - 分析每个TODO的优先级、难度、价值
    - 计算优先级分数
    - 生成优先排序列表
    - 提供实现建议

    使用场景：
    - 规划工作内容
    - 决定下一步行动
    - 分析TODO质量
    """

    def __init__(self, base_path: str = "."):
        self.name = "list_todos_skill"
        self.version = "1.0.0"
        self.description = "列出TODO技能 - 分析和优先处理TODO项"
        self.base_path = Path(base_path)

    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        执行技能主入口

        Args:
            work_dir: 工作目录
            include_analysis: 是否包含详细分析

        Returns:
            Dict 包含TODO列表和分析
        """
        work_dir = kwargs.get("work_dir", self.base_path)
        include_analysis = kwargs.get("include_analysis", True)

        try:
            todos = self.list_todos(work_dir)

            if include_analysis:
                analyses = [self._analyze_todo(todo) for todo in todos]
                analyses.sort(key=lambda x: x.priority_score, reverse=True)
            else:
                analyses = []

            return {
                "status": "success",
                "skill": self.name,
                "count": len(todos),
                "todos": [
                    {
                        "title": t["title"],
                        "priority": t["priority"],
                        "effort": t["effort"],
                        "completed": t["completed"]
                    }
                    for t in todos
                ],
                "analysis": [
                    {
                        "title": a.title,
                        "score": round(a.priority_score, 1),
                        "clarity": a.clarity.name,
                        "ease": a.ease.name,
                        "value": a.value.name,
                        "next_action": a.next_action
                    }
                    for a in analyses
                ] if analyses else None
            }

        except Exception as e:
            return {
                "status": "error",
                "skill": self.name,
                "error": str(e)
            }

    def list_todos(self, work_dir: Optional[Path] = None) -> List[Dict[str, Any]]:
        """
        列出所有TODO

        Args:
            work_dir: 工作目录

        Returns:
            TODO项列表
        """
        work_dir = Path(work_dir) if work_dir else self.base_path
        todos_path = work_dir / "TODOS.md"

        if not todos_path.exists():
            return []

        try:
            content = todos_path.read_text(encoding="utf-8")
            todos = []

            # 匹配TODO行
            pattern = r"- \[([ x])\] \*\*\[(P\d) / (\w+)(?: x([\d.]+))?\]\*\* (.+?)(?: — (.+))?\s*$"

            for line in content.split("\n"):
                match = re.match(pattern, line)
                if match:
                    checked, priority, effort, multiplier, title, description = match.groups()
                    todos.append({
                        "title": title.strip(),
                        "priority": priority,
                        "effort": effort,
                        "multiplier": float(multiplier) if multiplier else 1.0,
                        "description": description.strip() if description else "",
                        "completed": checked == "x"
                    })

            return todos

        except Exception as e:
            print(f"解析TODO失败: {e}")
            return []

    def _analyze_todo(self, todo: Dict[str, Any]) -> TodoAnalysis:
        """分析单个TODO"""
        title = todo["title"]
        description = todo.get("description", "")

        # 1. 评估需求清晰度
        if description and len(description) > 20:
            clarity = Clarity.HIGH
            clarity_reason = "有详细描述"
        elif description:
            clarity = Clarity.MEDIUM
            clarity_reason = "有简要描述"
        else:
            clarity = Clarity.LOW
            clarity_reason = "仅有标题，无描述"

        # 2. 评估实现难度（基于关键词）
        title_lower = title.lower()
        if any(word in title_lower for word in ["修复", "bug", "fix", "错误"]):
            ease = ImplementationEase.MEDIUM
            ease_reason = "Bug修复，通常有明确范围"
        elif any(word in title_lower for word in ["添加", "add", "新", "new"]):
            ease = ImplementationEase.HIGH
            ease_reason = "新功能，可能需要设计"
        elif any(word in title_lower for word in ["优化", "改进", "refactor"]):
            ease = ImplementationEase.MEDIUM
            ease_reason = "优化改进，需要评估"
        else:
            ease = ImplementationEase.MEDIUM
            ease_reason = "常规任务"

        # 3. 评估项目价值（基于优先级）
        priority = todo.get("priority", "P2")
        if priority == "P0":
            value = ProjectValue.HIGH
            value_reason = "P0 - 关键优先级"
        elif priority == "P1":
            value = ProjectValue.MEDIUM
            value_reason = "P1 - 高优先级"
        else:
            value = ProjectValue.LOW
            value_reason = "P2 - 低优先级"

        # 4. 计算优先级分数
        # Priority = ((Clarity + Ease + (Value × 2)) / 4 × 10) × Multiplier
        base_score = (
            (clarity.value + ease.value + (value.value * 2)) / 4 * 10
        )

        # 如果清晰度低，分数上限为3
        if clarity == Clarity.LOW:
            base_score = min(base_score, 3)

        multiplier = todo.get("multiplier", 1.0)
        final_score = base_score * multiplier

        # 5. 确定下一步行动
        if clarity == Clarity.LOW:
            next_action = "需要澄清需求"
        elif final_score >= 20:
            next_action = "可以开始实现"
        elif final_score >= 15:
            next_action = "准备好实现"
        else:
            next_action = "考虑推迟"

        return TodoAnalysis(
            title=title,
            priority=priority,
            effort=todo.get("effort", "Medium"),
            multiplier=multiplier,
            clarity=clarity,
            ease=ease,
            value=value,
            clarity_reason=clarity_reason,
            ease_reason=ease_reason,
            value_reason=value_reason,
            priority_score=final_score,
            next_action=next_action
        )

    def generate_report(self, analyses: List[TodoAnalysis]) -> str:
        """生成分析报告"""
        lines = [
            "# TODO 分析报告",
            "",
            f"**生成时间:** {__import__('datetime').datetime.now().strftime('%Y-%m-%d')}",
            f"**TODO数量:** {len(analyses)}",
            "",
            "---",
            ""
        ]

        # 按分数排序
        sorted_analyses = sorted(analyses, key=lambda x: x.priority_score, reverse=True)

        for i, analysis in enumerate(sorted_analyses, 1):
            lines.extend([
                f"## {i}. {analysis.title}",
                "",
                f"**优先级分数:** {analysis.priority_score:.1f}/10",
                f"**基础优先级:** {analysis.priority} / {analysis.effort}",
                "",
                "**评估维度:**",
                f"- 需求清晰度: {analysis.clarity.name} — {analysis.clarity_reason}",
                f"- 实现难度: {analysis.ease.name} — {analysis.ease_reason}",
                f"- 项目价值: {analysis.value.name} — {analysis.value_reason}",
                f"- 个人倍数: ×{analysis.multiplier}",
                "",
                f"**建议行动:** {analysis.next_action}",
                "",
                "---",
                ""
            ])

        # 总结表格
        lines.extend([
            "## 总结",
            "",
            "| 排名 | 任务 | 分数 | 建议行动 |",
            "|------|------|------|----------|"
        ])

        for i, analysis in enumerate(sorted_analyses[:10], 1):
            lines.append(
                f"| {i} | {analysis.title[:30]}... | "
                f"{analysis.priority_score:.1f} | {analysis.next_action} |"
            )

        lines.append("")

        return "\n".join(lines)

    def get_capabilities(self) -> Dict[str, Any]:
        """获取技能能力信息"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "features": [
                "todo_parsing",
                "priority_analysis",
                "difficulty_assessment",
                "value_evaluation",
                "score_calculation",
                "report_generation",
                "action_recommendation"
            ],
            "analysis_factors": [
                "requirements_clarity",
                "ease_of_implementation",
                "value_to_project",
                "personal_multiplier"
            ]
        }


# 向后兼容
List_Todos_Skill = ListTodosSkill


def main():
    """入口函数 - 演示用法"""
    print("=" * 60)
    print("List Todos Skill - 演示")
    print("=" * 60)

    skill = ListTodosSkill()

    # 演示: 列出TODO
    print("\n1. 列出TODO")
    print("-" * 40)
    result = skill.execute()
    print(f"状态: {result['status']}")
    print(f"TODO数量: {result['count']}")

    if result['analysis']:
        print("\n优先级分析:")
        for item in result['analysis'][:3]:
            print(f"  - {item['title']}: {item['score']}分 ({item['next_action']})")

    print("\n" + "=" * 60)
    print("演示完成！")
    print("=" * 60)

    return skill


if __name__ == "__main__":
    main()
