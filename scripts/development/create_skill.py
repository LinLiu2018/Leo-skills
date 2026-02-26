#!/usr/bin/env python3
"""
创建新技能模板生成器
用法: python scripts/create_skill.py --name my_skill --category tools
"""

import argparse
import os
import sys
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent
SKILLS_DIR = PROJECT_ROOT / "src" / "leo_skills"


def create_skill(name: str, category: str):
    """创建新技能目录和文件"""

    # 确保命名规范
    if not name.endswith("_skill"):
        name = f"{name}_skill"

    skill_dir = SKILLS_DIR / category / name

    if skill_dir.exists():
        print(f"❌ 错误: 技能目录已存在: {skill_dir}")
        sys.exit(1)

    # 创建目录
    skill_dir.mkdir(parents=True)
    (skill_dir / "config").mkdir()

    # 创建 SKILL.md
    skill_md_content = f'''---
name: {name.replace("_skill", "")}
version: "1.0.0"
description: |
  一句话描述技能功能
category: {category}
author: Leo AI System
user-invocable: true
priority: 1
activation_keywords:
  - 关键词1
  - 关键词2
---

# {name}

## 功能描述

描述这个技能是做什么的。

## 使用场景

- 场景1
- 场景2

## 使用方法

```
使用示例
```

## 依赖

- 依赖1
- 依赖2

## 示例

### 示例1

```python
# 代码示例
```

## 注意事项

- 注意事项1
- 注意事项2
'''

    (skill_dir / "SKILL.md").write_text(skill_md_content, encoding="utf-8")

    # 创建 __init__.py
    class_name = "".join(word.capitalize() for word in name.split("_"))
    init_content = f'''# -*- coding: utf-8 -*-
"""
{name} - 技能描述

详情请查看 SKILL.md
"""

from .{name} import {class_name}

__all__ = ["{class_name}"]
'''

    (skill_dir / "__init__.py").write_text(init_content, encoding="utf-8")

    # 创建 {skill_name}.py
    skill_py_content = f'''# -*- coding: utf-8 -*-
"""
{name} - 技能实现

详情请查看 SKILL.md
"""

from typing import Dict, Any, Optional


class {class_name}:
    """
    {class_name}

    技能实现
    """

    def __init__(self):
        self.name = "{name}"
        self.version = "1.0.0"
        self.description = "技能描述"

    def execute(self, **kwargs) -> Dict[str, Any]:
        """执行技能"""
        return {{"status": "completed", "skill": self.name}}


def main():
    """入口函数"""
    return {class_name}()


if __name__ == "__main__":
    skill = main()
'''

    (skill_dir / f"{name}.py").write_text(skill_py_content, encoding="utf-8")

    # 创建 config/config.yaml
    config_content = f'''skill:
  name: {name}
  version: 1.0.0
  category: {category}
  description: "技能描述"
  author: Leo AI System

execution:
  timeout: 300
  retry: 1

evolution:
  enabled: true
  learn_on_failure: true
  max_tips: 50
'''

    (skill_dir / "config" / "config.yaml").write_text(config_content, encoding="utf-8")

    # 创建 evolution.json
    today = datetime.now().strftime("%Y-%m-%d")
    evolution_content = f'''{{
  "version": "1.0.0",
  "evolution_history": [
    {{
      "version": "1.0.0",
      "date": "{today}",
      "changes": "Initial creation with standard skill structure"
    }}
  ],
  "learned_tips": [],
  "learned_errors": []
}}'''

    (skill_dir / "evolution.json").write_text(evolution_content, encoding="utf-8")

    print(f"✅ 技能创建成功: {name}")
    print(f"   路径: {skill_dir.relative_to(PROJECT_ROOT)}")
    print(f"   文件:")
    print(f"     - SKILL.md")
    print(f"     - __init__.py")
    print(f"     - {name}.py")
    print(f"     - config/config.yaml")
    print(f"     - evolution.json")
    print(f"\n📝 下一步:")
    print(f"   1. 编辑 SKILL.md 完善技能描述")
    print(f"   2. 编辑 {name}.py 实现技能逻辑")
    print(f"   3. 编辑 config/config.yaml 配置参数")


def main():
    parser = argparse.ArgumentParser(description="创建新技能模板")
    parser.add_argument("--name", "-n", required=True, help="技能名称 (例如: web_search)")
    parser.add_argument("--category", "-c", required=True,
                       help="技能类别 (例如: tools, core, utilities)")

    args = parser.parse_args()

    create_skill(args.name, args.category)


if __name__ == "__main__":
    main()
