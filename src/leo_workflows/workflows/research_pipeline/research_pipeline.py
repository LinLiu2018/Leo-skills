"""
Research Pipeline - 研究调研工作流
====================================
提供研究调研全流程自动化：
- 主题分析与关键词提取
- 多源信息收集
- 资料整理与分类
- 深度分析
- 报告生成
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


class ResearchPipeline:
    """
    研究调研工作流
    ==============
    提供研究调研全流程自动化
    """

    def __init__(self):
        """初始化工作流"""
        self.workflow_dir = Path(__file__).parent
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """加载工作流配置"""
        config_path = self.workflow_dir / "workflow.yaml"
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        return {}

    def run(
        self,
        orchestrator,
        topic: str,
        research_type: str = "general",
        depth: str = "standard",
        sources: List[str] = None,
        output_format: str = "report",
        **kwargs
    ) -> Dict[str, Any]:
        """
        执行研究调研工作流

        Args:
            orchestrator: 编排器实例
            topic: 研究主题
            research_type: 研究类型 (general/market/technology/competitor)
            depth: 研究深度 (quick/standard/deep)
            sources: 数据源列表
            output_format: 输出格式 (report/summary/both)
            **kwargs: 其他参数

        Returns:
            执行结果
        """
        # 验证必要参数
        if not topic:
            raise ValueError("缺少必要参数: topic")

        # 准备输入参数
        inputs = {
            "topic": topic,
            "research_type": research_type,
            "depth": depth,
            "sources": sources or ["web", "academic", "news"],
            "output_format": output_format,
            **kwargs
        }

        # 执行工作流
        return orchestrator.run_workflow(self.config, inputs)

    def quick_research(
        self,
        orchestrator,
        topic: str,
    ) -> Dict[str, Any]:
        """
        快速研究（概览级）

        Args:
            orchestrator: 编排器实例
            topic: 研究主题

        Returns:
            执行结果
        """
        return self.run(
            orchestrator,
            topic=topic,
            research_type="general",
            depth="quick",
            output_format="summary",
        )

    def deep_research(
        self,
        orchestrator,
        topic: str,
        sources: List[str] = None,
    ) -> Dict[str, Any]:
        """
        深度研究（全面调研）

        Args:
            orchestrator: 编排器实例
            topic: 研究主题
            sources: 数据源列表

        Returns:
            执行结果
        """
        return self.run(
            orchestrator,
            topic=topic,
            research_type="general",
            depth="deep",
            sources=sources or ["web", "academic", "news", "industry", "social"],
            output_format="both",
        )

    def market_research(
        self,
        orchestrator,
        topic: str,
        industry: str = None,
    ) -> Dict[str, Any]:
        """
        市场研究

        Args:
            orchestrator: 编排器实例
            topic: 研究主题
            industry: 行业领域

        Returns:
            执行结果
        """
        return self.run(
            orchestrator,
            topic=topic,
            research_type="market",
            depth="standard",
            output_format="report",
            industry=industry,
        )

    def competitor_research(
        self,
        orchestrator,
        company_name: str,
        competitors: List[str] = None,
    ) -> Dict[str, Any]:
        """
        竞品研究

        Args:
            orchestrator: 编排器实例
            company_name: 公司名称
            competitors: 竞争对手列表

        Returns:
            执行结果
        """
        return self.run(
            orchestrator,
            topic=f"竞品分析: {company_name}",
            research_type="competitor",
            depth="standard",
            output_format="report",
            target_company=company_name,
            competitors=competitors or [],
        )

    def technology_research(
        self,
        orchestrator,
        technology: str,
        include_trends: bool = True,
    ) -> Dict[str, Any]:
        """
        技术研究

        Args:
            orchestrator: 编排器实例
            technology: 技术名称
            include_trends: 是否包含趋势分析

        Returns:
            执行结果
        """
        return self.run(
            orchestrator,
            topic=technology,
            research_type="technology",
            depth="deep" if include_trends else "standard",
            output_format="report",
            include_trends=include_trends,
        )

    def get_info(self) -> Dict[str, Any]:
        """
        获取工作流信息

        Returns:
            工作流基本信息
        """
        return {
            "name": self.config.get("name", "research-pipeline"),
            "description": self.config.get("description", "研究调研工作流"),
            "version": self.config.get("version", "1.0.0"),
            "steps_count": len(self.config.get("steps", [])),
            "triggers": self.config.get("triggers", []),
            "inputs": list(self.config.get("inputs", {}).keys()),
            "outputs": list(self.config.get("outputs", {}).keys()),
            "supported_research_types": ["general", "market", "technology", "competitor"],
            "supported_depths": ["quick", "standard", "deep"],
        }

    def get_required_agents(self) -> List[str]:
        """获取所需代理"""
        return ["research_agent"]

    def get_required_skills(self) -> List[str]:
        """获取所需技能"""
        return ["web_search_skill", "business_research_skill"]


# 便捷函数
def create_pipeline() -> ResearchPipeline:
    """创建工作流实例"""
    return ResearchPipeline()


# 导出实例
research_pipeline = ResearchPipeline()
