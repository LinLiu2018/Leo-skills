"""
增强版 Skill 加载器
===================
支持递归扫描、多种命名模式、Workflow 加载
"""

import os
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class SkillInfo:
    """Skill 信息"""
    name: str
    path: str
    category: str
    subcategory: str = ""
    description: str = ""
    version: str = "1.0.0"
    enabled: bool = True
    has_skill_md: bool = False
    has_readme: bool = False
    has_scripts: bool = False
    actions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "path": self.path,
            "category": self.category,
            "subcategory": self.subcategory,
            "description": self.description,
            "version": self.version,
            "enabled": self.enabled,
            "has_skill_md": self.has_skill_md,
            "has_readme": self.has_readme,
            "has_scripts": self.has_scripts,
            "actions": self.actions
        }


@dataclass
class WorkflowInfo:
    """Workflow 信息"""
    name: str
    path: str
    description: str = ""
    steps: List[Dict] = field(default_factory=list)
    enabled: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "path": self.path,
            "description": self.description,
            "steps": self.steps,
            "enabled": self.enabled
        }


class EnhancedSkillLoader:
    """
    增强版 Skill 加载器
    ==================
    - 递归扫描所有目录
    - 支持多种命名模式（-cskill, -skills, 无后缀）
    - 加载 Workflows
    - 更好的元数据提取
    """
    
    # 识别为 Skill 的文件标记
    SKILL_MARKERS = ['SKILL.md', 'README.md', 'skill.yaml', 'skill.yml']
    
    # 排除的目录
    EXCLUDE_DIRS = {
        '__pycache__', '.git', '.github', 'node_modules', 
        '.evolution_data', 'demo_output', 'test_output',
        'venv', '.venv', 'env', '.env'
    }
    
    def __init__(self, 
                 skills_path: Optional[Path] = None,
                 workflows_path: Optional[Path] = None):
        """初始化加载器"""
        if skills_path is None:
            current_file = Path(__file__).parent.parent.parent
            skills_path = current_file / "leo-skills"
        if workflows_path is None:
            current_file = Path(__file__).parent.parent.parent
            workflows_path = current_file / "leo_workflows" / "workflows"
        
        self.skills_path = Path(skills_path)
        self.workflows_path = Path(workflows_path)
        
        self.skills: Dict[str, SkillInfo] = {}
        self.workflows: Dict[str, WorkflowInfo] = {}
        self.categories: Dict[str, List[str]] = {}
        self.stats = {
            "total_skills": 0,
            "total_workflows": 0,
            "by_category": {},
            "scan_depth": 0
        }
    
    def discover_all(self) -> Dict[str, Any]:
        """
        发现所有 Skills 和 Workflows
        
        Returns:
            发现的统计信息
        """
        print(f"🔍 扫描 Skills 目录: {self.skills_path}")
        
        # 扫描 Skills
        if self.skills_path.exists():
            self._scan_skills_recursive(self.skills_path, "", 0)
        
        # 扫描 Workflows
        if self.workflows_path.exists():
            self._scan_workflows()
        
        self.stats["total_skills"] = len(self.skills)
        self.stats["total_workflows"] = len(self.workflows)
        self.stats["by_category"] = {cat: len(skills) for cat, skills in self.categories.items()}
        
        print(f"✅ 发现 {len(self.skills)} 个 Skills, {len(self.workflows)} 个 Workflows")
        
        return self.stats
    
    def _scan_skills_recursive(self, 
                                directory: Path, 
                                parent_category: str,
                                depth: int,
                                max_depth: int = 5):
        """递归扫描目录发现 Skills"""
        if depth > max_depth:
            return
        
        self.stats["scan_depth"] = max(self.stats["scan_depth"], depth)
        
        for item in directory.iterdir():
            if not item.is_dir():
                continue
            
            # 跳过排除的目录
            if item.name in self.EXCLUDE_DIRS or item.name.startswith('.'):
                continue
            
            # 检查是否为 Skill 目录
            if self._is_skill_directory(item):
                skill_info = self._extract_skill_info(item, parent_category)
                if skill_info:
                    self.skills[skill_info.name] = skill_info
                    
                    # 更新分类
                    cat = skill_info.category or "uncategorized"
                    if cat not in self.categories:
                        self.categories[cat] = []
                    self.categories[cat].append(skill_info.name)
                    
                    print(f"  ✅ {skill_info.name} ({cat})")
            else:
                # 递归扫描子目录
                new_category = f"{parent_category}/{item.name}" if parent_category else item.name
                self._scan_skills_recursive(item, new_category, depth + 1, max_depth)
    
    def _is_skill_directory(self, directory: Path) -> bool:
        """判断目录是否为 Skill 目录"""
        # 方式1：包含标记文件
        for marker in self.SKILL_MARKERS:
            if (directory / marker).exists():
                return True
        
        # 方式2：名称以 -cskill 或 -skills 结尾
        if directory.name.endswith(('-cskill', '-skills')):
            return True
        
        # 方式3：包含 scripts 目录和配置文件
        if (directory / 'scripts').exists() and (
            (directory / 'config').exists() or 
            any(directory.glob('*.yaml')) or
            any(directory.glob('*.yml'))
        ):
            return True
        
        return False
    
    def _extract_skill_info(self, directory: Path, parent_category: str) -> Optional[SkillInfo]:
        """提取 Skill 信息"""
        name = directory.name
        
        # 解析分类
        parts = parent_category.split('/') if parent_category else []
        category = parts[0] if parts else "general"
        subcategory = '/'.join(parts[1:]) if len(parts) > 1 else ""
        
        # 检查文件存在
        has_skill_md = (directory / 'SKILL.md').exists()
        has_readme = (directory / 'README.md').exists()
        has_scripts = (directory / 'scripts').exists()
        
        # 尝试从 SKILL.md 提取描述
        description = ""
        if has_skill_md:
            description = self._extract_description_from_skill_md(directory / 'SKILL.md')
        elif has_readme:
            description = self._extract_description_from_readme(directory / 'README.md')
        
        # 尝试加载 skill.yaml
        version = "1.0.0"
        actions = []
        skill_yaml = directory / 'skill.yaml'
        if not skill_yaml.exists():
            skill_yaml = directory / 'skill.yml'
        
        if skill_yaml.exists():
            try:
                with open(skill_yaml, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    version = data.get('version', version)
                    actions = data.get('actions', [])
                    if not description:
                        description = data.get('description', '')
            except:
                pass
        
        return SkillInfo(
            name=name,
            path=str(directory),
            category=category,
            subcategory=subcategory,
            description=description[:200] if description else f"{name} Skill",
            version=version,
            enabled=True,
            has_skill_md=has_skill_md,
            has_readme=has_readme,
            has_scripts=has_scripts,
            actions=actions
        )
    
    def _extract_description_from_skill_md(self, path: Path) -> str:
        """从 SKILL.md 提取描述"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 查找 description 字段（YAML frontmatter）
            if content.startswith('---'):
                end = content.find('---', 3)
                if end != -1:
                    frontmatter = content[3:end]
                    try:
                        data = yaml.safe_load(frontmatter)
                        if isinstance(data, dict) and 'description' in data:
                            return data['description']
                    except:
                        pass
            
            # 查找第一个段落
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#') and not line.startswith('-'):
                    return line[:200]
            
            return ""
        except:
            return ""
    
    def _extract_description_from_readme(self, path: Path) -> str:
        """从 README.md 提取描述"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 跳过标题，找第一个非空段落
            for i, line in enumerate(lines):
                line = line.strip()
                if line and not line.startswith('#'):
                    return line[:200]
            
            return ""
        except:
            return ""
    
    def _scan_workflows(self):
        """扫描 Workflows"""
        print(f"🔍 扫描 Workflows 目录: {self.workflows_path}")
        
        if not self.workflows_path.exists():
            return
        
        for item in self.workflows_path.iterdir():
            if item.is_dir():
                workflow_info = self._extract_workflow_info(item)
                if workflow_info:
                    self.workflows[workflow_info.name] = workflow_info
                    print(f"  ✅ Workflow: {workflow_info.name}")
    
    def _extract_workflow_info(self, directory: Path) -> Optional[WorkflowInfo]:
        """提取 Workflow 信息"""
        name = directory.name
        description = ""
        steps = []
        
        # 查找 workflow.yaml
        workflow_file = directory / 'workflow.yaml'
        if not workflow_file.exists():
            workflow_file = directory / 'workflow.yml'
        
        if workflow_file.exists():
            try:
                with open(workflow_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    description = data.get('description', '')
                    steps = data.get('steps', [])
            except:
                pass
        
        # 查找 README
        readme = directory / 'README.md'
        if readme.exists() and not description:
            description = self._extract_description_from_readme(readme)
        
        return WorkflowInfo(
            name=name,
            path=str(directory),
            description=description or f"{name} 工作流",
            steps=steps,
            enabled=True
        )
    
    def get_skill(self, name: str) -> Optional[SkillInfo]:
        """获取 Skill"""
        return self.skills.get(name)
    
    def get_workflow(self, name: str) -> Optional[WorkflowInfo]:
        """获取 Workflow"""
        return self.workflows.get(name)
    
    def list_skills(self, category: Optional[str] = None) -> List[str]:
        """列出 Skills"""
        if category:
            return self.categories.get(category, [])
        return list(self.skills.keys())
    
    def list_workflows(self) -> List[str]:
        """列出 Workflows"""
        return list(self.workflows.keys())
    
    def list_categories(self) -> List[str]:
        """列出所有分类"""
        return list(self.categories.keys())
    
    def get_summary(self) -> Dict[str, Any]:
        """获取汇总信息"""
        return {
            "skills": {
                "total": len(self.skills),
                "by_category": {cat: len(skills) for cat, skills in self.categories.items()},
                "list": [s.to_dict() for s in self.skills.values()]
            },
            "workflows": {
                "total": len(self.workflows),
                "list": [w.to_dict() for w in self.workflows.values()]
            },
            "stats": self.stats
        }


# ==================== 全局实例 ====================

_enhanced_loader: Optional[EnhancedSkillLoader] = None


def get_enhanced_loader() -> EnhancedSkillLoader:
    """获取增强版加载器"""
    global _enhanced_loader
    if _enhanced_loader is None:
        _enhanced_loader = EnhancedSkillLoader()
        _enhanced_loader.discover_all()
    return _enhanced_loader


# ==================== 命令行测试 ====================

if __name__ == "__main__":
    loader = EnhancedSkillLoader()
    loader.discover_all()
    
    print("\n" + "=" * 60)
    print("📊 Skills 汇总")
    print("=" * 60)
    
    for cat, skills in sorted(loader.categories.items()):
        print(f"\n📁 {cat} ({len(skills)} 个):")
        for skill_name in skills[:10]:  # 只显示前10个
            skill = loader.skills[skill_name]
            print(f"  • {skill_name}")
            if skill.description:
                print(f"    {skill.description[:60]}...")
        if len(skills) > 10:
            print(f"  ... 还有 {len(skills) - 10} 个")
    
    print(f"\n📋 Workflows ({len(loader.workflows)} 个):")
    for name in loader.workflows:
        print(f"  • {name}")
    
    print("\n" + "=" * 60)
