"""
统一请求/响应模型。
"""

from typing import Any, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class LeoRequest(BaseModel):
    """统一请求。"""

    intent: str = Field(..., description="用户意图")
    target: Optional[str] = Field(None, description="目标技能/代理")
    params: dict = Field(default_factory=dict, description="额外参数")
    trace_id: str = Field(default_factory=lambda: str(uuid4())[:8], description="追踪ID")


class LeoResponse(BaseModel):
    """统一响应。"""

    trace_id: str
    status: str
    intent: Optional[str] = None
    target: Optional[str] = None
    data: Any = None
    error_code: Optional[str] = None
    message: str = ""


class ErrorCode:
    E_VALIDATION = "E_VALIDATION"
    E_ROUTE = "E_ROUTE"
    E_SKILL = "E_SKILL"
    E_WORKFLOW = "E_WORKFLOW"
    E_INTERNAL = "E_INTERNAL"

