"""
Perception/monitoring layer.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List


@dataclass
class EventRecord:
    ts: str
    event_type: str
    status: str
    latency_ms: int = 0
    detail: Dict[str, str] = field(default_factory=dict)


class SystemMonitor:
    """Collect lightweight runtime signals for strategy decisions."""

    def __init__(self):
        self.events: List[EventRecord] = []

    def record_event(self, event_type: str, status: str, latency_ms: int = 0, detail: Dict[str, str] | None = None) -> None:
        self.events.append(
            EventRecord(
                ts=datetime.now(timezone.utc).isoformat(),
                event_type=event_type,
                status=status,
                latency_ms=latency_ms,
                detail=detail or {},
            )
        )

    def get_metrics(self) -> Dict[str, float]:
        if not self.events:
            return {
                "event_count": 0,
                "error_rate": 0.0,
                "avg_latency_ms": 0.0,
            }

        count = len(self.events)
        errors = sum(1 for event in self.events if event.status != "success")
        avg_latency = sum(event.latency_ms for event in self.events) / count
        return {
            "event_count": float(count),
            "error_rate": errors / count,
            "avg_latency_ms": round(avg_latency, 2),
        }

    def get_breakdown(self) -> Dict[str, int]:
        bucket: Dict[str, int] = defaultdict(int)
        for event in self.events:
            bucket[event.event_type] += 1
        return dict(bucket)
