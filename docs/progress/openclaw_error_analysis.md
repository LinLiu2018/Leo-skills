# OpenClaw 配置报错归因分析报告

> **日期**: 2026-02-03
> **问题**: OpenClaw 智能守护系统报错，网关启动失败

## 1. 问题现象

### 1.1 错误日志
```
[2026-02-03 14:58:34] [修复] [诊断 2/5] 正在检查启动脚本...
[2026-02-03 14:58:34] [修复] [诊断 3/5] 检查OpenClaw安装
[2026-02-03 14:58:34] [成功] OpenClaw 安装完成
正在清理僵尸进程...
正在尝试启动网关 (1/3) ...
网关启动失败，端口未监听
正在尝试启动网关 (2/3) ...
网关启动失败，端口未监听
正在尝试启动网关 (3/3) ...
[2026-02-03 14:59:50] [警告] 网关启动失败，端口未监听
启动在最大重试次数后失败
错误
[2026-02-03 15:00:41] [警告] 检测到网关异常（连续：1）
```

### 1.2 配置验证错误
```
Invalid config at C:\Users\刘方林\.openclaw\openclaw.json:
- agents.defaults: Unrecognized key: "mcpTools"
- agents.list.0.identity: Invalid input: expected object, received string
- agents.list.0: Unrecognized keys: "systemPrompt", "mcpTools"
- cron: Unrecognized key: "jobs"
- <root>: Unrecognized key: "mcp"
```

## 2. 根因分析

### 2.1 直接原因

OpenClaw 配置文件 `C:\Users\刘方林\.openclaw\openclaw.json` 包含了不被 OpenClaw 2026.1.30 识别的配置键：

| 错误配置键 | 问题说明 | 来源 |
|-----------|---------|------|
| `agents.defaults.mcpTools` | 已废弃，不被识别 | AI 在飞书对话中自动添加 |
| `agents.list.0.identity` | 格式错误，应为对象而非字符串 | AI 尝试配置 Leo 身份 |
| `agents.list.0.systemPrompt` | 已废弃 | AI 尝试设置系统提示词 |
| `agents.list.0.mcpTools` | 已废弃 | AI 尝试配置 MCP 工具 |
| `cron.jobs` | 不被识别 | AI 尝试配置定时任务 |
| `mcp` | 配置位置/格式错误 | AI 尝试配置 MCP 服务器 |

### 2.2 根本原因

**用户在飞书中让 OpenClaw "继承 Leo 系统的所有能力"时，AI 代理尝试自动修改配置文件**，但：

1. **使用了已废弃的配置键** - OpenClaw 版本更新后不再支持 `mcpTools`, `systemPrompt` 等键
2. **配置格式不符合规范** - `identity` 应为对象 `{kind: "inline", content: "..."}` 而非字符串
3. **功能配置位置错误** - `cron` 和 `mcp` 不应在 openclaw.json 中配置

### 2.3 问题链路

```
用户在飞书对话中请求 "继承 Leo 系统能力"
    │
    ▼
AI 代理尝试修改 openclaw.json
    │
    ▼
添加了不被识别的配置键 (mcpTools, systemPrompt, cron, mcp)
    │
    ▼
OpenClaw 配置验证失败
    │
    ▼
Gateway 启动失败，端口 18789 未监听
    │
    ▼
智能守护系统检测到异常，尝试重启（失败）
```

## 3. 修复过程

### 3.1 诊断步骤

1. 检查端口状态：`Test-NetConnection -Port 18789` → False
2. 检查 Node 进程：无 OpenClaw 相关进程
3. 尝试手动启动网关：发现配置验证错误
4. 运行 `openclaw doctor --fix`：自动清理无效配置

### 3.2 修复操作

```bash
# 1. 备份原配置
copy C:\Users\刘方林\.openclaw\openclaw.json openclaw.json.backup

# 2. 运行 doctor 修复
cd D:\moltbot
node openclaw.mjs doctor --fix

# 3. 重新启动网关
node openclaw.mjs gateway --port 18789
```

### 3.3 修复结果

- ✅ 配置文件已修复
- ✅ 网关已启动 (PID: 38260)
- ✅ 端口 18789 正常监听

## 4. 经验教训

### 4.1 配置保护红线

**绝对禁止**：
1. 不要在飞书对话中请求 AI 修改 OpenClaw 配置
2. 不要手动添加 `mcpTools`, `systemPrompt`, `cron`, `mcp` 到 openclaw.json
3. 不要修改 `plugins.entries`（OpenClaw 自动管理）

### 4.2 安全修改流程

```bash
# 1. 备份
copy %USERPROFILE%\.openclaw\openclaw.json openclaw.json.backup

# 2. 使用 CLI 修改（推荐）
cd D:\moltbot
node openclaw.mjs config set {key} {value}

# 3. 验证
node openclaw.mjs doctor

# 4. 测试
node openclaw.mjs gateway --port 18789
```

### 4.3 历史问题对比

| 日期 | 问题 | 原因 | 修复 |
|------|------|------|------|
| 2026-02-02 | Gateway 启动失败 | 守护脚本错误修改 `plugins.entries` | 更新守护脚本 v2.1 |
| 2026-02-03 | Gateway 启动失败 | AI 在飞书对话中添加无效配置 | 运行 `doctor --fix` |

## 5. 预防措施

### 5.1 配置验证脚本

创建 `scripts/validate_openclaw_config.py` 用于启动前验证配置。

### 5.2 标准配置模板

创建 `docs/reference/openclaw_config_template.json` 作为参考。

### 5.3 运维手册更新

更新 `leo_knowledge/context/openclaw_operations.md` 添加配置保护规则。

---

## 6. 相关文件

- OpenClaw 配置: `C:\Users\刘方林\.openclaw\openclaw.json`
- 守护脚本: `scripts/openclaw_auto_healer.ps1`
- 用户档案: `leo_knowledge/context/user_profile.md`
- 运维手册: `leo_knowledge/context/openclaw_operations.md`

---

# 2026-02-25: HTTP 401 认证错误 + 多模型配置

> **日期**: 2026-02-25
> **问题**: OpenClaw 飞书消息无响应，HTTP 401 认证错误
> **解决**: 修复 MiniMax API 端点，配置多模型 (MiniMax/Kimi/GLM)

## 1. 问题现象

### 1.1 错误日志

```
HTTP 401: authentication_error: invalid api key
```

### 1.2 飞书表现

- 发送消息无 AI 响应
- 网关端口 18789 正常监听

## 2. 根因分析

### 2.1 MiniMax API 端点问题

| 尝试 | 端点 | API 类型 | 结果 |
|------|------|---------|------|
| 1 | `https://api.minimax.io/anthropic` | anthropic-messages | ❌ 401 错误 |
| 2 | `https://api.minimax.chat/v1` | chat/completions | ❌ OpenClaw 不支持 |
| 3 | `https://api.minimaxi.com/anthropic` | anthropic-messages | ✅ 成功 |

**结论**: MiniMax 需要使用**中国区端点** `api.minimaxi.com`，国际区端点 `api.minimax.io` 对新 API Key 无效。

### 2.2 API 类型限制

OpenClaw 只支持两种 API 类型：
- `anthropic-messages` - 用于 Anthropic 兼容 API (MiniMax)
- `openai-completions` - 用于 OpenAI 兼容 API (Kimi, GLM)

**错误**: 使用 `chat/completions` 会被 OpenClaw 拒绝

## 3. 修复过程

### 3.1 修复配置

编辑 `C:\Users\刘方林\.openclaw\openclaw.json`:

```json
{
  "models": {
    "providers": {
      "minimax": {
        "baseUrl": "https://api.minimaxi.com/anthropic",
        "apiKey": "sk-api-lyPJcMI3FdlNODeFtBxJoXDKaeWJACDsI9_cPrDTd7ztwNO5VfwM5ZR7OJlcUnvWuiavLFbDkxzDSYJKP9NaOCYtAUU59n460d6RJpddNc3EmvNPbpaENwA",
        "api": "anthropic-messages",
        "models": [...]
      }
    }
  }
}
```

### 3.2 配置多模型

| Provider | Model ID | Alias | API 类型 |
|----------|----------|-------|---------|
| MiniMax | MiniMax-M2.5 | Minimax | anthropic-messages |
| MiniMax | MiniMax-M2.1 | M2.1 | anthropic-messages |
| MiniMax | MiniMax-VL-01 | Vision | anthropic-messages |
| Moonshot | kimi-k2.5 | Kimi | openai-completions |
| Z.AI | glm-5 | GLM-5 | openai-completions |
| Z.AI | glm-4v | GLM-Vision | openai-completions |

### 3.3 模型别名配置

```json
{
  "agents": {
    "defaults": {
      "models": {
        "minimax/MiniMax-M2.5": {"alias": "Minimax"},
        "moonshot/kimi-k2.5": {"alias": "Kimi"},
        "zai/glm-5": {"alias": "GLM-5"}
      }
    }
  }
}
```

## 4. 飞书使用方法

### 4.1 默认模型

直接发送消息，使用默认模型 (Minimax)

### 4.2 切换模型

| 命令 | 效果 |
|------|------|
| `@Leo 切换到 Kimi` | 使用 Kimi k2.5 |
| `@Leo 使用 GLM-5` | 使用 GLM-5 |
| `@Leo 视觉模型` | 使用 MiniMax-VL-01 |

## 5. 最佳实践总结

### 5.1 MiniMax 配置要点

1. **必须使用中国区端点**: `https://api.minimaxi.com/anthropic`
2. **API 类型必须是**: `anthropic-messages`
3. **API Key 格式**: `sk-api-...` (不是 `sk-cp-...`)

### 5.2 多模型配置模板

```json
{
  "models": {
    "mode": "merge",
    "providers": {
      "minimax": {
        "baseUrl": "https://api.minimaxi.com/anthropic",
        "apiKey": "${MINIMAX_API_KEY}",
        "api": "anthropic-messages",
        "models": [
          {"id": "MiniMax-M2.5", "name": "M2.5", "reasoning": true, "contextWindow": 200000}
        ]
      },
      "moonshot": {
        "baseUrl": "https://api.moonshot.cn/v1",
        "apiKey": "${MOONSHOT_API_KEY}",
        "api": "openai-completions",
        "models": [
          {"id": "kimi-k2.5", "name": "Kimi", "contextWindow": 256000}
        ]
      },
      "zai": {
        "baseUrl": "https://api.zai.io/v1",
        "apiKey": "${ZAI_API_KEY}",
        "api": "openai-completions",
        "models": [
          {"id": "glm-5", "name": "GLM-5", "contextWindow": 200000}
        ]
      }
    }
  }
}
```

### 5.3 快速诊断命令

```bash
# 检查端口
netstat -ano | findstr "18789"

# 测试 API 端点 (MiniMax)
curl -X POST "https://api.minimaxi.com/anthropic/v1/messages" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"MiniMax-M2.5","max_tokens":10,"messages":[{"role":"user","content":"hi"}]}'

# 重启网关
cd D:\openclaw && node openclaw.mjs gateway --port 18789
```

## 6. 相关文件

- OpenClaw 配置: `C:\Users\刘方林\.openclaw\openclaw.json`
- Agent 模型配置: `C:\Users\刘方林\.openclaw\agents\leo-assistant\agent\models.json`
- 启动脚本: `C:\Users\刘方林\.openclaw\gateway.cmd`
- OpenClaw 官方文档: `D:\openclaw\docs\`
