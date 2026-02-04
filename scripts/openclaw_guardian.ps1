# OpenClaw (大龙虾) 网关守护进程
# 功能: 监控网关状态，自动重连，记录日志
# 用法: PowerShell -ExecutionPolicy Bypass -File scripts\openclaw_guardian.ps1

param(
    [string]$OpenClawPath = "D:\moltbot",  # OpenClaw 安装目录 (已从 moltbot 重命名为 openclaw)
    [int]$CheckInterval = 30,  # 检查间隔(秒)
    [int]$Port = 18789,
    [string]$LogDir = "$env:USERPROFILE\.openclaw\logs"
)

# 确保日志目录存在
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

$LogFile = Join-Path $LogDir "guardian_$(Get-Date -Format 'yyyyMMdd').log"
$ErrorLogFile = Join-Path $LogDir "error_$(Get-Date -Format 'yyyyMMdd').log"

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"
    Write-Host $logEntry
    Add-Content -Path $LogFile -Value $logEntry
}

function Test-GatewayRunning {
    try {
        $connection = Test-NetConnection -ComputerName 127.0.0.1 -Port $Port -WarningAction SilentlyContinue
        return $connection.TcpTestSucceeded
    } catch {
        return $false
    }
}

function Get-OpenClawProcess {
    return Get-Process -Name "node" -ErrorAction SilentlyContinue | Where-Object {
        $_.CommandLine -like "*openclaw*gateway*"
    }
}

function Fix-Config {
    try {
        Write-Log "检查配置..." "INFO"
        Set-Location $OpenClawPath

        # 只运行 doctor --fix 清理无效配置，不要手动修改 plugins.entries
        $fixResult = & node openclaw.mjs doctor --fix 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Log "配置检查完成" "SUCCESS"
        }

        # 确保 gateway.mode 设置为 local
        & node openclaw.mjs config set gateway.mode local 2>&1 | Out-Null

        return $true
    } catch {
        Write-Log "配置检查异常: $_" "WARN"
        return $false
    }
}

function Start-Gateway {
    try {
        Write-Log "正在启动 OpenClaw Gateway..." "INFO"

        # 先修复配置
        Fix-Config | Out-Null

        # 启动网关（带端口参数）
        $startInfo = New-Object System.Diagnostics.ProcessStartInfo
        $startInfo.FileName = "node"
        $startInfo.Arguments = "openclaw.mjs gateway --port $Port"
        $startInfo.WorkingDirectory = $OpenClawPath
        $startInfo.UseShellExecute = $false
        $startInfo.RedirectStandardOutput = $true
        $startInfo.RedirectStandardError = $true
        $startInfo.CreateNoWindow = $true

        $process = [System.Diagnostics.Process]::Start($startInfo)

        # 等待启动
        Start-Sleep -Seconds 5

        if (Test-GatewayRunning) {
            Write-Log "网关启动成功 (PID: $($process.Id))" "SUCCESS"
            return $true
        } else {
            Write-Log "网关启动失败，端口 $Port 未监听" "ERROR"
            $stderr = $process.StandardError.ReadToEnd()
            if ($stderr) {
                Write-Log "错误输出: $stderr" "ERROR"
                Add-Content -Path $ErrorLogFile -Value "[$(Get-Date)] $stderr"
            }
            return $false
        }
    } catch {
        Write-Log "启动异常: $_" "ERROR"
        Add-Content -Path $ErrorLogFile -Value "[$(Get-Date)] 启动异常: $_"
        return $false
    }
}

function Stop-Gateway {
    $processes = Get-OpenClawProcess
    foreach ($proc in $processes) {
        Write-Log "停止现有网关进程 (PID: $($proc.Id))" "INFO"
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
    }
}

# 主循环
Write-Log "=== OpenClaw 网关守护进程启动 ===" "INFO"
Write-Log "检查间隔: ${CheckInterval}秒, 端口: $Port" "INFO"

$restartCount = 0
$maxRestarts = 5  # 防无限重启

while ($restartCount -lt $maxRestarts) {
    if (-not (Test-GatewayRunning)) {
        Write-Log "网关未运行，尝试重启..." "WARN"
        Stop-Gateway
        Start-Sleep -Seconds 2

        if (Start-Gateway) {
            $restartCount = 0  # 重置计数器
        } else {
            $restartCount++
            Write-Log "重启失败 ($restartCount/$maxRestarts)" "ERROR"
            if ($restartCount -ge $maxRestarts) {
                Write-Log "达到最大重试次数，守护进程退出" "FATAL"
                break
            }
        }
    }

    Start-Sleep -Seconds $CheckInterval
}
