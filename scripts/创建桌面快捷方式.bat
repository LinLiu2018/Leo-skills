@echo off
echo 正在创建桌面快捷方式...

powershell -NoProfile -ExecutionPolicy Bypass -Command "
$WshShell = New-Object -comObject WScript.Shell
$DesktopPath = [Environment]::GetFolderPath('Desktop')
$Shortcut = $WshShell.CreateShortcut(\"$DesktopPath\启动大龙虾.lnk\")
$Shortcut.TargetPath = 'D:\桌面\leo_ai_system\scripts\一键启动大龙虾_带守护.bat'
$Shortcut.WorkingDirectory = 'D:\桌面\leo_ai_system\scripts'
$Shortcut.IconLocation = 'C:\Windows\System32\shell32.dll,13'
$Shortcut.Description = '一键启动大龙虾网关 + 自动守护进程'
$Shortcut.Save()
Write-Host '快捷方式已创建在桌面: 启动大龙虾.lnk' -ForegroundColor Green
"

echo.
pause
