"""
Analysis Pipeline - 数据分析工作流
==================================
提供数据分析全流程自动化：
- 数据采集与验证
- 数据清洗与预处理
- 描述性统计分析
- 趋势分析与对比分析
- 可视化生成
- 分析报告输出
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


class AnalysisPipeline:
    """
    数据分析工作流
    ==============
    提供数据分析全流程自动化
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
        data_source: str,
        analysis_type: str = "descriptive",
        output_format: str = "report",
        visualization: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        执行数据分析工作流

        Args:
            orchestrator: 编排器实例
            data_source: 数据源路径或标识
            analysis_type: 分析类型 (descriptive/trend/comparative/comprehensive)
            output_format: 输出格式 (report/dashboard/both)
            visualization: 是否生成可视化
            **kwargs: 其他参数

        Returns:
            执行结果
        """
        # 验证必要参数
        if not data_source:
            raise ValueError("缺少必要参数: data_source")

        # 准备输入参数
        inputs = {
            "data_source": data_source,
            "analysis_type": analysis_type,
            "output_format": output_format,
            "visualization": visualization,
            **kwargs
        }

        # 执行工作流
        return orchestrator.run_workflow(self.config, inputs)

    def quick_analysis(
        self,
        orchestrator,
        data_source: str,
    ) -> Dict[str, Any]:
        """
        快速分析（描述性统计）

        Args:
            orchestrator: 编排器实例
            data_source: 数据源路径

        Returns:
            执行结果
        """
        return self.run(
            orchestrator,
            data_source=data_source,
            analysis_type="descriptive",
            output_format="report",
            visualization=False,
        )

    def full_analysis(
        self,
        orchestrator,
        data_source: str,
        include_visualization: bool = True,
    ) -> Dict[str, Any]:
        """
        完整分析（描述+趋势+对比+可视化）

        Args:
            orchestrator: 编排器实例
            data_source: 数据源路径
            include_visualization: 是否包含可视化

        Returns:
            执行结果
        """
        return self.run(
            orchestrator,
            data_source=data_source,
            analysis_type="comprehensive",
            output_format="both",
            visualization=include_visualization,
        )

    def trend_analysis(
        self,
        orchestrator,
        data_source: str,
        time_column: str = "date",
        metric: str = "value",
    ) -> Dict[str, Any]:
        """
        趋势分析

        Args:
            orchestrator: 编排器实例
            data_source: 数据源路径
            time_column: 时间列名
            metric: 指标列名

        Returns:
            执行结果
        """
        return self.run(
            orchestrator,
            data_source=data_source,
            analysis_type="trend",
            output_format="report",
            visualization=True,
            time_column=time_column,
            metric=metric,
        )

    def comparative_analysis(
        self,
        orchestrator,
        data_source: str,
        group_by: str,
        metrics: List[str],
    ) -> Dict[str, Any]:
        """
        对比分析

        Args:
            orchestrator: 编排器实例
            data_source: 数据源路径
            group_by: 分组字段
            metrics: 对比指标列表

        Returns:
            执行结果
        """
        return self.run(
            orchestrator,
            data_source=data_source,
            analysis_type="comparative",
            output_format="report",
            visualization=True,
            group_by=group_by,
            metrics=metrics,
        )

    def get_info(self) -> Dict[str, Any]:
        """
        获取工作流信息

        Returns:
            工作流基本信息
        """
        return {
            "name": self.config.get("name", "analysis-pipeline"),
            "description": self.config.get("description", "数据分析工作流"),
            "version": self.config.get("version", "1.0.0"),
            "steps_count": len(self.config.get("steps", [])),
            "triggers": self.config.get("triggers", []),
            "inputs": list(self.config.get("inputs", {}).keys()),
            "outputs": list(self.config.get("outputs", {}).keys()),
            "supported_analysis_types": ["descriptive", "trend", "comparative", "comprehensive"],
        }

    def get_required_agents(self) -> List[str]:
        """获取所需代理"""
        return ["analysis_agent"]

    def get_required_skills(self) -> List[str]:
        """获取所需技能"""
        return ["data_analyzer_skill"]


# 便捷函数
def create_pipeline() -> AnalysisPipeline:
    """创建数据分析工作流实例"""
    return AnalysisPipeline()


# 导出实例
analysis_pipeline = AnalysisPipeline()
