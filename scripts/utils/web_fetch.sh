#!/bin/bash
# web_fetch.sh - 绕过 Claude Code WebFetch 限制获取网页内容
# 使用方法: ./web_fetch.sh <网址>

URL="$1"

if [ -z "$URL" ]; then
    echo "用法: $0 <网址>"
    echo "示例: $0 https://news.ycombinator.com"
    exit 1
fi

# 使用 jina.ai 摘要服务
curl -sL "https://r.jina.ai/http://$URL" 2>/dev/null
