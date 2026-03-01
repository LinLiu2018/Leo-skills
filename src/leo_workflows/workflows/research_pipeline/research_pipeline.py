"""
Research Pipeline - 研究调研工作流
====================================
提供研究调研全流程自动化：
- 主题分析与关键词提取
- 多源信息收集
- 资料整理与分类
- 深度分析
- 报告生成

配置来源：definitions/research_pipeline.yaml（统一 YAML）
"""

from typing import Any, Dict, List

from leo_workflows.pipeline_base import PipelineBase


class ResearchPipeline(PipelineBase):
    """
    研究调研工作流
    ==============
    提供研究调研全流程自动化。
    配置统一从 definitions/research_pipeline.yaml 加载。
    """

    yaml_name = "research_pipeline"

    def run(
        self,
        orchestrator,
        topic: str = "",
        research_type: str = "general",
        depth: str = "standard",
        sources: List[str] = None,
        output_format: str = "report",
        **kwargs
    ) -> Dict[str, Any]:
        if not topic:
            raise ValueError("缺少必要参数: topic")

        inputs = {
            "topic": topic,
            "research_type": research_type,
            "depth": depth,
            "sources": sources or ["web", "academic", "news"],
            "output_format": output_format,
            **kwargs
        }
        return orchestrator.run_workflow(self.config, inputs)

    # ---- 领域快捷方法 ----

    def quick_research(self, orchestrator, topic: str) -> Dict[str, Any]:
        """快速研究（概览级）"""
        return self.run(orchestrator, topic=topic, depth="quick", output_format="summary")

    def deep_research(self, orchestrator, topic: str, sources: List[str] = None) -> Dict[str, Any]:
        """深度研究（全面调研）"""
        return self.run(
            orchestrator, topic=topic, depth="deep",
            sources=sources or ["web", "academic", "news", "industry", "social"],
            output_format="both",
        )

    def market_research(self, orchestrator, topic: str, industry: str = None) -> Dict[str, Any]:
        """市场研究"""
        return self.run(orchestrator, topic=topic, research_type="market", industry=industry)

    def competitor_research(self, orchestrator, company_name: str, competitors: List[str] = None) -> Dict[str, Any]:
        """竞品研究"""
        return self.run(
            orchestrator, topic=f"竞品分析: {company_name}",
            research_type="competitor", target_company=company_name,
            competitors=competitors or [],
        )

    def technology_research(self, orchestrator, technology: str, include_trends: bool = True) -> Dict[str, Any]:
        """技术研究"""
        return self.run(
            orchestrator, topic=technology, research_type="technology",
            depth="deep" if include_trends else "standard",
            include_trends=include_trends,
        )

    def get_required_skills(self) -> List[str]:
        return ["web_search_skill", "business_research_skill"]


# 便捷函数
def create_pipeline() -> ResearchPipeline:
    """创建工作流实例"""
    return ResearchPipeline()


# 导出实例
research_pipeline = ResearchPipeline()
