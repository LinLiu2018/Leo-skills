# -*- coding: utf-8 -*-
"""
消息协议定义

基于 OpenClaw Gateway Protocol
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid


class MessageType(str, Enum):
    """消息类型"""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    FILE = "file"
    BUTTON = "button"
    INTERACTIVE = "interactive"
    SYSTEM = "system"
    REQUEST = "request"
    RESPONSE = "response"


class ChannelType(str, Enum):
    """通道类型"""
    CLI = "cli"           # Claude Code CLI
    MCP = "mcp"          # MCP 协议
    WEB = "web"          # Web UI
    OPENCLAW = "openclaw"  # OpenClaw (飞书等)
    TELEGRAM = "telegram"
    DISCORD = "discord"
    SLACK = "slack"
    WHATSAPP = "whatsapp"
    WEBHOOK = "webhook"


@dataclass
class Message:
    """消息数据模型"""
    content: str
    user_id: str
    session_id: Optional[str] = None
    channel: Optional[str] = None
    message_type: MessageType = MessageType.TEXT
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    attachments: List[Dict[str, Any]] = field(default_factory=list)
    reply_to: Optional[str] = None  # 回复的消息ID

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "message_id": self.message_id,
            "content": self.content,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "channel": self.channel,
            "message_type": self.message_type.value,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
            "attachments": self.attachments,
            "reply_to": self.reply_to,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        """从字典创建"""
        msg = cls(
            content=data.get("content", ""),
            user_id=data.get("user_id", ""),
            session_id=data.get("session_id"),
            channel=data.get("channel"),
            message_type=MessageType(data.get("message_type", "text")),
            message_id=data.get("message_id", str(uuid.uuid4())),
            metadata=data.get("metadata", {}),
            attachments=data.get("attachments", []),
            reply_to=data.get("reply_to"),
        )
        if "timestamp" in data:
            if isinstance(data["timestamp"], str):
                msg.timestamp = datetime.fromisoformat(data["timestamp"])
            else:
                msg.timestamp = data["timestamp"]
        return msg


@dataclass
class User:
    """用户模型"""
    user_id: str
    name: Optional[str] = None
    avatar: Optional[str] = None
    platform: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "name": self.name,
            "avatar": self.avatar,
            "platform": self.platform,
            "metadata": self.metadata,
        }


# 协议常量
PROTOCOL_VERSION = "1.0.0"
DEFAULT_TIMEOUT = 30
MAX_MESSAGE_LENGTH = 10000
