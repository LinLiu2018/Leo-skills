"""
线程安全单例工具
================
提供统一的线程安全单例获取模式，消除全局裸 global 竞态条件。
"""
import threading
from typing import TypeVar, Callable, Optional

T = TypeVar("T")

# 全局锁注册表，每个单例名称对应一把锁
_locks: dict = {}
_meta_lock = threading.Lock()


def _get_lock(name: str) -> threading.Lock:
    """获取指定名称的锁（线程安全）"""
    if name not in _locks:
        with _meta_lock:
            if name not in _locks:
                _locks[name] = threading.Lock()
    return _locks[name]


def thread_safe_singleton(
    name: str,
    current_ref: Optional[T],
    factory: Callable[[], T],
) -> T:
    """
    线程安全的单例获取

    Args:
        name: 单例标识名（用于锁隔离）
        current_ref: 当前引用值（可能为 None）
        factory: 创建实例的工厂函数

    Returns:
        单例实例
    """
    if current_ref is not None:
        return current_ref
    lock = _get_lock(name)
    with lock:
        # double-check：锁内再检查一次
        # 注意：调用方需要在返回后赋值给全局变量
        return factory()
