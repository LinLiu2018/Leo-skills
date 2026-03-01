# -*- coding: utf-8 -*-
"""
LLM 调用适配器
=============
支持 Claude/DeepSeek/OpenAI 的统一调用接口

为 Agent 执行层提供真实的 LLM 调用能力
"""

import os
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum


class LLMProvider(Enum):
    """支持的 LLM 提供商"""
    CLAUDE = "claude"
    DEEPSEEK = "deepseek"
    OPENAI = "openai"


@dataclass
class LLMResponse:
    """LLM 响应封装"""
    content: str
    usage: Dict[str, int]
    model: str
    provider: str
    raw_response: Any = None


class LLMAdapter:
    """
    LLM 调用适配器

    提供统一的 LLM 调用接口，支持多种提供商
    自动处理 API 密钥、重试、错误处理

    用法:
        llm = LLMAdapter(provider="claude")
        response = llm.call(
            prompt="分析宁波商铺市场",
            system_prompt="你是一个房地产分析师"
        )
        print(response.content)
    """

    def __init__(self, provider: str = "claude", api_key: Optional[str] = None):
        """
        初始化 LLM 适配器

        Args:
            provider: LLM 提供商 (claude/deepseek/openai)
            api_key: API 密钥，默认从环境变量读取
        """
        self.provider = LLMProvider(provider)
        self.api_key = api_key or self._get_api_key()
        self._client = None

    def _get_api_key(self) -> str:
        """从环境变量获取 API 密钥"""
        env_var = f"{self.provider.value.upper()}_API_KEY"
        api_key = os.getenv(env_var)
        if not api_key:
            # 尝试通用密钥
            api_key = os.getenv("ANTHROPIC_API_KEY") if self.provider == LLMProvider.CLAUDE else \
                     os.getenv("DEEPSEEK_API_KEY") if self.provider == LLMProvider.DEEPSEEK else \
                     os.getenv("OPENAI_API_KEY")
        return api_key

    def _get_client(self):
        """延迟初始化客户端"""
        if self._client is None:
            if self.provider == LLMProvider.CLAUDE:
                self._client = self._init_claude_client()
            elif self.provider == LLMProvider.DEEPSEEK:
                self._client = self._init_deepseek_client()
            elif self.provider == LLMProvider.OPENAI:
                self._client = self._init_openai_client()
        return self._client

    def _init_claude_client(self):
        """初始化 Claude 客户端"""
        try:
            import anthropic
            return anthropic.Anthropic(api_key=self.api_key)
        except ImportError:
            raise ImportError("请安装 anthropic: pip install anthropic")

    def _init_deepseek_client(self):
        """初始化 DeepSeek 客户端"""
        try:
            import openai
            return openai.OpenAI(
                api_key=self.api_key,
                base_url="https://api.deepseek.com/v1"
            )
        except ImportError:
            raise ImportError("请安装 openai: pip install openai")

    def _init_openai_client(self):
        """初始化 OpenAI 客户端"""
        try:
            import openai
            return openai.OpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError("请安装 openai: pip install openai")

    def call(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4000,
        temperature: float = 0.7,
        **kwargs
    ) -> LLMResponse:
        """
        统一调用接口

        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词
            max_tokens: 最大生成 token 数
            temperature: 温度参数
            **kwargs: 其他参数

        Returns:
            LLMResponse 响应对象
        """
        if not self.api_key:
            # 降级到模拟模式（用于测试）
            return self._mock_call(prompt, system_prompt)

        try:
            if self.provider == LLMProvider.CLAUDE:
                return self._call_claude(prompt, system_prompt, max_tokens, temperature, **kwargs)
            elif self.provider == LLMProvider.DEEPSEEK:
                return self._call_deepseek(prompt, system_prompt, max_tokens, temperature, **kwargs)
            elif self.provider == LLMProvider.OPENAI:
                return self._call_openai(prompt, system_prompt, max_tokens, temperature, **kwargs)
        except Exception as e:
            # 失败后尝试切换到模拟模式
            print(f"[WARNING] LLM 调用失败: {e}，使用模拟模式")
            return self._mock_call(prompt, system_prompt)

    def _call_claude(
        self,
        prompt: str,
        system_prompt: Optional[str],
        max_tokens: int,
        temperature: float,
        **kwargs
    ) -> LLMResponse:
        """调用 Claude API"""
        client = self._get_client()

        messages = [{"role": "user", "content": prompt}]

        response = client.messages.create(
            model=kwargs.get("model", "claude-3-opus-20240229"),
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt or "",
            messages=messages
        )

        return LLMResponse(
            content=response.content[0].text,
            usage={
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens
            },
            model=response.model,
            provider="claude",
            raw_response=response
        )

    def _call_deepseek(
        self,
        prompt: str,
        system_prompt: Optional[str],
        max_tokens: int,
        temperature: float,
        **kwargs
    ) -> LLMResponse:
        """调用 DeepSeek API"""
        client = self._get_client()

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = client.chat.completions.create(
            model=kwargs.get("model", "deepseek-chat"),
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )

        return LLMResponse(
            content=response.choices[0].message.content,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens
            },
            model=response.model,
            provider="deepseek",
            raw_response=response
        )

    def _call_openai(
        self,
        prompt: str,
        system_prompt: Optional[str],
        max_tokens: int,
        temperature: float,
        **kwargs
    ) -> LLMResponse:
        """调用 OpenAI API"""
        client = self._get_client()

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = client.chat.completions.create(
            model=kwargs.get("model", "gpt-4"),
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )

        return LLMResponse(
            content=response.choices[0].message.content,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens
            },
            model=response.model,
            provider="openai",
            raw_response=response
        )

    def _mock_call(
        self,
        prompt: str,
        system_prompt: Optional[str]
    ) -> LLMResponse:
        """
        模拟 LLM 调用（用于测试或无 API 密钥时）

        返回一个模拟的 JSON 格式响应，包含动作指令
        """
        # 从 prompt 中提取任务关键词
        task_keywords = self._extract_keywords(prompt)

        # 构建模拟响应
        mock_response = {
            "task_analysis": f"分析用户任务: {task_keywords}",
            "actions": [
                {
                    "type": "use_skill",
                    "skill": "research_assistant_skill",
                }
            ]
        }

        return LLMResponse(
            content=json.dumps(mock_response, ensure_ascii=False, indent=2),
            usage={"prompt_tokens": 100, "completion_tokens": 50},
            model="mock-model",
            provider="mock"
        )

    def _extract_keywords(self, text: str) -> List[str]:
        """从文本中提取关键词"""
        # 简单关键词提取
        keywords = []
        if "研究" in text or "调研" in text:
            keywords.append("研究")
        if "分析" in text:
            keywords.append("分析")
        if "生成" in text or "创建" in text:
            keywords.append("生成")
        if "商铺" in text or "房地产" in text:
            keywords.append("房地产")
        return keywords

    def call_with_tools(
        self,
        prompt: str,
        tools: List[Dict],
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """
        带工具调用的 LLM 调用

        Args:
            prompt: 用户提示词
            tools: 可用工具列表
            system_prompt: 系统提示词
            **kwargs: 其他参数

        Returns:
            LLMResponse 包含工具调用指令
        """
        # 构建包含工具描述的 prompt
        tools_description = json.dumps(tools, ensure_ascii=False, indent=2)

        enhanced_prompt = f"""{prompt}

可用工具:
{tools_description}

请分析任务并选择合适的工具，以 JSON 格式返回：
{{
    "thought": "你的思考过程",
    "actions": [
        {{"tool": "工具名", "params": {{}}}}
    ]
}}
"""

        return self.call(enhanced_prompt, system_prompt, **kwargs)


# ==================== 便捷函数 ====================

def get_llm(provider: str = "claude") -> LLMAdapter:
    """获取 LLM 适配器实例"""
    return LLMAdapter(provider=provider)


def quick_call(prompt: str, system_prompt: Optional[str] = None) -> str:
    """快速调用，只返回内容"""
    llm = get_llm()
    response = llm.call(prompt, system_prompt)
    return response.content


# ==================== 测试入口 ====================

if __name__ == "__main__":
    print("=" * 60)
    print("LLM Adapter 测试")
    print("=" * 60)

    # 测试模拟模式
    llm = LLMAdapter(provider="claude")
    response = llm.call(
        prompt="研究宁波商铺市场趋势",
        system_prompt="你是一个房地产分析师"
    )

    print(f"\n提供商: {response.provider}")
    print(f"模型: {response.model}")
    print(f"Token 使用: {response.usage}")
    print(f"\n响应内容:\n{response.content}")

    # 测试工具调用
    print("\n" + "=" * 60)
    print("工具调用测试")
    print("=" * 60)

    tools = [
        {
            "name": "web_search",
            "description": "搜索网络信息"
        },
        {
            "name": "data_analyze",
            "description": "分析数据"
        }
    ]

    response = llm.call_with_tools(
        prompt="帮我研究宁波商铺市场",
        tools=tools
    )
    print(f"\n响应:\n{response.content}")
