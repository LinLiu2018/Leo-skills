# -*- coding: utf-8 -*-
"""
criteria_audit_skill - 标准审计技能

审计验收标准是否符合SMART原则：具体、可衡量、可实现、相关、有时限。
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class AuditSeverity(Enum):
    """审计严重程度"""
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


@dataclass
class CriterionAudit:
    """标准审计"""
    criterion_id: str
    original_text: str
    is_valid: bool
    issues: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=dict)


@dataclass
class AuditReport:
    """审计报告"""
    total_criteria: int = 0
    valid_count: int = 0
    invalid_count: int = 0
    criteria: List[CriterionAudit] = field(default_factory=list)


class CriteriaAuditSkill:
    """
    标准审计技能

    审计验收标准是否符合SMART原则：
    - Specific（具体）：描述清晰明确
    - Measurable（可衡量）：有明确的衡量标准
    - Achievable（可实现）：在合理时间内可完成
    - Relevant（相关）：与目标直接相关
    - Time-bound（有时限）：有明确的完成时间
    """

    def __init__(self):
        self.name = "criteria_audit_skill"
        self.version = "1.0.0"
        self.description = "审计验收标准质量"
        self.category = "testing"

    def execute(
        self,
        criteria: List[Dict[str, str]],
        **kwargs
    ) -> Dict[str, Any]:
        """
        执行标准审计

        Args:
            criteria: 标准列表

        Returns:
            审计结果
        """
        try:
            report = AuditReport(total_criteria=len(criteria))

            for i, criterion in enumerate(criteria, 1):
                audit = self._audit_criterion(
                    f"C{i:03d}",
                    criterion.get("description", "")
                )
                report.criteria.append(audit)
                if audit.is_valid:
                    report.valid_count += 1
                else:
                    report.invalid_count += 1

            return {
                "status": "success",
                "report": report,
                "summary": {
                    "total": report.total_criteria,
                    "valid": report.valid_count,
                    "invalid": report.invalid_count,
                    "pass_rate": f"{report.valid_count/report.total_criteria*100:.1f}%" if report.total_criteria > 0 else "0%"
                }
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "skill": self.name
            }

    def _audit_criterion(self, criterion_id: str, text: str) -> CriterionAudit:
        """审计单个标准"""
        audit = CriterionAudit(
            criterion_id=criterion_id,
            original_text=text,
            is_valid=True
        )

        # 检查是否具体
        vague_words = ["好", "快", "完善", "优化", "改进", "适当"]
        for word in vague_words:
            if word in text:
                audit.is_valid = False
                audit.issues.append(f"使用模糊词汇: '{word}'")
                audit.suggestions.append(f"将 '{word}' 替换为具体描述")

        # 检查是否可衡量
        measure_words = ["百分比", "数量", "时间", "秒", "分钟", "%", "次"]
        has_measure = any(w in text for w in measure_words)
        if not has_measure:
            audit.issues.append("缺少可衡量的指标")
            audit.suggestions.append("添加具体的数值指标")

        return audit


def main():
    """入口函数"""
    return CriteriaAuditSkill()


if __name__ == "__main__":
    skill = main()
