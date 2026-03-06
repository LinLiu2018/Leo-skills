# -*- coding: utf-8 -*-
"""
Session 会话管理系统

基于 OpenClaw Session Management
"""

import json
import logging
import uuid
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
import threading


logger = logging.getLogger(__name__)


@dataclass
class Session:
    """会话数据模型"""
    id: str
    user_id: str
    channel: str
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    messages: List[Dict[str, Any]] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    active: bool = True

    # 消息数量限制配置
    MAX_MESSAGES: int = field(default=1000, repr=False)  # 最大消息数
    TRIM_TO: int = field(default=500, repr=False)        # 超出后保留的数量

    def add_message(self, message) -> None:
        """添加消息到会话"""
        msg_dict = message.to_dict() if hasattr(message, 'to_dict') else message
        self.messages.append(msg_dict)

        # 消息数量限制 - 防止内存泄漏和 compaction 失败
        if len(self.messages) > self.MAX_MESSAGES:
            # 保留最近的一半，移除旧的
            self.messages = self.messages[-self.TRIM_TO:]
            logger.info(f"Session {self.id} trimmed to {len(self.messages)} messages")

        self.updated_at = datetime.now()

    def get_messages(self, limit: int = 50) -> List[Dict[str, Any]]:
        """获取最近消息"""
        return self.messages[-limit:]

    def set_context(self, key: str, value: Any) -> None:
        """设置上下文"""
        self.context[key] = value

    def get_context(self, key: str, default: Any = None) -> Any:
        """获取上下文"""
        return self.context.get(key, default)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "channel": self.channel,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "message_count": len(self.messages),
            "messages": self.messages,  # 修复：添加 messages 字段，确保会话历史持久化
            "context": self.context,
            "metadata": self.metadata,
            "active": self.active,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Session":
        """从字典创建"""
        session = cls(
            id=data["id"],
            user_id=data["user_id"],
            channel=data["channel"],
            active=data.get("active", True),
        )
        if "created_at" in data:
            session.created_at = datetime.fromisoformat(data["created_at"])
        if "updated_at" in data:
            session.updated_at = datetime.fromisoformat(data["updated_at"])
        if "messages" in data:
            session.messages = data["messages"]
        if "context" in data:
            session.context = data["context"]
        if "metadata" in data:
            session.metadata = data["metadata"]
        return session


class SessionManager:
    """
    会话管理器

    支持:
    - 内存会话存储
    - 持久化到文件
    - 自动过期清理
    - 线程安全
    """

    def __init__(
        self,
        timeout: int = 3600,
        max_sessions: int = 1000,
        storage_path: Optional[Path] = None
    ):
        self.timeout = timeout
        self.max_sessions = max_sessions
        self.storage_path = storage_path or Path("./data/sessions")

        # 内存存储
        self._sessions: Dict[str, Session] = {}
        self._lock = threading.Lock()

        # 确保存储目录存在
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # 加载已有会话
        self._load_sessions()

        logger.info(f"SessionManager initialized: timeout={timeout}s, max={max_sessions}")

    def get_or_create(
        self,
        channel: str,
        user_id: str,
        session_id: Optional[str] = None
    ) -> Session:
        """
        获取或创建会话

        Args:
            channel: 通道名称
            user_id: 用户ID
            session_id: 会话ID (可选)

        Returns:
            Session 对象
        """
        # 如果提供了 session_id，尝试查找
        if session_id:
            session = self.get(session_id)
            if session and session.active:
                return session

        # 查找现有会话 (同一用户 + 同一通道 + 最近活跃)
        session = self._find_active_session(channel, user_id)
        if session:
            session.updated_at = datetime.now()
            return session

        # 创建新会话
        with self._lock:
            # 检查是否达到上限
            if len(self._sessions) >= self.max_sessions:
                self._cleanup_oldest()

            session = Session(
                id=str(uuid.uuid4()),
                user_id=user_id,
                channel=channel,
            )
            self._sessions[session.id] = session

        logger.debug(f"Session created: {session.id} (user: {user_id}, channel: {channel})")
        return session

    def get(self, session_id: str) -> Optional[Session]:
        """获取会话"""
        return self._sessions.get(session_id)

    def _find_active_session(self, channel: str, user_id: str) -> Optional[Session]:
        """查找活动的会话"""
        now = datetime.now()
        cutoff = now - timedelta(seconds=self.timeout)

        for session in self._sessions.values():
            if (session.channel == channel
                and session.user_id == user_id
                and session.active
                and session.updated_at > cutoff):
                return session
        return None

    def _cleanup_oldest(self) -> None:
        """清理最旧的会话"""
        if not self._sessions:
            return

        # 按更新时间排序
        sorted_sessions = sorted(
            self._sessions.values(),
            key=lambda s: s.updated_at
        )

        # 删除最旧的 10%
        count = max(1, len(sorted_sessions) // 10)
        for session in sorted_sessions[:count]:
            self._save_session(session)
            del self._sessions[session.id]

        logger.info(f"Cleaned up {count} old sessions")

    def _save_session(self, session: Session) -> None:
        """保存单个会话到文件"""
        try:
            filepath = self.storage_path / f"{session.id}.json"
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(session.to_dict(), f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save session {session.id}: {e}")

    def save_all(self) -> None:
        """保存所有会话"""
        with self._lock:
            for session in self._sessions.values():
                self._save_session(session)
        logger.info(f"All sessions saved ({len(self._sessions)})")

    def _load_sessions(self) -> None:
        """从文件加载会话"""
        try:
            for filepath in self.storage_path.glob("*.json"):
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    session = Session.from_dict(data)
                    if session.active:
                        self._sessions[session.id] = session
            logger.info(f"Loaded {len(self._sessions)} sessions from disk")
        except Exception as e:
            logger.error(f"Failed to load sessions: {e}")

    def delete(self, session_id: str) -> bool:
        """删除会话"""
        if session_id in self._sessions:
            session = self._sessions[session_id]
            session.active = False
            self._save_session(session)
            del self._sessions[session_id]
            return True
        return False

    def list_sessions(
        self,
        channel: Optional[str] = None,
        user_id: Optional[str] = None,
        active_only: bool = True
    ) -> List[Session]:
        """列出会话"""
        sessions = list(self._sessions.values())

        if channel:
            sessions = [s for s in sessions if s.channel == channel]
        if user_id:
            sessions = [s for s in sessions if s.user_id == user_id]
        if active_only:
            sessions = [s for s in sessions if s.active]

        return sorted(sessions, key=lambda s: s.updated_at, reverse=True)

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "total": len(self._sessions),
            "active": sum(1 for s in self._sessions.values() if s.active),
            "timeout": self.timeout,
            "max_sessions": self.max_sessions,
        }

    @property
    def active_count(self) -> int:
        return sum(1 for s in self._sessions.values() if s.active)
