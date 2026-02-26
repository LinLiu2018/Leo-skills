# 设置每日记忆同步定时任务
# 运行方式: 以管理员身份运行 PowerShell，执行此脚本

$TaskName = "LeoSystem_DailyMemorySync"
$TaskPath = "D:\桌面\leo_ai_system\scripts\daily_sync.bat"
$Description = "Leo System 每日记忆同步 - 每晚23:00自动同步飞书对话记录"

# 删除已存在的任务
Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue

# 创建触发器 - 每天晚上 23:00
$Trigger = New-ScheduledTaskTrigger -Daily -At "23:00"

# 创建操作
$Action = New-ScheduledTaskAction -Execute $TaskPath -WorkingDirectory "D:\桌面\leo_ai_system"

# 创建设置
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# 注册任务
Register-ScheduledTask -TaskName $TaskName -Trigger $Trigger -Action $Action -Settings $Settings -Description $Description -RunLevel Highest

Write-Host "定时任务已创建: $TaskName"
Write-Host "执行时间: 每天 23:00"
Write-Host "执行脚本: $TaskPath"
Write-Host ""
Write-Host "可以使用以下命令管理任务:"
Write-Host "  查看: Get-ScheduledTask -TaskName $TaskName"
Write-Host "  手动运行: Start-ScheduledTask -TaskName $TaskName"
Write-Host "  删除: Unregister-ScheduledTask -TaskName $TaskName"
