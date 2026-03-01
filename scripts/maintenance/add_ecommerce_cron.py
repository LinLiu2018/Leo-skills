# -*- coding: utf-8 -*-
"""
跨境电商 Cron 任务添加脚本
"""

import json
import uuid
from datetime import datetime

JOBS_FILE = r"C:\Users\刘方林\.openclaw\cron\jobs.json"

# 新增 Cron 任务
NEW_JOBS = [
    {
        "id": str(uuid.uuid4()),
        "agentId": "leo-assistant",
        "name": "竞品监控_每日 9 点",
        "description": "每日 9 点监控亚马逊/eBay/速卖通竞品",
        "enabled": True,
        "schedule": {
            "kind": "cron",
            "expr": "0 9 * * *",
            "tz": "Asia/Shanghai"
        },
        "sessionTarget": "isolated",
        "wakeMode": "now",
        "payload": {
            "kind": "agentTurn",
            "message": "监控亚马逊/eBay/速卖通智能穿戴设备竞品，记录价格、评价、销量变化"
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
        "name": "物流成本_每周分析",
        "description": "每周一 10 点分析物流成本",
        "enabled": True,
        "schedule": {
            "kind": "cron",
            "expr": "0 10 * * 1",
            "tz": "Asia/Shanghai"
        },
        "sessionTarget": "isolated",
        "wakeMode": "now",
        "payload": {
            "kind": "agentTurn",
            "message": "分析上周物流成本，对比不同物流商价格，生成优化建议"
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
        "name": "选品推荐_每周生成",
        "description": "每周五 15 点生成选品推荐",
        "enabled": True,
        "schedule": {
            "kind": "cron",
            "expr": "0 15 * * 5",
            "tz": "Asia/Shanghai"
        },
        "sessionTarget": "isolated",
        "wakeMode": "now",
        "payload": {
            "kind": "agentTurn",
            "message": "基于市场趋势和竞品分析，生成下周智能穿戴设备选品推荐"
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

print(f"\n[OK] Added {len(NEW_JOBS)} ecommerce cron jobs")
print("Restart Gateway to apply changes")
