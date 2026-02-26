@echo off
chcp 65001 >nul
echo ========================================
echo   启动 OpenClaw Gateway (v2026.1.30)
echo   官方仓库: github.com/openclaw/openclaw
echo ========================================
echo.
cd /d D:\moltbot

:: 检查并修复配置
echo [1/2] 检查配置...
node openclaw.mjs doctor --fix 2>nul >nul
if %errorlevel% neq 0 (
    echo [!] 配置有问题，尝试修复...
)

:: 确保 gateway.mode 设置
echo [2/2] 设置网关模式...
node openclaw.mjs config set gateway.mode local 2>nul >nul

echo.
echo 正在启动网关...
node openclaw.mjs gateway --port 18789
pause
