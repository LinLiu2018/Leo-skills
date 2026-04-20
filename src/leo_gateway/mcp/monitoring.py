"""
Leo MCP Monitoring - MCP 监控与指标

提供 MCP 请求监控、性能指标收集功能。
"""

from __future__ import annotations

import time
import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional
from collections import defaultdict
from uuid import uuid4

from leo_core.logging import get_logger

logger = get_logger(__name__)


# ============================================================
# 请求状态
# ============================================================

class RequestStatus(str, Enum):
    """请求状态"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


# ============================================================
# MCP 请求记录
# ============================================================

@dataclass
class MCPRequest:
    """MCP 请求记录"""
    request_id: str
    tool_name: str
    resource_uri: Optional[str]
    start_time: float
    end_time: float = 0
    status: RequestStatus = RequestStatus.PENDING
    error_message: str = ""
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Any = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None

    @property
    def duration(self) -> float:
        """请求耗时（秒）"""
        if self.end_time > 0:
            return self.end_time - self.start_time
        return time.time() - self.start_time

    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_id,
            "tool_name": self.tool_name,
            "resource_uri": self.resource_uri,
            "start_time": datetime.fromtimestamp(self.start_time).isoformat(),
            "end_time": datetime.fromtimestamp(self.end_time).isoformat() if self.end_time else None,
            "duration": self.duration,
            "status": self.status.value,
            "error_message": self.error_message,
            "user_id": self.user_id,
            "session_id": self.session_id,
        }


# ============================================================
# MCP 监控器
# ============================================================

class MCPMonitor:
    """MCP 监控器"""

    def __init__(self, max_records: int = 1000, max_history_hours: int = 24):
        self.max_records = max_records
        self.max_history_hours = max_history_hours
        self._requests: List[MCPRequest] = []
        self._stats: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            "total": 0,
            "success": 0,
            "error": 0,
            "timeout": 0,
            "total_duration": 0.0,
            "min_duration": float("inf"),
            "max_duration": 0.0,
        })
        self._lock = asyncio.Lock()

    def start_request(
        self,
        tool_name: str,
        input_data: Optional[Dict[str, Any]] = None,
        resource_uri: Optional[str] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> MCPRequest:
        """开始记录请求"""
        request = MCPRequest(
            request_id=str(uuid4()),
            tool_name=tool_name,
            resource_uri=resource_uri,
            start_time=time.time(),
            status=RequestStatus.RUNNING,
            input_data=input_data or {},
            user_id=user_id,
            session_id=session_id,
        )
        return request

    def end_request(
        self,
        request: MCPRequest,
        status: RequestStatus,
        error_message: str = "",
        output_data: Any = None,
    ) -> None:
        """结束记录请求"""
        request.end_time = time.time()
        request.status = status
        request.error_message = error_message
        request.output_data = output_data

        # 更新统计
        self._update_stats(request)

        # 保存请求记录
        self._requests.append(request)
        self._trim_history()

    def _update_stats(self, request: MCPRequest) -> None:
        """更新统计信息"""
        tool = request.tool_name or "unknown"
        stats = self._stats[tool]

        stats["total"] += 1

        if request.status == RequestStatus.SUCCESS:
            stats["success"] += 1
        elif request.status == RequestStatus.ERROR:
            stats["error"] += 1
        elif request.status == RequestStatus.TIMEOUT:
            stats["timeout"] += 1

        duration = request.duration
        stats["total_duration"] += duration
        stats["min_duration"] = min(stats["min_duration"], duration)
        stats["max_duration"] = max(stats["max_duration"], duration)

    def _trim_history(self) -> None:
        """修剪历史记录"""
        cutoff_time = time.time() - (self.max_history_hours * 3600)

        # 按时间修剪
        self._requests = [
            r for r in self._requests
            if r.start_time >= cutoff_time
        ]

        # 按数量修剪
        if len(self._requests) > self.max_records:
            self._requests = self._requests[-self.max_records:]

    def get_stats(self, tool_name: Optional[str] = None) -> Dict[str, Any]:
        """获取统计信息"""
        if tool_name:
            stats = self._stats.get(tool_name, {})
            if stats and stats["total"] > 0:
                return {
                    "tool_name": tool_name,
                    "total": stats["total"],
                    "success": stats["success"],
                    "error": stats["error"],
                    "timeout": stats["timeout"],
                    "success_rate": stats["success"] / stats["total"],
                    "avg_duration": stats["total_duration"] / stats["total"],
                    "min_duration": stats["min_duration"] if stats["min_duration"] != float("inf") else 0,
                    "max_duration": stats["max_duration"],
                }
            return {"tool_name": tool_name, "total": 0}

        # 汇总所有
        total = sum(s["total"] for s in self._stats.values())
        success = sum(s["success"] for s in self._stats.values())
        error = sum(s["error"] for s in self._stats.values())
        total_duration = sum(s["total_duration"] for s in self._stats.values())

        return {
            "total_requests": total,
            "total_success": success,
            "total_error": error,
            "overall_success_rate": success / total if total > 0 else 0,
            "avg_duration": total_duration / total if total > 0 else 0,
            "tools": {
                name: {
                    "total": stats["total"],
                    "success": stats["success"],
                    "error": stats["error"],
                    "success_rate": stats["success"] / stats["total"] if stats["total"] > 0 else 0,
                }
                for name, stats in self._stats.items()
            }
        }

    def get_recent_requests(self, limit: int = 50) -> List[Dict[str, Any]]:
        """获取最近的请求记录"""
        return [r.to_dict() for r in self._requests[-limit:]]

    def get_error_requests(self, limit: int = 50) -> List[Dict[str, Any]]:
        """获取错误的请求记录"""
        errors = [r for r in self._requests if r.status == RequestStatus.ERROR]
        return [r.to_dict() for r in errors[-limit:]]

    def clear(self) -> None:
        """清除所有记录"""
        self._requests.clear()
        self._stats.clear()


# ============================================================
# 速率限制器
# ============================================================

@dataclass
class RateLimitConfig:
    """速率限制配置"""
    max_requests: int = 100  # 每窗口最大请求数
    window_seconds: int = 60  # 窗口大小（秒）


class RateLimiter:
    """MCP 速率限制器"""

    def __init__(self, config: Optional[RateLimitConfig] = None):
        self.config = config or RateLimitConfig()
        self._requests: Dict[str, List[float]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def check(self, client_id: str) -> bool:
        """检查是否允许请求"""
        async with self._lock:
            now = time.time()
            window_start = now - self.config.window_seconds

            # 清理过期请求记录
            self._requests[client_id] = [
                t for t in self._requests[client_id]
                if t >= window_start
            ]

            # 检查是否超过限制
            if len(self._requests[client_id]) >= self.config.max_requests:
                return False

            # 记录新请求
            self._requests[client_id].append(now)
            return True

    async def get_remaining(self, client_id: str) -> int:
        """获取剩余请求数"""
        async with self._lock:
            now = time.time()
            window_start = now - self.config.window_seconds

            # 清理过期请求记录
            self._requests[client_id] = [
                t for t in self._requests[client_id]
                if t >= window_start
            ]

            return max(0, self.config.max_requests - len(self._requests[client_id]))

    async def get_reset_time(self, client_id: str) -> float:
        """获取重置时间（秒）"""
        async with self._lock:
            if not self._requests[client_id]:
                return 0

            oldest = min(self._requests[client_id])
            return max(0, oldest + self.config.window_seconds - time.time())


# ============================================================
# 全局实例
# ============================================================

_mcp_monitor: Optional[MCPMonitor] = None
_rate_limiter: Optional[RateLimiter] = None


def get_mcp_monitor() -> MCPMonitor:
    """获取全局 MCP 监控器"""
    global _mcp_monitor
    if _mcp_monitor is None:
        _mcp_monitor = MCPMonitor()
    return _mcp_monitor


def get_rate_limiter() -> RateLimiter:
    """获取全局速率限制器"""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter
