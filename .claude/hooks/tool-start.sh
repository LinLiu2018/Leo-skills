#!/usr/bin/env bash
# ToolStart Hook - 工具执行前触发

# 获取工具名称
TOOL_NAME="$1"

# 记录日志
echo "$(date '+%Y-%m-%d %H:%M:%S') - ToolStart: $TOOL_NAME" >> .claude/hooks/logs/tool_start.log

exit 0
