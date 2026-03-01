#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Claude 会话自动初始化脚本

用法:
    python .claude/session_init.py [模式]

模式:
    continue  - 继续当前项目（默认）
    fresh     - 新任务，清空上下文
    demo      - 运行演示
    test      - 测试记忆系统

示例:
    python .claude/session_init.py
    python .claude/session_init.py continue
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime


def load_memory():
    """加载 memory.json"""
    memory_path = Path(__file__).parent / "memory.json"
    if memory_path.exists():
        with open(memory_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def generate_context(memory, mode="continue"):
    """生成 Claude 上下文"""

    if mode == "fresh":
        return """
## 新任务模式

准备开始新的开发任务。
请先检查当前项目状态，了解可用资源：
- 查看能力索引: leo_knowledge/context/capability_index.md
- 查看开发指南: leo_knowledge/context/development_guide.md
"""

    project = memory.get("current_project", "Leo Wingman v2.0")
    completed = memory.get("completed_tasks", [])
    pending = memory.get("pending_tasks", [])
    key_files = memory.get("key_files", [])

    context = f"""## 会话上下文恢复

**项目**: {project}
**时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
**模式**: {mode}

### ✅ 已完成 ({len(completed)}项)
"""
    for task in completed[-5:]:  # 只显示最近5个
        context += f"- ✅ {task}\n"

    context += f"\n### 🔄 待完成 ({len(pending)}项)\n"
    for i, task in enumerate(pending[:5], 1):  # 只显示前5个
        context += f"{i}. {task}\n"

    context += "\n### 📁 关键文件\n"
    for f in key_files[:3]:
        context += f"- `{f}`\n"

    context += f"""
### 🚀 快捷命令
```bash
# 测试系统
python examples/v2_demo.py

# 查看记忆
python -c "from src.leo_memory import get_auto_memory; print(get_auto_memory().get_session_summary())"

# 统计 Agents
ls src/leo_subagents/agents/ | wc -l
```

### 💡 下一步建议
"""

    if pending:
        context += f"优先处理: **{pending[0]}**\n"
    else:
        context += "所有任务已完成，请确认下一步计划。\n"

    return context


def update_memory(**kwargs):
    """更新 memory.json"""
    memory_path = Path(__file__).parent / "memory.json"
    memory = load_memory()
    memory.update(kwargs)
    memory["last_session"] = datetime.now().strftime("%Y-%m-%d")

    with open(memory_path, 'w', encoding='utf-8') as f:
        json.dump(memory, f, indent=2, ensure_ascii=False)


def copy_to_clipboard(text):
    """复制到剪贴板（Windows）"""
    try:
        # 使用 PowerShell 复制到剪贴板
        subprocess.run(
            ["powershell", "-command", f"Set-Clipboard -Value '{text.replace(\"'\", \"'\"'\"')}'"],
            check=True
        )
        return True
    except:
        return False


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "continue"
    valid_modes = ["continue", "fresh", "demo", "test"]

    if mode not in valid_modes:
        print(f"❌ 无效模式: {mode}")
        print(f"可用模式: {', '.join(valid_modes)}")
        sys.exit(1)

    memory = load_memory()
    context = generate_context(memory, mode)

    # 输出上下文
    print(context)
    print("\n" + "="*60)

    # 尝试复制到剪贴板
    if copy_to_clipboard(context):
        print("✅ 已自动复制到剪贴板，直接粘贴到 Claude 即可")
    else:
        print("⚠️  请手动复制以上内容，粘贴到 Claude 新会话")

    print("="*60)

    # 根据模式执行操作
    if mode == "demo":
        print("\n🚀 正在启动演示...")
        subprocess.run([sys.executable, "examples/v2_demo.py"])

    elif mode == "test":
        print("\n🧠 正在测试记忆系统...")
        # 这里可以添加测试代码
        print("测试完成")

    # 更新最后会话时间
    update_memory()


if __name__ == "__main__":
    main()
