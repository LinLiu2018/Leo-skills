"""
Bank Product Agent - 银行产品代理

银行产品专家，专注银行产品库维护、利率监控和银行经理对接。
"""

from typing import Dict, Any, Optional
from pathlib import Path


class BankProductAgent:
    """银行产品代理"""
    
    def __init__(self, workspace: Optional[str] = None):
        self.name = "bank_product_agent"
        self.display_name = "银行产品专家"
        self.emoji = "💳"
        self.workspace = Path(workspace) if workspace else Path.home() / ".openclaw" / "workspace-bank-product"
        self.model = "qwen3.5-plus"
        self.workspace.mkdir(parents=True, exist_ok=True)
        
        self.skills = ["bank_product_db_skill", "web_search_skill", "data_analyzer_skill"]
        self.triggers = ["银行产品", "利率对比", "LPR", "银行经理", "产品库", "房贷利率"]
    
    def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        context = context or {}
        if "产品库" in task or "维护" in task:
            return self._product_db_maintain(task, context)
        elif "利率" in task or "LPR" in task:
            return self._rate_monitor(task, context)
        elif "经理" in task or "对接" in task:
            return self._bank_liaison(task, context)
        else:
            return self._general_response(task, context)
    
    def _product_db_maintain(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "success", "agent": self.name, "action": "product_db_maintain", "message": f"💳 正在维护产品库...\n\n任务：{task}", "next_steps": ["更新产品信息", "记录利率变动", "同步数据"]}
    
    def _rate_monitor(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "success", "agent": self.name, "action": "rate_monitor", "message": f"💳 正在监控利率...\n\n任务：{task}", "next_steps": ["查询 LPR", "对比银行利率", "推送变动通知"]}
    
    def _bank_liaison(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "success", "agent": self.name, "action": "bank_liaison", "message": f"💳 正在对接银行...\n\n任务：{task}", "next_steps": ["联系银行经理", "获取最新政策", "更新联系人"]}
    
    def _general_response(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "success", "agent": self.name, "action": "general", "message": f"💳 银行产品专家收到任务：{task}", "next_steps": ["识别任务", "调用技能", "返回结果"]}
    
    def get_status(self) -> Dict[str, Any]:
        return {"name": self.name, "display_name": self.display_name, "emoji": self.emoji, "model": self.model, "workspace": str(self.workspace), "skills": self.skills, "triggers": self.triggers, "status": "active"}


__all__ = ["BankProductAgent"]
