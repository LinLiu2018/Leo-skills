@echo off
chcp 65001 >nul
cls
echo ========================================
echo        OpenClaw Gateway 启动器
echo   官方仓库: github.com/openclaw/openclaw
echo ========================================
echo.
echo 正在启动...
echo.

cd /d "%~dp0"

REM 启动日志监视器
echo [1/2] 启动日志监视器...
start /B "LeoLogger" node feishu_log_watcher.js 2>nul

REM 启动 Gateway
echo [2/2] 启动 OpenClaw Gateway...
cd /d "D:\moltbot"
node openclaw.mjs gateway --port 18789

pause
