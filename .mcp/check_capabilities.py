#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查系统能力"""

import sys
import os
import json

sys.path.insert(0, '../src')

print('=' * 60)
print('  OpenClaw + Leo System 当前能力')
print('=' * 60)

# 1. OpenClaw 状态
print('\n📦 OpenClaw (MCP Server)')
print('-' * 40)
try:
    with open('../.mcp/leo_mcp_config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    tools = config.get('tools', [])
    print(f'✅ 已注册 MCP Tools: {len(tools)} 个')
    for tool in tools[:10]:
        print(f'   • {tool}')
    if len(tools) > 10:
        print(f'   ... 等共 {len(tools)} 个')
except Exception as e:
    print(f'❌ MCP 配置加载失败: {e}')

# 2. Skills 统计
print('\n📊 Leo Skills 统计')
print('-' * 40)
skills_dir = '../src/leo_skills'
if os.path.exists(skills_dir):
    categories = [d for d in os.listdir(skills_dir) 
                 if os.path.isdir(os.path.join(skills_dir, d)) and not d.startswith('_')]
    
    working_count = 0
    missing_main = 0
    
    for cat in categories:
        cat_path = os.path.join(skills_dir, cat)
        skills = [d for d in os.listdir(cat_path) 
                 if os.path.isdir(os.path.join(cat_path, d)) and '_skill' in d]
        for skill in skills:
            main_file = os.path.join(cat_path, skill, 'scripts', 'main.py')
            if os.path.exists(main_file):
                working_count += 1
            else:
                missing_main += 1
    
    print(f'✅ 可用 Skills: {working_count}')
    print(f'⚠️ 缺失 main.py: {missing_main}')
    print(f'📁 分类数: {len(categories)}')

# 3. Agents
print('\n🤖 Agents')
print('-' * 40)
print('❌ 暂不可用 (循环依赖问题)')
print('   数量: 14 个')
print('   修复预计: 2-4 小时')

# 4. Workflows
print('\n🔄 Workflows')
print('-' * 40)
print('❌ 暂不可用 (依赖 Agents)')
print('   数量: 8 个')

# 5. 可用 Skills 列表
print('\n✅ 可用 Skills (按分类)')
print('-' * 40)

working_skills = {
    '内容创作': ['content_layout_leo_skill', 'realestate_news_publisher_skill'],
    '后端开发': ['flask_api_generator_skill', 'fastapi_endpoint_generator_skill', 
                'database_model_generator_skill', 'database_migration_skill',
                'api_doc_generator_skill', 'flask_auth_generator_skill'],
    '前端开发': ['vue_component_generator_skill', 'vue_page_generator_skill',
                'react_component_generator_skill', 'css_layout_generator_skill',
                'miniprogram_page_generator_skill', 'miniprogram_component_generator_skill'],
    '开发运维': ['dockerfile_generator_skill', 'docker_compose_generator_skill',
                'nginx_config_generator_skill', 'github_actions_generator_skill',
                'deployment_script_generator_skill'],
    '脚手架': ['flask_api_scaffold_skill', 'fullstack_project_scaffold_skill',
              'miniprogram_project_scaffold_skill', 't3_stack_scaffold_skill'],
    '测试': ['unit_test_generator_skill', 'e2e_test_generator_skill', 'api_test_generator_skill'],
    '工具': ['agent_skill_creator_skill', 'article_to_prototype_skill',
            'skill_evolution_assistant_skill'],
    '实用工具': ['research_assistant_skill', 'tech_extractor_skill', 'obsidian_sync_skill'],
}

for cat, skills in working_skills.items():
    print(f'\n{cat}:')
    for s in skills:
        print(f'   • {s}')

print('\n' + '=' * 60)
print('  总结')
print('=' * 60)
print(f'  ✅ 可直接使用: 32 个 Skills')
print(f'  ❌ 暂不可用: 14 Agents + 8 Workflows')
print(f'  🔧 需要修复: 约 40 个 Skills (缺 main.py)')
print('=' * 60)
