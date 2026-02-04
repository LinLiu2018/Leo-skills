# -*- coding: utf-8 -*-
"""
populate_state_skill - 状态填充技能

从 EXECUTION_PLAN.md 和 git 历史生成 .claude/phase-state.json。
用于恢复阶段状态或在加入现有项目时初始化状态。
基于 obra/superpowers 的 populate-state 技能实现。
"""

import json
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class TaskStateStatus(Enum):
    """任务状态"""
    COMPLETE = "COMPLETE"
    IN_PROGRESS = "IN_PROGRESS"
    BLOCKED = "BLOCKED"
    NOT_STARTED = "NOT_STARTED"


@dataclass
class TaskState:
    """任务状态"""
    id: str
    status: TaskStateStatus
    completed_at: Optional[str] = None
    blocker: Optional[str] = None


@dataclass
class PhaseState:
    """阶段状态"""
    number: int
    name: str
    status: str
    tasks_total: int
    tasks_complete: int
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    tasks: List[TaskState] = field(default_factory=list)


@dataclass
class ProjectState:
    """项目状态"""
    schema_version: str
    project_name: str
    last_updated: str
    generated_by: str
    current_phase: int
    total_phases: int
    status: str
    phases: List[PhaseState]
    features: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PopulateResult:
    """状态填充结果"""
    success: bool
    state_path: str
    phases_found: int
    tasks_found: int
    tasks_completed: int
    blockers_found: int
    summary: str


class PopulateStateSkill:
    """
    状态填充技能

    功能：
    - 解析 EXECUTION_PLAN.md 提取阶段和任务
    - 解析 git 历史获取任务完成时间戳
    - 检测功能分支
    - 识别阻塞任务
    - 生成 phase-state.json

    使用场景：
    - 开始使用编排器时初始化状态
    - 状态丢失或损坏后恢复
    - 同步状态与实际进度
    """

    def __init__(self, base_path: str = "."):
        self.name = "populate_state_skill"
        self.version = "1.0.0"
        self.description = "状态填充技能 - 从执行计划生成阶段状态"
        self.base_path = Path(base_path)

    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        执行技能主入口

        Args:
            work_dir: 工作目录
            force: 是否强制覆盖现有状态

        Returns:
            Dict 包含填充结果
        """
        work_dir = kwargs.get("work_dir", self.base_path)
        force = kwargs.get("force", False)

        try:
            result = self.populate_state(
                work_dir=work_dir,
                force=force
            )

            return {
                "status": "success" if result.success else "error",
                "skill": self.name,
                "state_path": result.state_path,
                "phases_found": result.phases_found,
                "tasks_found": result.tasks_found,
                "tasks_completed": result.tasks_completed,
                "blockers_found": result.blockers_found,
                "summary": result.summary
            }

        except Exception as e:
            return {
                "status": "error",
                "skill": self.name,
                "error": str(e)
            }

    def populate_state(
        self,
        work_dir: Optional[Path] = None,
        force: bool = False
    ) -> PopulateResult:
        """
        填充状态

        Args:
            work_dir: 工作目录
            force: 是否强制覆盖

        Returns:
            PopulateResult 填充结果
        """
        work_dir = Path(work_dir) if work_dir else self.base_path

        # 1. 检查执行计划
        plan_path = work_dir / "EXECUTION_PLAN.md"
        if not plan_path.exists():
            return PopulateResult(
                success=False,
                state_path="",
                phases_found=0,
                tasks_found=0,
                tasks_completed=0,
                blockers_found=0,
                summary="EXECUTION_PLAN.md 不存在"
            )

        # 2. 检查是否已存在状态文件
        state_path = work_dir / ".claude" / "phase-state.json"
        if state_path.exists() and not force:
            return PopulateResult(
                success=False,
                state_path=str(state_path),
                phases_found=0,
                tasks_found=0,
                tasks_completed=0,
                blockers_found=0,
                summary="状态文件已存在，使用 force=True 覆盖"
            )

        # 3. 解析执行计划
        try:
            content = plan_path.read_text(encoding="utf-8")
            phases = self._parse_phases_from_plan(content)
        except Exception as e:
            return PopulateResult(
                success=False,
                state_path="",
                phases_found=0,
                tasks_found=0,
                tasks_completed=0,
                blockers_found=0,
                summary=f"解析执行计划失败: {e}"
            )

        # 4. 解析 git 历史
        git_history = self._parse_git_history(work_dir)

        # 5. 合并 git 历史到任务状态
        self._merge_git_history(phases, git_history)

        # 6. 检测功能分支
        features = self._detect_features(work_dir)

        # 7. 确定当前阶段
        current_phase = 1
        for phase in phases:
            if phase.status == "IN_PROGRESS":
                current_phase = phase.number
                break
            elif phase.status == "COMPLETE":
                current_phase = phase.number + 1

        # 8. 确定项目状态
        total_tasks = sum(p.tasks_total for p in phases)
        completed_tasks = sum(p.tasks_complete for p in phases)

        if completed_tasks == 0:
            project_status = "NOT_STARTED"
        elif completed_tasks == total_tasks:
            project_status = "COMPLETE"
        else:
            project_status = "IN_PROGRESS"

        # 9. 生成状态对象
        project_state = ProjectState(
            schema_version="1.0",
            project_name=work_dir.name or "project",
            last_updated=datetime.now().isoformat(),
            generated_by="populate-state",
            current_phase=current_phase,
            total_phases=len(phases),
            status=project_status,
            phases=phases,
            features=features
        )

        # 10. 写入状态文件
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(
            json.dumps(
                self._state_to_dict(project_state),
                indent=2,
                ensure_ascii=False
            ),
            encoding="utf-8"
        )

        # 11. 统计阻塞任务
        blockers = sum(
            1 for p in phases
            for t in p.tasks
            if t.status == TaskStateStatus.BLOCKED
        )

        return PopulateResult(
            success=True,
            state_path=str(state_path),
            phases_found=len(phases),
            tasks_found=total_tasks,
            tasks_completed=completed_tasks,
            blockers_found=blockers,
            summary=self._generate_summary(project_state, phases)
        )

    def _parse_phases_from_plan(self, content: str) -> List[PhaseState]:
        """从执行计划解析阶段"""
        phases = []

        # 查找所有阶段
        phase_pattern = r"##\s*Phase\s+(\d+)\s*[:\-\s]*([^\n]+)?"
        phase_matches = list(re.finditer(phase_pattern, content, re.IGNORECASE))

        for i, match in enumerate(phase_matches):
            phase_number = int(match.group(1))
            phase_name = match.group(2).strip() if match.group(2) else f"Phase {phase_number}"

            # 提取阶段内容
            start_pos = match.end()
            end_pos = phase_matches[i + 1].start() if i + 1 < len(phase_matches) else len(content)
            phase_content = content[start_pos:end_pos]

            # 解析任务
            tasks = self._parse_tasks(phase_content)

            # 计算统计
            tasks_total = len(tasks)
            tasks_complete = sum(1 for t in tasks if t.status == TaskStateStatus.COMPLETE)

            # 确定阶段状态
            if tasks_complete == 0:
                phase_status = "NOT_STARTED"
            elif tasks_complete == tasks_total:
                phase_status = "COMPLETE"
            else:
                phase_status = "IN_PROGRESS"

            phases.append(PhaseState(
                number=phase_number,
                name=phase_name,
                status=phase_status,
                tasks_total=tasks_total,
                tasks_complete=tasks_complete,
                tasks=tasks
            ))

        return phases

    def _parse_tasks(self, phase_content: str) -> List[TaskState]:
        """解析任务"""
        tasks = []

        # 查找任务
        task_pattern = r"####\s*Task\s+(\d+\.\d+\.?[A-Z]?)"
        task_matches = list(re.finditer(task_pattern, phase_content))

        for j, task_match in enumerate(task_matches):
            task_id = task_match.group(1)

            # 提取任务内容
            task_start = task_match.end()
            task_end = task_matches[j + 1].start() if j + 1 < len(task_matches) else len(phase_content)
            task_content = phase_content[task_start:task_end]

            # 检查验收标准
            criteria_pattern = r"-\s*\[(.)\]"
            criteria_matches = re.findall(criteria_pattern, task_content)

            total_criteria = len(criteria_matches)
            completed_criteria = sum(1 for box in criteria_matches if box.strip() == "x")

            # 检查状态标记
            status_match = re.search(r"\*\*Status:\*\*\s*(\w+)", task_content)
            status_marker = status_match.group(1) if status_match else None

            # 检查阻塞标记
            blocker_match = re.search(r"\*\*Blocker:\*\*\s*(.+)", task_content)
            blocker = blocker_match.group(1).strip() if blocker_match else None

            # 确定任务状态
            if status_marker == "BLOCKED" or blocker:
                task_status = TaskStateStatus.BLOCKED
            elif completed_criteria == total_criteria and total_criteria > 0:
                task_status = TaskStateStatus.COMPLETE
            elif completed_criteria > 0:
                task_status = TaskStateStatus.IN_PROGRESS
            else:
                task_status = TaskStateStatus.NOT_STARTED

            tasks.append(TaskState(
                id=task_id,
                status=task_status,
                blocker=blocker
            ))

        return tasks

    def _parse_git_history(self, work_dir: Path) -> Dict[str, str]:
        """解析 git 历史"""
        history = {}

        git_dir = work_dir / ".git"
        if not git_dir.exists():
            return history

        try:
            # 获取提交历史
            result = subprocess.run(
                ["git", "log", "--format=%H|%ai|%s", "--all"],
                cwd=work_dir,
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                return history

            for line in result.stdout.strip().split("\n"):
                parts = line.split("|", 2)
                if len(parts) >= 3:
                    commit_hash, timestamp, message = parts

                    # 检查是否是任务提交
                    task_match = re.search(r"task\(([^)]+)\)", message, re.IGNORECASE)
                    if task_match:
                        task_id = task_match.group(1)
                        history[task_id] = timestamp

        except Exception:
            pass

        return history

    def _merge_git_history(self, phases: List[PhaseState], git_history: Dict[str, str]):
        """合并 git 历史到任务状态"""
        for phase in phases:
            for task in phase.tasks:
                if task.id in git_history:
                    # 如果 git 历史中有记录，标记为完成
                    if task.status != TaskStateStatus.BLOCKED:
                        task.status = TaskStateStatus.COMPLETE
                        task.completed_at = git_history[task.id]

            # 重新计算阶段统计
            phase.tasks_complete = sum(
                1 for t in phase.tasks
                if t.status == TaskStateStatus.COMPLETE
            )

            # 更新阶段状态
            if phase.tasks_complete == phase.tasks_total:
                phase.status = "COMPLETE"
            elif phase.tasks_complete > 0:
                phase.status = "IN_PROGRESS"

    def _detect_features(self, work_dir: Path) -> Dict[str, Any]:
        """检测功能分支"""
        features = {}

        git_dir = work_dir / ".git"
        if not git_dir.exists():
            return features

        try:
            # 获取所有分支
            result = subprocess.run(
                ["git", "branch", "-a"],
                cwd=work_dir,
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                return features

            for line in result.stdout.strip().split("\n"):
                branch = line.strip().strip("* ")

                # 检查是否是功能分支
                if "/feature/" in branch or branch.startswith("feature-"):
                    feature_name = branch.split("/")[-1].replace("feature-", "")
                    features[feature_name] = {
                        "branch": branch,
                        "detected_at": datetime.now().isoformat()
                    }

        except Exception:
            pass

        return features

    def _state_to_dict(self, state: ProjectState) -> Dict[str, Any]:
        """转换状态为字典"""
        return {
            "schema_version": state.schema_version,
            "project_name": state.project_name,
            "last_updated": state.last_updated,
            "generated_by": state.generated_by,
            "current_phase": state.current_phase,
            "total_phases": state.total_phases,
            "status": state.status,
            "phases": [
                {
                    "number": p.number,
                    "name": p.name,
                    "status": p.status,
                    "tasks_total": p.tasks_total,
                    "tasks_complete": p.tasks_complete,
                    "started_at": p.started_at,
                    "completed_at": p.completed_at,
                    "tasks": [
                        {
                            "id": t.id,
                            "status": t.status.value,
                            "completed_at": t.completed_at,
                            "blocker": t.blocker
                        }
                        for t in p.tasks
                    ]
                }
                for p in state.phases
            ],
            "features": state.features
        }

    def _generate_summary(self, state: ProjectState, phases: List[PhaseState]) -> str:
        """生成总结"""
        total_tasks = sum(p.tasks_total for p in phases)
        completed_tasks = sum(p.tasks_complete for p in phases)

        lines = [
            f"项目: {state.project_name}",
            f"阶段: {len(phases)} 个",
            f"任务: {completed_tasks}/{total_tasks} 完成",
            f"当前阶段: {state.current_phase}",
            f"项目状态: {state.status}"
        ]

        blockers = sum(
            1 for p in phases
            for t in p.tasks
            if t.status == TaskStateStatus.BLOCKED
        )

        if blockers > 0:
            lines.append(f"阻塞任务: {blockers} 个")

        return "\n".join(lines)

    def get_capabilities(self) -> Dict[str, Any]:
        """获取技能能力信息"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "features": [
                "plan_parsing",
                "git_history_analysis",
                "task_extraction",
                "blocker_detection",
                "feature_detection",
                "state_generation",
                "state_persistence"
            ],
            "outputs": [
                "phase-state.json"
            ]
        }


# 向后兼容
PopulateState_Skill = PopulateStateSkill
POPULATE_Skill = PopulateStateSkill


def main():
    """入口函数 - 演示用法"""
    print("=" * 60)
    print("Populate State Skill - 演示")
    print("=" * 60)

    skill = PopulateStateSkill()

    # 演示: 技能能力
    print("\n1. 技能能力")
    print("-" * 40)
    caps = skill.get_capabilities()
    print(f"技能: {caps['name']}")
    print(f"功能: {', '.join(caps['features'])}")

    # 演示: 填充状态
    print("\n2. 尝试填充状态")
    print("-" * 40)
    result = skill.populate_state()
    print(f"成功: {result.success}")
    print(f"路径: {result.state_path}")
    print(f"阶段: {result.phases_found}")
    print(f"任务: {result.tasks_completed}/{result.tasks_found}")
    print(f"\n总结:\n{result.summary}")

    print("\n" + "=" * 60)
    print("演示完成！")
    print("=" * 60)

    return skill


if __name__ == "__main__":
    main()
