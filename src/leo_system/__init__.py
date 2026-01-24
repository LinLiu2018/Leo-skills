"""
Leo System 核心包
=================
暴露系统单例获取方法和核心类。
"""

from .core import LeoSystem
from .errors import (
    AgentDispatchError,
    AgentError,
    AgentExecutionError,
    AgentNotFoundError,
    ConfigurationError,
    InitializationError,
    LeoError,
    RegistryError,
    SkillError,
    SkillExecutionError,
    SkillLoadError,
    SkillNotFoundError,
    SystemError,
    WorkflowError,
    WorkflowExecutionError,
)
from .logger import get_logger, system_logger
from .metrics import (
    Timer,
    get_metrics,
    get_performance_report,
    measure_time,
    print_performance_report,
    track_time,
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
