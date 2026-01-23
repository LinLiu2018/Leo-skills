"""
Leo Skills桥接层
================
连接Subagents和Skills的适配器系统

主要组件:
- SkillAdapter: Skill适配器，将Claude Skills适配为可调用接口
- SkillLoader: Skill加载器，自动发现和加载所有Skills
- SkillExecutor: Skill执行器，执行Skill操作并管理结果

使用示例:
    from leo_subagents.skills_bridge import SkillLoader, SkillExecutor

    # 加载所有Skills
    loader = SkillLoader()
    loader.discover_and_load()

    # 执行Skill
    executor = SkillExecutor(loader)
    result = executor.execute("content-layout-leo-cskill", "layout", content="...")
"""

from .skill_adapter import (
    SkillAdapter,
    SkillMetadata,
    get_skill_adapter,
    clear_adapter_cache
)

from .skill_loader import (
    SkillLoader,
    get_loader,
    load_skill
)

from .skill_executor import (
    SkillExecutor,
    ExecutionResult,
    get_executor,
    execute_skill
)

__version__ = "1.0.0"
__author__ = "Leo Liu"

__all__ = [
    # 适配器
    'SkillAdapter',
    'SkillMetadata',
    'get_skill_adapter',
    'clear_adapter_cache',

    # 加载器
    'SkillLoader',
    'get_loader',
    'load_skill',

    # 执行器
    'SkillExecutor',
    'ExecutionResult',
    'get_executor',
    'execute_skill',
]
