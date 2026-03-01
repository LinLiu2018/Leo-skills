"""
Task parsing utilities for Wingman.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class ParsedTask:
    raw: str
    intents: List[str]
    priority: str


def parse_task(text: str) -> ParsedTask:
    normalized = text.lower().strip()
    intents: List[str] = []
    if any(k in normalized for k in ["workflow", "pipeline", "cron"]):
        intents.append("automation")
    if any(k in normalized for k in ["agent", "skill", "orchestrator"]):
        intents.append("system")
    if any(k in normalized for k in ["villa", "residential", "commercial", "auction"]):
        intents.append("realestate")
    if not intents:
        intents.append("general")

    priority = "high" if "urgent" in normalized else "normal"
    return ParsedTask(raw=text, intents=intents, priority=priority)


def to_dict(parsed: ParsedTask) -> Dict[str, str]:
    return {
        "raw": parsed.raw,
        "intents": ",".join(parsed.intents),
        "priority": parsed.priority,
    }
