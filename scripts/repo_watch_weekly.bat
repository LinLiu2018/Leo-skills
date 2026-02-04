@echo off
chcp 65001 >nul
cd /d "d:\桌面\leo_ai_system"
echo [%date% %time%] 开始执行仓库周报任务...
py scripts\repo_watch_weekly.py
echo [%date% %time%] 任务执行完成
