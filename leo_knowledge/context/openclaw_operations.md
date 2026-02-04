# OpenClaw (大龙虾) 运维手册

> 记录网关运行中的问题、错误和解决方案
> **最后更新:** 2026-02-03 15:30

---

## ⚠️ 配置保护红线（必读）

### 绝对禁止的操作

| 禁止操作 | 原因 | 后果 |
|---------|------|------|
| **在飞书对话中请求 AI 修改 OpenClaw 配置** | AI 可能添加不被识别的配置键 | Gateway 启动失败 |
| 手动添加 `mcpTools` 到配置 | 已废弃 | 配置验证失败 |
| 手动添加 `systemPrompt` 到配置 | 已废弃 | 配置验证失败 |
| 手动添加 `cron` 到配置 | 不被识别 | 配置验证失败 |
| 手动添加 `mcp` 到配置 | 格式/位置错误 | 配置验证失败 |
| 修改 `plugins.entries` | OpenClaw 自动管理 | 配置验证失败 |
| 随意运行 `openclaw doctor --fix` | 可能覆盖自定义配置 | 配置丢失 |

### 安全的配置修改流程

```bash
# 1. 备份当前配置
copy %USERPROFILE%\.openclaw\openclaw.json openclaw.json.backup

# 2. 使用 CLI 修改（推荐）
cd D:\moltbot
node openclaw.mjs config set {key} {value}

# 3. 验证配置
node openclaw.mjs doctor

# 4. 测试启动
node openclaw.mjs gateway --port 18789
```

### 配置验证脚本

```bash
# 启动前验证配置
python d:\桌面\leo_ai_system\scripts\validate_openclaw_config.py
```

---

## 官方资源

| 资源 | 地址 |
|------|------|
| **GitHub 仓库** | https://github.com/openclaw/openclaw |
| **官方文档** | https://docs.openclaw.dev |
| **Releases** | https://github.com/openclaw/openclaw/releases |
| **当前版本** | v2026.1.30 (2026-01-31 发布) |

### v2026.1.30 主要更新

- CLI 自动补全支持 (Zsh/Bash/PowerShell/Fish)
- MiniMax OAuth 插件和 LINE 消息支持
- TypeScript 构建迁移到 `tsdown` + `tsgo`
- 安全修复: 防止本地文件包含 (LFI) 漏洞
- 多渠道修复 (Telegram, BlueBubbles, LINE, Matrix)

---

## 重大 Bug 记录

### ❌ Bug 2026-02-03: AI 自动修改配置导致启动失败

**事件背景:**
用户在飞书对话中让 OpenClaw "继承 Leo 系统的所有能力"，AI 代理尝试自动修改配置文件。

**问题现象:**
- Gateway 启动失败，端口 18789 未监听
- 智能守护系统报错，重试 3 次后失败
- 配置验证错误: `Unrecognized keys: "mcpTools", "systemPrompt", "cron", "mcp"`

**根本原因:**
AI 在配置文件中添加了不被 OpenClaw 2026.1.30 识别的配置键：
| 错误键 | 问题 |
|-------|------|
| `agents.defaults.mcpTools` | 已废弃 |
| `agents.list.0.identity` | 格式错误（应为对象） |
| `agents.list.0.systemPrompt` | 已废弃 |
| `cron.jobs` | 不被识别 |
| `mcp` | 配置位置错误 |

**修复操作:**
```bash
cd D:\moltbot
node openclaw.mjs doctor --fix
node openclaw.mjs gateway --port 18789
```

**教训:**
1. **不要在飞书对话中请求 AI 修改 OpenClaw 配置**
2. 配置修改必须使用 CLI: `node openclaw.mjs config set {key} {value}`
3. 修改前必须备份配置文件

**详细分析报告:** [docs/progress/openclaw_error_analysis.md](../../docs/progress/openclaw_error_analysis.md)

---

### ❌ Bug 2026-02-02: GitHub 改名导致启动失败

**事件背景:**
OpenClaw 官方从 `moltbot` 改名为 `openclaw`，GitHub 仓库从 `github.com/moltbot/moltbot` 迁移到 `github.com/openclaw/openclaw`。

**问题现象:**
- Gateway 启动失败：`Cannot find module 'C:\Users\...\moltbot\dist\index.js'`
- 飞书无法连接：`unknown channel id: feishu`
- 命令行工具报错：`Invalid config at openclaw.json`

**根本原因:**
1. **启动命令错误**: 使用 `node dist/index.js` 而非 `node openclaw.mjs`
2. **路径引用混乱**: 多处配置文件仍引用旧路径 `D:\moltbot`
3. **插件配置错误**: 在 `plugins.entries` 中手动添加 feishu 导致验证失败
4. **配置格式变更**: 2026.1.30 版本重构配置格式，不兼容旧配置

**修复过程:**
| 时间 | 操作 | 结果 |
|------|------|------|
| 2026-02-02 01:00 | 检查 GitHub 最新版本 | 确认已改名 openclaw |
| 2026-02-02 01:30 | 更新所有文档引用 | 28+ 文件 |
| 2026-02-02 02:00 | 修复 gateway.cmd 路径 | 指向 `openclaw.mjs` |
| 2026-02-02 03:00 | 清理 plugins.entries | 移除错误配置 |
| 2026-02-02 19:00 | 发现必须用 `openclaw.mjs` 启动 | 根本原因解决 |

**教训:**
1. **启动必须用**: `node openclaw.mjs gateway --port 18789`
2. **不要直接调用**: `dist/index.js` 或 `dist/entry.js`
3. **不要修改**: `plugins.entries` 配置项
4. **改名后路径**: D盘仍为 `D:\moltbot`，因为目录名未改

---

### ✅ Bug 2026-02-02 19:00: Gateway 断开连接

**问题现象:**
- 端口 18789 未监听
- 飞书机器人无响应
- 日志报错: `Invalid config: Unrecognized keys: "enabled", "host"`

**根本原因:**
- ❌ **自动修复脚本错误**: `openclaw_auto_healer.ps1` 和 `openclaw_guardian.ps1` 会错误地将 feishu 添加到 `plugins.entries`
- ❌ **OpenClaw 2026.1.30 不支持** `plugins.entries` 手动配置 feishu
- 旧 Node 进程残留 (PID 4900, 52532)

**修复操作:**
| 时间 | 操作 | 结果 |
|------|------|------|
| 19:00 | 清理 `plugins.entries.feishu` | ✅ |
| 19:05 | 停止旧进程并重启 Gateway | ✅ |
| 19:10 | 验证端口 18789 监听 | ✅ |
| 19:30 | 修复守护脚本，不再修改 plugins.entries | ✅ |

**修复后的守护脚本规则:**
1. ✅ 只检查 `channels.feishu`（用户配置）
2. ✅ 不修改 `plugins.entries`（OpenClaw 自动管理）
3. ✅ 信任 `openclaw doctor --fix` 的自动修复

**测试命令:**
```powershell
# 启动智能守护（不会破坏配置）
powershell -ExecutionPolicy Bypass -File d:\桌面\leo_ai_system\scripts\openclaw_auto_healer.ps1
```

---

## 智能自愈守护系统 (推荐)

### 🤖 OpenClaw Auto Healer v2.0

**自动功能**:
- ✅ 30秒间隔健康检查
- ✅ 自动诊断5大类常见问题
- ✅ 智能修复配置文件错误
- ✅ 自动清理僵尸进程
- ✅ 掉线后自动重启 (最多3次重试)
- ✅ 完整修复日志记录

**使用方式**:

```batch
# 方法1: 一键启动
d:\桌面\leo_ai_system\scripts\一键启动智能守护.bat

# 方法2: 安装开机自动启动
d:\桌面\leo_ai_system\scripts\install_auto_healer.bat

# 方法3: PowerShell 直接运行
powershell -ExecutionPolicy Bypass -File d:\桌面\leo_ai_system\scripts\openclaw_auto_healer.ps1
```

**自动修复能力**:

| 问题类型 | 检测方式 | 修复动作 |
|---------|---------|---------|
| 配置文件错误 | JSON解析检查 | 清理plugins.entries, 恢复channels.feishu |
| 启动脚本错误 | 正则匹配 | 修复gateway.cmd指向 |
| 端口占用 | TCP连接测试 | 终止占用进程 |
| 僵尸进程 | 进程存活时间 | 强制终止超过10分钟的进程 |
| 飞书扩展缺失 | 目录存在性 | 记录警告 |

**日志位置**:
```
%USERPROFILE%\.openclaw\logs\auto_healer_YYYYMMdd.log
```

**最新状态** (2026-02-02):
- ✅ 智能守护系统已部署并运行
- ✅ Gateway 正常运行 (PID 43588, ws://127.0.0.1:18789)
- ✅ 飞书 WebSocket 连接正常 (ws client ready)
- ✅ FFmpeg 8.0.1 已安装
- ✅ 视频编辑技能就绪

---

## 常见错误与解决方案

### ❌ 错误 1: gateway 配置格式错误 (2026.1.30+ 版本)

**症状:**
```
Invalid config at C:\Users\刘方林\.openclaw\openclaw.json:
- gateway: Unrecognized key: "local"
# 或
- gateway: Unrecognized keys: "enabled", "host"
```

**根本原因:**
OpenClaw 2026.1.30 版本完全重构了配置格式：
- 不再支持 `gateway.local` 嵌套对象
- 不再支持 `gateway.enabled`、`gateway.host`、`gateway.port`
- 改为使用 `gateway.mode` 简化配置

**正确配置 (2026.1.30+):**
```json
{
  "gateway": {
    "mode": "local",
    "auth": {
      "token": "leo-feishu-2024"
    }
  }
}
```

**修复步骤:**
1. 运行修复命令: `openclaw doctor --fix`
2. 设置网关模式: `openclaw config set gateway.mode local`
3. 启动网关: `openclaw gateway --port 18789`

**启动命令:**
```batch
cd D:\moltbot
node openclaw.mjs gateway --port 18789
```

**预防措施:**
- 升级 OpenClaw 前备份 `openclaw.json`
- 使用 `scripts\一键启动大龙虾_带守护.bat` 自动修复配置问题

---

### ❌ 错误 2: 网关频繁断开

**症状:**
- 飞书机器人无响应
- 端口 18789 未监听
- `netstat -ano | findstr "18789"` 无输出

**可能原因:**
1. Node 进程崩溃
2. 配置错误导致启动失败
3. 网络连接问题
4. 飞书 WebSocket 断开

**解决方案:**
1. **使用守护进程**: 运行 `scripts\openclaw_guardian.ps1`
2. **手动重启**:
   ```batch
   scripts\stop_gateway.bat
   scripts\start_gateway.bat
   ```
3. **检查日志**: `%USERPROFILE%\.openclaw\logs\error_*.log`

---

### ❌ 错误 3: 飞书收不到消息

**排查步骤:**
1. 检查网关是否运行: `netstat -ano | findstr "18789"`
2. 检查飞书配置: `~/.openclaw/openclaw.json` 中的 `channels.feishu`
3. 检查飞书机器人状态: 飞书开放平台 → 机器人管理
4. 查看 OpenClaw 日志: `~/.openclaw/logs/`

---

## 自动运维工具

| 脚本 | 用途 | 位置 |
|------|------|------|
| `一键启动大龙虾_带守护.bat` | 一键启动网关+守护进程 | `scripts/` |
| `openclaw_guardian.ps1` | PowerShell 守护进程，自动重连 | `scripts/` |
| `stop_gateway.bat` | 停止网关 | `scripts/` |
| `view_logs.bat` | 查看日志 | `scripts/` |

---

## 监控命令

```batch
# 检查端口
netstat -ano | findstr "18789"

# 检查 Node 进程
tasklist | findstr "node"

# 查看网关日志
type %USERPROFILE%\.openclaw\logs\guardian_*.log

# 测试飞书连接
curl http://127.0.0.1:18789/health
```

---

## 版本兼容性记录

| OpenClaw 版本 | 配置格式 | 备注 |
|---------------|----------|------|
| 2026.1.27-beta.1 | 支持 `gateway.local` | 旧格式 (已弃用) |
| 2026.1.30 | 使用 `gateway.mode` + 命令行参数 | **当前格式** |

**2026.1.30 重大变更:**
- 移除 `gateway.local/host/port/enabled` 配置项
- 新增 `gateway.mode` (local/remote)
- 端口通过命令行 `--port 18789` 指定
- 必须通过 `openclaw doctor --fix` 修复旧配置

**快速修复:**
```batch
cd D:\moltbot
node openclaw.mjs doctor --fix
node openclaw.mjs config set gateway.mode local
node openclaw.mjs gateway --port 18789
```

---

## 最佳实践

### 1. 官方推荐安装方式

```bash
# 要求 Node ≥22
npm install -g openclaw@latest
openclaw onboard --install-daemon
```

引导向导会自动安装 Gateway 守护进程（macOS 使用 launchd，Linux 使用 systemd）。

### 2. 版本更新检查

```batch
cd D:\moltbot
node openclaw.mjs --version
node openclaw.mjs update
```

切换更新频道：
- `openclaw update --channel stable` - 稳定版
- `openclaw update --channel beta` - 预发布版
- `openclaw update --channel dev` - 开发版

### 3. 配置备份

每次升级前备份配置：
```batch
copy %USERPROFILE%\.openclaw\openclaw.json %USERPROFILE%\.openclaw\openclaw.json.backup
```

### 4. 使用守护进程

**永远使用守护进程启动网关**，而不是直接运行 `gateway` 命令：
```batch
scripts\一键启动大龙虾_带守护.bat
```

### 5. 安全配置检查

定期运行安全检查：
```batch
openclaw doctor
openclaw security audit --deep
```

**安全默认设置**：
- DM 配对策略 (`dmPolicy="pairing"`)：未知发送者需要配对码
- 使用 `openclaw pairing approve <channel> <code>` 批准新用户
- 公开 DM 需要显式设置 `dmPolicy="open"`

### 6. 日志监控

定期检查日志发现潜在问题：
```batch
type %USERPROFILE%\.openclaw\logs\guardian_*.log
```

---

## 故障场景与恢复方案

### 场景 1: Gateway 断开连接（已修复）

**使用守护进程**（推荐）:
```powershell
powershell -ExecutionPolicy Bypass -File d:\桌面\leo_ai_system\scripts\openclaw_auto_healer.ps1
```
守护进程会每 30 秒检测一次，自动修复配置并重启。

**手动重启**:
```batch
scripts\stop_gateway.bat
scripts\start_gateway.bat
```

---

### 场景 2: 电脑关机/断电后恢复

**方案 A: 安装开机自启（推荐）**
```batch
scripts\install_openclaw_startup.bat
```
安装后，每次开机自动启动守护进程。

**方案 B: 手动启动**
```batch
scripts\start_gateway.bat
```

**验证**:
```batch
netstat -ano | findstr 18789
```

---

### 场景 3: 网络断开

| 情况 | 守护进程行为 |
|------|------------|
| 飞书 WebSocket 断开 | 自动重连（无限次重试） |
| 飞书服务器不可达 | 等待恢复后自动重连 |
| 网络恢复 | 自动恢复服务，无需人工干预 |

**日志查看**:
```batch
type %USERPROFILE%\.openclaw\logs\auto_healer_*.log
```

---

### 场景 4: 进程崩溃

守护进程检测到进程崩溃后会自动重启：

1. 第 1-2 次崩溃：快速重启
2. 连续失败：进入诊断模式，修复配置
3. 超过 10 次失败：进入 60 秒冷却期，防止无限重启

---

### 场景 5: 配置文件损坏

运行自动修复:
```powershell
powershell -ExecutionPolicy Bypass -File d:\桌面\leo_ai_system\scripts\openclaw_auto_healer.ps1 -CheckInterval 0
```

或手动修复:
```batch
cd D:\moltbot
node openclaw.mjs doctor --fix
node openclaw.mjs config set gateway.mode local
node openclaw.mjs gateway --port 18789
```

---

## 紧急联系

- **本地配置**: `C:\Users\刘方林\.openclaw\openclaw.json`
- **守护脚本**: `D:\桌面\leo_ai_system\scripts\openclaw_guardian.ps1`
- **日志目录**: `%USERPROFILE%\.openclaw\logs\`
