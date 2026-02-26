#!/usr/bin/env python3
"""
创建新代理模板生成器
用法: python scripts/create_agent.py --name my_agent
"""

import argparse
import os
import sys
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent
AGENTS_DIR = PROJECT_ROOT / "src" / "leo_subagents" / "agents"


def create_agent(name: str):
    """创建新代理目录和文件"""

    # 确保命名规范
    if not name.endswith("_agent"):
        name = f"{name}_agent"

    agent_dir = AGENTS_DIR / name

    if agent_dir.exists():
        print(f"❌ 错误: 代理目录已存在: {agent_dir}")
        sys.exit(1)

    # 创建目录
    agent_dir.mkdir(parents=True)

    # 创建 AGENT.md
    agent_md_content = f'''# {name.replace("_", " ").title()}

描述代理的职责和功能。

## 职责

- 职责1
- 职责2

## 技能

- skill1: 技能描述
- skill2: 技能描述

## 激活关键词

- "关键词1"
- "关键词2"

## 输出物

- 输出物1
- 输出物2

## 配置

```yaml
name: {name.replace("_", "-")}
type: executor
priority: 1
enabled: true
skills:
  - skill1
  - skill2
metadata:
  description: "代理描述"
  activation_keywords:
    - "关键词1"
    - "关键词2"
```

## 版本

- 版本: 1.0.0
- 作者: Leo AI System
'''

    (agent_dir / "AGENT.md").write_text(agent_md_content, encoding="utf-8")

    # 创建 __init__.py
    class_name = "".join(word.capitalize() for word in name.split("_"))
    init_content = f'''# -*- coding: utf-8 -*-
"""
{name} - 代理描述

详情请查看 AGENT.md
"""

from .{name} import {class_name}

__all__ = ["{class_name}"]
'''

    (agent_dir / "__init__.py").write_text(init_content, encoding="utf-8")

    # 创建 {agent_name}.py
    agent_py_content = f'''# -*- coding: utf-8 -*-
"""
{name} - 代理实现

详情请查看 AGENT.md
"""

from typing import Dict, Any, Optional


class {class_name}:
    """
    {class_name}

    代理实现
    """

    def __init__(self):
        self.name = "{name}"
        self.version = "1.0.0"
        self.description = "代理描述"

    def execute(self, task: str, **kwargs) -> Dict[str, Any]:
        """执行代理任务"""
        return {{"status": "completed", "agent": self.name, "task": task}}


def main():
    """入口函数"""
    return {class_name}()


if __name__ == "__main__":
    agent = main()
'''

    (agent_dir / f"{name}.py").write_text(agent_py_content, encoding="utf-8")

    # 创建 evolution.json
    today = datetime.now().strftime("%Y-%m-%d")
    evolution_content = f'''{{
  "version": "1.0.0",
  "evolution_history": [
    {{
      "version": "1.0.0",
      "date": "{today}",
      "changes": "Initial creation with standard agent structure"
    }}
  ],
  "learned_tips": [],
  "learned_errors": []
}}'''

    (agent_dir / "evolution.json").write_text(evolution_content, encoding="utf-8")

    print(f"✅ 代理创建成功: {name}")
    print(f"   路径: {agent_dir.relative_to(PROJECT_ROOT)}")
    print(f"   文件:")
    print(f"     - AGENT.md")
    print(f"     - __init__.py")
    print(f"     - {name}.py")
    print(f"     - evolution.json")
    print(f"\n📝 下一步:")
    print(f"   1. 编辑 AGENT.md 完善代理描述")
    print(f"   2. 编辑 {name}.py 实现代理逻辑")


def main():
    parser = argparse.ArgumentParser(description="创建新代理模板")
    parser.add_argument("--name", "-n", required=True, help="代理名称 (例如: research)")

    args = parser.parse_args()

    create_agent(args.name)


if __name__ == "__main__":
    main()
