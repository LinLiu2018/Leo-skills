"""
Leasing Agent - 招商助手代理
"""

from typing import Dict, Any, Optional
from pathlib import Path

from leo_memory import auto_memorize


@auto_memorize
class LeasingAgent:
    """招商助手代理"""
    
    def __init__(self, workspace: Optional[str] = None):
        self.name = "leasing_agent"
        self.display_name = "招商助手"
        self.emoji = "🏢"
        self.workspace = Path(workspace) if workspace else Path.home() / ".openclaw" / "workspace-leasing"
        self.model = "qwen3.5-plus"
        self.workspace.mkdir(parents=True, exist_ok=True)
        
        self.triggers = ["招商", "租户", "租赁", "商铺", "写字楼", "出租率"]
    
    def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        context = context or {}
        
        if "招商" in task or "咨询" in task:
            return self._handle_inquiry(task, context)
        elif "租户" in task or "筛选" in task:
            return self._handle_screening(task, context)
        elif "租赁" in task or "合同" in task:
            return self._handle_lease(task, context)
        elif "出租率" in task or "分析" in task:
            return self._handle_analysis(task, context)
        else:
            return self._general_response(task, context)
    
    def _handle_inquiry(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "success",
            "agent": self.name,
            "action": "handle_inquiry",
            "message": f"🏢 正在处理招商咨询...\n\n任务：{task}",
            "next_steps": ["查询房源", "提供信息", "安排看房"]
        }
    
    def _handle_screening(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "success",
            "agent": self.name,
            "action": "handle_screening",
            "message": f"🏢 正在筛选租户...\n\n任务：{task}",
            "next_steps": ["资质审核", "信用评估", "行业匹配"]
        }
    
    def _handle_lease(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "success",
            "agent": self.name,
            "action": "handle_lease",
            "message": f"🏢 正在处理租赁合同...\n\n任务：{task}",
            "next_steps": ["准备合同", "确认条款", "安排签约"]
        }
    
    def _handle_analysis(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "success",
            "agent": self.name,
            "action": "handle_analysis",
            "message": f"🏢 正在分析招商数据...\n\n任务：{task}",
            "next_steps": ["收集数据", "生成报表", "提供建议"]
        }
    
    def _general_response(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "success",
            "agent": self.name,
            "action": "general",
            "message": f"🏢 招商助手收到任务：{task}",
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


__all__ = ["LeasingAgent"]
