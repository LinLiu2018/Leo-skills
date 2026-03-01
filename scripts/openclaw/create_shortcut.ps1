$WshShell = New-Object -comObject WScript.Shell
$StartupPath = [Environment]::GetFolderPath('Startup')
$Shortcut = $WshShell.CreateShortcut("$StartupPath\OpenClaw_AutoHealer.lnk")
$Shortcut.TargetPath = "powershell.exe"
$Shortcut.Arguments = '-ExecutionPolicy Bypass -WindowStyle Hidden -File "D:\桌面\leo_ai_system\scripts\openclaw\openclaw_auto_healer.ps1"'
$Shortcut.WorkingDirectory = "D:\桌面\leo_ai_system\scripts\openclaw"
$Shortcut.Description = "OpenClaw Auto Healer"
$Shortcut.Save()
Write-Host "Shortcut created at: $StartupPath\OpenClaw_AutoHealer.lnk"
