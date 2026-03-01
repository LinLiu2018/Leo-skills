"""
Pipeline 基类 — 统一 YAML 来源
================================
所有 Pipeline 类从 definitions/*.yaml 加载配置，
不再使用 workflows/*/workflow.yaml（已废弃）。

Pipeline 类保留为领域快捷方法的薄封装层。
新工作流应直接使用 WorkflowEngine.execute_from_yaml()。
"""

import warnings
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


# definitions 目录的绝对路径
_DEFINITIONS_DIR = Path(__file__).parent / "definitions"


class PipelineBase:
    """
    Pipeline 统一基类

    子类只需指定 yaml_name 和提供领域快捷方法。
    配置统一从 definitions/ 目录加载。
    """

    # 子类覆盖：对应 definitions/ 下的 YAML 文件名（不含 .yaml）
    yaml_name: str = ""

    def __init__(self):
        self._config: Optional[Dict[str, Any]] = None

    @property
    def config(self) -> Dict[str, Any]:
        """惰性加载配置"""
        if self._config is None:
            self._config = self._load_config()
        return self._config

    def _load_config(self) -> Dict[str, Any]:
        """从 definitions/ 目录加载 YAML 配置"""
        yaml_path = _DEFINITIONS_DIR / f"{self.yaml_name}.yaml"
        if yaml_path.exists():
            with open(yaml_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}

        # 向后兼容：尝试旧路径
        legacy_dir = Path(__file__).parent / "workflows" / self.yaml_name
        legacy_path = legacy_dir / "workflow.yaml"
        if legacy_path.exists():
            warnings.warn(
                f"Pipeline '{self.yaml_name}' 使用了旧路径 workflows/*/workflow.yaml，"
                f"请迁移到 definitions/{self.yaml_name}.yaml",
                DeprecationWarning,
                stacklevel=2,
            )
            with open(legacy_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}

        return {}

    def run(self, orchestrator, **inputs) -> Dict[str, Any]:
        """执行工作流（委托给 orchestrator）"""
        return orchestrator.run_workflow(self.config, inputs)

    def get_info(self) -> Dict[str, Any]:
        """获取工作流信息"""
        return {
            "name": self.config.get("name", self.yaml_name),
            "description": self.config.get("description", ""),
            "version": self.config.get("version", "1.0.0"),
            "steps_count": len(self.config.get("steps", [])),
            "inputs": list(self.config.get("inputs", {}).keys()),
        }

    def get_required_agents(self) -> list:
        """从 YAML steps 中提取所需 Agent"""
        agents = set()
        for step in self.config.get("steps", []):
            if "agent" in step:
                agents.add(step["agent"])
            for branch in step.get("branches", []):
                if isinstance(branch, dict) and "agent" in branch:
                    agents.add(branch["agent"])
        return sorted(agents)
