@echo off
chcp 65001 >nul
echo ========================================
echo   🦞 飞书对话日志监视器
echo ========================================
echo.
echo 启动后将自动记录所有飞书对话到日志文件
echo 日志位置: logs\feishu\dialogue_YYYY-MM-DD.md
echo.
echo ========================================

cd /d "%~dp0"
node feishu_log_watcher.js

if errorlevel 1 (
    echo.
    echo 错误: 启动失败
    pause
    exit /b 1
)
