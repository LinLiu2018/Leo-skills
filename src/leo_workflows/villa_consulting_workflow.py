# -*- coding: utf-8 -*-
"""
别墅咨询工作流
==============

完整的别墅客户咨询流程：
1. 客户需求分析
2. 房源匹配推荐
3. 看房安排
4. 跟进反馈
"""

from pathlib import Path
from typing import Any, Dict, Optional

from ..leo_orchestrator.workflow_engine import WorkflowEngine, WorkflowDefinition
from ..leo_subagents.agents.villa_agent.villa_agent import VillaAgent


class VillaConsultingWorkflow:
    """
    别墅咨询工作流

    处理从客户咨询到成交的完整流程
    """

    def __init__(self):
        self.name = "villa_consulting"
        self.display_name = "别墅咨询流程"

        # 创建Agents
        self.agents = {
            "villa_agent": VillaAgent(),
        }

        # 创建引擎
        self.engine = WorkflowEngine(self.agents)

        # 工作流定义路径
        self.workflow_path = Path(__file__).parent / "definitions" / "villa_consulting_workflow.yaml"

    def execute(self, customer_query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        执行别墅咨询工作流

        Args:
            customer_query: 客户咨询内容
            context: 额外上下文

        Returns:
            工作流执行结果
        """
        context = context or {}
        context["task"] = customer_query
        context["workflow_type"] = "villa_consulting"

        # 如果YAML存在则使用，否则使用内置定义
        if self.workflow_path.exists():
            return self.engine.execute_from_yaml(str(self.workflow_path), **context)
        else:
            return self._execute_builtin(context)

    def _execute_builtin(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """使用内置工作流定义执行"""
        workflow = {
            "name": "villa_consulting",
            "description": "别墅咨询完整流程",
            "steps": [
                {
                    "name": "analyze_requirement",
                    "agent": "villa_agent",
                    "description": "分析客户需求",
                },
                {
                    "name": "recommend_properties",
                    "agent": "villa_agent",
                    "description": "推荐匹配房源",
                },
                {
                    "name": "schedule_viewing",
                    "agent": "villa_agent",
                    "description": "安排看房",
                },
            ],
        }
        return self.engine.execute(workflow, **context)

    def get_status(self) -> Dict[str, Any]:
        """获取工作流状态"""
        return {
            "name": self.name,
            "display_name": self.display_name,
            "agents": list(self.agents.keys()),
            "engine_status": "active",
        }


# 便捷函数
def run_villa_consulting(customer_query: str, **kwargs) -> Dict[str, Any]:
    """
    快速运行别墅咨询工作流

    Args:
        customer_query: 客户咨询内容
        **kwargs: 其他参数

    Returns:
        执行结果
    """
    workflow = VillaConsultingWorkflow()
    return workflow.execute(customer_query, context=kwargs)


__all__ = ["VillaConsultingWorkflow", "run_villa_consulting"]
