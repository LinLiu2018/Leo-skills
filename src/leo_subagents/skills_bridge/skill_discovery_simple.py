#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Leo Skills Auto-Discovery System - 简化版本

自动发现、验证和管理Leo技能的系统，替代手动符号链接。
"""

import os
import sys
import json
import yaml
import hashlib
import importlib.util
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

# 添加父目录到路径
parent_path = Path(__file__).parent.parent.parent
if str(parent_path) not in sys.path:
    sys.path.insert(0, str(parent_path))

from leo_system.logger import get_logger

# 创建日志记录器
logger = get_logger(__name__)

@dataclass
class SkillMetadata:
    """技能元数据"""
    name: str
    path: str
    category: str
    version: str = "1.0.0"
    description: str = ""
    author: str = "Leo Liu"
    keywords: List[str] = None
    activation_keywords: List[str] = None
    entry_point: str = "scripts/main.py"
    dependencies: List[str] = None
    last_modified: str = ""
    checksum: str = ""
    is_valid: bool = False
    validation_errors: List[str] = None
    loaded_at: Optional[str] = None
    
    def __post_init__(self):
        if self.keywords is None:
            self.keywords = []
        if self.activation_keywords is None:
            self.activation_keywords = []
        if self.dependencies is None:
            self.dependencies = []
        if self.validation_errors is None:
            self.validation_errors = []

class SkillDiscoverySystem:
    """技能发现系统 - 简化版"""
    
    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path.cwd()

        self.project_root = project_root
        # 优先使用 src/leo_skills，如果不存在则回退到 leo_skills
        self.skills_path = project_root / "src" / "leo_skills"
        if not self.skills_path.exists():
            self.skills_path = project_root / "leo_skills"
        self.registry_path = project_root / ".claude" / "skill_registry.json"
        self.cache_dir = project_root / ".claude" / "cache"
        
        # 确保目录存在
        self.registry_path.parent.mkdir(exist_ok=True)
        self.cache_dir.mkdir(exist_ok=True)
        
        self.registry = self._load_registry()
        
    def _load_registry(self) -> Dict[str, Any]:
        """加载技能注册表"""
        if self.registry_path.exists():
            try:
                with open(self.registry_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load registry: {e}")
        
        # 创建空注册表
        return {
            'skills': {},
            'categories': {},
            'last_updated': datetime.now().isoformat()
        }
    
    def _save_registry(self):
        """保存技能注册表"""
        try:
            with open(self.registry_path, 'w', encoding='utf-8') as f:
                json.dump(self.registry, f, indent=2, ensure_ascii=False)
            logger.info(f"Registry saved to {self.registry_path}")
        except Exception as e:
            logger.error(f"Failed to save registry: {e}")
    
    def _calculate_checksum(self, skill_path: Path) -> str:
        """计算技能目录的校验和"""
        hash_md5 = hashlib.md5()
        
        # 只计算关键文件的校验和
        key_files = ["SKILL.md", "scripts/main.py", "README.md"]
        
        for file_name in key_files:
            file_path = skill_path / file_name
            if file_path.exists():
                with open(file_path, 'rb') as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        hash_md5.update(chunk)
        
        return hash_md5.hexdigest()
    
    def _validate_skill(self, skill_path: Path) -> Tuple[bool, List[str]]:
        """验证技能结构"""
        errors = []
        
        # 检查必要文件
        required_files = ["SKILL.md"]
        for file_name in required_files:
            if not (skill_path / file_name).exists():
                errors.append(f"Missing required file: {file_name}")
        
        # 检查入口点
        entry_point = skill_path / "scripts" / "main.py"
        if not entry_point.exists():
            # 尝试其他可能的入口点
            alternative_entries = ["main.py", "__init__.py"]
            entry_found = False
            for alt in alternative_entries:
                if (skill_path / alt).exists():
                    entry_found = True
                    break
            if not entry_found:
                errors.append("No valid entry point found")
        
        # 检查SKILL.md格式
        skill_md = skill_path / "SKILL.md"
        if skill_md.exists():
            try:
                with open(skill_md, 'r', encoding='utf-8') as f:
                    content = f.read()
                if len(content.strip()) < 50:
                    errors.append("SKILL.md content too short")
            except Exception as e:
                errors.append(f"Failed to read SKILL.md: {e}")
        
        return len(errors) == 0, errors
    
    def discover_skills(self) -> Dict[str, Dict[str, Any]]:
        """发现所有技能"""
        if not self.skills_path.exists():
            logger.warning(f"Skills path not found: {self.skills_path}")
            return {}
        
        discovered_skills = {}
        
        for category_dir in self.skills_path.iterdir():
            if not category_dir.is_dir() or category_dir.name.startswith('.'):
                continue
            
            category_name = category_dir.name
            logger.info(f"Scanning category: {category_name}")
            
            for skill_dir in category_dir.iterdir():
                if not skill_dir.is_dir() or skill_dir.name.startswith('.'):
                    continue
                
                skill_name = skill_dir.name
                logger.debug(f"Found skill: {skill_name}")
                
                # 验证技能
                is_valid, validation_errors = self._validate_skill(skill_dir)
                
                # 创建技能元数据
                skill_meta = SkillMetadata(
                    name=skill_name,
                    path=str(skill_dir),
                    category=category_name,
                    description=f"Skill in {category_name}",
                    last_modified=datetime.fromtimestamp(skill_dir.stat().st_mtime).isoformat(),
                    checksum=self._calculate_checksum(skill_dir),
                    is_valid=is_valid,
                    validation_errors=validation_errors
                )
                
                # 转换为字典
                skill_dict = asdict(skill_meta)
                discovered_skills[f"{category_name}/{skill_name}"] = skill_dict
        
        return discovered_skills
    
    def update_registry(self) -> Dict[str, Any]:
        """更新技能注册表"""
        logger.info("Updating skill registry...")
        
        discovered_skills = self.discover_skills()
        
        # 检查变化
        old_skills = self.registry.get('skills', {})
        new_skills = []
        updated_skills = []
        removed_skills = []
        
        for skill_key, skill_data in discovered_skills.items():
            if skill_key not in old_skills:
                new_skills.append(skill_key)
            else:
                existing = old_skills[skill_key]
                if existing.get('checksum') != skill_data.get('checksum'):
                    updated_skills.append(skill_key)
        
        for skill_key in list(old_skills.keys()):
            if skill_key not in discovered_skills:
                removed_skills.append(skill_key)
        
        # 更新注册表
        self.registry['skills'] = discovered_skills
        
        # 重建分类索引
        categories = {}
        for skill_key, skill_data in discovered_skills.items():
            category = skill_data['category']
            if category not in categories:
                categories[category] = []
            categories[category].append(skill_key)
        self.registry['categories'] = categories
        
        self.registry['last_updated'] = datetime.now().isoformat()
        self._save_registry()
        
        # 输出报告
        logger.info(f"\n[技能发现报告] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"新发现技能: {len(new_skills)} 个")
        logger.info(f"更新技能: {len(updated_skills)} 个")
        logger.info(f"移除技能: {len(removed_skills)} 个")
        logger.info(f"总技能数: {len(discovered_skills)} 个")
        
        if new_skills:
            logger.info("\n[新技能]")
            for skill_key in new_skills:
                logger.info(f"  + {skill_key}")
        
        if updated_skills:
            logger.info("\n[更新技能]")
            for skill_key in updated_skills:
                logger.info(f"  ~ {skill_key}")
        
        if removed_skills:
            logger.info("\n[移除技能]")
            for skill_key in removed_skills:
                logger.info(f"  - {skill_key}")
        
        return {
            'new_skills': new_skills,
            'updated_skills': updated_skills,
            'removed_skills': removed_skills,
            'total_skills': len(discovered_skills)
        }
    
    def get_status_report(self) -> Dict[str, Any]:
        """获取系统状态报告"""
        skills = self.registry.get('skills', {})
        valid_skills = [s for s in skills.values() if s.get('is_valid', False)]
        invalid_skills = [s for s in skills.values() if not s.get('is_valid', False)]
        
        return {
            'total_skills': len(skills),
            'valid_skills': len(valid_skills),
            'invalid_skills': len(invalid_skills),
            'categories': len(self.registry.get('categories', {})),
            'last_updated': self.registry.get('last_updated'),
            'registry_path': str(self.registry_path),
            'skills_path': str(self.skills_path),
            'invalid_skill_details': [
                {
                    'name': s['name'],
                    'path': s['path'],
                    'errors': s.get('validation_errors', [])
                }
                for s in invalid_skills
            ]
        }
    
    def search_skills(self, query: str) -> List[Dict[str, Any]]:
        """搜索技能"""
        query = query.lower()
        results = []
        
        for skill_data in self.registry.get('skills', {}).values():
            # 搜索名称、描述、关键词
            if (query in skill_data['name'].lower() or 
                query in skill_data.get('description', '').lower() or
                any(query in keyword.lower() for keyword in skill_data.get('keywords', []))):
                results.append(skill_data)
        
        return results
    
    def generate_claude_skills_directory(self, target_dir: Optional[Path] = None) -> bool:
        """为Claude Code生成技能目录（替代符号链接）"""
        if target_dir is None:
            target_dir = Path.home() / ".claude" / "skills"
        
        try:
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # 创建技能索引文件
            index_file = target_dir / "leo_skills_index.json"
            index_data = {
                'source': str(self.skills_path),
                'skills': {},
                'last_updated': self.registry.get('last_updated')
            }
            
            # 为每个技能创建入口文件
            for skill_key, skill_data in self.registry.get('skills', {}).items():
                if not skill_data.get('is_valid', False):
                    continue
                
                skill_name = skill_data['name']
                skill_path = Path(skill_data['path'])
                
                # 创建简化的技能入口文件
                skill_entry = target_dir / f"leo_{skill_name.replace('-', '_')}.py"
                
                entry_content = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Auto-generated Leo Skill Entry Point
Skill: {skill_key}
Description: {skill_data.get('description', '')}
"""

import sys
from pathlib import Path

# Add skill path to Python path
skill_path = Path("{skill_path}")
sys.path.insert(0, str(skill_path))

try:
    # Try to import skill
    if (skill_path / "scripts" / "main.py").exists():
        from scripts.main import main as skill_main
    elif (skill_path / "main.py").exists():
        from main import main as skill_main
    else:
        raise ImportError("No valid entry point found")
    
    def main(*args, **kwargs):
        """Skill entry point"""
        return skill_main(*args, **kwargs)
    
    if __name__ == "__main__":
        main()
        
except ImportError as e:
    print(f"[ERROR] Failed to load skill {skill_key}: {{e}}")
'''
                
                with open(skill_entry, 'w', encoding='utf-8') as f:
                    f.write(entry_content)
                
                index_data['skills'][skill_key] = {
                    'entry_file': skill_entry.name,
                    'path': skill_data['path'],
                    'category': skill_data['category'],
                    'loaded_at': skill_data.get('loaded_at')
                }
            
            # 保存索引
            with open(index_file, 'w', encoding='utf-8') as f:
                json.dump(index_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Claude skills directory generated at: {target_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to generate Claude skills directory: {e}")
            return False