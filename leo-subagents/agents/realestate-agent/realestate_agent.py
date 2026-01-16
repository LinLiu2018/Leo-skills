"""
RealEstate Agent
================
房地产代理 - 专注房地产市场分析、项目营销、政策追踪
"""

from typing import Dict, Any, List
import sys
from pathlib import Path

# 添加父目录到路径
parent_path = Path(__file__).parent.parent.parent
if str(parent_path) not in sys.path:
    sys.path.insert(0, str(parent_path))

from leo_subagents.agents.base_agent import BaseAgent, AgentConfig, AgentFactory


class RealEstateAgent(BaseAgent):
    """
    RealEstate Agent
    ================
    房地产专业代理，擅长：
    - 房地产市场分析
    - 项目营销文档生成
    - 政策追踪和解读
    - 竞品分析
    """

    ACTIVATION_KEYWORDS = [
        "房地产", "楼盘", "项目", "营销",
        "政策", "市场", "竞品", "地产"
    ]

    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.capabilities = {
            "market_analysis": "research-assistant-cskill",
            "marketing_docs": "project-marketing-doc-generator-cskill",
            "news_publishing": "realestate-news-publisher-cskill",
            "web_search": "web-search-cskill"
        }

    def can_handle(self, task: str) -> float:
        """判断是否能处理此任务"""
        task_lower = task.lower()

        keyword_matches = sum(1 for kw in self.ACTIVATION_KEYWORDS if kw in task_lower)

        capability_score = 0.0
        if any(kw in task_lower for kw in ["房地产", "楼盘", "项目"]):
            capability_score += 0.4
        if any(kw in task_lower for kw in ["营销", "文案", "推广"]):
            capability_score += 0.3
        if any(kw in task_lower for kw in ["政策", "市场", "分析"]):
            capability_score += 0.2

        score = min(1.0, 0.3 + keyword_matches * 0.1 + capability_score)
        return score

    def execute(self, task: str, **kwargs) -> Dict[str, Any]:
        """执行房地产相关任务"""
        task_type = self._determine_task_type(task, **kwargs)

        if task_type == "marketing":
            return self._handle_marketing_task(task, **kwargs)
        elif task_type == "analysis":
            return self._handle_analysis_task(task, **kwargs)
        elif task_type == "policy":
            return self._handle_policy_task(task, **kwargs)
        else:
            return self._handle_general_task(task, **kwargs)

    def _determine_task_type(self, task: str, **kwargs) -> str:
        """确定任务类型"""
        task_lower = task.lower()

        if any(kw in task_lower for kw in ["营销", "文案", "推广", "宣传"]):
            return "marketing"
        elif any(kw in task_lower for kw in ["分析", "市场", "竞品", "调研"]):
            return "analysis"
        elif any(kw in task_lower for kw in ["政策", "法规", "规定"]):
            return "policy"
        else:
            return "general"

    def _handle_marketing_task(self, task: str, **kwargs) -> Dict[str, Any]:
        """处理营销任务"""
        result = {
            "task": task,
            "type": "marketing",
            "steps": [
                "收集项目信息",
                "分析目标客户",
                "生成营销文案",
                "优化内容布局"
            ],
            "skills_used": [
                "project-marketing-doc-generator-cskill",
                "content-layout-leo-cskill"
            ],
            "status": "completed"
        }

        self.log_task(task, result)
        return result

    def _handle_analysis_task(self, task: str, **kwargs) -> Dict[str, Any]:
        """处理分析任务"""
        result = {
            "task": task,
            "type": "analysis",
            "steps": [
                "搜索市场信息",
                "收集竞品数据",
                "分析市场趋势",
                "生成分析报告"
            ],
            "skills_used": [
                "web-search-cskill",
                "research-assistant-cskill"
            ],
            "status": "completed"
        }

        self.log_task(task, result)
        return result

    def _handle_policy_task(self, task: str, **kwargs) -> Dict[str, Any]:
        """处理政策任务"""
        result = {
            "task": task,
            "type": "policy",
            "steps": [
                "搜索最新政策",
                "解读政策内容",
                "分析影响范围",
                "生成政策报告"
            ],
            "skills_used": [
                "web-search-cskill",
                "research-assistant-cskill"
            ],
            "status": "completed"
        }

        self.log_task(task, result)
        return result

    def _handle_general_task(self, task: str, **kwargs) -> Dict[str, Any]:
        """处理通用任务"""
        result = {
            "task": task,
            "type": "general",
            "message": "房地产通用任务处理",
            "status": "completed"
        }

        self.log_task(task, result)
        return result

    def get_capabilities(self) -> Dict[str, str]:
        """获取能力列表"""
        return self.capabilities

    def get_help_text(self) -> str:
        """获取帮助文本"""
        return f"""
RealEstate Agent 帮助
====================

专业领域: 房地产市场

能力:
1. 市场分析 - 房地产市场趋势分析
2. 营销文档 - 项目营销手册生成
3. 政策追踪 - 房地产政策解读
4. 竞品分析 - 竞品项目对比分析

激活关键词:
{', '.join(self.ACTIVATION_KEYWORDS)}

使用示例:
- agent.execute("分析宁波房地产市场")
- agent.execute("生成淮安建华官园营销手册")
- agent.execute("追踪最新房地产政策")
"""


# 注册到工厂
AgentFactory.register_agent_class("realestate", RealEstateAgent)


if __name__ == "__main__":
    config = AgentConfig(
        name="realestate-agent",
        type="realestate",
        priority=5,
        skills=[],
        description="房地产专业代理"
    )

    agent = RealEstateAgent(config)

    print("能力判断测试:")
    print(f"- 房地产任务: {agent.can_handle('分析宁波房地产市场')}")
    print(f"- 营销任务: {agent.can_handle('生成项目营销手册')}")
    print(f"- 政策任务: {agent.can_handle('追踪房地产政策')}")

    print(agent.get_help_text())
