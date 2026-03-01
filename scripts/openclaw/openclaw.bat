@echo off
chcp 65001 >nul
REM OpenClaw 统一入口脚本 (Windows)
REM 解决 npm CLI 和本地 runtime 不一致问题

set OPENCLAW_DIR=D:\openclaw
set NODE_CMD=node

if "%~1"=="" (
    echo Usage: openclaw ^<command^> [args...]
    echo.
    echo Commands:
    echo   gateway         启动网关服务
    echo   agent           运行 Agent
    echo   cron            管理定时任务
    echo   channels        管理消息渠道
    echo   doctor          诊断配置
    echo   dashboard       打开管理界面
    echo.
    exit /b 1
)

cd /d "%OPENCLAW_DIR%"
%NODE_CMD% openclaw.mjs %*
