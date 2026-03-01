@echo off
chcp 65001 >nul
echo 启动 OpenClaw Gateway...
cd /d "D:\moltbot"
node openclaw.mjs gateway --port 18789
