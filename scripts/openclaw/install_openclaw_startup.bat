@echo off
REM OpenClaw Gateway 开机自启脚本（静默启动）
REM 注意: 此版本仅启动 Gateway，不包含守护进程
REM 如需守护进程自动恢复，请运行 openclaw_guardian.ps1
REM 用法: 双击安装开机自启，或直接运行启动

chcp 65001 >nul
echo ========================================
REM 检查是否以管理员权限运行
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] 建议以管理员权限运行此脚本
    echo.
)

REM 创建启动目录快捷方式
set "StartupDir=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "ScriptPath=%~dp0start_gateway_silent.bat"
set "LnkPath=%StartupDir%\OpenClaw Guardian.lnk"

echo [1/2] 检查启动目录...
if not exist "%StartupDir%" (
    mkdir "%StartupDir%" 2>nul
)

echo [2/2] 创建开机自启快捷方式...
REM 使用 PowerShell 创建快捷方式
powershell -Command "$s = (New-Object -COM WScript.Shell).CreateShortcut('%LnkPath%'); $s.TargetPath = 'powershell.exe'; $s.Arguments = '-ExecutionPolicy Bypass -File \"%ScriptPath%\"'; $s.WorkingDirectory = '%~dp0'; $s.Description = 'OpenClaw Gateway Guardian'; $s.Save()"

if exist "%LnkPath%" (
    echo.
    echo [OK] 开机自启已安装！
    echo    快捷方式: %LnkPath%
    echo.
    echo 电脑重启后，OpenClaw Gateway 将自动启动
) else (
    echo [!] 快捷方式创建失败，请手动操作
    echo    手动操作: 将快捷方式放入 %StartupDir%
)

echo.
pause
