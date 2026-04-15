#!/usr/bin/env bash
# UserPromptSubmit Hook - 用户提交输入前触发
# 注入相关记忆上下文

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
MEMORY_DIR="$PROJECT_ROOT/leo_knowledge/memory/auto_storage"

# Claude Code 通过 stdin 传递 JSON
INPUT=$(cat)

# 提取用户输入
USER_INPUT=$(echo "$INPUT" | jq -r '.user_input // empty' 2>/dev/null)

if [ -z "$USER_INPUT" ]; then
    exit 0
fi

# 读取上次会话摘要获取相关上下文
LAST_SUMMARY="$MEMORY_DIR/last_session_summary.json"

if [ -f "$LAST_SUMMARY" ]; then
    LAST_TOPIC=$(cat "$LAST_SUMMARY" | jq -r '.last_topic // "general"' 2>/dev/null)
    LAST_LANG=$(cat "$LAST_SUMMARY" | jq -r '.language // "zh-CN"' 2>/dev/null)

    # 检查用户输入是否与上次主题相关
    echo "[UserPrompt] 主题关联检查: $LAST_TOPIC vs $USER_INPUT" >> "$SCRIPT_DIR/logs/memory_inject.log"

    # 这里可以扩展为向量相似度匹配
    # 简化为关键词匹配
    case "$USER_INPUT" in
        *"$LAST_TOPIC"*)
            # 相关上下文注入提示
            echo "[Context] 检测到与上次会话相关的话题: $LAST_TOPIC" >> "$SCRIPT_DIR/logs/memory_inject.log"
            ;;
    esac
fi

exit 0