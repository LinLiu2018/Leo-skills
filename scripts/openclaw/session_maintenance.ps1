# OpenClaw 会话自动维护脚本
# 功能: 防止会话历史过多导致的 Message ordering conflict

$SESSION_DIR = "$env:USERPROFILE\.openclaw\agents\leo-assistant\sessions"
$MAX_SESSION_SIZE_MB = 10  # 单个会话文件最大 10MB
$MAX_SESSION_AGE_DAYS = 7   # 会话最大保留 7 天

function Write-Log {
    param($Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$timestamp] $Message"
}

# 检查会话目录
if (-not (Test-Path $SESSION_DIR)) {
    Write-Log "会话目录不存在: $SESSION_DIR"
    exit 0
}

$jsonlFiles = Get-ChildItem -Path $SESSION_DIR -Filter "*.jsonl" -ErrorAction SilentlyContinue
$totalCleaned = 0

foreach ($file in $jsonlFiles) {
    $sizeMB = $file.Length / 1MB
    $ageDays = (Get-Date) - $file.LastWriteTime | Select-Object -ExpandProperty TotalDays

    # 清理超大会话文件
    if ($sizeMB -gt $MAX_SESSION_SIZE_MB) {
        Write-Log "清理超大会话: $($file.Name) (${sizeMB:N1} MB)"
        Remove-Item $file.FullName -Force
        $totalCleaned++
        continue
    }

    # 清理过期会话
    if ($ageDays -gt $MAX_SESSION_AGE_DAYS) {
        Write-Log "清理过期会话: $($file.Name) (${ageDays:N0} 天)"
        Remove-Item $file.FullName -Force
        $totalCleaned++
        continue
    }

    # 检查消息数量（超过500条清理）
    $lineCount = (Get-Content $file.FullName | Measure-Object -Line).Lines
    if ($lineCount -gt 500) {
        Write-Log "清理消息过多会话: $($file.Name) ($lineCount 条消息)"
        Remove-Item $file.FullName -Force
        $totalCleaned++
    }
}

# 重置损坏的 sessions.json
$sessionsJson = Join-Path $SESSION_DIR "sessions.json"
if (Test-Path $sessionsJson) {
    try {
        $content = Get-Content $sessionsJson -Raw | ConvertFrom-Json
    } catch {
        Write-Log "sessions.json 损坏，重置为空"
        "[]" | Out-File $sessionsJson -Encoding utf8
    }
}

Write-Log "会话维护完成，清理 $totalCleaned 个会话"

# 如果清理了会话，建议重启网关
if ($totalCleaned -gt 0) {
    Write-Log "建议重启 OpenClaw 网关以应用清理: taskkill /F /IM node.exe && cd D:\openclaw && node openclaw.mjs gateway --port 18789"
}
