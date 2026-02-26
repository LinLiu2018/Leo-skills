#!/usr/bin/env python3
"""
Leo Skills 标准化转换脚本

将 Leo Skills 转换为 OpenClaw 标准格式
"""
import json
import os
from pathlib import Path

SKILLS_DIR = Path("src/leo_skills")

# 标准 SKILL.md 模板
SKILL_TEMPLATE = '''---
name: {name}
version: "1.0.0"
description: |
  {description}
category: {category}
author: Leo AI System
user-invocable: true
priority: {priority}
activation_keywords:
  - {name}
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
---

# {display_name}

## 概述

{description}

## 使用方法

```bash
python scripts/main.py --action execute
```

## 与其他组件集成

此技能可与 Leo System 的其他组件配合使用。
'''

# Category 映射
CATEGORY_MAP = {
    'content_creation': 'content',
    'utilities': 'utilities',
    'tools': 'tools',
    'development': 'development',
    'devops': 'devops',
    'testing': 'testing',
    'security': 'security',
    'collaboration': 'collaboration',
    'core': 'core',
    'frontend': 'development',
    'backend': 'development',
    'scaffold': 'development',
    'automation': 'utilities',
    'intelligence': 'utilities',
    'business': 'utilities',
    'video_editing': 'utilities',
    'prompt_engineering': 'development'
}

# 优先级映射
PRIORITY_MAP = {
    'core': 1,
    'content': 2,
    'utilities': 3,
    'tools': 4,
    'development': 5,
    'devops': 6,
    'testing': 7,
    'security': 8
}


def get_category(skill_path: Path) -> str:
    """检测 Skills 类别"""
    for parent in skill_path.parts:
        if parent in CATEGORY_MAP:
            return CATEGORY_MAP[parent]
    return 'utilities'


def get_priority(category: str) -> int:
    """获取优先级"""
    return PRIORITY_MAP.get(category, 5)


def migrate_skill(skill_path: Path) -> bool:
    """迁移单个 Skill"""
    name = skill_path.name
    display_name = name.replace('_', ' ').title()
    category = get_category(skill_path)
    priority = get_priority(category)

    # 读取现有的 SKILL.md（如果存在）
    skill_md = skill_path / 'SKILL.md'
    existing_content = ""
    if skill_md.exists():
        with open(skill_md, 'r', encoding='utf-8') as f:
            existing_content = f.read()

    # 检查是否需要更新
    if existing_content and "OpenClaw" in existing_content:
        print(f"  跳过: {name} (已是 OpenClaw 格式)")
        return False

    # 生成新内容
    content = SKILL_TEMPLATE.format(
        name=name,
        display_name=display_name,
        description=f'{display_name} skill for Leo AI System',
        category=category,
        priority=priority
    )

    # 写入文件
    with open(skill_md, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"  已更新: {name} ({category})")
    return True


def main():
    """主函数"""
    print("=" * 60)
    print("Leo Skills 标准化工具")
    print("=" * 60)
    print(f"Skills 目录: {SKILLS_DIR}")
    print()

    if not SKILLS_DIR.exists():
        print(f"错误: 目录不存在: {SKILLS_DIR}")
        return

    updated = 0
    skipped = 0

    for skill_path in SKILLS_DIR.iterdir():
        if skill_path.is_dir() and (skill_path / 'scripts').exists():
            print(f"处理: {skill_path.name}")
            if migrate_skill(skill_path):
                updated += 1
            else:
                skipped += 1

    print()
    print(f"完成! 更新: {updated}, 跳过: {skipped}")
    print()
    print("提示:")
    print("  - 已标准化的 Skills 可被 OpenClaw Skills Loader 直接加载")
    print("  - 核心 Skills (core/) 自动获得最高优先级")


if __name__ == "__main__":
    main()
