"""Unified executor base for scheduled/triggered/output-enabled skills."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import inspect
from typing import Any, Dict, List, Optional

from .output import OutputManager
from .triggers import TriggerConfig, TriggerManager, TriggerType


@dataclass
class ExecutionContext:
    """Standard execution context for direct/system-triggered skill runs."""

    trigger_type: str = "manual"
    user_id: Optional[str] = None
    query: Optional[str] = None
    params: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "trigger_type": self.trigger_type,
            "user_id": self.user_id,
            "query": self.query,
            "params": dict(self.params),
            "metadata": dict(self.metadata),
        }


class BaseExecutor(ABC):
    """Executor mixin/base for all skills."""

    def __init__(
        self,
        skill_name: Optional[str] = None,
        trigger_manager: Optional[TriggerManager] = None,
        output_manager: Optional[OutputManager] = None,
    ) -> None:
        self.executor_name = skill_name or self.__class__.__name__
        self.schedule: Optional[str] = None
        self.schedule_timezone: str = "Asia/Shanghai"
        self.trigger_manager = trigger_manager or TriggerManager()
        self.output_manager = output_manager or OutputManager()

    def _ensure_executor_state(self) -> None:
        # Supports legacy skills that do not call super().__init__().
        if not hasattr(self, "executor_name"):
            self.executor_name = getattr(self, "name", self.__class__.__name__)
        if not hasattr(self, "schedule"):
            self.schedule = None
        if not hasattr(self, "schedule_timezone"):
            self.schedule_timezone = "Asia/Shanghai"
        if not hasattr(self, "trigger_manager"):
            self.trigger_manager = TriggerManager()
        if not hasattr(self, "output_manager"):
            self.output_manager = OutputManager()

    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """Execute current skill."""

    def setup_schedule(self, schedule: str, timezone: str = "Asia/Shanghai") -> TriggerConfig:
        self._ensure_executor_state()
        self.schedule = schedule
        self.schedule_timezone = timezone
        return self.trigger_manager.add_cron_trigger(
            expr=schedule,
            tz=timezone,
            name=f"{self.executor_name}:schedule",
        )

    def setup_trigger(self, trigger: TriggerConfig) -> TriggerConfig:
        self._ensure_executor_state()
        return self.trigger_manager.add_trigger(trigger)

    def add_event_trigger(self, event: str, name: Optional[str] = None) -> TriggerConfig:
        self._ensure_executor_state()
        return self.trigger_manager.add_event_trigger(event=event, name=name)

    def add_webhook_trigger(
        self,
        path: str,
        method: str = "POST",
        name: Optional[str] = None,
    ) -> TriggerConfig:
        self._ensure_executor_state()
        return self.trigger_manager.add_webhook_trigger(path=path, method=method, name=name)

    def add_manual_trigger(self, name: str = "manual") -> TriggerConfig:
        self._ensure_executor_state()
        return self.trigger_manager.add_manual_trigger(name=name)

    def to_file(self, path: str, fmt: str = "json", append: bool = False) -> None:
        self._ensure_executor_state()
        self.output_manager.to_file(path, fmt=fmt, append=append)

    def to_feishu(
        self,
        webhook: str,
        secret: Optional[str] = None,
        mention_all: bool = False,
    ) -> None:
        self._ensure_executor_state()
        self.output_manager.to_feishu(webhook=webhook, secret=secret, mention_all=mention_all)

    def to_database(self, db_path: str, table: str = "skill_output") -> None:
        self._ensure_executor_state()
        self.output_manager.to_database({"db_path": db_path, "table": table})

    def notify(self, result: Any, context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        self._ensure_executor_state()
        return self.output_manager.dispatch(
            result=result,
            context=context or {},
            skill_name=getattr(self, "name", self.executor_name),
        )

    def run(
        self,
        context: Optional[Dict[str, Any]] = None,
        auto_notify: bool = True,
        **kwargs,
    ) -> Any:
        self._ensure_executor_state()
        result = self._invoke_execute(context=context, **kwargs)
        if auto_notify:
            self.notify(result, context=context)
        return result

    def trigger(
        self,
        event_type: TriggerType,
        event_name: Optional[str] = None,
        webhook_path: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
        auto_notify: bool = True,
        **kwargs,
    ) -> Dict[str, Any]:
        self._ensure_executor_state()
        matched = self.trigger_manager.matching(
            event_type=event_type,
            event_name=event_name,
            webhook_path=webhook_path,
        )
        if not matched:
            return {"triggered": False, "reason": "no_matching_trigger"}

        context = payload or {}
        result = self.run(context=context, auto_notify=auto_notify, **kwargs)
        return {
            "triggered": True,
            "matched": [item.name for item in matched],
            "result": result,
        }

    def _invoke_execute(self, context: Optional[Dict[str, Any]] = None, **kwargs) -> Any:
        execute = getattr(self, "execute")
        signature = inspect.signature(execute)

        if "context" in signature.parameters:
            return execute(context=context or {}, **kwargs)

        if context is None:
            return execute(**kwargs)

        if isinstance(context, dict):
            merged = dict(context)
            merged.update(kwargs)
            try:
                return execute(**merged)
            except TypeError:
                return execute(context, **kwargs)

        return execute(context, **kwargs)
