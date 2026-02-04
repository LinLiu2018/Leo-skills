# -*- coding: utf-8 -*-
"""
phase_prep_skill - 阶段准备技能

在执行阶段前检查先决条件，验证依赖是否满足且上下文已加载。
基于 obra/superpowers 的 phase-prep 技能实现。
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class CheckStatus(Enum):
    """检查状态"""
    PASS = "pass"
    FAIL = "fail"
    BLOCKED = "blocked"
    PENDING = "pending"


@dataclass
class CheckItem:
    """检查项"""
    name: str
    status: CheckStatus
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PhasePrepResult:
    """阶段准备结果"""
    phase_number: int
    ready: bool
    checks: List[CheckItem]
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    auto_advance: bool = False


class PhasePrepSkill:
    """
    阶段准备技能

    功能：
    - 检查执行计划文档是否存在
    - 验证前置阶段是否完成
    - 检查验证配置
    - 检查 Git 状态
    - 检查工具可用性
    - 生成详细准备报告

    使用场景：
    - 在执行 /phase-start 之前使用
    - 验证阶段准备情况
    """

    def __init__(self, base_path: str = "."):
        self.name = "phase_prep_skill"
        self.version = "1.0.0"
        self.description = "阶段准备技能 - 执行前检查先决条件"
        self.base_path = Path(base_path)

    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        执行技能主入口

        Args:
            phase_number: 阶段编号
            work_dir: 工作目录
            auto_advance: 是否允许自动推进

        Returns:
            Dict 包含准备检查结果
        """
        phase_number = kwargs.get("phase_number", 1)
        work_dir = kwargs.get("work_dir", self.base_path)
        auto_advance = kwargs.get("auto_advance", True)

        try:
            result = self.check_phase_ready(
                phase_number=phase_number,
                work_dir=work_dir,
                auto_advance=auto_advance
            )

            return {
                "status": "success" if result.ready else "blocked",
                "skill": self.name,
                "phase": phase_number,
                "ready": result.ready,
                "auto_advance": result.auto_advance,
                "checks": [
                    {
                        "name": c.name,
                        "status": c.status.value,
                        "message": c.message,
                        "details": c.details
                    }
                    for c in result.checks
                ],
                "issues": result.issues,
                "recommendations": result.recommendations
            }

        except Exception as e:
            return {
                "status": "error",
                "skill": self.name,
                "phase": phase_number,
                "error": str(e)
            }

    def check_phase_ready(
        self,
        phase_number: int,
        work_dir: Optional[Path] = None,
        auto_advance: bool = True
    ) -> PhasePrepResult:
        """
        检查阶段是否准备就绪

        Args:
            phase_number: 阶段编号
            work_dir: 工作目录
            auto_advance: 是否允许自动推进

        Returns:
            PhasePrepResult 检查结果
        """
        work_dir = Path(work_dir) if work_dir else self.base_path
        checks = []
        issues = []
        recommendations = []

        # 1. 检查执行计划文档
        check = self._check_execution_plan(work_dir)
        checks.append(check)
        if check.status != CheckStatus.PASS:
            issues.append(f"执行计划检查: {check.message}")

        # 2. 检查 AGENTS.md
        check = self._check_agents_md(work_dir)
        checks.append(check)
        if check.status != CheckStatus.PASS:
            issues.append(f"AGENTS.md 检查: {check.message}")

        # 3. 验证前置阶段
        check = self._check_prior_phases(work_dir, phase_number)
        checks.append(check)
        if check.status != CheckStatus.PASS:
            issues.append(f"前置阶段检查: {check.message}")
            recommendations.append("完成前置阶段后再继续")

        # 4. 检查验证配置
        check = self._check_verification_config(work_dir)
        checks.append(check)
        if check.status == CheckStatus.FAIL:
            recommendations.append("运行 /configure-verification 配置验证命令")

        # 5. 检查 Git 状态
        check = self._check_git_status(work_dir)
        checks.append(check)
        checks.append(check)

        # 6. 检查阶段配置
        check = self._check_phase_config(work_dir, phase_number)
        checks.append(check)
        if check.status != CheckStatus.PASS:
            issues.append(f"阶段配置检查: {check.message}")

        # 确定是否就绪
        ready = all(c.status == CheckStatus.PASS for c in checks)

        # 确定是否允许自动推进
        can_auto_advance = (
            ready and
            auto_advance and
            not any(c.status == CheckStatus.BLOCKED for c in checks)
        )

        return PhasePrepResult(
            phase_number=phase_number,
            ready=ready,
            checks=checks,
            issues=issues,
            recommendations=recommendations,
            auto_advance=can_auto_advance
        )

    def _check_execution_plan(self, work_dir: Path) -> CheckItem:
        """检查执行计划文档"""
        plan_path = work_dir / "EXECUTION_PLAN.md"

        if not plan_path.exists():
            return CheckItem(
                name="执行计划文档",
                status=CheckStatus.FAIL,
                message="EXECUTION_PLAN.md 不存在",
                details={"path": str(plan_path)}
            )

        try:
            content = plan_path.read_text(encoding="utf-8")
            # 检查是否有阶段定义
            phase_pattern = r"##\s*Phase\s+\d+"
            phases = re.findall(phase_pattern, content)

            return CheckItem(
                name="执行计划文档",
                status=CheckStatus.PASS,
                message=f"找到 {len(phases)} 个阶段定义",
                details={
                    "path": str(plan_path),
                    "phases_count": len(phases)
                }
            )
        except Exception as e:
            return CheckItem(
                name="执行计划文档",
                status=CheckStatus.FAIL,
                message=f"无法读取执行计划: {e}",
                details={"error": str(e)}
            )

    def _check_agents_md(self, work_dir: Path) -> CheckItem:
        """检查 AGENTS.md"""
        agents_path = work_dir / "AGENTS.md"

        if not agents_path.exists():
            return CheckItem(
                name="AGENTS.md",
                status=CheckStatus.WARNING,
                message="AGENTS.md 不存在（可选）",
                details={"path": str(agents_path)}
            )

        return CheckItem(
            name="AGENTS.md",
            status=CheckStatus.PASS,
            message="AGENTS.md 存在",
            details={"path": str(agents_path)}
        )

    def _check_prior_phases(self, work_dir: Path, phase_number: int) -> CheckItem:
        """检查前置阶段是否完成"""
        if phase_number <= 1:
            return CheckItem(
                name="前置阶段",
                status=CheckStatus.PASS,
                message="阶段 1 无需前置检查",
                details={"phase": phase_number}
            )

        plan_path = work_dir / "EXECUTION_PLAN.md"
        if not plan_path.exists():
            return CheckItem(
                name="前置阶段",
                status=CheckStatus.BLOCKED,
                message="无法验证前置阶段：执行计划不存在",
                details={}
            )

        try:
            content = plan_path.read_text(encoding="utf-8")

            # 检查前置阶段的任务完成情况
            prior_incomplete = []
            for prior in range(1, phase_number):
                phase_pattern = rf"##\s*Phase\s+{prior}.*?(?=##\s*Phase|\Z)"
                phase_match = re.search(phase_pattern, content, re.DOTALL)

                if phase_match:
                    phase_content = phase_match.group(0)
                    # 检查未完成的任务
                    unchecked = len(re.findall(r"-\s*\[\s*\]", phase_content))
                    if unchecked > 0:
                        prior_incomplete.append(f"Phase {prior} ({unchecked} 未完成)")

            if prior_incomplete:
                return CheckItem(
                    name="前置阶段",
                    status=CheckStatus.BLOCKED,
                    message=f"前置阶段未完成: {', '.join(prior_incomplete)}",
                    details={"incomplete_phases": prior_incomplete}
                )

            return CheckItem(
                name="前置阶段",
                status=CheckStatus.PASS,
                message="所有前置阶段已完成",
                details={"checked_phases": list(range(1, phase_number))}
            )

        except Exception as e:
            return CheckItem(
                name="前置阶段",
                status=CheckStatus.WARNING,
                message=f"无法验证前置阶段: {e}",
                details={"error": str(e)}
            )

    def _check_verification_config(self, work_dir: Path) -> CheckItem:
        """检查验证配置"""
        config_path = work_dir / ".claude" / "verification-config.json"

        if not config_path.exists():
            return CheckItem(
                name="验证配置",
                status=CheckStatus.FAIL,
                message="verification-config.json 不存在",
                details={"path": str(config_path)}
            )

        try:
            config = json.loads(config_path.read_text(encoding="utf-8"))
            commands = config.get("commands", {})

            missing = []
            for cmd in ["test", "lint", "typecheck", "build"]:
                if not commands.get(cmd):
                    missing.append(cmd)

            if missing:
                return CheckItem(
                    name="验证配置",
                    status=CheckStatus.WARNING,
                    message=f"缺少命令配置: {', '.join(missing)}",
                    details={"missing": missing, "configured": list(commands.keys())}
                )

            return CheckItem(
                name="验证配置",
                status=CheckStatus.PASS,
                message="验证配置完整",
                details={"commands": list(commands.keys())}
            )

        except Exception as e:
            return CheckItem(
                name="验证配置",
                status=CheckStatus.FAIL,
                message=f"验证配置读取失败: {e}",
                details={"error": str(e)}
            )

    def _check_git_status(self, work_dir: Path) -> CheckItem:
        """检查 Git 状态"""
        git_dir = work_dir / ".git"

        if not git_dir.exists():
            return CheckItem(
                name="Git 状态",
                status=CheckStatus.WARNING,
                message="非 Git 仓库（可选）",
                details={}
            )

        # 尝试获取 Git 状态
        try:
            import subprocess
            result = subprocess.run(
                ["git", "status", "--short"],
                cwd=work_dir,
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                changes = result.stdout.strip()
                if changes:
                    return CheckItem(
                        name="Git 状态",
                        status=CheckStatus.WARNING,
                        message=f"工作目录有未提交更改",
                        details={
                            "changes": len(changes.split("\n")),
                            "dirty": True
                        }
                    )

                return CheckItem(
                    name="Git 状态",
                    status=CheckStatus.PASS,
                    message="工作目录干净",
                    details={"dirty": False}
                )

        except Exception:
            pass

        return CheckItem(
            name="Git 状态",
            status=CheckStatus.WARNING,
            message="无法检查 Git 状态",
            details={}
        )

    def _check_phase_config(self, work_dir: Path, phase_number: int) -> CheckItem:
        """检查阶段配置"""
        plan_path = work_dir / "EXECUTION_PLAN.md"

        if not plan_path.exists():
            return CheckItem(
                name="阶段配置",
                status=CheckStatus.FAIL,
                message="执行计划不存在",
                details={}
            )

        try:
            content = plan_path.read_text(encoding="utf-8")

            # 查找指定阶段
            phase_pattern = rf"##\s*Phase\s+{phase_number}\b"
            if not re.search(phase_pattern, content):
                return CheckItem(
                    name="阶段配置",
                    status=CheckStatus.FAIL,
                    message=f"阶段 {phase_number} 不存在于执行计划中",
                    details={"phase": phase_number}
                )

            return CheckItem(
                name="阶段配置",
                status=CheckStatus.PASS,
                message=f"阶段 {phase_number} 配置存在",
                details={"phase": phase_number}
            )

        except Exception as e:
            return CheckItem(
                name="阶段配置",
                status=CheckStatus.FAIL,
                message=f"无法读取阶段配置: {e}",
                details={"error": str(e)}
            )

    def generate_report(self, result: PhasePrepResult) -> str:
        """
        生成准备检查报告

        Args:
            result: 准备检查结果

        Returns:
            格式化报告字符串
        """
        lines = [
            f"阶段 {result.phase_number} 准备检查报告",
            "=" * 50,
            "",
            f"状态: {'✅ 就绪' if result.ready else '❌ 未就绪'}",
            f"自动推进: {'✅ 允许' if result.auto_advance else '❌ 阻止'}",
            "",
            "检查项:",
            "-" * 50
        ]

        for check in result.checks:
            status_icon = {
                CheckStatus.PASS: "✅",
                CheckStatus.FAIL: "❌",
                CheckStatus.BLOCKED: "🚫",
                CheckStatus.PENDING: "⏳",
                CheckStatus.WARNING: "⚠️"
            }.get(check.status, "❓")

            lines.append(f"{status_icon} {check.name}: {check.message}")

        if result.issues:
            lines.extend([
                "",
                "待解决问题:",
                "-" * 50
            ])
            for issue in result.issues:
                lines.append(f"  - {issue}")

        if result.recommendations:
            lines.extend([
                "",
                "建议:",
                "-" * 50
            ])
            for rec in result.recommendations:
                lines.append(f"  - {rec}")

        return "\n".join(lines)

    def get_capabilities(self) -> Dict[str, Any]:
        """获取技能能力信息"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "checks": [
                "execution_plan",
                "agents_md",
                "prior_phases",
                "verification_config",
                "git_status",
                "phase_config"
            ],
            "features": [
                "phase_readiness_check",
                "dependency_validation",
                "auto_advance_detection",
                "report_generation"
            ]
        }


# 向后兼容
PhasePrep_Skill = PhasePrepSkill
PHASE_Skill = PhasePrepSkill


def main():
    """入口函数 - 演示用法"""
    print("=" * 60)
    print("Phase Prep Skill - 演示")
    print("=" * 60)

    skill = PhasePrepSkill()

    # 演示: 检查当前目录
    print("\n1. 检查当前目录准备状态")
    print("-" * 40)
    result = skill.check_phase_ready(phase_number=1)
    print(skill.generate_report(result))

    print("\n" + "=" * 60)
    print("演示完成！")
    print("=" * 60)

    return skill


if __name__ == "__main__":
    main()
