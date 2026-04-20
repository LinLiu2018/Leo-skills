"""
Leo MCP Resources - MCP 资源定义与管理

提供标准化的 MCP 资源定义和注册机制。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Awaitable

from leo_core.logging import get_logger

logger = get_logger(__name__)


# ============================================================
# 资源类型
# ============================================================

class ResourceType(str, Enum):
    """资源类型"""
    SKILLS = "skills"
    AGENTS = "agents"
    MEMORY = "memory"
    GATEWAY = "gateway"
    USER = "user"
    WORKFLOWS = "workflows"
    CONFIG = "config"


# ============================================================
# 缓存策略
# ============================================================

@dataclass
class CacheStrategy:
    """缓存策略"""
    ttl: int = 300  # 默认5分钟
    cache: bool = True
    max_size: int = 100

    @classmethod
    def default(cls) -> "CacheStrategy":
        return cls(ttl=300, cache=True)


# 预定义缓存策略
CACHE_STRATEGIES: Dict[str, CacheStrategy] = {
    "leo://skills/registry": CacheStrategy(ttl=3600, cache=True),
    "leo://agents/list": CacheStrategy(ttl=3600, cache=True),
    "leo://memory/shared": CacheStrategy(ttl=60, cache=False),  # 频繁变化
    "leo://gateway/status": CacheStrategy(ttl=10, cache=True),
    "leo://user/profile": CacheStrategy(ttl=300, cache=True),
    "leo://workflows/list": CacheStrategy(ttl=600, cache=True),
    "leo://config/current": CacheStrategy(ttl=60, cache=False),
}


# ============================================================
# 资源定义
# ============================================================

@dataclass
class ResourceDefinition:
    """MCP 资源定义"""
    uri: str
    name: str
    description: str
    resource_type: ResourceType
    mime_type: str = "application/json"
    version: str = "1.0.0"
    cache_strategy: CacheStrategy = field(default_factory=CacheStrategy.default)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "uri": self.uri,
            "name": self.name,
            "description": self.description,
            "type": self.resource_type.value,
            "mime_type": self.mime_type,
            "version": self.version,
            "cache_ttl": self.cache_strategy.ttl,
            "cache_enabled": self.cache_strategy.cache,
            "metadata": self.metadata,
        }


# 资源读取器类型
ResourceReader = Callable[[], Awaitable[str]]


# ============================================================
# 资源注册表
# ============================================================

class ResourceRegistry:
    """MCP 资源注册表"""

    def __init__(self):
        self._resources: Dict[str, ResourceDefinition] = {}
        self._readers: Dict[str, ResourceReader] = {}
        self._type_index: Dict[ResourceType, Set[str]] = {}
        self._cache: Dict[str, tuple] = {}  # (data, timestamp)

    def register(
        self,
        definition: ResourceDefinition,
        reader: ResourceReader,
    ) -> None:
        """注册资源"""
        if definition.uri in self._resources:
            logger.warning(f"Resource '{definition.uri}' already registered, overwriting")

        self._resources[definition.uri] = definition
        self._readers[definition.uri] = reader

        # 更新类型索引
        if definition.resource_type not in self._type_index:
            self._type_index[definition.resource_type] = set()
        self._type_index[definition.resource_type].add(definition.uri)

        logger.info(f"Registered MCP resource: {definition.uri}")

    def unregister(self, uri: str) -> bool:
        """注销资源"""
        if uri not in self._resources:
            return False

        resource = self._resources[uri]
        resource_type = resource.resource_type

        del self._resources[uri]
        del self._readers[uri]
        self._type_index[resource_type].discard(uri)
        self._cache.pop(uri, None)

        logger.info(f"Unregistered MCP resource: {uri}")
        return True

    def get(self, uri: str) -> Optional[ResourceDefinition]:
        """获取资源定义"""
        return self._resources.get(uri)

    def get_reader(self, uri: str) -> Optional[ResourceReader]:
        """获取资源读取器"""
        return self._readers.get(uri)

    def list_all(self) -> List[ResourceDefinition]:
        """列出所有资源"""
        return list(self._resources.values())

    def list_by_type(self, resource_type: ResourceType) -> List[ResourceDefinition]:
        """按类型列出资源"""
        uris = self._type_index.get(resource_type, set())
        return [self._resources[uri] for uri in uris if uri in self._resources]

    def get_cached(self, uri: str) -> Optional[str]:
        """获取缓存的资源数据"""
        if uri not in self._resources:
            return None

        strategy = self._resources[uri].cache_strategy
        if not strategy.cache:
            return None

        if uri not in self._cache:
            return None

        data, timestamp = self._cache[uri]
        # 检查是否过期
        age = (datetime.now() - timestamp).total_seconds()
        if age > strategy.ttl:
            del self._cache[uri]
            return None

        return data

    def set_cached(self, uri: str, data: str) -> None:
        """缓存资源数据"""
        if uri not in self._resources:
            return

        strategy = self._resources[uri].cache_strategy
        if not strategy.cache:
            return

        # 检查缓存大小
        if len(self._cache) >= strategy.max_size:
            # 清除最老的缓存
            oldest = min(self._cache.items(), key=lambda x: x[1][1])
            del self._cache[oldest[0]]

        self._cache[uri] = (data, datetime.now())

    def clear_cache(self, uri: Optional[str] = None) -> None:
        """清除缓存"""
        if uri:
            self._cache.pop(uri, None)
        else:
            self._cache.clear()

    def exists(self, uri: str) -> bool:
        """检查资源是否存在"""
        return uri in self._resources


# ============================================================
# 全局注册表
# ============================================================

_resource_registry: Optional[ResourceRegistry] = None


def get_resource_registry() -> ResourceRegistry:
    """获取全局资源注册表"""
    global _resource_registry
    if _resource_registry is None:
        _resource_registry = ResourceRegistry()
    return _resource_registry


# ============================================================
# 内置资源定义
# ============================================================

def get_default_resources() -> List[ResourceDefinition]:
    """获取默认资源定义"""
    return [
        ResourceDefinition(
            uri="leo://skills/registry",
            name="Skill Registry",
            description="所有已注册的 Leo Skills",
            resource_type=ResourceType.SKILLS,
            cache_strategy=CACHE_STRATEGIES["leo://skills/registry"],
        ),
        ResourceDefinition(
            uri="leo://agents/list",
            name="Agent List",
            description="所有可用的 Agents",
            resource_type=ResourceType.AGENTS,
            cache_strategy=CACHE_STRATEGIES["leo://agents/list"],
        ),
        ResourceDefinition(
            uri="leo://memory/shared",
            name="Shared Memory",
            description="共享记忆存储",
            resource_type=ResourceType.MEMORY,
            cache_strategy=CACHE_STRATEGIES["leo://memory/shared"],
        ),
        ResourceDefinition(
            uri="leo://gateway/status",
            name="Gateway Status",
            description="Leo Gateway 运行状态",
            resource_type=ResourceType.GATEWAY,
            cache_strategy=CACHE_STRATEGIES["leo://gateway/status"],
        ),
        ResourceDefinition(
            uri="leo://user/profile",
            name="User Profile",
            description="当前用户画像",
            resource_type=ResourceType.USER,
            cache_strategy=CACHE_STRATEGIES["leo://user/profile"],
        ),
        ResourceDefinition(
            uri="leo://workflows/list",
            name="Workflow List",
            description="所有可用的工作流",
            resource_type=ResourceType.WORKFLOWS,
            cache_strategy=CACHE_STRATEGIES["leo://workflows/list"],
        ),
    ]
