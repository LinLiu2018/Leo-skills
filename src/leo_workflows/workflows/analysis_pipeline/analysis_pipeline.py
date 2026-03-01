"""
Analysis Pipeline - 数据分析工作流
==================================
配置来源：definitions/analysis_pipeline.yaml（统一 YAML）
"""

from typing import Any, Dict, List

from leo_workflows.pipeline_base import PipelineBase


class AnalysisPipeline(PipelineBase):
    """数据分析工作流，配置统一从 definitions/analysis_pipeline.yaml 加载。"""

    yaml_name = "analysis_pipeline"

    def run(self, orchestrator, data_source: str = "", analysis_type: str = "descriptive",
            output_format: str = "report", visualization: bool = True, **kwargs) -> Dict[str, Any]:
        if not data_source:
            raise ValueError("缺少必要参数: data_source")
        inputs = {"data_source": data_source, "analysis_type": analysis_type,
                  "output_format": output_format, "visualization": visualization, **kwargs}
        return orchestrator.run_workflow(self.config, inputs)

    def quick_analysis(self, orchestrator, data_source: str) -> Dict[str, Any]:
        """快速分析（描述性统计）"""
        return self.run(orchestrator, data_source=data_source, visualization=False)

    def full_analysis(self, orchestrator, data_source: str, include_visualization: bool = True) -> Dict[str, Any]:
        """完整分析"""
        return self.run(orchestrator, data_source=data_source, analysis_type="comprehensive",
                        output_format="both", visualization=include_visualization)

    def trend_analysis(self, orchestrator, data_source: str, time_column: str = "date", metric: str = "value") -> Dict[str, Any]:
        """趋势分析"""
        return self.run(orchestrator, data_source=data_source, analysis_type="trend",
                        time_column=time_column, metric=metric)

    def comparative_analysis(self, orchestrator, data_source: str, group_by: str, metrics: List[str]) -> Dict[str, Any]:
        """对比分析"""
        return self.run(orchestrator, data_source=data_source, analysis_type="comparative",
                        group_by=group_by, metrics=metrics)

    def get_required_skills(self) -> List[str]:
        return ["data_analyzer_skill"]


def create_pipeline() -> AnalysisPipeline:
    return AnalysisPipeline()

analysis_pipeline = AnalysisPipeline()
