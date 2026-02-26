@echo off
REM 每日记忆同步 - Windows 批处理脚本
REM 用于 Windows 任务计划程序

cd /d "D:\桌面\leo_ai_system"
python scripts\daily_memory_sync.py >> logs\daily_sync.log 2>&1

echo [%date% %time%] 同步完成 >> logs\daily_sync.log
