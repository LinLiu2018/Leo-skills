#!/usr/bin/env python3
"""
Claude 新会话自动初始化脚本

用法:
    python .claude/startup.py [任务类型]

示例:
    python .claude/startup.py continue    # 继续v2.0实施
    python .claude/startup.py memory      # 测试记忆系统
    python .claude/startup.py demo        # 运行演示
"""

import sys
import json

# 会话上下文模板
CONTEXT_TEMPLATES = {
    "continue": """
## 会话上下文恢复

**项目**: Leo Wingman v2.0
**状态**: 实施中
**日期**: 2026-02-28

### 已完成
- ✅ 52个Workflows
- ✅ 37个Agents
- ✅ 全自动记忆系统(auto_memory.py, memory_hooks.py)
- ✅ 4层自动进化架构
- ✅ 用户偏好学习
- ✅ 文档更新(CHANGELOG, README, RELEASE)

### 待完成
1. 端到端测试(Villa Agent → Workflow → 飞书)
2. 为5个房产Agent启用@auto_memorize
3. OpenClaw集成测试
4. Workflow实现类(当前只有定义)

### 关键文件
- src/leo_memory/ - 自动记忆系统
- src/leo_subagents/agents/{villa,residential,leasing,commercial_sales,auction}_agent/
- examples/v2_demo.py - 演示脚本

### 下一步
请先运行 `python examples/v2_demo.py` 验证系统状态。
""",

    "memory": """
## 测试全自动记忆系统

**目标**: 验证自动记忆功能

### 测试步骤
1. 导入 leo_memory 模块
2. 检查自动初始化
3. 测试自动记录
4. 验证跨Agent共享

### 关键代码
```python
from leo_memory import get_auto_memory, auto_record, get_context

# 检查状态
memory = get_auto_memory()
print(memory.get_session_summary())
```
""",

    "demo": """
## 运行系统演示

**脚本**: examples/v2_demo.py

**功能**:
- 演示自动记忆
- 演示多Agent协作
- 演示工作流
- 展示系统统计
""",
}


def print_context(context_type: str):
    """打印会话上下文"""
    context = CONTEXT_TEMPLATES.get(context_type, CONTEXT_TEMPLATES["continue"])
    print(context)
    print("\n" + "="*50)
    print("请根据以上上下文继续工作")
    print("="*50)


def main():
    task = sys.argv[1] if len(sys.argv) > 1 else "continue"
    print_context(task)


if __name__ == "__main__":
    main()
