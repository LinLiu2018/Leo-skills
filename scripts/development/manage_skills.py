#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Leo Skills Management CLI

简化的技能管理命令行工具，用于替代手动符号链接
"""

import sys
from pathlib import Path

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

def main():
    """简化的命令行界面"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Leo Skills Management CLI')
    parser.add_argument('command', choices=['update', 'status', 'search', 'install', 'list'], 
                       help='Command to execute')
    parser.add_argument('--query', type=str, help='Search query (for search command)')
    parser.add_argument('--category', type=str, help='Filter by category (for list command)')
    parser.add_argument('--project-root', type=str, default='.', help='Project root directory')
    
    args = parser.parse_args()
    
    # 创建发现系统
    discovery = SkillDiscoverySystem(Path(args.project_root))
    
    if args.command == 'update':
        safe_print("正在更新技能注册表...")
        result = discovery.update_registry()
        safe_print(f"[SUCCESS] 注册表已更新")
        safe_print(f"  新技能: {len(result['new_skills'])} 个")
        safe_print(f"  更新技能: {len(result['updated_skills'])} 个")
        safe_print(f"  总技能数: {result['total_skills']} 个")
    
    elif args.command == 'status':
        report = discovery.get_status_report()
        safe_print("=== Leo Skills 系统状态 ===")
        safe_print(f"总技能数: {report['total_skills']}")
        safe_print(f"有效技能: {report['valid_skills']}")
        safe_print(f"无效技能: {report['invalid_skills']}")
        safe_print(f"分类数: {report['categories']}")
        safe_print(f"最后更新: {report['last_updated']}")
        
        if report['invalid_skills'] > 0:
            safe_print("\n[警告] 发现无效技能:")
            for skill_detail in report['invalid_skill_details']:
                safe_print(f"  - {skill_detail['name']}: {', '.join(skill_detail['errors'])}")
    
    elif args.command == 'search':
        if not args.query:
            safe_print("[ERROR] 搜索命令需要 --query 参数")
            return
        
        results = discovery.search_skills(args.query)
        safe_print(f"找到 {len(results)} 个匹配 '{args.query}' 的技能:")
        for skill in results:
            status = "[有效]" if skill.get('is_valid', False) else "[无效]"
            safe_print(f"  {status} {skill.get('name', 'Unknown')} ({skill.get('category', 'unknown')})")
            safe_print(f"    {skill.get('description', '')}")
            keywords = skill.get('keywords', [])
            if keywords:
                safe_print(f"    关键词: {', '.join(keywords)}")
    
    elif args.command == 'list':
        skills = list(discovery.registry.get('skills', {}).values())
        
        if args.category:
            skills = [s for s in skills if s.get('category') == args.category]
            safe_print(f"分类 '{args.category}' 中的技能:")
        else:
            safe_print("所有技能:")
        
        # 按分类分组显示
        categories = {}
        for skill in skills:
            category = skill.get('category', 'unknown')
            if category not in categories:
                categories[category] = []
            categories[category].append(skill)
        
        for category, category_skills in categories.items():
            safe_print(f"\n📁 {category} ({len(category_skills)} 个技能)")
            for skill in category_skills:
                status = "[有效]" if skill.get('is_valid', False) else "[无效]"
                safe_print(f"  {status} {skill.get('name', 'Unknown')}")
                description = skill.get('description', '')
                if description:
                    safe_print(f"    {description[:80]}...")
    
    elif args.command == 'install':
        safe_print("正在为Claude Code生成技能目录...")
        success = discovery.generate_claude_skills_directory()
        if success:
            safe_print("[SUCCESS] 技能目录已生成")
            safe_print("现在可以在Claude Code中使用这些技能了")
        else:
            safe_print("[ERROR] 技能目录生成失败")

if __name__ == "__main__":
    main()