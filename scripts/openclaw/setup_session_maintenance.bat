@echo off
chcp 65001 > nul
echo 设置 OpenClaw 会话自动维护...

:: 创建定时任务，每天凌晨3点运行维护
schtasks /create /tn "OpenClaw-Session-Maintenance" /tr "powershell.exe -ExecutionPolicy Bypass -File D:\桌面\leo_ai_system\scripts\openclaw\session_maintenance.ps1" /sc daily /st 03:00 /f

if %errorlevel% equ 0 (
    echo 定时任务创建成功！每天凌晨3点自动清理会话。
) else (
    echo 定时任务创建失败，可能需要管理员权限。
    echo 请右键以管理员身份运行此脚本。
)

pause
