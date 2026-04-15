@echo off
REM Leo Memory Worker 启动脚本
REM 端口: 37777

cd /d "%~dp0.."

echo Starting Leo Memory Worker...
echo Web UI: http://localhost:37777
echo Press Ctrl+C to stop

python -m src.leo_memory.claude_mem_integration.web_ui --background

echo Memory Worker started in background