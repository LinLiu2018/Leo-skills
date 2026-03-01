"""
Tool Tracker
============
工具调用追踪器 - 记录和追踪所有工具调用

参考 Claude Code 官方最佳实践:
- subagent_tracker.py 实现模式
- 记录每个工具的输入输出
- 关联到具体的 Agent/Session
"""

import json
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, field, asdict

from .hooks import HookRegistry, HookContext, ToolCallRecord, HookPhase, get_hook_registry


@dataclass
class ToolCallEvent:
    """工具调用事件"""
    event: str  # "tool_call_start" | "tool_call_complete" | "tool_call_error"
    tool_id: str
    tool_name: str
    agent_id: str
    parent_tool_use_id: str
    timestamp: str
    input_size: int = 0
    output_size: int = 0
    duration_ms: float = 0.0
    success: bool = True
    error: Optional[str] = None


class ToolTracker:
    """
    工具调用追踪器
    ==============
    追踪所有工具调用，记录详细的输入输出信息
    """

    def __init__(self, output_dir: str = "logs/tool_calls"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.session_id: str = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.jsonl_path = self.output_dir / f"tool_calls_{self.session_id}.jsonl"
        self.transcript_path = self.output_dir / f"transcript_{self.session_id}.txt"

        # 追踪上下文
        self._current_agent_id: str = "main"
        self._parent_id_stack: List[str] = []

        # 注册 Hooks
        self._hooks = get_hook_registry()
        self._register_hooks()

    def _register_hooks(self):
        """注册追踪 Hooks"""
        # 注册全局 Pre Hook
        self._hooks.register_global_pre_hook(self.pre_tool_use_hook)

        # 注册全局 Post Hook
        self._hooks.register_global_post_hook(self.post_tool_use_hook)

    def set_agent_id(self, agent_id: str):
        """设置当前 Agent ID"""
        self._current_agent_id = agent_id

    def push_parent_id(self, parent_id: str):
        """推入父工具调用 ID"""
        self._parent_id_stack.append(parent_id)

    def pop_parent_id(self) -> Optional[str]:
        """弹出父工具调用 ID"""
        if self._parent_id_stack:
            return self._parent_id_stack.pop()
        return None

    def get_parent_id(self) -> str:
        """获取当前父工具调用 ID"""
        return self._parent_id_stack[-1] if self._parent_id_stack else ""

    def pre_tool_use_hook(self, record: ToolCallRecord) -> None:
        """Pre Tool Use Hook - 工具调用前"""
        # 构建上下文
        context = HookContext(
            agent_id=self._current_agent_id,
            parent_tool_use_id=self.get_parent_id()
        )

        event = ToolCallEvent(
            event="tool_call_start",
            tool_id=record.tool_id,
            tool_name=record.tool_name,
            agent_id=context.agent_id,
            parent_tool_use_id=context.parent_tool_use_id,
            timestamp=record.context.timestamp,
            input_size=self._estimate_size(record.tool_input)
        )

        # 写入日志
        self._write_jsonl(event)
        self._write_transcript(
            f"[{record.context.agent_id}] → {record.tool_name}\n"
            f"    Input: {self._format_input(record.tool_input)}\n"
        )

    def post_tool_use_hook(self, record: ToolCallRecord) -> None:
        """Post Tool Use Hook - 工具调用后"""
        context = HookContext(
            agent_id=self._current_agent_id,
            parent_tool_use_id=self.get_parent_id()
        )

        event = ToolCallEvent(
            event="tool_call_complete" if record.success else "tool_call_error",
            tool_id=record.tool_id,
            tool_name=record.tool_name,
            agent_id=context.agent_id,
            parent_tool_use_id=context.parent_tool_use_id,
            timestamp=datetime.now().isoformat(),
            output_size=self._estimate_size(record.tool_output),
            duration_ms=record.duration_ms,
            success=record.success,
            error=record.error
        )

        # 写入日志
        self._write_jsonl(event)
        self._write_transcript(
            f"[{record.context.agent_id}] ← {record.tool_name}\n"
            f"    Output: {self._format_output(record.tool_output)}\n"
            f"    Duration: {record.duration_ms:.2f}ms\n"
        )

    def _write_jsonl(self, event: ToolCallEvent):
        """写入 JSONL 格式日志"""
        try:
            with open(self.jsonl_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(asdict(event), ensure_ascii=False) + '\n')
        except Exception:
            pass  # 静默失败，避免影响主流程

    def _write_transcript(self, line: str):
        """写入可读格式日志"""
        try:
            with open(self.transcript_path, 'a', encoding='utf-8') as f:
                f.write(line)
        except Exception:
            pass

    def _estimate_size(self, obj: Any) -> int:
        """估算对象大小"""
        try:
            return len(json.dumps(obj, ensure_ascii=False))
        except Exception:
            return 0

    def _format_input(self, tool_input: Dict[str, Any]) -> str:
        """格式化输入"""
        try:
            # 简化显示
            formatted = json.dumps(tool_input, ensure_ascii=False, indent=2)
            if len(formatted) > 200:
                return formatted[:200] + "..."
            return formatted
        except Exception:
            return str(tool_input)[:200]

    def _format_output(self, tool_output: Any) -> str:
        """格式化输出"""
        try:
            if tool_output is None:
                return "None"
            formatted = json.dumps(tool_output, ensure_ascii=False, indent=2)
            if len(formatted) > 200:
                return formatted[:200] + "..."
            return formatted
        except Exception:
            output_str = str(tool_output)
            if len(output_str) > 200:
                return output_str[:200] + "..."
            return output_str


# ==================== 便捷函数 ====================

_global_tracker: Optional[ToolTracker] = None


def get_tool_tracker(output_dir: str = "logs/tool_calls") -> ToolTracker:
    """获取全局工具追踪器"""
    global _global_tracker
    if _global_tracker is None:
        _global_tracker = ToolTracker(output_dir)
    return _global_tracker


def track_agent(agent_id: str):
    """设置当前追踪的 Agent"""
    tracker = get_tool_tracker()
    tracker.set_agent_id(agent_id)


def track_subagent_start(parent_id: str) -> str:
    """开始追踪子代理 - 返回新的子代理 ID"""
    tracker = get_tool_tracker()
    subagent_id = f"{parent_id}-subagent-{uuid.uuid4().hex[:8]}"
    tracker.push_parent_id(subagent_id)
    return subagent_id


def track_subagent_end():
    """结束追踪子代理"""
    tracker = get_tool_tracker()
    tracker.pop_parent_id()
