# Claude Code 斜杠命令完整清单

> 最后更新: 2026-04-15

## 状态说明

| 状态 | 含义 |
|------|------|
| ✅ 可用 | 本身内置，直接使用 |
| ⚠️ 受限 | 需要付费订阅 |
| ❌ 不可用 | Windows 不支持或功能移除 |

---

## 完整命令列表 (65+)

### 📁 文件和会话

| 命令 | 状态 | 说明 |
|------|------|------|
| `/add-dir <path>` | ✅ 可用 | 添加工作目录 |
| `/branch [name]` | ✅ 可用 | 创建分支（别名: `/fork`） |
| `/clear` | ✅ 可用 | 清除会话历史 |
| `/compact [instructions]` | ✅ 可用 | 压缩对话 |
| `/continue` | ✅ 可用 | 继续最新会话 |
| `/desktop` | ⚠️ 受限 | 需要桌面应用订阅 |
| `/export [filename]` | ✅ 可用 | 导出会话 |
| `/fork-session` | ✅ 可用 | 创建新会话 ID |
| `/new` | ✅ 可用 | 新会话（别名: `/reset`） |
| `/rename [name]` | ✅ 可用 | 重命名会话 |
| `/resume [session]` | ✅ 可用 | 恢复会话 |
| `/rewind` | ✅ 可用 | 回溯对话/代码 |
| `/session-id` | ✅ 可用 | 显示会话 ID |

### 🔧 配置和系统

| 命令 | 状态 | 说明 |
|------|------|------|
| `/agents` | ✅ 可用 | 管理代理配置 |
| `/config` | ✅ 可用 | 打开设置界面 |
| `/help` | ✅ 可用 | 显示帮助 |
| `/hooks` | ✅ 可用 | 查看钩子配置 |
| `/ide` | ✅ 可用 | 管理 IDE 集成 |
| `/keybindings` | ✅ 可用 | 快捷键配置 |
| `/language [lang]` | ✅ 可用 | 设置语言 |
| `/login` | ✅ 可用 | 登录 |
| `/logout` | ✅ 可用 | 登出 |
| `/mcp` | ✅ 可用 | 管理 MCP 服务器 |
| `/permissions` | ✅ 可用 | 管理权限规则 |
| `/plugin` | ✅ 可用 | 管理插件 |
| `/privacy-settings` | ✅ 可用 | 隐私设置 |
| `/release-notes` | ✅ 可用 | 查看更新日志 |
| `/settings` | ✅ 可用 | 设置（别名: `/config`） |
| `/status` | ✅ 可用 | 状态标签页 |
| `/statusline` | ✅ 可用 | 配置状态栏 |
| `/theme [theme]` | ✅ 可用 | 更改颜色主题 |
| `/upgrade` | ⚠️ 受限 | 需要付费订阅 |

### 🧠 AI 和模型

| 命令 | 状态 | 说明 |
|------|------|------|
| `/auto-mode` | ⚠️ 受限 | 需要 Team/Enterprise |
| `/batch <instruction>` | ✅ 可用 | 大规模并行更改 |
| `/btw <question>` | ✅ 可用 | 快速侧问 |
| `/claude-api` | ✅ 可用 | Claude API 参考 |
| `/compact` | ✅ 可用 | 压缩对话 |
| `/cost` | ✅ 可用 | 令牌使用统计 |
| `/debug [description]` | ✅ 可用 | 调试日志 |
| `/effort [level]` | ✅ 可用 | 设置努力级别 |
| `/extra-usage` | ⚠️ 受限 | 免费周限制 |
| `/fast [on\|off]` | ✅ 可用 | 快速模式 |
| `/loop [interval]` | ✅ 可用 | 重复运行提示 |
| `/model [model]` | ✅ 可用 | 选择 AI 模型 |
| `/passes` | ⚠️ 受限 | 免费周 |
| `/plan [description]` | ✅ 可用 | 进入计划模式 |
| `/powerup` | ✅ 可用 | 功能教程 |
| `/simplify [focus]` | ✅ 可用 | 简化代码 |
| `/skills` | ✅ 可用 | 列出可用技能 |
| `/stats` | ✅ 可用 | 使用统计 |
| `/ultraplan <prompt>` | ⚠️ 受限 | 云端规划 |
| `/voice` | ⚠️ 受限 | 需要桌面应用 |

### 🔌 集成

| 命令 | 状态 | 说明 |
|------|------|------|
| `/chrome` | ⚠️ 受限 | Chrome 集成 |
| `/desktop` | ⚠️ 受限 | 桌面应用 |
| `/github` | ⚠️ 受限 | GitHub 集成 |
| `/init` | ✅ 可用 | 初始化项目 |
| `/install-github-app` | ⚠️ 受限 | GitHub Actions |
| `/install-slack-app` | ⚠️ 受限 | Slack 应用 |
| `/mobile` | ⚠️ 受限 | 移动应用 |
| `/remote-control` | ⚠️ 受限 | 远程控制 |
| `/remote-env` | ⚠️ 受限 | 远程环境 |
| `/setup-bedrock` | ⚠️ 受限 | AWS Bedrock |
| `/setup-vertex` | ⚠️ 受限 | Google Vertex |
| `/teleport` | ⚠️ 受限 | Web 会话拉取 |
| `/web-setup` | ⚠️ 受限 | GitHub 连接 |

### 🔒 安全

| 命令 | 状态 | 说明 |
|------|------|------|
| `/autofix-pr [prompt]` | ✅ 可用 | 自动修复 PR |
| `/doctor` | ✅ 可用 | 诊断验证 |
| `/feedback [report]` | ✅ 可用 | 提交反馈 |
| `/privacy-settings` | ✅ 可用 | 隐私设置 |
| `/sandbox` | ✅ 可用 | 沙箱模式 |
| `/security-review` | ✅ 可用 | 安全审查 |

### 📋 任务管理

| 命令 | 状态 | 说明 |
|------|------|------|
| `/schedule [description]` | ⚠️ 受限 | 云端计划任务 |
| `/tasks` | ✅ 可用 | 后台任务列表 |

### 🎨 其他

| 命令 | 状态 | 说明 |
|------|------|------|
| `/color [color]` | ✅ 可用 | 提示栏颜色 |
| `/copy [N]` | ✅ 可用 | 复制响应 |
| `/context` | ✅ 可用 | 上下文可视化 |
| `/diff` | ✅ 可用 | 交互式 diff |
| `/exit` | ✅ 可用 | 退出 |
| `/export` | ✅ 可用 | 导出 |
| `/help` | ✅ 可用 | 帮助 |
| `/insights` | ✅ 可用 | 会话分析 |
| `/memory` | ✅ 可用 | 编辑记忆 |
| `/review` | ❌ 已移除 | 已弃用 |
| `/stickers` | ✅ 可用 | 订购贴纸 |
| `/terminal-setup` | ✅ 可用 | 终端快捷键 |
| `/vim` | ❌ 已移除 | v2.1.92 移除 |

---

## 统计

| 类别 | 可用 | 受限 | 不可用 |
|------|------|------|--------|
| 文件和会话 | 13 | 1 | 0 |
| 配置和系统 | 15 | 1 | 0 |
| AI 和模型 | 17 | 4 | 0 |
| 集成 | 1 | 11 | 0 |
| 安全 | 5 | 1 | 0 |
| 任务管理 | 0 | 1 | 0 |
| 其他 | 9 | 0 | 2 |
| **总计** | **60** | **19** | **2** |

---

## 需要付费订阅的功能

1. **自动模式** (`/auto-mode`) - Team/Enterprise 订阅
2. **Channels** (Telegram/Slack) - Teams/Enterprise 订阅
3. **远程控制** - claude.ai 订阅
4. **桌面应用** - 付费订阅
5. **Web 会话** - claude.ai 订阅
6. **GitHub Actions** - 免费有限，完整功能需付费
7. **云端规划** (`/ultraplan`) - 需要订阅
8. **语音输入** (`/voice`) - 桌面应用订阅
9. **Slack 集成** - 需要 Slack App 配置

---

## 激活受限功能的方法

### 1. 免费订阅（基础）

已有 MiniMax API 方案可满足大部分需求。

### 2. Team 订阅（推荐）

- 自动模式
- Channels
- 远程控制
- GitHub Actions 完整版

### 3. Enterprise 订阅

- 所有功能
- 高级安全和合规
- 专属支持
