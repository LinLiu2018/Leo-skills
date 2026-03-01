# OpenClaw 运维手册

> 从 CLAUDE.md 提取，减少主配置文件体积。按需查阅。

## 1. 飞书消息无响应 - 快速诊断

```bash
# 1. 检查网关端口是否监听
netstat -ano | findstr "18789"

# 2. 如果端口未监听，启动网关
cd D:\openclaw && node openclaw.mjs gateway --port 18789

# 3. 检查实时日志
type \tmp\openclaw\openclaw-{date}.log | more
```

## 2. 常见问题归因表

| 现象 | 根因 | 解决方案 |
|------|------|----------|
| 飞书消息无响应 | 网关进程停止 | 重启网关: `cd D:\openclaw && node openclaw.mjs gateway --port 18789` |
| `plugin not found: feishu` | plugins.entries 配置错误 | feishu 是 channel 不是 plugin，从 plugins.entries 移除 |
| `Cannot read properties of undefined (reading 'trim')` | leo-system 插件配置问题 | 清空 plugins.entries 或修复插件代码 |
| `Unrecognized key: "schedules"` | 配置文件使用了不支持的键 | 移除 schedules，使用 `openclaw cron add` 命令添加定时任务 |
| 配置被自动恢复 | OpenClaw doctor 自动修复 | 手动编辑后立即重启网关 |
| Control UI build failed | 未安装 pnpm | `npm install -g pnpm`，确保 PATH 包含 npm 全局目录 |
| Control UI "gateway token missing" | 访问 URL 未带 token | 使用 `openclaw dashboard` 命令打开带 token 的 URL |
| **HTTP 401 MiniMax 认证错误** | `ANTHROPIC_AUTH_TOKEN` env 干扰 | 修改 pi-ai 添加 `authToken: null`，使用 `minimax-cn` provider |

## 3. 故障案例

### 3.1 2026-02-05 飞书消息无响应

- **根因**: `openclaw doctor --fix` 误将 feishu channel 当作 plugin 添加到 `plugins.entries`
- **修复**: 编辑 `openclaw.json`，将 `plugins.entries` 设为空对象 `{}`，重启网关
- **教训**: `openclaw doctor --fix` 后必须人工检查配置

### 3.2 2026-02-06 Control UI 构建失败

- **根因**: 系统未安装 `pnpm`，Git Bash PATH 不含 npm 全局目录
- **修复**: `npm install -g pnpm` + `export PATH="$PATH:/c/Users/刘方林/AppData/Roaming/npm"` + 重启网关
- **教训**: Control UI 构建失败不影响核心功能

### 3.3 2026-02-25 MiniMax API 401 认证错误

- **根因**: Claude Code 设置的 `ANTHROPIC_AUTH_TOKEN` 环境变量被 OpenClaw 继承，导致发送空 `Authorization: Bearer` header
- **修复**: 修改 `pi-ai` 库添加 `authToken: null`，使用 `minimax-cn` provider
- **教训**: 空字符串 `""` 不等于 `null`，第三方 SDK 环境变量可能跨服务冲突

## 4. 配置保护规则

**绝对禁止**：
1. 不要在飞书对话中请求 AI 修改 OpenClaw 配置
2. 不要手动添加 `mcpTools`, `systemPrompt`, `cron`, `schedules` 到 openclaw.json
3. 不要在 `plugins.entries` 中添加 channel 类型

**Channel vs Plugin 区分**：
- Channel (配置在 `channels.{name}`): feishu, lark, discord, telegram, slack, whatsapp, teams
- Plugin (配置在 `plugins.entries.{name}`): leo-system, memory-core, bluebubbles

**定时任务**：用 `openclaw cron add` 命令，不要在配置文件中添加 `schedules`

## 5. 关键文件路径

| 文件 | 路径 |
|------|------|
| OpenClaw 配置 | `C:\Users\刘方林\.openclaw\openclaw.json` |
| 运行日志 | `\tmp\openclaw\openclaw-{date}.log` |
| 会话历史 | `C:\Users\刘方林\.openclaw\agents\leo-assistant\sessions\` |
| 守护脚本日志 | `C:\Users\刘方林\.openclaw\logs\auto_healer_*.log` |

## 6. 已配置定时任务

| 任务名 | 调度 | 说明 |
|--------|------|------|
| health_check_hourly | 每小时 | 系统健康检查 |
| capability_index_daily | 每天 06:00 | 自动更新能力索引 |
| github_skills_daily | 每天 08:00 | GitHub 技能检查 |
| memory_cleanup_weekly | 每周六 03:00 | 清理过期记忆 |
| session_analysis_weekly | 每周日 06:00 | 会话分析与知识提取 |
| skills_update_weekly | 每周日 22:00 | 技能更新检查 |
| repo_watch_weekly | 每周一 09:00 | 仓库监控报告 |
