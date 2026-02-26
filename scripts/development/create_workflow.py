#!/usr/bin/env python3
"""
创建新工作流模板生成器
用法: python scripts/create_workflow.py --name my_pipeline
"""

import argparse
import os
import sys
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent
WORKFLOWS_DIR = PROJECT_ROOT / "src" / "leo_workflows" / "workflows"


def create_workflow(name: str):
    """创建新工作流目录和文件"""

    # 确保命名规范
    if not name.endswith("_pipeline"):
        name = f"{name}_pipeline"

    workflow_dir = WORKFLOWS_DIR / name

    if workflow_dir.exists():
        print(f"❌ 错误: 工作流目录已存在: {workflow_dir}")
        sys.exit(1)

    # 创建目录
    workflow_dir.mkdir(parents=True)

    # 创建 workflow.yaml
    workflow_yaml_content = f'''name: {name.replace("_", "-")}
description: |
  工作流描述

version: "1.0.0"
author: Leo AI System

steps:
  - name: step1
    agent: agent_name
    description: "第一步描述"
    input:
      param1: value1

  - name: step2
    agent: agent_name
    description: "第二步描述"
    depends_on:
      - step1

config:
  timeout: 300
  retry: 1
  parallel: false
'''

    (workflow_dir / "workflow.yaml").write_text(workflow_yaml_content, encoding="utf-8")

    # 创建 __init__.py
    init_content = f'''# -*- coding: utf-8 -*-
"""
{name} - 工作流描述

详情请查看 workflow.yaml
"""

from .{name} import {name}

__all__ = ["{name}"]
'''

    (workflow_dir / "__init__.py").write_text(init_content, encoding="utf-8")

    # 创建 {pipeline_name}.py
    workflow_py_content = f'''# -*- coding: utf-8 -*-
"""
{name} - 工作流实现

详情请查看 workflow.yaml
"""

from typing import Dict, Any, Optional
import yaml


class {name}:
    """
    {name}

    工作流实现
    """

    def __init__(self):
        self.name = "{name}"
        self.version = "1.0.0"
        self.description = "工作流描述"
        self.config = None
        self.steps = []

    def load_config(self, config_path: Optional[str] = None):
        """加载工作流配置"""
        if config_path is None:
            config_path = Path(__file__).parent / "workflow.yaml"

        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        self.config = config
        self.steps = config.get("steps", [])
        return self

    def execute(self, **kwargs) -> Dict[str, Any]:
        """执行工作流"""
        results = {{}}

        for step in self.steps:
            step_name = step.get("name")
            # 这里实现具体的步骤执行逻辑
            results[step_name] = {{"status": "completed"}}

        return {{"status": "completed", "workflow": self.name, "results": results}}


def main():
    """入口函数"""
    workflow = {name}()
    workflow.load_config()
    return workflow


if __name__ == "__main__":
    wf = main()
'''

    (workflow_dir / f"{name}.py").write_text(workflow_py_content, encoding="utf-8")

    # 创建 README.md
    readme_content = f'''# {name}

工作流描述

## 用途

描述这个工作流是做什么的。

## 输入

- 输入参数1: 描述
- 输入参数2: 描述

## 输出

- 输出1: 描述
- 输出2: 描述

## 步骤

1. **step1**: 第一步描述
2. **step2**: 第二步描述

## 使用示例

```python
from {name} import {name}

workflow = {name}()
workflow.load_config()
result = workflow.execute(param1="value1")
```
'''

    (workflow_dir / "README.md").write_text(readme_content, encoding="utf-8")

    print(f"✅ 工作流创建成功: {name}")
    print(f"   路径: {workflow_dir.relative_to(PROJECT_ROOT)}")
    print(f"   文件:")
    print(f"     - workflow.yaml")
    print(f"     - __init__.py")
    print(f"     - {name}.py")
    print(f"     - README.md")
    print(f"\n📝 下一步:")
    print(f"   1. 编辑 workflow.yaml 定义工作流步骤")
    print(f"   2. 编辑 {name}.py 实现工作流逻辑")
    print(f"   3. 编辑 README.md 完善文档")


def main():
    parser = argparse.ArgumentParser(description="创建新工作流模板")
    parser.add_argument("--name", "-n", required=True, help="工作流名称 (例如: content)")

    args = parser.parse_args()

    create_workflow(args.name)


if __name__ == "__main__":
    main()
