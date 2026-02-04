# OpenClaw 云端部署指南

> 创建时间: 2026-01-31
> 最后更新: 2026-01-31
> 状态: ✅ 已确定方案 - Hostinger KVM 1 (长期使用，性价比最优)

---

## 1. 部署架构

```
┌─────────────────────────────────────────────────────────────┐
│                      飞书服务器                               │
│                  (open.feishu.cn)                            │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │ WebSocket 长连接
                              │ (客户端主动连接)
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     云端服务器                                │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                  OpenClaw Gateway                    │   │
│  │              (Node.js 22 + PM2)                      │   │
│  │                                                      │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │   │
│  │  │ 飞书通道  │  │ 技能系统  │  │ AI Agent │          │   │
│  │  │ (feishu) │  │ (skills) │  │ (Kimi)   │          │   │
│  │  └──────────┘  └──────────┘  └──────────┘          │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. 部署日志 (2026-01-31)

### 2.1 腾讯云硅谷站部署记录

| 时间 | 操作 | 结果 |
|------|------|------|
| 13:00 | 开始部署腾讯云硅谷站 | - |
| 13:02 | 运行 `openclaw onboard` | 完成向导配置 |
| 13:10 | 配置飞书通道 | 成功连接 |
| 13:15 | 飞书消息测试 | 成功响应 |
| 13:30 | Gateway 断开连接 | 问题出现 |
| 13:35 | 使用 PM2 守护进程 | 启动成功 |
| 13:45 | 再次断开连接 | 问题复现 |

### 2.2 遇到的问题

| 问题 | 原因分析 | 解决方案 |
|------|----------|----------|
| Gateway 频繁断开 | 服务器资源不足 / 网络不稳定 | 使用 PM2 + 健康检查 |
| TUI 界面卡死 | 腾讯云 Web 终端不稳定 | 使用本地 SSH 客户端 |
| 配置文件写入失败 | cat heredoc 格式问题 | 使用 nano/vi 编辑 |
| nano 命令不存在 | OpenCloudOS 精简系统 | 使用 vi 或 cat |
| systemctl 找不到服务 | 未安装为 systemd 服务 | 使用 PM2 管理 |

### 2.3 经验教训

1. **腾讯云 Web 终端 (OrcaTerm) 不稳定**，建议使用本地 SSH 客户端
2. **轻量服务器资源有限**，OpenClaw + Node.js 可能占用较多内存
3. **必须使用进程守护** (PM2)，否则终端关闭服务就停止
4. **配置文件用 vi 编辑更可靠**，避免 cat heredoc 格式问题
5. **硅谷站到飞书的网络可能不稳定**，考虑使用香港或国内节点

---

## 3. 飞书机器人配置

### 3.1 本地机器人 (开发环境)

| 配置项 | 值 |
|--------|-----|
| App ID | `cli_a9f18849edbb9cb1` |
| App Secret | `UUNNVCiRRheoPkdnKPeVycYTTlVQ8emS` |
| 配置文件 | `C:\Users\刘方林\.openclaw\openclaw.json` |
| Gateway 端口 | 18789 |
| Web UI | `http://127.0.0.1:18789?token=leo-feishu-2024` |

### 3.2 云端机器人 (生产环境)

| 配置项 | 值 |
|--------|-----|
| App ID | `cli_a9f7c17a65b89cd2` |
| App Secret | `T5pWcoYJ4qlCYmDLA8g0fbziBylJDFAh` |
| 配置文件 | `~/.openclaw/openclaw.json` |
| Gateway 端口 | 18789 |
| 模型 | `kimi-code/kimi-for-coding` |

---

## 4. Hostinger 部署方案 (推荐 - 长期使用)

### 4.1 为什么选择 Hostinger

| 对比项 | Hostinger KVM 1 | Vultr High Perf 2GB | 腾讯云硅谷 |
|--------|-----------------|---------------------|-----------|
| 月费 | ¥36.99 (首购) | $12 (~¥88) | ¥80+ |
| 续费价 | ¥73.99/月 | $12/月 | ¥80+/月 |
| 内存 | **4GB** ✅ | 2GB | 2GB |
| 存储 | 50GB NVMe | 50GB SSD | 40GB |
| 流量 | 4TB | 3TB | 1TB |
| 处理器 | AMD EPYC | AMD EPYC | Intel |
| 网络速度 | 1Gbps | 1Gbps | 30Mbps |
| 稳定性 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |

**选择理由**:
1. **4GB 内存** - 足够同时运行 OpenClaw + n8n + Dify
2. **首购价格低** - ¥36.99/月 × 24个月 = ¥887.76 (约 $122)
3. **AMD EPYC 处理器** - 性能强劲
4. **NVMe SSD** - 比普通 SSD 快 3-5 倍
5. **30天退款保障** - 不满意可退

### 4.2 推荐配置

| 配置项 | 推荐值 |
|--------|--------|
| **套餐** | KVM 1 |
| **订阅期限** | 24个月 (最优惠) |
| **数据中心** | 新加坡 或 美国 (根据飞书延迟选择) |
| **操作系统** | Ubuntu 24.04 LTS |
| **总费用** | ¥887.76 (约 $122/2年) |

### 4.3 购买步骤

```
步骤 1: 访问 https://www.hostinger.com/hk/jiage/vps-hosting#pricing
步骤 2: 选择 "KVM 1" 套餐
步骤 3: 选择 "24个月" 订阅期限
步骤 4: 点击 "选择套餐"
步骤 5: 创建账户或登录
步骤 6: 选择数据中心 (推荐: 新加坡 - 到飞书延迟低)
步骤 7: 选择操作系统: Ubuntu 24.04 LTS
步骤 8: 设置 root 密码 (记录下来!)
步骤 9: 完成支付 (支持支付宝/微信)
步骤 10: 等待服务器创建完成 (约 2-5 分钟)
```

---

## 5. 部署实操指南 (Step by Step)

### 5.1 第一阶段: 服务器初始化

**连接服务器** (使用本地 SSH 客户端，不要用 Web 终端)

```bash
# Windows PowerShell 或 Terminal
ssh root@你的服务器IP
```

**系统更新**

```bash
# 更新系统
apt update && apt upgrade -y

# 安装必要工具
apt install -y curl wget git vim htop

# 设置时区
timedatectl set-timezone Asia/Shanghai
```

### 5.2 第二阶段: 安装 Node.js 22

```bash
# 安装 Node.js 22 (OpenClaw 需要)
curl -fsSL https://deb.nodesource.com/setup_22.x | bash -
apt install -y nodejs

# 验证安装
node -v  # 应显示 v22.x.x
npm -v   # 应显示 10.x.x
```

### 5.3 第三阶段: 安装 OpenClaw

```bash
# 安装 OpenClaw
npm install -g openclaw@latest

# 验证安装
openclaw --version

# 运行配置向导
openclaw onboard
```

**配置向导选项**:
```
? 选择消息通道: feishu (飞书)
? App ID: cli_a9f7c17a65b89cd2
? App Secret: T5pWcoYJ4qlCYmDLA8g0fbziBylJDFAh
? 选择 AI 模型: kimi-code/kimi-for-coding
? 启用 Gateway: Yes
```

### 5.4 第四阶段: 配置文件 (手动编辑)

```bash
# 创建配置目录
mkdir -p ~/.openclaw

# 编辑配置文件
vim ~/.openclaw/openclaw.json
```

**配置文件内容** (按 `i` 进入编辑模式，粘贴后按 `Esc`，输入 `:wq` 保存):

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
      "token": "leo-cloud-2026"
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

### 5.5 第五阶段: PM2 进程守护

```bash
# 安装 PM2
npm install -g pm2

# 创建 PM2 配置文件
cat > ~/ecosystem.config.js << 'EOF'
module.exports = {
  apps: [{
    name: 'openclaw',
    script: 'openclaw',
    args: 'gateway',
    max_memory_restart: '800M',
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
# 执行输出的命令 (类似: sudo env PATH=... pm2 startup systemd -u root --hp /root)
```

### 5.6 第六阶段: 验证部署

```bash
# 检查进程状态
pm2 status

# 检查端口监听
netstat -tlnp | grep 18789

# 检查内存使用
free -h

# 查看实时日志
pm2 logs openclaw --lines 50
```

**飞书测试**:
1. 打开飞书 App
2. 找到你的机器人
3. 发送消息测试
4. 确认收到回复

---

## 6. n8n 部署 (可选)

### 6.1 使用 Docker 安装

```bash
# 安装 Docker
curl -fsSL https://get.docker.com | sh

# 创建 n8n 数据目录
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

# 查看状态
docker ps
docker logs n8n
```

### 6.2 访问 n8n

```
http://你的服务器IP:5678
用户名: leo
密码: 你设置的密码
```

---

## 7. Dify 部署 (可选)

### 7.1 使用 Docker Compose 安装

```bash
# 克隆 Dify 仓库
git clone https://github.com/langgenius/dify.git
cd dify/docker

# 复制环境配置
cp .env.example .env

# 编辑配置 (设置密码等)
vim .env

# 启动 Dify
docker compose up -d

# 查看状态
docker compose ps
```

### 7.2 访问 Dify

```
http://你的服务器IP:3000
首次访问需要设置管理员账户
```

---

## 8. 完整架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                    Hostinger KVM 1 (4GB RAM)                    │
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   OpenClaw      │  │      n8n        │  │      Dify       │ │
│  │   (PM2 守护)    │  │   (Docker)      │  │   (Docker)      │ │
│  │   :18789        │  │   :5678         │  │   :3000         │ │
│  │   ~200MB RAM    │  │   ~300MB RAM    │  │   ~500MB RAM    │ │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘ │
│           │                    │                    │           │
│           └────────────────────┼────────────────────┘           │
│                                │                                │
│                         内部 API 调用                            │
│                                                                 │
│  预估内存使用: ~1.5GB / 4GB (剩余 2.5GB 余量)                    │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 │ WebSocket
                                 ▼
                    ┌─────────────────────────┐
                    │      飞书服务器          │
                    │   (open.feishu.cn)      │
                    └─────────────────────────┘
```

---

## 9. 常用运维命令

### 9.1 PM2 管理

```bash
pm2 status              # 查看状态
pm2 logs openclaw       # 查看日志
pm2 logs openclaw -f    # 实时日志
pm2 restart openclaw    # 重启
pm2 stop openclaw       # 停止
pm2 delete openclaw     # 删除
pm2 monit               # 监控面板
```

### 9.2 Docker 管理

```bash
docker ps               # 查看运行容器
docker logs n8n         # 查看 n8n 日志
docker restart n8n      # 重启 n8n
docker stop n8n         # 停止 n8n
```

### 9.3 系统监控

```bash
htop                    # 实时资源监控
free -h                 # 内存使用
df -h                   # 磁盘使用
netstat -tlnp           # 端口监听
```

### 9.4 健康检查脚本

```bash
# 创建健康检查脚本
cat > ~/health_check.sh << 'EOF'
#!/bin/bash
echo "=== 系统状态 ==="
echo "内存: $(free -h | grep Mem | awk '{print $3"/"$2}')"
echo "磁盘: $(df -h / | tail -1 | awk '{print $3"/"$2}')"
echo ""
echo "=== 服务状态 ==="
pm2 status
echo ""
echo "=== Docker 容器 ==="
docker ps --format "table {{.Names}}\t{{.Status}}"
echo ""
echo "=== 端口监听 ==="
netstat -tlnp | grep -E '18789|5678|3000'
EOF

chmod +x ~/health_check.sh

# 运行健康检查
~/health_check.sh
```

---

## 10. 故障排查

### 10.1 OpenClaw 无法连接飞书

```bash
# 检查进程
pm2 status

# 查看错误日志
pm2 logs openclaw --err --lines 100

# 重启服务
pm2 restart openclaw

# 检查配置文件
cat ~/.openclaw/openclaw.json
```

### 10.2 内存不足

```bash
# 查看内存使用
free -h

# 查看进程内存
ps aux --sort=-%mem | head -10

# 清理 Docker 缓存
docker system prune -a
```

### 10.3 服务自动重启

```bash
# 查看 PM2 重启记录
pm2 logs openclaw --lines 200

# 增加内存限制
# 编辑 ~/ecosystem.config.js
# 将 max_memory_restart 改为 '1G'
pm2 restart openclaw
```

---

## 11. 部署检查清单

- [ ] **购买服务器**
  - [ ] 访问 Hostinger 官网
  - [ ] 选择 KVM 1 套餐 (24个月)
  - [ ] 选择数据中心 (新加坡推荐)
  - [ ] 完成支付

- [ ] **服务器初始化**
  - [ ] SSH 连接成功
  - [ ] 系统更新完成
  - [ ] 时区设置正确

- [ ] **OpenClaw 部署**
  - [ ] Node.js 22 安装成功
  - [ ] OpenClaw 安装成功
  - [ ] 配置文件创建完成
  - [ ] PM2 守护进程启动
  - [ ] 开机自启设置完成

- [ ] **功能验证**
  - [ ] 飞书消息测试通过
  - [ ] Gateway 稳定运行 (观察 1 小时)

- [ ] **可选服务**
  - [ ] n8n 部署完成
  - [ ] Dify 部署完成
  - [ ] 三者集成测试通过

---

*文档创建于 2026-01-31*
