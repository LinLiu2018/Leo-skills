#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Documentation Synchronization System

自动同步Leo系统文档，确保文档与实际系统状态一致。
基于技能发现系统的最新数据更新所有相关文档。
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from leo_subagents.skills_bridge.skill_discovery_simple import SkillDiscoverySystem

def safe_print(text):
    """安全打印，避免编码错误"""
    try:
        print(text)
    except UnicodeEncodeError:
        safe_text = text.encode('ascii', 'ignore').decode('ascii')
        print(safe_text)

class DocumentationSync:
    """文档同步系统"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.discovery = SkillDiscoverySystem(project_root)
        
        # 文档路径
        self.context_path = project_root / "leo_knowledge" / "context"
        self.docs_path = project_root / "docs"
        self.readme_path = project_root / "README.md"
        self.skills_manifest_path = project_root / "SKILLS_MANIFEST.md"
        
    def sync_capability_index(self):
        """同步能力索引"""
        safe_print("同步能力索引...")
        
        # 获取技能数据
        skills = self.discovery.registry.get('skills', {})
        categories = self.discovery.registry.get('categories', {})
        
        # 按分类分组技能
        skill_list = []
        for skill_key, skill_data in skills.items():
            if skill_data.get('is_valid', False):
                category = skill_data.get('category', 'unknown')
                skill_list.append(f"- **{skill_data['name']}**: {category}/{skill_data['name']}")
        
        # 读取Agents和Workflows
        agents_path = self.project_root / "leo_subagents" / "agents"
        agents = []
        if agents_path.exists():
            for item in agents_path.iterdir():
                if item.is_dir() and not item.name.startswith('_'):
                    agents.append(f"- **{item.name}**")
        
        workflows_path = self.project_root / "leo_workflows" / "workflows"
        workflows = []
        if workflows_path.exists():
            for item in workflows_path.iterdir():
                if item.is_dir() and not item.name.startswith('_'):
                    workflows.append(f"- **{item.name}**")
        
        content = [
            "# System Capabilities Index (Auto-Generated)",
            f"> Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n",
            "## 🧩 Skills (能力库)",
            "\\n".join(sorted(skill_list)) if skill_list else "- No skills found",
            "\\n## 🤖 Subagents (代理库)",
            "\\n".join(sorted(agents)) if agents else "- No agents found",
            "\\n## 🌊 Workflows (工作流)",
            "\\n".join(sorted(workflows)) if workflows else "- No workflows found"
        ]
        
        output_path = self.context_path / "capability_index.md"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("\\n".join(content))
        
        safe_print(f"[SUCCESS] 能力索引已更新: {output_path}")
    
    def update_skills_manifest(self):
        """更新技能清单"""
        safe_print("更新技能清单...")
        
        skills = self.discovery.registry.get('skills', {})
        categories = self.discovery.registry.get('categories', {})
        
        # 统计有效技能
        valid_skills = [s for s in skills.values() if s.get('is_valid', False)]
        
        # 按分类统计
        category_stats = {}
        category_details = {}
        
        for skill_data in valid_skills:
            category = skill_data.get('category', 'unknown')
            if category not in category_stats:
                category_stats[category] = 0
                category_details[category] = []
            category_stats[category] += 1
            category_details[category].append(skill_data)
        
        # 生成技能清单内容
        content = [
            "# Leo Skills Manifest",
            "",
            "**Leo 的 Claude Code 技能清单** - 基于自动发现系统的实时技能索引",
            "",
            "---",
            "",
            "## 技能总览",
            "",
            "| 分类 | 技能数 | 状态 |",
            "|------|--------|------|",
        ]
        
        for category, count in sorted(category_stats.items()):
            content.append(f"| {category} | {count} | 🟢 活跃 |")
        
        content.extend([
            "",
            f"**总计**: {len(valid_skills)} 个活跃技能",
            "",
            "---",
            "",
            "## 详细清单",
            "",
        ])
        
        for category, category_skills in sorted(category_details.items()):
            content.append(f"### 📁 {category.title()}")
            content.append("")
            
            for skill_data in sorted(category_skills, key=lambda x: x['name']):
                content.extend([
                    f"#### {skill_data['name']}",
                    f"- **路径**: `{skill_data['category']}/{skill_data['name']}/`",
                    f"- **描述**: {skill_data.get('description', '暂无描述')}",
                    f"- **版本**: {skill_data.get('version', '1.0.0')}",
                    f"- **状态**: {'🟢 有效' if skill_data.get('is_valid') else '🔴 无效'}",
                    ""
                ])
                
                # 添加关键词信息
                keywords = skill_data.get('keywords', [])
                if keywords:
                    content.append(f"- **关键词**: {', '.join(keywords)}")
                
                # 添加入口点信息
                entry_point = skill_data.get('entry_point', 'scripts/main.py')
                content.append(f"- **入口点**: `{entry_point}`")
                content.append("")
        
        # 添加使用指南
        content.extend([
            "---",
            "",
            "## 使用指南",
            "",
            "### 自动技能管理",
            "```bash",
            "# 更新技能注册表",
            "python scripts/manage_skills.py update",
            "",
            "# 查看所有技能",
            "python scripts/manage_skills.py list",
            "",
            "# 搜索技能",
            "python scripts/manage_skills.py search --query <关键词>",
            "",
            "# 为Claude Code生成技能目录",
            "python scripts/manage_skills.py install",
            "```",
            "",
            "---",
            "",
            f"**最后更新**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**生成方式**: 技能自动发现系统",
            f"**总技能数**: {len(valid_skills)}",
        ])
        
        # 写入文件
        with open(self.skills_manifest_path, 'w', encoding='utf-8') as f:
            f.write("\\n".join(content))
        
        safe_print(f"[SUCCESS] 技能清单已更新: {self.skills_manifest_path}")
    
    def update_main_readme(self):
        """更新主README"""
        safe_print("更新主README...")
        
        status = self.discovery.get_status_report()
        valid_skills = status['valid_skills']
        categories = status['categories']
        
        content = [
            "# Leo Skills Collection",
            "",
            "**Leo 的 Claude Code 技能合集** - 自动化技能发现与管理系统",
            "",
            "---",
            "",
            "## 🚀 快速开始",
            "",
            "### 1. 系统要求",
            "- Python 3.8+",
            "- Claude Code (已安装)",
            "",
            "### 2. 自动技能管理",
            "",
            "```bash",
            "# 更新技能注册表",
            "python scripts/manage_skills.py update",
            "",
            "# 查看系统状态",
            "python scripts/manage_skills.py status",
            "",
            "# 为Claude Code生成技能目录",
            "python scripts/manage_skills.py install",
            "```",
            "",
            "### 3. 技能统计",
            "",
            f"- **总技能数**: {status['total_skills']}",
            f"- **有效技能**: {valid_skills}",
            f"- **分类数**: {categories}",
            f"- **最后更新**: {status['last_updated']}",
            "",
            "---",
            "",
            "## 📁 技能分类",
            ""
        ]
        
        # 添加各分类概览
        skills_by_category = {}
        for skill_data in self.discovery.registry.get('skills', {}).values():
            if skill_data.get('is_valid', False):
                category = skill_data.get('category', 'unknown')
                if category not in skills_by_category:
                    skills_by_category[category] = []
                skills_by_category[category].append(skill_data)
        
        for category, category_skills in sorted(skills_by_category.items()):
            content.extend([
                f"### {category.title()} ({len(category_skills)} 个技能)",
                ""
            ])
            
            for skill_data in sorted(category_skills, key=lambda x: x['name'])[:5]:  # 只显示前5个
                content.extend([
                    f"- **{skill_data['name']}**: {skill_data.get('description', '暂无描述')[:50]}..."
                ])
            
            if len(category_skills) > 5:
                content.append(f"- *... 还有 {len(category_skills) - 5} 个技能*")
            
            content.append("")
        
        # 添加开发指南
        content.extend([
            "---",
            "",
            "## 🛠️ 开发指南",
            "",
            "### 技能开发规范",
            "",
            "每个技能必须包含：",
            "- `SKILL.md` - 技能定义文档",
            "- `scripts/main.py` - 入口脚本",
            "- `README.md` - 使用说明",
            "",
            "### 测试",
            "",
            "```bash",
            "# 运行所有测试",
            "pytest",
            "",
            "# 运行测试并生成覆盖率报告",
            "pytest --cov=leo_skills --cov-report=html",
            "```",
            "",
            "---",
            "",
            "## 📚 相关文档",
            "",
            "- [技能清单](SKILLS_MANIFEST.md) - 完整技能列表",
            "- [系统架构](leo_knowledge/context/system_architecture.md)",
            "- [开发指南](leo_knowledge/context/development_guide.md)",
            "- [用户档案](leo_knowledge/context/user_profile.md)",
            "",
            "---",
            "",
            f"**自动生成于**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "**作者**: Leo Liu",
            ""
        ])
        
        # 写入文件
        with open(self.readme_path, 'w', encoding='utf-8') as f:
            f.write("\\n".join(content))
        
        safe_print(f"[SUCCESS] 主README已更新: {self.readme_path}")
    
    def sync_all(self):
        """同步所有文档"""
        safe_print("=== 开始文档同步 ===")
        
        # 确保技能注册表是最新的
        self.discovery.update_registry()
        
        # 同步各个文档
        self.sync_capability_index()
        self.update_skills_manifest()
        self.update_main_readme()
        
        safe_print("\n[SUCCESS] 所有文档同步完成!")
        
        # 显示同步统计
        status = self.discovery.get_status_report()
        safe_print(f"\n=== 同步统计 ===")
        safe_print(f"总技能数: {status['total_skills']}")
        safe_print(f"有效技能: {status['valid_skills']}")
        safe_print(f"无效技能: {status['invalid_skills']}")
        safe_print(f"分类数: {status['categories']}")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Documentation Synchronization System')
    parser.add_argument('--project-root', type=str, default='.', help='Project root directory')
    parser.add_argument('--capability-index', action='store_true', help='Sync capability index only')
    parser.add_argument('--skills-manifest', action='store_true', help='Sync skills manifest only')
    parser.add_argument('--readme', action='store_true', help='Sync main README only')
    
    args = parser.parse_args()
    
    # 创建文档同步系统
    sync = DocumentationSync(Path(args.project_root))
    
    if args.capability_index:
        sync.sync_capability_index()
    elif args.skills_manifest:
        sync.update_skills_manifest()
    elif args.readme:
        sync.update_main_readme()
    else:
        # 默认同步所有文档
        sync.sync_all()

if __name__ == "__main__":
    main()