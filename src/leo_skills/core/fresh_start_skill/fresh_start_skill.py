# -*- coding: utf-8 -*-
"""
fresh_start_skill - 项目上下文加载技能

用于在新会话开始时加载项目上下文，理解项目状态
"""

from typing import Dict, Any, Optional
from pathlib import Path


class FreshStartSkill:
    """
    FreshStartSkill

    项目上下文加载技能 - 在每个新会话开始时或上下文重置后使用，
    以了解项目状态并加载必要的上下文。
    """

    def __init__(self):
        self.name = "fresh_start"
        self.version = "1.0.0"
        self.description = "Orient to project structure and load context"

    def execute(self, project_dir: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        执行项目上下文加载

        Args:
            project_dir: 项目目录路径，默认为当前工作目录
            **kwargs: 其他参数

        Returns:
            包含项目上下文信息的字典
        """
        working_dir = Path(project_dir) if project_dir else Path.cwd()

        result = {
            "status": "completed",
            "working_dir": str(working_dir),
            "context": {},
            "files_loaded": []
        }

        # 检查项目结构
        context = self._detect_context(working_dir)
        result["context"] = context

        # 加载必需文件
        files_to_load = self._get_required_files(context)
        result["files_loaded"] = files_to_load

        return result

    def _detect_context(self, working_dir: Path) -> Dict[str, Any]:
        """检测工作上下文"""
        context = {
            "mode": "greenfield",
            "project_root": str(working_dir),
            "feature_dir": None,
            "is_git_repo": False
        }

        # 检测是否是 feature 模式
        if "/features/" in str(working_dir):
            context["mode"] = "feature"
            context["feature_dir"] = str(working_dir)
            context["project_root"] = str(working_dir.parent.parent)

        return context

    def _get_required_files(self, context: Dict[str, Any]) -> list:
        """获取需要加载的必需文件列表"""
        files = []
        project_root = Path(context["project_root"])

        # 核心文件
        core_files = [
            "AGENTS.md",
            "EXECUTION_PLAN.md",
            "PRODUCT_SPEC.md",
            "TECHNICAL_SPEC.md"
        ]

        for file in core_files:
            file_path = project_root / file
            if file_path.exists():
                files.append(str(file_path))

        # Feature 模式下的额外文件
        if context["mode"] == "feature" and context["feature_dir"]:
            feature_dir = Path(context["feature_dir"])
            feature_files = [
                "FEATURE_SPEC.md",
                "FEATURE_TECHNICAL_SPEC.md"
            ]
            for file in feature_files:
                file_path = feature_dir / file
                if file_path.exists():
                    files.append(str(file_path))

        return files


def main():
    """入口函数"""
    skill = FreshStartSkill()
    return skill


if __name__ == "__main__":
    skill = main()
