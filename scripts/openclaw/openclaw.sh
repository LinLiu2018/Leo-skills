#!/bin/bash
# OpenClaw 统一入口脚本
# 解决 npm CLI 和本地 runtime 不一致问题

OPENCLAW_DIR="D:/openclaw"
NODE_CMD="node"

# 检查参数
if [ $# -eq 0 ]; then
    echo "Usage: openclaw <command> [args...]"
    echo ""
    echo "Commands:"
    echo "  gateway         启动网关服务"
    echo "  agent           运行 Agent"
    echo "  cron            管理定时任务"
    echo "  channels        管理消息渠道"
    echo "  doctor          诊断配置"
    echo "  dashboard       打开管理界面"
    echo ""
    exit 1
fi

# 使用本地 openclaw.mjs 执行
cd "$OPENCLAW_DIR" || exit 1
$NODE_CMD openclaw.mjs "$@"
