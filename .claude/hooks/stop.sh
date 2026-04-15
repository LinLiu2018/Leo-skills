#!/usr/bin/env bash
# Stop Hook - 会话停止时触发
# 生成会话摘要

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
MEMORY_DIR="$PROJECT_ROOT/leo_knowledge/memory/auto_storage"

mkdir -p "$MEMORY_DIR"

# 读取会话统计
SESSION_ID="${LEO_CURRENT_SESSION_ID:-$(date +%Y%m%d_%H%M%S)}"

# 生成Stop摘要
STOP_SUMMARY=$(cat <<EOF
{
  "event": "stop",
  "session_id": "$SESSION_ID",
  "timestamp": "$(date +%Y-%m-%dT%H:%M:%S)",
  "summary_reason": "用户请求停止"
}
EOF
)

# 更新会话摘要
LAST_SUMMARY="$MEMORY_DIR/last_session_summary.json"
if [ -f "$LAST_SUMMARY" ]; then
    python3 -c "
import json
summary_file = '$LAST_SUMMARY'
try:
    with open(summary_file, 'r', encoding='utf-8') as f:
        summary = json.load(f)
    summary['stopped_at'] = '$(date +%Y-%m-%dT%H:%M:%S)'
    summary['stop_event'] = True
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
except Exception as e:
    print(f'更新失败: {e}')
" 2>/dev/null
fi

echo "[Stop] 会话 $SESSION_ID 停止"

exit 0