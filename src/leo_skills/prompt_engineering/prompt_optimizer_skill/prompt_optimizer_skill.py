# -*- coding: utf-8 -*-
"""
prompt_optimizer - 提示词优化技能

分析和优化提示词，提高输出质量和一致性。
核心思想：通过结构化、具体化和约束来提升提示词效果。
"""

import re
from typing import Dict, Any, Optional, List, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum


class OptimizationGoal(Enum):
    """优化目标"""
    CLARITY = "clarity"           # 提高清晰度
    SPECIFICITY = "specificity"   # 提高具体性
    STRUCTURE = "structure"       # 改善结构
    CONSTRAINT = "constraint"     # 增加约束
    CONTEXT = "context"           # 添加上下文


@dataclass
class PromptIssue:
    """提示词问题"""
    issue_type: str
    description: str
    severity: str  # high, medium, low
    suggestion: str


@dataclass
class OptimizationResult:
    """优化结果"""
    original_prompt: str
    optimized_prompt: str
    improvements: List[str]
    issues_fixed: List[str]
    score_before: int
    score_after: int


class PromptOptimizerSkill:
    """
    提示词优化技能 - 提升提示词质量

    功能：
    - 分析提示词问题
    - 提供优化建议
    - 自动重构提示词
    - 评估优化效果

    优化维度：
    - 清晰度：消除歧义
    - 具体性：明确指令
    - 结构：组织有序
    - 约束：限定范围
    - 上下文：提供背景
    """

    def __init__(self):
        self.name = "prompt_optimizer_skill"
        self.version = "1.0.0"
        self.description = "提示词优化技能 - 提升AI输出质量"

    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        执行技能主入口

        Args:
            action: 动作类型 (analyze/optimize/evaluate)
            prompt: 原始提示词
            goal: 优化目标
            context: 上下文

        Returns:
            Dict 包含执行结果
        """
        action = kwargs.get("action", "analyze")

        try:
            if action == "analyze":
                result = self.analyze_prompt(
                    prompt=kwargs.get("prompt", "")
                )
            elif action == "optimize":
                result = self.optimize_prompt(
                    prompt=kwargs.get("prompt", ""),
                    goal=kwargs.get("goal", "general"),
                    context=kwargs.get("context", {})
                )
            elif action == "evaluate":
                result = self.evaluate_prompt(
                    prompt=kwargs.get("prompt", "")
                )
            else:
                return {
                    "status": "error",
                    "skill": self.name,
                    "error": f"Unknown action: {action}"
                }

            return {
                "status": "success",
                "skill": self.name,
                "action": action,
                "result": result
            }

        except Exception as e:
            return {
                "status": "error",
                "skill": self.name,
                "action": action,
                "error": str(e)
            }

    def analyze_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        分析提示词问题

        Args:
            prompt: 提示词文本

        Returns:
            Dict 包含分析结果
        """
        issues = []
        strengths = []

        # 检查长度
        word_count = len(prompt.split())
        if word_count < 10:
            issues.append(PromptIssue(
                issue_type="长度过短",
                description=f"提示词只有 {word_count} 个词，可能缺少必要信息",
                severity="medium",
                suggestion="添加更多上下文和具体要求"
            ))

        # 检查模糊词汇
        vague_words = ["一些", "几个", "适当", "合理", "可能", "大概", "等等"]
        found_vague = [w for w in vague_words if w in prompt]
        if found_vague:
            issues.append(PromptIssue(
                issue_type="模糊词汇",
                description=f"发现模糊词汇: {', '.join(found_vague)}",
                severity="high",
                suggestion="替换为具体的数值或明确的描述"
            ))

        # 检查指令清晰度
        instruction_words = ["请", "需要", "应该", "必须", "要求"]
        has_instruction = any(w in prompt for w in instruction_words)
        if not has_instruction:
            issues.append(PromptIssue(
                issue_type="缺乏明确指令",
                description="提示词缺少明确的行动指令",
                severity="high",
                suggestion="使用'请...'或'需要...'等明确的指令词汇"
            ))

        # 检查输出格式
        format_indicators = ["格式", "输出", "返回", "以...形式"]
        has_format = any(f in prompt for f in format_indicators)
        if not has_format:
            issues.append(PromptIssue(
                issue_type="缺少输出格式",
                description="未指定期望的输出格式",
                severity="medium",
                suggestion="明确说明期望的输出格式（JSON、Markdown、列表等）"
            ))

        # 检查约束条件
        constraint_words = ["限制", "约束", "不要", "避免", "仅限于"]
        has_constraint = any(c in prompt for c in constraint_words)
        if has_constraint:
            strengths.append("包含约束条件")

        # 检查上下文
        context_indicators = ["背景", "上下文", "场景", "基于"]
        has_context = any(c in prompt for c in context_indicators)
        if has_context:
            strengths.append("提供了上下文信息")

        # 检查结构
        structure_indicators = ["步骤", "首先", "然后", "最后", "1.", "2."]
        has_structure = any(s in prompt for s in structure_indicators)
        if has_structure:
            strengths.append("有良好的结构组织")

        # 计算评分
        base_score = 70
        base_score += len(strengths) * 10
        base_score -= len([i for i in issues if i.severity == "high"]) * 15
        base_score -= len([i for i in issues if i.severity == "medium"]) * 10
        base_score -= len([i for i in issues if i.severity == "low"]) * 5
        score = max(0, min(100, base_score))

        return {
            "issues": [
                {
                    "type": i.issue_type,
                    "description": i.description,
                    "severity": i.severity,
                    "suggestion": i.suggestion
                }
                for i in issues
            ],
            "strengths": strengths,
            "score": score,
            "word_count": word_count,
            "issue_count": len(issues)
        }

    def optimize_prompt(
        self,
        prompt: str,
        goal: str = "general",
        context: Dict[str, Any] = {}
    ) -> Dict[str, Any]:
        """
        优化提示词

        Args:
            prompt: 原始提示词
            goal: 优化目标
            context: 额外上下文

        Returns:
            Dict 包含优化结果
        """
        original = prompt
        improvements = []

        # 基础优化：清理和格式化
        optimized = self._basic_cleanup(prompt)
        if optimized != prompt:
            improvements.append("清理了格式和多余空格")

        # 根据目标优化
        if goal == "clarity" or goal == "general":
            optimized = self._optimize_clarity(optimized)
            improvements.append("提高了清晰度，消除了模糊词汇")

        if goal == "specificity" or goal == "general":
            optimized = self._optimize_specificity(optimized)
            improvements.append("增加了具体性，明确了要求")

        if goal == "structure" or goal == "general":
            optimized = self._optimize_structure(optimized)
            improvements.append("改善了结构，添加了步骤说明")

        if goal == "constraint":
            optimized = self._add_constraints(optimized, context)
            improvements.append("添加了约束条件和边界")

        # 评估优化效果
        before_score = self.evaluate_prompt(original)["score"]
        after_score = self.evaluate_prompt(optimized)["score"]

        return {
            "original_prompt": original,
            "optimized_prompt": optimized,
            "improvements": improvements,
            "score_before": before_score,
            "score_after": after_score,
            "improvement": after_score - before_score
        }

    def _basic_cleanup(self, prompt: str) -> str:
        """基础清理"""
        # 去除多余空格
        cleaned = " ".join(prompt.split())
        # 统一标点符号
        cleaned = cleaned.replace("，", ", ").replace("。", ". ")
        cleaned = cleaned.replace("  ", " ")
        return cleaned.strip()

    def _optimize_clarity(self, prompt: str) -> str:
        """优化清晰度"""
        # 替换模糊词汇
        replacements = {
            "一些": "3-5个",
            "几个": "2-4个",
            "适当": "具体且合适的",
            "合理": "基于最佳实践的"
        }

        for old, new in replacements.items():
            prompt = prompt.replace(old, new)

        return prompt

    def _optimize_specificity(self, prompt: str) -> str:
        """优化具体性"""
        # 如果没有明确的指令前缀，添加
        instruction_prefixes = ["请", "需要", "应该", "要求"]
        has_prefix = any(prompt.startswith(p) for p in instruction_prefixes)

        if not has_prefix:
            prompt = f"请{prompt}"

        # 如果没有输出格式说明，添加
        format_keywords = ["格式", "输出", "返回"]
        has_format = any(k in prompt for k in format_keywords)

        if not has_format:
            prompt += "\n\n请以清晰的段落形式输出结果。"

        return prompt

    def _optimize_structure(self, prompt: str) -> str:
        """优化结构"""
        lines = prompt.split('\n')

        # 检查是否需要添加结构
        if len(lines) == 1 and len(prompt) > 50:
            # 长段落，添加结构
            parts = []
            parts.append("【任务】")
            parts.append(prompt)
            parts.append("")
            parts.append("【要求】")
            parts.append("- 提供详细的回答")
            parts.append("- 使用清晰的结构")
            parts.append("- 确保内容准确")

            return "\n".join(parts)

        return prompt

    def _add_constraints(self, prompt: str, context: Dict[str, Any]) -> str:
        """添加约束"""
        constraints = context.get("constraints", [])

        if constraints:
            prompt += "\n\n【约束条件】\n"
            for i, constraint in enumerate(constraints, 1):
                prompt += f"{i}. {constraint}\n"

        return prompt

    def evaluate_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        评估提示词质量

        Args:
            prompt: 提示词

        Returns:
            Dict 包含评估结果
        """
        scores = {
            "clarity": 0,
            "specificity": 0,
            "structure": 0,
            "completeness": 0,
            "context": 0
        }

        # 清晰度评分
        vague_count = sum(1 for w in ["一些", "几个", "适当"] if w in prompt)
        scores["clarity"] = max(0, 100 - vague_count * 20)

        # 具体性评分
        specific_indicators = len(re.findall(r'\d+', prompt))  # 数字表示具体
        scores["specificity"] = min(100, 60 + specific_indicators * 10)

        # 结构评分
        structure_elements = len(re.findall(r'[\[【\n\d+\.]', prompt))
        scores["structure"] = min(100, structure_elements * 20)

        # 完整性评分
        required_elements = ["请", "需要"]
        has_elements = sum(1 for e in required_elements if e in prompt)
        scores["completeness"] = has_elements * 50

        # 上下文评分
        context_length = len(prompt.split())
        scores["context"] = min(100, context_length * 2)

        # 总分
        total_score = sum(scores.values()) // len(scores)

        return {
            "score": total_score,
            "breakdown": scores,
            "grade": self._get_grade(total_score),
            "recommendations": self._get_eval_recommendations(scores)
        }

    def _get_grade(self, score: int) -> str:
        """获取等级"""
        if score >= 90:
            return "优秀"
        elif score >= 80:
            return "良好"
        elif score >= 70:
            return "中等"
        elif score >= 60:
            return "及格"
        else:
            return "需改进"

    def _get_eval_recommendations(self, scores: Dict[str, int]) -> List[str]:
        """获取评估建议"""
        recommendations = []

        if scores["clarity"] < 70:
            recommendations.append("清晰度：减少模糊词汇，使用具体描述")

        if scores["specificity"] < 70:
            recommendations.append("具体性：添加数字、示例或明确的标准")

        if scores["structure"] < 70:
            recommendations.append("结构：使用标题、列表或段落组织内容")

        if scores["completeness"] < 70:
            recommendations.append("完整性：确保包含明确的指令词")

        if scores["context"] < 70:
            recommendations.append("上下文：添加更多背景信息")

        if not recommendations:
            recommendations.append("提示词质量良好！")

        return recommendations

    def suggest_templates(self, task_type: str) -> Dict[str, Any]:
        """
        建议提示词模板

        Args:
            task_type: 任务类型

        Returns:
            Dict 包含模板建议
        """
        templates = {
            "coding": {
                "template": """请编写 {language} 代码实现以下功能：

功能描述：{description}

要求：
- 代码风格遵循 {style_guide}
- 包含必要的注释
- 处理边界情况
- 时间复杂度不超过 {complexity}

请提供代码和简要说明。""",
                "variables": ["language", "description", "style_guide", "complexity"]
            },
            "analysis": {
                "template": """请分析以下 {topic}：

背景：{background}

分析维度：
1. {dimension1}
2. {dimension2}
3. {dimension3}

请以结构化方式呈现分析结果。""",
                "variables": ["topic", "background", "dimension1", "dimension2", "dimension3"]
            },
            "writing": {
                "template": """请撰写一篇关于 {topic} 的 {document_type}。

目标受众：{audience}
字数要求：{word_count} 字
风格：{style}

要点：
- {point1}
- {point2}
- {point3}

请确保内容连贯、逻辑清晰。""",
                "variables": ["topic", "document_type", "audience", "word_count", "style", "point1", "point2", "point3"]
            }
        }

        return templates.get(task_type, {
            "template": "请描述您的需求...",
            "variables": []
        })

    def get_capabilities(self) -> Dict[str, Any]:
        """获取技能能力信息"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "actions": ["analyze", "optimize", "evaluate"],
            "optimization_goals": [g.value for g in OptimizationGoal],
            "templates": ["coding", "analysis", "writing"]
        }


# 向后兼容
Prompt_Optimizer_Skill = PromptOptimizerSkill


def main():
    """入口函数 - 演示用法"""
    print("=" * 60)
    print("Prompt Optimizer Skill - 演示")
    print("=" * 60)

    skill = PromptOptimizerSkill()

    # 演示1: 分析提示词
    print("\n1. 分析提示词")
    print("-" * 40)
    bad_prompt = "写一些代码来排序"
    result = skill.analyze_prompt(prompt=bad_prompt)
    print(f"原始提示词: {bad_prompt}")
    print(f"评分: {result['score']}/100")
    print(f"发现问题: {result['issue_count']} 个")
    for issue in result['issues'][:2]:
        print(f"  - {issue['type']}: {issue['suggestion']}")

    # 演示2: 优化提示词
    print("\n2. 优化提示词")
    print("-" * 40)
    result = skill.optimize_prompt(
        prompt=bad_prompt,
        goal="general"
    )
    print(f"优化前评分: {result['score_before']}/100")
    print(f"优化后评分: {result['score_after']}/100")
    print(f"改进点: {', '.join(result['improvements'])}")
    print(f"优化后:\n{result['optimized_prompt']}")

    # 演示3: 评估提示词
    print("\n3. 评估提示词")
    print("-" * 40)
    good_prompt = """请编写一个Python函数，实现快速排序算法。

要求：
- 输入：一个整数列表
- 输出：排序后的列表
- 时间复杂度：O(n log n)
- 包含类型注解和文档字符串

请提供完整的代码实现和测试用例。"""
    result = skill.evaluate_prompt(prompt=good_prompt)
    print(f"总分: {result['score']}/100")
    print(f"等级: {result['grade']}")
    print("各项评分:")
    for dim, score in result['breakdown'].items():
        print(f"  {dim}: {score}")

    # 演示4: 获取模板
    print("\n4. 获取模板")
    print("-" * 40)
    template = skill.suggest_templates("coding")
    print(f"代码任务模板变量: {template['variables']}")

    print("\n" + "=" * 60)
    print("演示完成！")
    print("=" * 60)

    return skill


if __name__ == "__main__":
    main()

