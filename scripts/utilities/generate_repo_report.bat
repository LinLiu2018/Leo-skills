@echo off
chcp 65001 >nul
echo ========================================
echo   核心仓库周报生成器
echo   监控: Claude Code + OpenClaw
echo ========================================
echo.

cd /d "D:\桌面\leo_ai_system"

echo [1/2] 生成周报...
python -c "from src.leo_skills.tools.repo_watch_skill import generate_weekly_report; result = generate_weekly_report(); print(result.get('report', 'Error generating report'))"

echo.
echo [2/2] 报告已生成
echo 报告位置: logs\repo_watch\report_*.md
echo.
pause
