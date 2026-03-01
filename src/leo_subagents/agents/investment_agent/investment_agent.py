"""
Investment Agent - 投资顾问代理

投资分析专家，专注投资回报测算、财务分析和投资建议。
"""

from typing import Dict, Any, Optional
from pathlib import Path


class InvestmentAgent:
    """投资顾问代理"""
    
    def __init__(self, workspace: Optional[str] = None):
        self.name = "investment_agent"
        self.display_name = "投资顾问"
        self.emoji = "💰"
        self.workspace = Path(workspace) if workspace else Path.home() / ".openclaw" / "workspace-investment"
        self.model = "qwen3.5-plus"
        self.workspace.mkdir(parents=True, exist_ok=True)
        
        self.skills = ["investment_calculator_skill", "data_analyzer_skill", "web_search_skill"]
        self.triggers = ["投资分析", "ROI", "回报率", "财务测算", "现金流", "投资建议", "IRR"]
    
    def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        context = context or {}
        if "ROI" in task or "回报" in task or "测算" in task:
            return self._roi_calc(task, context)
        elif "财务" in task or "现金流" in task:
            return self._financial_analysis(task, context)
        elif "风险" in task or "评估" in task:
            return self._risk_assess(task, context)
        else:
            return self._general_response(task, context)
    
    def _roi_calc(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "success", "agent": self.name, "action": "roi_calc", "message": f"💰 正在计算投资回报...\n\n任务：{task}", "next_steps": ["收集投资数据", "计算 ROI/IRR", "生成报告"]}
    
    def _financial_analysis(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "success", "agent": self.name, "action": "financial_analysis", "message": f"💰 正在财务分析...\n\n任务：{task}", "next_steps": ["现金流预测", "损益分析", "敏感性分析"]}
    
    def _risk_assess(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "success", "agent": self.name, "action": "risk_assess", "message": f"💰 正在风险评估...\n\n任务：{task}", "next_steps": ["识别风险因素", "评估影响", "制定应对策略"]}
    
    def _general_response(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "success", "agent": self.name, "action": "general", "message": f"💰 投资顾问收到任务：{task}", "next_steps": ["识别任务", "调用技能", "返回结果"]}
    
    def get_status(self) -> Dict[str, Any]:
        return {"name": self.name, "display_name": self.display_name, "emoji": self.emoji, "model": self.model, "workspace": str(self.workspace), "skills": self.skills, "triggers": self.triggers, "status": "active"}


__all__ = ["InvestmentAgent"]
