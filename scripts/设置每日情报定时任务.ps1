# 设置 Windows 定时任务 - 每日全球商业情报推送

$TaskName = "Leo每日情报推送"
$ScriptPath = "d:\桌面\leo_ai_system\scripts\每日情报定时推送.bat"
$TriggerTime = "08:00"  # 每天早上8点

echo "============================================"
echo "   Leo AI System - 每日情报定时推送设置"
echo "============================================"
echo ""
echo "任务名称: $TaskName"
echo "执行脚本: $ScriptPath"
echo "执行时间: 每天 $TriggerTime"
echo ""

# 检查是否需要管理员权限
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    echo "[!] 建议以管理员身份运行此脚本"
    echo ""
}

# 创建定时任务
$Action = New-ScheduledTaskAction -Execute $ScriptPath
$Trigger = New-ScheduledTaskTrigger -Daily -At $TriggerTime
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

try {
    Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Description "每日全球商业情报推送 via Leo AI System" -ErrorAction Stop
    echo "[OK] 定时任务创建成功!"
    echo ""
} catch {
    echo "[!] 任务已存在或创建失败: $_"
    echo ""
    echo "尝试更新现有任务..."
    try {
        Set-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger
        echo "[OK] 任务更新成功!"
    } catch {
        echo "[!] 更新失败: $_"
    }
}

echo ""
echo "============================================"
echo "验证任务状态:"
schtasks /query /tn "$TaskName" /fo list | findstr "状态"
echo "============================================"
echo ""
echo "手动设置方法:"
echo "1. 打开 任务计划程序 (taskschd.msc)"
echo "2. 创建基本任务"
echo "3. 名称: Leo每日情报推送"
echo "4. 触发器: 每天 08:00"
echo "5. 操作: 启动程序 - 选择上述 bat 文件"
echo "============================================"

pause
