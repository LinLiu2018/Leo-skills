"""
Sales Agent - 销售助手代理
"""

from typing import Dict, Any, Optional
from pathlib import Path


class SalesAgent:
    """销售助手代理"""
    
    def __init__(self, workspace: Optional[str] = None):
        self.name = "sales_agent"
        self.display_name = "销售助手"
        self.emoji = "💼"
        self.workspace = Path(workspace) if workspace else Path.home() / ".openclaw" / "workspace-sales"
        self.model = "qwen3.5-plus"
        self.workspace.mkdir(parents=True, exist_ok=True)
        
        self.triggers = ["销售", "线索", "客户跟进", "成交", "签单", "业绩"]
    
    def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        context = context or {}
        
        if "线索" in task or "客户" in task:
            return self._handle_lead(task, context)
        elif "跟进" in task or "回访" in task:
            return self._handle_followup(task, context)
        elif "成交" in task or "签单" in task:
            return self._handle_deal(task, context)
        elif "业绩" in task or "分析" in task:
            return self._handle_analysis(task, context)
        else:
            return self._general_response(task, context)
    
    def _handle_lead(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "success",
            "agent": self.name,
            "action": "handle_lead",
            "message": f"💼 正在处理销售线索...\n\n任务：{task}",
            "next_steps": ["录入 CRM", "分配销售", "安排跟进"]
        }
    
    def _handle_followup(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "success",
            "agent": self.name,
            "action": "handle_followup",
            "message": f"💼 正在处理客户跟进...\n\n任务：{task}",
            "next_steps": ["查看跟进记录", "生成跟进话术", "安排回访"]
        }
    
    def _handle_deal(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "success",
            "agent": self.name,
            "action": "handle_deal",
            "message": f"💼 正在处理成交签单...\n\n任务：{task}",
            "next_steps": ["准备合同", "确认条款", "安排签约"]
        }
    
    def _handle_analysis(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "success",
            "agent": self.name,
            "action": "handle_analysis",
            "message": f"💼 正在分析销售数据...\n\n任务：{task}",
            "next_steps": ["收集数据", "生成报表", "提供建议"]
        }
    
    def _general_response(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "success",
            "agent": self.name,
            "action": "general",
            "message": f"💼 销售助手收到任务：{task}",
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


__all__ = ["SalesAgent"]
