# -*- coding: utf-8 -*-
"""
phase_start_skill - 阶段执行技能

执行阶段中的所有任务，支持自动提交和状态跟踪。
基于 obra/superpowers 的 phase-start 技能实现。
"""

import json
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"
    BLOCKED = "blocked"
    FAILED = "failed"


@dataclass
class TaskResult:
    """任务执行结果"""
    task_id: str
    status: TaskStatus
    description: str = ""
    commits: List[str] = field(default_factory=list)
    error: str = ""
    duration_seconds: float = 0.0


@dataclass
class PhaseStartResult:
    """阶段执行结果"""
    phase_number: int
    success: bool
    tasks_completed: int
    tasks_failed: int
    tasks_blocked: int
    task_results: List[TaskResult] = field(default_factory=list)
    branch_name: str = ""
    commits: List[str] = field(default_factory=list)
    summary: str = ""


class PhaseStartSkill:
    """
    阶段执行技能

    功能：
    - 解析执行计划中的阶段任务
    - 创建阶段分支并执行任务
    - 自动提交更改
    - 更新任务状态
    - 生成执行报告

    使用场景：
    - 执行阶段中的所有任务
    - 自动化开发工作流
    """

    def __init__(self, base_path: str = "."):
        self.name = "phase_start_skill"
        self.version = "1.0.0"
        self.description = "阶段执行技能 - 执行阶段中的所有任务"
        self.base_path = Path(base_path)

    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        执行技能主入口

        Args:
            phase_number: 阶段编号
            work_dir: 工作目录
            create_branch: 是否创建阶段分支
            auto_commit: 是否自动提交

        Returns:
            Dict 包含执行结果
        """
        phase_number = kwargs.get("phase_number", 1)
        work_dir = kwargs.get("work_dir", self.base_path)
        create_branch = kwargs.get("create_branch", True)
        auto_commit = kwargs.get("auto_commit", True)

        try:
            result = self.execute_phase(
                phase_number=phase_number,
                work_dir=work_dir,
                create_branch=create_branch,
                auto_commit=auto_commit
            )

            return {
                "status": "success" if result.success else "partial",
                "skill": self.name,
                "phase": phase_number,
                "success": result.success,
                "tasks_completed": result.tasks_completed,
                "tasks_failed": result.tasks_failed,
                "tasks_blocked": result.tasks_blocked,
                "branch": result.branch_name,
                "commits": result.commits,
                "summary": result.summary,
                "task_results": [
                    {
                        "task_id": t.task_id,
                        "status": t.status.value,
                        "description": t.description,
                        "commits": t.commits,
                        "error": t.error,
                        "duration": t.duration_seconds
                    }
                    for t in result.task_results
                ]
            }

        except Exception as e:
            return {
                "status": "error",
                "skill": self.name,
                "phase": phase_number,
                "error": str(e)
            }

    def execute_phase(
        self,
        phase_number: int,
        work_dir: Optional[Path] = None,
        create_branch: bool = True,
        auto_commit: bool = True
    ) -> PhaseStartResult:
        """
        执行阶段

        Args:
            phase_number: 阶段编号
            work_dir: 工作目录
            create_branch: 是否创建阶段分支
            auto_commit: 是否自动提交

        Returns:
            PhaseStartResult 执行结果
        """
        import time
        work_dir = Path(work_dir) if work_dir else self.base_path
        task_results = []

        # 1. 检查执行计划
        plan_path = work_dir / "EXECUTION_PLAN.md"
        if not plan_path.exists():
            return PhaseStartResult(
                phase_number=phase_number,
                success=False,
                tasks_completed=0,
                tasks_failed=0,
                tasks_blocked=0,
                summary="EXECUTION_PLAN.md 不存在"
            )

        # 2. 获取阶段任务
        tasks = self._parse_phase_tasks(plan_path, phase_number)
        if not tasks:
            return PhaseStartResult(
                phase_number=phase_number,
                success=True,
                tasks_completed=0,
                tasks_failed=0,
                tasks_blocked=0,
                summary=f"阶段 {phase_number} 没有任务"
            )

        # 3. 创建阶段分支
        branch_name = f"phase-{phase_number}"
        if create_branch:
            self._create_phase_branch(work_dir, branch_name)

        # 4. 执行任务
        completed = 0
        failed = 0
        blocked = 0
        all_commits = []

        for task in tasks:
            task_id = task["id"]
            description = task["description"]

            start_time = time.time()

            # 检查任务是否被阻塞
            if task.get("status") == "BLOCKED":
                task_results.append(TaskResult(
                    task_id=task_id,
                    status=TaskStatus.BLOCKED,
                    description=description,
                    error=task.get("blocker", "任务被阻塞")
                ))
                blocked += 1
                continue

            # 模拟执行任务
            try:
                # 实际项目中这里会调用相应的工具执行任务
                task_result = self._execute_task(work_dir, task, auto_commit)

                duration = time.time() - start_time

                task_results.append(TaskResult(
                    task_id=task_id,
                    status=TaskStatus.COMPLETE,
                    description=description,
                    commits=task_result.get("commits", []),
                    duration_seconds=duration
                ))
                completed += 1
                all_commits.extend(task_result.get("commits", []))

                # 更新执行计划中的任务状态
                self._update_task_status(plan_path, task_id, True)

            except Exception as e:
                duration = time.time() - start_time
                task_results.append(TaskResult(
                    task_id=task_id,
                    status=TaskStatus.FAILED,
                    description=description,
                    error=str(e),
                    duration_seconds=duration
                ))
                failed += 1

        # 5. 生成总结
        success = failed == 0 and blocked == 0
        summary = self._generate_summary(
            phase_number, completed, failed, blocked, all_commits
        )

        # 6. 更新阶段状态
        self._update_phase_state(work_dir, phase_number, task_results)

        return PhaseStartResult(
            phase_number=phase_number,
            success=success,
            tasks_completed=completed,
            tasks_failed=failed,
            tasks_blocked=blocked,
            task_results=task_results,
            branch_name=branch_name,
            commits=all_commits,
            summary=summary
        )

    def _parse_phase_tasks(self, plan_path: Path, phase_number: int) -> List[Dict[str, Any]]:
        """解析阶段任务"""
        try:
            content = plan_path.read_text(encoding="utf-8")

            # 查找阶段内容
            phase_pattern = rf"##\s*Phase\s+{phase_number}\b.*?(?=##\s*Phase|\Z)"
            phase_match = re.search(phase_pattern, content, re.DOTALL)

            if not phase_match:
                return []

            phase_content = phase_match.group(0)

            # 提取任务
            tasks = []
            task_pattern = r"####\s*Task\s+(\d+\.\d+\.?[A-Z]?)\s*[-:]?\s*(.*?)(?=####\s*Task|\Z)"
            task_matches = re.findall(task_pattern, phase_content, re.DOTALL)

            for task_id, task_content in task_matches:
                # 检查任务状态
                status_match = re.search(r"\*\*Status:\*\*\s*(\w+)", task_content)
                status = status_match.group(1) if status_match else None

                # 检查是否有阻塞标记
                blocker_match = re.search(r"\*\*Blocker:\*\*\s*(.+)", task_content)
                blocker = blocker_match.group(1) if blocker_match else None

                tasks.append({
                    "id": task_id.strip(),
                    "description": task_content.strip().split("\n")[0][:100],
                    "content": task_content.strip(),
                    "status": status,
                    "blocker": blocker
                })

            return tasks

        except Exception as e:
            print(f"解析任务失败: {e}")
            return []

    def _create_phase_branch(self, work_dir: Path, branch_name: str) -> bool:
        """创建阶段分支"""
        try:
            # 检查是否是 Git 仓库
            git_dir = work_dir / ".git"
            if not git_dir.exists():
                return False

            # 创建并切换分支
            subprocess.run(
                ["git", "checkout", "-b", branch_name],
                cwd=work_dir,
                capture_output=True,
                check=True
            )
            return True

        except subprocess.CalledProcessError:
            # 分支可能已存在，尝试切换
            try:
                subprocess.run(
                    ["git", "checkout", branch_name],
                    cwd=work_dir,
                    capture_output=True,
                    check=True
                )
                return True
            except subprocess.CalledProcessError:
                return False
        except Exception:
            return False

    def _execute_task(self, work_dir: Path, task: Dict[str, Any], auto_commit: bool) -> Dict[str, Any]:
        """
        执行单个任务

        注意：这是一个模拟实现。实际使用时需要集成具体的执行逻辑。
        """
        task_id = task["id"]

        # 模拟任务执行结果
        # 实际项目中这里会根据任务内容调用相应的工具
        commits = []

        if auto_commit:
            # 模拟提交
            commit_msg = f"task({task_id}): {task['description'][:50]}"
            commits.append(commit_msg)

        return {
            "success": True,
            "commits": commits
        }

    def _update_task_status(self, plan_path: Path, task_id: str, completed: bool) -> bool:
        """更新任务状态在执行计划中"""
        try:
            content = plan_path.read_text(encoding="utf-8")

            # 找到任务并更新复选框
            task_pattern = rf"(####\s*Task\s+{re.escape(task_id)}.*?)(- \[)\s*(.)\s*(\])"

            def replace_checkbox(match):
                prefix = match.group(1)
                checkbox_open = match.group(2)
                checkbox_close = match.group(4)
                new_status = "x" if completed else " "
                return f"{prefix}{checkbox_open}{new_status}{checkbox_close}"

            updated_content = re.sub(task_pattern, replace_checkbox, content, flags=re.DOTALL)

            if updated_content != content:
                plan_path.write_text(updated_content, encoding="utf-8")

            return True

        except Exception:
            return False

    def _update_phase_state(self, work_dir: Path, phase_number: int, task_results: List[TaskResult]) -> bool:
        """更新阶段状态文件"""
        try:
            state_path = work_dir / ".claude" / "phase-state.json"
            state_path.parent.mkdir(parents=True, exist_ok=True)

            # 读取现有状态
            if state_path.exists():
                state = json.loads(state_path.read_text(encoding="utf-8"))
            else:
                state = {"phases": []}

            # 更新或添加阶段信息
            phase_info = {
                "number": phase_number,
                "status": "IN_PROGRESS",
                "started_at": datetime.now().isoformat(),
                "tasks": [
                    {
                        "id": t.task_id,
                        "status": t.status.value,
                        "completed_at": datetime.now().isoformat() if t.status == TaskStatus.COMPLETE else None
                    }
                    for t in task_results
                ]
            }

            # 更新 phases 列表
            existing_idx = None
            for idx, p in enumerate(state.get("phases", [])):
                if p.get("number") == phase_number:
                    existing_idx = idx
                    break

            if existing_idx is not None:
                state["phases"][existing_idx] = phase_info
            else:
                state["phases"].append(phase_info)

            # 更新当前阶段
            state["current_phase"] = phase_number

            state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
            return True

        except Exception as e:
            print(f"更新阶段状态失败: {e}")
            return False

    def _generate_summary(
        self,
        phase_number: int,
        completed: int,
        failed: int,
        blocked: int,
        commits: List[str]
    ) -> str:
        """生成执行总结"""
        total = completed + failed + blocked

        lines = [
            f"阶段 {phase_number} 执行完成",
            f"任务总数: {total}",
            f"完成: {completed}",
            f"失败: {failed}",
            f"阻塞: {blocked}",
        ]

        if commits:
            lines.extend([
                f"提交数: {len(commits)}",
                "提交列表:"
            ])
            for commit in commits[:5]:  # 最多显示5个
                lines.append(f"  - {commit}")
            if len(commits) > 5:
                lines.append(f"  ... 还有 {len(commits) - 5} 个提交")

        return "\n".join(lines)

    def get_capabilities(self) -> Dict[str, Any]:
        """获取技能能力信息"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "features": [
                "phase_execution",
                "task_parsing",
                "branch_creation",
                "auto_commit",
                "status_tracking",
                "state_management"
            ],
            "execution_modes": [
                "sequential",
                "with_branch",
                "auto_commit"
            ]
        }


# 向后兼容
PhaseStart_Skill = PhaseStartSkill
PHASE_Skill = PhaseStartSkill


def main():
    """入口函数 - 演示用法"""
    print("=" * 60)
    print("Phase Start Skill - 演示")
    print("=" * 60)

    skill = PhaseStartSkill()

    # 演示: 解析任务
    print("\n1. 技能能力")
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
