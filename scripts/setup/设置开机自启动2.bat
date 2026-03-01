@echo off
chcp 65001 >nul
echo ========================================
echo   🚀 设置大龙虾开机自启动
echo ========================================
echo.

set "SCRIPT_DIR=D:\桌面\leo_ai_system\scripts"
set "TARGET_BAT=%SCRIPT_DIR%\一键启动大龙虾.bat"
set "SHORTCUT_DIR=%USERPROFILE%\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup"
set "SHORTCUT=%SHORTCUT_DIR%\大龙虾.lnk"

echo 目标脚本: %TARGET_BAT%
echo 快捷方式: %SHORTCUT%
echo.

REM 使用 PowerShell 创建快捷方式
powershell -Command ^
    "$s = (New-Object -COM WScript.Shell).CreateShortcut('%SHORTCUT%');" ^
    "$s.TargetPath = '%TARGET_BAT%';" ^
    "$s.WorkingDirectory = '%SCRIPT_DIR%';" ^
    "$s.Description = '大龙虾飞书网关';" ^
    "$s.Save();"

if exist "%SHORTCUT%" (
    echo.
    echo ✅ 已成功设置开机自启动！
    echo.
    echo 电脑开机后大龙虾将自动运行。
) else (
    echo.
    echo ⚠️  设置失败，请手动创建快捷方式：
    echo    1. 右键 "一键启动大龙虾.bat"
    echo    2. 选择 "创建快捷方式"
    echo    3. 把快捷方式拖到 "启动" 文件夹
)

echo.
pause
