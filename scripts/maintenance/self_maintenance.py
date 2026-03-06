#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Leo AI System - 自我维护脚本

自动执行系统维护任务：
1. 清理 OpenClaw 大会话文件
2. 优化系统状态
3. 检查健康
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime


def main():
    print("=" * 60)
    print("Leo AI System - 自我维护")
    print("=" * 60)
    print()

    # 1. 清理 OpenClaw 大会话文件
    print("[1/3] 清理 OpenClaw 大会话文件...")
    session_dir = Path.home() / ".openclaw" / "agents" / "leo-assistant" / "sessions"

    if session_dir.exists():
        large_files = []
        for f in session_dir.glob("*.jsonl"):
            if f.stat().st_size > 500 * 1024:  # 500KB
                large_files.append(f)

        if large_files:
            # 创建备份目录
            backup_dir = session_dir / f"sessions_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            backup_dir.mkdir(exist_ok=True)

            # 移动大文件
            total_size = 0
            for f in large_files:
                size_mb = f.stat().st_size / (1024 * 1024)
                print(f"  - 移动: {f.name} ({size_mb:.1f}MB)")
                f.rename(backup_dir / f.name)
                total_size += size_mb

            print(f"  已清理 {len(large_files)} 个文件，共 {total_size:.1f}MB")
        else:
            print("  无需清理的文件")
    else:
        print("  会话目录不存在")

    print()

    # 2. 检查并初始化自管理系统
    print("[2/3] 初始化自管理系统...")

    # 设置正确的路径
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))

    try:
        from src.leo_skills.core.system import initialize_system

        result = initialize_system()
        print(f"  初始化状态: {result.get('status')}")

        components = result.get('components', {})
        for name, status in components.items():
            print(f"    - {name}: {status}")

    except Exception as e:
        import traceback
        print(f"  初始化失败: {e}")
        traceback.print_exc()

    print()

    # 3. 运行健康检查
    print("[3/3] 运行健康检查...")
    try:
        from src.leo_skills.core.system import run_check

        health = run_check()
        print(f"  健康检查完成")

        if 'health' in health:
            h = health['health']
            print(f"    - 整体状态: {h.get('overall_status', 'unknown')}")

        if 'faults' in health:
            f = health['faults']
            print(f"    - 故障统计: {f.get('total', 0)} 个")

    except Exception as e:
        import traceback
        print(f"  健康检查失败: {e}")
        traceback.print_exc()

    print()
    print("=" * 60)
    print("维护完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()
