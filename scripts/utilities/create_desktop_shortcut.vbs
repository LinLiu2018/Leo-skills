' 创建桌面快捷方式
Set WshShell = CreateObject("WScript.Shell")
DesktopPath = WshShell.SpecialFolders("Desktop")

Set Shortcut = WshShell.CreateShortcut(DesktopPath & "\启动大龙虾.lnk")
Shortcut.TargetPath = "D:\桌面\leo_ai_system\scripts\一键启动大龙虾_带守护.bat"
Shortcut.WorkingDirectory = "D:\桌面\leo_ai_system\scripts"
Shortcut.IconLocation = "C:\Windows\System32\shell32.dll,13"
Shortcut.Description = "一键启动大龙虾网关 + 自动守护进程"
Shortcut.Save

WScript.Echo "桌面快捷方式已创建: " & DesktopPath & "\启动大龙虾.lnk"
