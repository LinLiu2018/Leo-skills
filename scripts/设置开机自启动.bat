@echo off
chcp 65001 >nul

echo ========================================
echo   🚀 设置大龙虾开机自启动
echo ========================================
echo.

set SCRIPT_PATH=%~dp0一键启动大龙虾.bat
set SHORTCUT_PATH=%USERPROFILE%\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\大龙虾.lnk

echo 脚本路径: %SCRIPT_PATH%
echo 快捷方式: %SHORTCUT_PATH%
echo.

REM 创建 PowerShell 脚用来创建快捷方式
echo $WshShell = New-Object -ComObject WScript.Shell > "%TEMP%\create_shortcut.ps1"
echo $Shortcut = $WshShell.CreateShortcut("%SHORTCUT_PATH%") >> "%TEMP%\create_shortcut.ps1"
echo $Shortcut.TargetPath = "cmd.exe" >> "%TEMP%\create_shortcut.ps1"
echo $Shortcut.Arguments = "/c ""%SCRIPT_PATH%""" >> "%TEMP%\create_shortcut.ps1"
echo $Shortcut.WorkingDirectory = "%~dp0" >> "%TEMP%\create_shortcut.psell
echo $Shortcut.Description = "大龙虾飞书网关" >> "%TEMP%\create_shortcut.ps1"
echo $Shortcut.Save() >> "%TEMP%\create_shortcut.ps1"

echo 正在创建快捷方式...
powershell -ExecutionPolicy Bypass -File "%TEMP%\create_shortcut.ps1" 2>nul

if exist "%SHORTCUT_PATH%" (
    echo.
    echo ✅ 已成功设置开机自启动！
    echo.
    echo 电脑开机后大龙虾将自动运行。
    echo.
    echo 快捷方式位置:
    echo %SHORTCUT_PATH%
) else (
    echo.
    echo ⚠️  设置失败，请手动创建快捷方式。
)

echo.
pause
