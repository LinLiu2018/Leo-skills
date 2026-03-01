@echo off
chcp 65001 > nul
echo ========================================
echo 修复 OpenClaw Message Ordering Conflict
echo ========================================
echo.

:: 停止网关
echo [1/4] 停止 OpenClaw 网关...
taskkill /F /IM node.exe 2> nul
ping -n 3 127.0.0.1 > nul

:: 备份并清理会话
echo [2/4] 清理损坏的会话文件...
set SESSION_DIR=%USERPROFILE%\.openclaw\agents\leo-assistant\sessions
set BACKUP_DIR=%USERPROFILE%\.openclaw\agents\leo-assistant\sessions_backup_%date:~0,4%%date:~5,2%%date:~8,2%

if exist "%SESSION_DIR%" (
    mkdir "%BACKUP_DIR%" 2> nul
    xcopy "%SESSION_DIR%\*.jsonl" "%BACKUP_DIR%\" /Y /Q 2> nul
    del /Q "%SESSION_DIR%\*.jsonl" 2> nul
    del /Q "%SESSION_DIR%\*.jsonl.*" 2> nul
    echo [] > "%SESSION_DIR%\sessions.json"
    echo 会话已清理，备份在: %BACKUP_DIR%
) else (
    echo 会话目录不存在，跳过清理
)

echo.
echo [3/4] 验证网关配置...
cd /d D:\openclaw
node openclaw.mjs doctor 2> nul | findstr "Feishu" > nul
if %errorlevel% equ 0 (
    echo 配置检查通过
) else (
    echo 配置可能有异常，请手动检查
)

echo.
echo [4/4] 启动网关...
start /min cmd /c "cd /d D:\openclaw && node openclaw.mjs gateway --port 18789"

echo.
echo 等待网关启动...
ping -n 6 127.0.0.1 > nul

curl -s http://localhost:18789/ > nul
if %errorlevel% equ 0 (
    echo ✅ 网关启动成功！
) else (
    echo ⚠️ 网关可能未启动，请手动检查
)

echo.
echo ========================================
echo 修复完成！请去飞书发送消息测试。
echo 如仍有问题，尝试发送 /new 开始新会话
echo ========================================
pause
