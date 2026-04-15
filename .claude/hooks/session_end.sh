#!/usr/bin/env bash
# SessionEnd Hook - 会话结束时触发
# 持久化本次会话记忆

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
MEMORY_DIR="$PROJECT_ROOT/leo_knowledge/memory/auto_storage"

mkdir -p "$MEMORY_DIR"

# 获取会话时长
SESSION_ID="${LEO_CURRENT_SESSION_ID:-$(date +%Y%m%d_%H%M%S)}"
SESSION_START="${LEO_SESSION_START_TIME:-$(date -d '1 hour ago' +%Y-%m-%dT%H:%M:%S)}"

# 收集会话统计
SESSION_DURATION=""
if command -v python3 &> /dev/null; then
    SESSION_DURATION=$(python3 -c "
from datetime import datetime
try:
    start = datetime.fromisoformat('$SESSION_START')
    end = datetime.now()
    diff = (end - start).total_seconds()
    print(f'{int(diff // 60)}分钟')
except:
    print('未知')
" 2>/dev/null || echo "未知")
else
    SESSION_DURATION="未知"
fi

# 统计本次会话的日志
TOOL_CALL_COUNT=$(wc -l < "$SCRIPT_DIR/logs/tool_start.log" 2>/dev/null || echo "0")
ERROR_COUNT=$(grep -c "error\|ERROR\|失败" "$SCRIPT_DIR/logs/tool_start.log" 2>/dev/null || echo "0")

# 提取活跃Agents
ACTIVE_AGENTS="claude-code"
if [ -n "$LEO_LAST_SESSION_AGENTS" ]; then
    ACTIVE_AGENTS="$LEO_LAST_SESSION_AGENTS,claude-code"
fi

# 提取本次主题（从最近的日志）
LAST_TOPIC=$(tail -20 "$SCRIPT_DIR/logs/tool_start.log" 2>/dev/null | grep -o "PreToolUse: [^ ]*" | tail -1 | cut -d':' -f2 || echo "general")

# 生成会话摘要
SESSION_SUMMARY=$(cat <<EOF
{
  "session_id": "$SESSION_ID",
  "end_time": "$(date +%Y-%m-%dT%H:%M:%S)",
  "duration": "$SESSION_DURATION",
  "tool_calls": $TOOL_CALL_COUNT,
  "errors": $ERROR_COUNT,
  "active_agents": ["claude-code"],
  "last_topic": "$LAST_TOPIC",
  "language": "${LEO_USER_LANGUAGE:-zh-CN}"
}
EOF
)

# 保存会话摘要
echo "$SESSION_SUMMARY" > "$MEMORY_DIR/last_session_summary.json"

# 归档完整会话（如果会话足够长）
if [ "$TOOL_CALL_COUNT" -gt 10 ]; then
    ARCHIVE_FILE="$MEMORY_DIR/session_${SESSION_ID}.json"
    cat <<EOF > "$ARCHIVE_FILE"
{
  "session_summary": $SESSION_SUMMARY,
  "tool_logs": $(cat "$SCRIPT_DIR/logs/tool_start.log" 2>/dev/null | tail -100 || echo "[]"),
  "timestamp": "$(date +%Y-%m-%dT%H:%M:%S)"
}
EOF
fi

# 更新全局索引
INDEX_FILE="$MEMORY_DIR/memory_index.json"
if [ -f "$INDEX_FILE" ]; then
    # 添加新会话到索引
    python3 -c "
import json
index_file = '$INDEX_FILE'
try:
    with open(index_file, 'r', encoding='utf-8') as f:
        index = json.load(f)
except:
    index = {'sessions': [], 'stats': {}}

summary = json.loads('''$SESSION_SUMMARY''')
index['sessions'].append(summary)
index['sessions'] = index['sessions'][-50:]  # 只保留最近50个会话

with open(index_file, 'w', encoding='utf-8') as f:
    json.dump(index, f, ensure_ascii=False, indent=2)
print('索引已更新')
" 2>/dev/null || echo "索引更新失败"
fi

echo "[SessionEnd] 会话 $SESSION_ID 已保存 | 时长: $SESSION_DURATION | 工具调用: $TOOL_CALL_COUNT"

exit 0