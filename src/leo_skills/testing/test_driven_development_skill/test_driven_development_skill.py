# -*- coding: utf-8 -*-
"""
test_driven_development_skill - 测试驱动开发技能

基于 obra/superpowers 的 test-driven-development 技能。
核心理念：先写测试，观察失败，编写最少代码通过。
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class TDDPhase(Enum):
    """TDD阶段"""
    RED = "red"           # 编写失败测试
    GREEN = "green"       # 编写最少代码通过
    REFACTOR = "refactor" # 重构


class TestStatus(Enum):
    """测试状态"""
    FAILING = "failing"
    PASSING = "passing"
    ERROR = "error"
    NOT_RUN = "not_run"


@dataclass
class TestCase:
    """测试用例"""
    name: str
    code: str
    status: TestStatus = TestStatus.NOT_RUN
    error_message: str = ""


@dataclass
class TDDCycle:
    """TDD循环"""
    phase: TDDPhase
    test: Optional[TestCase] = None
    implementation: str = ""
    refactor_changes: List[str] = field(default_factory=list)
    started_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None


@dataclass
class TDDResult:
    """TDD结果"""
    status: str
    cycles: List[TDDCycle] = field(default_factory=list)
    current_phase: TDDPhase = TDDPhase.RED
    all_tests_passing: bool = False
    message: str = ""


class TestDrivenDevelopmentSkill:
    """
    测试驱动开发技能

    核心理念：如果没看到测试失败，就不知道是否测试了正确的东西。
    铁律：没有失败的测试就不能写生产代码。
    """

    def __init__(self):
        self.name = "test_driven_development_skill"
        self.version = "1.0.0"
        self.description = "测试驱动开发实践，红-绿-重构循环"
        self.category = "testing"

    def execute(
        self,
        feature_name: str,
        test_cases: List[Dict[str, str]],
        current_code: str = "",
        phase: str = "red",
        **kwargs
    ) -> Dict[str, Any]:
        """
        执行TDD流程

        Args:
            feature_name: 功能名称
            test_cases: 测试用例列表
            current_code: 当前代码
            phase: 当前阶段 (red/green/refactor)

        Returns:
            TDD执行结果
        """
        try:
            current_phase = TDDPhase(phase.lower())
            result = TDDResult(
                status="in_progress",
                current_phase=current_phase
            )

            # 解析测试用例
            tests = [TestCase(name=t["name"], code=t["code"]) for t in test_cases]

            if current_phase == TDDPhase.RED:
                # RED阶段：编写失败测试
                cycle = self._execute_red_phase(tests[0] if tests else None)
                result.cycles.append(cycle)
                result.current_phase = TDDPhase.GREEN
                result.message = "测试已编写，观察它失败，然后进入GREEN阶段"

            elif current_phase == TDDPhase.GREEN:
                # GREEN阶段：编写最少代码
                cycle = self._execute_green_phase(tests[0] if tests else None, current_code)
                result.cycles.append(cycle)
                result.current_phase = TDDPhase.REFACTOR
                result.message = "最少实现已完成，验证测试通过，准备重构"

            elif current_phase == TDDPhase.REFACTOR:
                # REFACTOR阶段：重构
                cycle = self._execute_refactor_phase(current_code)
                result.cycles.append(cycle)
                result.current_phase = TDDPhase.RED
                result.message = "重构完成，保持测试绿色，准备下一个功能"

            result.status = "completed"
            return {
                "status": "success",
                "result": result,
                "next_phase": result.current_phase.value,
                "message": result.message,
                "checklist": self._generate_checklist(result.current_phase)
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "skill": self.name
            }

    def _execute_red_phase(self, test: Optional[TestCase]) -> TDDCycle:
        """执行RED阶段"""
        cycle = TDDCycle(phase=TDDPhase.RED, test=test)

        if test:
            test.status = TestStatus.FAILING
            cycle.completed_at = datetime.now().isoformat()

        return cycle

    def _execute_green_phase(self, test: Optional[TestCase], code: str) -> TDDCycle:
        """执行GREEN阶段"""
        cycle = TDDCycle(
            phase=TDDPhase.GREEN,
            test=test,
            implementation=code
        )

        if test:
            test.status = TestStatus.PASSING

        cycle.completed_at = datetime.now().isoformat()
        return cycle

    def _execute_refactor_phase(self, code: str) -> TDDCycle:
        """执行REFACTOR阶段"""
        cycle = TDDCycle(
            phase=TDDPhase.REFACTOR,
            implementation=code,
            refactor_changes=["移除重复", "改进命名", "提取辅助函数"]
        )
        cycle.completed_at = datetime.now().isoformat()
        return cycle

    def _generate_checklist(self, phase: TDDPhase) -> List[str]:
        """生成阶段检查清单"""
        if phase == TDDPhase.RED:
            return [
                "[ ] 编写清晰的测试名称",
                "[ ] 测试一个行为",
                "[ ] 使用真实代码（非模拟）",
                "[ ] 运行测试验证它失败",
                "[ ] 确认失败消息符合预期"
            ]
        elif phase == TDDPhase.GREEN:
                return [
                "[ ] 编写最少代码通过测试",
                "[ ] 不要添加额外功能",
                "[ ] 运行测试验证通过",
                "[ ] 其他测试仍然通过",
                "[ ] 输出干净（无错误警告）"
            ]
        else:  # REFACTOR
            return [
                "[ ] 移除重复代码",
                "[ ] 改进变量/函数命名",
                "[ ] 提取辅助函数",
                "[ ] 保持测试绿色",
                "[ ] 不添加新行为"
            ]

    def validate_test_quality(self, test: TestCase) -> Dict[str, Any]:
        """验证测试质量"""
        issues = []

        # 检查测试名称
        if len(test.name) < 10:
            issues.append("测试名称太短，应描述行为")

        if "test" in test.name.lower() and test.name.lower().startswith("test"):
            issues.append("测试名称不应以'test'开头，应描述行为")

        # 检查是否有多个行为
        if " and " in test.name.lower() or "和" in test.name:
            issues.append("测试名称包含'和'，应只测试一个行为")

        # 检查是否有意义断言
        if "assert" not in test.code.lower():
            issues.append("测试缺少断言")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "quality_score": max(0, 100 - len(issues) * 25)
        }

    def generate_tdd_workflow(self) -> str:
        """生成TDD工作流程说明"""
        return """
TDD 工作流程：红-绿-重构

┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   RED       │  →  │   GREEN     │  →  │  REFACTOR   │
│ 写失败测试   │     │ 最少代码     │     │   清理      │
└─────────────┘     └─────────────┘     └─────────────┘
       ↓                   ↓                   ↓
   验证失败             验证通过             保持绿色

铁律：
1. 没有失败的测试就不能写生产代码
2. 删除预先编写的代码，用TDD重新开始
3. 测试通过不能证明它测试了正确的东西

常见借口与现实：
- "太简单不用测试" → 简单代码也会坏
- "我之后测试" → 之后测试立即通过不能证明任何事
- "保留作为参考" → 你会适应它，删除意味着删除
- "删除X小时是浪费" → 沉没成本谬论
        """.strip()


def main():
    """入口函数"""
    return TestDrivenDevelopmentSkill()


if __name__ == "__main__":
    skill = main()
