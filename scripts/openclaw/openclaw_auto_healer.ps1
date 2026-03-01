# OpenClaw (大龙虾) 智能自愈守护系统 v2.1
# 功能: 监控网关状态、自动诊断问题、智能修复、自动重启
# 修复记录: 2026-02-02 - 移除 plugins.entries 修改逻辑（OpenClaw 自动管理）
# 用法: PowerShell -ExecutionPolicy Bypass -File scripts\openclaw_auto_healer.ps1

param(
    [string]$OpenClawPath = "D:\openclaw",
    [int]$CheckInterval = 30,
    [int]$Port = 18789,
    [string]$LogDir = "$env:USERPROFILE\.openclaw\logs",
    [string]$ConfigPath = "$env:USERPROFILE\.openclaw\openclaw.json"
)

# 确保日志目录
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

$LogFile = Join-Path $LogDir "auto_healer_$(Get-Date -Format 'yyyyMMdd').log"
$StateFile = Join-Path $LogDir ".healer_state.json"

# 状态跟踪
$global:state = @{
    restartCount = 0
    lastRestart = $null
    consecutiveFailures = 0
}

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"
    Write-Host $logEntry
    Add-Content -Path $LogFile -Value $logEntry -Encoding UTF8
}

function Save-State {
    $global:state | ConvertTo-Json | Out-File $StateFile -Encoding UTF8
}

function Load-State {
    if (Test-Path $StateFile) {
        try {
            $saved = Get-Content $StateFile -Raw | ConvertFrom-Json
            $global:state.restartCount = $saved.restartCount
        } catch {}
    }
}

function Test-GatewayHealth {
    try {
        $tcp = Test-NetConnection -ComputerName 127.0.0.1 -Port $Port -WarningAction SilentlyContinue
        return $tcp.TcpTestSucceeded
    } catch {
        return $false
    }
}

function Get-GatewayProcess {
    Get-Process -Name "node" -ErrorAction SilentlyContinue | Where-Object {
        $_.CommandLine -like "*openclaw*"
    }
}

function Stop-Gateway {
    Write-Log "Stopping existing Gateway processes..." "WARN"
    Get-GatewayProcess | ForEach-Object {
        try {
            Stop-Process -Id $_.Id -Force
            Write-Log "Stopped PID: $($_.Id)" "SUCCESS"
            Start-Sleep -Seconds 2
        } catch {
            Write-Log "Failed to stop PID: $($_.Id)" "ERROR"
        }
    }
}

function Invoke-SmartHeal {
    Write-Log "Starting smart diagnosis and repair..." "HEAL"
    $healSteps = @()

    # Step 1: Check config file
    Write-Log "[Diagnosis 1/5] Checking configuration..." "HEAL"
    if (Test-Path $ConfigPath) {
        try {
            $config = Get-Content $ConfigPath -Raw | ConvertFrom-Json

            # FIXED: Never touch plugins.entries - it's managed by OpenClaw itself
            # The old code that added feishu to plugins.entries was the bug root cause
            Write-Log "  Skipping plugins.entries (OpenClaw manages this)" "INFO"

            # Ensure channels.feishu exists (this is correct - channels are user config)
            if (-not $config.channels.feishu) {
                Write-Log "  Issue found: channels.feishu missing" "WARN"
                $config.channels = @{
                    feishu = @{
                        enabled = $true
                        appId = "cli_a9f18849edbb9cb1"
                        appSecret = "UUNNVCiRRheoPkdnKPeVycYTTlVQ8emS"
                        domain = "feishu"
                        connectionMode = "websocket"
                        dmPolicy = "open"
                        groupPolicy = "open"
                        requireMention = $false
                    }
                }
                $healSteps += "Restore channels.feishu"
            }

            $config | ConvertTo-Json -Depth 10 | Out-File $ConfigPath -Encoding UTF8
            Write-Log "  Configuration verified" "SUCCESS"
        } catch {
            Write-Log "  Config check failed: $_" "ERROR"
        }
    }

    # Step 2: Check gateway.cmd
    Write-Log "[Diagnosis 2/5] Checking startup script..." "HEAL"
    $gatewayCmd = "$env:USERPROFILE\.openclaw\gateway.cmd"
    if (Test-Path $gatewayCmd) {
        $cmdContent = Get-Content $gatewayCmd -Raw
        if ($cmdContent -match "dist[/\\]index\.js") {
            Write-Log "  Issue found: gateway.cmd points to old path" "WARN"
            $fixedContent = '@echo off' + "`r`n" +
                'rem OpenClaw Gateway (v2026.1.30) - Auto Healed' + "`r`n" +
                'set OPENCLAW_GATEWAY_PORT=18789' + "`r`n" +
                'set OPENCLAW_GATEWAY_TOKEN=%OPENCLAW_GATEWAY_TOKEN%' + "`r`n" +
                'set MINIMAX_API_KEY=%MINIMAX_API_KEY%' + "`r`n" +
                '"C:\Program Files\nodejs\node.exe" "D:\openclaw\openclaw.mjs" gateway --port 18789'
            $fixedContent | Out-File $gatewayCmd -Encoding UTF8
            Write-Log "  gateway.cmd fixed" "SUCCESS"
            $healSteps += "Fix gateway.cmd"
        }
    }

    # Step 3: Check OpenClaw files
    Write-Log "[Diagnosis 3/5] Checking OpenClaw installation..." "HEAL"
    $openclawMjs = Join-Path $OpenClawPath "openclaw.mjs"
    if (-not (Test-Path $openclawMjs)) {
        Write-Log "  Error: openclaw.mjs not found!" "ERROR"
        return $false
    }
    Write-Log "  OpenClaw installation OK" "SUCCESS"

    # Step 4: Clean zombie processes
    Write-Log "[Diagnosis 4/5] Cleaning zombie processes..." "HEAL"
    Get-Process -Name "node" -ErrorAction SilentlyContinue | Where-Object {
        $_.StartTime -lt (Get-Date).AddMinutes(-10) -and $_.CommandLine -like "*openclaw*"
    } | ForEach-Object {
        Stop-Process -Id $_.Id -Force
        Write-Log "  Cleaned zombie PID: $($_.Id)" "SUCCESS"
        $healSteps += "Clean zombie process"
    }

    if ($healSteps.Count -gt 0) {
        Write-Log "Repair completed: $($healSteps -join ', ')" "SUCCESS"
    }

    return $true
}

function Start-GatewayWithRetry {
    param([int]$MaxRetries = 3)

    for ($i = 1; $i -le $MaxRetries; $i++) {
        Write-Log "Attempting to start Gateway ($i/$MaxRetries)..." "INFO"

        try {
            $startInfo = New-Object System.Diagnostics.ProcessStartInfo
            $startInfo.FileName = "node"
            $startInfo.Arguments = "openclaw.mjs gateway --port $Port"
            $startInfo.WorkingDirectory = $OpenClawPath
            $startInfo.UseShellExecute = $false
            $startInfo.RedirectStandardOutput = $true
            $startInfo.RedirectStandardError = $true
            $startInfo.CreateNoWindow = $true

            $process = [System.Diagnostics.Process]::Start($startInfo)
            Start-Sleep -Seconds 5

            if (Test-GatewayHealth) {
                Write-Log "Gateway started successfully! PID: $($process.Id)" "SUCCESS"
                $global:state.consecutiveFailures = 0
                $global:state.lastRestart = Get-Date
                $global:state.restartCount++
                Save-State
                return $true
            } else {
                Write-Log "Gateway failed to start, port not listening" "WARN"
                Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
                Start-Sleep -Seconds 3
            }
        } catch {
            Write-Log "Start exception: $_" "ERROR"
            Start-Sleep -Seconds 3
        }
    }

    Write-Log "Start failed after max retries" "ERROR"
    return $false
}

# ========== Main Program ==========

Write-Log "================================" "INFO"
Write-Log " OpenClaw Auto Healer v2.0" "INFO"
Write-Log "================================" "INFO"
Write-Log "Check interval: ${CheckInterval}s" "INFO"
Write-Log "Config path: $ConfigPath" "INFO"
Write-Log "================================" "INFO"

Load-State

# Initial check
if (-not (Test-GatewayHealth)) {
    Write-Log "Initial state: Gateway not running, starting repair..." "WARN"
    Stop-Gateway
    Invoke-SmartHeal | Out-Null
    Start-GatewayWithRetry
} else {
    Write-Log "Initial state: Gateway is healthy" "SUCCESS"
}

# Main loop
while ($true) {
    Start-Sleep -Seconds $CheckInterval

    $healthy = Test-GatewayHealth

    if (-not $healthy) {
        $global:state.consecutiveFailures++
        Write-Log "Gateway anomaly detected (consecutive: $($global:state.consecutiveFailures))" "WARN"

        if ($global:state.consecutiveFailures -ge 2) {
            Write-Log "Triggering smart repair..." "HEAL"
            Stop-Gateway
            Invoke-SmartHeal | Out-Null

            if (Start-GatewayWithRetry) {
                Write-Log "Gateway restored!" "SUCCESS"
            } else {
                Write-Log "Gateway repair failed, will retry next check" "ERROR"
                if ($global:state.consecutiveFailures -gt 10) {
                    Write-Log "Too many failures, entering cooldown (60s)" "WARN"
                    Start-Sleep -Seconds 60
                }
            }
        } else {
            Write-Log "Brief anomaly, trying quick restart..." "WARN"
            Stop-Gateway
            Start-GatewayWithRetry -MaxRetries 2 | Out-Null
        }
    } else {
        if ($global:state.consecutiveFailures -gt 0) {
            $global:state.consecutiveFailures = 0
            Save-State
            Write-Log "Gateway recovered" "SUCCESS"
        }
    }
}
