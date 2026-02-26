#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SKILL.md 标准化脚本
==================
统一所有 SKILL.md 文件格式，添加 YAML frontmatter
"""

import re
import yaml
from pathlib import Path
from typing import Dict, List, Optional
import argparse


# 标准 SKILL.md 模板
STANDARD_TEMPLATE = """---
name: {name}
version: {version}
category: {category}
description: {description}
triggers:{triggers}
inputs:{inputs}
outputs:{outputs}
author: {author}
---

# {title}

{description}

## 功能概述

### 核心能力

{capabilities}

## 激活词

使用以下关键词可自动触发此技能：

{activation_words}

## 使用方法

### 命令行使用

```bash
{cli_usage}
```

### Python 代码调用

```python
{python_usage}
```

## 版本信息

- **版本:** {version}
- **作者:** {author}
- **分类:** {category}
"""


def extract_info_from_skill_md(content: str) -> Dict:
    """从现有 SKILL.md 提取信息"""
    info = {
        "name": "",
        "version": "1.0.0",
        "category": "general",
        "description": "",
        "triggers": [],
        "title": "",
        "capabilities": "",
        "activation_words": "",
        "cli_usage": "# 见具体技能文档",
        "python_usage": "# 见具体技能文档",
        "author": "Leo Liu"
    }

    # 提取标题
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if title_match:
        info["title"] = title_match.group(1)
        # 从标题提取名称
        info["name"] = title_match.group(1).lower().replace(' ', '_').replace('-', '_')

    # 提取版本
    version_match = re.search(r'\*\*Version:\*\*\s*(.+)', content)
    if version_match:
        info["version"] = version_match.group(1).strip()

    # 提取描述（第一段）
    desc_match = re.search(r'^#\s+.+\n\n(.+?)(?:\n\n|\n##)', content, re.DOTALL)
    if desc_match:
        info["description"] = desc_match.group(1).strip()

    # 提取激活词
    trigger_section = re.search(r'##\s*激活词\s*\n\n(.+?)(?:\n\n##|\Z)', content, re.DOTALL)
    if trigger_section:
        triggers_text = trigger_section.group(1)
        triggers = re.findall(r'-\s*"(.+?)"', triggers_text)
        info["triggers"] = triggers
        info["activation_words"] = '\n'.join([f'- "{t}"' for t in triggers])

    # 提取核心能力
    capabilities_section = re.search(r'###\s*核心能力\s*\n\n(.+?)(?:\n\n##|\n###|\Z)', content, re.DOTALL)
    if capabilities_section:
        info["capabilities"] = capabilities_section.group(1).strip()

    return info


def standardize_skill_md(skill_path: Path) -> bool:
    """
    标准化单个 SKILL.md 文件

    Args:
        skill_path: SKILL.md 文件路径

    Returns:
        是否成功
    """
    try:
        with open(skill_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 如果已经有 YAML frontmatter，跳过
        if content.startswith('---'):
            print(f"  ⏭️  {skill_path} 已有 YAML frontmatter，跳过")
            return True

        # 提取信息
        info = extract_info_from_skill_md(content)

        # 从路径推断分类
        parts = skill_path.parts
        if 'leo_skills' in parts:
            idx = parts.index('leo_skills')
            if idx + 1 < len(parts):
                info["category"] = parts[idx + 1]

        # 构建 triggers YAML
        triggers_yaml = ''
        for trigger in info["triggers"]:
            triggers_yaml += f'\n  - "{trigger}"'
        if not triggers_yaml:
            triggers_yaml = '\n  - "触发词"'

        # 构建标准格式
        standardized = STANDARD_TEMPLATE.format(
            name=info["name"] or skill_path.parent.name,
            version=info["version"],
            category=info["category"],
            description=info["description"][:100] + '...' if len(info["description"]) > 100 else info["description"],
            triggers=triggers_yaml,
            inputs='\n  - name: input\n    type: string\n    required: true',
            outputs='\n  - name: output\n    type: string',
            author=info["author"],
            title=info["title"] or skill_path.parent.name,
            capabilities=info["capabilities"] or "| 功能 | 说明 |\n|------|------|",
            activation_words=info["activation_words"] or '- "激活词"',
            cli_usage=info["cli_usage"],
            python_usage=info["python_usage"]
        )

        # 保存原文件备份
        backup_path = skill_path.with_suffix('.md.backup')
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)

        # 写入标准化内容
        with open(skill_path, 'w', encoding='utf-8') as f:
            f.write(standardized)

        print(f"  ✅ {skill_path} 已标准化")
        return True

    except Exception as e:
        print(f"  ❌ {skill_path} 处理失败: {e}")
        return False


def standardize_all_skills(base_path: str = "src/leo_skills") -> Dict:
    """
    标准化所有 SKILL.md 文件

    Args:
        base_path: 技能根目录

    Returns:
        统计信息
    """
    base = Path(base_path)
    if not base.exists():
        print(f"❌ 目录不存在: {base_path}")
        return {"total": 0, "success": 0, "failed": 0}

    stats = {"total": 0, "success": 0, "failed": 0}

    print(f"🔍 扫描目录: {base_path}")
    print("=" * 60)

    for skill_md in base.rglob("SKILL.md"):
        # 跳过 references/examples 中的 SKILL.md
        if 'references' in skill_md.parts or 'examples' in skill_md.parts:
            continue

        stats["total"] += 1
        if standardize_skill_md(skill_md):
            stats["success"] += 1
        else:
            stats["failed"] += 1

    print("=" * 60)
    print(f"📊 统计: 总计 {stats['total']}, 成功 {stats['success']}, 失败 {stats['failed']}")

    return stats


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="标准化 SKILL.md 文件")
    parser.add_argument(
        "--path",
        default="src/leo_skills",
        help="技能根目录 (默认: src/leo_skills)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="仅预览，不实际修改文件"
    )

    args = parser.parse_args()

    if args.dry_run:
        print("🔍 预览模式（不会修改文件）")

    standardize_all_skills(args.path)


if __name__ == "__main__":
    main()
