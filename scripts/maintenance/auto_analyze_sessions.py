# -*- coding: utf-8 -*-
"""
auto_analyze_sessions.py - 定时自动执行会话分析

由 Windows 任务计划程序或 OpenClaw cron 触发。
执行 analyze_sessions_skill 全量分析，生成报告到 .claude/logs/。
"""

import json
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))


def run():
    from leo_skills.utilities.analyze_sessions_skill import (
        AnalyzeSessionsSkill,
    )

    skill = AnalyzeSessionsSkill(project_root=str(PROJECT_ROOT))
    result = skill.execute(source="all", save_report=True, update_memory=True)

    # 写入执行日志
    log_dir = PROJECT_ROOT / ".claude" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "auto_analyze.log"
    entry = {
        "timestamp": datetime.now().isoformat(),
        "status": result.get("status"),
        "sessions": result.get("sessions_analyzed", 0),
        "report": result.get("report_path", ""),
    }
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    print(f"[{entry['timestamp']}] 分析完成: {entry['sessions']} 个会话")
    return 0 if result.get("status") == "completed" else 1


if __name__ == "__main__":
    sys.exit(run())
