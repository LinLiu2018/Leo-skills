"""
Ecommerce Pipeline - 电商分析工作流
===================================
配置来源：definitions/ 目录（统一 YAML，向后兼容 workflow.yaml）
"""

from typing import Any, Dict, List, Optional

from leo_workflows.pipeline_base import PipelineBase


class EcommercePipeline(PipelineBase):
    """电商分析工作流，配置统一从 definitions/ 或 workflow.yaml 加载。"""

    yaml_name = "ecommerce_pipeline"

    def run(self, orchestrator, product_category: str = "", product_name: str = "",
            platforms: Optional[List[str]] = None, analysis_depth: str = "standard",
            output_type: str = "both", **kwargs) -> Dict[str, Any]:
        if not product_category:
            raise ValueError("缺少必要参数: product_category")
        inputs = {"product_category": product_category, "product_name": product_name,
                  "platforms": platforms or ["taobao", "jd", "douyin"],
                  "analysis_depth": analysis_depth, "output_type": output_type}
        return orchestrator.run_workflow(self.config, inputs)

    def quick_analysis(self, orchestrator, product_category: str) -> Dict[str, Any]:
        """快速分析"""
        return self.run(orchestrator, product_category=product_category, analysis_depth="quick", output_type="report")

    def full_analysis(self, orchestrator, product_category: str, product_name: str = "") -> Dict[str, Any]:
        """完整分析"""
        return self.run(orchestrator, product_category=product_category, product_name=product_name,
                        analysis_depth="deep", output_type="both")


def create_pipeline() -> EcommercePipeline:
    return EcommercePipeline()
