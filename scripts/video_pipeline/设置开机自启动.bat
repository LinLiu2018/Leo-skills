@echo off
chcp 65001 >nul
echo 正在设置视频流水线开机自启动...

set SCRIPT_PATH=%~dp0run_pipeline.bat
set STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup

:: 创建快捷方式到启动文件夹
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%STARTUP_DIR%\视频流水线.lnk'); $Shortcut.TargetPath = '%SCRIPT_PATH%'; $Shortcut.WorkingDirectory = '%~dp0'; $Shortcut.Save()"

echo ✅ 开机自启动已设置
echo 启动命令: %STARTUP_DIR%\视频流水线.lnk
pause
