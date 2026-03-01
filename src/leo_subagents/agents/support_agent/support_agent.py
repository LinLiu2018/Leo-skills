"""
Support Agent - 客服助手代理
"""

from typing import Dict, Any, Optional
from pathlib import Path


class SupportAgent:
    """客服助手代理"""
    
    def __init__(self, workspace: Optional[str] = None):
        self.name = "support_agent"
        self.display_name = "客服助手"
        self.emoji = "🎧"
        self.workspace = Path(workspace) if workspace else Path.home() / ".openclaw" / "workspace-support"
        self.model = "qwen3.5-plus"
        self.workspace.mkdir(parents=True, exist_ok=True)
        
        self.triggers = ["客服", "咨询", "投诉", "售后", "退换货", "客户支持"]
    
    def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        context = context or {}
        
        if "咨询" in task or "问题" in task:
            return self._handle_inquiry(task, context)
        elif "投诉" in task:
            return self._handle_complaint(task, context)
        elif "售后" in task or "退换" in task:
            return self._handle_after_sales(task, context)
        else:
            return self._general_response(task, context)
    
    def _handle_inquiry(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "success",
            "agent": self.name,
            "action": "handle_inquiry",
            "message": f"🎧 正在处理客户咨询...\n\n任务：{task}",
            "next_steps": ["查询知识库", "生成回复", "发送客户"]
        }
    
    def _handle_complaint(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "success",
            "agent": self.name,
            "action": "handle_complaint",
            "message": f"🎧 正在处理客户投诉...\n\n任务：{task}",
            "next_steps": ["记录投诉", "分类转办", "跟进处理"]
        }
    
    def _handle_after_sales(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "success",
            "agent": self.name,
            "action": "handle_after_sales",
            "message": f"🎧 正在处理售后支持...\n\n任务：{task}",
            "next_steps": ["确认问题", "安排处理", "跟进结果"]
        }
    
    def _general_response(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "success",
            "agent": self.name,
            "action": "general",
            "message": f"🎧 客服助手收到任务：{task}",
            "next_steps": ["识别任务", "调用技能", "返回结果"]
        }
    
    def get_status(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "display_name": self.display_name,
            "emoji": self.emoji,
            "model": self.model,
            "workspace": str(self.workspace),
            "triggers": self.triggers,
            "status": "active"
        }


__all__ = ["SupportAgent"]
