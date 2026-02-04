# -*- coding: utf-8 -*-
"""
progress_skill - 进度查询技能

显示通过 EXECUTION_PLAN.md 和功能计划的总体项目进度。
基于 obra/superpowers 的 progress 技能实现。
"""

import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class PhaseStatus(Enum):
    """阶段状态"""
    COMPLETE = "Complete"
    IN_PROGRESS = "In Progress"
    NOT_STARTED = "Not Started"


@dataclass
class PhaseProgress:
    """阶段进度"""
    number: int
    name: str
    status: PhaseStatus
    total_criteria: int
    completed_criteria: int
    checkpoint_criteria: int = 0
    completed_checkpoint: int = 0


@dataclass
class PlanProgress:
    """计划进度"""
    name: str
    path: str
    total_phases: int
    phases: List[PhaseProgress]
    current_phase: Optional[int] = None

    @property
    def total_criteria(self) -> int:
        return sum(p.total_criteria for p in self.phases)

    @property
    def completed_criteria(self) -> int:
        return sum(p.completed_criteria for p in self.phases)

    @property
    def completion_percentage(self) -> float:
        if self.total_criteria == 0:
            return 0.0
        return (self.completed_criteria / self.total_criteria) * 100


@dataclass
class ProgressResult:
    """进度查询结果"""
    plans: List[PlanProgress]
    overall_total: int
    overall_completed: int
    next_action: str = ""

    @property
    def overall_percentage(self) -> float:
        if self.overall_total == 0:
            return 0.0
        return (self.overall_completed / self.overall_total) * 100


class ProgressSkill:
    """
    进度查询技能

    功能：
    - 解析主执行计划和功能计划
    - 计算任务验收标准完成度
    - 显示阶段进度和状态
    - 推荐下一步行动

    使用场景：
    - 检查项目整体进度
    - 识别剩余工作
    - 规划下一步行动
    """

    def __init__(self, base_path: str = "."):
        self.name = "progress_skill"
        self.version = "1.0.0"
        self.description = "进度查询技能 - 显示项目完成状态"
        self.base_path = Path(base_path)

    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        执行技能主入口

        Args:
            work_dir: 工作目录
            include_features: 是否包含功能计划

        Returns:
            Dict 包含进度信息
        """
        work_dir = kwargs.get("work_dir", self.base_path)
        include_features = kwargs.get("include_features", True)

        try:
            result = self.check_progress(
                work_dir=work_dir,
                include_features=include_features
            )

            return {
                "status": "success",
                "skill": self.name,
                "overall": {
                    "total": result.overall_total,
                    "completed": result.overall_completed,
                    "percentage": round(result.overall_percentage, 1)
                },
                "plans": [
                    {
                        "name": p.name,
                        "path": p.path,
                        "phases": len(p.phases),
                        "total": p.total_criteria,
                        "completed": p.completed_criteria,
                        "percentage": round(p.completion_percentage, 1),
                        "current_phase": p.current_phase
                    }
                    for p in result.plans
                ],
                "next_action": result.next_action,
                "report": self.generate_report(result)
            }

        except Exception as e:
            return {
                "status": "error",
                "skill": self.name,
                "error": str(e)
            }

    def check_progress(
        self,
        work_dir: Optional[Path] = None,
        include_features: bool = True
    ) -> ProgressResult:
        """
        检查进度

        Args:
            work_dir: 工作目录
            include_features: 是否包含功能计划

        Returns:
            ProgressResult 进度结果
        """
        work_dir = Path(work_dir) if work_dir else self.base_path
        plans = []

        # 1. 解析主执行计划
        main_plan = self._parse_main_plan(work_dir)
        if main_plan:
            plans.append(main_plan)

        # 2. 解析功能计划
        if include_features:
            feature_plans = self._parse_feature_plans(work_dir)
            plans.extend(feature_plans)

        # 3. 计算总体进度
        overall_total = sum(p.total_criteria for p in plans)
        overall_completed = sum(p.completed_criteria for p in plans)

        # 4. 确定下一步行动
        next_action = self._determine_next_action(plans)

        return ProgressResult(
            plans=plans,
            overall_total=overall_total,
            overall_completed=overall_completed,
            next_action=next_action
        )

    def _parse_main_plan(self, work_dir: Path) -> Optional[PlanProgress]:
        """解析主执行计划"""
        plan_path = work_dir / "EXECUTION_PLAN.md"

        if not plan_path.exists():
            return None

        try:
            content = plan_path.read_text(encoding="utf-8")
            phases = self._extract_phases(content)

            # 找到当前阶段
            current_phase = None
            for phase in phases:
                if phase.status == PhaseStatus.IN_PROGRESS:
                    current_phase = phase.number
                    break

            return PlanProgress(
                name="Main Project",
                path=str(plan_path),
                total_phases=len(phases),
                phases=phases,
                current_phase=current_phase
            )

        except Exception as e:
            print(f"解析主计划失败: {e}")
            return None

    def _parse_feature_plans(self, work_dir: Path) -> List[PlanProgress]:
        """解析功能计划"""
        feature_plans = []

        # 查找功能目录模式
        feature_patterns = [
            work_dir / "features" / "*" / "EXECUTION_PLAN.md",
            work_dir / "FEATURES" / "*" / "EXECUTION_PLAN.md",
            work_dir / "feature" / "*" / "EXECUTION_PLAN.md",
        ]

        for pattern in feature_patterns:
            for plan_path in pattern.parent.glob("*/EXECUTION_PLAN.md"):
                try:
                    content = plan_path.read_text(encoding="utf-8")
                    phases = self._extract_phases(content)

                    # 从路径提取功能名称
                    feature_name = plan_path.parent.name

                    # 找到当前阶段
                    current_phase = None
                    for phase in phases:
                        if phase.status == PhaseStatus.IN_PROGRESS:
                            current_phase = phase.number
                            break

                    feature_plans.append(PlanProgress(
                        name=f"Feature: {feature_name}",
                        path=str(plan_path),
                        total_phases=len(phases),
                        phases=phases,
                        current_phase=current_phase
                    ))

                except Exception as e:
                    print(f"解析功能计划失败 {plan_path}: {e}")

        return feature_plans

    def _extract_phases(self, content: str) -> List[PhaseProgress]:
        """从内容提取阶段信息"""
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

            # 计算任务验收标准
            total_criteria = 0
            completed_criteria = 0

            # 查找任务部分
            task_pattern = r"####\s*Task\s+\d+\.\d+"
            task_matches = list(re.finditer(task_pattern, phase_content))

            for j, task_match in enumerate(task_matches):
                task_start = task_match.end()
                task_end = task_matches[j + 1].start() if j + 1 < len(task_matches) else len(phase_content)
                task_content = phase_content[task_start:task_end]

                # 查找验收标准复选框
                criteria_pattern = r"-\s*\[(.)\]"
                criteria_matches = re.findall(criteria_pattern, task_content)

                for checkbox in criteria_matches:
                    total_criteria += 1
                    if checkbox.strip() == "x":
                        completed_criteria += 1

            # 确定阶段状态
            if total_criteria == 0:
                status = PhaseStatus.NOT_STARTED
            elif completed_criteria == total_criteria:
                status = PhaseStatus.COMPLETE
            elif completed_criteria > 0:
                status = PhaseStatus.IN_PROGRESS
            else:
                status = PhaseStatus.NOT_STARTED

            # 提取检查点标准
            checkpoint_criteria = 0
            completed_checkpoint = 0
            checkpoint_pattern = r"###\s*Phase\s+\d+\s*Checkpoint.*?(?=###|\Z)"
            checkpoint_match = re.search(checkpoint_pattern, phase_content, re.DOTALL | re.IGNORECASE)

            if checkpoint_match:
                checkpoint_content = checkpoint_match.group(0)
                checkpoint_boxes = re.findall(r"-\s*\[(.)\]", checkpoint_content)
                checkpoint_criteria = len(checkpoint_boxes)
                completed_checkpoint = sum(1 for box in checkpoint_boxes if box.strip() == "x")

            phases.append(PhaseProgress(
                number=phase_number,
                name=phase_name,
                status=status,
                total_criteria=total_criteria,
                completed_criteria=completed_criteria,
                checkpoint_criteria=checkpoint_criteria,
                completed_checkpoint=completed_checkpoint
            ))

        return phases

    def _determine_next_action(self, plans: List[PlanProgress]) -> str:
        """确定下一步行动"""
        if not plans:
            return "创建 EXECUTION_PLAN.md 开始项目"

        # 检查主计划
        main_plan = next((p for p in plans if p.name == "Main Project"), None)

        if main_plan:
            # 找到第一个未完成的阶段
            for phase in main_plan.phases:
                if phase.status != PhaseStatus.COMPLETE:
                    if phase.status == PhaseStatus.IN_PROGRESS:
                        return f"继续主项目阶段 {phase.number}: {phase.name}"
                    else:
                        return f"开始主项目阶段 {phase.number}: {phase.name}"

        # 检查功能计划
        for plan in plans:
            if plan.name.startswith("Feature:"):
                for phase in plan.phases:
                    if phase.status != PhaseStatus.COMPLETE:
                        feature_name = plan.name.replace("Feature: ", "")
                        if phase.status == PhaseStatus.IN_PROGRESS:
                            return f"继续功能 '{feature_name}' 阶段 {phase.number}"
                        else:
                            return f"开始功能 '{feature_name}' 阶段 {phase.number}"

        return "所有计划已完成！运行最终检查点"

    def generate_report(self, result: ProgressResult) -> str:
        """生成进度报告"""
        lines = [
            "项目进度报告",
            "=" * 60,
            "",
            f"总体进度: {result.overall_completed}/{result.overall_total} ({result.overall_percentage:.1f}%)",
            f"计划数量: {len(result.plans)}",
            ""
        ]

        # 显示每个计划
        for plan in result.plans:
            lines.extend([
                f"{plan.name}",
                "-" * 60,
                f"  路径: {plan.path}",
                f"  阶段: {plan.total_phases}",
                f"  进度: {plan.completed_criteria}/{plan.total_criteria} ({plan.completion_percentage:.1f}%)",
                "",
                "  阶段详情:",
            ])

            for phase in plan.phases:
                icon = {
                    PhaseStatus.COMPLETE: "✅",
                    PhaseStatus.IN_PROGRESS: "🔄",
                    PhaseStatus.NOT_STARTED: "⏳"
                }.get(phase.status, "❓")

                lines.append(
                    f"    {icon} Phase {phase.number}: {phase.name} "
                    f"({phase.completed_criteria}/{phase.total_criteria})"
                )

            lines.append("")

        # 下一步行动
        lines.extend([
            "下一步行动:",
            "-" * 60,
            result.next_action,
            ""
        ])

        return "\n".join(lines)

    def get_capabilities(self) -> Dict[str, Any]:
        """获取技能能力信息"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "features": [
                "main_plan_parsing",
                "feature_plan_parsing",
                "progress_calculation",
                "status_tracking",
                "next_action_recommendation",
                "report_generation"
            ],
            "metrics": [
                "task_criteria_count",
                "completion_percentage",
                "phase_status",
                "overall_progress"
            ]
        }


# 向后兼容
Progress_Skill = ProgressSkill


def main():
    """入口函数 - 演示用法"""
    print("=" * 60)
    print("Progress Skill - 演示")
    print("=" * 60)

    skill = ProgressSkill()

    # 演示: 技能能力
    print("\n1. 技能能力")
    print("-" * 40)
    caps = skill.get_capabilities()
    print(f"技能: {caps['name']}")
    print(f"功能: {', '.join(caps['features'])}")

    # 演示: 检查进度
    print("\n2. 检查当前目录进度")
    print("-" * 40)
    result = skill.check_progress()
    print(f"总体: {result.overall_completed}/{result.overall_total} ({result.overall_percentage:.1f}%)")
    print(f"计划数: {len(result.plans)}")
    print(f"下一步: {result.next_action}")

    print("\n" + "=" * 60)
    print("演示完成！")
    print("=" * 60)

    return skill


if __name__ == "__main__":
    main()
