"""
Find Skills Skill - 技能发现技能
"""
from leo_skills.core.base_executor import BaseExecutor

from typing import Dict, Any, Optional, List
from pathlib import Path


class FindSkillsSkill(BaseExecutor):
    """技能发现技能"""
    
    def __init__(self):
        self.name = "find_skills_skill"
        self.version = "1.0.0"
        self.category = "tools"
        self.workspace = Path(__file__).parent.parent.parent.parent
    
    def execute(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        params = params or {}
        action = params.get("action", "search")
        
        if action == "search":
            return self._search_skills(params)
        elif action == "recommend":
            return self._recommend_skills(params)
        elif action == "install":
            return self._install_skill(params)
        else:
            return {"status": "error", "message": f"未知操作：{action}"}
    
    def _search_skills(self, params: Dict) -> Dict[str, Any]:
        query = params.get("query", "")
        
        # 扫描现有技能
        skills_dir = self.workspace / "src" / "leo_skills"
        found_skills = []
        
        if skills_dir.exists():
            for category in skills_dir.iterdir():
                if not category.is_dir():
                    continue
                for skill_dir in category.iterdir():
                    if skill_dir.is_dir() and query.lower() in skill_dir.name.lower():
                        found_skills.append({
                            "name": skill_dir.name,
                            "category": category.name,
                            "path": str(skill_dir)
                        })
        
        return {
            "status": "success",
            "skill": self.name,
            "action": "search",
            "query": query,
            "count": len(found_skills),
            "skills": found_skills[:20]
        }
    
    def _recommend_skills(self, params: Dict) -> Dict[str, Any]:
        use_case = params.get("use_case", "")
        
        # 基于用例推荐技能（简化版）
        recommendations = []
        
        if "搜索" in use_case or "search" in use_case.lower():
            recommendations.append({"name": "web_search_skill", "reason": "网络搜索必备"})
        
        if "总结" in use_case or "summarize" in use_case.lower():
            recommendations.append({"name": "summarize_skill", "reason": "内容总结"})
        
        if "GitHub" in use_case or "github" in use_case.lower():
            recommendations.append({"name": "github_integration_skill", "reason": "GitHub 集成"})
        
        if "安全" in use_case or "security" in use_case.lower():
            recommendations.append({"name": "skill_vetter_skill", "reason": "安全扫描"})
        
        return {
            "status": "success",
            "skill": self.name,
            "action": "recommend",
            "use_case": use_case,
            "count": len(recommendations),
            "recommendations": recommendations
        }
    
    def _install_skill(self, params: Dict) -> Dict[str, Any]:
        skill_name = params.get("skill_name", "")
        
        return {
            "status": "success",
            "skill": self.name,
            "action": "install",
            "skill_name": skill_name,
            "message": f"请运行：python scripts/skills/install.py {skill_name}",
            "note": "安装后需要重启 OpenClaw 生效"
        }
    
    def get_status(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "category": self.category,
            "status": "active"
        }


__all__ = ["FindSkillsSkill"]
