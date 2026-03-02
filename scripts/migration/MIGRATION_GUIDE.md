# OpenClaw + Leo AI System 迁移指南

> 从旧电脑迁移到新电脑的完整步骤

## 一、GitHub 仓库地址

- **Leo AI System**: https://github.com/LinLiu2018/Leo-skills.git
- **分支**: `refactor/standardize-structure`
- **备份文件位置**: `scripts/migration/`

## 二、新电脑操作步骤

### 1. 克隆项目

```bash
# 创建项目目录
mkdir -p D:\桌面
cd D:\桌面

# 克隆仓库
git clone https://github.com/LinLiu2018/Leo-skills.git leo_ai_system
cd leo_ai_system

# 切换到正确的分支
git checkout refactor/standardize-structure
```

### 2. 安装 Node.js 和 OpenClaw

```bash
# 安装 Node.js (v20+)
# 从 https://nodejs.org/ 下载安装

# 安装 OpenClaw
npm install -g openclaw

# 验证安装
openclaw --version
```

### 3. 恢复 OpenClaw 配置

```bash
# 创建 OpenClaw 配置目录
mkdir -p ~/.openclaw

# 复制主配置文件
cp scripts/migration/openclaw_config_backup.json ~/.openclaw/openclaw.json

# 创建 agent 目录
mkdir -p ~/.openclaw/agents/leo-assistant
cp -r scripts/migration/agent_config ~/.openclaw/agents/leo-assistant/

# 创建 workspace 目录
mkdir -p ~/.openclaw/workspace
cp scripts/migration/USER.md.backup ~/.openclaw/workspace/USER.md
cp scripts/migration/SOUL.md.backup ~/.openclaw/workspace/SOUL.md

# 恢复定时任务
cp scripts/migration/cron_jobs_backup.json ~/.openclaw/cron/jobs.json

# 恢复扩展插件
mkdir -p ~/.openclaw/extensions
cp -r scripts/migration/extensions/* ~/.openclaw/extensions/
```

### 4. 启动 OpenClaw 网关

```bash
cd D:\openclaw
node openclaw.mjs gateway --port 18789
```

### 5. 验证安装

```bash
# 检查 agent 状态
openclaw agents list

# 检查通道状态
openclaw channels status

# 检查定时任务
openclaw cron list
```

## 三、注意事项

### 需要手动配置的内容

1. **环境变量**: 检查 `~/.openclaw/openclaw.json` 中的 API Key
2. **路径调整**: 确保 `workspace` 路径指向正确的项目目录
3. **定时任务**: 可能需要重新激活某些任务

### 常见问题

**问题 1: 端口被占用**
```bash
# 查找占用 18789 端口的进程
netstat -ano | findstr "18789"

# 结束进程后重启网关
taskkill /F /PID <PID>
```

**问题 2: 飞书通道无法连接**
```bash
# 检查配置
openclaw config get channels.feishu

# 重新配置
openclaw config set channels.feishu.appId "cli_a9f18849edbb9cb1"
```

**问题 3: 缺少依赖**
```bash
# 在项目目录安装依赖
cd D:\桌面\leo_ai_system
npm install
```

## 四、文件清单

### 已备份到 GitHub 的文件

| 文件 | 说明 | 新电脑位置 |
|------|------|-----------|
| `openclaw_config_backup.json` | OpenClaw 主配置 | `~/.openclaw/openclaw.json` |
| `agent_config/` | Agent 配置 | `~/.openclaw/agents/leo-assistant/agent/` |
| `USER.md.backup` | 用户画像 | `~/.openclaw/workspace/USER.md` |
| `SOUL.md.backup` | AI 灵魂设定 | `~/.openclaw/workspace/SOUL.md` |
| `cron_jobs_backup.json` | 定时任务 | `~/.openclaw/cron/jobs.json` |
| `extensions/` | 扩展插件 | `~/.openclaw/extensions/` |

## 五、验证清单

- [ ] 网关成功启动 (curl http://localhost:18789/ 返回 200)
- [ ] Agent 列表显示 `leo-assistant`
- [ ] 飞书通道状态为 `running`
- [ ] 定时任务列表显示所有任务
- [ ] 飞书发送测试消息能收到回复

## 六、联系支持

如有问题，参考：
- `docs/reference/OPENCLAW_OPS.md` - 运维手册
- `leo_knowledge/context/openclaw_operations.md` - 操作指南
