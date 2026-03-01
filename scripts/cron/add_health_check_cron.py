# -*- coding: utf-8 -*-
"""
添加健康检查 Cron 任务
每 4 小时执行一次
"""

import json
import os
from datetime import datetime

JOBS_FILE = r"C:\Users\刘方林\.openclaw\cron\jobs.json"
BACKUP_FILE = r"C:\Users\刘方林\.openclaw\cron\jobs.json.backup_health"

# 健康检查 Cron 任务
HEALTH_CHECK_JOB = {
    "id": "health_check_4h",
    "agentId": "leo-assistant",
    "name": "健康检查_每 4 小时",
    "description": "每 4 小时自动执行系统健康检查，发送报告",
    "enabled": True,
    "schedule": {
        "kind": "cron",
        "expr": "0 */4 * * *",  # 每 4 小时
        "tz": "Asia/Shanghai"
    },
    "sessionTarget": "isolated",
    "wakeMode": "now",
    "payload": {
        "kind": "workflow",
        "workflow": "health-check-workflow",
        "message": "执行系统健康检查，生成报告并发送给用户"
    },
    "delivery": {
        "mode": "announce",
        "channel": "feishu",
        "to": "ou_099438b3924bd34e5f9445bc8220a460"
    },
    "retry": {
        "maxAttempts": 3,
        "delayMs": 300000  # 5 分钟
    }
}

def add_health_check_cron():
    """添加健康检查 Cron 任务"""
    print("=" * 80)
    print("添加健康检查 Cron 任务")
    print("=" * 80)
    print()
    
    # 备份
    if os.path.exists(JOBS_FILE):
        import shutil
        shutil.copy(JOBS_FILE, BACKUP_FILE)
        print(f"[OK] Backup: {BACKUP_FILE}")
    
    # 加载配置
    with open(JOBS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    jobs = data.get('jobs', [])
    
    # 检查是否已存在
    existing = [j for j in jobs if j.get('name') == '健康检查_每 4 小时']
    if existing:
        print(f"[INFO] 健康检查任务已存在，跳过")
        return
    
    # 添加新任务
    jobs.append(HEALTH_CHECK_JOB)
    data['jobs'] = jobs
    
    # 保存
    with open(JOBS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"[OK] 已添加健康检查 Cron 任务")
    print()
    print("=" * 80)
    print("配置详情")
    print("=" * 80)
    print(f"任务名称：{HEALTH_CHECK_JOB['name']}")
    print(f"执行时间：每 4 小时 (0:00, 4:00, 8:00, 12:00, 16:00, 20:00)")
    print(f"发送渠道：飞书")
    print(f"接收用户：ou_099438b3924bd34e5f9445bc8220a460")
    print()
    print("重启 Gateway 生效:")
    print("  cd D:\\openclaw")
    print("  node openclaw.mjs gateway restart")
    print()

if __name__ == "__main__":
    add_health_check_cron()
