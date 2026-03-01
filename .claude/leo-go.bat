@echo off
chcp 65001 >nul
echo.
echo ===========================================
echo   Leo Wingman v2.0 - 会话快速恢复
echo ===========================================
echo.
echo 正在生成上下文...
echo.

cd /d D:\桌面\leo_ai_system
python .claude\session_init.py %*

echo.
pause
