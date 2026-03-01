"""
RealEstate Agent
================
房地产代理 - 专注房地产市场分析、项目营销、政策追踪
"""

import sys
from pathlib import Path
from typing import Any, Dict

# 添加父目录到路径
parent_path = Path(__file__).parent.parent.parent.parent
if str(parent_path) not in sys.path:
    sys.path.insert(0, str(parent_path))

from leo_subagents.agents.base_agent import AgentConfig, AgentFactory, BaseAgent
from leo_skills.core.evolution.base import EvolvableSkill


class RealEstateAgent(BaseAgent, EvolvableSkill):
    """
    RealEstate Agent
    ================
    房地产专业代理，擅长：
    - 房地产市场分析
    - 项目营销文档生成
    - 政策追踪和解读
    - 竞品分析
    """

    ACTIVATION_KEYWORDS = ["房地产", "楼盘", "项目", "营销", "政策", "市场", "竞品", "地产"]

    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.capabilities = {
            "market_analysis": "research_assistant_skill",
            "marketing_docs": "project_marketing_doc_generator_skill",
            "news_publishing": "realestate_news_publisher_skill",
            "web_search": "web_search_skill",
        }

        # 初始化进化能力
        # 经验存档位于 agent 同级目录
        evolution_path = Path(__file__).parent / "evolution.json"
        EvolvableSkill.__init__(self, config.name, evolution_path)

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
        """处理营销任务 - 真正调用skill执行"""
        steps_executed = []
        results = []

        # 步骤1: 收集项目信息
        try:
            if self.has_skill("web_search_skill"):
                search_result = self.use_skill("web_search_skill", "search", query=task, max_results=5)
                steps_executed.append("收集项目信息")
                results.append({"step": "search", "result": search_result})
        except Exception as e:
            results.append({"step": "search", "error": str(e)})

        # 步骤2: 生成营销文档
        try:
            if self.has_skill("project_marketing_doc_generator_skill"):
                doc_result = self.use_skill(
                    "project_marketing_doc_generator_skill",
                    "generate",
                    project_name=kwargs.get("project_name", task),
                    project_type="realestate",
                    target_audience=kwargs.get("audience", "潜在购房者")
                )
                steps_executed.append("生成营销文案")
                results.append({"step": "generate_doc", "result": doc_result})
        except Exception as e:
            results.append({"step": "generate_doc", "error": str(e)})

        # 步骤3: 优化内容布局
        try:
            if self.has_skill("content_layout_leo_skill"):
                layout_result = self.use_skill(
                    "content_layout_leo_skill",
                    "layout",
                    content=results[-1].get("result", "") if results else "",
                    template="marketing"
                )
                steps_executed.append("优化内容布局")
                results.append({"step": "layout", "result": layout_result})
        except Exception as e:
            results.append({"step": "layout", "error": str(e)})

        result = {
            "task": task,
            "type": "marketing",
            "steps": steps_executed,
            "results": results,
            "skills_used": ["web_search_skill", "project_marketing_doc_generator_skill", "content_layout_leo_skill"],
            "status": "completed" if steps_executed else "failed",
        }

        # 注入进化经验
        experience = self.get_experience_context()
        if experience:
            result["experience_applied"] = experience

        self.log_task(task, result)
        return result

    def _handle_analysis_task(self, task: str, **kwargs) -> Dict[str, Any]:
        """处理分析任务 - 真正调用skill执行"""
        steps_executed = []
        results = []

        # 步骤1: 搜索市场信息
        try:
            if self.has_skill("web_search_skill"):
                search_result = self.use_skill(
                    "web_search_skill",
                    "search",
                    query=f"{task} 房地产市场",
                    max_results=10
                )
                steps_executed.append("搜索市场信息")
                results.append({"step": "market_search", "result": search_result})
        except Exception as e:
            results.append({"step": "market_search", "error": str(e)})

        # 步骤2: 收集竞品数据
        try:
            if self.has_skill("research_assistant_skill"):
                research_result = self.use_skill(
                    "research_assistant_skill",
                    "research",
                    topic=f"{task} 竞品分析",
                    depth=2
                )
                steps_executed.append("收集竞品数据")
                results.append({"step": "competitor_research", "result": research_result})
        except Exception as e:
            results.append({"step": "competitor_research", "error": str(e)})

        # 步骤3: 分析市场趋势
        try:
            if self.has_skill("data_analyzer_skill"):
                analysis_result = self.use_skill(
                    "data_analyzer_skill",
                    "analyze",
                    data=results,
                    analysis_type="trend"
                )
                steps_executed.append("分析市场趋势")
                results.append({"step": "trend_analysis", "result": analysis_result})
        except Exception as e:
            results.append({"step": "trend_analysis", "error": str(e)})

        result = {
            "task": task,
            "type": "analysis",
            "steps": steps_executed,
            "results": results,
            "skills_used": ["web_search_skill", "research_assistant_skill", "data_analyzer_skill"],
            "status": "completed" if steps_executed else "failed",
        }

        self.log_task(task, result)
        return result

    def _handle_policy_task(self, task: str, **kwargs) -> Dict[str, Any]:
        """处理政策任务 - 真正调用skill执行"""
        steps_executed = []
        results = []

        # 步骤1: 搜索最新政策
        try:
            if self.has_skill("web_search_skill"):
                search_result = self.use_skill(
                    "web_search_skill",
                    "search",
                    query=f"{task} 房地产政策 2024 2025",
                    max_results=10
                )
                steps_executed.append("搜索最新政策")
                results.append({"step": "policy_search", "result": search_result})
        except Exception as e:
            results.append({"step": "policy_search", "error": str(e)})

        # 步骤2: 解读政策内容
        try:
            if self.has_skill("research_assistant_skill"):
                research_result = self.use_skill(
                    "research_assistant_skill",
                    "research",
                    topic=f"{task} 政策解读",
                    depth=2
                )
                steps_executed.append("解读政策内容")
                results.append({"step": "policy_research", "result": research_result})
        except Exception as e:
            results.append({"step": "policy_research", "error": str(e)})

        result = {
            "task": task,
            "type": "policy",
            "steps": steps_executed,
            "results": results,
            "skills_used": ["web_search_skill", "research_assistant_skill"],
            "status": "completed" if steps_executed else "failed",
        }

        self.log_task(task, result)
        return result

    def _handle_general_task(self, task: str, **kwargs) -> Dict[str, Any]:
        """处理通用任务"""
        result = {
            "task": task,
            "type": "general",
            "message": "房地产通用任务处理",
            "status": "completed",
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

进化能力:
该 Agent 具备自我进化能力，会记录并复用过往经验。
存档位置: {self.evolution_path}
"""


# 注册到工厂
AgentFactory.register_agent_class("realestate", RealEstateAgent)


if __name__ == "__main__":
    config = AgentConfig(
        name="realestate-agent",
        type="realestate",
        priority=5,
        skills=[],
        description="房地产专业代理",
    )

    agent = RealEstateAgent(config)

    print("能力判断测试:")
    print(f"- 房地产任务: {agent.can_handle('分析宁波房地产市场')}")
    print(f"- 营销任务: {agent.can_handle('生成项目营销手册')}")
    print(f"- 政策任务: {agent.can_handle('追踪房地产政策')}")

    print("\n进化能力测试:")
    print(f"- 初始经验: {agent.get_tips()}")
    agent.learn("对于宁波市场，重点关注海曙区学区房政策")
    print(f"- 学习后经验: {agent.get_tips()}")

    print(agent.get_help_text())
