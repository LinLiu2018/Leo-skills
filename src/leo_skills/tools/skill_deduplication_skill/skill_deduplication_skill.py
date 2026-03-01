"""
Skill Deduplication Skill - 技能去重检查

扫描所有技能，检测功能重复和命名冲突，提供合并建议。
"""
from leo_skills.core.base_executor import BaseExecutor

from typing import Dict, Any, List, Set
from pathlib import Path
import os


class SkillDeduplicationSkill(BaseExecutor):
    """
    技能去重检查技能
    
    功能:
    - 扫描所有技能目录
    - 检测命名冲突
    - 检测功能重复
    - 提供合并建议
    """
    
    def __init__(self):
        self.name = "skill_deduplication_skill"
        self.version = "1.0.0"
        self.category = "tools"
        
        self.workspace = Path(__file__).parent.parent.parent.parent
        self.skills_dir = self.workspace / "src" / "leo_skills"
    
    def execute(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """执行技能去重检查"""
        params = params or {}
        
        result = {
            "status": "success",
            "skill": self.name,
            "action": "skill_deduplication",
            "checks": []
        }
        
        # 检查 1: 命名冲突
        naming_conflicts = self._check_naming_conflicts()
        result["checks"].append({
            "type": "naming_conflicts",
            "count": len(naming_conflicts),
            "items": naming_conflicts
        })
        
        # 检查 2: 功能重复
        functional_duplicates = self._check_functional_duplicates()
        result["checks"].append({
            "type": "functional_duplicates",
            "count": len(functional_duplicates),
            "items": functional_duplicates
        })
        
        # 检查 3: 能力重叠
        capability_overlaps = self._check_capability_overlaps()
        result["checks"].append({
            "type": "capability_overlaps",
            "count": len(capability_overlaps),
            "items": capability_overlaps
        })
        
        return result
    
    def _check_naming_conflicts(self) -> List[Dict[str, Any]]:
        """检查命名冲突"""
        conflicts = []
        names: Set[str] = set()
        
        for category in self.skills_dir.iterdir():
            if not category.is_dir():
                continue
            for skill_dir in category.iterdir():
                if not skill_dir.is_dir():
                    continue
                name = skill_dir.name
                if name in names:
                    conflicts.append({
                        "name": name,
                        "paths": [str(skill_dir)],
                        "severity": "high"
                    })
                names.add(name)
        
        return conflicts
    
    def _check_functional_duplicates(self) -> List[Dict[str, Any]]:
        """检查功能重复"""
        # TODO: 实现功能重复检测逻辑
        return []
    
    def _check_capability_overlaps(self) -> List[Dict[str, Any]]:
        """检查能力重叠"""
        # TODO: 实现能力重叠检测逻辑
        return []
    
    def get_status(self) -> Dict[str, Any]:
        """获取技能状态"""
        return {
            "name": self.name,
            "version": self.version,
            "category": self.category,
            "status": "active"
        }


__all__ = ["SkillDeduplicationSkill"]
