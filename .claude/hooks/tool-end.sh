#!/usr/bin/env bash
# ToolEnd Hook - 工具执行后触发

# 获取工具名称和执行结果
TOOL_NAME="$1"
RESULT="$2"

# 记录日志
echo "$(date '+%Y-%m-%d %H:%M:%S') - ToolEnd: $TOOL_NAME (exit: $?)" >> .claude/hooks/logs/tool_end.log

exit 0
