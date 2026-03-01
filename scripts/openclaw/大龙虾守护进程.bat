@echo off
chcp 65001 >nul
cls
echo ========================================
echo        OpenClaw 守护进程
echo   官方仓库: github.com/openclaw/openclaw
echo ========================================
echo.
echo 功能: 自动监控并重启 OpenClaw Gateway
echo.
echo ========================================
echo.

:LOOP
echo [%time%] 检查 OpenClaw 状态...

REM 检查 Gateway 是否在运行
tasklist /FI "IMAGENAME eq node.exe" 2>nul | findstr /i "node.exe" >nul
if errorlevel 1 (
    echo [%time%] Gateway 未运行，正在启动...
    start /B "LeoGateway" node "D:\moltbot\openclaw.mjs" gateway --port 18789
    echo [%time%] Gateway 已启动
) else (
    echo [%time%] Gateway 运行正常
)

REM 检查日志监视器是否在运行
tasklist /FI "WINDOWTITLE eq LeoLogger*" 2>nul | findstr /i "node.exe" >nul
if errorlevel 1 (
    echo [%time%] 日志监视器未运行，正在启动...
    start /B "LeoLogger" node "D:\桌面\leo_ai_system\scripts\feishu_log_watcher.js"
    echo [%time%] 日志监视器已启动
) else (
    echo [%time%] 日志监视器运行正常
)

echo.
REM 等待 30 秒后再次检查
timeout /t 30 /nobreak >nul
goto LOOP
