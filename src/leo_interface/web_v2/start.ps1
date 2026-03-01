# Leo AI System Web UI startup script
# Starts frontend (Vite) and backend (FastAPI) for web_v2.
param(
    [switch]$FrontendOnly,
    [switch]$BackendOnly
)

$frontendPort = 5173
$backendPort = 8001
$apiHost = "127.0.0.1"
$workspaceRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path

function Start-Frontend {
    Write-Host "Starting frontend dev server on port $frontendPort..." -ForegroundColor Green
    Start-Process npm -ArgumentList "run", "dev" -WorkingDirectory $PSScriptRoot -NoNewWindow
}

function Start-Backend {
    Write-Host "Starting backend API on $apiHost`:$backendPort..." -ForegroundColor Blue
    $uvicornArgs = @(
        "-m", "uvicorn",
        "src.leo_interface.web_v2.api.main:app",
        "--host", $apiHost,
        "--port", $backendPort
    )
    Start-Process python -ArgumentList $uvicornArgs -WorkingDirectory $workspaceRoot -NoNewWindow
}

function Wait-BackendReady {
    $healthUrl = "http://$apiHost`:$backendPort/"
    for ($i = 0; $i -lt 20; $i++) {
        try {
            $null = Invoke-RestMethod -Uri $healthUrl -TimeoutSec 2
            Write-Host "Backend is ready: $healthUrl" -ForegroundColor Blue
            return
        } catch {
            Start-Sleep -Milliseconds 500
        }
    }
    Write-Host "Backend did not become ready in time: $healthUrl" -ForegroundColor Yellow
}

function Start-Both {
    Start-Frontend
    Start-Sleep -Seconds 2
    Start-Backend
    Wait-BackendReady

    Write-Host "`n======================================" -ForegroundColor Cyan
    Write-Host "Leo AI System Web UI is starting up..." -ForegroundColor Cyan
    Write-Host "======================================" -ForegroundColor Cyan
    Write-Host "Frontend: http://127.0.0.1:$frontendPort" -ForegroundColor Green
    Write-Host "Backend:  http://$apiHost`:$backendPort" -ForegroundColor Blue
    Write-Host "API Docs: http://$apiHost`:$backendPort/docs" -ForegroundColor Yellow
    Write-Host "======================================`n" -ForegroundColor Cyan
}

# Main
if ($FrontendOnly) {
    Start-Frontend
} elseif ($BackendOnly) {
    Start-Backend
    Wait-BackendReady
} else {
    Start-Both
}

Write-Host "Press Ctrl+C to stop all services" -ForegroundColor Gray
