"""
Loan Agent - 贷款顾问代理

贷款方案顾问，专注房贷政策追踪、贷款方案匹配和银行产品推荐。
"""

from typing import Dict, Any, Optional
from pathlib import Path


class LoanAgent:
    """贷款顾问代理"""
    
    def __init__(self, workspace: Optional[str] = None):
        self.name = "loan_agent"
        self.display_name = "贷款顾问"
        self.emoji = "🏦"
        self.workspace = Path(workspace) if workspace else Path.home() / ".openclaw" / "workspace-loan"
        self.model = "qwen3.5-plus"
        self.workspace.mkdir(parents=True, exist_ok=True)
        
        self.skills = ["loan_calculator_skill", "credit_assessment_skill", "bank_product_db_skill", "web_search_skill"]
        self.triggers = ["贷款", "房贷", "银行", "LPR", "月供", "利率", "首付"]
    
    def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        context = context or {}
        if "政策" in task or "LPR" in task or "利率" in task:
            return self._policy_track(task, context)
        elif "方案" in task or "匹配" in task:
            return self._scheme_match(task, context)
        elif "银行" in task or "产品" in task:
            return self._bank_product(task, context)
        elif "计算" in task or "月供" in task:
            return self._loan_calc(task, context)
        else:
            return self._general_response(task, context)
    
    def _policy_track(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "success", "agent": self.name, "action": "policy_track", "message": f"🏦 正在追踪贷款政策...\n\n任务：{task}", "next_steps": ["搜索最新政策", "分析影响", "推送简报"]}
    
    def _scheme_match(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "success", "agent": self.name, "action": "scheme_match", "message": f"🏦 正在匹配贷款方案...\n\n任务：{task}", "next_steps": ["评估客户资质", "对比银行产品", "推荐最优方案"]}
    
    def _bank_product(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "success", "agent": self.name, "action": "bank_product", "message": f"🏦 正在查询银行产品...\n\n任务：{task}", "next_steps": ["查询产品库", "对比利率", "推荐银行"]}
    
    def _loan_calc(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "success", "agent": self.name, "action": "loan_calc", "message": f"🏦 正在计算贷款...\n\n任务：{task}", "next_steps": ["输入贷款信息", "计算月供", "生成对比表"]}
    
    def _general_response(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "success", "agent": self.name, "action": "general", "message": f"🏦 贷款顾问收到任务：{task}", "next_steps": ["识别任务", "调用技能", "返回结果"]}
    
    def get_status(self) -> Dict[str, Any]:
        return {"name": self.name, "display_name": self.display_name, "emoji": self.emoji, "model": self.model, "workspace": str(self.workspace), "skills": self.skills, "triggers": self.triggers, "status": "active"}


__all__ = ["LoanAgent"]
