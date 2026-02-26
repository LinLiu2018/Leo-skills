@echo off
REM OpenClaw Gateway 静默启动脚本（无控制台窗口）
REM 用于开机自启场景
REM 用法: 通过任务计划程序或快捷方式运行

chcp 65001 >nul

REM 检查 Gateway 是否已运行
netstat -ano | findstr "18789" >nul 2>&1
if %errorlevel% equ 0 (
    echo Gateway 已运行，退出
    exit /b 0
)

REM 切换到 OpenClaw 目录
cd /d D:\moltbot

REM 修复配置（静默）
node openclaw.mjs doctor --fix 2>nul >nul
node openclaw.mjs config set gateway.mode local 2>nul >nul

REM 启动 Gateway（无窗口）
set "PS_COMMAND=Start-Process -FilePath 'node' -ArgumentList 'openclaw.mjs','gateway','--port','18789' -WindowStyle Hidden -WorkingDirectory 'D:\moltbot'"

powershell -ExecutionPolicy Bypass -Command "%PS_COMMAND%"

REM 等待启动
timeout /t 5 /nobreak >nul 2>&1

REM 验证
netstat -ano | findstr "18789" >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Gateway 已启动
    exit /b 0
) else (
    echo [ERROR] Gateway 启动失败
    exit /b 1
)
