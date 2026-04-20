#!/usr/bin/env bash
# PostToolUse Hook - 工具执行后触发
# Claude Code 通过 stdin 传递 JSON 数据

INPUT=$(cat)
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // empty')
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

if [ -n "$TOOL_NAME" ]; then
  echo "$(date '+%Y-%m-%d %H:%M:%S') - PostToolUse: $TOOL_NAME" >> .claude/hooks/logs/tool_end.log
fi

exit 0
