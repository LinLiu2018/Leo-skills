# OpenClaw 守护进程启动器
# 双层守护：1.开机启动 2.持续监控

# 不要用 Stop，否则任何异常都会终止守护进程
$ErrorActionPreference = "Continue"

# 配置
$OpenClawPath = "D:\openclaw"
$Port = 18789
$CheckInterval = 30  # 每30秒检查一次
$MaxRestartAttempts = 3

$LogDir = "$env:USERPROFILE\.openclaw\logs"
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}
$LogFile = Join-Path $LogDir "guardian_$(Get-Date -Format 'yyyyMMdd').log"

function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] $Message"
    Write-Host $logEntry
    Add-Content -Path $LogFile -Value $logEntry -Encoding UTF8
}

function Test-GatewayRunning {
    try {
        $tcp = Test-NetConnection -ComputerName 127.0.0.1 -Port $Port -WarningAction SilentlyContinue
        return $tcp.TcpTestSucceeded
    } catch {
        return $false
    }
}

function Start-Gateway {
    Write-Log "Starting OpenClaw Gateway..."
    $process = Start-Process -FilePath "node" `
        -ArgumentList "openclaw.mjs","gateway","--port","$Port" `
        -WorkingDirectory $OpenClawPath `
        -PassThru `
        -WindowStyle Hidden

    if ($process) {
        Write-Log "Gateway started with PID: $($process.Id)"
        return $process.Id
    } else {
        Write-Log "Failed to start gateway"
        return $null
    }
}

# 主循环
Write-Log "=== OpenClaw Guardian Started ==="
Write-Log "Monitoring port $Port every $CheckInterval seconds"

$restartCount = 0

while ($true) {
    try {
        $isRunning = $false
        try {
            $isRunning = Test-GatewayRunning
        } catch {
            Write-Log "Health check error: $($_.Exception.Message)"
            $isRunning = $false
        }

        if (-not $isRunning) {
            Write-Log "Gateway not responding, attempting restart..."

            # 尝试启动网关
            $started = $null
            try {
                $started = Start-Gateway
            } catch {
                Write-Log "Start error: $($_.Exception.Message)"
            }

            if ($started) {
                $restartCount++
                Write-Log "Restart attempt $restartCount successful"

                # 等待网关启动
                Start-Sleep -Seconds 5

                # 验证是否真的启动成功
                try {
                    if (Test-GatewayRunning) {
                        Write-Log "Gateway is now running"
                        $restartCount = 0  # 重置计数
                    } else {
                        Write-Log "Gateway started but not responding"
                    }
                } catch {
                    Write-Log "Verify error: $($_.Exception.Message)"
                }
            }

            if ($restartCount -ge $MaxRestartAttempts) {
                Write-Log "Max restart attempts reached, waiting 60 seconds..."
                Start-Sleep -Seconds 60
                $restartCount = 0
            }
        }
    } catch {
        # 最外层兜底，确保守护进程永不退出
        Write-Log "Unexpected error (guardian continues): $($_.Exception.Message)"
    }

    Start-Sleep -Seconds $CheckInterval
}
