#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Leo Skills Auto-Discovery System

自动发现、验证和管理Leo技能的现代化系统，替代手动符号链接。
支持热加载、版本管理、依赖检查和性能监控。
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
    path: Path
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

@dataclass
class SkillRegistry:
    """技能注册表"""
    skills: Dict[str, SkillMetadata]
    categories: Dict[str, List[str]]
    last_updated: str
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'skills': {name: asdict(skill) for name, skill in self.skills.items()},
            'categories': self.categories,
            'last_updated': self.last_updated
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SkillRegistry':
        """从字典创建实例"""
        skills = {name: SkillMetadata(**skill_data) for name, skill_data in data['skills'].items()}
        return cls(
            skills=skills,
            categories=data['categories'],
            last_updated=data['last_updated']
        )

class SkillDiscoverySystem:
    """技能发现系统"""
    
    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path.cwd()
        
        self.project_root = project_root
        self.skills_path = project_root / "leo_skills"
        self.registry_path = project_root / ".claude" / "skill_registry.json"
        self.cache_dir = project_root / ".claude" / "cache"
        
        # 确保目录存在
        self.registry_path.parent.mkdir(exist_ok=True)
        self.cache_dir.mkdir(exist_ok=True)
        
        self.registry: SkillRegistry = self._load_registry()
        
    def _load_registry(self) -> SkillRegistry:
        """加载技能注册表"""
        if self.registry_path.exists():
            try:
                with open(self.registry_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return SkillRegistry.from_dict(data)
            except Exception as e:
                logger.warning(f"Failed to load registry: {e}")
        
        # 创建空注册表
        return SkillRegistry(
            skills={},
            categories={},
            last_updated=datetime.now().isoformat()
        )
    
    def _save_registry(self):
        """保存技能注册表"""
        try:
            with open(self.registry_path, 'w', encoding='utf-8') as f:
                json.dump(self.registry.to_dict(), f, indent=2, ensure_ascii=False)
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
            alternative_entries = ["main.py", "__init__.py", "SKILL.md"]
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
    
    def _extract_metadata_from_skill_md(self, skill_path: Path) -> Dict[str, Any]:
        """从SKILL.md提取元数据"""
        metadata = {}
        skill_md = skill_path / "SKILL.md"
        
        if not skill_md.exists():
            return metadata
        
        try:
            with open(skill_md, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 简单的元数据提取（基于YAML front matter或关键词）
            lines = content.split('\n')
            
            for line in lines:
                line = line.strip()
                
                # 提取描述
                if line.startswith('# ') and 'description' not in metadata:
                    metadata['description'] = line[2:].strip()
                
                # 提取关键词
                if line.lower().startswith('keywords:'):
                    keywords_str = line[9:].strip()
                    metadata['keywords'] = [k.strip() for k in keywords_str.split(',')]
                
                # 提取激活词
                if 'activation' in line.lower() and 'keywords' in line.lower():
                    # 简化处理，实际可能需要更复杂的解析
                    pass
                    
        except Exception as e:
            logger.warning(f"Failed to extract metadata from {skill_md}: {e}")
        
        return metadata
    
    def discover_skills(self) -> Dict[str, SkillMetadata]:
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
                
                # 提取元数据
                extracted_meta = self._extract_metadata_from_skill_md(skill_dir)
                
                # 创建技能元数据
                skill_meta = SkillMetadata(
                    name=skill_name,
                    path=skill_dir,
                    category=category_name,
                    version=extracted_meta.get('version', '1.0.0'),
                    description=extracted_meta.get('description', ''),
                    keywords=extracted_meta.get('keywords', []),
                    activation_keywords=extracted_meta.get('activation_keywords', []),
                    last_modified=datetime.fromtimestamp(skill_dir.stat().st_mtime).isoformat(),
                    checksum=self._calculate_checksum(skill_dir),
                    is_valid=is_valid,
                    validation_errors=validation_errors
                )
                
                discovered_skills[f"{category_name}/{skill_name}"] = skill_meta
        
        return discovered_skills
    
    def update_registry(self):
        """更新技能注册表"""
        logger.info("Updating skill registry...")
        
        discovered_skills = self.discover_skills()
        
        # 检查变化
        new_skills = []
        updated_skills = []
        removed_skills = []
        
        for skill_key, skill_meta in discovered_skills.items():
            if skill_key not in self.registry.skills:
                new_skills.append(skill_key)
            else:
                existing = self.registry.skills[skill_key]
                if existing.checksum != skill_meta.checksum:
                    updated_skills.append(skill_key)
        
        for skill_key in list(self.registry.skills.keys()):
            if skill_key not in discovered_skills:
                removed_skills.append(skill_key)
        
        # 更新注册表
        self.registry.skills = discovered_skills
        
        # 重建分类索引
        categories = {}
        for skill_key, skill_meta in discovered_skills.items():
            category = skill_meta.category
            if category not in categories:
                categories[category] = []
            categories[category].append(skill_key)
        self.registry.categories = categories
        
        self.registry.last_updated = datetime.now().isoformat()
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
    
    def get_skill_by_name(self, skill_name: str) -> Optional[SkillMetadata]:
        """根据名称获取技能"""
        for skill_key, skill_meta in self.registry.skills.items():
            if skill_meta.name == skill_name or skill_key == skill_name:
                return skill_meta
        return None
    
    def get_skills_by_category(self, category: str) -> List[SkillMetadata]:
        """根据分类获取技能"""
        return [skill for skill in self.registry.skills.values() if skill.category == category]
    
    def search_skills(self, query: str) -> List[SkillMetadata]:
        """搜索技能"""
        query = query.lower()
        results = []
        
        for skill_meta in self.registry.skills.values():
            # 搜索名称、描述、关键词
            if (query in skill_meta.name.lower() or 
                query in skill_meta.description.lower() or
                any(query in keyword.lower() for keyword in skill_meta.keywords)):
                results.append(skill_meta)
        
        return results
    
    def load_skill(self, skill_key: str) -> Optional[Any]:
        """动态加载技能"""
        if skill_key not in self.registry.skills:
            logger.error(f"Skill not found: {skill_key}")
            return None
        
        skill_meta = self.registry.skills[skill_key]
        
        if not skill_meta.is_valid:
            logger.error(f"Skill is not valid: {skill_key}")
            return None
        
        # 尝试加载入口点
        entry_path = skill_meta.path / skill_meta.entry_point
        if not entry_path.exists():
            logger.error(f"Entry point not found: {entry_path}")
            return None
        
        try:
            spec = importlib.util.spec_from_file_location(f"skill_{skill_key.replace('/', '_')}", entry_path)
            if spec is None or spec.loader is None:
                logger.error(f"Cannot create spec for {entry_path}")
                return None
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # 记录加载时间
            skill_meta.loaded_at = datetime.now().isoformat()
            self._save_registry()
            
            logger.info(f"Successfully loaded skill: {skill_key}")
            return module
            
        except Exception as e:
            logger.error(f"Failed to load skill {skill_key}: {e}")
            return None
    
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
                'last_updated': self.registry.last_updated
            }
            
            # 为每个技能创建入口文件
            for skill_key, skill_meta in self.registry.skills.items():
                if not skill_meta.is_valid:
                    continue
                
                # 创建简化的技能入口文件
                skill_entry = target_dir / f"leo_{skill_meta.name.replace('-', '_')}.py"
                
                entry_content = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Auto-generated Leo Skill Entry Point
Skill: {skill_key}
Description: {skill_meta.description}
"""

import sys
from pathlib import Path

# Add skill path to Python path
skill_path = Path("{skill_meta.path}")
sys.path.insert(0, str(skill_path))

try:
    # Try to import the skill
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
                    'path': str(skill_meta.path),
                    'category': skill_meta.category,
                    'loaded_at': skill_meta.loaded_at
                }
            
            # 保存索引
            with open(index_file, 'w', encoding='utf-8') as f:
                json.dump(index_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Claude skills directory generated at: {target_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to generate Claude skills directory: {e}")
            return False
    
    def get_status_report(self) -> Dict[str, Any]:
        """获取系统状态报告"""
        valid_skills = [s for s in self.registry.skills.values() if s.is_valid]
        invalid_skills = [s for s in self.registry.skills.values() if not s.is_valid]
        
        return {
            'total_skills': len(self.registry.skills),
            'valid_skills': len(valid_skills),
            'invalid_skills': len(invalid_skills),
            'categories': len(self.registry.categories),
            'last_updated': self.registry.last_updated,
            'registry_path': str(self.registry_path),
            'skills_path': str(self.skills_path),
            'invalid_skill_details': [
                {
                    'name': s.name,
                    'path': str(s.path),
                    'errors': s.validation_errors
                }
                for s in invalid_skills
            ]
        }

def main():
    """主函数 - 可以作为命令行工具使用"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Leo Skills Auto-Discovery System')
    parser.add_argument('--project-root', type=str, default='.', help='Project root directory')
    parser.add_argument('--update', action='store_true', help='Update skill registry')
    parser.add_argument('--status', action='store_true', help='Show system status')
    parser.add_argument('--search', type=str, help='Search skills')
    parser.add_argument('--generate-claude-dir', action='store_true', help='Generate Claude skills directory')
    parser.add_argument('--load', type=str, help='Load and test a specific skill')
    
    args = parser.parse_args()
    
    # 创建发现系统
    discovery = SkillDiscoverySystem(Path(args.project_root))
    
    if args.update:
        result = discovery.update_registry()
        logger.info(f"Registry updated: {result}")
    
    if args.status:
        report = discovery.get_status_report()
        logger.info(json.dumps(report, indent=2, ensure_ascii=False))
    
    if args.search:
        results = discovery.search_skills(args.search)
        logger.info(f"Found {len(results)} skills matching '{args.search}':")
        for skill in results:
            logger.info(f"  - {skill.name} ({skill.category}): {skill.description}")
    
    if args.generate_claude_dir:
        success = discovery.generate_claude_skills_directory()
        logger.info(f"Claude directory generation: {'SUCCESS' if success else 'FAILED'}")
    
    if args.load:
        module = discovery.load_skill(args.load)
        logger.info(f"Skill loading: {'SUCCESS' if module else 'FAILED'}")
    
    # 默认行为：更新注册表
    if not any([args.status, args.search, args.generate_claude_dir, args.load]):
        discovery.update_registry()

if __name__ == "__main__":
    main()