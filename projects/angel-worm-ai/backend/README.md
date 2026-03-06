# 天使虫AI操盘手系统 - 后端服务

## 技术栈
- Python 3.10+
- FastAPI - 高性能异步Web框架
- SQLAlchemy 2.0 - ORM
- MySQL - 关系型数据库
- ChromaDB - 向量数据库
- Redis - 缓存和消息队列
- Celery - 异步任务队列

## 项目结构
```
backend/
├── app/
│   ├── api/            # API路由
│   │   ├── auth.py
│   │   ├── accounts.py
│   │   ├── content.py
│   │   ├── publish.py
│   │   ├── auto_ops.py
│   │   ├── private_domain.py
│   │   ├── analytics.py
│   │   └── ai_command.py
│   ├── core/           # 核心配置
│   │   └── config.py
│   ├── db/             # 数据库
│   │   └── database.py
│   ├── models/         # ORM模型
│   ├── schemas/        # Pydantic模型
│   ├── services/       # 业务服务
│   └── utils/          # 工具函数
├── tests/              # 测试文件
├── requirements.txt    # 依赖列表
└── main.py            # 启动入口
```

## 安装依赖
```bash
pip install -r requirements.txt
```

## 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，配置相关参数
```

## 启动服务
```bash
# 开发模式
uvicorn app.main:app --reload --port 8000

# 生产模式
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API文档
启动服务后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 数据库迁移
```bash
# 创建迁移
alembic revision --autogenerate -m "描述"

# 执行迁移
alembic upgrade head
```
