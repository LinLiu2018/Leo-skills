@echo off
chcp 65001 >nul
cd /d "%~dp0..\.."
python scripts/video_pipeline/run_pipeline.py --watch D:/video_pipeline/watch
pause
