# -*- coding: utf-8 -*-
"""
告警通知模块

提供多通道告警能力
"""

import json
import requests
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


class AlertLevel(str, Enum):
    """告警级别"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertChannel(str, Enum):
    """告警通道"""
    CONSOLE = "console"
    FEISHU = "feishu"
    EMAIL = "email"
    SLACK = "slack"
    DINGTALK = "dingtalk"
    WEBHOOK = "webhook"


@dataclass
class Alert:
    """告警数据"""
    alert_id: str
    level: AlertLevel
    title: str
    message: str
    source: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    resolved: bool = False
    resolved_at: Optional[datetime] = None

    def to_dict(self) -> Dict:
        return {
            "alert_id": self.alert_id,
            "level": self.level.value,
            "title": self.title,
            "message": self.message,
            "source": self.source,
            "timestamp": self.timestamp.isoformat(),
            "tags": self.tags,
            "metadata": self.metadata,
            "resolved": self.resolved,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None
        }


class AlertChannelBase:
    """告警通道基类"""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}

    def send(self, alert: Alert) -> bool:
        """发送告警"""
        raise NotImplementedError

    def test(self) -> bool:
        """测试通道"""
        raise NotImplementedError


class ConsoleChannel(AlertChannelBase):
    """控制台告警通道"""

    def send(self, alert: Alert) -> bool:
        """发送告警到控制台"""
        level_emoji = {
            AlertLevel.INFO: "ℹ️",
            AlertLevel.WARNING: "⚠️",
            AlertLevel.ERROR: "❌",
            AlertLevel.CRITICAL: "🔴"
        }

        emoji = level_emoji.get(alert.level, "📢")
        print(f"\n{emoji} [{alert.level.value.upper()}] {alert.title}")
        print(f"   {alert.message}")
        if alert.source:
            print(f"   来源: {alert.source}")
        print(f"   时间: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        return True

    def test(self) -> bool:
        print("[Console] Channel test OK")
        return True


class FeishuChannel(AlertChannelBase):
    """飞书告警通道"""

    def send(self, alert: Alert) -> bool:
        """发送告警到飞书"""
        webhook_url = self.config.get("webhook_url")
        if not webhook_url:
            print("[Feishu] No webhook_url configured")
            return False

        # 构建消息
        level_colors = {
            AlertLevel.INFO: "green",
            AlertLevel.WARNING: "orange",
            AlertLevel.ERROR: "red",
            AlertLevel.CRITICAL: "red"
        }

        post_data = {
            "msg_type": "interactive",
            "card": {
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": f"{alert.title}"
                    },
                    "template": level_colors.get(alert.level, "gray")
                },
                "elements": [
                    {
                        "tag": "markdown",
                        "content": alert.message
                    },
                    {
                        "tag": "div",
                        "fields": [
                            {
                                "is_short": True,
                                "text": {
                                    "tag": "lark_md",
                                    "content": f"**级别**: {alert.level.value}"
                                }
                            },
                            {
                                "is_short": True,
                                "text": {
                                    "tag": "lark_md",
                                    "content": f"**来源**: {alert.source}"
                                }
                            }
                        ]
                    },
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": f"**时间**: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
                        }
                    }
                ]
            }
        }

        try:
            response = requests.post(webhook_url, json=post_data, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"[Feishu] Send failed: {e}")
            return False

    def test(self) -> bool:
        """测试飞书通道"""
        webhook_url = self.config.get("webhook_url")
        if not webhook_url:
            return False

        test_alert = Alert(
            alert_id="test",
            level=AlertLevel.INFO,
            title="测试告警",
            message="这是一条测试告警",
            source="AlertManager"
        )
        return self.send(test_alert)


class SlackChannel(AlertChannelBase):
    """Slack告警通道"""

    def send(self, alert: Alert) -> bool:
        """发送告警到Slack"""
        webhook_url = self.config.get("webhook_url")
        if not webhook_url:
            return False

        level_colors = {
            AlertLevel.INFO: "#36a64f",
            AlertLevel.WARNING: "#ff9800",
            AlertLevel.ERROR: "#f44336",
            AlertLevel.CRITICAL: "#d32f2f"
        }

        payload = {
            "attachments": [
                {
                    "color": level_colors.get(alert.level, "#95a5a6"),
                    "title": alert.title,
                    "text": alert.message,
                    "fields": [
                        {"title": "Level", "value": alert.level.value, "short": True},
                        {"title": "Source", "value": alert.source, "short": True}
                    ],
                    "footer": f"Alert ID: {alert.alert_id}",
                    "ts": int(alert.timestamp.timestamp())
                }
            ]
        }

        try:
            response = requests.post(webhook_url, json=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"[Slack] Send failed: {e}")
            return False

    def test(self) -> bool:
        return True


class WebhookChannel(AlertChannelBase):
    """通用Webhook告警通道"""

    def send(self, alert: Alert) -> bool:
        """发送告警到Webhook"""
        webhook_url = self.config.get("webhook_url")
        if not webhook_url:
            return False

        method = self.config.get("method", "POST").upper()
        headers = self.config.get("headers", {"Content-Type": "application/json"})

        payload = alert.to_dict()

        try:
            response = requests.request(
                method=method,
                url=webhook_url,
                json=payload,
                headers=headers,
                timeout=10
            )
            return response.status_code < 400
        except Exception as e:
            print(f"[Webhook] Send failed: {e}")
            return False

    def test(self) -> bool:
        return True


class AlertManager:
    """
    告警管理器

    管理告警规则和发送
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.channels: Dict[AlertChannel, AlertChannelBase] = {}
        self.alerts: List[Alert] = []
        self._alert_id_counter = 0

        # 默认配置
        self._setup_default_channels()

    def _setup_default_channels(self):
        """设置默认通道"""
        # 控制台通道
        self.channels[AlertChannel.CONSOLE] = ConsoleChannel()

        # 飞书通道
        feishu_config = self.config.get("feishu")
        if feishu_config:
            self.channels[AlertChannel.FEISHU] = FeishuChannel(feishu_config)

        # Slack通道
        slack_config = self.config.get("slack")
        if slack_config:
            self.channels[AlertChannel.SLACK] = SlackChannel(slack_config)

        # Webhook通道
        webhook_config = self.config.get("webhook")
        if webhook_config:
            self.channels[AlertChannel.WEBHOOK] = WebhookChannel(webhook_config)

    def register_channel(self, channel: AlertChannel, handler: AlertChannelBase):
        """注册告警通道"""
        self.channels[channel] = handler

    def send_alert(
        self,
        level: AlertLevel,
        title: str,
        message: str,
        source: str = "",
        channels: Optional[List[AlertChannel]] = None,
        tags: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Alert:
        """
        发送告警

        Args:
            level: 告警级别
            title: 告警标题
            message: 告警消息
            source: 告警来源
            channels: 指定发送通道，默认使用所有已配置的通道
            tags: 标签
            metadata: 额外数据

        Returns:
            发送的告警对象
        """
        self._alert_id_counter += 1
        alert = Alert(
            alert_id=f"alert_{self._alert_id_counter}_{int(datetime.now().timestamp())}",
            level=level,
            title=title,
            message=message,
            source=source,
            tags=tags or {},
            metadata=metadata or {}
        )

        # 保存告警
        self.alerts.append(alert)

        # 确定发送通道
        if channels is None:
            channels = list(self.channels.keys())

        # 发送
        for channel in channels:
            handler = self.channels.get(channel)
            if handler:
                try:
                    handler.send(alert)
                except Exception as e:
                    print(f"[AlertManager] Failed to send via {channel}: {e}")

        return alert

    # ========== 便捷方法 ==========

    def info(self, title: str, message: str, **kwargs) -> Alert:
        """发送信息告警"""
        return self.send_alert(AlertLevel.INFO, title, message, **kwargs)

    def warning(self, title: str, message: str, **kwargs) -> Alert:
        """发送警告"""
        return self.send_alert(AlertLevel.WARNING, title, message, **kwargs)

    def error(self, title: str, message: str, **kwargs) -> Alert:
        """发送错误告警"""
        return self.send_alert(AlertLevel.ERROR, title, message, **kwargs)

    def critical(self, title: str, message: str, **kwargs) -> Alert:
        """发送严重告警"""
        return self.send_alert(AlertLevel.CRITICAL, title, message, **kwargs)

    # ========== 查询管理 ==========

    def get_alerts(
        self,
        level: Optional[AlertLevel] = None,
        source: Optional[str] = None,
        unresolved_only: bool = False,
        limit: int = 100
    ) -> List[Alert]:
        """查询告警"""
        results = self.alerts

        if level:
            results = [a for a in results if a.level == level]
        if source:
            results = [a for a in results if a.source == source]
        if unresolved_only:
            results = [a for a in results if not a.resolved]

        return results[-limit:]

    def resolve_alert(self, alert_id: str) -> bool:
        """解除告警"""
        for alert in self.alerts:
            if alert.alert_id == alert_id:
                alert.resolved = True
                alert.resolved_at = datetime.now()
                return True
        return False

    def clear_resolved(self):
        """清除已解除的告警"""
        self.alerts = [a for a in self.alerts if not a.resolved]

    def get_stats(self) -> Dict:
        """获取告警统计"""
        total = len(self.alerts)
        resolved = sum(1 for a in self.alerts if a.resolved)

        by_level = {}
        for level in AlertLevel:
            by_level[level.value] = sum(
                1 for a in self.alerts if a.level == level
            )

        return {
            "total": total,
            "resolved": resolved,
            "unresolved": total - resolved,
            "by_level": by_level
        }

    def test_channels(self) -> Dict[str, bool]:
        """测试所有通道"""
        results = {}
        for channel, handler in self.channels.items():
            try:
                results[channel.value] = handler.test()
            except Exception as e:
                results[channel.value] = False
                print(f"[AlertManager] Test {channel} failed: {e}")
        return results


# 全局告警管理器
_global_alert_manager: Optional[AlertManager] = None


def get_alert_manager() -> AlertManager:
    """获取全局告警管理器"""
    global _global_alert_manager
    if _global_alert_manager is None:
        _global_alert_manager = AlertManager()
    return _global_alert_manager
