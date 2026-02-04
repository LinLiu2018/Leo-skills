@echo off
chcp 65001 >nul
cls
echo ========================================
echo   安装 OpenClaw 智能守护系统
echo ========================================
echo.

:: 检查管理员权限
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] 需要管理员权限，请右键以管理员身份运行
    pause
    exit /b 1
)

echo [1/3] 创建定时任务...

schtasks /create /tn "OpenClaw_AutoHealer" /tr "powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -File 'D:\桌面\leo_ai_system\scripts\openclaw_auto_healer.ps1'" /sc onstart /delay 0001:00 /f /np /rl HIGHEST 2>nul

if %errorlevel% equ 0 (
    echo     任务创建成功
) else (
    echo     任务可能已存在，尝试更新...
    schtasks /delete /tn "OpenClaw_AutoHealer" /f 2>nul
    schtasks /create /tn "OpenClaw_AutoHealer" /tr "powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -File 'D:\桌面\leo_ai_system\scripts\openclaw_auto_healer.ps1'" /sc onstart /delay 0001:00 /f /np /rl HIGHEST
)

echo.
echo [2/3] 创建开机启动快捷方式...

set "STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "SCRIPT_PATH=D:\桌面\leo_ai_system\scripts\一键启动智能守护.bat"

powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%STARTUP%\OpenClaw智能守护.lnk'); $Shortcut.TargetPath = '%SCRIPT_PATH%'; $Shortcut.WorkingDirectory = 'D:\桌面\leo_ai_system\scripts'; $Shortcut.IconLocation = 'powershell.exe,0'; $Shortcut.Save()"

echo     快捷方式已创建

echo.
echo [3/3] 验证安装...

echo     定时任务:
schtasks /query /tn "OpenClaw_AutoHealer" /fo list | findstr "任务名称"

echo.
echo ========================================
echo   安装完成！
echo ========================================
echo.
echo 启动方式:
echo   1. 立即启动: 运行 "一键启动智能守护.bat"
echo   2. 开机启动: 已设置开机自动运行
echo   3. 查看日志: %%USERPROFILE%%\.openclaw\logs\
echo.
echo 是否需要立即启动守护进程?
set /p choice="启动? (Y/N): "
if /i "%choice%"=="Y" (
    start "" "%~dp0一键启动智能守护.bat"
)

echo.
pause
