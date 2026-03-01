# -*- coding: utf-8 -*-
"""
Cron 时间优化脚本
将 19 个任务分散到 7:00-10:00 时段，避免 API 限流
"""

import json
import os
from pathlib import Path
from datetime import datetime

# 配置
JOBS_FILE = r"C:\Users\刘方林\.openclaw\cron\jobs.json"
BACKUP_FILE = r"C:\Users\刘方林\.openclaw\cron\jobs.json.backup2"

# 时间调整映射 (任务名 -> 新时间)
SCHEDULE_MAP = {
    # 系统任务
    "capability_index_daily": "0 7 * * *",           # 7:00 (最早)
    
    # 核心资讯 (8:00 时段)
    "房产资讯_每日 8 点_v3": "0 8 * * *",             # 8:00
    "AI 财经资讯_每日 8 点_v2": "15 8 * * *",         # 8:15
    "AI 财经政治_每日 8 点_v3": "30 8 * * *",         # 8:30
    "房产内容创意_每日早": "45 8 * * *",              # 8:45
    "宁波别墅_每日内容策略": "0 9 * * *",             # 9:00
    "视频号公众号_内容收集": "15 9 * * *",            # 9:15
    
    # 定期检查
    "宁波新房_定时检查_v2": "0 8,12,18 * * *",       # 8:00,12:00,18:00 (每日 3 次)
    
    # 监控任务 (9:00 时段)
    "宁波别墅_小红书_每日监控": "30 9 * * *",         # 9:30
    "宁波别墅_抖音_每日监控": "45 9 * * *",           # 9:45
    "AI 与 OpenClaw_每日报告": "0 10 * * *",          # 10:00
    
    # 晚间任务
    "优质内容_每日 OpenClaw": "0 20 * * *",           # 20:00 (提前 1 小时)
    
    # 周任务
    "repo_watch_weekly": "0 9 * * 1",                # 周一 9:00
    "skills_update_weekly": "0 20 * * 0",            # 周日 20:00
    "memory_cleanup_weekly": "0 7 * * 0",            # 周日 7:00
    "宁波别墅_每周内容报告": "0 20 * * 0",           # 周日 20:00
    
    # 系统任务 (保持不变)
    "health_check_hourly": "0 * * * *",              # 每小时
    "github_skills_daily": "0 8 * * *",              # 8:00
}

# 添加 staggerMs 配置 (错开执行)
STAGGER_MAP = {
    "房产资讯_每日 8 点_v3": 0,
    "AI 财经资讯_每日 8 点_v2": 60000,       # 60 秒
    "AI 财经政治_每日 8 点_v3": 120000,      # 120 秒
    "房产内容创意_每日早": 180000,           # 180 秒
    "宁波别墅_每日内容策略": 240000,        # 240 秒
    "视频号公众号_内容收集": 300000,        # 300 秒
}


def optimize_cron():
    """优化 Cron 配置"""
    print("=" * 80)
    print("Cron 时间优化")
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
    modified = 0
    
    print()
    print("调整详情:")
    print("-" * 80)
    
    for job in jobs:
        name = job.get('name', '')
        old_expr = job.get('schedule', {}).get('expr', '')
        
        if name in SCHEDULE_MAP:
            new_expr = SCHEDULE_MAP[name]
            
            if old_expr != new_expr:
                job['schedule']['expr'] = new_expr
                modified += 1
                print(f"[MODIFY] {name}")
                print(f"         {old_expr} -> {new_expr}")
                
                # 添加 staggerMs
                if name in STAGGER_MAP:
                    job['schedule']['staggerMs'] = STAGGER_MAP[name]
                    print(f"         + staggerMs: {STAGGER_MAP[name]}ms")
            else:
                print(f"[KEEP]   {name}: {old_expr}")
        
        # 为 8:00 时段任务添加 staggerMs
        if old_expr.startswith("0 8 ") and 'staggerMs' not in job.get('schedule', {}):
            job['schedule']['staggerMs'] = 30000  # 默认 30 秒
            print(f"[ADD]    {name}: +staggerMs 30s")
    
    print()
    print("-" * 80)
    print(f"Modified: {modified} jobs")
    
    # 保存
    with open(JOBS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"[OK] Saved: {JOBS_FILE}")
    print()
    print("=" * 80)
    print("[SUCCESS] Cron 优化完成")
    print("=" * 80)
    print()
    print("新时间表:")
    print("  7:00  - 能力索引每日更新")
    print("  8:00  - 房产资讯 (核心)")
    print("  8:15  - AI 财经资讯")
    print("  8:30  - AI 财经政治")
    print("  8:45  - 房产内容创意")
    print("  9:00  - 宁波别墅策略")
    print("  9:15  - 视频号公众号收集")
    print("  9:30  - 小红书监控")
    print("  9:45  - 抖音监控")
    print("  10:00 - AI 与 OpenClaw 报告")
    print("  12:00 - 新房检查 (午间)")
    print("  18:00 - 新房检查 (晚间)")
    print("  20:00 - 优质内容 (提前)")
    print()
    print("重启 Gateway 生效:")
    print("  cd D:\\openclaw")
    print("  node openclaw.mjs gateway restart")
    print()


if __name__ == "__main__":
    optimize_cron()
