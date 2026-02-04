# -*- coding: utf-8 -*-
"""
systematic_debugging_skill - 系统化调试技能

基于 obra/superpowers 的 systematic-debugging 技能。
四阶段根因分析方法。
核心理念：永远先找到根因再尝试修复。
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class DebugPhase(Enum):
    """调试阶段"""
    ROOT_CAUSE = "root_cause"
    PATTERN = "pattern"
    HYPOTHESIS = "hypothesis"
    IMPLEMENTATION = "implementation"


class HypothesisStatus(Enum):
    """假设状态"""
    UNTESTED = "untested"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"


@dataclass
class DebugFinding:
    """调试发现"""
    phase: DebugPhase
    description: str
    evidence: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class Hypothesis:
    """假设"""
    id: str
    description: str
    test_method: str
    status: HypothesisStatus = HypothesisStatus.UNTESTED
    result: str = ""


@dataclass
class DebuggingSession:
    """调试会话"""
    bug_description: str
    error_message: str
    phase: DebugPhase
    findings: List[DebugFinding] = field(default_factory=list)
    hypotheses: List[Hypothesis] = field(default_factory=list)
    fix_attempts: int = 0
    root_cause: str = ""
    solution: str = ""
    status: str = "in_progress"


class SystematicDebuggingSkill:
    """
    系统化调试技能

    核心理念：永远先找到根因再尝试修复。修复症状等于失败。
    违反流程的字面要求就是违反调试的精神。
    """

    def __init__(self):
        self.name = "systematic_debugging_skill"
        self.version = "1.0.0"
        self.description = "系统化四阶段根因分析方法"
        self.category = "debugging"

    def execute(
        self,
        bug_description: str,
        error_message: str = "",
        stack_trace: str = "",
        recent_changes: List[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        执行系统化调试

        Args:
            bug_description: Bug描述
            error_message: 错误消息
            stack_trace: 堆栈跟踪
            recent_changes: 最近的变更

        Returns:
            调试会话结果
        """
        try:
            session = DebuggingSession(
                bug_description=bug_description,
                error_message=error_message,
                phase=DebugPhase.ROOT_CAUSE
            )

            # 阶段1: 根因调查
            self._investigate_root_cause(session, error_message, stack_trace, recent_changes or [])

            # 阶段2: 模式分析
            session.phase = DebugPhase.PATTERN
            self._analyze_patterns(session)

            # 阶段3: 假设与测试
            session.phase = DebugPhase.HYPOTHESIS
            self._test_hypotheses(session)

            # 阶段4: 实施修复
            session.phase = DebugPhase.IMPLEMENTATION
            self._implement_fix(session)

            return {
                "status": "success",
                "session": session,
                "root_cause": session.root_cause,
                "solution": session.solution,
                "phases_completed": [p.value for p in DebugPhase]
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "skill": self.name
            }

    def _investigate_root_cause(
        self,
        session: DebuggingSession,
        error_message: str,
        stack_trace: str,
        recent_changes: List[str]
    ):
        """阶段1: 根因调查"""
        # 记录错误信息
        if error_message:
            session.findings.append(DebugFinding(
                phase=DebugPhase.ROOT_CAUSE,
                description="错误消息分析",
                evidence=error_message
            ))

        # 记录堆栈跟踪
        if stack_trace:
            session.findings.append(DebugFinding(
                phase=DebugPhase.ROOT_CAUSE,
                description="堆栈跟踪分析",
                evidence=stack_trace[:500] + "..." if len(stack_trace) > 500 else stack_trace
            ))

        # 记录最近变更
        if recent_changes:
            session.findings.append(DebugFinding(
                phase=DebugPhase.ROOT_CAUSE,
                description="最近变更",
                evidence="\n".join(recent_changes[:5])
            ))

    def _analyze_patterns(self, session: DebuggingSession):
        """阶段2: 模式分析"""
        session.findings.append(DebugFinding(
            phase=DebugPhase.PATTERN,
            description="查找工作示例",
            evidence="搜索代码库中类似工作的代码模式"
        ))

        session.findings.append(DebugFinding(
            phase=DebugPhase.PATTERN,
            description="识别差异",
            evidence="比较工作和坏掉的代码之间的差异"
        ))

    def _test_hypotheses(self, session: DebuggingSession):
        """阶段3: 假设与测试"""
        # 创建假设
        hypotheses = [
            Hypothesis(
                id="H1",
                description="配置错误导致的问题",
                test_method="检查配置文件和环境变量"
            ),
            Hypothesis(
                id="H2",
                description="最近的代码变更引入的bug",
                test_method="回滚最近变更并测试"
            ),
            Hypothesis(
                id="H3",
                description="依赖版本不兼容",
                test_method="检查依赖版本和兼容性"
            )
        ]

        session.hypotheses = hypotheses

        # 如果没有找到根因，记录
        if not session.root_cause:
            session.root_cause = "需要进一步调查"

    def _implement_fix(self, session: DebuggingSession):
        """阶段4: 实施修复"""
        # 检查修复尝试次数
        if session.fix_attempts >= 3:
            session.status = "needs_architecture_review"
            session.solution = "多次修复失败，建议质疑架构"
        else:
            session.solution = f"基于根因 '{session.root_cause}' 实施修复"
            session.status = "ready_to_implement"

    def check_red_flags(self, action: str) -> bool:
        """检查红旗（违反调试原则的行为）"""
        red_flags = [
            "快速修复",
            "试试改",
            "跳过测试",
            "可能是",
            "就这一次",
            "再试一次修复"
        ]
        return any(flag in action for flag in red_flags)

    def generate_debug_report(self, session: DebuggingSession) -> str:
        """生成调试报告"""
        lines = [
            "系统化调试报告",
            "================",
            f"Bug描述: {session.bug_description}",
            f"当前阶段: {session.phase.value}",
            f"修复尝试: {session.fix_attempts}",
            "",
            "发现:",
        ]

        for finding in session.findings:
            lines.append(f"- [{finding.phase.value}] {finding.description}")

        lines.extend([
            "",
            "假设:",
        ])

        for h in session.hypotheses:
            lines.append(f"- [{h.id}] {h.description} ({h.status.value})")

        lines.extend([
            "",
            f"根因: {session.root_cause}",
            f"解决方案: {session.solution}",
        ])

        return "\n".join(lines)


def main():
    """入口函数"""
    return SystematicDebuggingSkill()


if __name__ == "__main__":
    skill = main()
