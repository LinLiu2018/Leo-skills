# -*- coding: utf-8 -*-
"""
添加 X 平台监控 Cron 任务
"""

import json
import uuid

JOBS_FILE = r"C:\Users\刘方林\.openclaw\cron\jobs.json"

# 新增 Cron 任务
NEW_JOBS = [
    {
        "id": str(uuid.uuid4()),
        "agentId": "leo-assistant",
        "name": "X 平台博主_每日检查",
        "description": "每日 8 点和 20 点检查 X 平台博主更新",
        "enabled": True,
        "schedule": {
            "kind": "cron",
            "expr": "0 8,20 * * *",
            "tz": "Asia/Shanghai"
        },
        "sessionTarget": "isolated",
        "wakeMode": "now",
        "payload": {
            "kind": "agentTurn",
            "message": "检查 X 平台博主 (@向阳乔木 @openclaw @anthropic @github) 最新推文，筛选高质量内容"
        },
        "delivery": {
            "mode": "announce",
            "channel": "feishu",
            "to": "ou_099438b3924bd34e5f9445bc8220a460"
        }
    },
    {
        "id": str(uuid.uuid4()),
        "agentId": "leo-assistant",
        "name": "X 平台内容_学习转化",
        "description": "每日 21 点将 X 平台内容转化为学习笔记",
        "enabled": True,
        "schedule": {
            "kind": "cron",
            "expr": "0 21 * * *",
            "tz": "Asia/Shanghai"
        },
        "sessionTarget": "isolated",
        "wakeMode": "now",
        "payload": {
            "kind": "agentTurn",
            "message": "将今日 X 平台优质内容转化为学习笔记和行动计划"
        },
        "delivery": {
            "mode": "announce",
            "channel": "feishu",
            "to": "ou_099438b3924bd34e5f9445bc8220a460"
        }
    },
    {
        "id": str(uuid.uuid4()),
        "agentId": "leo-assistant",
        "name": "X 平台监控_周报",
        "description": "每周日生成 X 平台监控周报",
        "enabled": True,
        "schedule": {
            "kind": "cron",
            "expr": "0 21 * * 0",
            "tz": "Asia/Shanghai"
        },
        "sessionTarget": "isolated",
        "wakeMode": "now",
        "payload": {
            "kind": "agentTurn",
            "message": "生成 X 平台博主监控周报，汇总本周优质内容、趋势分析、学习收获"
        },
        "delivery": {
            "mode": "announce",
            "channel": "feishu",
            "to": "ou_099438b3924bd34e5f9445bc8220a460"
        }
    }
]

# 加载配置
with open(JOBS_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 添加新任务
jobs = data.get('jobs', [])
for new_job in NEW_JOBS:
    jobs.append(new_job)
    print(f"[ADD] {new_job['name']}: {new_job['schedule']['expr']}")

# 保存
with open(JOBS_FILE, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n[OK] Added {len(NEW_JOBS)} X monitor cron jobs")
print("Restart Gateway to apply changes")
