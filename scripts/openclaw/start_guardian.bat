@echo off
chcp 65001 >nul
echo Starting OpenClaw Guardian...
powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -File "%~dp0guardian_loop.ps1"
