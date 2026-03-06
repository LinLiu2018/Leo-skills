# -*- coding: utf-8 -*-
"""
Channel 模块 - 消息通道

基于 OpenClaw Channels 架构
"""

from .base import (
    Channel,
    ChannelConfig,
    ChannelType,
    CLIClannel,
    MCPChannel,
    WebhookChannel,
    OpenClawChannel,
)

__all__ = [
    "Channel",
    "ChannelConfig",
    "ChannelType",
    "CLIClannel",
    "MCPChannel",
    "WebhookChannel",
    "OpenClawChannel",
]
