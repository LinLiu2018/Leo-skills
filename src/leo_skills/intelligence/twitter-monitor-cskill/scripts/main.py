"""
Twitter Monitor Skill - 主入口
监控 Twitter 上的 AI 科技博主，采集最新推文
"""

import os
import sys
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# 导入模块
from scripts.collectors.twitter_collector import TwitterCollector
from scripts.analyzers.deduplicator import Deduplicator
from scripts.models.database import Database


class TwitterMonitor:
    """Twitter 监控器"""

    def __init__(self, config_path: str = None):
        """
        初始化 Twitter 监控器

        Args:
            config_path: 配置文件路径（可选）
        """
        # 加载环境变量
        load_dotenv()

        # 确定配置文件路径
        if config_path is None:
            config_path = Path(__file__).parent.parent / 'config' / 'config.yaml'

        # 加载配置
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

        # 替换环境变量
        self._replace_env_vars(self.config)

        # 初始化组件
        self.collector = TwitterCollector(self.config)
        self.deduplicator = Deduplicator(self.config)

        # 初始化数据库
        db_path = self.config.get('database', {}).get('path', 'data/twitter_monitor.db')
        self.db = Database(db_path)

        # 加载博主列表
        bloggers_path = Path(__file__).parent.parent / 'config' / 'bloggers.yaml'
        with open(bloggers_path, 'r', encoding='utf-8') as f:
            bloggers_config = yaml.safe_load(f)
            self.bloggers = bloggers_config.get('bloggers', [])

    def _replace_env_vars(self, config: Dict[str, Any]):
        """
        递归替换配置中的环境变量

        Args:
            config: 配置字典
        """
        for key, value in config.items():
            if isinstance(value, dict):
                self._replace_env_vars(value)
            elif isinstance(value, str) and value.startswith('${') and value.endswith('}'):
                env_var = value[2:-1]
                config[key] = os.getenv(env_var, '')

    def monitor(self, bloggers: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        监控指定博主

        Args:
            bloggers: 博主列表（可选，默认使用配置文件中的列表）

        Returns:
            采集到的推文列表
        """
        if bloggers is None:
            # 只监控启用的博主
            bloggers = [b for b in self.bloggers if b.get('enabled', True)]

        print(f"\n{'='*60}")
        print(f"开始监控 {len(bloggers)} 个博主")
        print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")

        all_tweets = []

        for blogger in bloggers:
            username = blogger.get('username')
            if not username:
                continue

            print(f"\n监控博主：{username} ({blogger.get('display_name', username)})")
            print(f"分类：{blogger.get('category', 'unknown')}")
            print(f"优先级：{blogger.get('priority', 5)}")

            # 采集推文
            tweets = self.collector.collect_user_tweets(
                username=username,
                max_results=self.config.get('monitoring', {}).get('max_tweets_per_user', 100)
            )

            # 添加博主信息
            for tweet in tweets:
                tweet['blogger_category'] = blogger.get('category')
                tweet['priority'] = blogger.get('priority', 5)

            all_tweets.extend(tweets)

        print(f"\n{'='*60}")
        print(f"采集完成，共 {len(all_tweets)} 条推文")
        print(f"{'='*60}\n")

        # 去重
        unique_tweets = self.deduplicator.deduplicate(all_tweets)

        # 保存到数据库
        saved_count = 0
        for tweet in unique_tweets:
            if self.db.save_tweet(tweet):
                saved_count += 1

        print(f"\n保存到数据库：{saved_count} 条新推文")

        return unique_tweets

    def search_by_keywords(
        self,
        keywords: List[str],
        max_results: int = 100
    ) -> List[Dict[str, Any]]:
        """
        按关键词搜索推文

        Args:
            keywords: 关键词列表
            max_results: 最大结果数

        Returns:
            搜索到的推文列表
        """
        print(f"\n{'='*60}")
        print(f"搜索关键词：{', '.join(keywords)}")
        print(f"{'='*60}\n")

        # 构建查询
        query = " OR ".join(keywords)

        # 搜索推文
        tweets = self.collector.search_tweets(query, max_results)

        # 去重
        unique_tweets = self.deduplicator.deduplicate(tweets)

        # 保存到数据库
        saved_count = 0
        for tweet in unique_tweets:
            if self.db.save_tweet(tweet):
                saved_count += 1

        print(f"\n保存到数据库：{saved_count} 条新推文")

        return unique_tweets

    def get_unprocessed_tweets(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        获取未处理的推文

        Args:
            limit: 返回数量限制

        Returns:
            未处理的推文列表
        """
        tweets = self.db.get_tweets(processed=False, limit=limit)
        return [tweet.to_dict() for tweet in tweets]

    def mark_as_processed(self, tweet_ids: List[str]):
        """
        标记推文为已处理

        Args:
            tweet_ids: 推文 ID 列表
        """
        self.db.mark_as_processed(tweet_ids)
        print(f"已标记 {len(tweet_ids)} 条推文为已处理")

    def cleanup_old_tweets(self, days: int = None):
        """
        清理旧推文

        Args:
            days: 保留天数（可选，默认使用配置值）
        """
        if days is None:
            days = self.config.get('database', {}).get('retention_days', 90)

        if days > 0:
            self.db.cleanup_old_tweets(days)

    def get_stats(self) -> Dict[str, Any]:
        """
        获取统计信息

        Returns:
            统计信息字典
        """
        session = self.db.get_session()
        try:
            from scripts.models.database import Tweet

            total_tweets = session.query(Tweet).count()
            processed_tweets = session.query(Tweet).filter_by(processed=True).count()
            unprocessed_tweets = total_tweets - processed_tweets

            # 按作者统计
            author_stats = {}
            for blogger in self.bloggers:
                username = blogger.get('username')
                count = session.query(Tweet).filter_by(author_username=username).count()
                author_stats[username] = count

            return {
                'total_tweets': total_tweets,
                'processed_tweets': processed_tweets,
                'unprocessed_tweets': unprocessed_tweets,
                'author_stats': author_stats
            }

        finally:
            session.close()


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description='Twitter Monitor - 监控 AI 科技博主')
    parser.add_argument('--mode', choices=['monitor', 'search', 'stats'], default='monitor',
                        help='运行模式：monitor（监控博主）、search（关键词搜索）、stats（统计信息）')
    parser.add_argument('--keywords', nargs='+', help='搜索关键词（search 模式）')
    parser.add_argument('--max-results', type=int, default=100, help='最大结果数')
    parser.add_argument('--cleanup', action='store_true', help='清理旧推文')

    args = parser.parse_args()

    # 初始化监控器
    monitor = TwitterMonitor()

    if args.mode == 'monitor':
        # 监控博主
        tweets = monitor.monitor()
        print(f"\n[SUCCESS] 监控完成，采集到 {len(tweets)} 条推文")

    elif args.mode == 'search':
        # 关键词搜索
        if not args.keywords:
            print("[ERROR] 请提供搜索关键词：--keywords GPT Claude LangChain")
            return

        tweets = monitor.search_by_keywords(args.keywords, args.max_results)
        print(f"\n[SUCCESS] 搜索完成，找到 {len(tweets)} 条推文")

    elif args.mode == 'stats':
        # 统计信息
        stats = monitor.get_stats()
        print(f"\n{'='*60}")
        print("统计信息")
        print(f"{'='*60}")
        print(f"总推文数：{stats['total_tweets']}")
        print(f"已处理：{stats['processed_tweets']}")
        print(f"未处理：{stats['unprocessed_tweets']}")
        print(f"\n按作者统计：")
        for author, count in stats['author_stats'].items():
            print(f"  {author}: {count} 条")

    # 清理旧推文
    if args.cleanup:
        monitor.cleanup_old_tweets()


if __name__ == '__main__':
    main()
