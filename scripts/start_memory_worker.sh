#!/bin/bash
# Leo Memory Worker 启动脚本
# 端口: 37777

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

echo "🧠 Starting Leo Memory Worker..."
echo "   Web UI: http://localhost:37777"
echo "   API: http://localhost:37777/api/"
echo ""

# 设置Python路径
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

# 启动Worker
python -m src.leo_memory.claude_mem_integration.web_ui --background --port 37777

echo "✅ Memory Worker started in background"
echo "   Run 'python -m src.leo_memory.claude_mem_integration.web_ui' to see logs"