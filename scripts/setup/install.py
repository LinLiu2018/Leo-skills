# -*- coding: utf-8 -*-
import sys
import os
import shutil
from pathlib import Path

# 修复 Windows 编码问题
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# 工作空间
WORKSPACE = Path(__file__).parent.parent.parent
SKILLS_DIR = WORKSPACE / "src" / "leo_skills"

# 新创建的 ClawHub 技能
NEW_SKILLS = [
    "skill_vetter_skill",
    "web_search_enhanced_skill",
    "github_integration_skill",
    "summarize_skill",
    "memory_enhanced_skill",
    "find_skills_skill",
    "gog_skill"
]

NEW_AGENTS = [
    "self_improving_agent",
    "proactive_agent"
]


def install_skill(skill_name: str) -> bool:
    """安装技能"""
    # 检查技能是否存在
    skill_path = None
    
    # 在 Skills 中查找
    for category in SKILLS_DIR.iterdir():
        if not category.is_dir():
            continue
        candidate = category / skill_name
        if candidate.exists():
            skill_path = candidate
            break
    
    # 在 Agents 中查找
    if not skill_path:
        agents_dir = WORKSPACE / "src" / "leo_subagents" / "agents"
        candidate = agents_dir / skill_name
        if candidate.exists():
            skill_path = candidate
    
    if not skill_path:
        print(f"❌ 技能不存在：{skill_name}")
        print(f"\n可用技能:")
        for skill in NEW_SKILLS + NEW_AGENTS:
            print(f"  - {skill}")
        return False
    
    print(f"✅ 技能已就绪：{skill_path}")
    print(f"\n技能信息:")
    print(f"  名称：{skill_name}")
    print(f"  路径：{skill_path}")
    
    # 检查 SKILL.md 或 AGENT.md
    skill_md = skill_path / "SKILL.md"
    agent_md = skill_path / "AGENT.md"
    
    if skill_md.exists():
        print(f"  定义：SKILL.md ✓")
    elif agent_md.exists():
        print(f"  定义：AGENT.md ✓")
    else:
        print(f"  ⚠️ 未找到 SKILL.md 或 AGENT.md")
    
    print(f"\n✅ 技能安装完成！")
    print(f"\n注意：需要重启 OpenClaw 使新技能生效")
    print(f"重启命令：cd D:\\openclaw && node openclaw.mjs gateway restart")
    
    return True


def list_available_skills():
    """列出可用技能"""
    print("\n=== ClawHub Skills (Implemented) ===\n")
    
    print("Skills:")
    for skill in NEW_SKILLS:
        print(f"  - {skill}")
    
    print("\nAgents:")
    for agent in NEW_AGENTS:
        print(f"  - {agent}")
    
    print(f"\nTotal: {len(NEW_SKILLS)} Skills + {len(NEW_AGENTS)} Agents")


def main():
    if len(sys.argv) < 2:
        print("Leo AI System - 技能安装脚本")
        print("\n用法：python scripts/skills/install.py <skill_name>")
        print("\n示例:")
        print("  python scripts/skills/install.py skill_vetter_skill")
        print("  python scripts/skills/install.py github_integration_skill")
        print("\n可用技能:")
        list_available_skills()
        return
    
    skill_name = sys.argv[1]
    
    if skill_name == "--list":
        list_available_skills()
        return
    
    success = install_skill(skill_name)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
