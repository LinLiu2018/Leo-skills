#!/usr/bin/env bash
# PreToolUse Hook - 工具执行前触发
# Claude Code 通过 stdin 传递 JSON 数据

INPUT=$(cat)
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // empty')
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

if [ -n "$TOOL_NAME" ]; then
  echo "$(date '+%Y-%m-%d %H:%M:%S') - PreToolUse: $TOOL_NAME" >> .claude/hooks/logs/tool_start.log
fi

exit 0
