# -*- coding: utf-8 -*-
"""
audit_skills_skill - 技能审计技能

审计技能是否符合最佳实践，包括长度、检查清单、验证步骤和渐进式披露。
"""
from leo_skills.core.base_executor import BaseExecutor

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class Severity(Enum):
    """严重程度"""
    CRITICAL = "critical"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Violation:
    """违规项"""
    criterion_id: str
    description: str
    severity: Severity
    evidence: str
    suggested_fix: str


@dataclass
class SkillAudit:
    """技能审计"""
    skill_name: str
    line_count: int
    violations: List[Violation] = field(default_factory=list)


@dataclass
class AuditResult:
    """审计结果"""
    status: str
    skills_audited: int = 0
    total_violations: int = 0
    critical_count: int = 0
    medium_count: int = 0
    low_count: int = 0
    message: str = ""


class AuditSkillsSkill(BaseExecutor):
    """
    技能审计技能

    审计技能是否符合最佳实践：
    - 长度适中（不要太长）
    - 有检查清单
    - 有验证步骤
    - 渐进式披露
    """

    def __init__(self):
        self.name = "audit_skills_skill"
        self.version = "1.0.0"
        self.description = "审计技能最佳实践合规性"
        self.category = "tools"

    def execute(
        self,
        skills_dir: str = "src/leo_skills",
        severity_threshold: str = "low",
        **kwargs
    ) -> Dict[str, Any]:
        """
        执行技能审计

        Args:
            skills_dir: 技能目录
            severity_threshold: 严重程度阈值

        Returns:
            审计结果
        """
        try:
            # 发现技能
            skills = self._discover_skills(skills_dir)

            # 审计每个技能
            audits = []
            for skill_path in skills:
                audit = self._audit_skill(skill_path)
                audits.append(audit)

            # 计算结果
            total_violations = sum(len(a.violations) for a in audits)
            critical = sum(1 for a in audits for v in a.violations if v.severity == Severity.CRITICAL)
            medium = sum(1 for a in audits for v in a.violations if v.severity == Severity.MEDIUM)
            low = sum(1 for a in audits for v in a.violations if v.severity == Severity.LOW)

            result = AuditResult(
                status="completed",
                skills_audited=len(audits),
                total_violations=total_violations,
                critical_count=critical,
                medium_count=medium,
                low_count=low,
                message=f"审计完成: {len(audits)} 个技能, {total_violations} 个问题"
            )

            return {
                "status": "success",
                "result": result,
                "audits": audits,
                "report": self._generate_report(audits)
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "skill": self.name
            }

    def _discover_skills(self, skills_dir: str) -> List[Path]:
        """发现技能"""
        root = Path(skills_dir)
        skills = []
        for skill_md in root.rglob("SKILL.md"):
            skills.append(skill_md)
        return skills

    def _audit_skill(self, skill_path: Path) -> SkillAudit:
        """审计单个技能"""
        content = skill_path.read_text(encoding='utf-8')
        lines = content.split('\n')

        audit = SkillAudit(
            skill_name=skill_path.parent.name,
            line_count=len(lines)
        )

        # 检查长度
        if len(lines) > 300:
            audit.violations.append(Violation(
                criterion_id="C1",
                description="技能文档过长",
                severity=Severity.MEDIUM,
                evidence=f"{len(lines)} 行",
                suggested_fix="考虑拆分为多个技能或使用渐进式披露"
            ))

        # 检查检查清单
        if "- [ ]" not in content and "checklist" not in content.lower():
            audit.violations.append(Violation(
                criterion_id="C2",
                description="缺少检查清单",
                severity=Severity.MEDIUM,
                evidence="未找到 '- [ ]' 或 'checklist'",
                suggested_fix="添加检查清单帮助用户跟踪进度"
            ))

        # 检查验证步骤
        if "Verify:" not in content and "验证" not in content:
            audit.violations.append(Violation(
                criterion_id="C3",
                description="缺少验证步骤",
                severity=Severity.CRITICAL,
                evidence="未找到 'Verify:' 或 '验证'",
                suggested_fix="添加明确的验证步骤"
            ))

        return audit

    def _generate_report(self, audits: List[SkillAudit]) -> str:
        """生成审计报告"""
        lines = [
            "# 技能审计报告",
            f"生成时间: {datetime.now().isoformat()}",
            f"审计技能数: {len(audits)}",
            "",
            "## 摘要",
            "",
        ]

        for audit in audits:
            lines.append(f"### {audit.skill_name}")
            lines.append(f"行数: {audit.line_count}")
            if audit.violations:
                lines.append("违规项:")
                for v in audit.violations:
                    lines.append(f"- [{v.severity.value}] {v.description}")
            else:
                lines.append("✅ 无违规项")
            lines.append("")

        return "\n".join(lines)


def main():
    """入口函数"""
    return AuditSkillsSkill()


if __name__ == "__main__":
    skill = main()
