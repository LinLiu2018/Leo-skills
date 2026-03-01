# Vultr 云端部署指南

**创建时间**: 2026-02-26  
**优先级**: P1 (基础设施)  
**预计工时**: 1 天

---

## 一、服务器配置

### 推荐配置
| 项目 | 配置 | 月费 |
|------|------|------|
| 位置 | Vultr 美西 (Los Angeles) | - |
| 系统 | Ubuntu 22.04 LTS | - |
| CPU | 1 vCPU | - |
| 内存 | 2GB RAM | $12/月 |
| 存储 | 55GB NVMe | 包含 |
| 流量 | 2TB | 包含 |

### 创建步骤
1. 登录 https://my.vultr.com/
2. Deploy → New Server
3. 选择配置如上
4. 选择 SSH 密钥认证（推荐）或密码认证
5. 部署后记录 IP 地址

---

## 二、服务器初始化

### 1. SSH 连接
```bash
ssh root@<服务器 IP>
```

### 2. 系统更新
```bash
apt update && apt upgrade -y
```

### 3. 安装必要软件
```bash
# Node.js 20.x
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs

# Git
apt install -y git

# PM2
npm install -g pm2

# Python 3
apt install -y python3 python3-pip
```

---

## 三、OpenClaw 部署

### 1. 安装 OpenClaw
```bash
npm install -g openclaw@latest
```

### 2. 配置 OpenClaw
```bash
# 运行配置向导
openclaw onboard --install-daemon

# 或手动配置
mkdir -p ~/.openclaw
# 复制本地配置到服务器
```

### 3. 配置飞书机器人
```bash
# 编辑 ~/.openclaw/openclaw.json
# 添加飞书渠道配置（使用云端机器人 App ID）
```

### 4. 启动 Gateway
```bash
# 使用 PM2 守护
cd ~/.openclaw
pm2 start openclaw.mjs --name openclaw-gateway -- --port 18789

# 保存 PM2 配置
pm2 save

# 设置开机自启
pm2 startup
```

---

## 四、n8n 部署（可选）

### 1. 安装 n8n
```bash
npm install -g n8n
```

### 2. 启动 n8n
```bash
pm2 start n8n --name n8n -- start --port 5678
pm2 save
```

### 3. 访问 n8n
```
http://<服务器 IP>:5678
```

---

## 五、本地 + 云端双活配置

### 本地配置
- Gateway 端口：18789
- 飞书机器人：cli_a9f18849edbb9cb1 (本地开发)

### 云端配置
- Gateway 端口：18789
- 飞书机器人：cli_a9f7c17a65b89cd2 (生产环境)

### 切换方式
在飞书配置中切换 App ID，或使用不同机器人测试

---

## 六、监控与告警

### PM2 监控
```bash
# 查看状态
pm2 status

# 查看日志
pm2 logs openclaw-gateway

# 重启服务
pm2 restart openclaw-gateway
```

### 健康检查
```bash
# 检查端口
netstat -tlnp | grep 18789

# 检查进程
ps aux | grep openclaw
```

---

## 七、故障排查

| 问题 | 可能原因 | 解决方案 |
|------|----------|----------|
| Gateway 无法启动 | 端口被占用 | `lsof -i:18789` 查找并关闭 |
| 飞书连接失败 | 配置错误 | 检查 App ID/Secret |
| PM2 进程退出 | 内存不足 | 升级服务器或优化配置 |
| SSH 无法连接 | 防火墙 | 检查 Vultr 防火墙设置 |

---

## 八、成本优化

| 项目 | 月费 | 说明 |
|------|------|------|
| Vultr 服务器 | $12 | 2GB RAM 美西 |
| 域名（可选） | $1 | 可选 |
| **总计** | **~$13/月** | 约 ¥95/月 |

---

*部署完成后，测试本地 + 云端双活切换*
