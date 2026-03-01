# OpenClaw 运维日志

## 2026-02-25 MiniMax API 401 认证错误

### 故障现象
- 飞书发送消息返回 HTTP 401 认证错误
- 错误信息：`login fail: Please carry the API secret key in the 'Authorization' field of the request header`

### 根因分析（历时 3 小时深度调试）

#### 直接原因
Claude Code 插件设置了环境变量 `ANTHROPIC_AUTH_TOKEN`（Claude API key），当 OpenClaw 调用 MiniMax API 时，Anthropic SDK 自动读取该环境变量并添加 `Authorization: Bearer` header，导致：

1. SDK 同时发送 `X-Api-Key: sk-api-xxx`（MiniMax key）
2. SDK 同时发送 `Authorization: Bearer `（空 token，来自 `ANTHROPIC_AUTH_TOKEN=""` 被设置为空字符串后）
3. MiniMax API 优先使用 `Authorization` header，看到空 token 返回 401

#### 根本原因
- `ANTHROPIC_AUTH_TOKEN` 环境变量为空字符串时，SDK 的 `bearerAuth` 函数检查 `if (this.authToken == null)` 返回 false（因为 `"" != null`）
- 导致 SDK 发送 `Authorization: Bearer ` 而非完全不发送该 header

#### 配置问题叠加
- 使用了错误的 provider：`minimax`（国际版 baseUrl: `api.minimax.io`）而非 `minimax-cn`（中国区 baseUrl: `api.minimaxi.com`）
- 你的 MiniMax API key 只在 `api.minimaxi.com` 上有效

### 修复方案

#### 1. 修改 pi-ai 库禁用 Authorization header
文件：`D:\openclaw\node_modules\@mariozechner\pi-ai\dist\providers\anthropic.js`

```javascript
// API key auth
const client = new Anthropic({
    apiKey,
    authToken: null,  // 显式禁用 Authorization header，防止 ANTHROPIC_AUTH_TOKEN 环境变量干扰
    baseURL: model.baseUrl,
    dangerouslyAllowBrowser: true,
    // ...
});
```

#### 2. 重新配置 MiniMax 中国区 provider
```bash
cd D:\openclaw
node openclaw.mjs onboard --auth-choice minimax-api-key-cn \
  --minimax-api-key "sk-api-你的key" --non-interactive --accept-risk
```

#### 3. 清理 plugins.entries.feishu（如果存在）
feishu 是 channel 不是 plugin，不应出现在 `plugins.entries` 中

### 避免重复出现的措施

1. **不要在运行 OpenClaw 的 shell 环境中设置 `ANTHROPIC_AUTH_TOKEN`**
   - 如果使用 Claude Code 插件，确保其设置的 env 不会传递给 OpenClaw
   - 或使用 `--local` 模式测试，该模式下不会继承外部环境变量

2. **使用正确的 MiniMax provider**
   - 中国区用户应使用 `minimax-cn` provider
   - 配置命令：`--auth-choice minimax-api-key-cn`

3. **验证配置**
   - 运行 `node openclaw.mjs agent --agent leo-assistant --message "test" --local` 测试
   - 如返回 401，检查 `DEBUG-ALL` 日志中的 authorization header

### 相关文件路径
| 文件 | 路径 |
|------|------|
| OpenClaw 配置 | `C:\Users\刘方林\.openclaw\openclaw.json` |
| 修复的 pi-ai | `D:\openclaw\node_modules\@mariozechner\pi-ai\dist\providers\anthropic.js` |
| Auth profiles | `C:\Users\刘方林\.openclaw\agents\leo-assistant\agent\auth-profiles.json` |
| Gateway 日志 | `\tmp\openclaw\openclaw-*.log` |
