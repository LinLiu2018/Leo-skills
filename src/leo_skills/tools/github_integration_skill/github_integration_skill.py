"""
GitHub Integration Skill - GitHub 集成

基于 gh CLI 的 GitHub 操作技能。
"""
from leo_skills.core.base_executor import BaseExecutor

from typing import Dict, Any, Optional, List
from pathlib import Path
import subprocess


class GithubIntegrationSkill(BaseExecutor):
    """GitHub 集成技能"""
    
    def __init__(self):
        self.name = "github_integration_skill"
        self.version = "1.0.0"
        self.category = "tools"
    
    def execute(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        params = params or {}
        action = params.get("action", "search")
        
        if action == "search":
            return self._search(params)
        elif action == "create_repo":
            return self._create_repo(params)
        elif action == "list_issues":
            return self._list_issues(params)
        elif action == "create_pr":
            return self._create_pr(params)
        else:
            return {"status": "error", "message": f"未知操作：{action}"}
    
    def _search(self, params: Dict) -> Dict[str, Any]:
        """搜索仓库/代码"""
        query = params.get("query", "")
        search_type = params.get("type", "repos")  # repos, code, issues, prs
        
        try:
            cmd = ["gh", "search", search_type, query, "--json", "name,owner,description,stars"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                import json
                repos = json.loads(result.stdout)
                return {
                    "status": "success",
                    "skill": self.name,
                    "action": "search",
                    "count": len(repos),
                    "results": repos[:10]
                }
            else:
                return {"status": "error", "message": result.stderr}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _create_repo(self, params: Dict) -> Dict[str, Any]:
        """创建仓库"""
        name = params.get("name", "")
        visibility = params.get("visibility", "public")
        
        try:
            cmd = ["gh", "repo", "create", name, "--visibility", visibility, "--confirm"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return {
                    "status": "success",
                    "skill": self.name,
                    "action": "create_repo",
                    "repo": name,
                    "url": f"https://github.com/{name}"
                }
            else:
                return {"status": "error", "message": result.stderr}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _list_issues(self, params: Dict) -> Dict[str, Any]:
        """列出 Issue"""
        repo = params.get("repo", "")
        state = params.get("state", "open")
        
        try:
            cmd = ["gh", "issue", "list", "--repo", repo, "--state", state, "--json", "number,title,state"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                import json
                issues = json.loads(result.stdout)
                return {
                    "status": "success",
                    "skill": self.name,
                    "action": "list_issues",
                    "repo": repo,
                    "count": len(issues),
                    "issues": issues[:20]
                }
            else:
                return {"status": "error", "message": result.stderr}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _create_pr(self, params: Dict) -> Dict[str, Any]:
        """创建 PR"""
        title = params.get("title", "")
        body = params.get("body", "")
        base = params.get("base", "main")
        head = params.get("head", "feature")
        
        try:
            cmd = ["gh", "pr", "create", "--title", title, "--body", body, "--base", base, "--head", head]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return {
                    "status": "success",
                    "skill": self.name,
                    "action": "create_pr",
                    "message": "PR 创建成功"
                }
            else:
                return {"status": "error", "message": result.stderr}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_status(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "category": self.category,
            "status": "active"
        }


__all__ = ["GithubIntegrationSkill"]
