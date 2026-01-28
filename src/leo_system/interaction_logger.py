#!/usr/bin/env python3
"""
Leo System - 交互日志记录器
===========================
记录用户交互、Agent调用链路、Workflow执行等完整日志

功能：
1. 用户交互日志 - 记录用户输入和系统响应
2. Agent调用链路 - 记录Agent选择和调用过程
3. Workflow执行日志 - 记录工作流每步执行状态
4. 日志持久化 - 自动保存到JSON文件
5. 日志查询 - 按时间/类型/关键词查询
"""

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from .logger import get_logger

# 日志存储目录
INTERACTION_LOGS_DIR = Path(__file__).parent.parent / "logs" / "interactions"
INTERACTION_LOGS_DIR.mkdir(parents=True, exist_ok=True)

# 日志记录器
logger = get_logger(__name__)


class LogType(Enum):
    """日志类型"""
    USER_INPUT = "user_input"           # 用户输入
    SYSTEM_RESPONSE = "system_response" # 系统响应
    AGENT_SELECT = "agent_select"       # Agent选择
    AGENT_EXECUTE = "agent_execute"     # Agent执行
    SKILL_CALL = "skill_call"           # Skill调用
    WORKFLOW_START = "workflow_start"   # 工作流开始
    WORKFLOW_STEP = "workflow_step"     # 工作流步骤
    WORKFLOW_END = "workflow_end"       # 工作流结束
    ERROR = "error"                     # 错误


@dataclass
class InteractionLog:
    """交互日志条目"""
    log_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    log_type: str = ""
    session_id: str = ""
    content: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)


class InteractionLogger:
    """
    交互日志记录器
    ==============
    提供完整的交互日志记录和查询功能
    """

    def __init__(self, session_id: Optional[str] = None):
        """
        初始化日志记录器

        Args:
            session_id: 会话ID（可选，自动生成）
        """
        self.session_id = session_id or self._generate_session_id()
        self.logs: List[InteractionLog] = []
        self._current_workflow_id: Optional[str] = None
        self._current_agent_chain: List[str] = []

    def _generate_session_id(self) -> str:
        """生成会话ID"""
        return f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:4]}"

    # ==================== 用户交互日志 ====================

    def log_user_input(self, user_input: str, context: Optional[Dict] = None) -> str:
        """
        记录用户输入

        Args:
            user_input: 用户输入内容
            context: 上下文信息

        Returns:
            日志ID
        """
        log = InteractionLog(
            log_type=LogType.USER_INPUT.value,
            session_id=self.session_id,
            content={
                "input": user_input,
                "input_length": len(user_input),
            },
            metadata=context or {}
        )
        self._add_log(log)
        logger.info(f"[用户输入] {user_input[:100]}...")
        return log.log_id

    def log_system_response(
        self,
        response: str,
        response_type: str = "text",
        related_input_id: Optional[str] = None
    ) -> str:
        """
        记录系统响应

        Args:
            response: 系统响应内容
            response_type: 响应类型（text/file/action）
            related_input_id: 关联的用户输入ID

        Returns:
            日志ID
        """
        log = InteractionLog(
            log_type=LogType.SYSTEM_RESPONSE.value,
            session_id=self.session_id,
            content={
                "response": response[:500] if len(response) > 500 else response,
                "response_type": response_type,
                "response_length": len(response),
                "truncated": len(response) > 500,
            },
            metadata={
                "related_input_id": related_input_id,
            }
        )
        self._add_log(log)
        logger.info(f"[系统响应] {response_type}: {len(response)} chars")
        return log.log_id

    # ==================== Agent调用链路 ====================

    def log_agent_select(
        self,
        task: str,
        selected_agent: str,
        confidence: float,
        candidates: Optional[List[Dict]] = None
    ) -> str:
        """
        记录Agent选择

        Args:
            task: 任务描述
            selected_agent: 选中的Agent
            confidence: 置信度
            candidates: 候选Agent列表

        Returns:
            日志ID
        """
        self._current_agent_chain.append(selected_agent)

        log = InteractionLog(
            log_type=LogType.AGENT_SELECT.value,
            session_id=self.session_id,
            content={
                "task": task,
                "selected_agent": selected_agent,
                "confidence": confidence,
                "candidates": candidates or [],
            },
            metadata={
                "agent_chain": self._current_agent_chain.copy(),
            }
        )
        self._add_log(log)
        logger.info(f"[Agent选择] {selected_agent} (置信度: {confidence:.2f})")
        return log.log_id

    def log_agent_execute(
        self,
        agent_name: str,
        action: str,
        params: Dict[str, Any],
        result: Any,
        success: bool,
        execution_time: float
    ) -> str:
        """
        记录Agent执行

        Args:
            agent_name: Agent名称
            action: 执行的动作
            params: 参数
            result: 执行结果
            success: 是否成功
            execution_time: 执行时间

        Returns:
            日志ID
        """
        log = InteractionLog(
            log_type=LogType.AGENT_EXECUTE.value,
            session_id=self.session_id,
            content={
                "agent_name": agent_name,
                "action": action,
                "params": self._safe_serialize(params),
                "result_summary": self._summarize_result(result),
                "success": success,
                "execution_time": execution_time,
            },
            metadata={
                "agent_chain": self._current_agent_chain.copy(),
            }
        )
        self._add_log(log)
        status = "成功" if success else "失败"
        logger.info(f"[Agent执行] {agent_name}.{action} - {status} ({execution_time:.2f}s)")
        return log.log_id

    def log_skill_call(
        self,
        skill_name: str,
        action: str,
        params: Dict[str, Any],
        result: Any,
        success: bool,
        execution_time: float,
        called_by: Optional[str] = None
    ) -> str:
        """
        记录Skill调用

        Args:
            skill_name: Skill名称
            action: 动作
            params: 参数
            result: 结果
            success: 是否成功
            execution_time: 执行时间
            called_by: 调用者（Agent名称）

        Returns:
            日志ID
        """
        log = InteractionLog(
            log_type=LogType.SKILL_CALL.value,
            session_id=self.session_id,
            content={
                "skill_name": skill_name,
                "action": action,
                "params": self._safe_serialize(params),
                "result_summary": self._summarize_result(result),
                "success": success,
                "execution_time": execution_time,
            },
            metadata={
                "called_by": called_by,
                "workflow_id": self._current_workflow_id,
            }
        )
        self._add_log(log)
        status = "成功" if success else "失败"
        logger.info(f"[Skill调用] {skill_name}.{action} - {status} ({execution_time:.2f}s)")
        return log.log_id

    # ==================== Workflow执行日志 ====================

    def log_workflow_start(
        self,
        workflow_name: str,
        inputs: Dict[str, Any],
        total_steps: int
    ) -> str:
        """
        记录工作流开始

        Args:
            workflow_name: 工作流名称
            inputs: 输入参数
            total_steps: 总步骤数

        Returns:
            工作流ID
        """
        workflow_id = f"wf_{datetime.now().strftime('%H%M%S')}_{str(uuid.uuid4())[:4]}"
        self._current_workflow_id = workflow_id

        log = InteractionLog(
            log_type=LogType.WORKFLOW_START.value,
            session_id=self.session_id,
            content={
                "workflow_id": workflow_id,
                "workflow_name": workflow_name,
                "inputs": self._safe_serialize(inputs),
                "total_steps": total_steps,
            }
        )
        self._add_log(log)
        logger.info(f"[工作流开始] {workflow_name} ({total_steps}步)")
        return workflow_id

    def log_workflow_step(
        self,
        step_name: str,
        step_number: int,
        agent: str,
        status: str,
        result_summary: Optional[str] = None,
        execution_time: float = 0.0
    ) -> str:
        """
        记录工作流步骤

        Args:
            step_name: 步骤名称
            step_number: 步骤序号
            agent: 执行的Agent
            status: 状态（running/completed/failed/skipped）
            result_summary: 结果摘要
            execution_time: 执行时间

        Returns:
            日志ID
        """
        log = InteractionLog(
            log_type=LogType.WORKFLOW_STEP.value,
            session_id=self.session_id,
            content={
                "workflow_id": self._current_workflow_id,
                "step_name": step_name,
                "step_number": step_number,
                "agent": agent,
                "status": status,
                "result_summary": result_summary,
                "execution_time": execution_time,
            }
        )
        self._add_log(log)
        logger.info(f"[工作流步骤] {step_number}. {step_name} ({agent}) - {status}")
        return log.log_id

    def log_workflow_end(
        self,
        success: bool,
        total_time: float,
        completed_steps: int,
        output_summary: Optional[str] = None
    ) -> str:
        """
        记录工作流结束

        Args:
            success: 是否成功
            total_time: 总耗时
            completed_steps: 完成的步骤数
            output_summary: 输出摘要

        Returns:
            日志ID
        """
        log = InteractionLog(
            log_type=LogType.WORKFLOW_END.value,
            session_id=self.session_id,
            content={
                "workflow_id": self._current_workflow_id,
                "success": success,
                "total_time": total_time,
                "completed_steps": completed_steps,
                "output_summary": output_summary,
            }
        )
        self._add_log(log)

        status = "成功" if success else "失败"
        logger.info(f"[工作流结束] {status} - {completed_steps}步完成 ({total_time:.2f}s)")

        # 重置工作流状态
        self._current_workflow_id = None

        return log.log_id

    # ==================== 错误日志 ====================

    def log_error(
        self,
        error_type: str,
        error_message: str,
        context: Optional[Dict] = None,
        stack_trace: Optional[str] = None
    ) -> str:
        """
        记录错误

        Args:
            error_type: 错误类型
            error_message: 错误信息
            context: 上下文
            stack_trace: 堆栈跟踪

        Returns:
            日志ID
        """
        log = InteractionLog(
            log_type=LogType.ERROR.value,
            session_id=self.session_id,
            content={
                "error_type": error_type,
                "error_message": error_message,
                "stack_trace": stack_trace,
            },
            metadata={
                "context": context or {},
                "workflow_id": self._current_workflow_id,
                "agent_chain": self._current_agent_chain.copy(),
            }
        )
        self._add_log(log)
        logger.error(f"[错误] {error_type}: {error_message}")
        return log.log_id

    # ==================== 日志管理 ====================

    def _add_log(self, log: InteractionLog) -> None:
        """添加日志并自动保存"""
        self.logs.append(log)
        # 每10条日志自动保存一次
        if len(self.logs) % 10 == 0:
            self.save_to_file()

    def _safe_serialize(self, obj: Any) -> Any:
        """安全序列化对象"""
        try:
            json.dumps(obj)
            return obj
        except (TypeError, ValueError):
            return str(obj)[:500]

    def _summarize_result(self, result: Any) -> str:
        """生成结果摘要"""
        if result is None:
            return "None"
        if isinstance(result, str):
            return result[:200] + "..." if len(result) > 200 else result
        if isinstance(result, dict):
            return f"Dict with {len(result)} keys"
        if isinstance(result, list):
            return f"List with {len(result)} items"
        return str(result)[:200]

    def save_to_file(self, filename: Optional[str] = None) -> Path:
        """
        保存日志到文件

        Args:
            filename: 文件名（可选）

        Returns:
            保存的文件路径
        """
        if not filename:
            filename = f"{self.session_id}.json"

        filepath = INTERACTION_LOGS_DIR / filename

        data = {
            "session_id": self.session_id,
            "created_at": datetime.now().isoformat(),
            "log_count": len(self.logs),
            "logs": [log.to_dict() for log in self.logs]
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.debug(f"日志已保存到 {filepath}")
        return filepath

    def get_logs(
        self,
        log_type: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        keyword: Optional[str] = None
    ) -> List[InteractionLog]:
        """
        查询日志

        Args:
            log_type: 日志类型过滤
            start_time: 开始时间
            end_time: 结束时间
            keyword: 关键词搜索

        Returns:
            符合条件的日志列表
        """
        result = self.logs

        if log_type:
            result = [l for l in result if l.log_type == log_type]

        if start_time:
            result = [l for l in result if l.timestamp >= start_time]

        if end_time:
            result = [l for l in result if l.timestamp <= end_time]

        if keyword:
            result = [
                l for l in result
                if keyword.lower() in json.dumps(l.content, ensure_ascii=False).lower()
            ]

        return result

    def get_session_summary(self) -> Dict[str, Any]:
        """
        获取会话摘要

        Returns:
            会话摘要信息
        """
        type_counts = {}
        for log in self.logs:
            type_counts[log.log_type] = type_counts.get(log.log_type, 0) + 1

        return {
            "session_id": self.session_id,
            "total_logs": len(self.logs),
            "log_types": type_counts,
            "start_time": self.logs[0].timestamp if self.logs else None,
            "end_time": self.logs[-1].timestamp if self.logs else None,
            "agent_chain": self._current_agent_chain,
        }

    def clear_agent_chain(self) -> None:
        """清空Agent调用链"""
        self._current_agent_chain = []


# ==================== 全局实例 ====================

_global_logger: Optional[InteractionLogger] = None


def get_interaction_logger(session_id: Optional[str] = None) -> InteractionLogger:
    """
    获取全局交互日志记录器

    Args:
        session_id: 会话ID（可选）

    Returns:
        InteractionLogger实例
    """
    global _global_logger

    if _global_logger is None or session_id:
        _global_logger = InteractionLogger(session_id)

    return _global_logger


def new_session(session_id: Optional[str] = None) -> InteractionLogger:
    """
    创建新会话

    Args:
        session_id: 会话ID（可选）

    Returns:
        新的InteractionLogger实例
    """
    global _global_logger

    # 保存旧会话
    if _global_logger:
        _global_logger.save_to_file()

    _global_logger = InteractionLogger(session_id)
    return _global_logger


# ==================== 便捷函数 ====================

def log_user_input(user_input: str, context: Optional[Dict] = None) -> str:
    """记录用户输入"""
    return get_interaction_logger().log_user_input(user_input, context)


def log_system_response(response: str, response_type: str = "text") -> str:
    """记录系统响应"""
    return get_interaction_logger().log_system_response(response, response_type)


def log_agent_select(task: str, agent: str, confidence: float) -> str:
    """记录Agent选择"""
    return get_interaction_logger().log_agent_select(task, agent, confidence)


def log_skill_call(skill: str, action: str, params: Dict, result: Any, success: bool, time: float) -> str:
    """记录Skill调用"""
    return get_interaction_logger().log_skill_call(skill, action, params, result, success, time)


def log_error(error_type: str, message: str, context: Optional[Dict] = None) -> str:
    """记录错误"""
    return get_interaction_logger().log_error(error_type, message, context)
