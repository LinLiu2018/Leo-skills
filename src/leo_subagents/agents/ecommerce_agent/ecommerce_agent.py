"""
Ecommerce Agent
===============
电商代理 - 专注AI眼镜电商、竞品分析、爆款文案生成
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


class EcommerceAgent(BaseAgent, EvolvableSkill):
    """
    Ecommerce Agent
    ===============
    电商专业代理，擅长：
    - 竞品数据抓取与分析
    - 爆款文案生成
    - 选品分析
    - 营销策略制定
    """

    ACTIVATION_KEYWORDS = ["电商", "眼镜", "竞品", "爆款", "文案", "选品", "AI眼镜", "带货"]

    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.capabilities = {
            "competitor_analysis": "research_assistant_skill",
            "copywriting": "content_layout_leo_skill",
            "web_search": "web_search_skill",
            "product_analysis": "research_assistant_skill",
        }

        # 初始化进化能力
        evolution_path = Path(__file__).parent / "evolution.json"
        EvolvableSkill.__init__(self, config.name, evolution_path)

    def can_handle(self, task: str) -> float:
        """判断是否能处理此任务"""
        task_lower = task.lower()

        keyword_matches = sum(1 for kw in self.ACTIVATION_KEYWORDS if kw in task_lower)

        capability_score = 0.0
        if any(kw in task_lower for kw in ["眼镜", "ai眼镜", "电商"]):
            capability_score += 0.4
        if any(kw in task_lower for kw in ["竞品", "对标", "分析"]):
            capability_score += 0.3
        if any(kw in task_lower for kw in ["文案", "爆款", "标题"]):
            capability_score += 0.3

        score = min(1.0, 0.3 + keyword_matches * 0.1 + capability_score)
        return score

    def execute(self, task: str, **kwargs) -> Dict[str, Any]:
        """执行电商相关任务"""
        task_type = self._determine_task_type(task, **kwargs)

        if task_type == "analysis":
            return self._handle_analysis_task(task, **kwargs)
        elif task_type == "copywriting":
            return self._handle_copywriting_task(task, **kwargs)
        elif task_type == "product":
            return self._handle_product_task(task, **kwargs)
        else:
            return self._handle_general_task(task, **kwargs)

    def _determine_task_type(self, task: str, **kwargs) -> str:
        """确定任务类型"""
        task_lower = task.lower()

        if any(kw in task_lower for kw in ["竞品", "分析", "调研", "对标"]):
            return "analysis"
        elif any(kw in task_lower for kw in ["文案", "爆款", "标题", "脚本"]):
            return "copywriting"
        elif any(kw in task_lower for kw in ["选品", "产品", "眼镜"]):
            return "product"
        else:
            return "general"

    def _handle_analysis_task(self, task: str, **kwargs) -> Dict[str, Any]:
        """处理竞品分析任务 - 真正调用skill执行"""
        steps_executed = []
        results = []

        # 步骤1: 识别竞品并搜索
        try:
            if self.has_skill("web_search_skill"):
                search_result = self.use_skill(
                    "web_search_skill",
                    "search",
                    query=f"{task} 竞品分析",
                    max_results=10
                )
                steps_executed.append("识别竞品")
                results.append({"step": "competitor_search", "result": search_result})
        except Exception as e:
            results.append({"step": "competitor_search", "error": str(e)})

        # 步骤2: 深度研究竞品
        try:
            if self.has_skill("research_assistant_skill"):
                research_result = self.use_skill(
                    "research_assistant_skill",
                    "research",
                    topic=f"{task} 竞品深度分析",
                    depth=2
                )
                steps_executed.append("收集竞品数据")
                results.append({"step": "competitor_research", "result": research_result})
        except Exception as e:
            results.append({"step": "competitor_research", "error": str(e)})

        # 步骤3: 数据分析
        try:
            if self.has_skill("data_analyzer_skill"):
                analysis_result = self.use_skill(
                    "data_analyzer_skill",
                    "analyze",
                    data=results,
                    analysis_type="competitor"
                )
                steps_executed.append("分析评价反馈")
                results.append({"step": "data_analysis", "result": analysis_result})
        except Exception as e:
            results.append({"step": "data_analysis", "error": str(e)})

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

    def _handle_copywriting_task(self, task: str, **kwargs) -> Dict[str, Any]:
        """处理文案生成任务 - 真正调用skill执行"""
        steps_executed = []
        results = []

        # 获取进化经验
        experience = self.get_experience_context()

        # 步骤1: 分析痛点 - 使用web搜索获取用户痛点
        try:
            if self.has_skill("web_search_skill"):
                pain_point_search = self.use_skill(
                    "web_search_skill",
                    "search",
                    query=f"{task} 用户痛点 差评",
                    max_results=5
                )
                steps_executed.append("分析痛点")
                results.append({"step": "pain_point_analysis", "result": pain_point_search})
        except Exception as e:
            results.append({"step": "pain_point_analysis", "error": str(e)})

        # 步骤2: 提取卖点 - 使用research分析
        try:
            if self.has_skill("research_assistant_skill"):
                research_result = self.use_skill(
                    "research_assistant_skill",
                    "research",
                    topic=f"{task} 产品卖点分析",
                    depth=1
                )
                steps_executed.append("提取卖点")
                results.append({"step": "feature_extraction", "result": research_result})
        except Exception as e:
            results.append({"step": "feature_extraction", "error": str(e)})

        # 步骤3: 生成文案
        try:
            if self.has_skill("content_layout_leo_skill"):
                content = kwargs.get("product_info", task)
                copywriting_result = self.use_skill(
                    "content_layout_leo_skill",
                    "layout",
                    content=content,
                    template="ecommerce",
                    experience=experience
                )
                steps_executed.append("生成多版本文案")
                results.append({"step": "copywriting", "result": copywriting_result})
        except Exception as e:
            results.append({"step": "copywriting", "error": str(e)})

        result = {
            "task": task,
            "type": "copywriting",
            "steps": steps_executed,
            "results": results,
            "skills_used": ["web_search_skill", "research_assistant_skill", "content_layout_leo_skill"],
            "status": "completed" if steps_executed else "failed",
        }

        # 注入进化经验
        if experience:
            result["experience_applied"] = experience
            result["notes"] = "Applied accumulated copywriting tips."

        self.log_task(task, result)
        return result

    def _handle_product_task(self, task: str, **kwargs) -> Dict[str, Any]:
        """处理选品/产品任务 - 真正调用skill执行"""
        steps_executed = []
        results = []

        # 步骤1: 搜索热门产品
        try:
            if self.has_skill("web_search_skill"):
                search_result = self.use_skill(
                    "web_search_skill",
                    "search",
                    query=f"{task} 热门产品 销量排行榜",
                    max_results=10
                )
                steps_executed.append("搜索热门产品")
                results.append({"step": "hot_products_search", "result": search_result})
        except Exception as e:
            results.append({"step": "hot_products_search", "error": str(e)})

        # 步骤2: 分析市场趋势
        try:
            if self.has_skill("research_assistant_skill"):
                trend_result = self.use_skill(
                    "research_assistant_skill",
                    "research",
                    topic=f"{task} 市场趋势分析",
                    depth=2
                )
                steps_executed.append("分析市场趋势")
                results.append({"step": "trend_analysis", "result": trend_result})
        except Exception as e:
            results.append({"step": "trend_analysis", "error": str(e)})

        # 步骤3: 评估利润空间
        try:
            if self.has_skill("data_analyzer_skill"):
                profit_analysis = self.use_skill(
                    "data_analyzer_skill",
                    "analyze",
                    data=results,
                    analysis_type="profit"
                )
                steps_executed.append("评估利润空间")
                results.append({"step": "profit_analysis", "result": profit_analysis})
        except Exception as e:
            results.append({"step": "profit_analysis", "error": str(e)})

        result = {
            "task": task,
            "type": "product",
            "steps": steps_executed,
            "results": results,
            "skills_used": ["web_search_skill", "research_assistant_skill", "data_analyzer_skill"],
            "status": "completed" if steps_executed else "failed",
        }

        self.log_task(task, result)
        return result

    def _handle_general_task(self, task: str, **kwargs) -> Dict[str, Any]:
        """处理通用任务"""
        result = {
            "task": task,
            "type": "general",
            "message": "电商通用任务处理",
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
Ecommerce Agent 帮助
===================

专业领域: AI眼镜电商、内容电商

能力:
1. 竞品分析 - 抓取竞品数据和评价
2. 爆款文案 - 生成高转化率电商文案
3. 选品分析 - AI眼镜市场趋势分析
4. 营销策略 - 制定电商推广方案

激活关键词:
{', '.join(self.ACTIVATION_KEYWORDS)}

使用示例:
- agent.execute("分析Ray-Ban Meta眼镜竞品")
- agent.execute("生成AI眼镜爆款小红书文案")
- agent.execute("调研智能眼镜市场趋势")

进化能力:
该 Agent 具备自我进化能力，会记录并复用过往经验。
存档位置: {self.evolution_path}
"""


# 注册到工厂
AgentFactory.register_agent_class("ecommerce", EcommerceAgent)


if __name__ == "__main__":
    config = AgentConfig(
        name="ecommerce-agent",
        type="ecommerce",
        priority=6,
        skills=[],
        description="电商专业代理",
    )

    agent = EcommerceAgent(config)

    print("能力判断测试:")
    print(f"- 竞品分析: {agent.can_handle('分析竞品数据')}")
    print(f"- 文案生成: {agent.can_handle('生成爆款文案')}")
    print(f"- AI眼镜: {agent.can_handle('AI眼镜选品')}")

    print("\n进化能力测试:")
    print(f"- 初始经验: {agent.get_tips()}")
    agent.learn("写小红书文案时，标题必须包含emoji")
    print(f"- 学习后经验: {agent.get_tips()}")

    print(agent.get_help_text())
