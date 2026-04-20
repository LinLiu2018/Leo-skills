"""
Leo MCP Tools - MCP 工具注册与管理

提供标准化的 MCP 工具定义和注册机制。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Union, Awaitable

from leo_core.logging import get_logger

logger = get_logger(__name__)


# ============================================================
# 工具分类
# ============================================================

class ToolCategory(str, Enum):
    """工具分类"""
    AGENT = "agent"           # Agent 相关
    SKILL = "skill"          # Skill 执行
    MEMORY = "memory"        # 记忆系统
    INTEGRATION = "integration"  # 第三方集成
    SYSTEM = "system"        # 系统操作
    UTILITY = "utility"      # 通用工具


# ============================================================
# 工具定义
# ============================================================

@dataclass
class ToolExample:
    """工具使用示例"""
    input: Dict[str, Any]
    output: str


@dataclass
class ToolDefinition:
    """MCP 工具定义"""
    name: str
    description: str
    category: ToolCategory
    version: str = "1.0.0"
    deprecated: bool = False
    deprecation_message: Optional[str] = None
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)
    examples: List[ToolExample] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "version": self.version,
            "deprecated": self.deprecated,
            "deprecation_message": self.deprecation_message,
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
            "examples": [
                {"input": e.input, "output": e.output}
                for e in self.examples
            ],
            "tags": self.tags,
            "metadata": self.metadata,
        }


# 工具处理器类型
ToolHandler = Callable[..., Awaitable[Dict[str, Any]]]


# ============================================================
# 工具注册表
# ============================================================

class ToolRegistry:
    """MCP 工具注册表"""

    def __init__(self):
        self._tools: Dict[str, ToolDefinition] = {}
        self._handlers: Dict[str, ToolHandler] = {}
        self._category_index: Dict[ToolCategory, Set[str]] = {}

    def register(
        self,
        definition: ToolDefinition,
        handler: ToolHandler,
    ) -> None:
        """注册工具"""
        if definition.name in self._tools:
            logger.warning(f"Tool '{definition.name}' already registered, overwriting")

        self._tools[definition.name] = definition
        self._handlers[definition.name] = handler

        # 更新分类索引
        if definition.category not in self._category_index:
            self._category_index[definition.category] = set()
        self._category_index[definition.category].add(definition.name)

        logger.info(f"Registered MCP tool: {definition.name} (category: {definition.category.value})")

    def unregister(self, name: str) -> bool:
        """注销工具"""
        if name not in self._tools:
            return False

        tool = self._tools[name]
        category = tool.category

        del self._tools[name]
        del self._handlers[name]
        self._category_index[category].discard(name)

        logger.info(f"Unregistered MCP tool: {name}")
        return True

    def get(self, name: str) -> Optional[ToolDefinition]:
        """获取工具定义"""
        return self._tools.get(name)

    def get_handler(self, name: str) -> Optional[ToolHandler]:
        """获取工具处理器"""
        return self._handlers.get(name)

    def list_all(self) -> List[ToolDefinition]:
        """列出所有工具"""
        return list(self._tools.values())

    def list_by_category(self, category: ToolCategory) -> List[ToolDefinition]:
        """按分类列出工具"""
        tool_names = self._category_index.get(category, set())
        return [self._tools[name] for name in tool_names if name in self._tools]

    def list_active(self) -> List[ToolDefinition]:
        """列出所有非弃用的工具"""
        return [t for t in self._tools.values() if not t.deprecated]

    def exists(self, name: str) -> bool:
        """检查工具是否存在"""
        return name in self._tools

    def get_categories(self) -> List[ToolCategory]:
        """获取所有分类"""
        return list(self._category_index.keys())


# ============================================================
# 工具注册装饰器
# ============================================================

def register_tool(
    name: str,
    description: str,
    category: ToolCategory,
    input_schema: Optional[Dict[str, Any]] = None,
    output_schema: Optional[Dict[str, Any]] = None,
    examples: Optional[List[Dict[str, Any]]] = None,
    tags: Optional[List[str]] = None,
    version: str = "1.0.0",
) -> Callable[[ToolHandler], ToolHandler]:
    """工具注册装饰器

    Usage:
        @register_tool(
            name="execute_skill",
            description="执行指定的 Leo Skill",
            category=ToolCategory.SKILL,
            input_schema={...}
        )
        async def execute_skill(skill_name: str, parameters: dict = None):
            ...
    """
    def decorator(handler: ToolHandler) -> ToolHandler:
        # 创建工具定义
        tool_def = ToolDefinition(
            name=name,
            description=description,
            category=category,
            version=version,
            input_schema=input_schema or {},
            output_schema=output_schema or {},
            examples=[
                ToolExample(**ex) for ex in (examples or [])
            ],
            tags=tags or [],
        )

        # 注册到全局注册表
        registry = get_tool_registry()
        registry.register(tool_def, handler)

        return handler

    return decorator


# ============================================================
# 全局注册表
# ============================================================

_tool_registry: Optional[ToolRegistry] = None


def get_tool_registry() -> ToolRegistry:
    """获取全局工具注册表"""
    global _tool_registry
    if _tool_registry is None:
        _tool_registry = ToolRegistry()
    return _tool_registry


# ============================================================
# 内置工具定义
# ============================================================

# Skill 执行工具
SKILL_EXECUTION_SCHEMA = {
    "type": "object",
    "properties": {
        "skill_name": {
            "type": "string",
            "description": "要执行的 Skill 名称"
        },
        "parameters": {
            "type": "object",
            "description": "Skill 执行参数",
            "properties": {}
        },
        "session_id": {
            "type": "string",
            "description": "会话ID（可选）"
        }
    },
    "required": ["skill_name"]
}

# Agent 委托工具
AGENT_DELEGATION_SCHEMA = {
    "type": "object",
    "properties": {
        "agent_name": {
            "type": "string",
            "description": "要委托的 Agent 名称"
        },
        "task": {
            "type": "string",
            "description": "任务描述"
        },
        "context": {
            "type": "object",
            "description": "执行上下文"
        }
    },
    "required": ["agent_name", "task"]
}

# 记忆存储工具
MEMORY_STORE_SCHEMA = {
    "type": "object",
    "properties": {
        "content": {
            "type": "string",
            "description": "要存储的内容"
        },
        "memory_type": {
            "type": "string",
            "description": "记忆类型",
            "enum": ["general", "conversation", "fact", "preference"]
        },
        "tags": {
            "type": "array",
            "items": {"type": "string"},
            "description": "标签"
        },
        "user_id": {
            "type": "string",
            "description": "用户ID"
        }
    },
    "required": ["content"]
}

# 记忆检索工具
MEMORY_RECALL_SCHEMA = {
    "type": "object",
    "properties": {
        "query": {
            "type": "string",
            "description": "检索查询"
        },
        "limit": {
            "type": "integer",
            "description": "返回结果数量",
            "default": 10
        },
        "memory_type": {
            "type": "string",
            "description": "记忆类型过滤"
        },
        "tags": {
            "type": "array",
            "items": {"type": "string"},
            "description": "标签过滤"
        }
    },
    "required": ["query"]
}

# 飞书发送工具
FEISHU_SEND_SCHEMA = {
    "type": "object",
    "properties": {
        "message": {
            "type": "string",
            "description": "消息内容"
        },
        " receivers": {
            "type": "array",
            "items": {"type": "string"},
            "description": "接收者"
        },
        "message_type": {
            "type": "string",
            "enum": ["text", "markdown", "interactive"],
            "default": "text"
        }
    },
    "required": ["message"]
}

# 技能搜索工具
SKILL_SEARCH_SCHEMA = {
    "type": "object",
    "properties": {
        "query": {
            "type": "string",
            "description": "搜索关键词"
        },
        "category": {
            "type": "string",
            "description": "分类过滤"
        },
        "limit": {
            "type": "integer",
            "description": "返回结果数量",
            "default": 10
        }
    },
    "required": ["query"]
}

# 状态获取工具
STATUS_SCHEMA = {
    "type": "object",
    "properties": {
        "component": {
            "type": "string",
            "description": "组件名称",
            "enum": ["gateway", "agents", "skills", "memory", "all"]
        }
    }
}
