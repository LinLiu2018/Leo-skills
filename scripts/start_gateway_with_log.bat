@echo off
chcp 65001 >nul
echo ========================================
echo   OpenClaw Gateway + 自动日志
echo   官方仓库: github.com/openclaw/openclaw
echo ========================================
echo.
echo 同时启动 Gateway 和对话日志监视器
echo 所有飞书对话将自动记录到 logs\feishu\
echo.
echo ========================================

cd /d "%~dp0"

echo [1/2] 启动飞书对话日志监视器...
start /B "LogWatcher" node feishu_log_watcher.js

echo [2/2] 启动 Gateway...
cd /d "D:\moltbot"
node openclaw.mjs gateway --port 18789

if errorlevel 1 (
    echo.
    echo 错误: Gateway 启动失败
    pause
    exit /b 1
)
