# 数据库配置
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool

from app.core.config import settings

# 创建异步引擎
engine = create_async_engine(
    settings.DATABASE_URL.replace('pymysql', 'aiomysql'),
    echo=settings.DEBUG,
    poolclass=NullPool,
)

# 异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# 声明基类
Base = declarative_base()


async def init_db():
    """初始化数据库"""
    async with engine.begin() as conn:
        # 开发环境下创建表
        # await conn.run_sync(Base.metadata.create_all)
        pass


async def get_db():
    """获取数据库会话"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
