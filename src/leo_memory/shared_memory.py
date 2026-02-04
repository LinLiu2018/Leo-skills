#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
共享记忆持久化系统
==================
实现跨会话的长期记忆存储和检索

借鉴 OpenClaw 的本地文件持久化机制
"""

import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import threading


@dataclass
class MemoryEntry:
    """记忆条目"""
    key: str
    value: str
    category: str
    importance: int  # 1-5
    created_at: str
    expires_at: Optional[str] = None
    tags: List[str] = None
    context: Dict[str, Any] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.context is None:
            self.context = {}

    def to_dict(self) -> Dict:
        """转换为字典"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'MemoryEntry':
        """从字典创建"""
        return cls(**data)

    def is_expired(self) -> bool:
        """检查是否过期"""
        if self.expires_at is None:
            return False
        return datetime.now().isoformat() > self.expires_at


class SharedMemory:
    """
    共享记忆系统
    ============
    提供长期记忆存储、检索和管理功能
    """

    def __init__(self, memory_file: Optional[str] = None):
        """
        初始化共享记忆

        Args:
            memory_file: 记忆文件路径，默认使用项目目录
        """
        if memory_file is None:
            # 默认路径：项目根目录下的 leo_knowledge/context/shared_memory.md
            base_path = Path(__file__).parent.parent.parent
            self.memory_file = base_path / "leo_knowledge" / "context" / "shared_memory.md"
        else:
            self.memory_file = Path(memory_file)

        self.memory_file.parent.mkdir(parents=True, exist_ok=True)

        # 内存缓存
        self._cache: Dict[str, MemoryEntry] = {}
        self._lock = threading.Lock()

        # 加载已有记忆
        self._load()

    def _load(self):
        """从文件加载记忆"""
        if not self.memory_file.exists():
            return

        try:
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # 解析记忆条目
            entries = self._parse_memory_file(content)

            with self._lock:
                for entry in entries:
                    if not entry.is_expired():
                        self._cache[entry.key] = entry

        except Exception as e:
            print(f"[SharedMemory] 加载记忆失败: {e}")

    def _parse_memory_file(self, content: str) -> List[MemoryEntry]:
        """解析记忆文件内容"""
        entries = []

        # 匹配记忆条目格式：- [category] key: value (timestamp)
        pattern = r'-\s*\[(.*?)\]\s*(.*?):\s*(.*?)\s*\((\d{4}-\d{2}-\d{2}T[^)]+)\)'

        for match in re.finditer(pattern, content):
            category, key, value, timestamp = match.groups()

            entry = MemoryEntry(
                key=key.strip(),
                value=value.strip(),
                category=category.strip(),
                importance=3,
                created_at=timestamp
            )
            entries.append(entry)

        return entries

    def _save(self):
        """保存记忆到文件"""
        try:
            lines = ["# Leo AI System - 共享记忆\n", f"> 最后更新: {datetime.now().isoformat()}\n", ""]

            # 按分类分组
            by_category: Dict[str, List[MemoryEntry]] = {}

            with self._lock:
                for entry in self._cache.values():
                    if entry.is_expired():
                        continue

                    cat = entry.category
                    if cat not in by_category:
                        by_category[cat] = []
                    by_category[cat].append(entry)

            # 生成内容
            for category in sorted(by_category.keys()):
                entries = by_category[category]
                lines.append(f"\n## {category}\n")

                # 按重要性排序
                entries.sort(key=lambda x: x.importance, reverse=True)

                for entry in entries:
                    lines.append(f"- [{entry.category}] {entry.key}: {entry.value} ({entry.created_at})")

                lines.append('')

            # 写入文件
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))

        except Exception as e:
            print(f"[SharedMemory] 保存记忆失败: {e}")

    def remember(self, key: str, value: str, category: str = "general",
                 importance: int = 3, expires_in_days: Optional[int] = None,
                 tags: Optional[List[str]] = None, **context) -> MemoryEntry:
        """
        记住信息

        Args:
            key: 记忆键
            value: 记忆值
            category: 分类
            importance: 重要性 1-5
            expires_in_days: 过期天数
            tags: 标签列表
            **context: 额外上下文

        Returns:
            记忆条目
        """
        expires_at = None
        if expires_in_days:
            expires_at = (datetime.now() + timedelta(days=expires_in_days)).isoformat()

        entry = MemoryEntry(
            key=key,
            value=value,
            category=category,
            importance=importance,
            created_at=datetime.now().isoformat(),
            expires_at=expires_at,
            tags=tags or [],
            context=context
        )

        with self._lock:
            self._cache[key] = entry

        self._save()
        print(f"[SharedMemory] 已记住: [{category}] {key}")

        return entry

    def recall(self, key: str) -> Optional[MemoryEntry]:
        """
        回忆信息

        Args:
            key: 记忆键

        Returns:
            记忆条目或 None
        """
        with self._lock:
            entry = self._cache.get(key)

        if entry and entry.is_expired():
            self.forget(key)
            return None

        return entry

    def search(self, query: str, category: Optional[str] = None) -> List[MemoryEntry]:
        """
        搜索记忆

        Args:
            query: 搜索关键词
            category: 可选的分类过滤

        Returns:
            匹配的记忆条目列表
        """
        results = []
        query_lower = query.lower()

        with self._lock:
            for entry in self._cache.values():
                if entry.is_expired():
                    continue

                if category and entry.category != category:
                    continue

                # 匹配键、值或标签
                if (query_lower in entry.key.lower() or
                    query_lower in entry.value.lower() or
                    any(query_lower in tag.lower() for tag in entry.tags)):
                    results.append(entry)

        # 按重要性排序
        results.sort(key=lambda x: x.importance, reverse=True)

        return results

    def forget(self, key: str) -> bool:
        """
        遗忘信息

        Args:
            key: 记忆键

        Returns:
            是否成功
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                self._save()
                print(f"[SharedMemory] 已遗忘: {key}")
                return True

        return False

    def cleanup_expired(self) -> int:
        """
        清理过期记忆

        Returns:
            清理数量
        """
        expired_keys = []

        with self._lock:
            for key, entry in self._cache.items():
                if entry.is_expired():
                    expired_keys.append(key)

            for key in expired_keys:
                del self._cache[key]

        if expired_keys:
            self._save()
            print(f"[SharedMemory] 已清理 {len(expired_keys)} 个过期记忆")

        return len(expired_keys)

    def get_all(self, category: Optional[str] = None) -> List[MemoryEntry]:
        """
        获取所有记忆

        Args:
            category: 可选的分类过滤

        Returns:
            记忆条目列表
        """
        with self._lock:
            entries = list(self._cache.values())

        if category:
            entries = [e for e in entries if e.category == category]

        # 过滤过期并排序
        entries = [e for e in entries if not e.is_expired()]
        entries.sort(key=lambda x: (x.category, x.importance), reverse=True)

        return entries

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        with self._lock:
            total = len(self._cache)
            expired = sum(1 for e in self._cache.values() if e.is_expired())

            categories = {}
            for entry in self._cache.values():
                cat = entry.category
                if cat not in categories:
                    categories[cat] = 0
                categories[cat] += 1

        return {
            "total_entries": total,
            "expired_entries": expired,
            "active_entries": total - expired,
            "categories": categories,
            "memory_file": str(self.memory_file)
        }


# 全局共享记忆实例
_shared_memory: Optional[SharedMemory] = None


def get_shared_memory(memory_file: Optional[str] = None) -> SharedMemory:
    """获取全局共享记忆实例"""
    global _shared_memory
    if _shared_memory is None:
        _shared_memory = SharedMemory(memory_file)
    return _shared_memory


# ==================== 使用示例 ====================

if __name__ == "__main__":
    # 创建共享记忆实例
    memory = get_shared_memory()

    # 记住信息
    memory.remember(
        key="user_preference",
        value="喜欢简洁的回答",
        category="user_profile",
        importance=4,
        tags=["preference", "style"]
    )

    memory.remember(
        key="project_context",
        value="Leo AI System 优化项目",
        category="project",
        importance=5,
        expires_in_days=30
    )

    # 回忆信息
    entry = memory.recall("user_preference")
    if entry:
        print(f"回忆: {entry.key} = {entry.value}")

    # 搜索记忆
    results = memory.search("优化")
    print(f"搜索结果: {len(results)} 条")

    # 获取统计
    stats = memory.get_stats()
    print(f"统计: {stats}")
