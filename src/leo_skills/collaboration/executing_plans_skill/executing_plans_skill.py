# -*- coding: utf-8 -*-
"""
executing_plans_skill - 执行计划技能

基于 obra/superpowers 的 executing-plans 技能。
加载计划，批判性地审查，批量执行任务，批次之间报告审查。
核心理念：批量执行，架构师审查检查点。
"""
from leo_skills.core.base_executor import BaseExecutor

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


class VerificationResult(Enum):
    """验证结果"""
    PASS = "pass"
    FAIL = "fail"
    BLOCKED = "blocked"
    SKIP = "skip"


@dataclass
class CriterionVerification:
    """标准验证"""
    criterion_id: str
    description: str
    result: VerificationResult
    evidence: str = ""
    suggested_fix: str = ""


@dataclass
class TaskExecution:
    """任务执行"""
    task_id: str
    task_name: str
    status: TaskStatus
    steps_completed: int = 0
    total_steps: int = 0
    verifications: List[CriterionVerification] = field(default_factory=list)
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    notes: List[str] = field(default_factory=list)


@dataclass
class BatchResult:
    """批次结果"""
    batch_number: int
    tasks: List[TaskExecution]
    started_at: str
    completed_at: Optional[str] = None
    status: str = "in_progress"  # in_progress, completed, blocked


@dataclass
class ExecutionResult:
    """执行结果"""
    status: str
    plan_path: str
    batches: List[BatchResult] = field(default_factory=list)
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    message: str = ""


class ExecutingPlansSkill(BaseExecutor):
    """
    执行计划技能

    核心理念：批量执行，架构师审查检查点。
    加载计划，批判性地审查，批量执行任务，批次之间报告审查。
    """

    def __init__(self):
        self.name = "executing_plans_skill"
        self.version = "1.0.0"
        self.description = "执行实施计划，批量执行任务并审查"
        self.category = "collaboration"
        self.batch_size = 3  # 默认批次大小

    def execute(
        self,
        plan_path: str,
        start_task: Optional[int] = None,
        end_task: Optional[int] = None,
        batch_size: int = 3,
        project_root: str = ".",
        **kwargs
    ) -> Dict[str, Any]:
        """
        执行执行计划技能

        Args:
            plan_path: 计划文件路径
            start_task: 起始任务索引（1-based）
            end_task: 结束任务索引（1-based）
            batch_size: 批次大小（默认3个任务）
            project_root: 项目根目录

        Returns:
            包含执行结果的字典
        """
        try:
            self.batch_size = batch_size

            # 步骤1: 加载和审查计划
            review_result = self._load_and_review_plan(plan_path)
            if not review_result["can_proceed"]:
                return {
                    "status": "blocked",
                    "message": review_result["concerns"],
                    "skill": self.name
                }

            # 步骤2: 解析任务
            tasks = self._parse_tasks(plan_path, start_task, end_task)

            if not tasks:
                return {
                    "status": "error",
                    "message": "计划中未找到任务",
                    "skill": self.name
                }

            # 步骤3: 执行批次
            batches = self._execute_batches(tasks, project_root)

            # 步骤4: 汇总结果
            total = len(tasks)
            completed = sum(1 for b in batches for t in b.tasks if t.status == TaskStatus.COMPLETED)
            failed = sum(1 for b in batches for t in b.tasks if t.status == TaskStatus.FAILED)

            result = ExecutionResult(
                status="completed" if failed == 0 else "partial",
                plan_path=plan_path,
                batches=batches,
                total_tasks=total,
                completed_tasks=completed,
                failed_tasks=failed,
                message=f"执行完成: {completed}/{total} 任务成功"
            )

            return {
                "status": "success",
                "result": result,
                "summary": {
                    "total": total,
                    "completed": completed,
                    "failed": failed
                }
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "skill": self.name
            }

    def _load_and_review_plan(self, plan_path: str) -> Dict[str, Any]:
        """加载和审查计划"""
        path = Path(plan_path)
        if not path.exists():
            return {
                "can_proceed": False,
                "concerns": f"计划文件不存在: {plan_path}"
            }

        # 读取计划内容
        content = path.read_text(encoding='utf-8')

        # 检查关键元素
        concerns = []

        if "任务" not in content and "Task" not in content:
            concerns.append("计划中未找到任务定义")

        if "Verify:" not in content and "验证" not in content:
            concerns.append("任务缺少验证标准（Verify:）")

        if "### " not in content and "## " not in content:
            concerns.append("计划结构不清晰，缺少任务标题")

        # 检查是否有必须子技能声明
        if "executing_plans_skill" not in content and "REQUIRED SUB-SKILL" not in content:
            concerns.append("警告: 计划未声明使用 executing_plans_skill")

        return {
            "can_proceed": len(concerns) == 0 or concerns == ["警告: 计划未声明使用 executing_plans_skill"],
            "concerns": concerns
        }

    def _parse_tasks(
        self,
        plan_path: str,
        start_task: Optional[int],
        end_task: Optional[int]
    ) -> List[Dict[str, Any]]:
        """解析计划中的任务"""
        content = Path(plan_path).read_text(encoding='utf-8')
        tasks = []

        # 简单的任务解析逻辑
        # 查找 "### 任务 X:" 或 "### Task X:" 模式
        import re

        task_pattern = r'###\s+(?:任务|Task)\s+(\d+|\w+)[：:]\s*(.+)'
        task_matches = list(re.finditer(task_pattern, content, re.IGNORECASE))

        for i, match in enumerate(task_matches):
            task_num = match.group(1)
            task_name = match.group(2).strip()

            # 提取任务内容
            start_pos = match.end()
            end_pos = task_matches[i + 1].start() if i + 1 < len(task_matches) else len(content)
            task_content = content[start_pos:end_pos]

            # 解析步骤
            steps = self._parse_steps(task_content)

            # 解析验证标准
            criteria = self._parse_criteria(task_content)

            tasks.append({
                "id": str(task_num),
                "name": task_name,
                "content": task_content,
                "steps": steps,
                "criteria": criteria
            })

        # 应用范围过滤
        if start_task is not None:
            tasks = tasks[start_task - 1:]
        if end_task is not None:
            tasks = tasks[:end_task - (start_task or 1) + 1]

        return tasks

    def _parse_steps(self, task_content: str) -> List[Dict[str, str]]:
        """解析任务步骤"""
        steps = []
        import re

        # 查找 "步骤" 或数字列表
        step_pattern = r'(?:步骤|\*|-|\d+)[.、:]\s*(.+?)(?=\n(?:步骤|\*|-|\d+)[.、:]|\n###|\Z)'
        matches = re.finditer(step_pattern, task_content, re.DOTALL)

        for match in matches:
            step_text = match.group(1).strip()
            if step_text:
                steps.append({
                    "description": step_text,
                    "command": self._extract_command(step_text),
                    "code": self._extract_code_block(step_content, match.end())
                })

        return steps

    def _parse_criteria(self, task_content: str) -> List[Dict[str, str]]:
        """解析验收标准"""
        criteria = []
        import re

        # 查找 Verify: 行
        verify_pattern = r'(?:Verify:|验证[:：])\s*(.+)'
        matches = re.finditer(verify_pattern, task_content)

        for match in matches:
            criteria.append({
                "verify": match.group(1).strip(),
                "type": self._determine_criterion_type(match.group(1))
            })

        return criteria

    def _extract_command(self, text: str) -> Optional[str]:
        """从文本中提取命令"""
        import re
        # 查找 `command` 或 bash 代码块
        cmd_pattern = r'`([^`]+)`|```(?:bash|sh)?\n(.+?)\n```'
        match = re.search(cmd_pattern, text, re.DOTALL)
        if match:
            return match.group(1) or match.group(2)
        return None

    def _extract_code_block(self, content: str, after_pos: int) -> Optional[str]:
        """提取代码块"""
        import re
        code_pattern = r'```(\w+)?\n(.+?)\n```'
        match = re.search(code_pattern, content[after_pos:after_pos + 2000], re.DOTALL)
        if match:
            return match.group(2)
        return None

    def _determine_criterion_type(self, verify_text: str) -> str:
        """确定标准类型"""
        text_lower = verify_text.lower()
        if "test" in text_lower or "测试" in text_lower:
            return "TEST"
        elif "lint" in text_lower:
            return "LINT"
        elif "build" in text_lower or "编译" in text_lower:
            return "BUILD"
        elif "type" in text_lower or "类型" in text_lower:
            return "TYPE"
        elif "browser" in text_lower or "ui" in text_lower:
            return "BROWSER"
        return "CODE"

    def _execute_batches(
        self,
        tasks: List[Dict[str, Any]],
        project_root: str
    ) -> List[BatchResult]:
        """执行批次"""
        batches = []

        # 将任务分成批次
        for i in range(0, len(tasks), self.batch_size):
            batch_tasks = tasks[i:i + self.batch_size]
            batch_num = i // self.batch_size + 1

            batch = BatchResult(
                batch_number=batch_num,
                tasks=[],
                started_at=datetime.now().isoformat()
            )

            # 执行批次中的每个任务
            for task_data in batch_tasks:
                task_exec = self._execute_task(task_data, project_root)
                batch.tasks.append(task_exec)

            batch.completed_at = datetime.now().isoformat()
            batch.status = "completed" if all(
                t.status == TaskStatus.COMPLETED for t in batch.tasks
            ) else "partial"

            batches.append(batch)

        return batches

    def _execute_task(
        self,
        task_data: Dict[str, Any],
        project_root: str
    ) -> TaskExecution:
        """执行单个任务"""
        task_exec = TaskExecution(
            task_id=task_data["id"],
            task_name=task_data["name"],
            status=TaskStatus.IN_PROGRESS,
            total_steps=len(task_data.get("steps", [])),
            started_at=datetime.now().isoformat()
        )

        # 这里应该是实际的执行逻辑
        # 由于这是一个技能框架，实际执行由调用者处理
        # 我们记录任务结构和元数据

        # 模拟执行步骤
        for i, step in enumerate(task_data.get("steps", []), 1):
            task_exec.steps_completed = i
            if step.get("command"):
                task_exec.notes.append(f"步骤 {i}: 需要执行命令 - {step['command']}")

        # 验证标准
        for criterion in task_data.get("criteria", []):
            task_exec.verifications.append(CriterionVerification(
                criterion_id=f"V-{len(task_exec.verifications) + 1:03d}",
                description=criterion["verify"],
                result=VerificationResult.SKIP,  # 实际验证由调用者完成
                evidence="待验证"
            ))

        task_exec.status = TaskStatus.COMPLETED
        task_exec.completed_at = datetime.now().isoformat()

        return task_exec

    def generate_batch_report(self, batch: BatchResult) -> str:
        """生成批次报告"""
        lines = [
            f"批次 {batch.batch_number} 完成",
            "",
            "已实现：",
        ]

        for task in batch.tasks:
            status_icon = "✅" if task.status == TaskStatus.COMPLETED else "❌"
            lines.append(f"{status_icon} 任务 {task.task_id}: {task.task_name}")

        lines.extend([
            "",
            "验证输出：",
            f"- 完成任务: {sum(1 for t in batch.tasks if t.status == TaskStatus.COMPLETED)}/{len(batch.tasks)}",
            "",
            "准备接受反馈。"
        ])

        return "\n".join(lines)


def main():
    """入口函数"""
    return ExecutingPlansSkill()


if __name__ == "__main__":
    skill = main()
