#!/usr/bin/env python3
"""
Claude Code Python SDK 使用示例
官方文档: https://docs.anthropic.com/en/docs/claude-code

安装: pip install anthropic
"""

from anthropic import Anthropic

# 方式1: 直接使用 API Key
client = Anthropic(
    api_key="sk-ant-xxxxx"  # 从 ~/.claude/settings.json 读取
)

# 方式2: 使用 Claude Code 会话
# from anthropic import ClaudeCode
# code = ClaudeCode()
# result = code.query("解释这个代码库结构")

# 单次查询
message = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": "解释这个项目结构"}]
)
print(message.content)

# 连续对话
with client.messages.stream(
    model="claude-sonnet-4-6",
    messages=[{"role": "user", "content": "你好"}]
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
