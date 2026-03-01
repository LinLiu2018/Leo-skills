"""
AI 模型客户端 - 支持多种国内模型
"""

import os
from typing import Dict, List, Any, Optional
import json
from pathlib import Path

# 加载环境变量
from dotenv import load_dotenv
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# 优先使用智谱 AI
try:
    from zhipuai import ZhipuAI
    ZHIPU_AVAILABLE = True
except ImportError:
    ZHIPU_AVAILABLE = False

# 备选: OpenAI
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Minimax 使用 requests 直接调用
import requests


class AIClient:
    """AI 模型客户端"""

    def __init__(self):
        self.provider = os.getenv("AI_PROVIDER", "minimax")  # minimax / zhipu / openai
        self.model = os.getenv("AI_MODEL", "abab6.5s-chat")

        if self.provider == "minimax":
            api_key = os.getenv("MINIMAX_API_KEY")
            if not api_key:
                raise ValueError("MINIMAX_API_KEY not set")
            self.api_key = api_key
            self.api_url = "https://api.minimax.chat/v1/text/chatcompletion_v2"

        elif self.provider == "zhipu" and ZHIPU_AVAILABLE:
            api_key = os.getenv("ZHIPU_API_KEY")
            if not api_key:
                raise ValueError("ZHIPU_API_KEY not set")
            self.client = ZhipuAI(api_key=api_key)

        elif self.provider == "openai" and OPENAI_AVAILABLE:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not set")
            openai.api_key = api_key
            self.client = openai

        else:
            raise ValueError(f"AI provider {self.provider} not available")

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """
        调用 AI 模型生成回复

        Args:
            messages: 消息列表 [{"role": "system/user", "content": "..."}]
            temperature: 温度参数
            max_tokens: 最大 token 数

        Returns:
            生成的回复文本
        """
        try:
            if self.provider == "minimax":
                return await self._call_minimax(messages, temperature, max_tokens)

            elif self.provider == "zhipu":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                return response.choices[0].message.content

            elif self.provider == "openai":
                response = await self.client.ChatCompletion.acreate(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                return response.choices[0].message.content

        except Exception as e:
            print(f"AI API error: {e}")
            # 降级到模拟回复
            return self._fallback_response(messages)

    async def _call_minimax(self, messages: List[Dict[str, str]], temperature: float, max_tokens: int) -> str:
        """调用 Minimax API"""
        # 转换消息格式
        system_msg = ""
        user_msg = ""
        for msg in messages:
            if msg["role"] == "system":
                system_msg = msg["content"]
            elif msg["role"] == "user":
                user_msg = msg["content"]

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        response = requests.post(self.api_url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()

        # 解析 Minimax 响应
        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"]
        else:
            raise ValueError(f"Invalid response from Minimax: {result}")

    def _fallback_response(self, messages: List[Dict[str, str]]) -> str:
        """当 API 失败时的降级回复"""
        # 提取最后一条用户消息
        user_msg = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_msg = msg.get("content", "")
                break

        return f"""我已收到您的请求："{user_msg[:50]}..."

[注意：AI 服务暂时不可用，这是系统降级回复]

建议：
1. 检查 API Key 配置
2. 确认网络连接正常
3. 稍后重试

您也可以尝试使用其他功能，如技能执行或工作流。"""


# 预定义的 Agent 系统提示词
AGENT_PROMPTS = {
    "research_agent": """你是研究员 Agent，擅长深度研究和信息分析。

任务：
1. 分析用户的研究需求
2. 提供结构化的研究框架
3. 给出关键洞察和建议
4. 引用数据来源

回复格式：
📋 研究框架
🔍 关键发现
💡 行动建议
📚 参考资源

语言：中文""",

    "creative_agent": """你是创意设计师 Agent，擅长内容创作和创意策划。

任务：
1. 理解用户的创意需求
2. 提供多个创意方向
3. 给出具体的执行建议
4. 提供文案和设计参考

回复格式：
💡 创意概念
🎯 目标受众
📝 内容策略
🎨 视觉建议

语言：中文""",

    "analysis_agent": """你是数据分析师 Agent，擅长数据分析和洞察提取。

任务：
1. 分析用户提供的数据或需求
2. 识别关键指标和趋势
3. 提供数据驱动的建议
4. 生成可视化建议

回复格式：
📊 数据概览
📈 趋势分析
🔍 关键洞察
💡 优化建议

语言：中文""",

    "architect_agent": """你是系统架构师 Agent，擅长技术架构设计。

任务：
1. 理解系统需求
2. 设计技术架构方案
3. 推荐技术选型
4. 评估可行性

回复格式：
🏗️ 架构方案
🔧 技术选型
⚖️ 优劣分析
📝 实施建议

语言：中文""",

    "product_manager_agent": """你是产品经理 Agent，擅长产品规划和需求分析。

任务：
1. 分析产品需求
2. 梳理用户故事
3. 制定产品路线图
4. 评估优先级

回复格式：
📋 需求分析
👤 用户画像
🗺️ 产品路线图
⭐ 优先级建议

语言：中文"""
}


class AgentEngine:
    """Agent 执行引擎 - 真正的 AI 驱动"""

    def __init__(self):
        self.ai_client = AIClient()

    async def execute(
        self,
        agent_type: str,
        user_message: str,
        context: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        执行 Agent 任务

        Args:
            agent_type: Agent 类型 (research_agent, creative_agent 等)
            user_message: 用户消息
            context: 对话上下文

        Returns:
            执行结果
        """
        import time
        start_time = time.time()

        # 获取系统提示词
        system_prompt = AGENT_PROMPTS.get(
            agent_type,
            "你是 Leo AI 助手，请帮助用户完成任务。"
        )

        # 构建消息列表
        messages = [{"role": "system", "content": system_prompt}]

        if context:
            messages.extend(context)

        messages.append({"role": "user", "content": user_message})

        # 调用 AI 生成回复
        try:
            response_text = await self.ai_client.chat_completion(messages)
            status = "success"
            error = None
        except Exception as e:
            response_text = f"执行出错：{str(e)}"
            status = "error"
            error = str(e)

        execution_time = int((time.time() - start_time) * 1000)

        return {
            "response": response_text,
            "agent": agent_type,
            "agent_name": self._get_agent_name(agent_type),
            "role": agent_type.replace("_agent", ""),
            "task": user_message,
            "execution_time_ms": execution_time,
            "status": status,
            "error": error
        }

    def _get_agent_name(self, agent_type: str) -> str:
        """获取 Agent 显示名称"""
        names = {
            "research_agent": "研究员",
            "creative_agent": "创意设计师",
            "analysis_agent": "数据分析师",
            "architect_agent": "系统架构师",
            "product_manager_agent": "产品经理",
            "mobile_agent": "移动端开发",
            "realestate_agent": "房产顾问"
        }
        return names.get(agent_type, "AI 助手")


# 全局实例
_ai_client: Optional[AIClient] = None
_agent_engine: Optional[AgentEngine] = None


def get_ai_client() -> AIClient:
    """获取 AI 客户端单例"""
    global _ai_client
    if _ai_client is None:
        _ai_client = AIClient()
    return _ai_client


def get_agent_engine() -> AgentEngine:
    """获取 Agent 引擎单例"""
    global _agent_engine
    if _agent_engine is None:
        _agent_engine = AgentEngine()
    return _agent_engine
