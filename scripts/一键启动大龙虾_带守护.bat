@echo off
chcp 65001 >nul
echo ========================================
echo   启动大龙虾网关 + 自动守护进程
echo ========================================
echo.

:: 检查 PowerShell
where powershell >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] PowerShell 未找到
    pause
    exit /b 1
)

:: 修复 OpenClaw 配置
echo [1/3] 修复 OpenClaw 配置...
cd /d D:\moltbot 2>nul
node openclaw.mjs doctor --fix 2>nul >nul
node openclaw.mjs config set gateway.mode local 2>nul >nul
echo [✓] 配置修复完成
echo.

:: 启动守护进程
echo [2/3] 正在启动守护进程...
start "OpenClaw Guardian" powershell -ExecutionPolicy Bypass -WindowStyle Minimized -File "%~dp0\openclaw_guardian.ps1"
if %errorlevel% neq 0 (
    echo [错误] 守护进程启动失败
    pause
    exit /b 1
)
echo [✓] 守护进程已启动
echo.

:: 等待网关启动
echo [3/3] 等待网关初始化...
timeout /t 5 /nobreak >nul

:: 检查端口
echo 检查网关状态...
netstat -ano | findstr "18789" >nul
if %errorlevel% equ 0 (
    echo [✓] 网关运行正常 (端口 18789)
    echo.
    echo 访问地址: http://127.0.0.1:18789?token=leo-feishu-2024
    echo 守护日志: %USERPROFILE%\.openclaw\logs\guardian_*.log
) else (
    echo [!] 网关可能未启动，查看错误日志
    echo 错误日志: %USERPROFILE%\.openclaw\logs\error_*.log
    echo.
    echo 手动修复命令:
    echo   cd D:\moltbot
    echo   node openclaw.mjs doctor --fix
    echo   node openclaw.mjs gateway --port 18789
)

echo.
pause
