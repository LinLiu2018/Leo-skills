# -*- coding: utf-8 -*-
"""
Leo Gateway - 消息网关系统

基于 OpenClaw Gateway 架构 + Claude Code 最佳实践

模块:
    - gateway: Gateway 主类
    - router: 消息路由
    - session: 会话管理
    - channel: 通道抽象
    - protocol: 消息协议
"""

from .gateway import Gateway
from .router import MessageRouter
from .session import Session, SessionManager

__version__ = "1.0.0"
__all__ = [
    "Gateway",
    "MessageRouter",
    "Session",
    "SessionManager",
]
