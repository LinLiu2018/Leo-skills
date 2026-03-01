"""Trigger primitives for executor-style skills."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class TriggerType(str, Enum):
    """Supported trigger categories."""

    MANUAL = "manual"
    CRON = "cron"
    WEBHOOK = "webhook"
    EVENT = "event"


@dataclass
class TriggerConfig:
    """Single trigger configuration."""

    type: TriggerType
    name: str
    enabled: bool = True
    cron_expr: Optional[str] = None
    timezone: str = "Asia/Shanghai"
    webhook_path: Optional[str] = None
    webhook_method: str = "POST"
    event_name: Optional[str] = None
    payload_template: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class TriggerManager:
    """Stores and resolves trigger configs."""

    def __init__(self) -> None:
        self._triggers: List[TriggerConfig] = []

    @property
    def triggers(self) -> List[TriggerConfig]:
        return list(self._triggers)

    def add_cron_trigger(
        self,
        expr: str,
        tz: str = "Asia/Shanghai",
        name: Optional[str] = None,
        payload_template: Optional[Dict[str, Any]] = None,
    ) -> TriggerConfig:
        trigger = TriggerConfig(
            type=TriggerType.CRON,
            name=name or f"cron:{expr}",
            cron_expr=expr,
            timezone=tz,
            payload_template=payload_template or {},
        )
        self._triggers.append(trigger)
        return trigger

    def add_webhook_trigger(
        self,
        path: str,
        method: str = "POST",
        name: Optional[str] = None,
        payload_template: Optional[Dict[str, Any]] = None,
    ) -> TriggerConfig:
        trigger = TriggerConfig(
            type=TriggerType.WEBHOOK,
            name=name or f"webhook:{path}",
            webhook_path=path,
            webhook_method=method.upper(),
            payload_template=payload_template or {},
        )
        self._triggers.append(trigger)
        return trigger

    def add_event_trigger(
        self,
        event: str,
        name: Optional[str] = None,
        payload_template: Optional[Dict[str, Any]] = None,
    ) -> TriggerConfig:
        trigger = TriggerConfig(
            type=TriggerType.EVENT,
            name=name or f"event:{event}",
            event_name=event,
            payload_template=payload_template or {},
        )
        self._triggers.append(trigger)
        return trigger

    def add_manual_trigger(self, name: str = "manual") -> TriggerConfig:
        trigger = TriggerConfig(type=TriggerType.MANUAL, name=name)
        self._triggers.append(trigger)
        return trigger

    def add_trigger(self, trigger: TriggerConfig) -> TriggerConfig:
        self._triggers.append(trigger)
        return trigger

    def matching(
        self,
        event_type: TriggerType,
        event_name: Optional[str] = None,
        webhook_path: Optional[str] = None,
    ) -> List[TriggerConfig]:
        matches: List[TriggerConfig] = []
        for trigger in self._triggers:
            if not trigger.enabled or trigger.type != event_type:
                continue
            if event_type == TriggerType.EVENT and event_name and trigger.event_name != event_name:
                continue
            if event_type == TriggerType.WEBHOOK and webhook_path and trigger.webhook_path != webhook_path:
                continue
            matches.append(trigger)
        return matches
