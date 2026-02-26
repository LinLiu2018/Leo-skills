#!/usr/bin/env python3
"""
批量重命名Skills目录并更新所有引用
"""
import os
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
SKILLS_DIR = PROJECT_ROOT / "src" / "leo_skills"

# 重命名映射表
RENAME_MAP = {
    "api_doc_generator_skill": "api_doc_generator_skill",
    "database_migration_skill": "database_migration_skill",
    "database_model_generator_skill": "database_model_generator_skill",
    "fastapi_endpoint_generator_skill": "fastapi_endpoint_generator_skill",
    "flask_api_generator_skill": "flask_api_generator_skill",
    "flask_auth_generator_skill": "flask_auth_generator_skill",
    "content_layout_leo_skill": "content_layout_leo_skill",
    "project_marketing_doc_generator_skill": "project_marketing_doc_generator_skill",
    "realestate_news_publisher_skill": "realestate_news_publisher_skill",
    "text_generator_skill": "text_generator_skill",
    "skill_code_generator_skill": "skill_code_generator_skill",
    "deployment_script_generator_skill": "deployment_script_generator_skill",
    "docker_compose_generator_skill": "docker_compose_generator_skill",
    "dockerfile_generator_skill": "dockerfile_generator_skill",
    "github_actions_generator_skill": "github_actions_generator_skill",
    "nginx_config_generator_skill": "nginx_config_generator_skill",
    "css_layout_generator_skill": "css_layout_generator_skill",
    "miniprogram_component_generator_skill": "miniprogram_component_generator_skill",
    "miniprogram_page_generator_skill": "miniprogram_page_generator_skill",
    "react_component_generator_skill": "react_component_generator_skill",
    "vue_component_generator_skill": "vue_component_generator_skill",
    "vue_page_generator_skill": "vue_page_generator_skill",
    "twitter_monitor_skill": "twitter_monitor_skill",
    "flask_api_scaffold_skill": "flask_api_scaffold_skill",
    "fullstack_project_scaffold_skill": "fullstack_project_scaffold_skill",
    "miniprogram_project_scaffold_skill": "miniprogram_project_scaffold_skill",
    "t3_stack_scaffold_skill": "t3_stack_scaffold_skill",
    "security_scan_skill": "security_scan_skill",
    "api_test_generator_skill": "api_test_generator_skill",
    "e2e_test_generator_skill": "e2e_test_generator_skill",
    "unit_test_generator_skill": "unit_test_generator_skill",
    "agent_skill_creator_skill": "agent_skill_creator_skill",
    "article_to_prototype_skill": "article_to_prototype_skill",
    "skill_evolution_assistant_skill": "skill_evolution_assistant_skill",
    "data_analyzer_skill": "data_analyzer_skill",
    "obsidian_sync_skill": "obsidian_sync_skill",
    "research_assistant_skill": "research_assistant_skill",
    "tech_extractor_skill": "tech_extractor_skill",
    "web_search_skill": "web_search_skill",
}

def rename_directories():
    """重命名目录"""
    renamed = 0
    for category_dir in SKILLS_DIR.iterdir():
        if not category_dir.is_dir() or category_dir.name.startswith("."):
            continue
        for skill_dir in category_dir.iterdir():
            if skill_dir.is_dir() and skill_dir.name in RENAME_MAP:
                new_name = RENAME_MAP[skill_dir.name]
                new_path = skill_dir.parent / new_name
                print(f"重命名: {skill_dir.name} -> {new_name}")
                os.rename(skill_dir, new_path)
                renamed += 1
    return renamed

def update_file_references(file_path: Path):
    """更新文件中的引用"""
    try:
        content = file_path.read_text(encoding='utf-8')
        original = content
        for old_name, new_name in RENAME_MAP.items():
            content = content.replace(old_name, new_name)
        if content != original:
            file_path.write_text(content, encoding='utf-8')
            return True
    except Exception as e:
        print(f"跳过 {file_path}: {e}")
    return False

def update_all_references():
    """更新所有配置文件中的引用"""
    updated = 0
    extensions = ['.yaml', '.yml', '.md', '.py', '.json']
    
    for ext in extensions:
        for file_path in PROJECT_ROOT.rglob(f'*{ext}'):
            if '.git' in str(file_path) or '__pycache__' in str(file_path):
                continue
            if update_file_references(file_path):
                print(f"更新: {file_path.relative_to(PROJECT_ROOT)}")
                updated += 1
    return updated

if __name__ == "__main__":
    print("="*60)
    print("Step 1: 重命名目录")
    print("="*60)
    renamed = rename_directories()
    print(f"\n完成: 重命名了 {renamed} 个目录")
    
    print("\n" + "="*60)
    print("Step 2: 更新文件引用")
    print("="*60)
    updated = update_all_references()
    print(f"\n完成: 更新了 {updated} 个文件")
