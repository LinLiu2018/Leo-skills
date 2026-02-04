# -*- coding: utf-8 -*-
"""
claude_prompt_engineering_skills - Claude提示工程技能

提供Claude最佳提示工程技术，包括少样本学习、思维链、角色设定等。
"""

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum


class PromptTechnique(Enum):
    """提示工程技术"""
    FEW_SHOT = "few_shot"
    CHAIN_OF_THOUGHT = "chain_of_thought"
    ROLE_PLAYING = "role_playing"
    SELF_CORRECTION = "self_correction"
    CONTEXT_OPTIMIZATION = "context_optimization"
    OUTPUT_FORMATTING = "output_formatting"


@dataclass
class PromptExample:
    """提示示例"""
    input_text: str
    output_text: str
    explanation: str = ""


@dataclass
class PromptTemplate:
    """提示模板"""
    name: str
    template: str
    technique: PromptTechnique
    description: str
    examples: List[PromptExample] = field(default_factory=list)


class ClaudePromptEngineeringSkills:
    """
    Claude提示工程技能

    功能：
    - 提供最佳提示工程技术
    - 管理提示模板
    - 优化提示效果
    - 生成格式化输出

    使用场景：
    - 复杂任务分解
    - 精确输出控制
    - 上下文优化
    - 角色扮演对话
    """

    def __init__(self):
        self.name = "claude_prompt_engineering_skills"
        self.version = "1.0.0"
        self.description = "Claude提示工程技能 - 提供最佳提示工程技术"

        # 初始化模板库
        self._init_templates()

    def _init_templates(self):
        """初始化提示模板"""
        self.templates = {
            PromptTechnique.FEW_SHOT: PromptTemplate(
                name="Few-Shot Learning",
                template="""任务：{task}

示例：
{examples}

请根据以上示例完成任务：
{input}""",
                technique=PromptTechnique.FEW_SHOT,
                description="通过提供示例来引导模型学习模式",
                examples=[
                    PromptExample(
                        input_text="将以下句子转换为被动语态：主动sender sent the email.",
                        output_text="The email was sent by the sender.",
                        explanation="展示了主动到被动的转换模式"
                    )
                ]
            ),
            PromptTechnique.CHAIN_OF_THOUGHT: PromptTemplate(
                name="Chain of Thought",
                template="""问题：{problem}

请逐步思考：
{steps}

最终答案：""",
                technique=PromptTechnique.CHAIN_OF_THOUGHT,
                description="通过分解步骤来增强推理能力",
                examples=[
                    PromptExample(
                        input_text="如果A比B大，B比C大，A和C哪个大？",
                        output_text="1. A > B\n2. B > C\n3. 因此 A > C，A更大",
                        explanation="展示逐步推理过程"
                    )
                ]
            ),
            PromptTechnique.ROLE_PLAYING: PromptTemplate(
                name="Role Playing",
                template="""你是一个{role}。

背景信息：
{background}

你的专业知识：
{expertise}

请以{role}的身份回答以下问题：
{question}""",
                technique=PromptTechnique.ROLE_PLAYING,
                description="通过角色设定来获得专业视角",
                examples=[
                    PromptExample(
                        input_text="如何提高代码质量？",
                        output_text="作为资深架构师，我认为应该：1. 遵循SOLID原则...",
                        explanation="设定角色为架构师获取专业建议"
                    )
                ]
            ),
            PromptTechnique.SELF_CORRECTION: PromptTemplate(
                name="Self-Correction",
                template="""初始回答：{initial_answer}

请检查以上回答是否存在以下问题：
1. 逻辑错误
2. 事实错误
3. 不完整

修正后的回答：""",
                technique=PromptTechnique.SELF_CORRECTION,
                description="通过自我检查来提高回答质量",
                examples=[]
            ),
            PromptTechnique.CONTEXT_OPTIMIZATION: PromptTemplate(
                name="Context Optimization",
                template="""任务目标：{goal}

可用上下文：
{context}

请筛选最相关的上下文信息，并完成任务：
{task}""",
                technique=PromptTechnique.CONTEXT_OPTIMIZATION,
                description="优化上下文使用效率",
                examples=[]
            ),
            PromptTechnique.OUTPUT_FORMATTING: PromptTemplate(
                name="Output Formatting",
                template="""请按照以下格式输出结果：

{format_spec}

输入内容：
{input}""",
                technique=PromptTechnique.OUTPUT_FORMATTING,
                description="控制输出的格式和结构",
                examples=[
                    PromptExample(
                        input_text="分析这个项目的优缺点",
                        output_text="## 优点\n- ...\n\n## 缺点\n- ...\n\n## 建议\n- ...",
                        explanation="指定Markdown格式输出"
                    )
                ]
            )
        }

    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        执行提示工程

        Args:
            technique: 使用的技术 (few_shot/chain_of_thought/role_playing/self_correction/context_optimization/output_formatting)
            task: 任务描述
            examples: 示例列表 (few_shot)
            role: 角色设定 (role_playing)
            format_spec: 格式规范 (output_formatting)
            input: 输入内容
            goal: 目标 (context_optimization)

        Returns:
            Dict 包含生成的提示和结果
        """
        technique_name = kwargs.get("technique", "chain_of_thought")
        action = kwargs.get("action", "generate")

        try:
            technique = PromptTechnique(technique_name)

            if action == "generate":
                return self._generate_prompt(technique, kwargs)
            elif action == "optimize":
                return self._optimize_prompt(kwargs.get("prompt", ""))
            elif action == "list":
                return self._list_techniques()
            else:
                return {"status": "error", "message": f"Unknown action: {action}"}

        except Exception as e:
            return {"status": "error", "error": str(e), "skill": self.name}

    def _generate_prompt(self, technique: PromptTechnique, kwargs: Dict) -> Dict[str, Any]:
        """生成提示"""
        template = self.templates.get(technique)
        if not template:
            return {"status": "error", "message": f"Technique not found: {technique}"}

        # 根据技术类型填充模板
        if technique == PromptTechnique.FEW_SHOT:
            examples_text = self._format_examples(kwargs.get("examples", []))
            prompt = template.template.format(
                task=kwargs.get("task", ""),
                examples=examples_text,
                input=kwargs.get("input", "")
            )
        elif technique == PromptTechnique.CHAIN_OF_THOUGHT:
            prompt = template.template.format(
                problem=kwargs.get("problem", ""),
                steps="\n1. " + "\n2. ".join(kwargs.get("steps", ["分析问题", "制定计划", "执行解决"])),
                input=""
            )
        elif technique == PromptTechnique.ROLE_PLAYING:
            prompt = template.template.format(
                role=kwargs.get("role", "专家"),
                background=kwargs.get("background", ""),
                expertise=kwargs.get("expertise", ""),
                question=kwargs.get("question", "")
            )
        elif technique == PromptTechnique.SELF_CORRECTION:
            prompt = template.template.format(
                initial_answer=kwargs.get("initial_answer", "")
            )
        elif technique == PromptTechnique.CONTEXT_OPTIMIZATION:
            prompt = template.template.format(
                goal=kwargs.get("goal", ""),
                context=kwargs.get("context", ""),
                task=kwargs.get("task", "")
            )
        elif technique == PromptTechnique.OUTPUT_FORMATTING:
            prompt = template.template.format(
                format_spec=kwargs.get("format_spec", ""),
                input=kwargs.get("input", "")
            )
        else:
            prompt = template.template

        return {
            "status": "success",
            "skill": self.name,
            "technique": technique.value,
            "prompt": prompt
        }

    def _format_examples(self, examples: List[Dict]) -> str:
        """格式化示例"""
        if not examples:
            return "（无示例）"

        formatted = []
        for i, ex in enumerate(examples, 1):
            formatted.append(f"示例{i}:")
            formatted.append(f"  输入: {ex.get('input', '')}")
            formatted.append(f"  输出: {ex.get('output', '')}")
        return "\n".join(formatted)

    def _optimize_prompt(self, prompt: str) -> Dict[str, Any]:
        """优化提示"""
        suggestions = []

        # 检查长度
        if len(prompt) < 50:
            suggestions.append("提示过短，建议添加更多上下文和细节")

        # 检查是否有明确的目标
        if "请" not in prompt and "帮我" not in prompt:
            suggestions.append("建议在开头明确任务目标")

        # 检查是否有格式要求
        if "格式" not in prompt and "输出" not in prompt:
            suggestions.append("如果需要特定输出格式，建议明确说明")

        # 检查是否有示例
        if "例如" not in prompt and "示例" not in prompt:
            suggestions.append("考虑添加示例来引导期望的输出")

        # 检查是否使用了角色设定
        if "你是" not in prompt and "你是一个" not in prompt:
            suggestions.append("考虑设定角色以获得更专业的回答")

        return {
            "status": "success",
            "skill": self.name,
            "original_prompt": prompt,
            "suggestions": suggestions,
            "optimization_count": len(suggestions)
        }

    def _list_techniques(self) -> Dict[str, Any]:
        """列出所有技术"""
        techniques = []
        for tech, template in self.templates.items():
            techniques.append({
                "name": template.name,
                "technique": tech.value,
                "description": template.description,
                "example_count": len(template.examples)
            })

        return {
            "status": "success",
            "skill": self.name,
            "techniques": techniques
        }

    def create_few_shot_prompt(
        self,
        task: str,
        examples: List[Dict],
        input_text: str
    ) -> str:
        """创建Few-Shot提示"""
        return self.execute(
            technique="few_shot",
            action="generate",
            task=task,
            examples=examples,
            input=input_text
        )["prompt"]

    def create_cot_prompt(
        self,
        problem: str,
        steps: List[str] = None
    ) -> str:
        """创建Chain of Thought提示"""
        return self.execute(
            technique="chain_of_thought",
            action="generate",
            problem=problem,
            steps=steps or ["分析问题", "分解步骤", "逐步解决"]
        )["prompt"]

    def create_role_prompt(
        self,
        role: str,
        background: str,
        expertise: str,
        question: str
    ) -> str:
        """创建角色扮演提示"""
        return self.execute(
            technique="role_playing",
            action="generate",
            role=role,
            background=background,
            expertise=expertise,
            question=question
        )["prompt"]

    def get_capabilities(self) -> Dict[str, Any]:
        """获取技能能力信息"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "features": [
                "few_shot_learning",
                "chain_of_thought",
                "role_playing",
                "self_correction",
                "context_optimization",
                "output_formatting",
                "prompt_optimization"
            ],
            "techniques": [t.value for t in PromptTechnique]
        }


# 向后兼容
Claude_Prompt_Engineering_Skills = ClaudePromptEngineeringSkills


def main():
    """入口函数 - 演示用法"""
    print("=" * 60)
    print("Claude Prompt Engineering Skills - 演示")
    print("=" * 60)

    skill = ClaudePromptEngineeringSkills()

    # 演示1: 列出所有技术
    print("\n1. 列出所有提示工程技术")
    print("-" * 40)
    result = skill.execute(action="list")
    print(f"可用技术数: {len(result['techniques'])}")
    for t in result['techniques']:
        print(f"  - {t['name']}: {t['description']}")

    # 演示2: 生成Chain of Thought提示
    print("\n2. 生成Chain of Thought提示")
    print("-" * 40)
    result = skill.execute(
        technique="chain_of_thought",
        action="generate",
        problem="计算15分钟内有多少秒？"
    )
    print(f"生成的提示:\n{result['prompt']}")

    # 演示3: 生成角色扮演提示
    print("\n3. 生成角色扮演提示")
    print("-" * 40)
    result = skill.execute(
        technique="role_playing",
        action="generate",
        role="Python专家",
        background="你是一个有10年Python开发经验的专家",
        expertise="精通Python最佳实践、性能优化和代码重构",
        question="如何优化这个列表推导式？"
    )
    print(f"生成的提示:\n{result['prompt']}")

    # 演示4: 优化提示
    print("\n4. 优化提示")
    print("-" * 40)
    result = skill.execute(
        action="optimize",
        prompt="写一个函数"
    )
    print(f"优化建议数: {result['optimization_count']}")
    for s in result['suggestions']:
        print(f"  - {s}")

    print("\n" + "=" * 60)
    print("演示完成！")
    print("=" * 60)

    return skill


if __name__ == "__main__":
    main()
