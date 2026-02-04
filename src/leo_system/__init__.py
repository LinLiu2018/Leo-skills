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
from .interaction_logger import (
    InteractionLogger,
    get_interaction_logger,
    new_session,
    log_user_input,
    log_system_response,
    log_agent_select,
    log_skill_call,
    log_error,
    LogType,
)
from .skill_usage_stats import (
    SkillUsageTracker,
    get_usage_tracker,
    record_skill_call as record_skill_usage,
    get_skill_report,
    get_optimization_suggestions,
    print_skill_report,
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
