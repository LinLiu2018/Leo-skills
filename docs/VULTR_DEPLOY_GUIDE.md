# Vultr 云端部署指南

> 创建时间: 2026-02-01
> 适用场景: 按需付费、灵活测试、短期使用

---

## 1. 为什么选择 Vultr

| 优势 | 说明 |
|------|------|
| **按小时计费** | 用多少付多少，随时删除停止计费 |
| **31个数据中心** | 全球覆盖，可选最优节点 |
| **免费快照** | 随时备份，无额外费用 |
| **即时部署** | 服务器创建约 60 秒完成 |
| **无合约** | 无最低消费，无锁定期 |

---

## 2. 推荐配置

### 2.1 仅部署 OpenClaw (入门)

| 配置项 | 推荐值 |
|--------|--------|
| **套餐** | High Performance 2GB |
| **月费** | $12/月 (~¥88) |
| **配置** | 1 vCPU / 2GB RAM / 50GB NVMe / 3TB 流量 |
| **数据中心** | Los Angeles 或 Silicon Valley |
| **系统** | Ubuntu 24.04 LTS |

### 2.2 部署 OpenClaw + n8n + Dify (推荐)

| 配置项 | 推荐值 |
|--------|--------|
| **套餐** | High Performance 4GB |
| **月费** | $24/月 (~¥175) |
| **配置** | 2 vCPU / 4GB RAM / 100GB NVMe / 5TB 流量 |
| **数据中心** | Los Angeles 或 Silicon Valley |
| **系统** | Ubuntu 24.04 LTS |

### 2.3 Vultr 套餐对比

| 套餐 | 月费 | vCPU | RAM | 存储 | 流量 | 适用场景 |
|------|------|------|-----|------|------|----------|
| Regular 2GB | $10 | 1 | 2GB | 55GB | 2TB | 轻量测试 |
| High Perf 2GB | $12 | 1 | 2GB | 50GB | 3TB | 仅 OpenClaw |
| High Perf 4GB | $24 | 2 | 4GB | 100GB | 5TB | 三件套推荐 ✅ |
| High Perf 8GB | $48 | 4 | 8GB | 180GB | 6TB | 高负载场景 |

---

## 3. 购买步骤

### 3.1 注册账户

```
步骤 1: 访问 https://www.vultr.com/
步骤 2: 点击 "Sign Up" 注册账户
步骤 3: 验证邮箱
步骤 4: 添加支付方式 (支持信用卡、PayPal、支付宝)
步骤 5: 充值 (最低 $10，建议 $25 起)
```

### 3.2 创建服务器

```
步骤 1: 登录后点击 "Deploy +" 或 "Deploy New Server"
步骤 2: 选择 "Cloud Compute"
步骤 3: 选择 "High Performance" (AMD)
步骤 4: 选择数据中心: Los Angeles 或 Silicon Valley
步骤 5: 选择系统: Ubuntu 24.04 LTS x64
步骤 6: 选择配置: $24/mo (4GB RAM) 或 $12/mo (2GB RAM)
步骤 7: 可选: 启用 "Auto Backups" ($4.80/月)
步骤 8: 设置 Server Hostname: leo-openclaw
步骤 9: 点击 "Deploy Now"
步骤 10: 等待约 60 秒，状态变为 "Running"
```

### 3.3 获取服务器信息

```
部署完成后，在服务器详情页获取:
- IP Address: xxx.xxx.xxx.xxx
- Username: root
- Password: xxxxxxxx (点击眼睛图标查看)
```

---

## 4. 部署实操指南

### 4.1 第一阶段: 连接服务器

**Windows PowerShell / Terminal**

```bash
ssh root@你的服务器IP
# 输入密码 (首次连接输入 yes 确认)
```

**推荐: 配置 SSH 密钥登录**

```bash
# 本地生成密钥 (如果没有)
ssh-keygen -t ed25519 -C "leo@openclaw"

# 复制公钥到服务器
ssh-copy-id root@你的服务器IP

# 之后可免密登录
ssh root@你的服务器IP
```

### 4.2 第二阶段: 系统初始化

```bash
# 更新系统
apt update && apt upgrade -y

# 安装必要工具
apt install -y curl wget git vim htop net-tools

# 设置时区
timedatectl set-timezone Asia/Shanghai

# 设置主机名
hostnamectl set-hostname leo-openclaw
```

### 4.3 第三阶段: 安装 Node.js 22

```bash
# 安装 Node.js 22
curl -fsSL https://deb.nodesource.com/setup_22.x | bash -
apt install -y nodejs

# 验证安装
node -v  # v22.x.x
npm -v   # 10.x.x
```

### 4.4 第四阶段: 安装 OpenClaw

```bash
# 安装 OpenClaw
npm install -g openclaw@latest

# 验证安装
openclaw --version

# 创建配置目录
mkdir -p ~/.openclaw

# 编辑配置文件
vim ~/.openclaw/openclaw.json
```

**配置文件内容** (按 `i` 编辑，`Esc` + `:wq` 保存):

```json
{
  "agents": {
    "defaults": {
      "workspace": "/root/.openclaw/workspace",
      "model": {
        "primary": "kimi-code/kimi-for-coding"
      }
    }
  },
  "gateway": {
    "port": 18789,
    "mode": "local",
    "bind": "loopback",
    "auth": {
      "mode": "token",
      "token": "leo-vultr-2026"
    }
  },
  "channels": {
    "feishu": {
      "enabled": true,
      "appId": "cli_a9f7c17a65b89cd2",
      "appSecret": "T5pWcoYJ4qlCYmDLA8g0fbziBylJDFAh",
      "domain": "feishu",
      "connectionMode": "websocket",
      "dmPolicy": "open",
      "groupPolicy": "open",
      "requireMention": false
    }
  },
  "commands": {
    "native": "auto",
    "nativeSkills": "auto"
  }
}
```

### 4.5 第五阶段: PM2 进程守护

```bash
# 安装 PM2
npm install -g pm2

# 创建 PM2 配置
cat > ~/ecosystem.config.js << 'EOF'
module.exports = {
  apps: [{
    name: 'openclaw',
    script: 'openclaw',
    args: 'gateway',
    max_memory_restart: '500M',
    restart_delay: 5000,
    max_restarts: 50,
    autorestart: true,
    watch: false,
    env: {
      NODE_ENV: 'production'
    }
  }]
}
EOF

# 启动 OpenClaw
pm2 start ~/ecosystem.config.js

# 查看状态
pm2 status

# 查看日志
pm2 logs openclaw

# 设置开机自启
pm2 save
pm2 startup
# 执行输出的命令
```

### 4.6 第六阶段: 验证部署

```bash
# 检查进程
pm2 status

# 检查端口
netstat -tlnp | grep 18789

# 检查内存
free -h

# 实时日志
pm2 logs openclaw -f
```

**飞书测试**: 打开飞书 → 找到机器人 → 发送消息 → 确认回复

---

## 5. n8n 部署 (可选)

```bash
# 安装 Docker
curl -fsSL https://get.docker.com | sh

# 创建数据目录
mkdir -p ~/.n8n

# 启动 n8n
docker run -d \
  --name n8n \
  --restart always \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  -e N8N_BASIC_AUTH_ACTIVE=true \
  -e N8N_BASIC_AUTH_USER=leo \
  -e N8N_BASIC_AUTH_PASSWORD=你的密码 \
  n8nio/n8n

# 访问: http://你的IP:5678
```

---

## 6. Dify 部署 (可选)

```bash
# 克隆仓库
git clone https://github.com/langgenius/dify.git
cd dify/docker

# 配置环境
cp .env.example .env
vim .env  # 修改密码等配置

# 启动
docker compose up -d

# 访问: http://你的IP:3000
```

---

## 7. 常用运维命令

### 7.1 PM2 管理

```bash
pm2 status              # 状态
pm2 logs openclaw       # 日志
pm2 restart openclaw    # 重启
pm2 stop openclaw       # 停止
pm2 monit               # 监控
```

### 7.2 系统监控

```bash
htop                    # 资源监控
free -h                 # 内存
df -h                   # 磁盘
netstat -tlnp           # 端口
```

### 7.3 Vultr 快照备份

```
1. 登录 Vultr 控制台
2. 选择服务器 → Snapshots
3. 点击 "Take Snapshot"
4. 等待完成 (免费!)
```

---

## 8. 费用估算

### 8.1 仅 OpenClaw

| 项目 | 月费 |
|------|------|
| High Perf 2GB | $12 |
| **总计** | **$12/月 (~¥88)** |

### 8.2 三件套 (推荐)

| 项目 | 月费 |
|------|------|
| High Perf 4GB | $24 |
| Auto Backup (可选) | $4.80 |
| **总计** | **$24-29/月 (~¥175-212)** |

### 8.3 按小时计费

| 套餐 | 小时费率 | 说明 |
|------|----------|------|
| High Perf 2GB | $0.018/h | 测试几小时只需几毛钱 |
| High Perf 4GB | $0.036/h | 灵活开关，用完即删 |

---

## 9. Vultr vs Hostinger 对比

| 对比项 | Vultr High Perf 4GB | Hostinger KVM 1 |
|--------|---------------------|-----------------|
| 月费 | $24 (~¥175) | ¥36.99 (首购) |
| 内存 | 4GB | 4GB |
| 计费方式 | 按小时 ✅ | 预付24个月 |
| 灵活性 | 高 ✅ | 低 |
| 长期成本 | 高 | 低 ✅ |
| 适合场景 | 测试/短期 | 长期使用 |

**建议**:
- **测试阶段**: 用 Vultr，按小时计费，随时删除
- **确定长期使用**: 迁移到 Hostinger，成本更低

---

## 10. 部署检查清单

- [ ] **Vultr 账户**
  - [ ] 注册并验证邮箱
  - [ ] 添加支付方式
  - [ ] 充值 $25+

- [ ] **创建服务器**
  - [ ] 选择 High Performance
  - [ ] 选择 Los Angeles / Silicon Valley
  - [ ] 选择 Ubuntu 24.04 LTS
  - [ ] 选择 $24/mo (4GB) 或 $12/mo (2GB)

- [ ] **部署 OpenClaw**
  - [ ] SSH 连接成功
  - [ ] Node.js 22 安装
  - [ ] OpenClaw 安装
  - [ ] 配置文件创建
  - [ ] PM2 守护启动
  - [ ] 开机自启设置

- [ ] **验证**
  - [ ] 飞书消息测试通过
  - [ ] Gateway 稳定运行

---

## 11. 快速命令汇总

```bash
# 一键初始化 (复制粘贴即可)
apt update && apt upgrade -y && \
apt install -y curl wget git vim htop net-tools && \
timedatectl set-timezone Asia/Shanghai && \
curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
apt install -y nodejs && \
npm install -g openclaw@latest pm2

# 验证安装
node -v && npm -v && openclaw --version && pm2 --version
```

---

*文档创建于 2026-02-01*
