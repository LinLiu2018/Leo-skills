"""
数据库模型定义
定义 Tweet 和相关数据的数据库结构
"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, JSON, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()


class Tweet(Base):
    """推文模型"""
    __tablename__ = 'tweets'

    id = Column(Integer, primary_key=True, autoincrement=True)
    tweet_id = Column(String(50), unique=True, nullable=False, index=True)
    author_username = Column(String(100), nullable=False, index=True)
    author_id = Column(String(50))
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, index=True)
    url = Column(String(500))

    # 互动数据
    likes = Column(Integer, default=0)
    retweets = Column(Integer, default=0)
    replies = Column(Integer, default=0)
    quotes = Column(Integer, default=0)

    # 元数据
    language = Column(String(10))
    is_retweet = Column(Boolean, default=False)
    is_reply = Column(Boolean, default=False)
    metadata = Column(JSON)  # 存储额外信息

    # 系统字段
    collected_at = Column(DateTime, default=datetime.now)
    processed = Column(Boolean, default=False)
    priority = Column(Integer, default=5)

    def __repr__(self):
        return f"<Tweet(id={self.tweet_id}, author={self.author_username}, created_at={self.created_at})>"

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'tweet_id': self.tweet_id,
            'author_username': self.author_username,
            'author_id': self.author_id,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'url': self.url,
            'likes': self.likes,
            'retweets': self.retweets,
            'replies': self.replies,
            'quotes': self.quotes,
            'language': self.language,
            'is_retweet': self.is_retweet,
            'is_reply': self.is_reply,
            'metadata': self.metadata,
            'collected_at': self.collected_at.isoformat() if self.collected_at else None,
            'processed': self.processed,
            'priority': self.priority
        }


class Database:
    """数据库管理类"""

    def __init__(self, db_path='data/twitter_monitor.db'):
        """
        初始化数据库连接

        Args:
            db_path: 数据库文件路径
        """
        # 确保目录存在
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        # 创建引擎
        self.engine = create_engine(f'sqlite:///{db_path}', echo=False)

        # 创建表
        Base.metadata.create_all(self.engine)

        # 创建会话工厂
        self.Session = sessionmaker(bind=self.engine)

    def get_session(self):
        """获取数据库会话"""
        return self.Session()

    def save_tweet(self, tweet_data):
        """
        保存推文到数据库

        Args:
            tweet_data: 推文数据字典

        Returns:
            Tweet 对象或 None
        """
        session = self.get_session()
        try:
            # 检查是否已存在
            existing = session.query(Tweet).filter_by(
                tweet_id=tweet_data['tweet_id']
            ).first()

            if existing:
                # 更新互动数据
                existing.likes = tweet_data.get('likes', existing.likes)
                existing.retweets = tweet_data.get('retweets', existing.retweets)
                existing.replies = tweet_data.get('replies', existing.replies)
                existing.quotes = tweet_data.get('quotes', existing.quotes)
                session.commit()
                return existing

            # 创建新推文
            tweet = Tweet(**tweet_data)
            session.add(tweet)
            session.commit()
            return tweet

        except Exception as e:
            session.rollback()
            print(f"保存推文失败：{e}")
            return None
        finally:
            session.close()

    def get_tweets(self, author_username=None, limit=100, processed=None):
        """
        查询推文

        Args:
            author_username: 作者用户名（可选）
            limit: 返回数量限制
            processed: 是否已处理（可选）

        Returns:
            推文列表
        """
        session = self.get_session()
        try:
            query = session.query(Tweet)

            if author_username:
                query = query.filter_by(author_username=author_username)

            if processed is not None:
                query = query.filter_by(processed=processed)

            query = query.order_by(Tweet.created_at.desc()).limit(limit)

            return query.all()

        finally:
            session.close()

    def mark_as_processed(self, tweet_ids):
        """
        标记推文为已处理

        Args:
            tweet_ids: 推文 ID 列表
        """
        session = self.get_session()
        try:
            session.query(Tweet).filter(
                Tweet.tweet_id.in_(tweet_ids)
            ).update({'processed': True}, synchronize_session=False)
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"标记推文失败：{e}")
        finally:
            session.close()

    def cleanup_old_tweets(self, days=90):
        """
        清理旧推文

        Args:
            days: 保留天数
        """
        from datetime import timedelta

        session = self.get_session()
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            deleted = session.query(Tweet).filter(
                Tweet.created_at < cutoff_date
            ).delete()
            session.commit()
            print(f"清理了 {deleted} 条旧推文")
        except Exception as e:
            session.rollback()
            print(f"清理推文失败：{e}")
        finally:
            session.close()
