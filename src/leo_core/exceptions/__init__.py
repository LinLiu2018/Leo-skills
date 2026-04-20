"""
Leo Core Exceptions - 标准化异常处理

定义系统级异常和错误码。
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, Optional


# ============================================================
# 错误码枚举
# ============================================================

class ErrorCode(str, Enum):
    """系统错误码"""

    # 通用错误 (1xxx)
    UNKNOWN_ERROR = "E1000"
    INVALID_INPUT = "E1001"
    VALIDATION_ERROR = "E1002"
    RESOURCE_NOT_FOUND = "E1003"
    RESOURCE_CONFLICT = "E1004"

    # Agent 错误 (2xxx)
    AGENT_NOT_FOUND = "E2000"
    AGENT_INITIALIZATION_FAILED = "E2001"
    AGENT_EXECUTION_FAILED = "E2002"
    AGENT_TIMEOUT = "E2003"
    AGENT_NOT_SUPPORTED = "E2004"

    # Skill 错误 (3xxx)
    SKILL_NOT_FOUND = "E3000"
    SKILL_INITIALIZATION_FAILED = "E3001"
    SKILL_EXECUTION_FAILED = "E3002"
    SKILL_TIMEOUT = "E3003"
    SKILL_NOT_FOUND_METHOD = "E3004"

    # Workflow 错误 (4xxx)
    WORKFLOW_NOT_FOUND = "E4000"
    WORKFLOW_INITIALIZATION_FAILED = "E4001"
    WORKFLOW_EXECUTION_FAILED = "E4002"
    WORKFLOW_STEP_FAILED = "E4003"
    WORKFLOW_CIRCULAR_DEPENDENCY = "E4004"

    # LLM 错误 (5xxx)
    LLM_API_ERROR = "E5000"
    LLM_TIMEOUT = "E5001"
    LLM_INVALID_RESPONSE = "E5002"
    LLM_RATE_LIMIT = "E5003"
    LLM_QUOTA_EXCEEDED = "E5004"

    # Memory 错误 (6xxx)
    MEMORY_ERROR = "E6000"
    MEMORY_NOT_FOUND = "E6001"
    MEMORY_STORAGE_FAILED = "E6002"
    MEMORY_QUERY_FAILED = "E6003"

    # MCP 错误 (7xxx)
    MCP_ERROR = "E7000"
    MCP_TOOL_NOT_FOUND = "E7001"
    MCP_TOOL_EXECUTION_ERROR = "E7002"
    MCP_RESOURCE_NOT_FOUND = "E7003"
    MCP_RATE_LIMIT_EXCEEDED = "E7004"

    # 配置错误 (8xxx)
    CONFIG_ERROR = "E8000"
    CONFIG_NOT_FOUND = "E8001"
    CONFIG_VALIDATION_ERROR = "E8002"

    # 认证/授权错误 (9xxx)
    AUTH_ERROR = "E9000"
    AUTH_UNAUTHORIZED = "E9001"
    AUTH_FORBIDDEN = "E9002"
    AUTH_TOKEN_EXPIRED = "E9003"


# ============================================================
# 基础异常类
# ============================================================

class LeoException(Exception):
    """Leo 系统基础异常"""

    def __init__(
        self,
        message: str,
        code: ErrorCode = ErrorCode.UNKNOWN_ERROR,
        details: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}
        self.original_error = original_error

    def __str__(self) -> str:
        parts = [f"[{self.code.value}] {self.message}"]
        if self.details:
            parts.append(f"Details: {self.details}")
        return " ".join(parts)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {
            "error": {
                "code": self.code.value,
                "message": self.message,
            }
        }
        if self.details:
            result["error"]["details"] = self.details
        if self.original_error:
            result["error"]["original_error"] = str(self.original_error)
        return result


# ============================================================
# Agent 异常
# ============================================================

class AgentException(LeoException):
    """Agent 相关异常"""

    def __init__(
        self,
        message: str,
        agent_name: Optional[str] = None,
        **kwargs,
    ):
        code = kwargs.pop("code", ErrorCode.AGENT_EXECUTION_FAILED)
        details = kwargs.pop("details", {})
        if agent_name:
            details["agent_name"] = agent_name
        super().__init__(message, code, details, **kwargs)


class AgentNotFoundException(AgentException):
    """Agent 未找到异常"""

    def __init__(self, agent_name: str):
        super().__init__(
            f"Agent '{agent_name}' not found",
            code=ErrorCode.AGENT_NOT_FOUND,
            agent_name=agent_name,
        )


class AgentExecutionException(AgentException):
    """Agent 执行失败异常"""

    def __init__(self, agent_name: str, reason: str):
        super().__init__(
            f"Agent '{agent_name}' execution failed: {reason}",
            agent_name=agent_name,
            code=ErrorCode.AGENT_EXECUTION_FAILED,
        )


# ============================================================
# Skill 异常
# ============================================================

class SkillException(LeoException):
    """Skill 相关异常"""

    def __init__(
        self,
        message: str,
        skill_name: Optional[str] = None,
        **kwargs,
    ):
        code = kwargs.pop("code", ErrorCode.SKILL_EXECUTION_FAILED)
        details = kwargs.pop("details", {})
        if skill_name:
            details["skill_name"] = skill_name
        super().__init__(message, code, details, **kwargs)


class SkillNotFoundException(SkillException):
    """Skill 未找到异常"""

    def __init__(self, skill_name: str):
        super().__init__(
            f"Skill '{skill_name}' not found",
            code=ErrorCode.SKILL_NOT_FOUND,
            skill_name=skill_name,
        )


class SkillExecutionException(SkillException):
    """Skill 执行失败异常"""

    def __init__(self, skill_name: str, reason: str):
        super().__init__(
            f"Skill '{skill_name}' execution failed: {reason}",
            skill_name=skill_name,
            code=ErrorCode.SKILL_EXECUTION_FAILED,
        )


# ============================================================
# Workflow 异常
# ============================================================

class WorkflowException(LeoException):
    """Workflow 相关异常"""

    def __init__(
        self,
        message: str,
        workflow_id: Optional[str] = None,
        **kwargs,
    ):
        code = kwargs.pop("code", ErrorCode.WORKFLOW_EXECUTION_FAILED)
        details = kwargs.pop("details", {})
        if workflow_id:
            details["workflow_id"] = workflow_id
        super().__init__(message, code, details, **kwargs)


class WorkflowNotFoundException(WorkflowException):
    """Workflow 未找到异常"""

    def __init__(self, workflow_id: str):
        super().__init__(
            f"Workflow '{workflow_id}' not found",
            code=ErrorCode.WORKFLOW_NOT_FOUND,
            workflow_id=workflow_id,
        )


class WorkflowExecutionException(WorkflowException):
    """Workflow 执行失败异常"""

    def __init__(self, workflow_id: str, step_id: Optional[str] = None, reason: Optional[str] = None):
        details = {"workflow_id": workflow_id}
        if step_id:
            details["step_id"] = step_id
        message = f"Workflow '{workflow_id}' execution failed"
        if step_id:
            message += f" at step '{step_id}'"
        if reason:
            message += f": {reason}"
        super().__init__(message, code=ErrorCode.WORKFLOW_EXECUTION_FAILED, **details)


# ============================================================
# LLM 异常
# ============================================================

class LLMException(LeoException):
    """LLM 相关异常"""

    def __init__(
        self,
        message: str,
        model: Optional[str] = None,
        **kwargs,
    ):
        code = kwargs.pop("code", ErrorCode.LLM_API_ERROR)
        details = kwargs.pop("details", {})
        if model:
            details["model"] = model
        super().__init__(message, code, details, **kwargs)


class LLMTimeoutException(LLMException):
    """LLM 超时异常"""

    def __init__(self, model: str, timeout: int):
        super().__init__(
            f"LLM request timeout after {timeout}s",
            code=ErrorCode.LLM_TIMEOUT,
            model=model,
            details={"timeout": timeout},
        )


class LLMRateLimitException(LLMException):
    """LLM 速率限制异常"""

    def __init__(self, model: str, retry_after: Optional[int] = None):
        details = {"model": model}
        if retry_after:
            details["retry_after"] = retry_after
        super().__init__(
            f"LLM rate limit exceeded for model '{model}'",
            code=ErrorCode.LLM_RATE_LIMIT,
            **details,
        )


# ============================================================
# Memory 异常
# ============================================================

class MemoryException(LeoException):
    """Memory 相关异常"""

    def __init__(
        self,
        message: str,
        memory_id: Optional[str] = None,
        **kwargs,
    ):
        code = kwargs.pop("code", ErrorCode.MEMORY_ERROR)
        details = kwargs.pop("details", {})
        if memory_id:
            details["memory_id"] = memory_id
        super().__init__(message, code, details, **kwargs)


class MemoryNotFoundException(MemoryException):
    """Memory 未找到异常"""

    def __init__(self, memory_id: str):
        super().__init__(
            f"Memory entry '{memory_id}' not found",
            code=ErrorCode.MEMORY_NOT_FOUND,
            memory_id=memory_id,
        )


# ============================================================
# MCP 异常
# ============================================================

class MCPException(LeoException):
    """MCP 相关异常"""

    def __init__(
        self,
        message: str,
        tool_name: Optional[str] = None,
        **kwargs,
    ):
        code = kwargs.pop("code", ErrorCode.MCP_ERROR)
        details = kwargs.pop("details", {})
        if tool_name:
            details["tool_name"] = tool_name
        super().__init__(message, code, details, **kwargs)


class MCPTooLNotFoundException(MCPException):
    """MCP 工具未找到异常"""

    def __init__(self, tool_name: str):
        super().__init__(
            f"MCP tool '{tool_name}' not found",
            code=ErrorCode.MCP_TOOL_NOT_FOUND,
            tool_name=tool_name,
        )


class MCPRateLimitException(MCPException):
    """MCP 速率限制异常"""

    def __init__(self, limit: int, window: int):
        super().__init__(
            f"MCP rate limit exceeded: {limit} requests per {window}s",
            code=ErrorCode.MCP_RATE_LIMIT_EXCEEDED,
            details={"limit": limit, "window": window},
        )


# ============================================================
# 异常处理辅助
# ============================================================

def format_error_response(error: Exception) -> Dict[str, Any]:
    """格式化错误响应"""
    if isinstance(error, LeoException):
        return error.to_dict()

    # 未知错误
    return {
        "error": {
            "code": ErrorCode.UNKNOWN_ERROR.value,
            "message": str(error),
            "details": {"type": type(error).__name__},
        }
    }


def is_retryable_error(error: Exception) -> bool:
    """判断错误是否可重试"""
    retryable_codes = [
        ErrorCode.LLM_TIMEOUT,
        ErrorCode.LLM_RATE_LIMIT,
        ErrorCode.MCP_RATE_LIMIT_EXCEEDED,
    ]

    if isinstance(error, LeoException):
        return error.code in retryable_codes

    # 网络错误通常可重试
    if isinstance(error, (TimeoutError, ConnectionError)):
        return True

    return False
