# -*- coding: utf-8 -*-
"""
chain_of_thought_prompter - 思维链提示技能

通过引导模型逐步推理，提高复杂问题的解决能力。
核心思想：让模型展示思考过程，而不仅仅是给出答案。
"""

from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from enum import Enum


class CoTStrategy(Enum):
    """思维链策略"""
    ZERO_SHOT = "zero_shot"           # 零样本思维链
    FEW_SHOT = "few_shot"             # 少样本思维链
    SELF_CONSISTENCY = "self_consistency"  # 自一致性
    STEP_BY_STEP = "step_by_step"     # 逐步分解


@dataclass
class ReasoningStep:
    """推理步骤"""
    step_number: int
    description: str
    reasoning: str
    intermediate_result: str


@dataclass
class CoTResult:
    """思维链结果"""
    final_answer: str
    reasoning_chain: List[ReasoningStep]
    confidence: float
    strategy_used: str


class ChainOfThoughtPrompterSkill:
    """
    思维链提示技能 - 引导模型逐步推理

    功能：
    - 生成思维链提示词
    - 支持多种思维链策略
    - 解析和验证推理过程
    - 提高复杂问题的解决准确性

    适用场景：
    - 数学问题求解
    - 逻辑推理
    - 多步骤决策
    - 代码调试分析
    """

    def __init__(self):
        self.name = "chain_of_thought_prompter_skill"
        self.version = "1.0.0"
        self.description = "思维链提示技能 - 引导模型逐步推理"

    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        执行技能主入口

        Args:
            action: 动作类型 (generate/parse/validate)
            problem: 问题描述
            strategy: 思维链策略
            steps: 推理步骤
            reasoning: 推理文本

        Returns:
            Dict 包含执行结果
        """
        action = kwargs.get("action", "generate")

        try:
            if action == "generate":
                result = self.generate_prompt(
                    problem=kwargs.get("problem", ""),
                    strategy=kwargs.get("strategy", CoTStrategy.STEP_BY_STEP.value),
                    context=kwargs.get("context", "")
                )
            elif action == "parse":
                result = self.parse_reasoning(
                    reasoning_text=kwargs.get("reasoning", "")
                )
            elif action == "validate":
                result = self.validate_reasoning(
                    steps=kwargs.get("steps", []),
                    final_answer=kwargs.get("final_answer", "")
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

    def generate_prompt(
        self,
        problem: str,
        strategy: str = "step_by_step",
        context: str = ""
    ) -> Dict[str, Any]:
        """
        生成思维链提示词

        Args:
            problem: 问题描述
            strategy: 策略类型
            context: 上下文信息

        Returns:
            Dict 包含提示词
        """
        if strategy == CoTStrategy.ZERO_SHOT.value:
            prompt = self._zero_shot_prompt(problem, context)
        elif strategy == CoTStrategy.FEW_SHOT.value:
            prompt = self._few_shot_prompt(problem, context)
        elif strategy == CoTStrategy.SELF_CONSISTENCY.value:
            prompt = self._self_consistency_prompt(problem, context)
        else:  # step_by_step
            prompt = self._step_by_step_prompt(problem, context)

        return {
            "prompt": prompt,
            "strategy": strategy,
            "structure_hints": self._get_structure_hints(strategy)
        }

    def _zero_shot_prompt(self, problem: str, context: str) -> str:
        """零样本思维链提示"""
        base = f"""请逐步思考以下问题：

{problem}

请按以下步骤回答：
1. 首先，理解问题的关键要素
2. 然后，分析每个要素之间的关系
3. 逐步推导出结论
4. 最后，给出明确的答案

让我们一步步来思考："""

        if context:
            base = f"上下文：{context}\n\n{base}"

        return base

    def _few_shot_prompt(self, problem: str, context: str) -> str:
        """少样本思维链提示"""
        examples = """示例1：
问题：如果一支股票从100元涨到120元，涨幅是多少？
思考过程：
1. 初始价格是100元
2. 最终价格是120元
3. 涨幅 = (120 - 100) / 100 = 0.20 = 20%
答案：20%

示例2：
问题：一个项目需要5天完成，每天工作8小时，总共需要多少小时？
思考过程：
1. 项目需要5天
2. 每天工作8小时
3. 总小时 = 5 × 8 = 40小时
答案：40小时

现在请回答："""

        base = f"""{examples}

{problem}

请按照示例的格式，展示你的思考过程："""

        if context:
            base = f"上下文：{context}\n\n{base}"

        return base

    def _self_consistency_prompt(self, problem: str, context: str) -> str:
        """自一致性提示"""
        base = f"""请用多种方法思考以下问题，然后选择最一致的答案：

{problem}

方法1（逻辑推理）：
- 基于逻辑规则一步步推导

方法2（数值计算）：
- 用数学方法验证

方法3（实例验证）：
- 用具体例子检验

请分别用以上方法思考，然后选择最可靠的答案。"""

        if context:
            base = f"上下文：{context}\n\n{base}"

        return base

    def _step_by_step_prompt(self, problem: str, context: str) -> str:
        """逐步分解提示"""
        base = f"""请将以下问题分解为步骤并解决：

问题：{problem}

步骤1 - 理解问题：
- 明确问题的目标
- 识别已知条件和约束

步骤2 - 制定计划：
- 确定解决方法
- 列出需要的步骤

步骤3 - 执行计算/推理：
- 按顺序执行每个步骤
- 记录中间结果

步骤4 - 验证结果：
- 检查结果是否合理
- 确认是否回答了问题

步骤5 - 给出答案：
- 清晰陈述最终答案

现在请开始："""

        if context:
            base = f"上下文：{context}\n\n{base}"

        return base

    def _get_structure_hints(self, strategy: str) -> List[str]:
        """获取结构提示"""
        hints = {
            "zero_shot": [
                "使用'让我们一步步来思考'触发推理",
                "鼓励模型展示中间步骤",
                "不预设具体步骤数量"
            ],
            "few_shot": [
                "提供2-3个相关示例",
                "示例应展示完整推理链",
                "示例难度应与问题相近"
            ],
            "self_consistency": [
                "使用多种方法求解",
                "比较不同方法的结果",
                "选择最一致的答案"
            ],
            "step_by_step": [
                "明确定义每个步骤",
                "记录中间结果",
                "最后验证答案"
            ]
        }
        return hints.get(strategy, [])

    def parse_reasoning(self, reasoning_text: str) -> Dict[str, Any]:
        """
        解析推理文本

        Args:
            reasoning_text: 包含推理过程的文本

        Returns:
            Dict 包含解析后的步骤
        """
        steps = []
        lines = reasoning_text.strip().split('\n')

        current_step = None
        step_number = 0

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 识别步骤标题 (步骤1:, Step 1:, 1., 等)
            import re
            step_match = re.match(r'(?:步骤|Step)\s*(\d+)[:：\-\.]', line, re.IGNORECASE)
            if not step_match:
                step_match = re.match(r'^(\d+)[:\-\.]', line)

            if step_match:
                if current_step:
                    steps.append(current_step)
                step_number = int(step_match.group(1))
                current_step = {
                    "step_number": step_number,
                    "title": line[step_match.end():].strip(),
                    "content": []
                }
            elif current_step:
                current_step["content"].append(line)

        if current_step:
            steps.append(current_step)

        # 提取最终答案
        final_answer = self._extract_final_answer(reasoning_text)

        return {
            "steps": steps,
            "step_count": len(steps),
            "final_answer": final_answer,
            "reasoning_length": len(reasoning_text)
        }

    def _extract_final_answer(self, text: str) -> str:
        """提取最终答案"""
        import re

        # 常见的答案标记
        patterns = [
            r'(?:最终答案|Final Answer|答案|Answer)[:：]\s*(.+?)(?:\n|$)',
            r'(?:结论|Conclusion)[:：]\s*(.+?)(?:\n|$)',
            r'(?:因此|Therefore)[:，,]\s*(.+?)(?:\n|$)'
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        # 如果没有找到标记，返回最后一段
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        if paragraphs:
            return paragraphs[-1]

        return ""

    def validate_reasoning(
        self,
        steps: List[Dict[str, Any]],
        final_answer: str
    ) -> Dict[str, Any]:
        """
        验证推理过程

        Args:
            steps: 推理步骤
            final_answer: 最终答案

        Returns:
            Dict 包含验证结果
        """
        issues = []
        score = 100

        # 检查步骤数量
        if len(steps) < 2:
            issues.append("推理步骤过少，至少需要2个步骤")
            score -= 30

        # 检查步骤顺序
        step_numbers = [s.get("step_number", 0) for s in steps]
        if step_numbers != sorted(step_numbers):
            issues.append("步骤顺序混乱")
            score -= 20

        # 检查是否有重复步骤号
        if len(step_numbers) != len(set(step_numbers)):
            issues.append("存在重复的步骤编号")
            score -= 15

        # 检查最终答案
        if not final_answer or len(final_answer) < 3:
            issues.append("最终答案缺失或过于简短")
            score -= 25

        # 检查步骤内容
        for step in steps:
            content = step.get("content", [])
            if not content:
                issues.append(f"步骤 {step.get('step_number')} 缺少详细内容")
                score -= 10

        return {
            "valid": len(issues) == 0,
            "score": max(0, score),
            "issues": issues,
            "recommendations": self._get_validation_recommendations(issues)
        }

    def _get_validation_recommendations(self, issues: List[str]) -> List[str]:
        """获取验证建议"""
        recommendations = []

        if any("步骤过少" in i for i in issues):
            recommendations.append("增加中间推理步骤，展示更多思考过程")

        if any("顺序混乱" in i for i in issues):
            recommendations.append("重新组织步骤，确保逻辑顺序清晰")

        if any("最终答案" in i for i in issues):
            recommendations.append("明确标注最终答案，使用'答案：'或'结论：'等标记")

        if not recommendations:
            recommendations.append("推理过程完整，可以进一步优化表达清晰度")

        return recommendations

    def get_capabilities(self) -> Dict[str, Any]:
        """获取技能能力信息"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "strategies": [s.value for s in CoTStrategy],
            "features": [
                "generate_prompt",
                "parse_reasoning",
                "validate_reasoning"
            ]
        }


# 向后兼容
ChainOfThought_Skill = ChainOfThoughtPrompterSkill


def main():
    """入口函数 - 演示用法"""
    print("=" * 60)
    print("Chain of Thought Prompter Skill - 演示")
    print("=" * 60)

    skill = ChainOfThoughtPrompterSkill()

    # 演示1: 生成零样本提示
    print("\n1. 零样本思维链提示")
    print("-" * 40)
    problem = "一个水池有2个进水管和1个排水管。A管单独注满需要6小时，B管需要8小时，排水管排空需要4小时。如果同时打开三个管子，注满水池需要多长时间？"
    result = skill.generate_prompt(problem=problem, strategy="zero_shot")
    print(f"策略: {result['strategy']}")
    print(f"提示词:\n{result['prompt'][:200]}...")

    # 演示2: 生成逐步分解提示
    print("\n2. 逐步分解提示")
    print("-" * 40)
    result = skill.generate_prompt(problem=problem, strategy="step_by_step")
    print(f"策略: {result['strategy']}")
    print(f"提示词:\n{result['prompt'][:200]}...")

    # 演示3: 解析推理文本
    print("\n3. 解析推理文本")
    print("-" * 40)
    reasoning = """步骤1：理解问题
这是一个工作效率问题，需要计算三个管子同时工作时的净效率。

步骤2：计算各管效率
A管效率 = 1/6（每小时完成1/6）
B管效率 = 1/8
排水管效率 = -1/4（负号表示排水）

步骤3：计算总效率
总效率 = 1/6 + 1/8 - 1/4 = 4/24 + 3/24 - 6/24 = 1/24

步骤4：计算时间
时间 = 1 / (1/24) = 24小时

最终答案：24小时"""
    result = skill.parse_reasoning(reasoning_text=reasoning)
    print(f"解析到步骤数: {result['step_count']}")
    print(f"最终答案: {result['final_answer']}")

    # 演示4: 验证推理
    print("\n4. 验证推理")
    print("-" * 40)
    steps = result['steps']
    validation = skill.validate_reasoning(
        steps=steps,
        final_answer=result['final_answer']
    )
    print(f"验证通过: {validation['valid']}")
    print(f"得分: {validation['score']}/100")
    print(f"建议: {validation['recommendations']}")

    print("\n" + "=" * 60)
    print("演示完成！")
    print("=" * 60)

    return skill


if __name__ == "__main__":
    main()

