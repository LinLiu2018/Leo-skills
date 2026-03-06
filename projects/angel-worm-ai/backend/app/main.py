# 主入口文件
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api import auth, accounts, content, publish, auto_ops, private_domain, analytics, ai_command
from app.core.config import settings
from app.db.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    await init_db()
    yield
    # 关闭时清理


app = FastAPI(
    title="天使虫AI操盘手系统",
    description="全链路AI数字员工操作系统 API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(accounts.router, prefix="/api/accounts", tags=["账号管理"])
app.include_router(content.router, prefix="/api/content", tags=["内容创作"])
app.include_router(publish.router, prefix="/api/publish", tags=["智能发布"])
app.include_router(auto_ops.router, prefix="/api/auto-ops", tags=["自动化运营"])
app.include_router(private_domain.router, prefix="/api/private", tags=["私域管理"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["数据分析"])
app.include_router(ai_command.router, prefix="/api/ai", tags=["AI指令"])


@app.get("/")
async def root():
    return {
        "message": "天使虫AI操盘手系统 API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
