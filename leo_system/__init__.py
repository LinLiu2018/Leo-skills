"""
Leo System 核心包
=================
暴露系统单例获取方法和核心类。
"""

from .core import LeoSystem
from .logger import get_logger, system_logger
from .errors import (
    LeoError,
    SkillError,
    SkillNotFoundError,
    SkillLoadError,
    SkillExecutionError,
    AgentError,
    AgentNotFoundError,
    AgentDispatchError,
    AgentExecutionError,
    WorkflowError,
    WorkflowExecutionError,
    RegistryError,
    ConfigurationError,
    SystemError,
    InitializationError,
)
from .metrics import (
    get_metrics,
    track_time,
    Timer,
    measure_time,
    get_performance_report,
    print_performance_report,
)

_system_instance = None

def get_system(base_path=None) -> LeoSystem:
    """
    获取 LeoSystem 全局单例
    
    Args:
        base_path: 可选的项目根路径
    
    Returns:
        LeoSystem 实例
    """
    global _system_instance
    if _system_instance is None:
        _system_instance = LeoSystem(base_path)
    return _system_instance
