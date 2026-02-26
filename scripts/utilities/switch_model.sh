#!/bin/bash
# Claude 模型切换脚本
# 使用方法: ./switch_model.sh [模型名称]

MODEL_NAME=${1:-"claude-3-5-sonnet"}

# 可用模型列表
case $MODEL_NAME in
    "sonnet"|"claude-3-5-sonnet")
        MODEL="claude-3-5-sonnet"
        ;;
    "haiku"|"claude-3-5-haiku")
        MODEL="claude-3-5-haiku"
        ;;
    "opus"|"claude-3-opus")
        MODEL="claude-3-opus"
        ;;
    "gpt4o"|"gpt-4o")
        MODEL="gpt-4o"
        ;;
    "gpt4o-mini"|"gpt-4o-mini")
        MODEL="gpt-4o-mini"
        ;;
    *)
        echo "❌ 不支持的模型: $MODEL_NAME"
        echo "支持的模型: sonnet, haiku, opus, gpt4o, gpt4o-mini"
        exit 1
        ;;
esac

# 备份当前配置
cp ~/.claude/settings.json ~/.claude/settings.json.backup.$(date +%Y%m%d_%H%M%S)

# 更新配置
sed -i.tmp "s/\"ANTHROPIC_MODEL\": \".*\"/\"ANTHROPIC_MODEL\": \"$MODEL\"/" ~/.claude/settings.json
rm -f ~/.claude/settings.json.tmp

echo "✅ 模型已切换到: $MODEL"
echo "🔄 重启 Claude Code 生效"

# 显示当前配置
echo ""
echo "📋 当前配置:"
grep "ANTHROPIC_MODEL" ~/.claude/settings.json
