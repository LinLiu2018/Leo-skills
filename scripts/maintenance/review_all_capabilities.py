# -*- coding: utf-8 -*-
"""
OpenClaw 完整能力审查脚本
审查所有 Skills、Agents、Workflows 的实现情况
"""

import os
from pathlib import Path
from datetime import datetime

WORKSPACE = Path(__file__).parent.parent.parent

print("=" * 80)
print("OpenClaw 完整能力审查报告")
print("=" * 80)
print(f"审查时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"工作空间：{WORKSPACE}")
print()

# ========== 1. Skills 审查 ==========
print("=" * 80)
print("第一部分：Skills 技能审查")
print("=" * 80)
print()

skills_dir = WORKSPACE / "src" / "leo_skills"
skill_categories = {}
total_skills = 0
skills_with_issues = []

if skills_dir.exists():
    for category in skills_dir.iterdir():
        if not category.is_dir() or category.name.startswith('_'):
            continue
        
        category_skills = []
        for skill_dir in category.iterdir():
            if not skill_dir.is_dir() or skill_dir.name.startswith('_'):
                continue
            
            skill_name = skill_dir.name
            has_skill_md = (skill_dir / "SKILL.md").exists()
            has_init = (skill_dir / "__init__.py").exists()
            has_main = len(list(skill_dir.glob("*.py"))) > 0
            
            status = "✅" if (has_skill_md and has_init and has_main) else "⚠️"
            
            if not (has_skill_md and has_init and has_main):
                skills_with_issues.append({
                    "name": skill_name,
                    "category": category.name,
                    "issues": [] if has_skill_md else ["SKILL.md"] if not has_init else ["__init__.py"] if not has_main else ["main.py"]
                })
            
            category_skills.append(f"  {status} {skill_name}")
            total_skills += 1
        
        if category_skills:
            skill_categories[category.name] = category_skills

print(f"技能总数：{total_skills}")
print()

for category, skills in sorted(skill_categories.items()):
    print(f"### {category} ({len(skills)} 个)")
    for skill in skills[:10]:  # 显示前 10 个
        print(skill)
    if len(skills) > 10:
        print(f"  ... 还有 {len(skills) - 10} 个")
    print()

if skills_with_issues:
    print("⚠️  存在问题的技能:")
    for skill in skills_with_issues:
        print(f"  - {skill['category']}/{skill['name']}: 缺少 {', '.join(skill['issues'])}")
    print()

# ========== 2. Agents 审查 ==========
print("=" * 80)
print("第二部分：Agents 子代理审查")
print("=" * 80)
print()

agents_dir = WORKSPACE / "src" / "leo_subagents" / "agents"
total_agents = 0
agents_with_issues = []
agent_list = []

if agents_dir.exists():
    for agent_dir in agents_dir.iterdir():
        if not agent_dir.is_dir() or agent_dir.name.startswith('_'):
            continue
        
        agent_name = agent_dir.name
        has_agent_md = (agent_dir / "AGENT.md").exists()
        has_init = (agent_dir / "__init__.py").exists()
        has_main = len(list(agent_dir.glob("*.py"))) > 0
        has_evolution = (agent_dir / "evolution.json").exists()
        
        status = "✅" if (has_agent_md and has_init and has_main) else "⚠️"
        
        if not (has_agent_md and has_init and has_main):
            issues = []
            if not has_agent_md: issues.append("AGENT.md")
            if not has_init: issues.append("__init__.py")
            if not has_main: issues.append("main.py")
            if not has_evolution: issues.append("evolution.json")
            agents_with_issues.append({"name": agent_name, "issues": issues})
        
        agent_list.append((status, agent_name))
        total_agents += 1

print(f"子代理总数：{total_agents}")
print()

for status, name in sorted(agent_list, key=lambda x: x[1]):
    print(f"  {status} {name}")

print()

if agents_with_issues:
    print("⚠️  存在问题的子代理:")
    for agent in agents_with_issues:
        print(f"  - {agent['name']}: 缺少 {', '.join(agent['issues'])}")
    print()

# ========== 3. Workflows 审查 ==========
print("=" * 80)
print("第三部分：Workflows 工作流审查")
print("=" * 80)
print()

workflows_dir = WORKSPACE / "src" / "leo_workflows" / "definitions"
total_workflows = 0
workflow_list = []

if workflows_dir.exists():
    for wf_file in workflows_dir.glob("*.yaml"):
        workflow_name = wf_file.stem
        file_size = wf_file.stat().st_size
        
        # 读取 YAML 内容检查有效性
        try:
            with open(wf_file, 'r', encoding='utf-8') as f:
                content = f.read()
                has_name = 'name:' in content
                has_steps = 'steps:' in content or 'tasks:' in content
                status = "✅" if (has_name and has_steps) else "⚠️"
        except:
            status = "❌"
        
        workflow_list.append((status, workflow_name, file_size))
        total_workflows += 1

print(f"工作流总数：{total_workflows}")
print()

for status, name, size in sorted(workflow_list, key=lambda x: x[1]):
    print(f"  {status} {name} ({size/1024:.1f} KB)")

print()

# ========== 4. 新增 ClawHub 技能审查 ==========
print("=" * 80)
print("第四部分：ClawHub 热门技能实现审查")
print("=" * 80)
print()

clawhub_skills = [
    ("skill_vetter_skill", "tools", "技能安全扫描器"),
    ("web_search_enhanced_skill", "utilities", "增强版网络搜索"),
    ("github_integration_skill", "tools", "GitHub 集成"),
    ("summarize_skill", "utilities", "内容总结"),
    ("memory_enhanced_skill", "core", "增强记忆"),
    ("find_skills_skill", "tools", "技能发现"),
    ("gog_skill", "tools", "Google Workspace 集成"),
]

clawhub_agents = [
    ("self_improving_agent", "自我迭代代理"),
    ("proactive_agent", "主动规划代理"),
]

print("### ClawHub Skills (7 个)")
for skill_name, category, desc in clawhub_skills:
    skill_path = skills_dir / category / skill_name
    exists = skill_path.exists()
    has_skill_md = (skill_path / "SKILL.md").exists() if exists else False
    status = "✅" if (exists and has_skill_md) else "❌"
    print(f"  {status} {skill_name} - {desc}")

print()
print("### ClawHub Agents (2 个)")
for agent_name, desc in clawhub_agents:
    agent_path = agents_dir / agent_name
    exists = agent_path.exists()
    has_agent_md = (agent_path / "AGENT.md").exists() if exists else False
    status = "✅" if (exists and has_agent_md) else "❌"
    print(f"  {status} {agent_name} - {desc}")

print()

# ========== 5. 总结 ==========
print("=" * 80)
print("审查总结")
print("=" * 80)
print()

print("能力统计:")
print(f"  - Skills: {total_skills} 个")
print(f"  - Agents: {total_agents} 个")
print(f"  - Workflows: {total_workflows} 个")
print(f"  - 总计：{total_skills + total_agents + total_workflows} 个能力单元")
print()

print("实现状态:")
print(f"  - 完全实现：{total_skills + total_agents + total_workflows - len(skills_with_issues) - len(agents_with_issues)}")
print(f"  - 存在问题：{len(skills_with_issues) + len(agents_with_issues)}")
print(f"  - 完成率：{((total_skills + total_agents + total_workflows - len(skills_with_issues) - len(agents_with_issues)) / (total_skills + total_agents + total_workflows) * 100):.1f}%")
print()

if skills_with_issues or agents_with_issues:
    print("需要修复:")
    for skill in skills_with_issues[:5]:
        print(f"  - Skill: {skill['category']}/{skill['name']}")
    for agent in agents_with_issues[:5]:
        print(f"  - Agent: {agent['name']}")
    print()

print("=" * 80)
print("审查完成")
print("=" * 80)
