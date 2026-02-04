import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from leo_skills.core.evolution import EvolvableSkill


class GitHubSkillsMonitorSkill(EvolvableSkill):
    """
    GitHub技能监控器

    实时监控GitHub上的Claude Code Skills/Agents，自动检测并加载。
    """

    def __init__(self, skill_name: str = "github_skills_monitor", config_path: Optional[str] = None):
        super().__init__(skill_name, Path(__file__).parent / "evolution.json")
        self.config_path = Path(config_path) if config_path else Path(__file__).parent / "config.yaml"
        self.config = self._load_config()

        # 监控数据源
        self.sources = self.config.get("sources", [
            {
                "name": "anthropics_skills",
                "type": "skills",
                "url": "https://github.com/anthropics/skills",
                "priority": "high"
            },
            {
                "name": "obra_superpowers",
                "type": "skills",
                "url": "https://github.com/obra/superpowers",
                "priority": "high"
            },
            {
                "name": "awesome_claude_skills",
                "type": "skills",
                "url": "https://github.com/travisvn/awesome-claude-skills",
                "priority": "medium"
            },
            {
                "name": "awesome_claude_code_agents",
                "type": "agents",
                "url": "https://github.com/hesreallyhim/awesome-claude-code-agents",
                "priority": "medium"
            }
        ])

        # 已加载的技能缓存
        self.loaded_cache = self._load_cache()

    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if self.config_path.exists():
            import yaml
            with open(self.config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        return {
            "output_base_dir": "src/leo_skills",
            "min_stars": 10,
            "scan_interval_hours": 24,
            "auto_import": False
        }

    def _load_cache(self) -> set:
        """加载已加载技能缓存"""
        cache_file = Path(__file__).parent / "loaded_cache.json"
        if cache_file.exists():
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return set(data.get("loaded", []))
            except:
                pass
        return set()

    def _save_cache(self):
        """保存已加载技能缓存"""
        cache_file = Path(__file__).parent / "loaded_cache.json"
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump({"loaded": list(self.loaded_cache)}, f, ensure_ascii=False)

    def execute(self, action: str = "scan", **kwargs) -> Dict[str, Any]:
        """
        执行技能

        Args:
            action: 操作类型
                - scan_all: 扫描所有数据源
                - scan: 扫描单个数据源
                - detect_and_import: 检测并导入新技能
                - list_sources: 列出监控的数据源
            **kwargs: 额外参数

        Returns:
            执行结果
        """
        if action == "scan_all":
            return self._scan_all_sources()
        elif action == "scan":
            return self._scan_source(kwargs.get("source"))
        elif action == "detect_and_import":
            return self._detect_and_import(kwargs.get("min_stars", self.config.get("min_stars", 10)))
        elif action == "list_sources":
            return self._list_sources()
        else:
            return {"success": False, "error": f"Unknown action: {action}"}

    def _list_sources(self) -> Dict[str, Any]:
        """列出所有监控的数据源"""
        return {
            "success": True,
            "sources": self.sources,
            "count": len(self.sources)
        }

    def _scan_all_sources(self) -> Dict[str, Any]:
        """扫描所有数据源"""
        results = []
        for source in self.sources:
            result = self._scan_source(source["name"])
            results.append(result)

        return {
            "success": True,
            "scanned_count": len(results),
            "results": results
        }

    def _scan_source(self, source_name: str) -> Dict[str, Any]:
        """扫描单个数据源"""
        source = next((s for s in self.sources if s["name"] == source_name), None)
        if not source:
            return {"success": False, "error": f"Source not found: {source_name}"}

        try:
            # 获取仓库最新信息
            owner, repo = self._parse_url(source["url"])

            # 获取star数
            stars = self._get_repo_stars(owner, repo)

            # 获取最新更新
            updated = self._get_repo_updated(owner, repo)

            # 获取文件列表
            files = self._get_repo_files(owner, repo)

            # 判断类型
            skill_type = self._detect_type(files, source["type"])

            return {
                "success": True,
                "source": source_name,
                "url": source["url"],
                "type": skill_type,
                "stars": stars,
                "updated": updated,
                "files_count": len(files),
                "is_new": stars >= self.config.get("min_stars", 10)
            }

        except Exception as e:
            return {"success": False, "error": str(e), "source": source_name}

    def _parse_url(self, url: str) -> tuple:
        """解析GitHub URL获取owner和repo"""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        path_parts = parsed.path.strip("/").split("/")
        return path_parts[0], path_parts[1]

    def _get_repo_stars(self, owner: str, repo: str) -> int:
        """获取仓库星标数"""
        try:
            result = subprocess.run(
                ["gh", "repo", "view", f"{owner}/{repo}", "--json", "stargazerCount", "-q", ".stargazerCount"],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                return int(result.stdout.strip())
        except:
            pass
        return 0

    def _get_repo_updated(self, owner: str, repo: str) -> str:
        """获取仓库最后更新时间"""
        try:
            result = subprocess.run(
                ["gh", "repo", "view", f"{owner}/{repo}", "--json", "updatedAt", "-q", ".updatedAt"],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        return ""

    def _get_repo_files(self, owner: str, repo: str) -> List[str]:
        """获取仓库文件列表"""
        try:
            result = subprocess.run(
                ["gh", "repo", "view", f"{owner}/{repo}", "--json", "name", "--tree"],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                import yaml
                data = yaml.safe_load(result.stdout)
                return self._flatten_tree(data.get("tree", []))
        except:
            pass
        return []

    def _flatten_tree(self, tree: List[Dict], prefix: str = "") -> List[str]:
        """扁平化文件树"""
        files = []
        for item in tree:
            path = prefix + item.get("path", "")
            files.append(path)
        return files

    def _detect_type(self, files: List[str], default_type: str = "skills") -> str:
        """检测项目类型"""
        files_str = "\n".join(files).lower()

        if "agent" in files_str or ".claude/agents" in files_str:
            return "agents"
        elif "skill" in files_str or "/skills/" in files_str or "SKILL.md" in files_str:
            return "skills"
        elif "workflow" in files_str or "pipeline" in files_str:
            return "workflows"
        elif ".github/workflows" in files_str:
            return "ci"
        return default_type

    def _detect_and_import(self, min_stars: int = 10) -> Dict[str, Any]:
        """检测并导入新技能"""
        imported = []
        skipped = []

        for source in self.sources:
            if source["priority"] != "high":
                continue

            scan_result = self._scan_source(source["name"])

            if scan_result.get("is_new", False):
                repo_id = f"{source['name']}"

                if repo_id not in self.loaded_cache:
                    # 调用 github_to_skills_skill 进行转换
                    result = self._import_skill(source["url"], source["type"])
                    if result.get("success"):
                        self.loaded_cache.add(repo_id)
                        imported.append({
                            "source": source["name"],
                            "url": source["url"],
                            "result": result
                        })
                    else:
                        skipped.append({
                            "source": source["name"],
                            "url": source["url"],
                            "error": result.get("error")
                        })
                else:
                    skipped.append({
                        "source": source["name"],
                        "reason": "Already loaded"
                    })

        # 保存缓存
        self._save_cache()

        return {
            "success": True,
            "imported_count": len(imported),
            "skipped_count": len(skipped),
            "imported": imported,
            "skipped": skipped
        }

    def _import_skill(self, repo_url: str, skill_type: str) -> Dict[str, Any]:
        """导入技能"""
        try:
            # 动态导入 github_to_skills_skill
            from github_to_skills_skill import GitHubToSkillsSkill

            converter = GitHubToSkillsSkill()

            # 确定输出目录
            category = self._get_category_by_type(skill_type)
            output_dir = f"{self.config.get('output_base_dir', 'src/leo_skills')}/{category}"

            # 转换仓库
            result = converter.execute(
                action="convert",
                repo_url=repo_url,
                output_dir=output_dir
            )

            return result

        except ImportError as e:
            return {
                "success": False,
                "error": f"github_to_skills_skill not available: {str(e)}"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _get_category_by_type(self, skill_type: str) -> str:
        """根据类型确定分类"""
        type_mapping = {
            "skills": "tools",
            "agents": "collaboration",
            "workflows": "content_creation"
        }
        return type_mapping.get(skill_type, "tools")
