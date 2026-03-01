# -*- coding: utf-8 -*-
"""
add_todo_skill - 添加TODO技能

向 TODOS.md 添加格式化的TODO项，与 /list-todos 和 /run-todos 集成。
基于 obra/superpowers 的 add-todo 技能实现。
"""
from leo_skills.core.base_executor import BaseExecutor

import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum


class Priority(Enum):
    """优先级"""
    P0 = "P0"  # Critical
    P1 = "P1"  # High
    P2 = "P2"  # Low


class Effort(Enum):
    """工作量"""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


@dataclass
class TodoItem:
    """TODO项"""
    title: str
    priority: Priority
    effort: Effort
    description: str = ""
    section: str = "In Progress"
    multiplier: float = 1.0


class AddTodoSkill(BaseExecutor):
    """
    添加TODO技能

    功能：
    - 创建格式化的TODO项
    - 管理 TODOS.md 文件
    - 支持优先级和工作量标记
    - 自动分节管理

    使用场景：
    - 记录新任务
    - 跟踪Bug修复
    - 规划功能开发
    """

    DEFAULT_TEMPLATE = """# TODO

## In Progress

## Future Concepts

"""

    def __init__(self, base_path: str = "."):
        self.name = "add_todo_skill"
        self.version = "1.0.0"
        self.description = "添加TODO技能 - 向TODOS.md添加格式化的TODO项"
        self.base_path = Path(base_path)

    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        执行技能主入口

        Args:
            title: TODO标题
            priority: 优先级 (P0/P1/P2)
            effort: 工作量 (Low/Medium/High)
            description: 描述（可选）
            section: 所属章节 (In Progress/Future Concepts)
            multiplier: 优先级倍数（可选）
            work_dir: 工作目录

        Returns:
            Dict 包含添加结果
        """
        work_dir = kwargs.get("work_dir", self.base_path)

        try:
            todo = TodoItem(
                title=kwargs.get("title", "未命名任务"),
                priority=Priority(kwargs.get("priority", "P1")),
                effort=Effort(kwargs.get("effort", "Medium")),
                description=kwargs.get("description", ""),
                section=kwargs.get("section", "In Progress"),
                multiplier=kwargs.get("multiplier", 1.0)
            )

            result = self.add_todo(todo, work_dir)
            return {
                "status": "success",
                "skill": self.name,
                "todo_added": result
            }

        except Exception as e:
            return {
                "status": "error",
                "skill": self.name,
                "error": str(e)
            }

    def add_todo(self, todo: TodoItem, work_dir: Optional[Path] = None) -> Dict[str, Any]:
        """
        添加TODO项

        Args:
            todo: TODO项
            work_dir: 工作目录

        Returns:
            Dict 包含添加结果
        """
        work_dir = Path(work_dir) if work_dir else self.base_path
        todos_path = work_dir / "TODOS.md"

        # 1. 确保文件存在
        if not todos_path.exists():
            todos_path.write_text(self.DEFAULT_TEMPLATE, encoding="utf-8")

        # 2. 读取文件内容
        content = todos_path.read_text(encoding="utf-8")

        # 3. 格式化TODO行
        todo_line = self._format_todo(todo)

        # 4. 插入到正确位置
        section_heading = f"## {todo.section}"

        if section_heading not in content:
            # 创建新章节
            content += f"\n{section_heading}\n\n{todo_line}\n"
        else:
            # 在章节末尾插入
            pattern = rf"({re.escape(section_heading)}.*?)(\n## |\Z)"
            match = re.search(pattern, content, re.DOTALL)

            if match:
                section_content = match.group(1)
                # 在章节末尾添加TODO
                new_section = section_content.rstrip() + f"\n{todo_line}\n"
                content = content.replace(section_content, new_section)
            else:
                # 追加到文件
                content += f"\n{todo_line}\n"

        # 5. 写入文件
        todos_path.write_text(content, encoding="utf-8")

        return {
            "title": todo.title,
            "priority": todo.priority.value,
            "effort": todo.effort.value,
            "section": todo.section,
            "file": str(todos_path)
        }

    def _format_todo(self, todo: TodoItem) -> str:
        """格式化TODO项"""
        # 构建优先级标记
        priority_str = f"{todo.priority.value} / {todo.effort.value}"
        if todo.multiplier != 1.0:
            priority_str += f" x{todo.multiplier}"

        # 构建TODO行
        line = f"- [ ] **[{priority_str}]** {todo.title}"

        # 添加描述
        if todo.description:
            line += f" — {todo.description}"

        return line

    def parse_todos(self, work_dir: Optional[Path] = None) -> List[Dict[str, Any]]:
        """
        解析所有TODO项

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

    def mark_completed(self, title: str, work_dir: Optional[Path] = None) -> bool:
        """
        标记TODO为已完成

        Args:
            title: TODO标题
            work_dir: 工作目录

        Returns:
            是否成功
        """
        work_dir = Path(work_dir) if work_dir else self.base_path
        todos_path = work_dir / "TODOS.md"

        if not todos_path.exists():
            return False

        try:
            content = todos_path.read_text(encoding="utf-8")

            # 查找并更新TODO行
            pattern = rf"(- )\[ \](.*?{re.escape(title)}.*?)"
            replacement = r"- [x]\2 — DONE"

            new_content = re.sub(pattern, replacement, content, count=1)

            if new_content != content:
                todos_path.write_text(new_content, encoding="utf-8")
                return True

            return False

        except Exception:
            return False

    def get_capabilities(self) -> Dict[str, Any]:
        """获取技能能力信息"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "features": [
                "todo_creation",
                "todo_formatting",
                "section_management",
                "todo_parsing",
                "todo_completion"
            ],
            "priorities": [p.value for p in Priority],
            "efforts": [e.value for e in Effort],
            "sections": ["In Progress", "Future Concepts"]
        }


# 向后兼容
Add_Todo_Skill = AddTodoSkill


def main():
    """入口函数 - 演示用法"""
    print("=" * 60)
    print("Add Todo Skill - 演示")
    print("=" * 60)

    skill = AddTodoSkill()

    # 演示1: 添加简单TODO
    print("\n1. 添加简单TODO")
    print("-" * 40)
    result = skill.execute(
        title="添加用户认证",
        priority="P1",
        effort="Medium"
    )
    print(f"结果: {result}")

    # 演示2: 添加带描述的TODO
    print("\n2. 添加带描述的TODO")
    print("-" * 40)
    result = skill.execute(
        title="优化数据库查询",
        priority="P2",
        effort="High",
        description="添加索引和缓存"
    )
    print(f"结果: {result}")

    # 演示3: 列出所有TODO
    print("\n3. 列出所有TODO")
    print("-" * 40)
    todos = skill.parse_todos()
    print(f"找到 {len(todos)} 个TODO")
    for todo in todos[:3]:
        print(f"  - [{todo['priority']}] {todo['title']}")

    print("\n" + "=" * 60)
    print("演示完成！")
    print("=" * 60)

    return skill


if __name__ == "__main__":
    main()
