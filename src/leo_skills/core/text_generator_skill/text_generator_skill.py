# -*- coding: utf-8 -*-
"""
text_generator_skill - 文本生成核心技能

基于 LLM API 的文本生成、优化和合成功能。
支持多种生成模式：直接生成、模板渲染、文本优化、多输入合成。
"""

import os
import re
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from enum import Enum


class GenerationMode(Enum):
    """文本生成模式"""
    DIRECT = "direct"           # 直接生成
    TEMPLATE = "template"       # 模板渲染
    REFINE = "refine"          # 文本优化
    SYNTHESIZE = "synthesize"   # 多输入合成


@dataclass
class GenerationResult:
    """生成结果"""
    text: str
    status: str
    tokens_used: Optional[int] = None
    model: Optional[str] = None
    error: Optional[str] = None


class TextGeneratorSkill:
    """
    文本生成技能 - 核心文本生成引擎

    功能：
    - 基于提示词生成文本
    - 使用模板渲染内容
    - 优化和改进现有文本
    - 合成多个输入为连贯输出
    """

    def __init__(self):
        self.name = "text_generator_skill"
        self.version = "1.0.0"
        self.description = "基于LLM的文本生成核心技能"
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """加载配置"""
        return {
            "default_model": "claude-3-haiku-20240307",
            "max_tokens": 4000,
            "temperature": 0.7,
            "timeout": 300,
            "retry_count": 1
        }

    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        执行技能主入口

        Args:
            mode: 生成模式 (direct/template/refine/synthesize)
            prompt: 提示词
            context: 上下文信息
            template: 模板字符串
            text: 待优化的文本
            inputs: 合成模式的输入列表
            options: 额外选项

        Returns:
            Dict 包含生成结果
        """
        mode = kwargs.get("mode", "direct")

        try:
            if mode == GenerationMode.DIRECT.value:
                result = self.generate(
                    prompt=kwargs.get("prompt", ""),
                    context=kwargs.get("context", ""),
                    options=kwargs.get("options", {})
                )
            elif mode == GenerationMode.TEMPLATE.value:
                result = self.render_template(
                    template=kwargs.get("template", ""),
                    variables=kwargs.get("variables", {}),
                    options=kwargs.get("options", {})
                )
            elif mode == GenerationMode.REFINE.value:
                result = self.refine(
                    text=kwargs.get("text", ""),
                    instructions=kwargs.get("instructions", ""),
                    options=kwargs.get("options", {})
                )
            elif mode == GenerationMode.SYNTHESIZE.value:
                result = self.synthesize(
                    inputs=kwargs.get("inputs", []),
                    prompt=kwargs.get("prompt", ""),
                    options=kwargs.get("options", {})
                )
            else:
                return {
                    "status": "error",
                    "skill": self.name,
                    "error": f"Unknown mode: {mode}"
                }

            return {
                "status": "success",
                "skill": self.name,
                "mode": mode,
                "result": result
            }

        except Exception as e:
            return {
                "status": "error",
                "skill": self.name,
                "mode": mode,
                "error": str(e)
            }

    def generate(
        self,
        prompt: str,
        context: str = "",
        options: Optional[Dict[str, Any]] = None
    ) -> GenerationResult:
        """
        基于提示词生成文本

        Args:
            prompt: 主要提示词
            context: 上下文信息
            options: 生成选项

        Returns:
            GenerationResult 生成结果
        """
        options = options or {}

        # 构建完整提示词
        full_prompt = self._build_prompt(prompt, context)

        # 模拟LLM生成（实际项目中应调用真实API）
        generated_text = self._simulate_generation(full_prompt, options)

        return GenerationResult(
            text=generated_text,
            status="success",
            tokens_used=len(full_prompt.split()) + len(generated_text.split()),
            model=options.get("model", self.config["default_model"])
        )

    def render_template(
        self,
        template: str,
        variables: Dict[str, Any],
        options: Optional[Dict[str, Any]] = None
    ) -> GenerationResult:
        """
        使用模板渲染内容

        Args:
            template: 模板字符串，使用 {{variable}} 语法
            variables: 变量字典
            options: 渲染选项

        Returns:
            GenerationResult 渲染结果
        """
        try:
            # 简单的模板替换
            result_text = template
            for key, value in variables.items():
                placeholder = f"{{{{{key}}}}}"
                result_text = result_text.replace(placeholder, str(value))

            # 检查是否还有未替换的变量
            remaining = re.findall(r'\{\{(\w+)\}\}', result_text)
            if remaining:
                return GenerationResult(
                    text=result_text,
                    status="partial",
                    error=f"未替换的变量: {remaining}"
                )

            return GenerationResult(
                text=result_text,
                status="success"
            )

        except Exception as e:
            return GenerationResult(
                text="",
                status="error",
                error=str(e)
            )

    def refine(
        self,
        text: str,
        instructions: str,
        options: Optional[Dict[str, Any]] = None
    ) -> GenerationResult:
        """
        优化和改进现有文本

        Args:
            text: 待优化的文本
            instructions: 优化指令
            options: 优化选项

        Returns:
            GenerationResult 优化结果
        """
        options = options or {}

        # 构建优化提示词
        refine_prompt = f"""请根据以下指令优化文本：

优化指令：
{instructions}

原始文本：
{text}

请提供优化后的版本："""

        # 模拟生成优化文本
        refined_text = self._simulate_generation(refine_prompt, options)

        return GenerationResult(
            text=refined_text,
            status="success",
            tokens_used=len(refine_prompt.split()) + len(refined_text.split()),
            model=options.get("model", self.config["default_model"])
        )

    def synthesize(
        self,
        inputs: List[str],
        prompt: str,
        options: Optional[Dict[str, Any]] = None
    ) -> GenerationResult:
        """
        合成多个输入为连贯输出

        Args:
            inputs: 输入文本列表
            prompt: 合成提示词
            options: 合成选项

        Returns:
            GenerationResult 合成结果
        """
        options = options or {}

        # 构建合成提示词
        inputs_text = "\n\n---\n\n".join(
            f"输入 {i+1}:\n{inp}" for i, inp in enumerate(inputs)
        )

        synthesize_prompt = f"""请根据以下提示词，合成多个输入为连贯输出：

合成提示词：
{prompt}

输入内容：
{inputs_text}

请提供合成后的输出："""

        # 模拟生成合成文本
        synthesized_text = self._simulate_generation(synthesize_prompt, options)

        return GenerationResult(
            text=synthesized_text,
            status="success",
            tokens_used=len(synthesize_prompt.split()) + len(synthesized_text.split()),
            model=options.get("model", self.config["default_model"])
        )

    def _build_prompt(self, prompt: str, context: str) -> str:
        """构建完整提示词"""
        if context:
            return f"上下文：\n{context}\n\n任务：\n{prompt}"
        return prompt

    def _simulate_generation(
        self,
        prompt: str,
        options: Dict[str, Any]
    ) -> str:
        """
        模拟文本生成（实际项目应调用真实LLM API）

        支持的模型：
        - claude-3-haiku: 快速生成
        - claude-3-sonnet: 平衡质量与速度
        - claude-3-opus: 最高质量
        - gpt-4: OpenAI GPT-4
        - gpt-3.5-turbo: OpenAI GPT-3.5
        """
        # 这里应该调用实际的LLM API
        # 目前返回模拟响应用于演示
        model = options.get("model", self.config["default_model"])

        # 根据提示词长度生成模拟响应
        prompt_words = len(prompt.split())

        if "总结" in prompt or "summarize" in prompt.lower():
            return f"[这是基于 {model} 的总结输出]\n\n根据提供的内容，关键点包括：\n1. 主要概念说明\n2. 重要发现\n3. 结论和建议"

        elif "代码" in prompt or "code" in prompt.lower():
            return f"[这是基于 {model} 的代码生成]\n\n```python\n# 生成的代码示例\ndef example_function():\n    pass\n```"

        elif "优化" in prompt or "improve" in prompt.lower():
            return f"[这是基于 {model} 的优化版本]\n\n优化后的文本会更加清晰、简洁和专业。"

        else:
            return f"[这是基于 {model} 的生成结果]\n\n根据您的提示词（{prompt_words} 词），生成了相应的内容。实际部署时将连接真实LLM API。"

    def get_capabilities(self) -> Dict[str, Any]:
        """获取技能能力信息"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "modes": [m.value for m in GenerationMode],
            "config": self.config
        }


# 向后兼容
TEXT_Skill = TextGeneratorSkill


def main():
    """入口函数 - 演示用法"""
    skill = TextGeneratorSkill()

    print("=" * 60)
    print("Text Generator Skill - 演示")
    print("=" * 60)

    # 演示1: 直接生成
    print("\n1. 直接生成模式")
    print("-" * 40)
    result = skill.generate(
        prompt="写一段关于人工智能的简介",
        context="面向技术博客读者"
    )
    print(f"状态: {result.status}")
    print(f"结果: {result.text[:100]}...")

    # 演示2: 模板渲染
    print("\n2. 模板渲染模式")
    print("-" * 40)
    result = skill.render_template(
        template="你好 {{name}}，欢迎来到 {{place}}！",
        variables={"name": "Leo", "place": "AI世界"}
    )
    print(f"状态: {result.status}")
    print(f"结果: {result.text}")

    # 演示3: 文本优化
    print("\n3. 文本优化模式")
    print("-" * 40)
    result = skill.refine(
        text="这个产品很好，用起来很方便。",
        instructions="让这段文字更专业、更有说服力"
    )
    print(f"状态: {result.status}")
    print(f"结果: {result.text[:100]}...")

    # 演示4: 多输入合成
    print("\n4. 多输入合成模式")
    print("-" * 40)
    result = skill.synthesize(
        inputs=[
            "方案A的优点是成本低",
            "方案B的优点是性能好",
            "方案C的优点是易维护"
        ],
        prompt="综合以上方案，提出最佳建议"
    )
    print(f"状态: {result.status}")
    print(f"结果: {result.text[:100]}...")

    print("\n" + "=" * 60)
    print("演示完成！")
    print("=" * 60)

    return skill


if __name__ == "__main__":
    main()
