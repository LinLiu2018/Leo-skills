# -*- coding: utf-8 -*-
"""
更新 Cron 任务配置
1. 取消"宁波新房_定时检查_v2"任务
2. 修改"房产资讯_每日 8 点_v3"任务，加入房产政策内容
"""

import json
from pathlib import Path

JOBS_FILE = r"C:\Users\刘方林\.openclaw\cron\jobs.json"
BACKUP_FILE = r"C:\Users\刘方林\.openclaw\cron\jobs.json.backup_update"

# 1. 备份配置
print("正在备份配置...")
import shutil
shutil.copy(JOBS_FILE, BACKUP_FILE)
print(f"[OK] 备份完成：{BACKUP_FILE}")

# 2. 加载配置
print("正在加载配置...")
with open(JOBS_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

jobs = data.get('jobs', [])
print(f"[OK] 共加载 {len(jobs)} 个任务")

# 3. 取消"宁波新房_定时检查_v2"任务
print("\n正在取消'宁波新房_定时检查_v2'任务...")
for job in jobs:
    if job.get('name') == '宁波新房_定时检查_v2':
        job['enabled'] = False
        print(f"[OK] 已取消任务：{job['name']}")
        break

# 4. 修改"房产资讯_每日 8 点_v3"任务，加入房产政策内容
print("\n正在修改'房产资讯_每日 8 点_v3'任务...")
for job in jobs:
    if job.get('name') == '房产资讯_每日 8 点_v3':
        old_payload = job['payload']['message']
        new_payload = old_payload + " 同时搜索宁波房产政策（限购、贷款、契税、人才补贴等），并解读政策对刚需购房的影响。"
        job['payload']['message'] = new_payload
        print(f"[OK] 已更新任务：{job['name']}")
        print(f"  原指令：{old_payload[:50]}...")
        print(f"  新指令：{new_payload[:50]}...")
        break

# 5. 保存配置
print("\n正在保存配置...")
with open(JOBS_FILE, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f"[OK] 配置已保存：{JOBS_FILE}")

# 6. 显示修改摘要
print("\n" + "=" * 60)
print("修改摘要")
print("=" * 60)
print("1. 取消任务：宁波新房_定时检查_v2")
print("2. 更新任务：房产资讯_每日 8 点_v3（加入房产政策内容）")
print()
print("注意：需要重启 Gateway 才能生效")
print("重启命令：openclaw gateway restart")
print("=" * 60)
