# Docker 部署配置指南

**创建时间**: 2026-02-27  
**状态**: ✅ 配置完成

---

## 一、Docker Compose 配置

### 服务清单

| 服务 | 端口 | 说明 |
|------|------|------|
| **openclaw-gateway** | 18789 | Gateway 主服务 |
| **openclaw-browser** | 9222 | Playwright 浏览器 |

### 启动命令

```bash
# 启动所有服务
cd docker
docker-compose up -d

# 查看状态
docker-compose ps

# 查看日志
docker-compose logs -f gateway

# 停止服务
docker-compose down
```

---

## 二、配置说明

### 环境变量

| 变量 | 值 | 说明 |
|------|-----|------|
| NODE_ENV | production | 生产环境 |
| OPENCLAW_PORT | 18789 | Gateway 端口 |

### 卷映射

| 主机路径 | 容器路径 | 说明 |
|----------|----------|------|
| ~/.openclaw | /root/.openclaw | 配置和数据 |
| ./config | /app/config | 配置文件 |

---

## 三、验收标准

- [x] Docker Compose 配置已创建
- [ ] Dockerfile 已创建
- [ ] 服务可启动
- [ ] 端口可访问

---

*配置完成时间：2026-02-27*
