"""
RealEstate Pipeline - 房产营销工作流
====================================
专为房地产业务设计的完整营销工作流封装类
"""

from pathlib import Path
from typing import Any, Dict, Optional

import yaml


class RealEstatePipeline:
    """
    房产营销工作流
    ==============
    提供房产项目营销全流程自动化：
    - 市场调研
    - 竞品分析
    - 营销策划
    - 内容创作
    - 多渠道发布
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
        project_name: str,
        location: str,
        project_type: str = "residential",
        target_audience: str = "刚需改善",
        platforms: Optional[list] = None,
    ) -> Dict[str, Any]:
        """
        执行房产营销工作流

        Args:
            orchestrator: 编排器实例
            project_name: 项目名称
            location: 项目位置
            project_type: 项目类型 (residential/commercial/villa)
            target_audience: 目标客群
            platforms: 发布平台列表

        Returns:
            执行结果
        """
        # 验证必要参数
        if not project_name:
            raise ValueError("缺少必要参数: project_name")
        if not location:
            raise ValueError("缺少必要参数: location")

        # 准备输入参数
        inputs = {
            "project_name": project_name,
            "location": location,
            "project_type": project_type,
            "target_audience": target_audience,
            "platforms": platforms or ["wechat", "xiaohongshu"],
        }

        # 执行工作流
        return orchestrator.run_workflow(self.config, inputs)

    def get_info(self) -> Dict[str, Any]:
        """
        获取工作流信息

        Returns:
            工作流基本信息
        """
        return {
            "name": self.config.get("name", "realestate-marketing-pipeline"),
            "description": self.config.get("description", ""),
            "version": self.config.get("version", "1.0.0"),
            "steps_count": len(self.config.get("steps", [])),
            "triggers": self.config.get("triggers", []),
            "inputs": list(self.config.get("inputs", {}).keys()),
            "outputs": list(self.config.get("outputs", {}).keys()),
        }

    def get_required_agents(self) -> list:
        """
        获取所需的Agent列表

        Returns:
            Agent名称列表
        """
        agents = set()
        for step in self.config.get("steps", []):
            if "agent" in step:
                agents.add(step["agent"])
            if "branches" in step:
                for branch in step["branches"]:
                    if "agent" in branch:
                        agents.add(branch["agent"])
        return list(agents)

    def get_required_skills(self) -> list:
        """
        获取所需的Skill列表

        Returns:
            Skill名称列表
        """
        skills = set()
        for step in self.config.get("steps", []):
            if "skill" in step:
                skills.add(step["skill"])
            if "branches" in step:
                for branch in step["branches"]:
                    if "skill" in branch:
                        skills.add(branch["skill"])
        return list(skills)


# 便捷函数
def create_pipeline() -> RealEstatePipeline:
    """创建房产营销工作流实例"""
    return RealEstatePipeline()
