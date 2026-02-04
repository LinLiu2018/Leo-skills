@echo off
chcp 65001 >nul
echo ============================================
echo    每日全球商业情报定时推送
echo    定时任务: 每天 08:00 自动执行
echo ============================================
echo.

REM 设置时间格式
set TIME_FORMAT=%time:~0,5%
echo 当前时间: %TIME_FORMAT%

REM 进入项目目录
cd /d "d:\桌面\leo_ai_system"

REM 检查并安装依赖
pip show requests >nul 2>&1
if errorlevel 1 (
    echo [1/3] 安装依赖 requests...
    pip install requests -q
)

echo [2/3] 生成并发送全球商业情报...
python scripts/send_daily_intelligence.py

echo.
echo [3/3] 任务完成
echo ============================================

pause
