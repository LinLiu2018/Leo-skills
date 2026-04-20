"""
Leo Core - 核心模块

提供系统级的基础设施：类型定义、日志、异常、事件等。
"""

from .types import (
    # 基础类型
    Status,
    EntityStatus,
    # 请求/响应
    BaseRequest,
    BaseResponse,
    # Agent 类型
    AgentCapabilities,
    AgentResult,
    # Skill 类型
    SkillDefinition,
    SkillExecution,
    SkillResult,
    # 工作流类型
    WorkflowStep,
    WorkflowExecution,
    # 记忆类型
    MemoryEntry,
    MemoryQuery,
    # 事件类型
    Event,
    # 配置类型
    LLMConfig,
    DatabaseConfig,
    MCPServerConfig,
    # 注册表
    Registry,
    RegistryEntry,
    # 接口
    Executable,
    Cacheable,
)

from .exceptions import (
    # 错误码
    ErrorCode,
    # 基础异常
    LeoException,
    # Agent 异常
    AgentException,
    AgentNotFoundException,
    AgentExecutionException,
    # Skill 异常
    SkillException,
    SkillNotFoundException,
    SkillExecutionException,
    # Workflow 异常
    WorkflowException,
    WorkflowNotFoundException,
    WorkflowExecutionException,
    # LLM 异常
    LLMException,
    LLMTimeoutException,
    LLMRateLimitException,
    # Memory 异常
    MemoryException,
    MemoryNotFoundException,
    # MCP 异常
    MCPException,
    MCPTooLNotFoundException,
    MCPRateLimitException,
    # 辅助函数
    format_error_response,
    is_retryable_error,
)

from .logging import (
    # 日志管理器
    LogManager,
    LogConfig,
    LogLevel,
    # 便捷函数
    get_logger,
    setup_logging,
    # 装饰器
    log_execution,
    log_async_execution,
    # 上下文日志
    ContextLogger,
    create_context_logger,
)

from .events import (
    # 事件类型
    EventType,
    # 事件模型
    Event,
    # 事件处理器
    EventHandler,
    EventHandlerProtocol,
    # 事件总线
    EventBus,
    # 便捷函数
    get_event_bus,
    publish_event,
    subscribe,
    unsubscribe,
    # 辅助类
    EventSource,
)

__version__ = "2.0.0"

__all__ = [
    # 版本
    "__version__",
    # 类型
    "Status",
    "EntityStatus",
    "BaseRequest",
    "BaseResponse",
    "AgentCapabilities",
    "AgentResult",
    "SkillDefinition",
    "SkillExecution",
    "SkillResult",
    "WorkflowStep",
    "WorkflowExecution",
    "MemoryEntry",
    "MemoryQuery",
    "Event",
    "LLMConfig",
    "DatabaseConfig",
    "MCPServerConfig",
    "Registry",
    "RegistryEntry",
    "Executable",
    "Cacheable",
    # 异常
    "ErrorCode",
    "LeoException",
    "AgentException",
    "AgentNotFoundException",
    "AgentExecutionException",
    "SkillException",
    "SkillNotFoundException",
    "SkillExecutionException",
    "WorkflowException",
    "WorkflowNotFoundException",
    "WorkflowExecutionException",
    "LLMException",
    "LLMTimeoutException",
    "LLMRateLimitException",
    "MemoryException",
    "MemoryNotFoundException",
    "MCPException",
    "MCPTooLNotFoundException",
    "MCPRateLimitException",
    "format_error_response",
    "is_retryable_error",
    # 日志
    "LogManager",
    "LogConfig",
    "LogLevel",
    "get_logger",
    "setup_logging",
    "log_execution",
    "log_async_execution",
    "ContextLogger",
    "create_context_logger",
    # 事件
    "EventType",
    "Event",
    "EventHandler",
    "EventHandlerProtocol",
    "EventBus",
    "get_event_bus",
    "publish_event",
    "subscribe",
    "unsubscribe",
    "EventSource",
]
