@echo off
chcp 65001 >nul
title OpenClaw 智能守护系统
cls
echo ========================================
echo   OpenClaw 智能自愈守护系统
echo   github.com/openclaw/openclaw
echo ========================================
echo.
echo 功能说明:
echo - 监控 Gateway 运行状态
echo - 自动诊断和修复常见问题
echo - 掉线后自动重启
echo - 记录完整运行日志
echo.
echo 正在启动守护进程...
echo.

powershell -ExecutionPolicy Bypass -WindowStyle Hidden -File "%~dp0openclaw_auto_healer.ps1"

echo 守护进程已在后台启动
echo 日志位置: %%USERPROFILE%%\.openclaw\logs\auto_healer_*.log
echo.
pause
