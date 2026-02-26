@echo off
chcp 65001 >nul
echo ========================================
echo   OpenClaw 自动更新检查 (后台运行)
echo   官方仓库: github.com/openclaw/openclaw
echo ========================================

cd /d D:\moltbot

:: 使用 openclaw update 命令检查更新
node openclaw.mjs update 2>nul

:: 写入检查日志
echo [%date% %time%] 更新检查完成 >> "D:\桌面\leo_ai_system\logs\openclaw_updates.log"
