$WshShell = New-Object -comObject WScript.Shell
$StartupPath = [Environment]::GetFolderPath('Startup')
$ShortcutPath = "$StartupPath\OpenClaw_AutoHealer.lnk"

# Delete old shortcut
if (Test-Path $ShortcutPath) {
    Remove-Item $ShortcutPath -Force
}

# Create new shortcut to guardian_loop.ps1
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = "powershell.exe"
$Shortcut.Arguments = '-ExecutionPolicy Bypass -WindowStyle Hidden -File "D:\桌面\leo_ai_system\scripts\openclaw\guardian_loop.ps1"'
$Shortcut.WorkingDirectory = "D:\桌面\leo_ai_system\scripts\openclaw"
$Shortcut.Description = "OpenClaw Guardian - Auto restart gateway"
$Shortcut.Save()
Write-Host "Shortcut updated at: $ShortcutPath"
