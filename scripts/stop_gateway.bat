@echo off
chcp 65001 >nul
echo ========================================
echo   停止 OpenClaw Gateway
echo ========================================
echo.
cd /d D:\moltbot
node openclaw.mjs gateway stop
echo Gateway 已停止。
pause
