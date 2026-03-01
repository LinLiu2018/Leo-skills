"""
Unified request/response models.
"""

from typing import Any, Optional, Literal
from uuid import uuid4

from pydantic import BaseModel, Field


class LeoRequest(BaseModel):
    """Unified execute request."""

    intent: str = Field(..., description="User intent text")
    mode: Literal["auto", "skill", "agent", "workflow"] = Field("auto", description="Execution mode")
    target: Optional[str] = Field(None, description="Skill/agent/workflow target")
    method: Optional[str] = Field(None, description="Skill method when mode=skill")
    params: dict = Field(default_factory=dict, description="Execution params")
    trace_id: str = Field(default_factory=lambda: str(uuid4())[:8], description="Trace ID")


class LeoResponse(BaseModel):
    """Unified execute response."""

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
