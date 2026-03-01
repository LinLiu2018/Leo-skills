"""Database models for twitter monitor."""

from __future__ import annotations

from datetime import datetime, timedelta
import os
from typing import Any, Dict, List, Optional

from sqlalchemy import Boolean, Column, DateTime, Integer, JSON, String, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


class Tweet(Base):
    __tablename__ = "tweets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tweet_id = Column(String(50), unique=True, nullable=False, index=True)
    author_username = Column(String(100), nullable=False, index=True)
    author_id = Column(String(50))
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, index=True)
    url = Column(String(500))

    likes = Column(Integer, default=0)
    retweets = Column(Integer, default=0)
    replies = Column(Integer, default=0)
    quotes = Column(Integer, default=0)

    language = Column(String(10))
    is_retweet = Column(Boolean, default=False)
    is_reply = Column(Boolean, default=False)
    tweet_metadata = Column("metadata", JSON)

    collected_at = Column(DateTime, default=datetime.now)
    processed = Column(Boolean, default=False)
    priority = Column(Integer, default=5)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "tweet_id": self.tweet_id,
            "author_username": self.author_username,
            "author_id": self.author_id,
            "content": self.content,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "url": self.url,
            "likes": self.likes,
            "retweets": self.retweets,
            "replies": self.replies,
            "quotes": self.quotes,
            "language": self.language,
            "is_retweet": self.is_retweet,
            "is_reply": self.is_reply,
            "metadata": self.tweet_metadata,
            "collected_at": self.collected_at.isoformat() if self.collected_at else None,
            "processed": self.processed,
            "priority": self.priority,
        }


class Database:
    def __init__(self, db_path: str = "data/twitter_monitor.db"):
        directory = os.path.dirname(db_path)
        if directory:
            os.makedirs(directory, exist_ok=True)

        self.engine = create_engine(f"sqlite:///{db_path}", echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def get_session(self):
        return self.Session()

    def save_tweet(self, tweet_data: Dict[str, Any]) -> Optional[Tweet]:
        session = self.get_session()
        try:
            existing = session.query(Tweet).filter_by(tweet_id=tweet_data["tweet_id"]).first()
            if existing:
                existing.likes = tweet_data.get("likes", existing.likes)
                existing.retweets = tweet_data.get("retweets", existing.retweets)
                existing.replies = tweet_data.get("replies", existing.replies)
                existing.quotes = tweet_data.get("quotes", existing.quotes)
                session.commit()
                return existing

            if "metadata" in tweet_data and "tweet_metadata" not in tweet_data:
                tweet_data = dict(tweet_data)
                tweet_data["tweet_metadata"] = tweet_data.pop("metadata")

            tweet = Tweet(**tweet_data)
            session.add(tweet)
            session.commit()
            return tweet
        except Exception:
            session.rollback()
            return None
        finally:
            session.close()

    def get_tweets(self, author_username: Optional[str] = None, limit: int = 100, processed: Optional[bool] = None) -> List[Tweet]:
        session = self.get_session()
        try:
            query = session.query(Tweet)
            if author_username:
                query = query.filter_by(author_username=author_username)
            if processed is not None:
                query = query.filter_by(processed=processed)
            return query.order_by(Tweet.created_at.desc()).limit(limit).all()
        finally:
            session.close()

    def mark_as_processed(self, tweet_ids: List[str]) -> None:
        session = self.get_session()
        try:
            session.query(Tweet).filter(Tweet.tweet_id.in_(tweet_ids)).update({"processed": True}, synchronize_session=False)
            session.commit()
        except Exception:
            session.rollback()
        finally:
            session.close()

    def cleanup_old_tweets(self, days: int = 90) -> None:
        session = self.get_session()
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            session.query(Tweet).filter(Tweet.created_at < cutoff_date).delete()
            session.commit()
        except Exception:
            session.rollback()
        finally:
            session.close()
