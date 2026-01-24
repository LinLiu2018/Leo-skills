#!/usr/bin/env python3
"""
Leo System - 统一错误处理框架

定义系统中使用的异常类层次结构。
"""
from typing import Any, Dict, Optional


class LeoError(Exception):
    """
    Leo 系统基础异常类

    所有 Leo 系统的自定义异常都应继承此类。
    """

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        初始化异常

        Args:
            message: 错误消息
            error_code: 错误代码（用于分类和追踪）
            details: 额外的错误详情
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}

    def __str__(self) -> str:
        """返回格式化的错误信息"""
        base_msg = f"[{self.error_code}] {self.message}"
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            return f"{base_msg} ({details_str})"
        return base_msg


# ============================================================================
# Skill 相关异常
# ============================================================================


class SkillError(LeoError):
    """Skill 相关的基础异常"""



class SkillNotFoundError(SkillError):
    """Skill 未找到"""

    def __init__(self, skill_name: str, **kwargs):
        super().__init__(
            f"Skill '{skill_name}' not found",
            details={"skill_name": skill_name, **kwargs},
        )


class SkillLoadError(SkillError):
    """Skill 加载失败"""

    def __init__(self, skill_name: str, reason: str, **kwargs):
        super().__init__(
            f"Failed to load skill '{skill_name}': {reason}",
            details={"skill_name": skill_name, "reason": reason, **kwargs},
        )


class SkillExecutionError(SkillError):
    """Skill 执行失败"""

    def __init__(self, skill_name: str, reason: str, **kwargs):
        super().__init__(
            f"Failed to execute skill '{skill_name}': {reason}",
            details={"skill_name": skill_name, "reason": reason, **kwargs},
        )


class SkillValidationError(SkillError):
    """Skill 验证失败（输入或输出不符合要求）"""

    def __init__(self, skill_name: str, validation_error: str, **kwargs):
        super().__init__(
            f"Skill '{skill_name}' validation failed: {validation_error}",
            details={"skill_name": skill_name, "validation_error": validation_error, **kwargs},
        )


# ============================================================================
# Agent 相关异常
# ============================================================================


class AgentError(LeoError):
    """Agent 相关的基础异常"""



class AgentNotFoundError(AgentError):
    """Agent 未找到"""

    def __init__(self, agent_name: str, **kwargs):
        super().__init__(
            f"Agent '{agent_name}' not found",
            details={"agent_name": agent_name, **kwargs},
        )


class AgentDispatchError(AgentError):
    """Agent 调度失败"""

    def __init__(self, agent_name: str, reason: str, **kwargs):
        super().__init__(
            f"Failed to dispatch agent '{agent_name}': {reason}",
            details={"agent_name": agent_name, "reason": reason, **kwargs},
        )


class AgentExecutionError(AgentError):
    """Agent 执行失败"""

    def __init__(self, agent_name: str, reason: str, **kwargs):
        super().__init__(
            f"Agent '{agent_name}' execution failed: {reason}",
            details={"agent_name": agent_name, "reason": reason, **kwargs},
        )


# ============================================================================
# Workflow 相关异常
# ============================================================================


class WorkflowError(LeoError):
    """Workflow 相关的基础异常"""



class WorkflowNotFoundError(WorkflowError):
    """Workflow 未找到"""

    def __init__(self, workflow_name: str, **kwargs):
        super().__init__(
            f"Workflow '{workflow_name}' not found",
            details={"workflow_name": workflow_name, **kwargs},
        )


class WorkflowExecutionError(WorkflowError):
    """Workflow 执行失败"""

    def __init__(self, workflow_name: str, step: str, reason: str, **kwargs):
        super().__init__(
            f"Workflow '{workflow_name}' failed at step '{step}': {reason}",
            details={"workflow_name": workflow_name, "step": step, "reason": reason, **kwargs},
        )


class WorkflowValidationError(WorkflowError):
    """Workflow 定义验证失败"""

    def __init__(self, workflow_name: str, validation_error: str, **kwargs):
        super().__init__(
            f"Workflow '{workflow_name}' validation failed: {validation_error}",
            details={
                "workflow_name": workflow_name,
                "validation_error": validation_error,
                **kwargs,
            },
        )


# ============================================================================
# Registry 相关异常
# ============================================================================


class RegistryError(LeoError):
    """Registry 相关的基础异常"""



class RegistrationError(RegistryError):
    """注册失败"""

    def __init__(self, item_type: str, item_name: str, reason: str, **kwargs):
        super().__init__(
            f"Failed to register {item_type} '{item_name}': {reason}",
            details={"item_type": item_type, "item_name": item_name, "reason": reason, **kwargs},
        )


# ============================================================================
# Configuration 相关异常
# ============================================================================


class ConfigurationError(LeoError):
    """配置相关的异常"""

    def __init__(self, config_key: str, reason: str, **kwargs):
        super().__init__(
            f"Configuration error for '{config_key}': {reason}",
            details={"config_key": config_key, "reason": reason, **kwargs},
        )


# ============================================================================
# System 相关异常
# ============================================================================


class SystemError(LeoError):
    """系统级异常"""



class InitializationError(SystemError):
    """系统初始化失败"""

    def __init__(self, component: str, reason: str, **kwargs):
        super().__init__(
            f"Failed to initialize {component}: {reason}",
            details={"component": component, "reason": reason, **kwargs},
        )
