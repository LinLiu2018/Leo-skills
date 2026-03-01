"""
RealEstate Pipeline - 房产营销工作流
====================================
配置来源：definitions/ 目录（统一 YAML，向后兼容 workflow.yaml）
"""

from typing import Any, Dict, List, Optional

from leo_workflows.pipeline_base import PipelineBase


class RealEstatePipeline(PipelineBase):
    """房产营销工作流，配置统一从 definitions/ 或 workflow.yaml 加载。"""

    yaml_name = "realestate_pipeline"

    def run(self, orchestrator, project_name: str = "", location: str = "",
            project_type: str = "residential", target_audience: str = "刚需改善",
            platforms: Optional[list] = None, **kwargs) -> Dict[str, Any]:
        if not project_name:
            raise ValueError("缺少必要参数: project_name")
        if not location:
            raise ValueError("缺少必要参数: location")
        inputs = {"project_name": project_name, "location": location,
                  "project_type": project_type, "target_audience": target_audience,
                  "platforms": platforms or ["wechat", "xiaohongshu"]}
        return orchestrator.run_workflow(self.config, inputs)


def create_pipeline() -> RealEstatePipeline:
    return RealEstatePipeline()
