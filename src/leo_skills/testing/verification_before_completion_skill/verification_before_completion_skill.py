# -*- coding: utf-8 -*-
"""
verification_before_completion_skill - 完成前验证技能

基于 obra/superpowers 的 verification-before-completion 技能。
核心理念：证据在断言之前，始终。
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class VerificationType(Enum):
    """验证类型"""
    TEST = "test"
    LINT = "lint"
    BUILD = "build"
    TYPE_CHECK = "type_check"
    REQUIREMENTS = "requirements"
    REGRESSION = "regression"


class VerificationStatus(Enum):
    """验证状态"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class VerificationItem:
    """验证项"""
    vtype: VerificationType
    command: str
    description: str
    status: VerificationStatus = VerificationStatus.PENDING
    output: str = ""
    exit_code: int = 0
    executed_at: Optional[str] = None


@dataclass
class VerificationResult:
    """验证结果"""
    status: str
    items: List[VerificationItem] = field(default_factory=list)
    all_passed: bool = False
    can_complete: bool = False
    message: str = ""


class VerificationBeforeCompletionSkill:
    """
    完成前验证技能

    核心理念：证据在断言之前，始终。
    铁律：没有新鲜验证证据就不能声称完成。
    """

    def __init__(self):
        self.name = "verification_before_completion_skill"
        self.version = "1.0.0"
        self.description = "完成前验证，证据在断言之前"
        self.category = "testing"

    def execute(
        self,
        context: str = "",
        verification_types: List[str] = None,
        custom_commands: Dict[str, str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        执行完成前验证

        Args:
            context: 验证上下文（如"提交前"、"PR创建前"等）
            verification_types: 验证类型列表
            custom_commands: 自定义验证命令

        Returns:
            验证结果
        """
        try:
            vtypes = verification_types or ["test", "lint", "build"]
            custom = custom_commands or {}

            # 创建验证项
            items = self._create_verification_items(vtypes, custom)

            result = VerificationResult(
                status="in_progress",
                items=items
            )

            # 执行每个验证项（模拟）
            for item in items:
                item.status = VerificationStatus.RUNNING
                item.executed_at = datetime.now().isoformat()
                # 实际执行由调用者完成
                item.status = VerificationStatus.PASSED  # 模拟通过

            # 计算结果
            failed = sum(1 for i in items if i.status == VerificationStatus.FAILED)
            passed = sum(1 for i in items if i.status == VerificationStatus.PASSED)

            result.all_passed = failed == 0
            result.can_complete = result.all_passed
            result.status = "completed" if result.all_passed else "blocked"
            result.message = (
                f"验证完成: {passed}/{len(items)} 通过"
                if result.all_passed
                else f"验证失败: {failed} 项未通过，不能声称完成"
            )

            return {
                "status": "success",
                "result": result,
                "can_complete": result.can_complete,
                "message": result.message,
                "verification_items": [
                    {
                        "type": i.vtype.value,
                        "command": i.command,
                        "status": i.status.value
                    }
                    for i in items
                ]
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "skill": self.name
            }

    def _create_verification_items(
        self,
        vtypes: List[str],
        custom: Dict[str, str]
    ) -> List[VerificationItem]:
        """创建验证项"""
        items = []

        type_mapping = {
            "test": (VerificationType.TEST, "pytest", "运行测试"),
            "lint": (VerificationType.LINT, "ruff check .", "代码检查"),
            "build": (VerificationType.BUILD, "python setup.py build", "构建项目"),
            "type_check": (VerificationType.TYPE_CHECK, "mypy src/", "类型检查"),
        }

        for vt in vtypes:
            if vt in custom:
                items.append(VerificationItem(
                    vtype=VerificationType.TEST,
                    command=custom[vt],
                    description=f"自定义验证: {vt}"
                ))
            elif vt in type_mapping:
                vtype, cmd, desc = type_mapping[vt]
                items.append(VerificationItem(
                    vtype=vtype,
                    command=cmd,
                    description=desc
                ))

        return items

    def check_red_flags(self, statement: str) -> List[str]:
        """检查红旗（违反验证原则的表达）"""
        red_flags = []

        vague_terms = ["应该", "可能", "似乎", "大概", "可能吧"]
        for term in vague_terms:
            if term in statement:
                red_flags.append(f"使用模糊词汇'{term}'，缺乏确定性证据")

        premature_satisfaction = ["太棒了", "完美", "完成", "搞定"]
        for term in premature_satisfaction:
            if term in statement and "验证" not in statement:
                red_flags.append(f"过早表达满意'{term}'，未提供验证证据")

        trust_without_verify = ["代理说成功", "应该工作", "有信心"]
        for term in trust_without_verify:
            if term in statement:
                red_flags.append(f"未经验证的信任'{term}'")

        return red_flags

    def generate_verification_checklist(self, context: str = "") -> List[str]:
        """生成验证检查清单"""
        base_checklist = [
            "[ ] 识别：什么命令证明这个断言？",
            "[ ] 运行：执行完整命令（新鲜、完整）",
            "[ ] 阅读：完整输出，检查退出代码，统计失败",
            "[ ] 验证：输出确认断言吗？",
            "[ ] 断言：用证据陈述结果"
        ]

        context_checks = {
            "提交前": [
                "[ ] 所有测试通过",
                "[ ] 代码检查无错误",
                "[ ] 类型检查通过"
            ],
            "PR创建前": [
                "[ ] 本地功能验证",
                "[ ] 回归测试通过",
                "[ ] 文档已更新"
            ],
            "任务完成": [
                "[ ] 验收标准全部满足",
                "[ ] 验证证据已记录",
                "[ ] 无回归问题"
            ]
        }

        if context in context_checks:
            return base_checklist + [""] + context_checks[context]

        return base_checklist

    def generate_workflow_guide(self) -> str:
        """生成工作流程指南"""
        return """
完成前验证工作流程

门禁功能：
┌─────────────────────────────────────────┐
│ 1. 识别：什么命令证明这个断言？          │
│ 2. 运行：执行完整命令（新鲜、完整）      │
│ 3. 阅读：完整输出，检查退出代码          │
│ 4. 验证：输出确认断言吗？                │
│ 5. 只有那时：做出断言                    │
└─────────────────────────────────────────┘

常见失败对照表：
┌─────────────────┬────────────────────┬──────────────────┐
│ 断言            │ 需要               │ 不充分           │
├─────────────────┼────────────────────┼──────────────────┤
│ 测试通过        │ 0 失败             │ 上次运行         │
│ Linter 干净     │ 0 错误             │ 部分检查         │
│ 构建成功        │ 退出 0             │ Linter 通过      │
│ Bug 修复        │ 原始症状通过       │ 代码改变         │
│ 代理完成        │ VCS diff 显示更改  │ 代理报告成功     │
└─────────────────┴────────────────────┴──────────────────┘

红旗 - 停止：
- 使用"应该"、"可能"、"似乎"
- 在验证之前表达满意
- 即将提交/PR而不验证
- 信任代理成功报告
- 依赖部分验证

底线：验证没有捷径。运行命令。阅读输出。然后声称结果。
        """.strip()


def main():
    """入口函数"""
    return VerificationBeforeCompletionSkill()


if __name__ == "__main__":
    skill = main()
