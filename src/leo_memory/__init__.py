"""
Leo Memory System
=================
共享记忆和上下文管理系统

新功能 - 全自动记忆：
- 自动记录所有交互
- 跨 Agent 共享记忆
- 主动上下文注入
"""

from .shared_memory import SharedMemory, get_shared_memory, MemoryEntry
from .auto_memory import (
    AutoMemoryManager,
    get_auto_memory,
    auto_record,
    auto_recall,
    get_context
)
from .memory_hooks import (
    MemoryHook,
    AgentMemoryMixin,
    auto_memorize,
    SystemMemoryCapture,
    get_system_capture
)
from .preference_learning import (
    PreferenceLearner,
    get_preference_learner,
    record_positive_feedback,
    record_negative_feedback
)

# 自动初始化（导入时触发）
from . import auto_init

__all__ = [
    # 原有功能
    'SharedMemory', 'get_shared_memory', 'MemoryEntry',
    # 全自动记忆
    'AutoMemoryManager', 'get_auto_memory',
    'auto_record', 'auto_recall', 'get_context',
    # 记忆钩子
    'MemoryHook', 'AgentMemoryMixin', 'auto_memorize',
    'SystemMemoryCapture', 'get_system_capture',
    # 偏好学习
    'PreferenceLearner', 'get_preference_learner',
    'record_positive_feedback', 'record_negative_feedback',
]
