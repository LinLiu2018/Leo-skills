# -*- coding: utf-8 -*-
"""
run_todos_skill - 执行TODO技能

实现标记为 [ready] 的TODO项，自动提交更改。
基于 obra/superpowers 的 run-todos 技能实现。
"""

import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class TodoImplementation:
    """TODO实现结果"""
    title: str
    success: bool
    commit_hash: str = ""
    error: str = ""
    skipped: bool = False


class RunTodosSkill:
    """
    执行TODO技能

    功能：
    - 查找标记为 [ready] 的TODO项
    - 执行TODO实现
    - 自动提交更改
    - 更新TODO状态

    使用场景：
    - 批量实现TODO项
    - 自动化任务执行
    - 跟踪实现进度
    """

    def __init__(self, base_path: str = "."):
        self.name = "run_todos_skill"
        self.version = "1.0.0"
        self.description = "执行TODO技能 - 实现标记为ready的TODO项"
        self.base_path = Path(base_path)

    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        执行技能主入口

        Args:
            work_dir: 工作目录
            select_all: 是否选择所有ready项
            specific_items: 指定要执行的项

        Returns:
            Dict 包含执行结果
        """
        work_dir = kwargs.get("work_dir", self.base_path)
        select_all = kwargs.get("select_all", False)
        specific_items = kwargs.get("specific_items", [])

        try:
            # 查找ready项
            ready_items = self.find_ready_items(work_dir)

            if not ready_items:
                return {
                    "status": "success",
                    "skill": self.name,
                    "message": "没有标记为 [ready] 的TODO项",
                    "implementations": []
                }

            # 选择要执行的项
            if specific_items:
                items_to_run = [
                    item for item in ready_items
                    if item["title"] in specific_items
                ]
            elif select_all:
                items_to_run = ready_items
            else:
                # 默认执行第一个
                items_to_run = ready_items[:1]

            # 创建分支
            branch_name = self._create_branch(work_dir)

            # 执行实现
            implementations = []
            for item in items_to_run:
                impl = self._implement_todo(item, work_dir)
                implementations.append(impl)

            return {
                "status": "success",
                "skill": self.name,
                "branch": branch_name,
                "completed": sum(1 for i in implementations if i.success),
                "failed": sum(1 for i in implementations if not i.success and not i.skipped),
                "implementations": [
                    {
                        "title": i.title,
                        "success": i.success,
                        "commit": i.commit_hash,
                        "error": i.error,
                        "skipped": i.skipped
                    }
                    for i in implementations
                ]
            }

        except Exception as e:
            return {
                "status": "error",
                "skill": self.name,
                "error": str(e)
            }

    def find_ready_items(self, work_dir: Optional[Path] = None) -> List[Dict[str, Any]]:
        """
        查找标记为 [ready] 的TODO项

        Args:
            work_dir: 工作目录

        Returns:
            ready项列表
        """
        work_dir = Path(work_dir) if work_dir else self.base_path
        todos_path = work_dir / "TODOS.md"

        if not todos_path.exists():
            return []

        try:
            content = todos_path.read_text(encoding="utf-8")
            ready_items = []

            # 匹配带 [ready] 标记的TODO行
            pattern = r"- \[([ x])\] \*\*\[(P\d) / (\w+)(?: x([\d.]+))?\]\*\* (.+?)\s*\[ready\](?: — (.+))?\s*$"

            for line in content.split("\n"):
                match = re.match(pattern, line, re.IGNORECASE)
                if match:
                    checked = match.group(1)
                    # 跳过已完成的
                    if checked == "x":
                        continue

                    priority = match.group(2)
                    effort = match.group(3)
                    multiplier = match.group(4)
                    title = match.group(5)
                    description = match.group(6)

                    ready_items.append({
                        "title": title.strip(),
                        "priority": priority,
                        "effort": effort,
                        "multiplier": float(multiplier) if multiplier else 1.0,
                        "description": description.strip() if description else "",
                        "line": line
                    })

            return ready_items

        except Exception as e:
            print(f"查找ready项失败: {e}")
            return []

    def _create_branch(self, work_dir: Path) -> str:
        """创建实现分支"""
        date_str = datetime.now().strftime("%Y-%m-%d")
        branch_name = f"todo-impl-{date_str}"

        git_dir = work_dir / ".git"
        if not git_dir.exists():
            return ""

        try:
            # 提交任何未提交的更改
            subprocess.run(
                ["git", "add", "-A"],
                cwd=work_dir,
                capture_output=True
            )
            subprocess.run(
                ["git", "diff", "--cached", "--quiet"],
                cwd=work_dir,
                capture_output=True
            )

            # 创建并切换分支
            subprocess.run(
                ["git", "checkout", "-b", branch_name],
                cwd=work_dir,
                capture_output=True
            )

            return branch_name

        except Exception:
            return ""

    def _implement_todo(self, item: Dict[str, Any], work_dir: Path) -> TodoImplementation:
        """
        实现单个TODO

        注意：这是简化实现。实际使用时需要集成具体的执行逻辑。
        """
        title = item["title"]

        # 这里应该调用具体的实现逻辑
        # 简化版本：仅标记为完成

        # 更新TODOS.md
        if self._mark_todo_done(title, work_dir):
            # 提交更改
            commit_hash = self._commit_changes(title, work_dir)

            return TodoImplementation(
                title=title,
                success=True,
                commit_hash=commit_hash
            )

        return TodoImplementation(
            title=title,
            success=False,
            error="无法更新TODO状态"
        )

    def _mark_todo_done(self, title: str, work_dir: Path) -> bool:
        """标记TODO为已完成"""
        todos_path = work_dir / "TODOS.md"

        if not todos_path.exists():
            return False

        try:
            content = todos_path.read_text(encoding="utf-8")

            # 查找并更新TODO行
            # 匹配包含该标题的TODO行
            pattern = rf"(- )\[ \](.*?{re.escape(title)}.*?)(?:\s*—\s*DONE.*)?$"

            def replace_todo(match):
                prefix = match.group(1)
                rest = match.group(2)
                return f"- [x]{rest} — DONE"

            new_content = re.sub(pattern, replace_todo, content, flags=re.MULTILINE)

            if new_content != content:
                todos_path.write_text(new_content, encoding="utf-8")
                return True

            return False

        except Exception as e:
            print(f"标记TODO完成失败: {e}")
            return False

    def _commit_changes(self, title: str, work_dir: Path) -> str:
        """提交更改"""
        git_dir = work_dir / ".git"
        if not git_dir.exists():
            return ""

        try:
            # 添加更改
            subprocess.run(
                ["git", "add", "-A"],
                cwd=work_dir,
                capture_output=True,
                check=True
            )

            # 提交
            commit_msg = f"todo: {title[:50]}"
            subprocess.run(
                ["git", "commit", "-m", commit_msg],
                cwd=work_dir,
                capture_output=True,
                check=True
            )

            # 获取commit hash
            result = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                cwd=work_dir,
                capture_output=True,
                text=True,
                check=True
            )

            return result.stdout.strip()

        except Exception:
            return ""

    def get_capabilities(self) -> Dict[str, Any]:
        """获取技能能力信息"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "features": [
                "ready_item_detection",
                "branch_creation",
                "todo_implementation",
                "auto_commit",
                "status_update"
            ]
        }


# 向后兼容
Run_Todos_Skill = RunTodosSkill


def main():
    """入口函数 - 演示用法"""
    print("=" * 60)
    print("Run Todos Skill - 演示")
    print("=" * 60)

    skill = RunTodosSkill()

    # 演示: 查找ready项
    print("\n1. 查找 [ready] TODO项")
    print("-" * 40)
    ready_items = skill.find_ready_items()
    print(f"找到 {len(ready_items)} 个 [ready] 项")
    for item in ready_items[:3]:
        print(f"  - [{item['priority']}] {item['title']}")

    # 演示: 技能能力
    print("\n2. 技能能力")
    print("-" * 40)
    caps = skill.get_capabilities()
    print(f"技能: {caps['name']}")
    print(f"功能: {', '.join(caps['features'])}")

    print("\n" + "=" * 60)
    print("演示完成！")
    print("=" * 60)

    return skill


if __name__ == "__main__":
    main()
