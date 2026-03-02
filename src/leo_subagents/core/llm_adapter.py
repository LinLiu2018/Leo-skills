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
from pathlib import Path

# 尝试加载 .env 文件
try:
    from dotenv import load_dotenv
    # 查找项目根目录的 .env 文件
    env_path = Path(__file__).parent.parent.parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass  # 如果没有 python-dotenv，依赖系统环境变量


class LLMProvider(Enum):
    """支持的 LLM 提供商"""
    # 国际模型
    CLAUDE = "claude"
    DEEPSEEK = "deepseek"
    OPENAI = "openai"
    # 国内模型
    KIMI = "kimi"           # Moonshot AI
    QWEN = "qwen"           # 通义千问
    MINIMAX = "minimax"     # Minimax


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
            if self.provider == LLMProvider.CLAUDE:
                api_key = os.getenv("ANTHROPIC_API_KEY")
            elif self.provider == LLMProvider.DEEPSEEK:
                api_key = os.getenv("DEEPSEEK_API_KEY")
            elif self.provider == LLMProvider.OPENAI:
                api_key = os.getenv("OPENAI_API_KEY")
            # 国内模型
            elif self.provider == LLMProvider.KIMI:
                api_key = os.getenv("KIMI_API_KEY") or os.getenv("MOONSHOT_API_KEY")
            elif self.provider == LLMProvider.QWEN:
                api_key = os.getenv("QWEN_API_KEY") or os.getenv("DASHSCOPE_API_KEY")
            elif self.provider == LLMProvider.MINIMAX:
                api_key = os.getenv("MINIMAX_API_KEY")
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
            # 国内模型（使用 OpenAI 兼容接口）
            elif self.provider == LLMProvider.KIMI:
                self._client = self._init_kimi_client()
            elif self.provider == LLMProvider.QWEN:
                self._client = self._init_qwen_client()
            elif self.provider == LLMProvider.MINIMAX:
                self._client = self._init_minimax_client()
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

    # ==================== 国内模型客户端 ====================

    def _init_kimi_client(self):
        """初始化 Kimi (Moonshot) 客户端"""
        try:
            import openai
            return openai.OpenAI(
                api_key=self.api_key,
                base_url="https://api.moonshot.cn/v1"
            )
        except ImportError:
            raise ImportError("请安装 openai: pip install openai")

    def _init_qwen_client(self):
        """初始化通义千问客户端"""
        try:
            import openai
            return openai.OpenAI(
                api_key=self.api_key,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
            )
        except ImportError:
            raise ImportError("请安装 openai: pip install openai")

    def _init_minimax_client(self):
        """初始化 Minimax 客户端"""
        try:
            import openai
            return openai.OpenAI(
                api_key=self.api_key,
                base_url="https://api.minimax.chat/v1"
            )
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
            # 国内模型
            elif self.provider == LLMProvider.KIMI:
                return self._call_kimi(prompt, system_prompt, max_tokens, temperature, **kwargs)
            elif self.provider == LLMProvider.QWEN:
                return self._call_qwen(prompt, system_prompt, max_tokens, temperature, **kwargs)
            elif self.provider == LLMProvider.MINIMAX:
                return self._call_minimax(prompt, system_prompt, max_tokens, temperature, **kwargs)
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

    # ==================== 国内模型调用方法 ====================

    def _call_kimi(
        self,
        prompt: str,
        system_prompt: Optional[str],
        max_tokens: int,
        temperature: float,
        **kwargs
    ) -> LLMResponse:
        """调用 Kimi (Moonshot) API"""
        client = self._get_client()

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = client.chat.completions.create(
            model=kwargs.get("model", "moonshot-v1-8k"),
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
            provider="kimi",
            raw_response=response
        )

    def _call_qwen(
        self,
        prompt: str,
        system_prompt: Optional[str],
        max_tokens: int,
        temperature: float,
        **kwargs
    ) -> LLMResponse:
        """调用通义千问 API"""
        client = self._get_client()

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = client.chat.completions.create(
            model=kwargs.get("model", "qwen-max"),
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
            provider="qwen",
            raw_response=response
        )

    def _call_minimax(
        self,
        prompt: str,
        system_prompt: Optional[str],
        max_tokens: int,
        temperature: float,
        **kwargs
    ) -> LLMResponse:
        """调用 Minimax API"""
        client = self._get_client()

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = client.chat.completions.create(
            model=kwargs.get("model", "abab6.5-chat"),
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
            provider="minimax",
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


# ==================== 自动切换路由器 ====================

class LLMRouter:
    """
    LLM 自动切换路由器

    管理多个 LLM 提供商，当一个调用失败时自动切换到下一个
    支持优先级配置和额度管理

    用法:
        router = LLMRouter(
            providers=["kimi", "qwen", "deepseek", "minimax"],
            priorities={"kimi": 1, "qwen": 2, "deepseek": 3}
        )
        response = router.call("研究宁波商铺市场")
    """

    DEFAULT_PROVIDERS = ["kimi", "qwen", "deepseek", "minimax"]

    def __init__(
        self,
        providers: List[str] = None,
        priorities: Dict[str, int] = None,
        auto_switch_on_error: bool = True,
        max_retries_per_provider: int = 1
    ):
        """
        初始化 LLM 路由器

        Args:
            providers: 提供商列表，默认使用国内模型
            priorities: 优先级字典，数字越小优先级越高
            auto_switch_on_error: 错误时是否自动切换
            max_retries_per_provider: 每个提供商最大重试次数
        """
        self.providers = providers or self.DEFAULT_PROVIDERS
        self.priorities = priorities or {}
        self.auto_switch_on_error = auto_switch_on_error
        self.max_retries_per_provider = max_retries_per_provider

        # 初始化适配器
        self._adapters: Dict[str, LLMAdapter] = {}
        self._failed_providers: set = set()

        # 按优先级排序
        self._sort_providers()

    def _sort_providers(self):
        """按优先级排序提供商"""
        self.providers.sort(
            key=lambda p: self.priorities.get(p, 999)
        )

    def _get_adapter(self, provider: str) -> Optional[LLMAdapter]:
        """获取适配器（带缓存）"""
        if provider not in self._adapters:
            try:
                self._adapters[provider] = LLMAdapter(provider=provider)
            except Exception as e:
                print(f"[WARNING] 初始化 {provider} 失败: {e}")
                return None
        return self._adapters.get(provider)

    def call(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4000,
        temperature: float = 0.7,
        **kwargs
    ) -> LLMResponse:
        """
        调用 LLM，自动处理失败切换

        按优先级尝试各个提供商，直到成功或全部失败
        """
        last_error = None

        for provider in self.providers:
            if provider in self._failed_providers:
                continue

            adapter = self._get_adapter(provider)
            if not adapter:
                continue

            # 检查 API 密钥是否配置
            if not adapter.api_key:
                print(f"[INFO] {provider} 未配置 API 密钥，跳过")
                continue

            # 尝试调用
            for attempt in range(self.max_retries_per_provider):
                try:
                    print(f"[LLMRouter] 尝试 {provider} (第 {attempt + 1} 次)...")
                    response = adapter.call(
                        prompt=prompt,
                        system_prompt=system_prompt,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        **kwargs
                    )

                    # 检查是否是模拟模式（API 密钥无效）
                    if response.provider == "mock":
                        print(f"[INFO] {provider} 使用模拟模式，尝试下一个")
                        break

                    print(f"[LLMRouter] {provider} 调用成功")
                    return response

                except Exception as e:
                    last_error = e
                    print(f"[WARNING] {provider} 调用失败: {e}")

                    if not self.auto_switch_on_error:
                        raise

        # 所有提供商都失败，返回模拟响应
        print(f"[ERROR] 所有 LLM 提供商都失败，返回模拟模式")
        if last_error:
            print(f"[ERROR] 最后一个错误: {last_error}")

        return LLMAdapter(provider="claude")._mock_call(prompt, system_prompt)

    def get_status(self) -> Dict[str, Any]:
        """获取路由器状态"""
        return {
            "providers": self.providers,
            "priorities": self.priorities,
            "failed_providers": list(self._failed_providers),
            "configured_providers": [
                p for p in self.providers
                if self._get_adapter(p) and self._get_adapter(p).api_key
            ]
        }

    def reset_failed_providers(self):
        """重置失败的提供商列表"""
        self._failed_providers.clear()
        print("[LLMRouter] 已重置失败提供商列表")


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
