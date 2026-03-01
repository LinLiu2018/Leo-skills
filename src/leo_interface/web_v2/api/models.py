"""
数据库模型 - 使用SQLAlchemy
支持SQLite(开发)和PostgreSQL(生产)
"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, JSON, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from datetime import datetime
from typing import Optional, List, Dict, Any
import os

Base = declarative_base()

# 数据库URL - 优先使用PostgreSQL，否则使用SQLite
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./leo_system.db"
)

# 创建引擎
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class ConversationDB(Base):
    """对话历史表"""
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), default="新对话")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联消息
    messages = relationship("MessageDB", back_populates="conversation", cascade="all, delete-orphan")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "messages": [msg.to_dict() for msg in self.messages]
        }


class MessageDB(Base):
    """消息表"""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    role = Column(String(20), nullable=False)  # user / system / agent / skill / workflow
    content = Column(Text, nullable=False)
    metadata_json = Column(JSON, default=dict)  # 额外元数据
    created_at = Column(DateTime, default=datetime.utcnow)

    conversation = relationship("ConversationDB", back_populates="messages")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "role": self.role,
            "content": self.content,
            "metadata": self.metadata_json or {},
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class ExecutionLogDB(Base):
    """执行日志表 - 记录所有技能/代理/工作流的执行"""
    __tablename__ = "execution_logs"

    id = Column(Integer, primary_key=True, index=True)
    task_type = Column(String(50), nullable=False)  # skill / agent / workflow
    task_name = Column(String(100), nullable=False)
    status = Column(String(20), nullable=False)  # running / success / failed
    input_data = Column(JSON, default=dict)
    output_data = Column(JSON, default=dict)
    execution_time_ms = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "task_type": self.task_type,
            "task_name": self.task_name,
            "status": self.status,
            "input": self.input_data,
            "output": self.output_data,
            "execution_time_ms": self.execution_time_ms,
            "error": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class VideoAccountDB(Base):
    """视频号账号表 - 存储真实监测的账号数据"""
    __tablename__ = "video_accounts"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(String(100), unique=True, index=True, nullable=False)
    account_name = Column(String(200), nullable=False)
    city = Column(String(50), nullable=True)
    category = Column(String(50), nullable=True)
    followers = Column(Integer, default=0)
    videos_count = Column(Integer, default=0)
    avg_views = Column(Integer, default=0)
    avg_likes = Column(Integer, default=0)
    last_updated = Column(DateTime, default=datetime.utcnow)

    # 历史数据记录
    history = relationship("VideoAccountHistoryDB", back_populates="account", cascade="all, delete-orphan")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "account_id": self.account_id,
            "account_name": self.account_name,
            "city": self.city,
            "category": self.category,
            "followers": self.followers,
            "videos_count": self.videos_count,
            "avg_views": self.avg_views,
            "avg_likes": self.avg_likes,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None
        }


class VideoAccountHistoryDB(Base):
    """视频号账号历史数据表"""
    __tablename__ = "video_account_history"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("video_accounts.id"), nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    followers = Column(Integer, default=0)
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)

    account = relationship("VideoAccountDB", back_populates="history")


# 初始化数据库
def init_db():
    """创建所有表"""
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
    print("数据库初始化完成")
