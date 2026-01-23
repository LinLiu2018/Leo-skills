#!/bin/bash
# Leo AI Agent System - 多AI协作启动脚本
# ================================================

echo "🚀 Leo AI Agent System - 多AI协作环境启动"
echo "=================================================="

# 检查Claude Code状态
echo "📊 检查Claude Code状态..."
if command -v claude &> /dev/null; then
    echo "✅ Claude Code 已安装"
    claude --version
else
    echo "❌ Claude Code 未安装，请先安装Claude Code"
    exit 1
fi

# 检查OpenCode状态
echo "📊 检查OpenCode状态..."
if command -v opencode &> /dev/null; then
    echo "✅ OpenCode 已安装"
    opencode --version 2>/dev/null || echo "版本信息不可用"
else
    echo "⚠️  OpenCode 未安装，建议安装以获得多模型支持"
    echo "安装命令: npm install -g @opencode/cli"
fi

# 检查VS Code扩展
echo "📊 检查VS Code扩展..."
if code --list-extensions | grep -q "anthropic.claude-code"; then
    echo "✅ Claude Code VS Code扩展已安装"
else
    echo "⚠️  Claude Code VS Code扩展未安装"
    echo "安装地址: https://marketplace.visualstudio.com/items?itemName=anthropic.claude-code"
fi

if code --list-extensions | grep -q "sst-dev.opencode"; then
    echo "✅ OpenCode VS Code扩展已安装"
else
    echo "⚠️  OpenCode VS Code扩展未安装"
    echo "安装地址: https://marketplace.visualstudio.com/items?itemName=sst-dev.opencode"
fi

# 检查Leo系统状态
echo ""
echo "📊 检查Leo AI Agent System..."
if [ -f "leo-system.py" ]; then
    echo "✅ Leo系统主文件存在"
    
    # 检查配置文件
    if [ -f "leo_config/settings/config.yaml" ]; then
        echo "✅ 系统配置文件存在"
        echo "📋 已配置技能数: $(grep -c "name:" leo_config/settings/config.yaml || echo "0")"
    else
        echo "⚠️  系统配置文件不存在"
    fi
else
    echo "❌ Leo系统主文件不存在"
fi

# 启动建议
echo ""
echo "💡 启动建议:"
echo "1. 开发模式: 使用Claude Code VS Code扩展进行复杂开发"
echo "2. 快速任务: 使用OpenCode CLI进行轻量级任务"
echo "3. 模型测试: 使用OpenCode多提供商对比不同模型"
echo "4. 系统维护: 使用Leo系统管理技能和代理"

echo ""
echo "🔧 快捷命令:"
echo "启动Claude Code模式: code ."
echo "启动OpenCode模式: opencode"
echo "运行Leo系统: python leo-system.py --status"

echo ""
echo "📚 参考文档:"
echo "- 多AI集成配置: leo_config/settings/multi_ai_integration.yaml"
echo "- Claude Code文档: https://code.claude.com/docs"
echo "- OpenCode文档: https://opencode.ai/docs"

echo ""
echo "==================================================="
echo "🎯 多AI协作环境就绪！"