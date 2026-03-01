# -*- coding: utf-8 -*-
"""
添加睡眠提醒 Cron 任务
每天晚上 11 点提醒睡觉
"""

import json
import os
from datetime import datetime

JOBS_FILE = r"C:\Users\刘方林\.openclaw\cron\jobs.json"
BACKUP_FILE = r"C:\Users\刘方林\.openclaw\cron\jobs.json.backup_sleep"

# 睡眠提醒 Cron 任务
SLEEP_REMINDER_JOB = {
    "id": "sleep_reminder_23h",
    "agentId": "leo-assistant",
    "name": "睡眠提醒_每晚 11 点",
    "description": "每天晚上 11 点提醒用户睡觉",
    "enabled": True,
    "schedule": {
        "kind": "cron",
        "expr": "0 23 * * *",  # 每天 23:00
        "tz": "Asia/Shanghai"
    },
    "sessionTarget": "main",
    "wakeMode": "now",
    "payload": {
        "kind": "agentTurn",
        "message": "发送睡眠提醒消息给用户"
    },
    "delivery": {
        "mode": "announce",
        "channel": "feishu",
        "to": "ou_099438b3924bd34e5f9445bc8220a460",
        "message": "🌙 晚安提醒 (23:00)\n\n亲爱的马拉松达人：\n\n明天早上 5:30 就要起床啦！\n\n🏃 今日训练目标：\n- 全马配速目标：6:00/km\n- 半马配速目标：5:37/km\n\n💡 睡眠建议：\n- 保证 7-8 小时睡眠\n- 睡前避免蓝光\n- 保持房间凉爽\n\n晚安，好梦！😴"
    }
}

# 起床提醒 Cron 任务
WAKE_UP_JOB = {
    "id": "wake_up_reminder_5h30m",
    "agentId": "leo-assistant",
    "name": "起床提醒_每天 5:30",
    "description": "每天早上 5 点半提醒起床",
    "enabled": True,
    "schedule": {
        "kind": "cron",
        "expr": "30 5 * * *",  # 每天 5:30
        "tz": "Asia/Shanghai"
    },
    "sessionTarget": "main",
    "wakeMode": "now",
    "payload": {
        "kind": "agentTurn",
        "message": "发送起床提醒消息给用户"
    },
    "delivery": {
        "mode": "announce",
        "channel": "feishu",
        "to": "ou_099438b3924bd34e5f9445bc8220a460",
        "message": "☀️ 早安提醒 (5:30)\n\n马拉松达人，早上好！\n\n🏃 今日训练建议：\n- 配速目标：全马 6:00/km，半马 5:37/km\n- 跑前热身 10 分钟\n- 跑后拉伸 10 分钟\n\n💪 今日目标：\n- 保持配速稳定\n- 注意补水\n- 享受跑步！\n\n新的一天，加油！🎉"
    }
}

def add_reminders():
    """添加睡眠和起床提醒"""
    print("=" * 80)
    print("添加睡眠/起床提醒")
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
    existing_sleep = [j for j in jobs if j.get('name') == '睡眠提醒_每晚 11 点']
    existing_wake = [j for j in jobs if j.get('name') == '起床提醒_每天 5:30']
    
    if not existing_sleep:
        jobs.append(SLEEP_REMINDER_JOB)
        print(f"[OK] 已添加睡眠提醒 (23:00)")
    else:
        print(f"[INFO] 睡眠提醒已存在")
    
    if not existing_wake:
        jobs.append(WAKE_UP_JOB)
        print(f"[OK] 已添加起床提醒 (5:30)")
    else:
        print(f"[INFO] 起床提醒已存在")
    
    data['jobs'] = jobs
    
    # 保存
    with open(JOBS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print()
    print("=" * 80)
    print("提醒配置完成")
    print("=" * 80)
    print()
    print("睡眠提醒：每天 23:00")
    print("起床提醒：每天 5:30")
    print()
    print("重启 Gateway 生效:")
    print("  cd D:\\openclaw")
    print("  node openclaw.mjs gateway restart")
    print()

if __name__ == "__main__":
    add_reminders()
