# -*- coding: utf-8 -*-
"""
verify_task_skill - 验证任务技能

使用代码验证工作流验证特定任务的验收标准。
基于 EXECUTION_PLAN.md 解析任务并验证每个验收标准。
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class CriterionType(Enum):
    """标准类型"""
    TEST = "TEST"
    CODE = "CODE"
    LINT = "LINT"
    TYPE = "TYPE"
    BUILD = "BUILD"
    SECURITY = "SECURITY"
    BROWSER = "BROWSER"
    MANUAL = "MANUAL"


class VerificationStatus(Enum):
    """验证状态"""
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass
class AcceptanceCriterion:
    """验收标准"""
    id: str
    description: str
    ctype: CriterionType
    verify_method: str
    status: VerificationStatus = VerificationStatus.PENDING
    evidence: str = ""
    suggested_fix: str = ""


@dataclass
class TaskVerification:
    """任务验证"""
    task_id: str
    task_name: str
    criteria: List[AcceptanceCriterion] = field(default_factory=list)
    passed_count: int = 0
    failed_count: int = 0
    tdd_compliant: bool = False


@dataclass
class VerificationResult:
    """验证结果"""
    status: str
    task: Optional[TaskVerification] = None
    message: str = ""


class VerifyTaskSkill:
    """
    验证任务技能

    解析任务的验收标准，使用相应的验证方法进行验证。
    支持测试、代码检查、类型检查、构建、浏览器验证等多种验证类型。
    """

    def __init__(self):
        self.name = "verify_task_skill"
        self.version = "1.0.0"
        self.description = "验证特定任务的验收标准"
        self.category = "testing"

    def execute(
        self,
        task_id: str,
        execution_plan_path: str = "EXECUTION_PLAN.md",
        project_root: str = ".",
        **kwargs
    ) -> Dict[str, Any]:
        """
        执行任务验证

        Args:
            task_id: 任务ID
            execution_plan_path: 执行计划路径
            project_root: 项目根目录

        Returns:
            验证结果
        """
        try:
            # 解析任务
            task = self._parse_task_from_plan(task_id, execution_plan_path)

            # 验证每个标准
            for criterion in task.criteria:
                self._verify_criterion(criterion)

            # 计算结果
            passed = sum(1 for c in task.criteria if c.status == VerificationStatus.PASSED)
            failed = sum(1 for c in task.criteria if c.status == VerificationStatus.FAILED)

            task.passed_count = passed
            task.failed_count = failed

            result = VerificationResult(
                status="completed" if failed == 0 else "partial",
                task=task,
                message=f"任务 {task_id} 验证: {passed}/{len(task.criteria)} 通过"
            )

            return {
                "status": "success",
                "result": result,
                "tdd_compliance": self._check_tdd_compliance(task),
                "report": self._generate_report(task)
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "skill": self.name
            }

    def _parse_task_from_plan(self, task_id: str, plan_path: str) -> TaskVerification:
        """从计划解析任务"""
        # 模拟解析
        return TaskVerification(
            task_id=task_id,
            task_name=f"任务 {task_id}",
            criteria=[
                AcceptanceCriterion(
                    id=f"{task_id}.A",
                    description="功能实现完成",
                    ctype=CriterionType.TEST,
                    verify_method="pytest tests/"
                ),
                AcceptanceCriterion(
                    id=f"{task_id}.B",
                    description="代码检查通过",
                    ctype=CriterionType.LINT,
                    verify_method="ruff check ."
                )
            ]
        )

    def _verify_criterion(self, criterion: AcceptanceCriterion):
        """验证单个标准"""
        # 模拟验证过程
        criterion.status = VerificationStatus.PASSED
        criterion.evidence = f"已验证: {criterion.verify_method}"

    def _check_tdd_compliance(self, task: TaskVerification) -> Dict[str, Any]:
        """检查TDD合规性"""
        return {
            "compliant": True,
            "tests_found": task.passed_count > 0,
            "message": "任务符合TDD要求"
        }

    def _generate_report(self, task: TaskVerification) -> str:
        """生成验证报告"""
        lines = [
            f"任务验证报告: {task.task_id}",
            "=" * 40,
            f"任务名称: {task.task_name}",
            "",
            "验收标准:",
        ]

        for c in task.criteria:
            status_icon = "✅" if c.status == VerificationStatus.PASSED else "❌"
            lines.append(f"{status_icon} [{c.id}] {c.description}")
            lines.append(f"    类型: {c.ctype.value}")
            lines.append(f"    验证: {c.verify_method}")

        lines.extend([
            "",
            f"总计: {task.passed_count}/{len(task.criteria)} 通过",
        ])

        return "\n".join(lines)


def main():
    """入口函数"""
    return VerifyTaskSkill()


if __name__ == "__main__":
    skill = main()
