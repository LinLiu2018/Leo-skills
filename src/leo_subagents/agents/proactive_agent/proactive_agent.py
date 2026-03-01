"""
Proactive Agent - 主动规划代理
"""

from typing import Dict, Any, Optional, List
from pathlib import Path


class ProactiveAgent:
    """主动规划代理"""
    
    def __init__(self, workspace: Optional[str] = None):
        self.name = "proactive_agent"
        self.display_name = "主动规划"
        self.emoji = "⚡"
        self.workspace = Path(workspace) if workspace else Path.home() / ".openclaw" / "workspace-proactive"
        self.model = "qwen3.5-plus"
        self.workspace.mkdir(parents=True, exist_ok=True)
        
        self.triggers = ["主动", "规划", "帮我安排", "制定计划", "建议"]
    
    def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        context = context or {}
        
        if "规划" in task or "计划" in task or "安排" in task:
            return self._plan_task(task, context)
        elif "建议" in task or "推荐" in task:
            return self._suggest(task, context)
        elif "优化" in task or "改进" in task:
            return self._optimize(task, context)
        else:
            return self._general_response(task, context)
    
    def _plan_task(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "success",
            "agent": self.name,
            "action": "plan_task",
            "message": f"⚡ 正在制定计划...\n\n任务：{task}",
            "next_steps": ["分解任务", "分配优先级", "制定时间表"]
        }
    
    def _suggest(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "success",
            "agent": self.name,
            "action": "suggest",
            "message": f"⚡ 正在生成建议...\n\n任务：{task}",
            "next_steps": ["分析需求", "生成方案", "对比优劣"]
        }
    
    def _optimize(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "success",
            "agent": self.name,
            "action": "optimize",
            "message": f"⚡ 正在优化方案...\n\n任务：{task}",
            "next_steps": ["分析现状", "识别瓶颈", "提出优化"]
        }
    
    def _general_response(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "success",
            "agent": self.name,
            "action": "general",
            "message": f"⚡ 主动规划代理收到任务：{task}",
            "next_steps": ["识别任务", "主动规划", "执行优化"]
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


__all__ = ["ProactiveAgent"]
