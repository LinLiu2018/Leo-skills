@echo off
chcp 65001 >nul
echo ========================================
echo   📝 飞书对话日志查看器
echo ========================================
echo.
echo 选择要查看的日志:
echo.
echo [1] 今日日志
echo [2] 昨日日志
echo [3] 最近7天统计
echo [4] 查看索引
echo [0] 退出
echo.
set /p choice="请选择 (0-4): "

if "%choice%"=="1" (
    for /f "tokens=2 delims==" %%a in ('wmic os get localdatetime /value') do set dt=%%a
    set dateStr=%dt:~0,4%-%dt:~4,2%-%dt:~6,2%
    if exist "logs\feishu\dialogue_%dateStr%.md" (
        echo.
        echo ========== 今日日志 (%dateStr%) ==========
        type "logs\feishu\dialogue_%dateStr%.md"
    ) else (
        echo.
        echo 今日暂无日志记录
    )
) else if "%choice%"=="2" (
    echo.
    echo 请输入日期 (YYYY-MM-DD):
    set /p dateStr="日期: "
    if exist "logs\feishu\dialogue_%dateStr%.md" (
        echo.
        echo ========== 日志 (%dateStr%) ==========
        type "logs\feishu\dialogue_%dateStr%.md"
    ) else (
        echo.
        echo 日志文件不存在
    )
) else if "%choice%"=="3" (
    echo.
    echo ========== 统计 ==========
    echo.
    for %%f in (logs\feishu\dialogue_*.md) do (
        for %%a in (%%f) do (
            echo %%~nxf
        )
    )
) else if "%choice%"=="4" (
    if exist "logs\feishu\index.md" (
        echo.
        echo ========== 对话索引 ==========
        type "logs\feishu\index.md"
    ) else (
        echo.
        echo 索引文件不存在
    )
)

echo.
pause
