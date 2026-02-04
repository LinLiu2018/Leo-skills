开机自启动设置方法：

方法1: 手动创建快捷方式（推荐）
1. 打开文件夹: D:\桌面\leo_ai_system\scripts\
2. 右键点击 "一键启动大龙虾.bat"
3. 选择 "创建快捷方式"
4. 按 Win + R，输入:
   %USERPROFILE%\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup
5. 把创建的快捷方式拖到这个文件夹

方法2: 使用 PowerShell（管理员运行）
powershell -Command "$s=(New-Object -COM WScript.Shell).CreateShortcut($env:USERPROFILE+'\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\daxlongxia.lnk');$s.TargetPath='D:\桌面\leo_ai_system\scripts\一键启动大龙虾.bat';$s.WorkingDirectory='D:\桌面\leo_ai_system\scripts';$s.Save()"

验证是否设置成功：
1. 打开运行 (Win + R)
2. 输入: shell:startup
3. 查看是否有 "大龙虾" 或 "daxlongxia" 快捷方式
