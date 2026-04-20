"""
Leo MCP - Model Context Protocol 集成模块

提供与 Claude Code / OpenClaw 的 MCP 协议集成。

主要组件:
- tools: MCP 工具定义与注册
- resources: MCP 资源定义与管理
- monitoring: MCP 监控与指标

Usage:
    from leo_gateway.mcp import get_tool_registry, get_resource_registry

    # 注册工具
    registry = get_tool_registry()
    tools = registry.list_all()

    # 注册资源
    resource_registry = get_resource_registry()
    resources = resource_registry.list_all()
"""

from __future__ import annotations

# 工具模块
from .tools import (
    ToolCategory,
    ToolDefinition,
    ToolExample,
    ToolRegistry,
    get_tool_registry,
    register_tool,
    SKILL_EXECUTION_SCHEMA,
    AGENT_DELEGATION_SCHEMA,
    MEMORY_STORE_SCHEMA,
    MEMORY_RECALL_SCHEMA,
    FEISHU_SEND_SCHEMA,
    SKILL_SEARCH_SCHEMA,
    STATUS_SCHEMA,
)

# 资源模块
from .resources import (
    ResourceType,
    CacheStrategy,
    ResourceDefinition,
    ResourceRegistry,
    get_resource_registry,
    get_default_resources,
    CACHE_STRATEGIES,
)

# 监控模块
from .monitoring import (
    RequestStatus,
    MCPMonitor,
    RateLimiter,
    RateLimitConfig,
    get_mcp_monitor,
    get_rate_limiter,
)

__version__ = "2.0.0"

__all__ = [
    # 版本
    "__version__",
    # 工具
    "ToolCategory",
    "ToolDefinition",
    "ToolExample",
    "ToolRegistry",
    "get_tool_registry",
    "register_tool",
    "SKILL_EXECUTION_SCHEMA",
    "AGENT_DELEGATION_SCHEMA",
    "MEMORY_STORE_SCHEMA",
    "MEMORY_RECALL_SCHEMA",
    "FEISHU_SEND_SCHEMA",
    "SKILL_SEARCH_SCHEMA",
    "STATUS_SCHEMA",
    # 资源
    "ResourceType",
    "CacheStrategy",
    "ResourceDefinition",
    "ResourceRegistry",
    "get_resource_registry",
    "get_default_resources",
    "CACHE_STRATEGIES",
    # 监控
    "RequestStatus",
    "MCPMonitor",
    "RateLimiter",
    "RateLimitConfig",
    "get_mcp_monitor",
    "get_rate_limiter",
]
