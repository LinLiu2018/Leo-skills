#!/usr/bin/env bash
# SessionStart Hook - 会话启动时触发
# 加载历史记忆，注入上下文到环境变量

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
MEMORY_DIR="$PROJECT_ROOT/leo_knowledge/memory/auto_storage"

# 创建记忆目录
mkdir -p "$MEMORY_DIR"

# 检查是否有上次会话的摘要
LAST_SESSION_FILE="$MEMORY_DIR/last_session_summary.json"
CONTEXT_INJECT=""

if [ -f "$LAST_SESSION_FILE" ]; then
    # 读取上次会话摘要
    LAST_TOPIC=$(cat "$LAST_SESSION_FILE" 2>/dev/null | grep -o '"last_topic":"[^"]*"' | cut -d'"' -f4 || echo "")
    LAST_AGENTS=$(cat "$LAST_SESSION_FILE" 2>/dev/null | grep -o '"active_agents":\[[^]]*\]' | cut -d'[' -f2 | cut -d']' -f1 | tr ',' '\n' | tr -d '"' | head -5 || echo "")

    if [ -n "$LAST_TOPIC" ]; then
        CONTEXT_INJECT="[记忆系统] 上次会话主题: $LAST_TOPIC"
    fi

    # 写入环境变量供后续Hook使用
    export LEO_LAST_SESSION_TOPIC="$LAST_TOPIC"
    export LEO_LAST_SESSION_AGENTS="$LAST_AGENTS"
fi

# 加载用户偏好
USER_PREFS="$PROJECT_ROOT/leo_knowledge/context/user_profile.json"
if [ -f "$USER_PREFS" ]; then
    USER_LANG=$(cat "$USER_PREFS" 2>/dev/null | grep -o '"language":"[^"]*"' | cut -d'"' -f4 || echo "zh-CN")
    export LEO_USER_LANGUAGE="$USER_LANG"
fi

# 初始化会话记录
SESSION_ID=$(date +%Y%m%d_%H%M%S)
export LEO_CURRENT_SESSION_ID="$SESSION_ID"

echo "[SessionStart] 会话ID: $SESSION_ID, 上下文: $CONTEXT_INJECT"

exit 0