# -*- coding: utf-8 -*-
"""
自动记忆初始化
===============
系统启动时自动加载，为所有 Agent 注入记忆能力

无需手动配置，自动完成：
1. 启动记忆管理器
2. 扫描并包装所有 Agent
3. 建立跨 Agent 记忆共享
4. 开始自动记录
"""

import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

# 标记是否已初始化
_auto_memory_initialized = False


def initialize_auto_memory():
    """
    初始化全自动记忆系统

    在系统启动时调用一次
    """
    global _auto_memory_initialized

    if _auto_memory_initialized:
        return

    try:
        # 1. 启动记忆管理器（自动创建实例）
        from .auto_memory import get_auto_memory
        memory = get_auto_memory()

        logger.info("✅ 全自动记忆系统已初始化")

        # 2. 记录系统启动
        memory.auto_record(
            event_type="system_startup",
            content="Leo Wingman 系统启动，记忆系统激活",
            agent="system",
            importance=5,
            tags=["system", "startup"]
        )

        # 3. 尝试包装 Agent（如果已加载）
        _try_wrap_existing_agents()

        _auto_memory_initialized = True

    except Exception as e:
        logger.error(f"❌ 记忆系统初始化失败: {e}")


def _try_wrap_existing_agents():
    """尝试为已加载的 Agent 添加记忆能力"""
    try:
        from .memory_hooks import auto_memorize

        # 检查是否已加载 leo_subagents
        if 'leo_subagents' in sys.modules:
            import leo_subagents.agents as agents_module

            wrapped_count = 0
            for attr_name in dir(agents_module):
                attr = getattr(agents_module, attr_name)
                if (isinstance(attr, type) and
                    hasattr(attr, 'execute') and
                    not attr_name.startswith('_')):
                    try:
                        auto_memorize(attr)
                        wrapped_count += 1
                    except:
                        pass

            if wrapped_count > 0:
                logger.info(f"🔄 已为 {wrapped_count} 个 Agent 启用自动记忆")

    except Exception as e:
        logger.debug(f"Agent 自动包装跳过: {e}")


def inject_memory_to_agent(agent_class):
    """
    为单个 Agent 注入记忆能力

    用于手动启用记忆
    """
    from .memory_hooks import auto_memorize
    return auto_memorize(agent_class)


def get_shared_context(agent_name: str, task: str) -> dict:
    """
    获取共享上下文

    快捷函数，供 Agent 使用
    """
    from .auto_memory import get_auto_memory
    return get_auto_memory().get_context_for_agent(agent_name, task)


# 系统启动时自动初始化
def _auto_init():
    """自动初始化入口"""
    try:
        initialize_auto_memory()
    except:
        pass  # 静默失败，不影响主系统


# 模块导入时自动执行
_auto_init()


__all__ = [
    "initialize_auto_memory",
    "inject_memory_to_agent",
    "get_shared_context"
]
