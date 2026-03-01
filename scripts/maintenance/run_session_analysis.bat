@echo off
REM 注册会话分析定时任务 - 每周日 06:00 执行
set PYTHONUTF8=1
cd /d "d:\桌面\leo_ai_system"
python scripts/maintenance/auto_analyze_sessions.py
