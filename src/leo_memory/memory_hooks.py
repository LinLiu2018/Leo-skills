# -*- coding: utf-8 -*-
"""
记忆钩子系统
============
自动拦截Agent调用，记录记忆并注入上下文

无需修改现有Agent代码，自动实现：
1. 调用前自动获取相关记忆
2. 调用后自动记录结果
3. 错误自动记录
"""

import functools
import logging
from typing import Any, Callable, Dict, Optional
from datetime import datetime

from .auto_memory import get_auto_memory

logger = logging.getLogger(__name__)


class MemoryHook:
    """
    记忆钩子装饰器

    用法：
    @MemoryHook.capture(agent_name="villa_agent")
    def execute(self, task, context=None):
        ...
    """

    @staticmethod
    def capture(agent_name: Optional[str] = None, importance: int = 3):
        """
        捕获装饰器

        自动记录调用前后状态，并注入相关记忆
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # 确定Agent名称
                actual_agent = agent_name
                if actual_agent is None and args:
                    # 尝试从self获取
                    self_obj = args[0]
                    actual_agent = getattr(self_obj, 'name', self_obj.__class__.__name__)

                memory = get_auto_memory()
                task = kwargs.get('task', str(args[1]) if len(args) > 1 else "unknown")

                # 1. 调用前：获取相关记忆
                context = kwargs.get('context', {})
                if isinstance(context, dict):
                    relevant = memory.get_context_for_agent(actual_agent, task)
                    context['_injected_memory'] = relevant
                    kwargs['context'] = context

                # 2. 记录调用开始
                call_id = memory.auto_record(
                    event_type="agent_call_start",
                    content={
                        "function": func.__name__,
                        "task": task,
                        "args": str(args[1:]),
                        "kwargs_keys": list(kwargs.keys())
                    },
                    agent=actual_agent,
                    importance=importance,
                    tags=["agent_call", func.__name__]
                )

                try:
                    # 3. 执行原函数
                    result = func(*args, **kwargs)

                    # 4. 记录成功结果
                    memory.auto_record(
                        event_type="agent_call_success",
                        content={
                            "call_id": call_id,
                            "result_summary": str(result)[:200] if result else "None"
                        },
                        agent=actual_agent,
                        importance=importance,
                        tags=["agent_success", func.__name__]
                    )

                    # 5. 更新上下文链
                    memory.update_context_chain(task, status="completed", result=True)

                    # 6. 在结果中附加记忆引用
                    if isinstance(result, dict):
                        result['_memory_reference'] = {
                            'call_id': call_id,
                            'relevant_memories': relevant.get('relevant_memories', [])[:3]
                        }

                    return result

                except Exception as e:
                    # 7. 记录错误
                    memory.auto_record(
                        event_type="agent_call_error",
                        content={
                            "call_id": call_id,
                            "error": str(e),
                            "error_type": type(e).__name__
                        },
                        agent=actual_agent,
                        importance=5,  # 错误高重要性
                        tags=["agent_error", func.__name__, type(e).__name__]
                    )

                    memory.update_context_chain(task, status="error")
                    raise

            return wrapper
        return decorator


class AgentMemoryMixin:
    """
    Agent记忆混入类

    让Agent自动获得记忆能力
    """

    def __init__(self):
        self._memory = get_auto_memory()
        self._session_memories = []

    def remember(self, key: str, value: Any, importance: int = 3, tags: Optional[list] = None):
        """
        主动记录记忆

        Agent可以调用此方法来记录重要信息
        """
        memory_id = self._memory.auto_record(
            event_type="agent_memory",
            content={"key": key, "value": value},
            agent=getattr(self, 'name', self.__class__.__name__),
            importance=importance,
            tags=tags or ["agent_stored"]
        )
        self._session_memories.append(memory_id)
        return memory_id

    def recall(self, query: str, top_k: int = 5) -> list:
        """
        主动回忆

        获取与当前任务相关的历史记忆
        """
        agent_name = getattr(self, 'name', self.__class__.__name__)
        return self._memory.recall(
            query=query,
            agent=agent_name,
            top_k=top_k
        )

    def get_memory_context(self, task: str) -> Dict:
        """
        获取记忆上下文

        自动获取相关记忆作为上下文
        """
        agent_name = getattr(self, 'name', self.__class__.__name__)
        return self._memory.get_context_for_agent(agent_name, task)

    def learn_from_interaction(self, success: bool, feedback: Optional[str] = None):
        """
        从交互中学习

        记录交互结果用于改进
        """
        agent_name = getattr(self, 'name', self.__class__.__name__)

        if success:
            self._memory.auto_record(
                event_type="positive_feedback",
                content={"feedback": feedback or "Task completed successfully"},
                agent=agent_name,
                importance=4,
                tags=["learning", "positive"]
            )
        else:
            self._memory.auto_record(
                event_type="negative_feedback",
                content={"feedback": feedback or "Task failed"},
                agent=agent_name,
                importance=4,
                tags=["learning", "negative"]
            )


# 自动包装器 - 无需修改现有代码
def auto_memorize(agent_class):
    """
    自动记忆装饰器

    自动为Agent类的execute方法添加记忆功能

    用法：
    @auto_memorize
    class MyAgent:
        def execute(self, task, context=None):
            ...
    """
    original_init = agent_class.__init__
    original_execute = agent_class.execute

    @functools.wraps(original_init)
    def wrapped_init(self, *args, **kwargs):
        # 调用原始初始化
        original_init(self, *args, **kwargs)
        # 添加记忆属性
        self._memory = get_auto_memory()
        self._session_memories = []

    @functools.wraps(original_execute)
    def wrapped_execute(self, task, context=None, **kwargs):
        memory = get_auto_memory()
        agent_name = getattr(self, 'name', agent_class.__name__)

        # 注入记忆上下文
        if context is None:
            context = {}

        if isinstance(context, dict) and '_injected_memory' not in context:
            mem_context = memory.get_context_for_agent(agent_name, task)
            context['_injected_memory'] = mem_context

        # 记录调用
        call_id = memory.auto_record(
            event_type="agent_execute",
            content={"task": task, "context_keys": list(context.keys()) if context else []},
            agent=agent_name,
            importance=3,
            tags=["agent_execute", agent_name]
        )

        try:
            # 调用原始方法
            if context is not None:
                result = original_execute(self, task, context, **kwargs)
            else:
                result = original_execute(self, task, **kwargs)

            # 记录成功
            memory.auto_record(
                event_type="agent_success",
                content={"call_id": call_id, "has_result": result is not None},
                agent=agent_name,
                importance=3,
                tags=["agent_success", agent_name]
            )

            return result

        except Exception as e:
            # 记录错误
            memory.auto_record(
                event_type="agent_error",
                content={"call_id": call_id, "error": str(e)},
                agent=agent_name,
                importance=5,
                tags=["agent_error", agent_name, type(e).__name__]
            )
            raise

    agent_class.__init__ = wrapped_init
    agent_class.execute = wrapped_execute

    # 添加记忆混入方法
    agent_class.remember = AgentMemoryMixin.remember
    agent_class.recall = AgentMemoryMixin.recall
    agent_class.get_memory_context = AgentMemoryMixin.get_memory_context
    agent_class.learn_from_interaction = AgentMemoryMixin.learn_from_interaction

    return agent_class


# 系统级记忆捕获器
class SystemMemoryCapture:
    """
    系统级记忆捕获

    捕获系统级事件（用户输入、工具调用等）
    """

    def __init__(self):
        self.memory = get_auto_memory()

    def capture_user_input(self, user_input: str, source: str = "unknown"):
        """捕获用户输入"""
        return self.memory.auto_record(
            event_type="user_input",
            content=user_input,
            agent="system",
            importance=4,
            tags=["user_input", source],
            context={"source": source}
        )

    def capture_tool_call(self, tool_name: str, params: Dict, result: Any):
        """捕获工具调用"""
        return self.memory.auto_record(
            event_type="tool_call",
            content={
                "tool": tool_name,
                "params": params,
                "result_summary": str(result)[:100]
            },
            agent="system",
            importance=2,
            tags=["tool_call", tool_name]
        )

    def capture_correction(self, original: str, corrected: str, reason: str):
        """捕获用户修正"""
        return self.memory.auto_record(
            event_type="user_correction",
            content={
                "original": original,
                "corrected": corrected,
                "reason": reason
            },
            agent="system",
            importance=5,  # 修正高重要性
            tags=["correction", "learning"]
        )

    def capture_decision(self, decision: str, context: Dict, rationale: str):
        """捕获系统决策"""
        return self.memory.auto_record(
            event_type="system_decision",
            content={
                "decision": decision,
                "rationale": rationale
            },
            agent="system",
            importance=4,
            tags=["decision"],
            context=context
        )


# 全局系统捕获器
_system_capture: Optional[SystemMemoryCapture] = None


def get_system_capture() -> SystemMemoryCapture:
    """获取系统捕获器"""
    global _system_capture
    if _system_capture is None:
        _system_capture = SystemMemoryCapture()
    return _system_capture


__all__ = [
    "MemoryHook",
    "AgentMemoryMixin",
    "auto_memorize",
    "SystemMemoryCapture",
    "get_system_capture"
]
