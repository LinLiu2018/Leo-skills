# Leo AI System 生产环境部署方案

## 1. 系统架构概览

### 1.1 当前架构分析

```
┌─────────────────────────────────────────────────────────────┐
│                      前端层 (Frontend)                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  React 18 + TypeScript + Vite + Tailwind CSS        │   │
│  │  - 智能执行器 (SmartExecutor)                        │   │
│  │  - Skills/Agents/Workflows 管理界面                 │   │
│  │  - 意图调试、共享记忆、系统设置                      │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      API 层 (Backend)                        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  FastAPI (Python 3.9+)                              │   │
│  │  - REST API 接口                                    │   │
│  │  - 意图识别引擎                                     │   │
│  │  - 技能/代理/工作流执行                              │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    核心能力层 (Core)                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │ leo_skills  │  │ leo_agents  │  │ leo_workflows       │ │
│  │ (技能库)     │  │ (代理库)     │  │ (工作流定义)         │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │leo_orchestrator│ │leo_memory   │  │leo_knowledge        │ │
│  │ (编排引擎)   │  │ (共享记忆)   │  │ (知识库)            │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 生产架构设计

```
┌─────────────────────────────────────────────────────────────────┐
│                         负载均衡层 (Nginx)                       │
│              SSL 终止 / 静态资源缓存 / 反向代理                   │
└─────────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   前端服务 (2)   │  │   API 服务 (3)   │  │  WebSocket (1) │
│  (React + Nginx) │  │  (FastAPI/Uvicorn)│  │  (实时通知)     │
└─────────────────┘  └─────────────────┘  └─────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│    Redis 缓存    │  │   PostgreSQL    │  │   对象存储      │
│  - 会话状态      │  │  - 业务数据      │  │  - 文件上传      │
│  - 任务队列      │  │  - 执行日志      │  │  - 备份归档      │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

## 2. 部署方案选择

### 方案 A: 云服务器自建 (推荐中小型)

**适用场景**: 日均请求 < 10万, 团队规模 < 20人

**成本估算**: ￥500-2000/月

| 组件 | 推荐配置 | 月费用 |
|------|----------|--------|
| 云服务器 (2台) | 4核8G | ￥400 |
| 数据库 (RDS) | 2核4G | ￥200 |
| Redis | 1G 内存版 | ￥100 |
| 对象存储 (OSS) | 按量计费 | ￥50 |
| 带宽 | 10Mbps | ￥200 |

**优点**:
- 完全控制权
- 成本可控
- 灵活扩展

**缺点**:
- 需要运维知识
- 自行处理高可用

---

### 方案 B: 容器化部署 (K8s)

**适用场景**: 日均请求 > 10万, 需要自动扩缩容

**成本估算**: ￥2000-5000/月

**架构**:
```yaml
# k8s-deployment.yaml 概览
- Frontend: Deployment (3 replicas) + Service
- API: Deployment (3 replicas) + Service
- Worker: Deployment (2 replicas) for async tasks
- Redis: StatefulSet (1 master + 2 slave)
- PostgreSQL: Cloud RDS (managed)
```

**优点**:
- 自动扩缩容
- 高可用性
- 易于 CI/CD

**缺点**:
- 学习成本高
- 基础设施复杂

---

### 方案 C: Serverless (快速启动)

**适用场景**: MVP 阶段, 流量不确定

**成本估算**: ￥0-1000/月 (按量)

| 组件 | 服务 | 计费方式 |
|------|------|----------|
| 前端 | Vercel/Netlify | 免费-￥100 |
| API | Vercel Functions / AWS Lambda | 按调用次数 |
| 数据库 | Supabase / PlanetScale | 免费-￥200 |
| 存储 | Cloudflare R2 | 按量 |

**优点**:
- 零运维
- 按需付费
- 全球 CDN

**缺点**:
- 冷启动延迟
- 厂商锁定风险

## 3. 推荐部署方案 (方案 A 详细版)

### 3.1 服务器规划

```
服务器 A (前端 + API):
- CPU: 4核
- 内存: 8GB
- 磁盘: 100GB SSD
- 系统: Ubuntu 22.04 LTS

服务器 B (数据库 + 缓存):
- CPU: 2核
- 内存: 4GB
- 磁盘: 200GB SSD
- 系统: Ubuntu 22.04 LTS
```

### 3.2 部署目录结构

```
/opt/leo-ai-system/
├── docker-compose.yml          # 容器编排
├── .env                        # 环境变量
├── nginx/
│   ├── nginx.conf             # Nginx 主配置
│   └── conf.d/
│       └── leo.conf           # 站点配置
├── frontend/
│   └── dist/                  # 构建后的前端文件
├── backend/
│   ├── api/                   # FastAPI 代码
│   ├── src/                   # leo_skills 等核心代码
│   └── requirements.txt
├── data/
│   ├── postgres/              # 数据库数据
│   ├── redis/                 # 缓存数据
│   └── uploads/               # 上传文件
└── logs/
    ├── nginx/
    ├── api/
    └── worker/
```

### 3.3 Docker Compose 配置

```yaml
# docker-compose.yml
version: '3.8'

services:
  # 前端服务 (Nginx)
  frontend:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./frontend/dist:/usr/share/nginx/html:ro
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      - ./logs/nginx:/var/log/nginx
    depends_on:
      - api
    restart: unless-stopped

  # API 服务 (FastAPI)
  api:
    build:
      context: .
      dockerfile: Dockerfile.api
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://leo:${DB_PASSWORD}@postgres:5432/leo
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY}
      - ENV=production
    volumes:
      - ./backend:/app
      - ./data/uploads:/app/uploads
      - ./logs/api:/app/logs
    depends_on:
      - postgres
      - redis
    restart: unless-stopped
    command: uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4

  # 异步任务 Worker
  worker:
    build:
      context: .
      dockerfile: Dockerfile.api
    environment:
      - DATABASE_URL=postgresql://leo:${DB_PASSWORD}@postgres:5432/leo
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - ./backend:/app
    depends_on:
      - postgres
      - redis
    restart: unless-stopped
    command: celery -A api.worker worker --loglevel=info --concurrency=2

  # PostgreSQL 数据库
  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=leo
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_DB=leo
    volumes:
      - ./data/postgres:/var/lib/postgresql/data
    restart: unless-stopped

  # Redis 缓存
  redis:
    image: redis:7-alpine
    volumes:
      - ./data/redis:/data
    restart: unless-stopped

  # 定时任务调度器
  scheduler:
    build:
      context: .
      dockerfile: Dockerfile.api
    environment:
      - DATABASE_URL=postgresql://leo:${DB_PASSWORD}@postgres:5432/leo
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - ./backend:/app
    depends_on:
      - postgres
      - redis
    restart: unless-stopped
    command: celery -A api.worker beat --loglevel=info
```

## 4. 实施步骤

### Phase 1: 基础设施准备 (1-2 天)

- [ ] 购买云服务器
- [ ] 配置域名和 DNS
- [ ] 申请 SSL 证书 (Let's Encrypt)
- [ ] 配置安全组/防火墙

### Phase 2: 代码改造 (3-5 天)

- [ ] 创建 Dockerfile.api
- [ ] 添加数据库模型 (PostgreSQL)
- [ ] 实现异步任务队列 (Celery + Redis)
- [ ] 添加配置管理 (环境变量)
- [ ] 实现健康检查接口
- [ ] 添加日志收集 (结构化日志)

### Phase 3: 部署上线 (2-3 天)

- [ ] 安装 Docker & Docker Compose
- [ ] 配置 Nginx 反向代理
- [ ] 部署数据库和缓存
- [ ] 部署 API 服务
- [ ] 部署前端服务
- [ ] 配置 SSL/HTTPS
- [ ] 配置自动备份

### Phase 4: 监控与运维 (1-2 天)

- [ ] 部署 Prometheus + Grafana
- [ ] 配置告警规则
- [ ] 设置日志聚合 (ELK/Loki)
- [ ] 编写运维手册

## 5. 关键代码改造清单

### 5.1 数据库模型设计

```python
# models.py
from sqlalchemy import create_engine, Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True)
    hashed_password = Column(String(255))
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String(200))
    messages = Column(JSON)  # 存储消息列表
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ExecutionLog(Base):
    __tablename__ = "execution_logs"
    id = Column(Integer, primary_key=True)
    task_type = Column(String(50))  # skill/agent/workflow
    task_name = Column(String(100))
    status = Column(String(20))  # running/success/failed
    input_data = Column(JSON)
    output_data = Column(JSON)
    execution_time_ms = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
```

### 5.2 异步任务队列

```python
# worker.py
from celery import Celery
from celery.signals import task_failure
import logging

logger = logging.getLogger(__name__)

celery_app = Celery("leo_tasks", broker="redis://redis:6379/0")

@celery_app.task(bind=True, max_retries=3)
def execute_skill_async(self, skill_name: str, method: str, params: dict):
    """异步执行技能"""
    try:
        # 导入并执行技能
        result = execute_skill(skill_name, method, params)
        # 保存执行日志
        save_execution_log("skill", skill_name, "success", params, result)
        return result
    except Exception as exc:
        logger.error(f"Skill execution failed: {exc}")
        # 重试逻辑
        raise self.retry(exc=exc, countdown=60)

@celery_app.task
def monitor_system_health():
    """定时系统健康检查"""
    # 检查各组件状态
    pass

# 定时任务配置
@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(300.0, monitor_system_health.s(), name='health-check')
```

### 5.3 配置文件

```python
# config.py
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "Leo AI System"
    DEBUG: bool = False
    ENV: str = "production"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key")

    # 数据库
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://leo:password@localhost/leo")

    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # API 配置
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    WORKERS: int = 4

    # 安全
    CORS_ORIGINS: list = ["https://your-domain.com"]
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # 存储
    UPLOAD_DIR: str = "/app/uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB

    class Config:
        env_file = ".env"

settings = Settings()
```

## 6. 监控与告警

### 6.1 监控指标

```yaml
# 应用层指标
- api_requests_total: API 请求总数
- api_request_duration_seconds: 请求处理时间
- api_errors_total: 错误总数
- skill_executions_total: 技能执行次数
- skill_execution_duration_seconds: 技能执行时间
- active_conversations: 活跃对话数

# 系统层指标
- cpu_usage_percent: CPU 使用率
- memory_usage_percent: 内存使用率
- disk_usage_percent: 磁盘使用率
- network_io_bytes: 网络流量
```

### 6.2 告警规则

```yaml
# 关键告警
- 服务宕机: up == 0 for 1m
- 高错误率: rate(api_errors_total[5m]) > 0.05
- 慢响应: api_request_duration_seconds > 5s
- 磁盘满: disk_usage_percent > 85%
- 内存高: memory_usage_percent > 90%
```

## 7. 运维手册

### 7.1 日常维护命令

```bash
# 查看服务状态
docker-compose ps
docker-compose logs -f api

# 重启服务
docker-compose restart api
docker-compose up -d --force-recreate api

# 数据库备份
docker-compose exec postgres pg_dump -U leo leo > backup_$(date +%Y%m%d).sql

# 查看资源使用
docker stats

# 更新部署
git pull
docker-compose build api
docker-compose up -d
```

### 7.2 故障排查

```bash
# API 服务无法启动
docker-compose logs api | tail -100

# 数据库连接失败
docker-compose exec api nc -zv postgres 5432

# 性能问题
# 1. 检查慢查询
# 2. 查看 Redis 内存使用
# 3. 检查 API 响应时间
```

## 8. 成本优化建议

1. **数据库**: 初期可使用云厂商免费额度，数据量大时再升级
2. **存储**: 使用对象存储 + CDN 加速静态资源
3. **计算**: 非高峰时段可缩容 Worker 节点
4. **监控**: 使用云厂商基础监控，高级功能后期再加

## 9. 扩展路线图

### Phase 1 (当前): 单实例部署
- 所有服务部署在一台服务器
- 适合日活 < 1000

### Phase 2: 分离部署
- 前端、API、数据库分离到不同服务器
- 添加负载均衡
- 适合日活 1000-10000

### Phase 3: 高可用架构
- 多实例部署 + K8s
- 数据库主从复制
- 适合日活 > 10000

---

**下一步行动**:
1. 确认选择的部署方案 (A/B/C)
2. 准备云服务器/账号
3. 开始 Phase 1 基础设施准备
