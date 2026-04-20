"""
Leo Core Events - 事件驱动系统

提供事件总线和事件处理机制。
"""

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Awaitable, Callable, Dict, List, Optional, Set, Union
from uuid import uuid4

# ============================================================
# 事件类型
# ============================================================

class EventType(str, Enum):
    """系统事件类型"""

    # Agent 事件
    AGENT_STARTED = "agent.started"
    AGENT_COMPLETED = "agent.completed"
    AGENT_FAILED = "agent.failed"

    # Skill 事件
    SKILL_INVOKED = "skill.invoked"
    SKILL_COMPLETED = "skill.completed"
    SKILL_FAILED = "skill.failed"

    # Workflow 事件
    WORKFLOW_TRIGGERED = "workflow.triggered"
    WORKFLOW_STEP_STARTED = "workflow.step_started"
    WORKFLOW_STEP_COMPLETED = "workflow.step_completed"
    WORKFLOW_COMPLETED = "workflow.completed"
    WORKFLOW_FAILED = "workflow.failed"

    # Memory 事件
    MEMORY_CREATED = "memory.created"
    MEMORY_UPDATED = "memory.updated"
    MEMORY_DELETED = "memory.deleted"
    MEMORY_QUERIED = "memory.queried"

    # 系统事件
    SYSTEM_STARTUP = "system.startup"
    SYSTEM_SHUTDOWN = "system.shutdown"
    SYSTEM_ERROR = "system.error"


# ============================================================
# 事件模型
# ============================================================

@dataclass
class Event:
    """事件基类"""

    id: str = field(default_factory=lambda: str(uuid4()))
    type: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    source: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None

    def __post_init__(self):
        if not self.type:
            raise ValueError("Event type cannot be empty")

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "type": self.type,
            "payload": self.payload,
            "source": self.source,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
            "correlation_id": self.correlation_id,
            "causation_id": self.causation_id,
        }


# ============================================================
# 事件处理器
# ============================================================

EventHandler = Union[Callable[[Event], Awaitable[None]], Callable[[Event], None]]


class EventHandlerProtocol(ABC):
    """事件处理器协议"""

    @abstractmethod
    async def handle(self, event: Event) -> None:
        """处理事件"""
        pass

    @property
    @abstractmethod
    def event_types(self) -> Set[str]:
        """感兴趣的事件类型"""
        pass


# ============================================================
# 事件过滤器
# ============================================================

class EventFilter:
    """事件过滤器"""

    def __init__(
        self,
        event_types: Optional[Set[str]] = None,
        sources: Optional[Set[str]] = None,
        correlation_id: Optional[str] = None,
    ):
        self.event_types = event_types
        self.sources = sources
        self.correlation_id = correlation_id

    def matches(self, event: Event) -> bool:
        """检查事件是否匹配"""
        # 检查事件类型
        if self.event_types and event.type not in self.event_types:
            return False

        # 检查来源
        if self.sources and event.source not in self.sources:
            return False

        # 检查关联ID
        if self.correlation_id and event.correlation_id != self.correlation_id:
            return False

        return True


# ============================================================
# 事件订阅
# ============================================================

@dataclass
class Subscription:
    """事件订阅"""

    id: str = field(default_factory=lambda: str(uuid4()))
    handler: EventHandler = None
    filter: EventFilter = field(default_factory=EventFilter)
    priority: int = 0
    active: bool = True

    def __post_init__(self):
        if self.handler is None:
            raise ValueError("Handler cannot be None")


# ============================================================
# 事件总线
# ============================================================

class EventBus:
    """事件总线 - 事件发布订阅中心"""

    def __init__(self, max_subscribers: int = 1000):
        self._subscriptions: Dict[str, List[Subscription]] = {}
        self._global_subscriptions: List[Subscription] = []
        self._max_subscribers = max_subscribers
        self._event_history: List[Event] = []
        self._max_history = 100

    def subscribe(
        self,
        handler: EventHandler,
        event_types: Optional[Set[str]] = None,
        sources: Optional[Set[str]] = None,
        correlation_id: Optional[str] = None,
        priority: int = 0,
    ) -> str:
        """订阅事件

        Args:
            handler: 事件处理器
            event_types: 感兴趣的事件类型（None 表示所有类型）
            sources: 感兴趣的事件来源（None 表示所有来源）
            correlation_id: 关联ID过滤
            priority: 优先级（数字越大优先级越高）

        Returns:
            订阅ID
        """
        filter = EventFilter(
            event_types=event_types,
            sources=sources,
            correlation_id=correlation_id,
        )
        subscription = Subscription(
            handler=handler,
            filter=filter,
            priority=priority,
        )

        # 根据是否有事件类型过滤分别存储
        if event_types is None:
            self._global_subscriptions.append(subscription)
        else:
            for event_type in event_types:
                if event_type not in self._subscriptions:
                    self._subscriptions[event_type] = []
                self._subscriptions[event_type].append(subscription)

        # 按优先级排序
        self._sort_subscriptions()

        return subscription.id

    def unsubscribe(self, subscription_id: str) -> bool:
        """取消订阅"""
        # 检查全局订阅
        for sub in self._global_subscriptions:
            if sub.id == subscription_id:
                self._global_subscriptions.remove(sub)
                return True

        # 检查类型订阅
        for subs in self._subscriptions.values():
            for sub in subs:
                if sub.id == subscription_id:
                    subs.remove(sub)
                    return True

        return False

    def _sort_subscriptions(self) -> None:
        """按优先级排序订阅"""
        self._global_subscriptions.sort(key=lambda s: s.priority, reverse=True)
        for subs in self._subscriptions.values():
            subs.sort(key=lambda s: s.priority, reverse=True)

    async def publish(self, event: Event) -> List[Any]:
        """发布事件

        Args:
            event: 事件对象

        Returns:
            处理器返回结果列表
        """
        results = []

        # 获取匹配的订阅
        subscriptions = []

        # 添加全局订阅
        subscriptions.extend(self._global_subscriptions)

        # 添加类型特定订阅
        if event.type in self._subscriptions:
            subscriptions.extend(self._subscriptions[event.type])

        # 过滤活跃订阅
        subscriptions = [s for s in subscriptions if s.active]

        # 按优先级排序
        subscriptions.sort(key=lambda s: s.priority, reverse=True)

        # 执行处理器
        for subscription in subscriptions:
            if subscription.filter.matches(event):
                try:
                    result = subscription.handler(event)
                    if asyncio.iscoroutine(result):
                        result = await result
                    results.append(result)
                except Exception as e:
                    # 记录错误但继续处理其他订阅
                    results.append({"error": str(e), "subscription_id": subscription.id})

        # 保存到历史
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history = self._event_history[-self._max_history:]

        return results

    def get_history(
        self,
        event_type: Optional[str] = None,
        limit: int = 100,
    ) -> List[Event]:
        """获取事件历史"""
        history = self._event_history

        if event_type:
            history = [e for e in history if e.type == event_type]

        return history[-limit:]

    def clear_history(self) -> None:
        """清除事件历史"""
        self._event_history.clear()


# ============================================================
# 便捷函数
# ============================================================

# 全局事件总线实例
_event_bus: Optional[EventBus] = None


def get_event_bus() -> EventBus:
    """获取全局事件总线"""
    global _event_bus
    if _event_bus is None:
        _event_bus = EventBus()
    return _event_bus


async def publish_event(
    event_type: str,
    payload: Dict[str, Any],
    source: str = "",
    metadata: Optional[Dict[str, Any]] = None,
) -> Event:
    """便捷的事件发布函数"""
    event = Event(
        type=event_type,
        payload=payload,
        source=source,
        metadata=metadata or {},
    )
    bus = get_event_bus()
    await bus.publish(event)
    return event


def subscribe(
    handler: EventHandler,
    event_types: Optional[Set[str]] = None,
    sources: Optional[Set[str]] = None,
    priority: int = 0,
) -> str:
    """便捷的订阅函数"""
    bus = get_event_bus()
    return bus.subscribe(handler, event_types, sources, priority=priority)


def unsubscribe(subscription_id: str) -> bool:
    """便捷的取消订阅函数"""
    bus = get_event_bus()
    return bus.unsubscribe(subscription_id)


# ============================================================
# 事件辅助类
# ============================================================

class EventSource:
    """事件源辅助类"""

    def __init__(self, name: str, event_bus: Optional[EventBus] = None):
        self.name = name
        self.event_bus = event_bus or get_event_bus()

    async def emit(
        self,
        event_type: str,
        payload: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Event:
        """发出事件"""
        event = Event(
            type=event_type,
            payload=payload,
            source=self.name,
            metadata=metadata or {},
        )
        await self.event_bus.publish(event)
        return event
