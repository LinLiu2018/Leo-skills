# -*- coding: utf-8 -*-
"""
requesting_code_review_skill - 请求代码审查技能

基于 obra/superpowers 的 requesting-code-review 技能。
核心理念：早审查，常审查。
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class ReviewType(Enum):
    """审查类型"""
    IMPLEMENTATION = "implementation"
    SPEC_COMPLIANCE = "spec_compliance"
    CODE_QUALITY = "code_quality"
    FINAL = "final"


class ReviewPriority(Enum):
    """审查优先级"""
    CRITICAL = "critical"
    IMPORTANT = "important"
    MINOR = "minor"


@dataclass
class ReviewRequest:
    """审查请求"""
    review_type: ReviewType
    base_sha: str
    head_sha: str
    description: str
    what_was_implemented: str
    plan_or_requirements: str
    priority: ReviewPriority = ReviewPriority.IMPORTANT
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ReviewFinding:
    """审查发现"""
    category: str  # "strength", "important", "minor"
    description: str
    location: Optional[str] = None
    suggestion: str = ""


@dataclass
class ReviewResult:
    """审查结果"""
    status: str
    findings: List[ReviewFinding] = field(default_factory=list)
    approved: bool = False
    summary: str = ""


class RequestingCodeReviewSkill:
    """
    请求代码审查技能

    核心理念：早审查，常审查。
    在子代理驱动开发中每个任务后、主要功能完成后、合并前请求审查。
    """

    def __init__(self):
        self.name = "requesting_code_review_skill"
        self.version = "1.0.0"
        self.description = "分发代码审查子代理以捕获问题"
        self.category = "collaboration"

    def execute(
        self,
        what_was_implemented: str,
        plan_or_requirements: str,
        base_sha: str,
        head_sha: str,
        review_type: str = "implementation",
        **kwargs
    ) -> Dict[str, Any]:
        """
        执行请求代码审查

        Args:
            what_was_implemented: 刚刚构建了什么
            plan_or_requirements: 它应该做什么
            base_sha: 起始提交
            head_sha: 结束提交
            review_type: 审查类型

        Returns:
            审查请求结果
        """
        try:
            rtype = ReviewType(review_type)
            priority = ReviewPriority.IMPORTANT

            request = ReviewRequest(
                review_type=rtype,
                base_sha=base_sha,
                head_sha=head_sha,
                description=f"审查: {what_was_implemented}",
                what_was_implemented=what_was_implemented,
                plan_or_requirements=plan_or_requirements,
                priority=priority
            )

            # 生成审查模板
            review_template = self._generate_review_template(request)

            return {
                "status": "success",
                "request": request,
                "template": review_template,
                "instructions": [
                    "1. 使用提供的模板创建代码审查子代理",
                    "2. 子代理将审查代码变更",
                    "3. 根据反馈立即修复关键问题",
                    "4. 继续之前修复重要问题",
                    "5. 记录次要问题以供以后处理"
                ]
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "skill": self.name
            }

    def _generate_review_template(self, request: ReviewRequest) -> str:
        """生成审查模板"""
        return f"""
# 代码审查请求

## 实现内容
{request.what_was_implemented}

## 计划/需求
{request.plan_or_requirements}

## 提交范围
- Base: {request.base_sha}
- Head: {request.head_sha}

## 审查清单

### 优点（什么做得好）
- [ ]

### 重要问题（继续前修复）
- [ ]

### 次要问题（记录供以后）
- [ ]

### 建议
- [ ]

## 评估
- [ ] 准备好继续
- [ ] 需要修复后重新审查

---
请提供结构化的审查反馈。
        """.strip()

    def process_review_feedback(self, feedback: str) -> ReviewResult:
        """处理审查反馈"""
        findings = []

        # 简单解析反馈
        lines = feedback.split('\n')
        current_category = None

        for line in lines:
            line = line.strip()
            if line.startswith('### 优点') or line.startswith('### Strengths'):
                current_category = "strength"
            elif line.startswith('### 重要') or line.startswith('### Important'):
                current_category = "important"
            elif line.startswith('### 次要') or line.startswith('### Minor'):
                current_category = "minor"
            elif line.startswith('- [ ]') and current_category:
                finding = ReviewFinding(
                    category=current_category,
                    description=line.replace('- [ ]', '').strip()
                )
                findings.append(finding)

        approved = "准备好继续" in feedback or "approved" in feedback.lower()

        return ReviewResult(
            status="completed",
            findings=findings,
            approved=approved,
            summary=f"审查完成: {len(findings)} 项发现"
        )

    def generate_review_prompt(self) -> str:
        """生成审查提示"""
        return """
作为代码审查者，请提供结构化反馈：

1. **优点**: 识别代码中做得好的方面
2. **重要问题**: 任何需要立即修复的阻塞问题
3. **次要问题**: 可以稍后处理的建议
4. **建议**: 具体的改进建议

审查标准：
- 架构是否合理？
- 测试是否充分？
- 是否有安全问题？
- 是否符合项目规范？
- 是否有性能问题？

提供具体位置和建议。
        """.strip()


def main():
    """入口函数"""
    return RequestingCodeReviewSkill()


if __name__ == "__main__":
    skill = main()
