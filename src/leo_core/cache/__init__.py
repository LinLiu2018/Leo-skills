"""
Leo Core Cache - 缓存系统

提供通用缓存功能，支持内存缓存和磁盘缓存。
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, Generic, List, Optional, TypeVar, Union
import pickle
import logging

from leo_core.logging import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


# ============================================================
# 缓存策略配置
# ============================================================

@dataclass
class CacheConfig:
    """缓存配置"""
    default_ttl: int = 3600  # 默认 TTL（秒）
    max_size: int = 1000    # 最大缓存条目数
    cleanup_interval: int = 300  # 清理间隔（秒）
    enable_disk_cache: bool = False  # 是否启用磁盘缓存
    disk_cache_dir: str = ".cache"  # 磁盘缓存目录


# ============================================================
# 缓存条目
# ============================================================

@dataclass
class CacheEntry(Generic[T]):
    """缓存条目"""
    key: str
    value: T
    created_at: float = field(default_factory=time.time)
    expires_at: float = 0
    access_count: int = 0
    last_accessed: float = field(default_factory=time.time)

    def is_expired(self) -> bool:
        """检查是否过期"""
        if self.expires_at <= 0:
            return False
        return time.time() > self.expires_at

    def touch(self) -> None:
        """更新访问时间"""
        self.access_count += 1
        self.last_accessed = time.time()


# ============================================================
# 缓存存储接口
# ============================================================

class CacheStorage(ABC):
    """缓存存储抽象基类"""

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        pass

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """设置缓存"""
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """删除缓存"""
        pass

    @abstractmethod
    async def clear(self) -> None:
        """清空缓存"""
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        pass

    @abstractmethod
    async def cleanup(self) -> int:
        """清理过期缓存"""
        pass


# ============================================================
# 内存缓存
# ============================================================

class MemoryCache(CacheStorage):
    """内存缓存实现"""

    def __init__(self, config: Optional[CacheConfig] = None):
        self.config = config or CacheConfig()
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        async with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return None

            if entry.is_expired():
                del self._cache[key]
                return None

            entry.touch()
            return entry.value

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """设置缓存"""
        async with self._lock:
            # 检查是否需要清理
            if len(self._cache) >= self.config.max_size:
                await self._evict_oldest()

            expires_at = time.time() + (ttl or self.config.default_ttl)
            self._cache[key] = CacheEntry(
                key=key,
                value=value,
                expires_at=expires_at
            )

    async def delete(self, key: str) -> bool:
        """删除缓存"""
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    async def clear(self) -> None:
        """清空缓存"""
        async with self._lock:
            self._cache.clear()

    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        async with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return False
            if entry.is_expired():
                del self._cache[key]
                return False
            return True

    async def cleanup(self) -> int:
        """清理过期缓存"""
        async with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.is_expired()
            ]
            for key in expired_keys:
                del self._cache[key]
            return len(expired_keys)

    async def _evict_oldest(self) -> None:
        """驱逐最老的缓存条目"""
        if not self._cache:
            return

        # 按访问时间排序，删除最老的
        oldest_key = min(
            self._cache.items(),
            key=lambda x: x[1].last_accessed
        )[0]
        del self._cache[oldest_key]

    def size(self) -> int:
        """获取缓存大小"""
        return len(self._cache)

    def keys(self) -> List[str]:
        """获取所有键"""
        return list(self._cache.keys())


# ============================================================
# 磁盘缓存
# ============================================================

class DiskCache(CacheStorage):
    """磁盘缓存实现"""

    def __init__(self, cache_dir: str = ".cache", config: Optional[CacheConfig] = None):
        self.config = config or CacheConfig()
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._lock = asyncio.Lock()
        self._memory_index: Dict[str, float] = {}  # 内存索引

    def _get_file_path(self, key: str) -> Path:
        """获取缓存文件路径"""
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.cache"

    async def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        async with self._lock:
            file_path = self._get_file_path(key)
            if not file_path.exists():
                return None

            try:
                with open(file_path, "rb") as f:
                    data = pickle.load(f)

                # 检查过期
                if data.get("expires_at", 0) > 0 and time.time() > data["expires_at"]:
                    await self.delete(key)
                    return None

                return data.get("value")
            except Exception as e:
                logger.warning(f"Failed to load cache {key}: {e}")
                return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """设置缓存"""
        async with self._lock:
            file_path = self._get_file_path(key)
            expires_at = time.time() + (ttl or self.config.default_ttl)

            data = {
                "key": key,
                "value": value,
                "created_at": time.time(),
                "expires_at": expires_at,
            }

            try:
                with open(file_path, "wb") as f:
                    pickle.dump(data, f)
            except Exception as e:
                logger.warning(f"Failed to save cache {key}: {e}")

    async def delete(self, key: str) -> bool:
        """删除缓存"""
        async with self._lock:
            file_path = self._get_file_path(key)
            if file_path.exists():
                file_path.unlink()
                return True
            return False

    async def clear(self) -> None:
        """清空缓存"""
        async with self._lock:
            for file_path in self.cache_dir.glob("*.cache"):
                file_path.unlink()
            self._memory_index.clear()

    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        file_path = self._get_file_path(key)
        if not file_path.exists():
            return False

        # 检查过期
        try:
            with open(file_path, "rb") as f:
                data = pickle.load(f)
            if data.get("expires_at", 0) > 0 and time.time() > data["expires_at"]:
                await self.delete(key)
                return False
            return True
        except:
            return False

    async def cleanup(self) -> int:
        """清理过期缓存"""
        cleaned = 0
        async with self._lock:
            for file_path in self.cache_dir.glob("*.cache"):
                try:
                    with open(file_path, "rb") as f:
                        data = pickle.load(f)
                    if data.get("expires_at", 0) > 0 and time.time() > data["expires_at"]:
                        file_path.unlink()
                        cleaned += 1
                except:
                    pass
        return cleaned


# ============================================================
# 缓存管理器
# ============================================================

class CacheManager:
    """缓存管理器 - 支持多层缓存"""

    def __init__(self, config: Optional[CacheConfig] = None):
        self.config = config or CacheConfig()
        self._memory = MemoryCache(config)
        self._disk: Optional[DiskCache] = None

        if self.config.enable_disk_cache:
            self._disk = DiskCache(
                cache_dir=self.config.disk_cache_dir,
                config=config
            )

    async def get(self, key: str) -> Optional[Any]:
        """获取缓存（多层）"""
        # 先从内存获取
        value = await self._memory.get(key)
        if value is not None:
            return value

        # 再从磁盘获取
        if self._disk:
            value = await self._disk.get(key)
            if value is not None:
                # 回填内存
                await self._memory.set(key, value)
                return value

        return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """设置缓存（多层）"""
        # 同时设置内存和磁盘
        await self._memory.set(key, value, ttl)
        if self._disk:
            await self._disk.set(key, value, ttl)

    async def delete(self, key: str) -> bool:
        """删除缓存"""
        deleted = False
        if await self._memory.delete(key):
            deleted = True
        if self._disk:
            if await self._disk.delete(key):
                deleted = True
        return deleted

    async def clear(self) -> None:
        """清空缓存"""
        await self._memory.clear()
        if self._disk:
            await self._disk.clear()

    async def cleanup(self) -> int:
        """清理过期缓存"""
        cleaned = await self._memory.cleanup()
        if self._disk:
            cleaned += await self._disk.cleanup()
        return cleaned


# ============================================================
# 缓存装饰器
# ============================================================

def cached(
    ttl: Optional[int] = None,
    key_builder: Optional[Callable[..., str]] = None,
    manager: Optional[CacheManager] = None,
):
    """缓存装饰器

    Usage:
        @cached(ttl=300)
        async def expensive_function(arg1, arg2):
            ...
    """
    _cache_manager = manager or _default_cache_manager

    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # 构建缓存键
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                cache_key = _make_cache_key(func.__module__, func.__name__, args, kwargs)

            # 尝试获取缓存
            cached_value = await _cache_manager.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit: {cache_key}")
                return cached_value

            # 执行函数
            result = await func(*args, **kwargs)

            # 缓存结果
            await _cache_manager.set(cache_key, result, ttl)
            logger.debug(f"Cached: {cache_key}")

            return result

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # 构建缓存键
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                cache_key = _make_cache_key(func.__module__, func.__name__, args, kwargs)

            # 尝试获取缓存
            # 注意：同步版本需要同步获取，这里简化处理
            return func(*args, **kwargs)

        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


def _make_cache_key(module: str, func_name: str, args: tuple, kwargs: dict) -> str:
    """构建缓存键"""
    key_data = {
        "module": module,
        "function": func_name,
        "args": str(args),
        "kwargs": str(sorted(kwargs.items())),
    }
    key_str = json.dumps(key_data, sort_keys=True)
    return hashlib.sha256(key_str.encode()).hexdigest()


# ============================================================
# 全局缓存管理器
# ============================================================

_default_cache_manager: Optional[CacheManager] = None


def get_cache_manager(config: Optional[CacheConfig] = None) -> CacheManager:
    """获取全局缓存管理器"""
    global _default_cache_manager
    if _default_cache_manager is None:
        _default_cache_manager = CacheManager(config)
    return _default_cache_manager


# ============================================================
# LRU 缓存
# ============================================================

class LRUCache(Generic[T]):
    """LRU 缓存实现"""

    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self._cache: Dict[str, T] = {}
        self._access_order: List[str] = []

    def get(self, key: str) -> Optional[T]:
        """获取缓存"""
        if key not in self._cache:
            return None

        # 更新访问顺序
        self._access_order.remove(key)
        self._access_order.append(key)

        return self._cache[key]

    def set(self, key: str, value: T) -> None:
        """设置缓存"""
        if key in self._cache:
            # 更新已有键
            self._access_order.remove(key)
        elif len(self._cache) >= self.max_size:
            # 驱逐最老的
            oldest = self._access_order.pop(0)
            del self._cache[oldest]

        self._cache[key] = value
        self._access_order.append(key)

    def clear(self) -> None:
        """清空缓存"""
        self._cache.clear()
        self._access_order.clear()

    def size(self) -> int:
        return len(self._cache)
