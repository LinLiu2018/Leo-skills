"""
OpenClaw Client - OpenClaw 网关客户端

用于从 Leo System 调用 OpenClaw 的能力。
"""

import os
from typing import Any, Dict, Optional
import aiohttp


class OpenClawClient:
    """OpenClaw Gateway 客户端"""

    def __init__(self, gateway_url: str = "http://127.0.0.1:18789"):
        self.gateway_url = gateway_url
        self.token = self._get_token()

    def _get_token(self) -> str:
        """获取认证 Token"""
        # 从环境变量或配置文件获取
        token = os.getenv("OPENCLAW_TOKEN", "")
        if not token:
            # 尝试从默认位置读取
            token_file = os.path.expanduser("~/.openclaw/token")
            if os.path.exists(token_file):
                with open(token_file, "r") as f:
                    token = f.read().strip()
        return token

    async def send_message(self, channel: str, content: str) -> Dict[str, Any]:
        """发送飞书消息"""
        url = f"{self.gateway_url}/api/message/send"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        payload = {
            "channel": channel,
            "content": content
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as resp:
                return await resp.json()

    async def create_channel(self, name: str, members: list) -> Dict[str, Any]:
        """创建飞书群聊"""
        url = f"{self.gateway_url}/api/channel/create"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        payload = {
            "name": name,
            "members": members
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as resp:
                return await resp.json()

    async def get_channel_info(self, channel: str) -> Dict[str, Any]:
        """获取频道信息"""
        url = f"{self.gateway_url}/api/channel/{channel}"
        headers = {
            "Authorization": f"Bearer {self.token}"
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                return await resp.json()

    async def health_check(self) -> bool:
        """健康检查"""
        url = f"{self.g"
        try:
ateway_url}/health            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                    return resp.status == 200
        except:
            return False


# 全局实例
_openclaw_client: Optional[OpenClawClient] = None


def get_openclaw_client() -> OpenClawClient:
    """获取全局 OpenClaw 客户端"""
    global _openclaw_client
    if _openclaw_client is None:
        _openclaw_client = OpenClawClient()
    return _openclaw_client
