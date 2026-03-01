"""
Commercial Sales Agent - 商业销售部代理

商业地产销售专家，专注摊位/商铺/不良资产销售。
"""

from typing import Dict, Any, Optional
from pathlib import Path

from leo_memory import auto_memorize


@auto_memorize
class CommercialSalesAgent:
    """
    商业销售部代理
    
    职责:
    - 市场情报：宁波商业地产动态、摊位/商铺成交价
    - 内容创作：商铺销售文案、投资回报分析
    - 客户跟进：投资客户画像、商铺选址建议
    - 数据复盘：销售成交分析、渠道分析
    """
    
    def __init__(self, workspace: Optional[str] = None):
        self.name = "commercial_sales_agent"
        self.display_name = "商业销售专家"
        self.emoji = "🏪"
        self.workspace = Path(workspace) if workspace else Path.home() / ".openclaw" / "workspace-commercial-sales"
        self.model = "qwen3.5-plus"
        
        self.workspace.mkdir(parents=True, exist_ok=True)
        
        self.skills = [
            "web_search_skill",
            "competitor_scraper_skill",
            "investment_calculator_skill"
        ]
        
        self.triggers = [
            "商铺",
            "摊位",
            "商业销售",
            "不良资产",
            "商业地产",
            "商铺投资",
            "菜场摊位"
        ]
    
    def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        context = context or {}
        
        if "搜索" in task or "市场" in task:
            return self._search_market(task, context)
        elif "文案" in task or "内容" in task:
            return self._create_content(task, context)
        elif "客户" in task or "投资" in task:
            return self._analyze_customer(task, context)
        else:
            return self._general_response(task, context)
    
    def _search_market(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "success",
            "agent": self.name,
            "action": "market_search",
            "message": f"🏪 正在搜索商业地产情报...\n\n任务：{task}",
            "next_steps": ["搜索市场动态", "整理结果", "推送简报"]
        }
    
    def _create_content(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "success",
            "agent": self.name,
            "action": "content_creation",
            "message": f"🏪 正在创作商业销售内容...\n\n任务：{task}",
            "next_steps": ["分析卖点", "投资回报测算", "创作文案"]
        }
    
    def _analyze_customer(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "success",
            "agent": self.name,
            "action": "customer_analysis",
            "message": f"🏪 正在分析投资客户...\n\n任务：{task}",
            "next_steps": ["客户画像", "选址建议", "回报测算", "话术建议"]
        }
    
    def _general_response(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "success",
            "agent": self.name,
            "action": "general",
            "message": f"🏪 商业销售专家收到任务：{task}",
            "next_steps": ["识别任务", "调用技能", "返回结果"]
        }
    
    def get_status(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "display_name": self.display_name,
            "emoji": self.emoji,
            "model": self.model,
            "workspace": str(self.workspace),
            "skills": self.skills,
            "triggers": self.triggers,
            "status": "active"
        }


__all__ = ["CommercialSalesAgent"]
