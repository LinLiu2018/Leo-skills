import json
import os
import subprocess
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from leo_skills.core.evolution import EvolvableSkill


class GitHubToSkillsSkill(EvolvableSkill):
    """
    GitHub仓库转AI技能工具

    将GitHub仓库自动转换为符合Leo AI System标准的技能。
    """

    def __init__(self, skill_name: str = "github_to_skills", config_path: Optional[str] = None):
        super().__init__(skill_name, Path(__file__).parent / "evolution.json")
        self.config_path = Path(config_path) if config_path else Path(__file__).parent / "config.yaml"
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if self.config_path.exists():
            import yaml
            with open(self.config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        return {
            "output_base_dir": "src/leo_skills",
            "default_category": "tools",
            "skill_template": {
                "version": "1.0.0",
                "type": "standard",
            }
        }

    def execute(self, action: str = "convert", **kwargs) -> Dict[str, Any]:
        """
        执行技能

        Args:
            action: 操作类型
                - convert: 转换单个仓库
                - batch_convert: 批量转换
                - analyze: 分析仓库结构
            repo_url: 仓库URL
            repo_list: 仓库列表（批量转换用）
            output_dir: 输出目录

        Returns:
            执行结果
        """
        if action == "convert":
            return self._convert_repo(kwargs.get("repo_url"), kwargs.get("output_dir"))
        elif action == "batch_convert":
            return self._batch_convert(kwargs.get("repo_list", []))
        elif action == "analyze":
            return self._analyze_repo(kwargs.get("repo_url"))
        else:
            return {"success": False, "error": f"Unknown action: {action}"}

    def _convert_repo(self, repo_url: str, output_dir: Optional[str] = None) -> Dict[str, Any]:
        """转换单个仓库"""
        try:
            # 解析仓库信息
            parsed = urlparse(repo_url)
            path_parts = parsed.path.strip("/").split("/")
            owner, repo_name = path_parts[0], path_parts[1].replace(".git", "")

            # 获取仓库元数据
            metadata = self._fetch_repo_metadata(owner, repo_name)
            if not metadata["success"]:
                return metadata

            # 创建技能目录
            skill_name = self._generate_skill_name(repo_name)
            category = self._determine_category(metadata.get("description", ""))
            skill_dir = Path(output_dir or self.config["output_base_dir"]) / category / skill_name

            if skill_dir.exists():
                shutil.rmtree(skill_dir)

            skill_dir.mkdir(parents=True, exist_ok=True)

            # 生成文件
            self._generate_skill_files(skill_dir, metadata, skill_name)

            # 学习经验
            self.learn(f"Successfully converted {repo_url} to {skill_name}")

            return {
                "success": True,
                "skill_name": skill_name,
                "skill_dir": str(skill_dir),
                "metadata": metadata
            }

        except Exception as e:
            self.learn(f"Failed to convert {repo_url}: {str(e)}", "error_context")
            return {"success": False, "error": str(e)}

    def _fetch_repo_metadata(self, owner: str, repo_name: str) -> Dict[str, Any]:
        """获取仓库元数据"""
        try:
            # 使用gh命令获取仓库信息
            result = subprocess.run(
                ["gh", "repo", "view", f"{owner}/{repo_name}", "--json", "name,description,readme,defaultBranchRef,languages"],
                capture_output=True, text=True, timeout=30
            )

            if result.returncode == 0:
                import yaml
                metadata = yaml.safe_load(result.stdout)
                return {"success": True, "data": metadata}
            else:
                # 备用方案：直接克隆并读取
                return self._fetch_repo_metadata_fallback(owner, repo_name)

        except Exception as e:
            return self._fetch_repo_metadata_fallback(owner, repo_name)

    def _fetch_repo_metadata_fallback(self, owner: str, repo_name: str) -> Dict[str, Any]:
        """备用获取仓库元数据方式"""
        try:
            # 获取README
            readme_content = subprocess.run(
                ["gh", "repo", "view", f"{owner}/{repo_name}", "--readme"],
                capture_output=True, text=True, timeout=30
            ).stdout

            return {
                "success": True,
                "data": {
                    "name": repo_name,
                    "readme": readme_content,
                    "owner": owner
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _generate_skill_name(self, repo_name: str) -> str:
        """生成技能名称（snake_case）"""
        # 转换为snake_case
        skill_name = repo_name.lower().replace("-", "_").replace("_skill", "")
        if not skill_name.endswith("_skill"):
            skill_name = f"{skill_name}_skill"
        return skill_name

    def _determine_category(self, description: str) -> str:
        """根据描述确定技能分类"""
        description_lower = description.lower()

        categories = {
            "content-creation": ["content", "write", "article", "生成", "创作"],
            "development": ["code", "dev", "开发", "编程"],
            "utilities": ["util", "tool", "工具"],
            "intelligence": ["ai", "intelligence", "智能", "分析"],
            "frontend": ["frontend", "ui", "react", "vue", "前端"],
            "backend": ["backend", "api", "server", "后端"],
            "devops": ["docker", "deploy", "devops", "部署"],
        }

        for category, keywords in categories.items():
            if any(kw in description_lower for kw in keywords):
                return category

        return self.config.get("default_category", "tools")

    def _generate_skill_files(self, skill_dir: Path, metadata: Dict, skill_name: str):
        """生成技能文件"""
        skill_data = metadata.get("data", {})

        # 1. 生成SKILL.md
        skill_md = f"""# {skill_data.get('name', skill_name)}

## 技能描述

{skill_data.get('description', '自动生成的技能')}

## 核心能力

- 自动转换自GitHub仓库
- 支持标准化技能结构
- 集成进化机制

## 使用方法

```python
from {skill_name} import {skill_name.replace('_', '').title().replace(' ', '')}Skill

skill = {skill_name.replace('_', '').title().replace(' ', '')}Skill()
result = skill.execute(task="your_task")
```
"""

        (skill_dir / "SKILL.md").write_text(skill_md, encoding="utf-8")

        # 2. 生成 __init__.py
        init_py = f'''from .{skill_name} import {skill_name.replace('_', '').title().replace(' ', '')}Skill

__all__ = ["{skill_name.replace('_', '').title().replace(' ', '')}Skill"]
'''
        (skill_dir / "__init__.py").write_text(init_py, encoding="utf-8")

        # 3. 生成主模块文件
        main_py = f'''from leo_skills.core.evolution import EvolvableSkill


class {skill_name.replace('_', '').title().replace(' ', '')}Skill(EvolvableSkill):
    """
    {skill_name.replace('_', '').title().replace(' ', '')}Skill - 自动生成
    """

    def __init__(self):
        super().__init__("{skill_name}", __file__.parent / "evolution.json")

    def execute(self, task: str, **kwargs) -> dict:
        """
        执行任务

        Args:
            task: 任务类型
            **kwargs: 额外参数

        Returns:
            执行结果
        """
        if task == "example":
            return self._example_task(**kwargs)
        return {{"success": False, "error": "Unknown task"}}

    def _example_task(self, **kwargs) -> dict:
        """示例任务"""
        return {{
            "success": True,
            "message": "Task executed successfully",
            "data": kwargs
        }}
'''
        (skill_dir / f"{skill_name}.py").write_text(main_py, encoding="utf-8")

        # 4. 生成config目录
        config_dir = skill_dir / "config"
        config_dir.mkdir(exist_ok=True)

        config_yaml = f"""skill:
  name: {skill_name}
  version: 1.0.0
  category: auto-detected

# 进化配置
evolution:
  enabled: true
  learn_on_failure: true
  max_tips: 100
"""
        (config_dir / "config.yaml").write_text(config_yaml, encoding="utf-8")

    def _batch_convert(self, repo_list: List[str]) -> Dict[str, Any]:
        """批量转换仓库"""
        results = []
        for repo_url in repo_list:
            result = self._convert_repo(repo_url)
            results.append(result)

        success_count = sum(1 for r in results if r.get("success"))

        return {
            "success": success_count > 0,
            "total": len(repo_list),
            "success_count": success_count,
            "results": results
        }

    def _analyze_repo(self, repo_url: str) -> Dict[str, Any]:
        """分析仓库结构"""
        parsed = urlparse(repo_url)
        path_parts = parsed.path.strip("/").split("/")
        owner, repo_name = path_parts[0], path_parts[1].replace(".git", "")

        metadata = self._fetch_repo_metadata(owner, repo_name)

        return {
            "success": metadata["success"],
            "repo_url": repo_url,
            "owner": owner,
            "repo_name": repo_name,
            "suggested_skill_name": self._generate_skill_name(repo_name),
            "suggested_category": self._determine_category(metadata.get("data", {}).get("description", "")),
            "metadata": metadata
        }
