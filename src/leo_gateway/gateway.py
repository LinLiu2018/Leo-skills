# -*- coding: utf-8 -*-
"""
Leo Gateway - 消息网关主类

基于 OpenClaw Gateway 架构:
- 单一事实来源
- 消息路由
- 会话管理
- 多通道支持
"""

import asyncio
import logging
from typing import Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime

from .router import MessageRouter, SmartRouter, create_smart_router
from .session import SessionManager
from .channel.base import Channel, Message, MessageType

# 导入交互日志记录器
try:
    from leo_system import get_interaction_logger
    INTERACTION_LOGGER_AVAILABLE = True
except ImportError:
    INTERACTION_LOGGER_AVAILABLE = False
    get_interaction_logger = None


logger = logging.getLogger(__name__)


@dataclass
class GatewayConfig:
    """Gateway 配置"""
    host: str = "127.0.0.1"
    port: int = 18789
    debug: bool = False
    session_timeout: int = 3600  # 秒
    max_sessions: int = 1000
    enable_openclaw: bool = True
    openclaw_path: str = "D:/openclaw"

    # SmartRouter 配置
    use_smart_router: bool = True  # 启用与 Registry 联动的智能路由
    auto_sync_registry: bool = True  # 自动同步 Registry
    registry_sync_interval: int = 60  # Registry 同步间隔(秒)


class Gateway:
    """
    Leo Gateway - 消息网关主类

    单一事实来源，管理所有消息通道、会话和路由。
    支持 SmartRouter 与 UnifiedRegistry 联动。
    """

    def __init__(self, config: Optional[GatewayConfig] = None):
        self.config = config or GatewayConfig()

        # 初始化路由器 (SmartRouter 或普通 Router)
        if self.config.use_smart_router:
            self.router = create_smart_router()
            if hasattr(self.router, 'set_sync_interval'):
                self.router.set_sync_interval(self.config.registry_sync_interval)
            logger.info("Gateway using SmartRouter with Registry sync")
        else:
            self.router = MessageRouter()
            logger.info("Gateway using standard MessageRouter")

        self.session_mgr = SessionManager(
            timeout=self.config.session_timeout,
            max_sessions=self.config.max_sessions
        )
        self.channels: Dict[str, Channel] = {}
        self._running = False

        logger.info(f"Gateway initialized on {self.config.host}:{self.config.port}")

    def register_channel(self, channel: Channel) -> None:
        """注册消息通道"""
        self.channels[channel.name] = channel
        logger.info(f"Channel registered: {channel.name} ({channel.channel_type})")

    def unregister_channel(self, name: str) -> None:
        """注销消息通道"""
        if name in self.channels:
            del self.channels[name]
            logger.info(f"Channel unregistered: {name}")

    async def handle_message(
        self,
        channel_name: str,
        message: Message,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[Message]:
        """
        处理接收到的消息

        Args:
            channel_name: 通道名称
            message: 消息对象
            context: 额外上下文

        Returns:
            响应消息
        """
        import time
        start_time = time.time()

        # 0. 记录用户输入
        if INTERACTION_LOGGER_AVAILABLE:
            try:
                ilogger = get_interaction_logger(session_id=session.id if hasattr(self, 'session_mgr') else None)
                ilogger.log_user_input(
                    user_input=message.content,
                    context={
                        "channel": channel_name,
                        "user_id": message.user_id,
                        "message_type": message.message_type.value if hasattr(message, 'message_type') else "unknown",
                    }
                )
            except Exception as e:
                logger.warning(f"Failed to log user input: {e}")

        # 1. 获取或创建会话
        session = self.session_mgr.get_or_create(
            channel=channel_name,
            user_id=message.user_id,
            session_id=message.session_id
        )

        # 2. 路由消息
        route = await self.router.route(message, session, context or {})

        # 记录 Agent 选择
        if INTERACTION_LOGGER_AVAILABLE:
            try:
                ilogger = get_interaction_logger(session_id=session.id)
                ilogger.log_agent_select(
                    task=message.content[:200],
                    selected_agent=route.target,
                    confidence=route.confidence,
                    candidates=route.params.get("candidates", [])
                )
            except Exception as e:
                logger.warning(f"Failed to log agent select: {e}")

        # 3. 构建响应
        response = Message(
            content=route.get("response", ""),
            user_id=message.user_id,
            session_id=session.id,
            channel=channel_name,
            message_type=MessageType.RESPONSE
        )

        # 记录系统响应
        if INTERACTION_LOGGER_AVAILABLE:
            try:
                ilogger = get_interaction_logger(session_id=session.id)
                ilogger.log_system_response(
                    response=response.content,
                    response_type="text",
                    related_input_id=None
                )
                # 记录 Agent 执行结果
                ilogger.log_agent_execute(
                    agent_name=route.target,
                    action="handle_message",
                    params={"channel": channel_name},
                    result={"response_length": len(response.content)},
                    success=True,
                    execution_time=time.time() - start_time
                )
            except Exception as e:
                logger.warning(f"Failed to log response: {e}")

        # 4. 更新会话
        session.add_message(message)
        session.add_message(response)

        return response

    async def send_to_channel(
        self,
        channel_name: str,
        message: Message
    ) -> bool:
        """发送消息到指定通道"""
        channel = self.channels.get(channel_name)
        if not channel:
            logger.error(f"Channel not found: {channel_name}")
            return False

        try:
            await channel.send(message)
            return True
        except Exception as e:
            logger.error(f"Failed to send to channel {channel_name}: {e}")
            return False

    async def start(self) -> None:
        """启动 Gateway"""
        self._running = True
        logger.info("Gateway started")

        # 启动所有通道
        for channel in self.channels.values():
            try:
                await channel.connect()
            except Exception as e:
                logger.error(f"Failed to connect channel {channel.name}: {e}")

    async def stop(self) -> None:
        """停止 Gateway"""
        self._running = False
        logger.info("Gateway stopping")

        # 停止所有通道
        for channel in self.channels.values():
            try:
                await channel.disconnect()
            except Exception as e:
                logger.error(f"Failed to disconnect channel {channel.name}: {e}")

        # 保存会话
        self.session_mgr.save_all()

        logger.info("Gateway stopped")

    def get_status(self) -> Dict[str, Any]:
        """获取 Gateway 状态"""
        status = {
            "running": self._running,
            "config": {
                "host": self.config.host,
                "port": self.config.port,
                "use_smart_router": self.config.use_smart_router,
            },
            "channels": {
                name: ch.get_status()
                for name, ch in self.channels.items()
            },
            "sessions": self.session_mgr.get_stats(),
            "router": self.router.get_stats(),
        }

        # 添加 SmartRouter 特有状态
        if isinstance(self.router, SmartRouter):
            status["router"]["registry"] = self.router.get_registry_stats()

        return status

    def __repr__(self) -> str:
        return f"Gateway(channels={len(self.channels)}, sessions={self.session_mgr.active_count})"


# 全局 Gateway 实例
_gateway: Optional[Gateway] = None


def get_gateway(config: Optional[GatewayConfig] = None) -> Gateway:
    """获取全局 Gateway 实例"""
    global _gateway
    if _gateway is None:
        _gateway = Gateway(config)
    return _gateway
