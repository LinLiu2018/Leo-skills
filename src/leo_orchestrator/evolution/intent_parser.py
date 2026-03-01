"""
Intent parsing layer.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class ParsedIntent:
    raw_text: str
    category: str
    confidence: float
    goals: List[str]
    entities: Dict[str, str]


class IntentParser:
    """Parse natural language requests into structured goals."""

    _CATEGORY_KEYWORDS = {
        "development": ["code", "script", "api", "refactor", "deploy"],
        "workflow": ["workflow", "pipeline", "automation", "cron", "schedule"],
        "realestate": ["villa", "residential", "leasing", "commercial", "auction"],
        "content": ["article", "copy", "content", "publish", "seo"],
    }

    def parse(self, text: str) -> ParsedIntent:
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
        entities = {"city": "ningbo"} if "ningbo" in text_lower else {}

        return ParsedIntent(
            raw_text=text,
            category=category,
            confidence=confidence,
            goals=goals or [text],
            entities=entities,
        )
