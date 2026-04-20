"""
Leo Core Types - 核心类型定义

定义系统中使用的通用类型和接口。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    List,
    Optional,
    TypeVar,
    Union,
    Protocol,
    Sequence,
)

# ============================================================
# 基础类型
# ============================================================

T = TypeVar("T")


class Status(str, Enum):
    """通用状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class EntityStatus(str, Enum):
    """实体状态"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


# ============================================================
# 请求/响应模型
# ============================================================

@dataclass
class BaseRequest:
    """基础请求模型"""
    input: str
    context: Optional[Dict[str, Any]] = None
    parameters: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None
    user_id: Optional[str] = None

    def __post_init__(self):
        self.context = self.context or {}
        self.parameters = self.parameters or {}


@dataclass
class BaseResponse:
    """基础响应模型"""
    output: str
    status: Status
    metadata: Optional[Dict[str, Any]] = None
    artifacts: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "output": self.output,
            "status": self.status.value if isinstance(self.status, Status) else self.status,
            "metadata": self.metadata,
            "artifacts": self.artifacts,
            "error": self.error,
            "timestamp": self.timestamp.isoformat(),
        }


# ============================================================
# Agent 相关类型
# ============================================================

@dataclass
class AgentCapabilities:
    """Agent 能力描述"""
    name: str
    description: str
    version: str = "1.0.0"
    tags: List[str] = field(default_factory=list)
    supported_intents: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "tags": self.tags,
            "supported_intents": self.supported_intents,
            "parameters": self.parameters,
        }


@dataclass
class AgentResult:
    """Agent 执行结果"""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# Skill 相关类型
# ============================================================

@dataclass
class SkillDefinition:
    """Skill 定义"""
    name: str
    description: str
    version: str = "1.0.0"
    category: str = "general"
    tags: List[str] = field(default_factory=list)
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)
    examples: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "category": self.category,
            "tags": self.tags,
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
            "examples": self.examples,
        }


@dataclass
class SkillExecution:
    """Skill 执行上下文"""
    skill_name: str
    parameters: Dict[str, Any]
    context: Dict[str, Any] = field(default_factory=dict)
    session_id: Optional[str] = None
    user_id: Optional[str] = None


@dataclass
class SkillResult:
    """Skill 执行结果"""
    success: bool
    output: Any = None
    error: Optional[str] = None
    execution_time: float = 0.0
    artifacts: List[Dict[str, Any]] = field(default_factory=list)


# ============================================================
# 工作流相关类型
# ============================================================

@dataclass
class WorkflowStep:
    """工作流步骤"""
    id: str
    name: str
    action: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    depends_on: List[str] = field(default_factory=list)
    retry_policy: Optional[Dict[str, Any]] = None


@dataclass
class WorkflowExecution:
    """工作流执行"""
    workflow_id: str
    steps: List[WorkflowStep]
    current_step: Optional[str] = None
    status: Status = Status.PENDING
    results: Dict[str, Any] = field(default_factory=dict)
    errors: Dict[str, str] = field(default_factory=dict)


# ============================================================
# 记忆相关类型
# ============================================================

@dataclass
class MemoryEntry:
    """记忆条目"""
    id: str
    content: str
    type: str = "general"
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    user_id: Optional[str] = None
    session_id: Optional[str] = None


@dataclass
class MemoryQuery:
    """记忆查询"""
    query: str
    limit: int = 10
    tags: Optional[List[str]] = None
    type: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None


# ============================================================
# 事件相关类型
# ============================================================

@dataclass
class Event:
    """事件模型"""
    type: str
    payload: Dict[str, Any]
    source: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# 通用接口
# ============================================================

class Executable(Protocol):
    """可执行接口"""

    async def execute(self, request: BaseRequest) -> BaseResponse:
        """执行方法"""
        ...


class Cacheable(Protocol[T]):
    """可缓存接口"""

    async def get(self, key: str) -> Optional[T:
        """获取缓存"""
        ...

    async def set(self, key: str, value: T, ttl: Optional[int] = None) -> None:
        """设置缓存"""
        ...

    async def delete(self, key: str) -> None:
        """删除缓存"""
        ...


# ============================================================
# 配置类型
# ============================================================

@dataclass
class LLMConfig:
    """LLM 配置"""
    provider: str
    model: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 4096
    timeout: int = 60


@dataclass
class DatabaseConfig:
    """数据库配置"""
    url: str
    pool_size: int = 5
    max_overflow: int = 10
    echo: bool = False


@dataclass
class MCPServerConfig:
    """MCP 服务器配置"""
    host: str = "127.0.0.1"
    port: int = 8080
    log_level: str = "INFO"
    cache_ttl: int = 300
    rate_limit: int = 100


# ============================================================
# 注册表类型
# ============================================================

@dataclass
class RegistryEntry:
    """注册表条目"""
    name: str
    type: str
    version: str
    description: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    registered_at: datetime = field(default_factory=datetime.now)


class Registry:
    """通用注册表"""

    def __init__(self):
        self._entries: Dict[str, RegistryEntry] = {}

    def register(self, entry: RegistryEntry) -> None:
        """注册条目"""
        self._entries[entry.name] = entry

    def get(self, name: str) -> Optional[RegistryEntry]:
        """获取条目"""
        return self._entries.get(name)

    def list(self, type_filter: Optional[str] = None) -> List[RegistryEntry]:
        """列出条目"""
        entries = list(self._entries.values())
        if type_filter:
            entries = [e for e in entries if e.type == type_filter]
        return entries

    def unregister(self, name: str) -> bool:
        """注销条目"""
        if name in self._entries:
            del self._entries[name]
            return True
        return False
