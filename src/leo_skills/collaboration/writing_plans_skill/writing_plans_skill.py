# -*- coding: utf-8 -*-
"""
writing_plans_skill - 编写实施计划技能

基于 obra/superpowers 的 writing-plans 技能。
编写全面的实施计划，假设工程师对代码库零上下文。
"""
from leo_skills.core.base_executor import BaseExecutor

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


class TaskType(Enum):
    """任务类型"""
    MODEL = "model"
    API = "api"
    UI = "ui"
    TEST = "test"
    CONFIG = "config"
    DOCS = "docs"
    REFACTOR = "refactor"


@dataclass
class TaskStep:
    """任务步骤"""
    number: int
    description: str
    command: Optional[str] = None
    expected_output: Optional[str] = None
    code_block: Optional[str] = None


@dataclass
class Task:
    """计划任务"""
    id: str
    name: str
    description: str
    task_type: TaskType
    files_to_create: List[str] = field(default_factory=list)
    files_to_modify: List[str] = field(default_factory=list)
    test_files: List[str] = field(default_factory=list)
    steps: List[TaskStep] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)


@dataclass
class ExecutionPlan:
    """执行计划"""
    title: str
    target: str
    architecture: str
    tech_stack: str
    tasks: List[Task] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class WritingPlansResult:
    """编写计划结果"""
    status: str
    plan: Optional[ExecutionPlan] = None
    plan_path: Optional[str] = None
    tasks_count: int = 0
    message: str = ""


class WritingPlansSkill(BaseExecutor):
    """
    编写实施计划技能

    核心理念：假设工程师对代码库零上下文，文档化他们需要知道的一切。
    将整个计划提供为小步任务。DRY。YAGNI。TDD。频繁提交。
    """

    def __init__(self):
        self.name = "writing_plans_skill"
        self.version = "1.0.0"
        self.description = "编写详细的实施计划，提供小步任务粒度"
        self.category = "collaboration"

    def execute(
        self,
        feature_name: str,
        feature_description: str,
        architecture: str,
        tech_stack: str,
        output_dir: str = "docs/plans",
        project_context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        执行编写计划技能

        Args:
            feature_name: 功能名称
            feature_description: 功能描述
            architecture: 架构方法描述
            tech_stack: 技术栈
            output_dir: 输出目录
            project_context: 项目上下文信息

        Returns:
            包含执行计划的结果
        """
        try:
            # 创建执行计划
            plan = self._create_execution_plan(
                feature_name=feature_name,
                feature_description=feature_description,
                architecture=architecture,
                tech_stack=tech_stack,
                project_context=project_context
            )

            # 生成计划文件路径
            date_prefix = datetime.now().strftime("%Y-%m-%d")
            safe_name = feature_name.lower().replace(" ", "-").replace("_", "-")
            filename = f"{date_prefix}-{safe_name}.md"
            plan_path = Path(output_dir) / filename

            # 生成计划文档
            plan_content = self._generate_plan_document(plan)

            result = WritingPlansResult(
                status="completed",
                plan=plan,
                plan_path=str(plan_path),
                tasks_count=len(plan.tasks),
                message=f"计划已创建: {plan_path}"
            )

            return {
                "status": "success",
                "result": result,
                "plan_content": plan_content,
                "plan_path": str(plan_path),
                "tasks_count": len(plan.tasks)
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "skill": self.name
            }

    def _create_execution_plan(
        self,
        feature_name: str,
        feature_description: str,
        architecture: str,
        tech_stack: str,
        project_context: Optional[Dict[str, Any]] = None
    ) -> ExecutionPlan:
        """创建执行计划"""
        context = project_context or {}

        plan = ExecutionPlan(
            title=f"{feature_name} 实施计划",
            target=feature_description,
            architecture=architecture,
            tech_stack=tech_stack
        )

        # 基于功能描述分析并创建任务
        tasks = self._analyze_and_create_tasks(
            feature_name=feature_name,
            feature_description=feature_description,
            tech_stack=tech_stack,
            context=context
        )
        plan.tasks = tasks

        return plan

    def _analyze_and_create_tasks(
        self,
        feature_name: str,
        feature_description: str,
        tech_stack: str,
        context: Dict[str, Any]
    ) -> List[Task]:
        """分析功能并创建任务列表"""
        tasks = []

        # 根据技术栈和描述推断任务类型
        tech_lower = tech_stack.lower()

        # 任务1: 模型/数据结构
        if "model" in feature_description.lower() or "data" in feature_description.lower():
            tasks.append(self._create_model_task(tech_stack))

        # 任务2: API/服务端点
        if "api" in feature_description.lower() or "endpoint" in feature_description.lower():
            tasks.append(self._create_api_task(tech_stack))

        # 任务3: UI/前端组件
        if "ui" in feature_description.lower() or "component" in feature_description.lower() or "page" in feature_description.lower():
            tasks.append(self._create_ui_task(tech_stack))

        # 任务4: 配置
        tasks.append(self._create_config_task(tech_stack))

        # 任务5: 测试
        tasks.append(self._create_test_task(tech_stack))

        # 如果没有识别出特定任务，创建通用任务
        if not tasks:
            tasks = self._create_generic_tasks(feature_name, tech_stack)

        # 分配任务ID
        for i, task in enumerate(tasks, 1):
            task.id = f"T{i:02d}"

        return tasks

    def _create_model_task(self, tech_stack: str) -> Task:
        """创建模型任务"""
        steps = [
            TaskStep(1, "编写失败的测试", code_block="def test_model_creation():\n    model = Model()\n    assert model is not None"),
            TaskStep(2, "运行测试验证失败", command="pytest tests/test_model.py -v", expected_output="FAIL: Model not defined"),
            TaskStep(3, "编写最少实现"),
            TaskStep(4, "运行测试验证通过", command="pytest tests/test_model.py -v", expected_output="PASS"),
            TaskStep(5, "提交", command="git add . && git commit -m 'feat: add model'")
        ]

        return Task(
            id="",
            name="数据模型",
            description="创建核心数据模型",
            task_type=TaskType.MODEL,
            files_to_create=["src/models/model.py", "tests/test_model.py"],
            steps=steps
        )

    def _create_api_task(self, tech_stack: str) -> Task:
        """创建API任务"""
        steps = [
            TaskStep(1, "编写失败的测试"),
            TaskStep(2, "运行测试验证失败"),
            TaskStep(3, "实现API端点"),
            TaskStep(4, "运行测试验证通过"),
            TaskStep(5, "提交")
        ]

        return Task(
            id="",
            name="API端点",
            description="实现API端点",
            task_type=TaskType.API,
            files_to_create=["src/api/routes.py", "tests/test_api.py"],
            steps=steps
        )

    def _create_ui_task(self, tech_stack: str) -> Task:
        """创建UI任务"""
        steps = [
            TaskStep(1, "编写组件测试"),
            TaskStep(2, "运行测试验证失败"),
            TaskStep(3, "实现UI组件"),
            TaskStep(4, "运行测试验证通过"),
            TaskStep(5, "提交")
        ]

        return Task(
            id="",
            name="UI组件",
            description="实现用户界面组件",
            task_type=TaskType.UI,
            files_to_create=["src/components/Component.tsx", "src/components/Component.test.tsx"],
            steps=steps
        )

    def _create_config_task(self, tech_stack: str) -> Task:
        """创建配置任务"""
        return Task(
            id="",
            name="配置",
            description="添加必要的配置",
            task_type=TaskType.CONFIG,
            files_to_modify=[".env.example", "config.py"],
            steps=[TaskStep(1, "更新配置文件")]
        )

    def _create_test_task(self, tech_stack: str) -> Task:
        """创建测试任务"""
        return Task(
            id="",
            name="集成测试",
            description="添加集成测试",
            task_type=TaskType.TEST,
            files_to_create=["tests/integration/test_feature.py"],
            steps=[TaskStep(1, "编写集成测试")]
        )

    def _create_generic_tasks(self, feature_name: str, tech_stack: str) -> List[Task]:
        """创建通用任务"""
        return [
            Task(
                id="",
                name="实现核心功能",
                description=f"实现{feature_name}的核心功能",
                task_type=TaskType.MODEL,
                steps=[
                    TaskStep(1, "编写失败的测试"),
                    TaskStep(2, "运行测试验证失败"),
                    TaskStep(3, "编写最少实现"),
                    TaskStep(4, "运行测试验证通过"),
                    TaskStep(5, "提交")
                ]
            ),
            Task(
                id="",
                name="添加测试",
                description="添加单元测试和集成测试",
                task_type=TaskType.TEST,
                steps=[TaskStep(1, "编写测试")]
            )
        ]

    def _generate_plan_document(self, plan: ExecutionPlan) -> str:
        """生成计划文档内容"""
        lines = [
            f"# {plan.title}",
            "",
            "> **For Claude:** REQUIRED SUB-SKILL: 使用 executing_plans_skill 逐任务实施此计划。",
            "",
            f"**目标**：{plan.target}",
            "",
            f"**架构**：{plan.architecture}",
            "",
            f"**技术栈**：{plan.tech_stack}",
            "",
            "---",
            "",
        ]

        for task in plan.tasks:
            lines.extend([
                f"### 任务 {task.id}：{task.name}",
                "",
                f"**描述**：{task.description}",
                "",
            ])

            if task.files_to_create:
                lines.append("**创建文件**：")
                for f in task.files_to_create:
                    lines.append(f"- `{f}`")
                lines.append("")

            if task.files_to_modify:
                lines.append("**修改文件**：")
                for f in task.files_to_modify:
                    lines.append(f"- `{f}`")
                lines.append("")

            if task.steps:
                lines.append("**步骤**：")
                for step in task.steps:
                    lines.append(f"{step.number}. {step.description}")
                    if step.code_block:
                        lines.extend(["", "```python", step.code_block, "```", ""])
                    if step.command:
                        lines.extend([f"   - 运行：`{step.command}`"])
                    if step.expected_output:
                        lines.extend([f"   - 预期：`{step.expected_output}`"])
                lines.append("")

            lines.extend(["---", ""])

        lines.extend([
            "## 执行检查清单",
            "",
        ])
        for task in plan.tasks:
            lines.append(f"- [ ] 任务 {task.id}: {task.name}")
        lines.append("")

        return "\n".join(lines)


def main():
    """入口函数"""
    return WritingPlansSkill()


if __name__ == "__main__":
    skill = main()
