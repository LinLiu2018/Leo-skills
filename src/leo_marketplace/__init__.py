# -*- coding: utf-8 -*-
"""
插件市场模块

功能:
- Skills 发布与发现
- 第三方插件管理
- 插件商店 API
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class PluginStatus(str, Enum):
    """插件状态"""
    DRAFT = "draft"
    PUBLISHED = "published"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class PluginCategory(str, Enum):
    """插件分类"""
    CONTENT = "content"
    REALESTATE = "realestate"
    ECOMMERCE = "ecommerce"
    FINANCE = "finance"
    PRODUCTIVITY = "productivity"
    INTEGRATION = "integration"
    UTILITY = "utility"


@dataclass
class PluginMetadata:
    """插件元数据"""
    name: str
    version: str
    description: str
    author: str
    category: PluginCategory
    tags: List[str] = field(default_factory=list)
    homepage: Optional[str] = None
    repository: Optional[str] = None
    license: str = "MIT"
    dependencies: Dict[str, str] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class Plugin:
    """插件定义"""
    id: str
    metadata: PluginMetadata
    status: PluginStatus = PluginStatus.DRAFT
    downloads: int = 0
    rating: float = 0.0
    reviews: int = 0


class PluginManifest(BaseModel):
    """插件清单"""
    name: str
    version: str
    description: str
    author: str
    category: str
    tags: List[str] = []
    homepage: Optional[str] = None
    repository: Optional[str] = None
    license: str = "MIT"
    dependencies: Dict[str, str] = {}


class PluginPublisher:
    """
    插件发布器

    功能:
    - 验证插件清单
    - 发布插件到市场
    - 版本管理
    """

    def __init__(self, storage_dir: Optional[Path] = None):
        """
        初始化发布器

        Args:
            storage_dir: 插件存储目录
        """
        if storage_dir is None:
            project_root = Path(__file__).parent.parent.parent
            self.storage_dir = project_root / "data" / "marketplace" / "plugins"
        else:
            self.storage_dir = Path(storage_dir)

        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.plugins: Dict[str, Plugin] = {}
        self._load_plugins()

    def _get_plugin_file(self, plugin_id: str) -> Path:
        """获取插件文件路径"""
        return self.storage_dir / f"{plugin_id}.json"

    def _load_plugins(self):
        """加载已发布的插件"""
        for plugin_file in self.storage_dir.glob("*.json"):
            try:
                with open(plugin_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    plugin = Plugin(
                        id=data["id"],
                        metadata=PluginMetadata(**data["metadata"]),
                        status=PluginStatus(data["status"]),
                        downloads=data.get("downloads", 0),
                        rating=data.get("rating", 0.0),
                        reviews=data.get("reviews", 0)
                    )
                    self.plugins[plugin.id] = plugin
            except Exception as e:
                logger.error(f"Failed to load plugin {plugin_file}: {e}")

    def _save_plugin(self, plugin: Plugin):
        """保存插件"""
        data = {
            "id": plugin.id,
            "metadata": {
                "name": plugin.metadata.name,
                "version": plugin.metadata.version,
                "description": plugin.metadata.description,
                "author": plugin.metadata.author,
                "category": plugin.metadata.category.value,
                "tags": plugin.metadata.tags,
                "homepage": plugin.metadata.homepage,
                "repository": plugin.metadata.repository,
                "license": plugin.metadata.license,
                "dependencies": plugin.metadata.dependencies,
                "created_at": plugin.metadata.created_at,
                "updated_at": plugin.metadata.updated_at,
            },
            "status": plugin.status.value,
            "downloads": plugin.downloads,
            "rating": plugin.rating,
            "reviews": plugin.reviews,
        }

        with open(self._get_plugin_file(plugin.id), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def validate_manifest(self, manifest: PluginManifest) -> tuple[bool, Optional[str]]:
        """
        验证插件清单

        Args:
            manifest: 插件清单

        Returns:
            (是否有效, 错误信息)
        """
        if not manifest.name:
            return False, "Plugin name is required"
        if not manifest.version:
            return False, "Plugin version is required"
        if not manifest.author:
            return False, "Plugin author is required"

        # 检查版本格式
        parts = manifest.version.split(".")
        if len(parts) != 3:
            return False, "Version must be in format x.y.z"

        return True, None

    def publish(
        self,
        manifest: PluginManifest,
        status: PluginStatus = PluginStatus.PUBLISHED
    ) -> Plugin:
        """
        发布插件

        Args:
            manifest: 插件清单
            status: 发布状态

        Returns:
            发布的插件
        """
        # 验证清单
        valid, error = self.validate_manifest(manifest)
        if not valid:
            raise ValueError(f"Invalid manifest: {error}")

        # 生成唯一 ID
        plugin_id = hashlib.md5(
            f"{manifest.name}{manifest.version}".encode()
        ).hexdigest()[:12]

        metadata = PluginMetadata(
            name=manifest.name,
            version=manifest.version,
            description=manifest.description,
            author=manifest.author,
            category=PluginCategory(manifest.category),
            tags=manifest.tags,
            homepage=manifest.homepage,
            repository=manifest.repository,
            license=manifest.license,
            dependencies=manifest.dependencies,
        )

        plugin = Plugin(
            id=plugin_id,
            metadata=metadata,
            status=status,
        )

        self.plugins[plugin_id] = plugin
        self._save_plugin(plugin)

        logger.info(f"Published plugin: {manifest.name} v{manifest.version}")
        return plugin

    def unpublish(self, plugin_id: str) -> bool:
        """下架插件"""
        if plugin_id in self.plugins:
            self.plugins[plugin_id].status = PluginStatus.DEPRECATED
            self._save_plugin(self.plugins[plugin_id])
            return True
        return False

    def delete(self, plugin_id: str) -> bool:
        """删除插件"""
        if plugin_id in self.plugins:
            del self.plugins[plugin_id]
            plugin_file = self._get_plugin_file(plugin_id)
            if plugin_file.exists():
                plugin_file.unlink()
            return True
        return False


class PluginDiscovery:
    """
    插件发现

    功能:
    - 搜索插件
    - 按分类浏览
    - 推荐插件
    """

    def __init__(self, publisher: PluginPublisher):
        self.publisher = publisher

    def search(self, query: str, limit: int = 10) -> List[Plugin]:
        """
        搜索插件

        Args:
            query: 搜索关键词
            limit: 返回数量

        Returns:
            匹配的插件列表
        """
        query_lower = query.lower()
        results = []

        for plugin in self.publisher.plugins.values():
            if plugin.status != PluginStatus.PUBLISHED:
                continue

            # 搜索名称、描述、标签
            if (query_lower in plugin.metadata.name.lower() or
                query_lower in plugin.metadata.description.lower() or
                any(query_lower in tag.lower() for tag in plugin.metadata.tags)):
                results.append(plugin)

        results.sort(key=lambda p: p.downloads, reverse=True)
        return results[:limit]

    def list_by_category(
        self,
        category: PluginCategory,
        limit: int = 20
    ) -> List[Plugin]:
        """按分类列出插件"""
        results = [
            p for p in self.publisher.plugins.values()
            if p.status == PluginStatus.PUBLISHED and p.metadata.category == category
        ]
        results.sort(key=lambda p: p.downloads, reverse=True)
        return results[:limit]

    def get_popular(self, limit: int = 10) -> List[Plugin]:
        """获取热门插件"""
        results = [
            p for p in self.publisher.plugins.values()
            if p.status == PluginStatus.PUBLISHED
        ]
        results.sort(key=lambda p: (p.downloads, p.rating), reverse=True)
        return results[:limit]


class PluginLoader:
    """
    插件加载器

    功能:
    - 动态加载插件
    - 管理插件生命周期
    """

    def __init__(self):
        self.loaded_plugins: Dict[str, Any] = {}

    def load_plugin(self, plugin: Plugin) -> bool:
        """
        加载插件

        Args:
            plugin: 插件

        Returns:
            是否加载成功
        """
        try:
            # 动态导入插件模块
            # 这里简化实现，实际需要根据插件类型加载
            self.loaded_plugins[plugin.id] = {
                "metadata": plugin.metadata,
                "instance": None,
            }
            logger.info(f"Loaded plugin: {plugin.metadata.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to load plugin {plugin.id}: {e}")
            return False

    def unload_plugin(self, plugin_id: str) -> bool:
        """卸载插件"""
        if plugin_id in self.loaded_plugins:
            del self.loaded_plugins[plugin_id]
            return True
        return False


# 便捷函数
def get_plugin_publisher() -> PluginPublisher:
    """获取插件发布器"""
    return PluginPublisher()


def get_plugin_discovery() -> PluginDiscovery:
    """获取插件发现器"""
    return PluginDiscovery(PluginPublisher())
