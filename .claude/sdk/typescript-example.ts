/**
 * Claude Code TypeScript SDK 使用示例
 * 官方文档: https://docs.anthropic.com/en/docs/claude-code
 *
 * 安装: npm install @anthropic-ai/sdk
 */

import Anthropic from '@anthropic-ai/sdk';

const client = new Anthropic();

// 单次查询
async function query() {
  const message = await client.messages.create({
    model: 'claude-sonnet-4-6',
    max_tokens: 1024,
    messages: [{ role: 'user', content: '解释这个项目结构' }]
  });
  console.log(message.content);
}

// 连续对话
async function chat() {
  const stream = client.messages.stream({
    model: 'claude-sonnet-4-6',
    messages: [{ role: 'user', content: '你好' }]
  });

  for await (const event of stream) {
    if (event.type === 'content_block_delta') {
      process.stdout.write(event.delta.text);
    }
  }
}
