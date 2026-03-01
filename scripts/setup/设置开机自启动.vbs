' 设置大龙虾开机自启动
Set WshShell = CreateObject("WScript.Shell")
Set Shortcut = WshShell.CreateShortcut( _
    WshShell.SpecialFolders("Startup") & "\大龙虾.lnk")

Shortcut.TargetPath = "D:\桌面\leo_ai_system\scripts\一键启动大龙虾.bat"
Shortcut.WorkingDirectory = "D:\桌面\leo_ai_system\scripts"
Shortcut.Description = "大龙虾飞书网关"
Shortcut.Save

WScript.Echo "✅ 已设置开机自启动！"
WScript.Quit
