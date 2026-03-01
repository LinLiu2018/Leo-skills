"""
Delivery layer for Wingman outputs.
"""

from __future__ import annotations

from typing import Any, Dict


def format_delivery(payload: Dict[str, Any], channel: str = "feishu") -> Dict[str, Any]:
    content = payload.get("content") or payload.get("message") or str(payload)
    return {
        "channel": channel,
        "status": "ready",
        "content": content,
        "metadata": payload.get("metadata", {}),
    }


def mark_delivered(delivery: Dict[str, Any]) -> Dict[str, Any]:
    result = dict(delivery)
    result["status"] = "delivered"
    return result
