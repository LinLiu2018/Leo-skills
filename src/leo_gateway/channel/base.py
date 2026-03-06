# -*- coding: utf-8 -*-
"""
Channel 通道抽象基类

基于 OpenClaw Channels 架构
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Callable, Awaitable
from dataclasses import dataclass
from enum import Enum

from ..protocol import Message, MessageType, ChannelType


logger = logging.getLogger(__name__)


@dataclass
class ChannelConfig:
    """通道配置"""
    name: str
    channel_type: ChannelType
    enabled: bool = True
    timeout: int = 30
    retry: int = 3
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class Channel(ABC):
    """
    Channel 抽象基类

    所有消息通道必须继承此类并实现抽象方法。
    """

    def __init__(self, config: ChannelConfig):
        self.config = config
        self.name = config.name
        self.channel_type = config.channel_type
        self._connected = False
        self._handlers: Dict[str, Callable[[Message], Awaitable[None]]] = {}
        self._message_queue: asyncio.Queue = asyncio.Queue()

    @abstractmethod
    async def connect(self) -> bool:
        """连接到通道"""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """断开连接"""
        pass

    @abstractmethod
    async def send(self, message: Message) -> bool:
        """发送消息"""
        pass

    @abstractmethod
    async def receive(self) -> Optional[Message]:
        """接收消息"""
        pass

    async def start_listening(self) -> None:
        """开始监听消息"""
        if not self._connected:
            await self.connect()

        while self._connected:
            try:
                message = await self.receive()
                if message:
                    await self._handle_message(message)
            except Exception as e:
                logger.error(f"Error in message loop: {e}")
                await asyncio.sleep(1)

    async def _handle_message(self, message: Message) -> None:
        """处理接收到的消息"""
        # 触发处理器
        for handler in self._handlers.values():
            try:
                await handler(message)
            except Exception as e:
                logger.error(f"Handler error: {e}")

    def register_handler(
        self,
        event: str,
        handler: Callable[[Message], Awaitable[None]]
    ) -> None:
        """注册消息处理器"""
        self._handlers[event] = handler
        logger.debug(f"Handler registered: {self.name}.{event}")

    def unregister_handler(self, event: str) -> None:
        """注销处理器"""
        if event in self._handlers:
            del self._handlers[event]

    def get_status(self) -> Dict[str, Any]:
        """获取通道状态"""
        return {
            "name": self.name,
            "type": self.channel_type.value,
            "connected": self._connected,
            "handlers": list(self._handlers.keys()),
            "queue_size": self._message_queue.qsize(),
        }

    @property
    def is_connected(self) -> bool:
        return self._connected

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name}, connected={self._connected})"


class CLIClannel(Channel):
    """Claude Code CLI 通道"""

    def __init__(self, config: Optional[ChannelConfig] = None):
        super().__init__(config or ChannelConfig(
            name="cli",
            channel_type=ChannelType.CLI
        ))

    async def connect(self) -> bool:
        """连接 CLI"""
        self._connected = True
        logger.info("CLI Channel connected")
        return True

    async def disconnect(self) -> None:
        """断开 CLI"""
        self._connected = False
        logger.info("CLI Channel disconnected")

    async def send(self, message: Message) -> bool:
        """发送消息到 CLI"""
        print(f"[Leo] {message.content}")
        return True

    async def receive(self) -> Optional[Message]:
        """从 CLI 接收消息"""
        # CLI 通道由 Claude Code 主循环驱动
        return None


class MCPChannel(Channel):
    """MCP 协议通道"""

    def __init__(
        self,
        config: ChannelConfig,
        mcp_client: Any = None
    ):
        super().__init__(config)
        self.mcp_client = mcp_client

    async def connect(self) -> bool:
        """连接 MCP 服务器"""
        if self.mcp_client:
            self._connected = True
            logger.info(f"MCP Channel connected: {self.config.name}")
            return True
        return False

    async def disconnect(self) -> None:
        """断开 MCP"""
        self._connected = False
        logger.info(f"MCP Channel disconnected: {self.config.name}")

    async def send(self, message: Message) -> bool:
        """通过 MCP 发送消息"""
        # 实现 MCP 协议发送
        return True

    async def receive(self) -> bool:
        """接收 MCP 消息"""
        # 实现 MCP 协议接收
        return True


class WebhookChannel(Channel):
    """Webhook 通道"""

    def __init__(self, config: ChannelConfig, webhook_url: str = None):
        super().__init__(config)
        self.webhook_url = webhook_url

    async def connect(self) -> bool:
        """Webhook 不需要连接"""
        self._connected = True
        return True

    async def disconnect(self) -> None:
        self._connected = False

    async def send(self, message: Message) -> bool:
        """发送 Webhook"""
        # 实现 Webhook 发送
        return True

    async def receive(self) -> Optional[Message]:
        """接收 Webhook (由外部调用)"""
        return None


class OpenClawChannel(Channel):
    """OpenClaw 通道 (飞书等)"""

    def __init__(
        self,
        config: ChannelConfig,
        openclaw_path: str = "D:/openclaw"
    ):
        super().__init__(config)
        self.openclaw_path = openclaw_path

    async def connect(self) -> bool:
        """连接到 OpenClaw Gateway"""
        # 复用 D:\openclaw 连接
        self._connected = True
        logger.info(f"OpenClaw Channel connected: {self.config.name}")
        return True

    async def disconnect(self) -> None:
        self._connected = False
        logger.info("OpenClaw Channel disconnected")

    async def send(self, message: Message) -> bool:
        """通过 OpenClaw 发送消息"""
        # 调用 OpenClaw API
        return True

    async def receive(self) -> Optional[Message]:
        """接收 OpenClaw 消息"""
        # 监听 OpenClaw 消息
        return None
