#!/bin/bash
# 启动 Leo MCP Server
# 使 Claude Code 可以调用 Leo System 的能力

cd "D:/桌面/leo_ai_system"

# 检查 Python 环境
if ! command -v python &> /dev/null; then
    echo "错误: 未找到 Python"
    exit 1
fi

# 安装依赖（如果需要）
echo "检查 MCP 依赖..."
pip show mcp &> /dev/null || pip install mcp

# 启动 MCP Server
echo "启动 Leo MCP Server..."
echo "Claude Code 可以通过以下方式连接:"
echo "  claude --mcp-config ./mcp.json"
echo ""

python src/leo_gateway/mcp_server.py
