#!/usr/bin/env python3
"""
每日记忆同步脚本
================
每晚11点自动同步过去24小时的飞书对话，记录成长轨迹

功能：
1. 同步飞书对话记忆
2. 提取关键有效动态
3. 生成每日成长日志
4. 支持 Windows 任务计划程序调用
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# 添加项目路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from leo_memory.feishu_memory import FeishuMemory

# 成长日志目录
GROWTH_LOG_DIR = PROJECT_ROOT / "docs" / "growth_logs"


def generate_daily_growth_log(memory: FeishuMemory) -> str:
    """生成每日成长日志"""

    today = datetime.now().strftime('%Y-%m-%d')

    content = f"""# 每日成长日志 - {today}

> 自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 今日任务完成情况

| 任务 | 状态 |
|------|------|
"""

    # 今日任务
    today_tasks = [t for t in memory.memories["tasks"]
                   if t.get("timestamp", "").startswith(today[:10])]

    for task in today_tasks[-10:]:
        task_text = task['task'][:50].replace('|', '/')
        content += f"| {task_text} | {task['status']} |\n"

    if not today_tasks:
        content += "| (今日暂无记录) | - |\n"

    content += f"""
## 今日关键对话

"""

    # 今日对话
    today_convs = [c for c in memory.memories["conversations"]
                   if c.get("timestamp", "").startswith(today[:10]) and c["role"] == "user"]

    for conv in today_convs[-15:]:
        conv_text = conv['content'][:100].replace('\n', ' ')
        time_str = conv['timestamp'][11:16] if len(conv['timestamp']) > 16 else ""
        content += f"- [{time_str}] {conv_text}\n"

    if not today_convs:
        content += "- (今日暂无对话记录)\n"

    content += f"""
## 今日决策与成果

"""

    # 今日决策
    today_decisions = [d for d in memory.memories["decisions"]
                       if d.get("timestamp", "").startswith(today[:10])]

    for decision in today_decisions[-10:]:
        content += f"- {decision['decision'][:80]}\n"

    if not today_decisions:
        content += "- (今日暂无重要决策)\n"

    content += f"""
## 今日关键信息

"""

    # 今日关键信息
    today_info = [i for i in memory.memories["key_info"]
                  if i.get("timestamp", "").startswith(today[:10])]

    for info in today_info[-10:]:
        content += f"- {info['info'][:60]}\n"

    if not today_info:
        content += "- (今日暂无关键信息)\n"

    content += f"""
## 统计

- 任务数: {len(today_tasks)}
- 对话数: {len(today_convs)}
- 决策数: {len(today_decisions)}
- 关键信息: {len(today_info)}

---
*此日志由 daily_memory_sync.py 自动生成*
"""

    return content


def save_growth_log(content: str) -> str:
    """保存成长日志"""
    GROWTH_LOG_DIR.mkdir(parents=True, exist_ok=True)

    today = datetime.now().strftime('%Y-%m-%d')
    log_file = GROWTH_LOG_DIR / f"growth_{today}.md"

    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(content)

    return str(log_file)


def main():
    """主函数 - 每日同步"""
    print(f"[{datetime.now()}] 开始每日记忆同步...")

    # 1. 同步飞书记忆
    memory = FeishuMemory()
    result = memory.sync(hours_back=24)

    print(f"  - 处理消息: {result['messages_processed']}")
    print(f"  - 提取任务: {result['tasks_extracted']}")
    print(f"  - 提取决策: {result['decisions_extracted']}")

    # 2. 生成成长日志
    growth_log = generate_daily_growth_log(memory)
    log_file = save_growth_log(growth_log)

    print(f"  - 成长日志: {log_file}")

    # 3. 输出结果
    result["growth_log"] = log_file
    result["sync_time"] = datetime.now().isoformat()

    print(f"[{datetime.now()}] 同步完成!")
    print(json.dumps(result, indent=2, ensure_ascii=False))

    return result


if __name__ == "__main__":
    main()
