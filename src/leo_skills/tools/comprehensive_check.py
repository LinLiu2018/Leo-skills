# -*- coding: utf-8 -*-
"""
Comprehensive System Check
全面系统检查脚本
"""

from pathlib import Path
import re

# 1. 检查 Python 语法
print('='*80)
print('                    LEO AI SYSTEM - COMPREHENSIVE CHECK')
print('='*80)

print('\n[1/6] Checking Python syntax...')
errors = []
for py_file in Path('leo_skills').rglob('*.py'):
    if '__pycache__' in str(py_file) or '.git' in str(py_file):
        continue
    try:
        with open(py_file, 'r', encoding='utf-8') as f:
            compile(f.read(), py_file, 'exec')
    except SyntaxError as e:
        errors.append(f'{py_file}: {e}')

if errors:
    print(f'  ERRORS: {len(errors)}')
    for e in errors[:5]:
        print(f'    - {e}')
else:
    print('  OK: No syntax errors')

# 2. 检查 agents 配置
print('\n[2/6] Checking agents configuration...')
agents_path = Path('leo_subagents/config/agents.yaml')
if agents_path.exists():
    content = agents_path.read_text(encoding='utf-8')
    agents = re.findall(r'^  (\w+-agent):', content, re.MULTILINE)
    agent_dirs = [d.name for d in (Path('leo_subagents/agents')).iterdir() if d.is_dir() and d.name.endswith('_agent')]

    configured = len(agents)
    existing = len(agent_dirs)
    print(f'  Configured agents: {configured}')
    print(f'  Existing directories: {existing}')

    # 检查每个 agent 是否有 __init__.py
    missing_init = []
    for agent_dir in agent_dirs:
        init_file = Path('leo_subagents/agents') / agent_dir / '__init__.py'
        if not init_file.exists():
            missing_init.append(agent_dir)

    if missing_init:
        print(f'  WARN: {len(missing_init)} agents missing __init__.py')
        for m in missing_init[:3]:
            print(f'    - {m}')
    else:
        print('  OK: All agents have __init__.py')

# 3. 检查 skills 导入
print('\n[3/6] Checking skills imports...')
skills_root = Path('leo_skills')
import_warnings = []

for category in skills_root.iterdir():
    if category.is_dir() and not category.name.startswith('.'):
        for skill_dir in category.iterdir():
            if skill_dir.is_dir() and not skill_dir.name.startswith('.'):
                init_file = skill_dir / '__init__.py'
                main_file = skill_dir / f'{skill_dir.name}.py'

                # 检查 init 文件是否正确引用主模块
                if init_file.exists() and main_file.exists():
                    init_content = init_file.read_text(encoding='utf-8')
                    skill_name = skill_dir.name
                    if skill_name in init_content or skill_name.replace('_skill', '') in init_content:
                        pass
                    else:
                        import_warnings.append(str(skill_dir))

if import_warnings:
    print(f'  WARN: {len(import_warnings)} skills with potential import issues')
    for w in import_warnings[:3]:
        print(f'    - {w}')
else:
    print('  OK: All imports look correct')

# 4. 检查孤立文件
print('\n[4/6] Checking for orphan files...')
orphan = []
for py_file in Path('leo_skills').rglob('*.py'):
    if '__pycache__' in str(py_file) or '.git' in str(py_file):
        continue
    content = open(py_file, 'r', encoding='utf-8').read()
    if 'def main' in content or 'class ' in content:
        if not (py_file.parent / '__init__.py').exists():
            orphan.append(str(py_file.relative_to(Path('leo_skills').parent.parent)))

if orphan:
    print(f'  WARN: {len(orphan)} files without __init__.py')
    for o in orphan[:3]:
        print(f'    - {o}')
else:
    print('  OK: No orphan files')

# 5. 检查重复文件
print('\n[5/6] Checking for duplicate files...')
file_map = {}
duplicates = []
for py_file in Path('leo_skills').rglob('*.py'):
    if '__pycache__' in str(py_file) or '.git' in str(py_file):
        continue
    name = py_file.name
    if name in file_map:
        duplicates.append((file_map[name], str(py_file)))
    else:
        file_map[name] = str(py_file)

if duplicates:
    print(f'  WARN: {len(duplicates)} duplicate names')
    for d in duplicates[:3]:
        name = d[0].split('/')[-1]
        print(f'    - {name}')
else:
    print('  OK: No duplicate file names')

# 6. 统计
print('\n[6/6] Statistics...')
py_count = len(list(Path('leo_skills').rglob('*.py')))
md_count = len(list(Path('leo_skills').rglob('*.md')))
yaml_count = len(list(Path('leo_skills').rglob('*.yaml')) + list(Path('leo_skills').rglob('*.yml')))
print(f'  Python files: {py_count}')
print(f'  Markdown files: {md_count}')
print(f'  YAML files: {yaml_count}')

# 计算健康技能数
total_skills = 0
healthy_skills = 0
for category in skills_root.iterdir():
    if category.is_dir() and not category.name.startswith('.'):
        for skill_dir in category.iterdir():
            if skill_dir.is_dir() and not skill_dir.name.startswith('.'):
                total_skills += 1
                has_init = (skill_dir / '__init__.py').exists()
                has_main = any(f.suffix == '.py' and f.name not in ['__init__.py'] for f in skill_dir.glob('*.py'))
                if has_init and has_main:
                    healthy_skills += 1

print(f'  Total skills: {total_skills}')
print(f'  Healthy skills: {healthy_skills}')

print('\n' + '='*80)
print('                    CHECK COMPLETE')
print('='*80)
