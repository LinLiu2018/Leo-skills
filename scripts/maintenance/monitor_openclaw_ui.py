#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw UI 监控脚本
检查管理界面是否完整，缺失时告警
"""

import os
import sys
from pathlib import Path
from datetime import datetime

def check_ui_status():
    """检查 OpenClaw UI 状态"""
    openclaw_dir = Path("D:/openclaw")
    ui_dir = openclaw_dir / "dist" / "control-ui"
    index_file = ui_dir / "index.html"

    result = {
        "timestamp": datetime.now().isoformat(),
        "ui_dir_exists": ui_dir.exists(),
        "index_exists": index_file.exists(),
        "status": "unknown"
    }

    if not ui_dir.exists():
        result["status"] = "missing"
        result["message"] = "UI 目录缺失，需要重新构建"
    elif not index_file.exists():
        result["status"] = "incomplete"
        result["message"] = "UI 目录存在但 index.html 缺失"
    else:
        result["status"] = "ok"
        result["message"] = "UI 正常"

    return result

def log_result(result):
    """记录检查结果"""
    log_dir = Path(__file__).parent.parent.parent / "docs" / "progress"
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / "openclaw_ui_monitor.log"

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"{result['timestamp']} | {result['status']} | {result['message']}\n")

def main():
    result = check_ui_status()
    log_result(result)

    if result["status"] != "ok":
        print(f"⚠️  {result['message']}")
        print("修复命令: cd D:/openclaw && pnpm ui:build")
        return 1
    else:
        print(f"✅ {result['message']}")
        return 0

if __name__ == "__main__":
    sys.exit(main())
