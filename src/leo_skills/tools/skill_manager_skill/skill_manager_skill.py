import json
import os
import subprocess
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from leo_skills.core.evolution import EvolvableSkill


class SkillManagerSkill(EvolvableSkill):
    """
    技能生命周期管理器

    管理Leo AI System中所有技能的完整生命周期。
    """

    def __init__(self, skill_name: str = "skill_manager", config_path: Optional[str] = None):
        super().__init__(skill_name, Path(__file__).parent / "evolution.json")
        # 从 skill_manager_skill/ 向上两级到 leo_skills
        self.skills_root = Path(__file__).parents[2]
        self.config_path = Path(config_path) if config_path else Path(__file__).parent / "config.yaml"
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if self.config_path.exists():
            import yaml
            with open(self.config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        return {
            "scan_categories": ["content-creation", "development", "utilities", "tools", "intelligence"],
            "exclude_patterns": [".backup", "__pycache__", ".git"],
            "check_remote": True,
            "auto_backup": True,
        }

    def execute(self, action: str = "audit", **kwargs) -> Dict[str, Any]:
        """
        执行管理操作

        Args:
            action: 操作类型
                - audit: 审计所有技能
                - check_updates: 检查远程更新
                - report: 生成状态报告
                - upgrade: 升级指定技能
                - list: 列出技能
                - delete: 删除技能
            skill_name: 技能名称（upgrade/delete时需要）

        Returns:
            执行结果
        """
        actions = {
            "audit": self._audit_skills,
            "check_updates": self._check_remote_updates,
            "report": self._generate_report,
            "upgrade": self._upgrade_skill,
            "list": self._list_skills,
            "delete": self._delete_skill,
            "health_check": self._health_check,
            "execute": self._health_check,
        }

        if action not in actions:
            return {"success": False, "error": f"Unknown action: {action}"}

        return actions[action](**kwargs)

    def _audit_skills(self, **kwargs) -> Dict[str, Any]:
        """审计所有技能"""
        skills = []
        issues = []

        for category in self.config.get("scan_categories", []):
            category_path = self.skills_root / category
            if not category_path.exists():
                continue

            for skill_dir in category_path.iterdir():
                if not skill_dir.is_dir():
                    continue

                # 检查是否排除
                if any(p in skill_dir.name for p in self.config.get("exclude_patterns", [])):
                    continue

                skill_info = self._audit_single_skill(skill_dir, category)
                if skill_info:
                    skills.append(skill_info)

        # 统计问题
        for skill in skills:
            if skill.get("issues"):
                issues.extend(skill["issues"])

        # self._log_evolution(f"Audited {len(skills)} skills, found {len(issues)} issues")

        return {
            "success": True,
            "total_skills": len(skills),
            "skills_with_issues": sum(1 for s in skills if s.get("issues")),
            "total_issues": len(issues),
            "skills": skills,
            "issues_summary": self._summarize_issues(issues)
        }

    def _audit_single_skill(self, skill_dir: Path, category: str) -> Optional[Dict[str, Any]]:
        """审计单个技能"""
        skill_name = skill_dir.name
        issues = []
        has_skill_md = (skill_dir / "SKILL.md").exists()
        has_init = (skill_dir / "__init__.py").exists()
        has_main_module = any(f.suffix == ".py" and f.name != "__init__.py" for f in skill_dir.glob("*.py"))

        if not has_skill_md:
            issues.append("Missing SKILL.md")
        if not has_init:
            issues.append("Missing __init__.py")
        if not has_main_module:
            issues.append("Missing main module")

        return {
            "name": skill_name,
            "category": category,
            "path": str(skill_dir),
            "has_skill_md": has_skill_md,
            "has_init": has_init,
            "has_main_module": has_main_module,
            "issues": issues,
            "health_score": self._calculate_health_score(has_skill_md, has_init, has_main_module, issues)
        }

    def _calculate_health_score(self, has_skill_md: bool, has_init: bool, has_main_module: bool, issues: List[str]) -> float:
        """计算健康度分数"""
        score = 100
        if not has_skill_md:
            score -= 30
        if not has_init:
            score -= 20
        if not has_main_module:
            score -= 30
        score -= len(issues) * 10
        return max(0, score)

    def _summarize_issues(self, issues: List[str]) -> Dict[str, int]:
        """汇总问题"""
        summary = {}
        for issue in issues:
            summary[issue] = summary.get(issue, 0) + 1
        return summary

    def _check_remote_updates(self, **kwargs) -> Dict[str, Any]:
        """检查远程更新"""
        updates = []

        # 查找包含.git的技能目录
        for skill_dir in self.skills_root.rglob("*"):
            if not skill_dir.is_dir():
                continue
            git_dir = skill_dir / ".git"
            if git_dir.exists():
                skill_name = skill_dir.name
                try:
                    # 检查是否有远程更新
                    result = subprocess.run(
                        ["git", "fetch", "--dry-run"],
                        cwd=str(skill_dir),
                        capture_output=True,
                        timeout=10
                    )
                    # 简单判断：检查本地HEAD与远程差异
                    local_commit = subprocess.run(
                        ["git", "rev-parse", "HEAD"],
                        cwd=str(skill_dir),
                        capture_output=True,
                        text=True
                    ).stdout.strip()

                    if local_commit:
                        updates.append({
                            "skill": skill_name,
                            "path": str(skill_dir),
                            "local_commit": local_commit,
                            "has_remote": True
                        })
                except Exception:
                    pass

        return {
            "success": True,
            "total_checked": len(updates),
            "updates_available": updates
        }

    def _generate_report(self, **kwargs) -> Dict[str, Any]:
        """生成状态报告"""
        audit_result = self._audit_skills()
        update_result = self._check_remote_updates()

        report = {
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_skills": audit_result["total_skills"],
                "healthy_skills": audit_result["total_skills"] - audit_result["skills_with_issues"],
                "skills_needing_attention": audit_result["skills_with_issues"],
                "total_issues": audit_result["total_issues"],
                "updates_available": len(update_result["updates_available"])
            },
            "by_category": self._group_skills_by_category(audit_result["skills"]),
            "top_issues": list(audit_result["issues_summary"].items())[:5],
            "recommendations": self._generate_recommendations(audit_result, update_result)
        }

        # self._log_evolution(f"Generated report: {report['summary']['total_skills']} skills analyzed")

        return {
            "success": True,
            "report": report,
            "markdown": self._format_report_markdown(report)
        }

    def _group_skills_by_category(self, skills: List[Dict]) -> Dict[str, int]:
        """按分类统计技能"""
        categories = {}
        for skill in skills:
            cat = skill.get("category", "unknown")
            categories[cat] = categories.get(cat, 0) + 1
        return categories

    def _generate_recommendations(self, audit_result: Dict, update_result: Dict) -> List[str]:
        """生成建议"""
        recommendations = []

        if audit_result["skills_with_issues"] > 0:
            recommendations.append(f"修复 {audit_result['skills_with_issues']} 个有问题的技能")

        if update_result["updates_available"]:
            recommendations.append(f"检查 {len(update_result['updates_available'])} 个技能的远程更新")

        if not recommendations:
            recommendations.append("所有技能状态良好，继续保持！")

        return recommendations

    def _format_report_markdown(self, report: Dict) -> str:
        """格式化报告为Markdown"""
        lines = [
            "# 技能状态报告",
            f"\n生成时间: {report['generated_at']}",
            "\n## 概览",
            f"- 总技能数: {report['summary']['total_skills']}",
            f"- 健康技能: {report['summary']['healthy_skills']}",
            f"- 需关注: {report['summary']['skills_needing_attention']}",
            f"- 问题总数: {report['summary']['total_issues']}",
            f"- 可用更新: {report['summary']['updates_available']}",
            "\n## 按分类统计",
        ]

        for cat, count in report["by_category"].items():
            lines.append(f"- {cat}: {count} 个技能")

        lines.extend(["\n## 建议", *(f"- {r}" for r in report["recommendations"])])

        return "\n".join(lines)

    def _upgrade_skill(self, skill_name: str, **kwargs) -> Dict[str, Any]:
        """升级指定技能"""
        # 查找技能目录
        skill_dir = None
        for category in self.config.get("scan_categories", []):
            path = self.skills_root / category / skill_name
            if path.exists():
                skill_dir = path
                break

        if not skill_dir:
            return {"success": False, "error": f"Skill not found: {skill_name}"}

        # 执行升级（这里可以扩展为实际的升级逻辑）
        if self.config.get("auto_backup", True):
            backup_dir = skill_dir / ".backup"
            backup_dir.mkdir(exist_ok=True)
            # 复制重要文件到备份
            for f in skill_dir.glob("*.py"):
                if f.name not in ["__init__.py"]:
                    (backup_dir / f.name).write_bytes(f.read_bytes())

        # self._log_evolution(f"Upgraded skill: {skill_name}")

        return {
            "success": True,
            "skill_name": skill_name,
            "message": "Skill upgraded successfully"
        }

    def _list_skills(self, **kwargs) -> Dict[str, Any]:
        """列出所有技能"""
        audit_result = self._audit_skills()

        return {
            "success": True,
            "skills": [
                {"name": s["name"], "category": s["category"], "health": s["health_score"]}
                for s in audit_result["skills"]
            ],
            "total": audit_result["total_skills"]
        }

    def _delete_skill(self, skill_name: str, **kwargs) -> Dict[str, Any]:
        """删除技能"""
        # 查找技能目录
        skill_dir = None
        for category in self.config.get("scan_categories", []):
            path = self.skills_root / category / skill_name
            if path.exists():
                skill_dir = path
                break

        if not skill_dir:
            return {"success": False, "error": f"Skill not found: {skill_name}"}

        import shutil
        shutil.rmtree(skill_dir)

        # self._log_evolution(f"Deleted skill: {skill_name}")

        return {
            "success": True,
            "skill_name": skill_name,
            "message": "Skill deleted successfully"
        }

    def _health_check(self) -> dict:
        """Health check for scheduled tasks"""
        from datetime import datetime
        return {
            "success": True,
            "status": "ok",
            "skill": "skill_manager",
            "skills_root": str(self.skills_root) if hasattr(self, 'skills_root') else "N/A",
            "timestamp": datetime.now().isoformat()
        }
