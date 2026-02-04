@echo off
chcp 65001 >nul
cls
echo ========================================
echo   OpenClaw Gateway 状态检查
echo ========================================
echo.

echo [1/4] 检查端口 18789...
netstat -ano | findstr "18789" >nul
if %errorlevel% equ 0 (
    echo     状态: 监听中
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr "18789"') do (
        echo     PID: %%a
        tasklist | findstr "%%a" | findstr "node" >nul
        if !errorlevel! equ 0 (
            echo     进程: node.exe (正常)
        )
    )
) else (
    echo     状态: 未监听 (异常!)
)

echo.
echo [2/4] 检查进程...
tasklist | findstr "node" | findstr /i "openclaw" >nul
if %errorlevel% equ 0 (
    echo     node.exe 进程: 运行中
) else (
    echo     node.exe 进程: 未找到
)

echo.
echo [3/4] 检查飞书 WebSocket...
findstr /c:"ws client ready" "%USERPROFILE%\.openclaw\gateway.log" >nul 2>nul
if %errorlevel% equ 0 (
    echo     WebSocket: 已连接
) else (
    echo     WebSocket: 未连接或日志不存在
)

echo.
echo [4/4] 检查守护进程...
tasklist | findstr "powershell" | findstr /i "healer" >nul
if %errorlevel% equ 0 (
    echo     守护进程: 运行中
) else (
    echo     守护进程: 未运行
)

echo.
echo ========================================
echo   最近日志 (最后5行)
echo ========================================
if exist "%USERPROFILE%\.openclaw\logs\auto_healer_*.log" (
    powershell -Command "Get-ChildItem '%USERPROFILE%\.openclaw\logs\auto_healer_*.log' | Sort-Object LastWriteTime -Descending | Select-Object -First 1 | Get-Content -Tail 5"
) else (
    echo     暂无守护日志
)

echo.
echo ========================================
pause
