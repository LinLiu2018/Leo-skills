"""
Intent parsing layer - Enhanced with LLM support.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

import requests


@dataclass
class ParsedIntent:
    """解析后的意图"""
    raw_text: str
    category: str
    confidence: float
    goals: List[str]
    entities: Dict[str, str]
    sub_intents: List[str] = field(default_factory=list)
    context_requirements: Dict[str, Any] = field(default_factory=dict)


class IntentParser:
    """
    意图解析器 - 支持关键词和 LLM 两种模式

    功能:
    - 基础关键词匹配（无需外部依赖）
    - LLM 增强解析（需要 API）
    - 多意图识别
    - 实体抽取
    """

    _CATEGORY_KEYWORDS = {
        "development": ["code", "script", "api", "refactor", "deploy", "开发", "代码", "编程"],
        "workflow": ["workflow", "pipeline", "automation", "cron", "schedule", "工作流", "自动化"],
        "realestate": ["villa", "residential", "leasing", "commercial", "auction", "房产", "别墅", "住宅"],
        "content": ["article", "copy", "content", "publish", "seo", "文章", "内容", "文案"],
        "ecommerce": ["product", "shop", "order", "shipping", "商品", "电商", "订单"],
        "finance": ["loan", "mortgage", "invest", "贷款", "投资", "理财"],
    }

    def __init__(
        self,
        use_llm: bool = False,
        llm_provider: str = "openai",
        model: str = "gpt-4o-mini"
    ):
        """
        初始化意图解析器

        Args:
            use_llm: 是否使用 LLM 增强解析
            llm_provider: LLM 提供商 ("openai", "anthropic", "minimax")
            model: 模型名称
        """
        self.use_llm = use_llm
        self.llm_provider = llm_provider
        self.model = model

    def _keyword_parse(self, text: str) -> ParsedIntent:
        """基于关键词的解析"""
        text_lower = text.lower().strip()
        category = "general"
        confidence = 0.45

        for candidate, keywords in self._CATEGORY_KEYWORDS.items():
            hits = sum(1 for keyword in keywords if keyword in text_lower)
            if hits:
                category = candidate
                confidence = min(0.6 + hits * 0.1, 0.95)
                break

        goals = [part.strip() for part in text.replace("，", ",").split(",") if part.strip()]

        # 实体抽取
        entities = {}
        if "宁波" in text or "ningbo" in text_lower:
            entities["city"] = "宁波"
        if "上海" in text or "shanghai" in text_lower:
            entities["city"] = "上海"
        if "北京" in text or "beijing" in text_lower:
            entities["city"] = "北京"

        # 检测数字实体
        import re
        numbers = re.findall(r'\d+(?:\.\d+)?', text)
        if numbers:
            entities["numbers"] = numbers

        return ParsedIntent(
            raw_text=text,
            category=category,
            confidence=confidence,
            goals=goals or [text],
            entities=entities,
        )

    def _llm_parse(self, text: str) -> ParsedIntent:
        """基于 LLM 的解析"""
        if self.llm_provider == "openai":
            return self._openai_parse(text)
        elif self.llm_provider == "anthropic":
            return self._anthropic_parse(text)
        elif self.llm_provider == "minimax":
            return self._minimax_parse(text)
        else:
            return self._keyword_parse(text)

    def _openai_parse(self, text: str) -> ParsedIntent:
        """OpenAI API 解析"""
        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

        if not api_key:
            return self._keyword_parse(text)

        prompt = f"""请分析以下用户请求，提取意图信息。

请求: {text}

请以 JSON 格式返回以下字段:
- category: 意图分类 (development/workflow/realestate/content/ecommerce/finance/general)
- confidence: 置信度 (0-1)
- goals: 用户目标列表
- entities: 抽取的实体 (如城市、数字等)
- sub_intents: 子意图列表

只返回 JSON，不要其他内容。"""

        try:
            response = requests.post(
                f"{base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "max_tokens": 500,
                },
                timeout=10
            )

            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]

                import json
                data = json.loads(content)

                return ParsedIntent(
                    raw_text=text,
                    category=data.get("category", "general"),
                    confidence=data.get("confidence", 0.7),
                    goals=data.get("goals", [text]),
                    entities=data.get("entities", {}),
                    sub_intents=data.get("sub_intents", []),
                )
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"LLM parse failed: {e}")

        return self._keyword_parse(text)

    def _anthropic_parse(self, text: str) -> ParsedIntent:
        """Anthropic API 解析"""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        base_url = os.getenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com")

        if not api_key:
            return self._keyword_parse(text)

        prompt = f"""分析以下用户请求:

{text}

返回 JSON 格式:
{{"category": "...", "confidence": 0.0-1.0, "goals": [...], "entities": {{}}}}"""

        try:
            response = requests.post(
                f"{base_url}/v1/messages",
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "max_tokens": 500,
                    "messages": [{"role": "user", "content": prompt}]
                },
                timeout=10
            )

            if response.status_code == 200:
                result = response.json()
                content = result["content"][0]["text"]

                import json
                data = json.loads(content)

                return ParsedIntent(
                    raw_text=text,
                    category=data.get("category", "general"),
                    confidence=data.get("confidence", 0.7),
                    goals=data.get("goals", [text]),
                    entities=data.get("entities", {}),
                )
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Anthropic parse failed: {e}")

        return self._keyword_parse(text)

    def _minimax_parse(self, text: str) -> ParsedIntent:
        """MiniMax API 解析"""
        api_key = os.getenv("MINIMAX_API_KEY")
        group_id = os.getenv("MINIMAX_GROUP_ID")
        base_url = os.getenv("MINIMAX_BASE_URL", "https://api.minimax.chat/v1")

        if not api_key or not group_id:
            return self._keyword_parse(text)

        prompt = f"""分析用户意图:

{text}

返回 JSON (只返回 JSON):
{{"category": "...", "confidence": 0.0-1.0, "goals": [...], "entities": {{}}}}"""

        try:
            response = requests.post(
                f"{base_url}/text/chatcompletion_v2",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}]
                },
                timeout=10
            )

            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]

                import json
                data = json.loads(content)

                return ParsedIntent(
                    raw_text=text,
                    category=data.get("category", "general"),
                    confidence=data.get("confidence", 0.7),
                    goals=data.get("goals", [text]),
                    entities=data.get("entities", {}),
                )
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"MiniMax parse failed: {e}")

        return self._keyword_parse(text)

    def parse(self, text: str) -> ParsedIntent:
        """
        解析用户意图

        Args:
            text: 用户输入

        Returns:
            ParsedIntent: 解析后的意图
        """
        if self.use_llm:
            return self._llm_parse(text)
        else:
            return self._keyword_parse(text)

    def register_category(self, category: str, keywords: List[str]) -> None:
        """
        注册新的意图分类

        Args:
            category: 分类名称
            keywords: 关键词列表
        """
        self._CATEGORY_KEYWORDS[category] = keywords


# 便捷函数
def get_intent_parser(**kwargs) -> IntentParser:
    """获取意图解析器实例"""
    return IntentParser(**kwargs)
