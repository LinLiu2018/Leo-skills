# Leo AI System - 本地生产环境方案

让系统在本地就能真正实现功能，而非演示。

## 当前 vs 目标

| 功能 | 当前状态 | 目标状态 |
|------|----------|----------|
| 数据存储 | localStorage/内存 | SQLite数据库 |
| Agent回复 | 硬编码模板 | 调用AI模型生成 |
| 技能执行 | random随机数据 | 真实API调用 |
| 历史记录 | 浏览器存储 | 数据库存储 |
| 任务执行 | 同步阻塞 | 异步队列 |

## 架构改造

```
┌─────────────────────────────────────────────────────────────┐
│                      前端 (React)                            │
│              - 智能执行器、技能管理、意图调试                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    后端 (FastAPI)                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   API路由     │  │  Agent引擎   │  │  任务队列    │      │
│  │              │  │  (真实AI)    │  │  (Celery)   │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                 │                  │              │
│         └────────────┬────┴──────────────────┘              │
│                      ▼                                      │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              SQLite 数据库 (本地文件)                 │   │
│  │  - 用户数据                                           │   │
│  │  - 对话历史                                           │   │
│  │  - 执行日志                                           │   │
│  │  - 任务状态                                           │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  外部服务 (API Key)                          │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │ OpenAI API │  │ 搜索API    │  │ 其他API    │            │
│  │ (Agent大脑)│  │ (技能数据)  │  │ (扩展功能)  │            │
│  └────────────┘  └────────────┘  └────────────┘            │
└─────────────────────────────────────────────────────────────┘
```

## 改造清单

### Phase 1: 数据库层 (1-2天)

用 SQLite 替代所有内存/文件存储。

```python
# 数据模型
- User (用户表)
- Conversation (对话表)
- Message (消息表)
- ExecutionLog (执行日志表)
- ScheduledTask (定时任务表)
```

### Phase 2: Agent引擎 (2-3天)

让 Agent 真正"思考"而不是返回模板。

```python
# 当前
response = "作为研究员，我建议..."  # 硬编码

# 改造后
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "你是研究员Agent..."},
        {"role": "user", "content": user_message}
    ]
)
```

### Phase 3: 技能真实化 (2-3天)

让技能调用真实API或执行真实操作。

```python
# 当前: video_monitor
followers = random.randint(1000, 100000)  # 假数据

# 改造方案A: 调用真实API (需要申请Key)
followers = wechat_api.get_followers(account_id)

# 改造方案B: 本地数据爬取/导入
followers = local_db.query(Account).filter_by(id=account_id).first().followers
```

### Phase 4: 异步任务 (1-2天)

耗时任务后台执行，不阻塞前端。

```python
# 耗时操作放入后台
@celery_app.task
def execute_long_running_skill(skill_name, params):
    result = execute_skill(skill_name, params)
    # 完成后通知前端 (WebSocket/轮询)
```

## 实施步骤

### Step 1: 安装依赖

```bash
# 后端依赖
pip install sqlalchemy alembic celery redis openai

# 启动Redis (Windows)
redis-server

# 或 SQLite 模式 (无需Redis)
```

### Step 2: 数据库初始化

```bash
# 创建迁移
alembic init migrations

# 生成迁移脚本
alembic revision --autogenerate -m "init"

# 执行迁移
alembic upgrade head
```

### Step 3: 配置环境变量

```bash
# .env
DATABASE_URL=sqlite:///./leo.db
REDIS_URL=redis://localhost:6379/0
OPENAI_API_KEY=sk-...
SECRET_KEY=your-secret-key
```

### Step 4: 测试验证

```bash
# 1. 启动后端
cd api && python main.py

# 2. 启动前端
cd web_v2 && npm run dev

# 3. 启动Worker (另一个终端)
celery -A api.worker worker --loglevel=info
```

## 关键代码改造

### 1. 数据库模型

```python
# models.py
from sqlalchemy import create_engine, Column, Integer, String, DateTime, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()
engine = create_engine("sqlite:///./leo.db", connect_args={"check_same_thread": False})

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True)
    title = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    messages = Column(JSON, default=list)  # [{role, content, timestamp}, ...]
```

### 2. Agent真实执行

```python
# agent_engine.py
import openai
from typing import List, Dict

class RealAgent:
    """真正能执行任务的Agent"""

    def __init__(self, role: str, system_prompt: str):
        self.role = role
        self.system_prompt = system_prompt

    async def execute(self, user_message: str, context: List[Dict] = None) -> str:
        """调用AI模型生成回复"""
        messages = [{"role": "system", "content": self.system_prompt}]

        if context:
            messages.extend(context)

        messages.append({"role": "user", "content": user_message})

        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7
        )

        return response.choices[0].message.content

# 预定义Agent角色
AGENTS = {
    "research_agent": RealAgent(
        role="researcher",
        system_prompt="""你是研究员Agent，擅长：
1. 深度研究和信息收集
2. 数据分析和趋势判断
3. 撰写研究报告
请用中文回复，提供结构化、有深度的分析。"""
    ),
    "creative_agent": RealAgent(
        role="creator",
        system_prompt="""你是创意设计师Agent，擅长：
1. 内容创意和策划
2. 文案撰写
3. 视觉设计建议
请提供创新、实用的创意方案。"""
    ),
    # ... 更多Agent
}
```

### 3. 技能真实数据源

```python
# 方案A: 本地数据采集
class VideoMonitorSkill:
    def __init__(self):
        self.db = SessionLocal()

    def monitor_account(self, account_id: str):
        # 从本地数据库查询
        account = self.db.query(VideoAccount).filter_by(id=account_id).first()
        if not account:
            # 如果本地没有，尝试爬取或返回提示
            return {"error": "账号未收录，请先添加监测列表"}

        return {
            "account_id": account_id,
            "followers": account.followers,
            "videos": account.videos,
            # ... 真实数据
        }

    def add_account(self, account_data: dict):
        """手动添加账号到监测列表"""
        account = VideoAccount(**account_data)
        self.db.add(account)
        self.db.commit()
```

## 验证清单

- [ ] 对话历史存入数据库，重启不丢失
- [ ] Agent回复是AI生成的，不是模板
- [ ] 技能返回真实数据（哪怕是手动录入的）
- [ ] 耗时任务在后台执行
- [ ] 可以同时处理多个用户请求
- [ ] 系统有完整的日志记录

## 下一步

1. 确认采用此方案
2. 我帮你创建数据库模型
3. 改造Agent引擎
4. 逐个技能真实化
