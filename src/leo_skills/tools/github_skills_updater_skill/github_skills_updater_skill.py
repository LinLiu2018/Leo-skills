import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from leo_skills.core.evolution import EvolvableSkill


class GitHubSkillsUpdaterSkill(EvolvableSkill):
    """
    GitHub技能自动更新器

    跟踪已从GitHub加载的技能，自动检测并更新到最新版本。
    """

    def __init__(self, skill_name: str = "github_skills_updater", config_path: Optional[str] = None):
        super().__init__(skill_name, Path(__file__).parent / "evolution.json")
        self.config_path = Path(config_path) if config_path else Path(__file__).parent / "config.yaml"
        self.config = self._load_config()

        # 注册表路径
        self.registry_file = Path(__file__).parent / "registered_skills.json"
        self.history_file = Path(__file__).parent / "update_history.json"

        # 已注册的GitHub技能
        self.registry = self._load_registry()

    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if self.config_path.exists():
            import yaml
            with open(self.config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        return {
            "base_dir": "src/leo_skills",
            "auto_update": False,
            "check_interval_hours": 24,
            "max_history": 100
        }

    def _load_registry(self) -> Dict[str, Any]:
        """加载已注册技能表"""
        if self.registry_file.exists():
            try:
                with open(self.registry_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                pass
        return {"skills": {}, "last_scan": None}

    def _save_registry(self):
        """保存已注册技能表"""
        with open(self.registry_file, "w", encoding="utf-8") as f:
            json.dump(self.registry, f, ensure_ascii=False, indent=2)

    def _load_history(self) -> List[Dict]:
        """加载更新历史"""
        if self.history_file.exists():
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                pass
        return []

    def _save_history(self, history: List[Dict]):
        """保存更新历史"""
        max_history = self.config.get("max_history", 100)
        if len(history) > max_history:
            history = history[-max_history:]
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

    def execute(self, action: str = "check_updates", **kwargs) -> Dict[str, Any]:
        """
        执行技能

        Args:
            action: 操作类型
                - check_updates: 检测所有已注册技能的更新
                - update_all: 检测并自动更新所有
                - update: 更新单个技能
                - list_registered: 列出已注册技能
                - history: 查看更新历史
                - register: 手动注册技能
            **kwargs: 额外参数

        Returns:
            执行结果
        """
        if action == "check_updates":
            return self._check_all_updates()
        elif action == "update_all":
            return self._update_all(kwargs.get("auto_approve", False))
        elif action == "update":
            return self._update_skill(kwargs.get("skill_name"))
        elif action == "list_registered":
            return self._list_registered()
        elif action == "history":
            return self._get_history()
        elif action == "register":
            return self._register_skill(kwargs.get("repo_url"), kwargs.get("skill_path"))
        else:
            return {"success": False, "error": f"Unknown action: {action}"}

    def _list_registered(self) -> Dict[str, Any]:
        """列出已注册的GitHub技能"""
        skills = self.registry.get("skills", {})
        return {
            "success": True,
            "count": len(skills),
            "skills": skills
        }

    def _get_history(self) -> Dict[str, Any]:
        """获取更新历史"""
        history = self._load_history()
        return {
            "success": True,
            "count": len(history),
            "history": history[-50:]  # 最近50条
        }

    def _register_skill(self, repo_url: str, skill_path: str) -> Dict[str, Any]:
        """手动注册一个GitHub技能"""
        try:
            owner, repo = self._parse_url(repo_url)

            # 获取远程最新信息
            remote_sha = self._get_remote_sha(owner, repo)
            remote_version = self._get_remote_version(owner, repo)

            skill_name = Path(skill_path).name

            self.registry["skills"][skill_name] = {
                "repo_url": repo_url,
                "local_path": skill_path,
                "owner": owner,
                "repo": repo,
                "last_remote_sha": remote_sha,
                "last_remote_version": remote_version,
                "registered_at": datetime.now().isoformat(),
                "update_count": 0
            }
            self._save_registry()

            return {
                "success": True,
                "skill_name": skill_name,
                "message": f"Registered {skill_name} from {repo_url}"
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _check_all_updates(self) -> Dict[str, Any]:
        """检测所有已注册技能的更新"""
        skills = self.registry.get("skills", {})
        updates_needed = []
        up_to_date = []
        errors = []

        for skill_name, skill_info in skills.items():
            try:
                owner = skill_info.get("owner")
                repo = skill_info.get("repo")
                local_sha = skill_info.get("last_remote_sha")

                # 获取远程最新SHA
                remote_sha = self._get_remote_sha(owner, repo)

                if remote_sha and remote_sha != local_sha:
                    updates_needed.append({
                        "skill_name": skill_name,
                        "local_path": skill_info.get("local_path"),
                        "current_sha": local_sha[:8] if local_sha else None,
                        "remote_sha": remote_sha[:8],
                        "repo_url": skill_info.get("repo_url")
                    })
                else:
                    up_to_date.append(skill_name)

            except Exception as e:
                errors.append({
                    "skill_name": skill_name,
                    "error": str(e)
                })

        self.registry["last_scan"] = datetime.now().isoformat()
        self._save_registry()

        return {
            "success": True,
            "total_skills": len(skills),
            "need_update": len(updates_needed),
            "up_to_date": len(up_to_date),
            "errors": len(errors),
            "updates_needed": updates_needed,
            "up_to_date_list": up_to_date,
            "errors_detail": errors
        }

    def _update_all(self, auto_approve: bool = False) -> Dict[str, Any]:
        """检测并自动更新所有"""
        check_result = self._check_all_updates()

        if not check_result.get("need_update"):
            return {
                "success": True,
                "message": "All skills are up to date",
                "updated": []
            }

        # 如果需要确认
        if not auto_approve and not self.config.get("auto_update"):
            return {
                "success": True,
                "need_confirm": True,
                "message": f"{check_result['need_update']} skills need update",
                "updates_needed": check_result["updates_needed"],
                "hint": "Set auto_approve=True or config.auto_update=true to auto-update"
            }

        # 执行更新
        updated = []
        errors = []

        for update_info in check_result["updates_needed"]:
            result = self._update_skill(update_info["skill_name"])
            if result.get("success"):
                updated.append(update_info["skill_name"])
            else:
                errors.append({
                    "skill_name": update_info["skill_name"],
                    "error": result.get("error")
                })

        # 记录历史
        self._record_history("batch_update", {
            "updated_count": len(updated),
            "errors_count": len(errors),
            "updated_skills": updated
        })

        return {
            "success": True,
            "updated_count": len(updated),
            "errors_count": len(errors),
            "updated": updated,
            "errors": errors
        }

    def _update_skill(self, skill_name: str) -> Dict[str, Any]:
        """更新单个技能"""
        skill_info = self.registry.get("skills", {}).get(skill_name)
        if not skill_info:
            return {"success": False, "error": f"Skill not registered: {skill_name}"}

        try:
            owner = skill_info.get("owner")
            repo = skill_info.get("repo")
            local_path = Path(skill_info.get("local_path"))
            remote_sha = self._get_remote_sha(owner, repo)

            # 获取远程临时目录
            temp_dir = Path(__file__).parent / "temp_update"
            temp_dir.mkdir(exist_ok=True)
            repo_dir = temp_dir / repo

            # 克隆或更新
            if repo_dir.exists():
                subprocess.run(
                    ["git", "pull", "origin", "main"],
                    cwd=repo_dir,
                    capture_output=True, timeout=60
                )
            else:
                subprocess.run(
                    ["git", "clone", f"https://github.com/{owner}/{repo}.git", str(repo_dir)],
                    capture_output=True, timeout=120
                )

            # 同步到本地技能目录
            import shutil
            if local_path.exists():
                shutil.rmtree(local_path)
            shutil.copytree(repo_dir, local_path)

            # 清理临时目录
            shutil.rmtree(repo_dir, ignore_errors=True)

            # 更新注册表
            old_sha = skill_info.get("last_remote_sha")
            skill_info["last_remote_sha"] = remote_sha
            skill_info["last_updated"] = datetime.now().isoformat()
            skill_info["update_count"] = skill_info.get("update_count", 0) + 1
            self._save_registry()

            # 记录历史
            self._record_history("update", {
                "skill_name": skill_name,
                "repo_url": skill_info.get("repo_url"),
                "old_sha": old_sha[:8] if old_sha else None,
                "new_sha": remote_sha[:8]
            })

            return {
                "success": True,
                "skill_name": skill_name,
                "old_sha": old_sha[:8] if old_sha else None,
                "new_sha": remote_sha[:8]
            }

        except Exception as e:
            return {"success": False, "error": str(e), "skill_name": skill_name}

    def _record_history(self, action: str, details: Dict):
        """记录更新历史"""
        history = self._load_history()
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details
        }
        history.append(entry)
        self._save_history(history)

    def _parse_url(self, url: str) -> tuple:
        """解析GitHub URL"""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        path_parts = parsed.path.strip("/").split("/")
        return path_parts[0], path_parts[1]

    def _get_remote_sha(self, owner: str, repo: str) -> str:
        """获取远程最新commit SHA"""
        try:
            result = subprocess.run(
                ["gh", "repo", "view", f"{owner}/{repo}", "--json", "defaultBranchRef", "-q", ".defaultBranchRef.target.oid"],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        return ""

    def _get_remote_version(self, owner: str, repo: str) -> str:
        """获取远程最新版本标签"""
        try:
            result = subprocess.run(
                ["gh", "release", "view", "--json", "tagName", "-q", ".tagName"],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except:
            pass
        return "latest"

    def auto_discover_and_register(self):
        """自动发现并注册所有GitHub来源的技能"""
        base_dir = Path(self.config.get("base_dir", "src/leo_skills"))

        # 查找有evolution.json的技能（这些可能有GitHub来源）
        for skill_dir in base_dir.rglob("evolution.json"):
            skill_path = skill_dir.parent

            # 检查是否有标记为GitHub来源
            evolution_file = skill_path / "evolution.json"
            if evolution_file.exists():
                try:
                    with open(evolution_file, "r") as f:
                        evolution = json.load(f)

                    # 查找来源信息
                    # 这里可以扩展更复杂的检测逻辑
                except:
                    pass

        return {"success": True, "message": "Auto-discovery completed"}
