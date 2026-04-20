# Claude Code Agent SDK

## 简介

Claude Code Agent SDK 允许你以编程方式调用 Claude Code 的能力。

## 安装

```bash
# Python SDK
pip install anthropic

# TypeScript SDK
npm install @anthropic-ai/sdk
```

## 配置

从 `~/.claude/settings.json` 读取 API 密钥：

```json
{
  "env": {
    "ANTHROPIC_AUTH_TOKEN": "sk-ant-xxxxx",
    "ANTHROPIC_BASE_URL": "https://api.minimaxi.com/anthropic"
  }
}
```

## 使用方式

### Python

```python
from anthropic import ClaudeCode

code = ClaudeCode()
result = code.query("分析 src/ 目录结构")
```

### TypeScript

```typescript
import { ClaudeCode } from '@anthropic-ai/sdk';

const code = new ClaudeCode();
const result = await code.query("分析 src/ 目录结构");
```

## 与 MCP 的区别

| 特性 | MCP | Agent SDK |
|------|-----|-----------|
| 调用方式 | 工具调用 | API 调用 |
| 场景 | 集成到 Claude Code | 独立程序 |
| 认证 | MCP 服务器配置 | API Key |
| 能力 | 受限于 MCP 服务器 | 完整 Claude API |

## 示例文件

- `python-example.py` - Python SDK 使用示例
- `typescript-example.ts` - TypeScript SDK 使用示例
