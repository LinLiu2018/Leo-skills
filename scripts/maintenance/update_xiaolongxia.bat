@echo off
chcp 65001 >nul
echo ========================================
echo   OpenClaw 自动更新
echo   官方仓库: github.com/openclaw/openclaw
echo ========================================
echo.

cd /d D:\moltbot

echo [1/4] 检查当前版本...
for /f "tokens=*" %%i in ('node openclaw.mjs --version 2^>nul') do set CURRENT_VERSION=%%i
echo 当前版本: %CURRENT_VERSION%

echo.
echo [2/4] 检查更新...
node openclaw.mjs update

echo.
echo ========================================
echo   更新检查完成
echo ========================================
echo.
echo 提示: 如果 Gateway 正在运行，请重启以应用更新
echo.
pause
