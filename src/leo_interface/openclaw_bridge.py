"""
Bridge from local Python services to OpenClaw gateway APIs.
"""

from __future__ import annotations

import os
from typing import Any, Dict, Optional

import requests


class OpenClawBridge:
    """Simple HTTP client for OpenClaw gateway operations."""

    def __init__(self, gateway_url: str = "http://127.0.0.1:18789", token: Optional[str] = None):
        self.gateway_url = gateway_url.rstrip("/")
        self.token = token or os.getenv("OPENCLAW_GATEWAY_TOKEN")

    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _post(self, path: str, payload: Dict[str, Any], timeout: int = 30) -> Dict[str, Any]:
        url = f"{self.gateway_url}{path}"
        response = requests.post(url, json=payload, headers=self._headers(), timeout=timeout)
        return {
            "status_code": response.status_code,
            "ok": response.ok,
            "data": response.json() if response.content else {},
        }

    def healthcheck(self) -> Dict[str, Any]:
        """Check if gateway base endpoint is reachable."""
        url = f"{self.gateway_url}/"
        response = requests.get(url, headers=self._headers(), timeout=15)
        return {"status_code": response.status_code, "ok": response.ok, "url": url}

    def send_to_feishu(self, message: str, channel_id: str = "default") -> Dict[str, Any]:
        """Send a message through Feishu channel via gateway."""
        payload = {"message": message, "channel": channel_id}
        return self._post("/api/channels/feishu/send", payload, timeout=30)

    def trigger_agent(self, agent_name: str, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Trigger an agent execution from gateway."""
        payload = {"task": task, "context": context or {}}
        return self._post(f"/api/agents/{agent_name}/run", payload, timeout=120)
