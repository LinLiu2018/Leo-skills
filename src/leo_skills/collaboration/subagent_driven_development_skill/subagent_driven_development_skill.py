# -*- coding: utf-8 -*-
"""
subagent_driven_development_skill - 子代理驱动开发技能

基于 obra/superpowers 的 subagent-driven-development 技能。
核心理念：每个任务一个新子代理 + 两阶段审查 = 高质量，快速迭代。
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    IMPLEMENTED = "implemented"
    SPEC_REVIEWED = "spec_reviewed"
    CODE_REVIEWED = "code_reviewed"
    COMPLETED = "completed"
    FAILED = "failed"


class ReviewStatus(Enum):
    """审查状态"""
    PENDING = "pending"
    APPROVED = "approved"
    NEEDS_FIX = "needs_fix"


@dataclass
class Task:
    """开发任务"""
    id: str
    name: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    implementation: str = ""
    spec_review_status: ReviewStatus = ReviewStatus.PENDING
    code_review_status: ReviewStatus = ReviewStatus.PENDING
    notes: List[str] = field(default_factory=list)


@dataclass
class DevelopmentSession:
    """开发会话"""
    plan_path: str
    tasks: List[Task] = field(default_factory=list)
    current_task_index: int = 0
    status: str = "in_progress"
    started_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None


@dataclass
class SubagentDrivenDevelopmentResult:
    """子代理驱动开发结果"""
    status: str
    session: Optional[DevelopmentSession] = None
    completed_tasks: int = 0
    total_tasks: int = 0
    message: str = ""


class SubagentDrivenDevelopmentSkill:
    """
    子代理驱动开发技能

    核心理念：每个任务一个新子代理 + 两阶段审查（先规范符合性，再代码质量）= 高质量，快速迭代。
    """

    def __init__(self):
        self.name = "subagent_driven_development_skill"
        self.version = "1.0.0"
        self.description = "子代理驱动开发，两阶段审查工作流"
        self.category = "collaboration"

    def execute(
        self,
        plan_path: str,
        start_task: int = 1,
        end_task: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        执行子代理驱动开发

        Args:
            plan_path: 执行计划路径
            start_task: 起始任务索引（1-based）
            end_task: 结束任务索引（1-based）

        Returns:
            开发结果
        """
        try:
            # 创建开发会话
            session = DevelopmentSession(
                plan_path=plan_path,
                tasks=self._parse_tasks_from_plan(plan_path, start_task, end_task)
            )

            result = SubagentDrivenDevelopmentResult(
                status="started",
                session=session,
                total_tasks=len(session.tasks),
                message=f"开发会话已启动: {len(session.tasks)} 个任务"
            )

            return {
                "status": "success",
                "result": result,
                "workflow": {
                    "steps": [
                        "1. 读取计划，提取所有任务",
                        "2. 对每个任务:",
                        "   a. 分发实施子代理",
                        "   b. 实施子代理提问 -> 回答",
                        "   c. 实施子代理实现、测试、提交、自我审查",
                        "   d. 分发规范合规审查子代理",
                        "   e. 规范审查通过? -> 否则修复 -> 重新审查",
                        "   f. 分发代码质量审查子代理",
                        "   g. 代码审查通过? -> 否则修复 -> 重新审查",
                        "   h. 标记任务完成",
                        "3. 所有任务后分发最终代码审查",
                        "4. 使用 finishing-development-branch 完成"
                    ]
                }
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "skill": self.name
            }

    def _parse_tasks_from_plan(
        self,
        plan_path: str,
        start_task: int,
        end_task: Optional[int]
    ) -> List[Task]:
        """从计划解析任务"""
        # 模拟解析任务
        tasks = []
        # 实际实现需要读取计划文件并解析任务
        # 这里返回示例任务
        for i in range(start_task, (end_task or start_task + 2) + 1):
            tasks.append(Task(
                id=f"T{i:02d}",
                name=f"任务 {i}",
                description=f"实现任务 {i}"
            ))
        return tasks

    def get_next_action(self, session: DevelopmentSession) -> Dict[str, Any]:
        """获取下一步行动"""
        if session.current_task_index >= len(session.tasks):
            return {
                "action": "complete",
                "message": "所有任务已完成"
            }

        current_task = session.tasks[session.current_task_index]

        if current_task.status == TaskStatus.PENDING:
            return {
                "action": "dispatch_implementer",
                "task": current_task,
                "message": f"分发实施子代理执行任务 {current_task.id}"
            }
        elif current_task.status == TaskStatus.IMPLEMENTED:
            return {
                "action": "dispatch_spec_reviewer",
                "task": current_task,
                "message": f"分发规范合规审查子代理"
            }
        elif current_task.status == TaskStatus.SPEC_REVIEWED:
            return {
                "action": "dispatch_code_reviewer",
                "task": current_task,
                "message": f"分发代码质量审查子代理"
            }
        elif current_task.status == TaskStatus.CODE_REVIEWED:
            return {
                "action": "mark_complete",
                "task": current_task,
                "message": f"标记任务 {current_task.id} 完成"
            }

        return {"action": "unknown", "message": "未知状态"}

    def generate_implementer_prompt(self, task: Task, plan_context: str) -> str:
        """生成实施子代理提示"""
        return f"""
# 实施任务: {task.name}

## 任务描述
{task.description}

## 计划上下文
{plan_context}

## 要求
1. 如有问题请先提问，获得明确后再开始
2. 遵循TDD: 先写测试，观察失败，写最少代码通过
3. 实现完成后自我审查
4. 提交并报告完成

## 输出
- 实现的代码
- 测试文件
- 自我审查结果
- 提交SHA
        """.strip()

    def generate_spec_reviewer_prompt(self, task: Task) -> str:
        """生成规范审查子代理提示"""
        return f"""
# 规范合规审查: {task.name}

## 任务
{task.description}

## 审查重点
1. 是否实现了所有要求？
2. 是否有超出范围的内容？
3. 是否符合计划中的验收标准？
4. 是否有遗漏的功能？

## 输出
- ✅ 符合规范 / ❌ 存在问题
- 具体问题列表（如有）
- 修复建议
        """.strip()

    def generate_code_reviewer_prompt(self, task: Task) -> str:
        """生成代码质量审查子代理提示"""
        return f"""
# 代码质量审查: {task.name}

## 审查重点
1. 代码质量（可读性、可维护性）
2. 测试覆盖率
3. 架构合理性
4. 是否有代码异味

## 输出格式
### 优点
-

### 问题（重要）
-

### 建议（次要）
-

### 评估
- [ ] 批准
- [ ] 需要修复
        """.strip()

    def get_red_flags(self) -> List[str]:
        """获取红旗（禁止行为）"""
        return [
            "永远不要跳过审查（规范符合性或代码质量）",
            "永远不要继续未修复的问题",
            "永远不要并行分发多个实施子代理（冲突）",
            "永远不要让子代理读取计划文件（提供完整文本代替）",
            "永远不要跳过场景设置上下文",
            "永远不要接受'差不多'的规范符合性",
            "永远不要跳过审查循环",
            "永远不要让实施者自我审查取代实际审查",
            "永远不要在规范符合性✅之前开始代码质量审查",
            "永远不要在任一审查有未解决问题时进入下一个任务"
        ]


def main():
    """入口函数"""
    return SubagentDrivenDevelopmentSkill()


if __name__ == "__main__":
    skill = main()
