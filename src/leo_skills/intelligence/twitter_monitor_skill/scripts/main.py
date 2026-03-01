"""Twitter monitor core module."""

from __future__ import annotations

from datetime import datetime
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from dotenv import load_dotenv

if __package__:
    try:
        from .analyzers.deduplicator import Deduplicator  # type: ignore
    except Exception:
        class Deduplicator:  # type: ignore[no-redef]
            def __init__(self, config: Dict[str, Any]):
                self.config = config

            def deduplicate(self, tweets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
                return tweets

    try:
        from .collectors.twitter_collector import TwitterCollector  # type: ignore
    except Exception:
        class TwitterCollector:  # type: ignore[no-redef]
            def __init__(self, config: Dict[str, Any]):
                self.config = config

            def collect_user_tweets(self, username: str, max_results: int = 100) -> List[Dict[str, Any]]:
                return []

            def search_tweets(self, query: str, max_results: int = 100) -> List[Dict[str, Any]]:
                return []

    from .models.database import Database, Tweet
else:
    from scripts.analyzers.deduplicator import Deduplicator
    from scripts.collectors.twitter_collector import TwitterCollector
    from scripts.models.database import Database, Tweet


class TwitterMonitor:
    """Monitor tweets from configured bloggers and persist to local DB."""

    def __init__(self, config_path: Optional[str] = None):
        load_dotenv()

        if config_path is None:
            config_path = str(Path(__file__).parent.parent / "config" / "config.yaml")

        self.config: Dict[str, Any] = {}
        config_file = Path(config_path)
        if config_file.exists():
            with open(config_file, "r", encoding="utf-8") as handle:
                self.config = yaml.safe_load(handle) or {}

        self._replace_env_vars(self.config)

        db_path = self.config.get("database", {}).get(
            "path",
            str(Path(__file__).parent.parent / "data" / "twitter_monitor.db"),
        )
        self.db = Database(db_path)

        self.collector = TwitterCollector(self.config)
        self.deduplicator = Deduplicator(self.config)

        bloggers_path = Path(__file__).parent.parent / "config" / "bloggers.yaml"
        self.bloggers: List[Dict[str, Any]] = []
        if bloggers_path.exists():
            with open(bloggers_path, "r", encoding="utf-8") as handle:
                bloggers_config = yaml.safe_load(handle) or {}
                self.bloggers = bloggers_config.get("bloggers", [])

    def _replace_env_vars(self, config: Dict[str, Any]) -> None:
        for key, value in config.items():
            if isinstance(value, dict):
                self._replace_env_vars(value)
            elif isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                env_var = value[2:-1]
                config[key] = os.getenv(env_var, "")

    def monitor(self, bloggers: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        if bloggers is None:
            bloggers = [item for item in self.bloggers if item.get("enabled", True)]

        all_tweets: List[Dict[str, Any]] = []
        max_tweets = int(self.config.get("monitoring", {}).get("max_tweets_per_user", 100))

        for blogger in bloggers:
            username = blogger.get("username")
            if not username:
                continue
            tweets = self.collector.collect_user_tweets(username=username, max_results=max_tweets)
            for tweet in tweets:
                tweet["blogger_category"] = blogger.get("category")
                tweet["priority"] = blogger.get("priority", 5)
            all_tweets.extend(tweets)

        unique_tweets = self.deduplicator.deduplicate(all_tweets)
        for tweet in unique_tweets:
            self.db.save_tweet(tweet)
        return unique_tweets

    def search_by_keywords(self, keywords: List[str], max_results: int = 100) -> List[Dict[str, Any]]:
        if not keywords:
            return []

        query = " OR ".join(keywords)
        tweets = self.collector.search_tweets(query=query, max_results=max_results)
        unique_tweets = self.deduplicator.deduplicate(tweets)

        for tweet in unique_tweets:
            self.db.save_tweet(tweet)
        return unique_tweets

    def get_unprocessed_tweets(self, limit: int = 100) -> List[Dict[str, Any]]:
        tweets = self.db.get_tweets(processed=False, limit=limit)
        return [tweet.to_dict() for tweet in tweets]

    def mark_as_processed(self, tweet_ids: List[str]) -> None:
        self.db.mark_as_processed(tweet_ids)

    def cleanup_old_tweets(self, days: Optional[int] = None) -> None:
        if days is None:
            days = int(self.config.get("database", {}).get("retention_days", 90))
        if days > 0:
            self.db.cleanup_old_tweets(days)

    def get_stats(self) -> Dict[str, Any]:
        session = self.db.get_session()
        try:
            total_tweets = session.query(Tweet).count()
            processed_tweets = session.query(Tweet).filter_by(processed=True).count()
            unprocessed_tweets = total_tweets - processed_tweets

            author_stats: Dict[str, int] = {}
            for blogger in self.bloggers:
                username = blogger.get("username")
                if not username:
                    continue
                count = session.query(Tweet).filter_by(author_username=username).count()
                author_stats[username] = count

            return {
                "total_tweets": total_tweets,
                "processed_tweets": processed_tweets,
                "unprocessed_tweets": unprocessed_tweets,
                "author_stats": author_stats,
                "generated_at": datetime.now().isoformat(),
            }
        finally:
            session.close()


def main() -> None:
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Twitter monitor utility")
    parser.add_argument("--mode", choices=["monitor", "search", "stats"], default="monitor")
    parser.add_argument("--keywords", nargs="+", default=[])
    parser.add_argument("--max-results", type=int, default=100)
    parser.add_argument("--cleanup", action="store_true")
    args = parser.parse_args()

    monitor = TwitterMonitor()

    if args.mode == "monitor":
        data = monitor.monitor()
    elif args.mode == "search":
        data = monitor.search_by_keywords(args.keywords, args.max_results)
    else:
        data = monitor.get_stats()

    if args.cleanup:
        monitor.cleanup_old_tweets()

    print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
