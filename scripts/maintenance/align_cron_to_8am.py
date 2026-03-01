# -*- coding: utf-8 -*-
"""
定时任务时间对齐脚本 - 将所有用户任务调整到早上 8:00

用法：python scripts/maintenance/align_cron_to_8am.py
"""

import json
import os
from pathlib import Path

# 配置
JOBS_FILE = r"C:\Users\刘方林\.openclaw\cron\jobs.json"
BACKUP_FILE = r"C:\Users\刘方林\.openclaw\cron\jobs.json.backup"

# 需要保持原样的系统任务
SYSTEM_TASKS = ["health_check_hourly"]

# 周任务（调整到周日 8:00）
WEEKLY_TASKS = [
    "skills_update_weekly",
    "宁波别墅_每周内容报告",
    "memory_cleanup_weekly",
    "repo_watch_weekly"  # 周一 8:00
]

def load_jobs():
    """加载定时任务配置"""
    with open(JOBS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_jobs(data):
    """保存定时任务配置"""
    # 先备份
    if os.path.exists(JOBS_FILE):
        import shutil
        shutil.copy(JOBS_FILE, BACKUP_FILE)
        print(f"[OK] Backup saved to: {BACKUP_FILE}")
    
    with open(JOBS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[OK] Config saved to: {JOBS_FILE}")

def align_to_8am(job):
    """将任务调整到 8:00"""
    name = job.get("name", "")
    schedule = job.get("schedule", {})
    
    if name in SYSTEM_TASKS:
        return job, "KEEP (system)"
    
    if name == "repo_watch_weekly":
        schedule["expr"] = "0 8 * * 1"
        return job, "MON 8:00"
    
    if name in WEEKLY_TASKS:
        schedule["expr"] = "0 8 * * 0"
        return job, "SUN 8:00"
    
    if schedule.get("expr", "").startswith("0 */"):
        schedule["expr"] = "0 8 * * *"
        return job, "DAILY 8:00"
    
    current_expr = schedule.get("expr", "")
    if current_expr.startswith("0 8 "):
        return job, "ALREADY 8:00"
    
    parts = current_expr.split()
    if len(parts) == 5:
        parts[1] = "8"
        schedule["expr"] = " ".join(parts)
        return job, "DAILY 8:00"
    
    return job, "UNCHANGED"

def main():
    print("=" * 60)
    print("定时任务时间对齐脚本 - 调整到早上 8:00")
    print("=" * 60)
    print()
    
    # 加载配置
    print("正在加载定时任务配置...")
    data = load_jobs()
    jobs = data.get("jobs", [])
    print(f"找到 {len(jobs)} 个定时任务")
    print()
    
    # 调整每个任务
    print("调整详情:")
    print("-" * 60)
    
    for job in jobs:
        name = job.get("name", "未知")
        old_expr = job.get("schedule", {}).get("expr", "")
        
        job, status = align_to_8am(job)
        
        new_expr = job.get("schedule", {}).get("expr", "")
        
        if old_expr != new_expr:
            print(f"[MODIFY] {name}")
            print(f"   {old_expr} -> {status}")
        else:
            print(f"[KEEP] {name}: {status}")
    
    print()
    print("-" * 60)
    
    # 保存配置
    print("正在保存新配置...")
    save_jobs(data)
    
    print()
    print("=" * 60)
    print("[SUCCESS] 定时任务时间对齐完成！")
    print("=" * 60)
    print()
    print("注意：")
    print("1. 原配置已备份到：jobs.json.backup")
    print("2. 重启 OpenClaw Gateway 后生效")
    print("3. 如需恢复，复制备份文件覆盖 jobs.json 即可")
    print()
    print("重启命令:")
    print("  openclaw gateway restart")
    print()

if __name__ == "__main__":
    main()
