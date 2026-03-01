"""
Hook System
===========
基础 Hook 框架 - 用于拦截和监控工具调用

参考 Claude Code 官方最佳实践:
- PreToolUse: 工具调用前拦截
- PostToolUse: 工具调用后拦截
"""

import time
import uuid
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class HookPhase(Enum):
    """Hook 执行阶段"""
    PRE = "pre"       # 工具调用前
    POST = "post"    # 工具调用后


@dataclass
class HookContext:
    """Hook 上下文"""
    session_id: str = ""
    agent_id: str = ""
    parent_tool_use_id: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ToolCallRecord:
    """工具调用记录"""
    tool_id: str = ""
    tool_name: str = ""
    tool_input: Dict[str, Any] = field(default_factory=dict)
    tool_output: Any = None
    phase: HookPhase = HookPhase.PRE
    context: HookContext = field(default_factory=HookContext)
    duration_ms: float = 0.0
    success: bool = True
    error: Optional[str] = None


class HookRegistry:
    """
    Hook 注册中心
    ==============
    管理所有 Pre/Post Hook 的注册和执行
    """

    def __init__(self):
        self._pre_hooks: Dict[str, List[Callable]] = {}   # tool_name -> [hooks]
        self._post_hooks: Dict[str, List[Callable]] = {}  # tool_name -> [hooks]
        self._global_pre_hooks: List[Callable] = []       # 全局 Pre Hook
        self._global_post_hooks: List[Callable] = []      # 全局 Post Hook

    def register_pre_hook(self, tool_name: str, callback: Callable) -> None:
        """注册 Pre Hook - 工具调用前执行"""
        if tool_name not in self._pre_hooks:
            self._pre_hooks[tool_name] = []
        self._pre_hooks[tool_name].append(callback)

    def register_post_hook(self, tool_name: str, callback: Callable) -> None:
        """注册 Post Hook - 工具调用后执行"""
        if tool_name not in self._post_hooks:
            self._post_hooks[tool_name] = []
        self._post_hooks[tool_name].append(callback)

    def register_global_pre_hook(self, callback: Callable) -> None:
        """注册全局 Pre Hook - 所有工具调用前执行"""
        self._global_pre_hooks.append(callback)

    def register_global_post_hook(self, callback: Callable) -> None:
        """注册全局 Post Hook - 所有工具调用后执行"""
        self._global_post_hooks.append(callback)

    def execute_pre_hooks(
        self,
        tool_name: str,
        tool_input: Dict[str, Any],
        context: HookContext
    ) -> Optional[Dict[str, Any]]:
        """执行 Pre Hooks"""
        record = ToolCallRecord(
            tool_id=str(uuid.uuid4()),
            tool_name=tool_name,
            tool_input=tool_input,
            phase=HookPhase.PRE,
            context=context
        )

        # 执行全局 Pre Hooks
        for hook in self._global_pre_hooks:
            result = hook(record)
            if result is not None:
                tool_input = result

        # 执行工具特定的 Pre Hooks
        if tool_name in self._pre_hooks:
            for hook in self._pre_hooks[tool_name]:
                result = hook(record)
                if result is not None:
                    tool_input = result

        return tool_input

    def execute_post_hooks(
        self,
        tool_name: str,
        tool_input: Dict[str, Any],
        tool_output: Any,
        context: HookContext,
        duration_ms: float = 0.0,
        success: bool = True,
        error: Optional[str] = None
    ) -> Any:
        """执行 Post Hooks"""
        record = ToolCallRecord(
            tool_id=str(uuid.uuid4()),
            tool_name=tool_name,
            tool_input=tool_input,
            tool_output=tool_output,
            phase=HookPhase.POST,
            context=context,
            duration_ms=duration_ms,
            success=success,
            error=error
        )

        # 执行全局 Post Hooks
        for hook in self._global_post_hooks:
            result = hook(record)
            if result is not None:
                tool_output = result

        # 执行工具特定的 Post Hooks
        if tool_name in self._post_hooks:
            for hook in self._post_hooks[tool_name]:
                result = hook(record)
                if result is not None:
                    tool_output = result

        return tool_output


# ==================== 全局单例 ====================

_global_hook_registry: Optional[HookRegistry] = None


def get_hook_registry() -> HookRegistry:
    """获取全局 Hook 注册中心"""
    global _global_hook_registry
    if _global_hook_registry is None:
        _global_hook_registry = HookRegistry()
    return _global_hook_registry


# ==================== 便捷装饰器 ====================

def pre_hook(tool_name: str):
    """Pre Hook 装饰器"""
    def decorator(func: Callable):
        registry = get_hook_registry()
        registry.register_pre_hook(tool_name, func)
        return func
    return decorator


def post_hook(tool_name: str):
    """Post Hook 装饰器"""
    def decorator(func: Callable):
        registry = get_hook_registry()
        registry.register_post_hook(tool_name, func)
        return func
    return decorator
