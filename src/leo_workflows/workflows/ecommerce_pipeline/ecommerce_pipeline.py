"""
Ecommerce Pipeline - 电商分析工作流
===================================
专为电商业务设计的竞品分析和营销工作流封装类
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


class EcommercePipeline:
    """
    电商分析工作流
    ==============
    提供电商竞品分析全流程自动化：
    - 市场趋势调研
    - 多平台竞品分析
    - 选品建议
    - 爆款文案创作
    - 营销策略制定
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
        product_category: str,
        product_name: str = "",
        platforms: Optional[List[str]] = None,
        analysis_depth: str = "standard",
        output_type: str = "both",
    ) -> Dict[str, Any]:
        """
        执行电商分析工作流

        Args:
            orchestrator: 编排器实例
            product_category: 产品类目
            product_name: 具体产品名称（可选）
            platforms: 分析平台列表
            analysis_depth: 分析深度 (quick/standard/deep)
            output_type: 输出类型 (report/copywriting/both)

        Returns:
            执行结果
        """
        # 验证必要参数
        if not product_category:
            raise ValueError("缺少必要参数: product_category")

        # 准备输入参数
        inputs = {
            "product_category": product_category,
            "product_name": product_name,
            "platforms": platforms or ["taobao", "jd", "douyin"],
            "analysis_depth": analysis_depth,
            "output_type": output_type,
        }

        # 执行工作流
        return orchestrator.run_workflow(self.config, inputs)

    def quick_analysis(
        self,
        orchestrator,
        product_category: str,
    ) -> Dict[str, Any]:
        """
        快速分析（只生成报告）

        Args:
            orchestrator: 编排器实例
            product_category: 产品类目

        Returns:
            执行结果
        """
        return self.run(
            orchestrator,
            product_category=product_category,
            analysis_depth="quick",
            output_type="report",
        )

    def full_analysis(
        self,
        orchestrator,
        product_category: str,
        product_name: str = "",
    ) -> Dict[str, Any]:
        """
        完整分析（报告+文案）

        Args:
            orchestrator: 编排器实例
            product_category: 产品类目
            product_name: 具体产品名称

        Returns:
            执行结果
        """
        return self.run(
            orchestrator,
            product_category=product_category,
            product_name=product_name,
            analysis_depth="deep",
            output_type="both",
        )

    def get_info(self) -> Dict[str, Any]:
        """
        获取工作流信息

        Returns:
            工作流基本信息
        """
        return {
            "name": self.config.get("name", "ecommerce-analysis-pipeline"),
            "description": self.config.get("description", ""),
            "version": self.config.get("version", "1.0.0"),
            "steps_count": len(self.config.get("steps", [])),
            "triggers": self.config.get("triggers", []),
            "inputs": list(self.config.get("inputs", {}).keys()),
            "outputs": list(self.config.get("outputs", {}).keys()),
        }


# 便捷函数
def create_pipeline() -> EcommercePipeline:
    """创建电商分析工作流实例"""
    return EcommercePipeline()
