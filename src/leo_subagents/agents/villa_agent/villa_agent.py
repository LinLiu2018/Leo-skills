"""
Villa Agent - 别墅事业部代理

宁波度假别墅专家，专注别墅房源管理、客户跟进和内容创作。
"""

from typing import Dict, Any, Optional, List
import json
from pathlib import Path

# 自动记忆支持
from leo_memory import auto_memorize


@auto_memorize
class VillaAgent:
    """
    别墅事业部代理
    
    职责:
    - 市场情报：每日监控小红书/抖音别墅内容
    - 内容创作：别墅卖点提炼、短视频脚本、文案
    - 客户跟进：客户画像分析、话术建议
    - 数据复盘：内容效果分析、转化漏斗
    """
    
    def __init__(self, workspace: Optional[str] = None):
        """
        初始化别墅代理
        
        Args:
            workspace: 工作空间路径，默认 ~/.openclaw/workspace-villa
        """
        self.name = "villa_agent"
        self.display_name = "别墅专家"
        self.emoji = "🏡"
        self.workspace = Path(workspace) if workspace else Path.home() / ".openclaw" / "workspace-villa"
        self.model = "qwen3.5-plus"
        
        # 确保工作空间存在
        self.workspace.mkdir(parents=True, exist_ok=True)
        
        # 依赖的 Skills
        self.skills = [
            "web_search_skill",
            "video_monitor_skill",
            "creative_agent",
            "realestate_news_publisher_skill"
        ]
        
        # 触发词
        self.triggers = [
            "别墅",
            "度假别墅",
            "养老别墅",
            "宁波别墅",
            "别墅房源",
            "别墅客户"
        ]
    
    def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        执行任务
        
        Args:
            task: 任务描述
            context: 上下文信息
            
        Returns:
            执行结果
        """
        context = context or {}
        
        # 任务分类
        if "搜索" in task or "查询" in task or "动态" in task:
            return self._search_market_intelligence(task, context)
        elif "监控" in task or "小红书" in task or "抖音" in task:
            return self._monitor_competitor_content(task, context)
        elif "文案" in task or "内容" in task or "脚本" in task:
            return self._create_content(task, context)
        elif "客户" in task or "画像" in task or "话术" in task:
            return self._analyze_customer(task, context)
        else:
            return self._general_response(task, context)
    
    def _search_market_intelligence(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """搜索市场情报"""
        return {
            "status": "success",
            "agent": self.name,
            "action": "market_search",
            "message": f"🏡 正在搜索宁波别墅市场情报...\n\n任务：{task}\n\n将调用 web_search_skill 执行搜索，结果将通过飞书推送。",
            "next_steps": [
                "调用 web_search_skill 搜索宁波别墅最新动态",
                "整理搜索结果并生成简报",
                "通过飞书推送给用户"
            ]
        }
    
    def _monitor_competitor_content(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """监控竞品内容"""
        return {
            "status": "success",
            "agent": self.name,
            "action": "competitor_monitor",
            "message": f"🏡 正在执行别墅内容监控...\n\n任务：{task}\n\n将调用 video_monitor_skill 监控小红书/抖音别墅内容。",
            "next_steps": [
                "调用 video_monitor_skill 监控小红书别墅内容",
                "调用 video_monitor_skill 监控抖音别墅内容",
                "分析热门话题和竞品动态",
                "生成监控日报"
            ]
        }
    
    def _create_content(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """创作内容"""
        return {
            "status": "success",
            "agent": self.name,
            "action": "content_creation",
            "message": f"🏡 正在创别墅内容...\n\n任务：{task}\n\n将结合别墅卖点和目标客户创作内容。",
            "next_steps": [
                "分析别墅核心卖点",
                "确定目标客户群体",
                "创作适配平台的内容（朋友圈/小红书/抖音）",
                "生成配图建议"
            ]
        }
    
    def _analyze_customer(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """客户分析"""
        return {
            "status": "success",
            "agent": self.name,
            "action": "customer_analysis",
            "message": f"🏡 正在分析别墅客户...\n\n任务：{task}\n\n将生成客户画像和跟进建议。",
            "next_steps": [
                "分析客户基本信息",
                "生成客户画像（年龄/职业/需求/预算）",
                "推荐匹配房源",
                "提供跟进话术建议"
            ]
        }
    
    def _general_response(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """通用响应"""
        return {
            "status": "success",
            "agent": self.name,
            "action": "general",
            "message": f"🏡 别墅专家收到任务：{task}\n\n我将根据任务类型调用相应技能处理。",
            "next_steps": [
                "识别任务类型",
                "调用相应技能",
                "返回处理结果"
            ]
        }
    
    def get_status(self) -> Dict[str, Any]:
        """获取代理状态"""
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


# 导出主类
__all__ = ["VillaAgent"]
