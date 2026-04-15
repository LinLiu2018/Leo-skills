#!/usr/bin/env bash
# PostToolUse Hook - 工具执行后触发
# 记录工具调用结果到记忆系统

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
MEMORY_DIR="$PROJECT_ROOT/leo_knowledge/memory/auto_storage"

mkdir -p "$SCRIPT_DIR/logs"

# Claude Code 通过 stdin 传递 JSON
INPUT=$(cat)

# 提取工具信息
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // empty')
TOOL_INPUT=$(echo "$INPUT" | jq -r '.tool_input // empty' 2>/dev/null)
ERROR=$(echo "$INPUT" | jq -r '.error // empty' 2>/dev/null)
RESULT=$(echo "$INPUT" | jq -r '.result // empty' 2>/dev/null)

if [ -z "$TOOL_NAME" ]; then
    exit 0
fi

# 记录到工具日志
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

if [ -n "$ERROR" ]; then
    echo "$TIMESTAMP - [ERROR] $TOOL_NAME: $ERROR" >> "$SCRIPT_DIR/logs/tool_results.log"
else
    # 截断过长结果
    RESULT_SHORT=$(echo "$RESULT" | head -c 200 2>/dev/null || echo "")
    echo "$TIMESTAMP - [OK] $TOOL_NAME" >> "$SCRIPT_DIR/logs/tool_results.log"
fi

# 如果是文件修改类工具，记录变更
case "$TOOL_NAME" in
    *Write*|*Edit*|*Bash*)
        if [ -n "$TOOL_INPUT" ]; then
            echo "$TIMESTAMP - $TOOL_NAME: $(echo "$TOOL_INPUT" | head -c 100)" >> "$MEMORY_DIR/recent_changes.log"
        fi
        ;;
esac

exit 0