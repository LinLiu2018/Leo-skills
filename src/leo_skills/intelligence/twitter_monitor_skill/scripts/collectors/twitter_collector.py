"""
Twitter 推文采集器
使用 tweepy 库采集 Twitter 推文
"""

import tweepy
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import time
import random


class TwitterCollector:
    """Twitter 推文采集器"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化 Twitter 采集器

        Args:
            config: 配置字典，包含 Twitter API 凭证
        """
        self.config = config

        # 初始化 Twitter API 客户端
        twitter_config = config.get('twitter', {})
        self.client = tweepy.Client(
            bearer_token=twitter_config.get('bearer_token'),
            consumer_key=twitter_config.get('api_key'),
            consumer_secret=twitter_config.get('api_secret'),
            access_token=twitter_config.get('access_token'),
            access_token_secret=twitter_config.get('access_token_secret'),
            wait_on_rate_limit=True  # 自动处理速率限制
        )

        # 速率限制配置
        rate_config = config.get('rate_limiting', {})
        self.request_interval = rate_config.get('request_interval', 2)
        self.random_delay = rate_config.get('random_delay', 0.5)

        # 监控配置
        monitor_config = config.get('monitoring', {})
        self.max_tweets_per_user = monitor_config.get('max_tweets_per_user', 100)
        self.lookback_days = monitor_config.get('lookback_days', 7)
        self.include_retweets = monitor_config.get('include_retweets', False)
        self.include_replies = monitor_config.get('include_replies', False)

        # 质量过滤
        filters = monitor_config.get('filters', {})
        self.min_likes = filters.get('min_likes', 5)
        self.min_retweets = filters.get('min_retweets', 2)
        self.min_length = filters.get('min_length', 50)

        # 最后请求时间
        self.last_request_time = 0

    def _rate_limit(self):
        """实施速率限制"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time

        if time_since_last_request < self.request_interval:
            sleep_time = self.request_interval - time_since_last_request
            # 添加随机延迟以避免检测
            sleep_time += random.uniform(0, self.random_delay)
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def collect_user_tweets(
        self,
        username: str,
        max_results: int = None,
        start_time: datetime = None
    ) -> List[Dict[str, Any]]:
        """
        采集指定用户的推文

        Args:
            username: Twitter 用户名
            max_results: 最大结果数（默认使用配置值）
            start_time: 开始时间（默认为 lookback_days 天前）

        Returns:
            推文列表
        """
        if max_results is None:
            max_results = self.max_tweets_per_user

        if start_time is None:
            start_time = datetime.now() - timedelta(days=self.lookback_days)

        # 速率限制
        self._rate_limit()

        try:
            # 获取用户信息
            user = self.client.get_user(username=username)
            if not user.data:
                print(f"用户不存在：{username}")
                return []

            user_id = user.data.id

            # 构建查询参数
            tweet_fields = [
                'created_at', 'public_metrics', 'lang',
                'referenced_tweets', 'author_id'
            ]

            # 获取推文
            tweets = self.client.get_users_tweets(
                id=user_id,
                max_results=min(max_results, 100),  # API 限制最多 100
                tweet_fields=tweet_fields,
                start_time=start_time,
                exclude=['retweets'] if not self.include_retweets else None
            )

            if not tweets.data:
                print(f"未找到推文：{username}")
                return []

            # 处理推文数据
            processed_tweets = []
            for tweet in tweets.data:
                processed_tweet = self._process_tweet(tweet, username)

                # 质量过滤
                if not self._passes_quality_filter(processed_tweet):
                    continue

                processed_tweets.append(processed_tweet)

            print(f"采集到 {len(processed_tweets)} 条推文：{username}")
            return processed_tweets

        except tweepy.TweepyException as e:
            print(f"采集推文失败 ({username})：{e}")
            return []

    def search_tweets(
        self,
        query: str,
        max_results: int = 100,
        start_time: datetime = None
    ) -> List[Dict[str, Any]]:
        """
        按关键词搜索推文

        Args:
            query: 搜索查询
            max_results: 最大结果数
            start_time: 开始时间

        Returns:
            推文列表
        """
        if start_time is None:
            start_time = datetime.now() - timedelta(days=self.lookback_days)

        # 速率限制
        self._rate_limit()

        try:
            # 构建查询
            if not self.include_retweets:
                query += " -is:retweet"

            if not self.include_replies:
                query += " -is:reply"

            # 搜索推文
            tweets = self.client.search_recent_tweets(
                query=query,
                max_results=min(max_results, 100),
                tweet_fields=['created_at', 'public_metrics', 'lang', 'author_id'],
                expansions=['author_id'],
                start_time=start_time
            )

            if not tweets.data:
                print(f"未找到推文：{query}")
                return []

            # 处理推文数据
            processed_tweets = []
            users = {user.id: user.username for user in tweets.includes.get('users', [])}

            for tweet in tweets.data:
                username = users.get(tweet.author_id, 'unknown')
                processed_tweet = self._process_tweet(tweet, username)

                # 质量过滤
                if not self._passes_quality_filter(processed_tweet):
                    continue

                processed_tweets.append(processed_tweet)

            print(f"搜索到 {len(processed_tweets)} 条推文：{query}")
            return processed_tweets

        except tweepy.TweepyException as e:
            print(f"搜索推文失败 ({query})：{e}")
            return []

    def _process_tweet(self, tweet, username: str) -> Dict[str, Any]:
        """
        处理推文数据

        Args:
            tweet: tweepy Tweet 对象
            username: 用户名

        Returns:
            处理后的推文字典
        """
        # 获取互动数据
        metrics = tweet.public_metrics if hasattr(tweet, 'public_metrics') else {}

        # 检查是否为转发或回复
        is_retweet = False
        is_reply = False
        if hasattr(tweet, 'referenced_tweets') and tweet.referenced_tweets:
            for ref in tweet.referenced_tweets:
                if ref.type == 'retweeted':
                    is_retweet = True
                elif ref.type == 'replied_to':
                    is_reply = True

        return {
            'tweet_id': str(tweet.id),
            'author_username': username,
            'author_id': str(tweet.author_id) if hasattr(tweet, 'author_id') else None,
            'content': tweet.text,
            'created_at': tweet.created_at if hasattr(tweet, 'created_at') else datetime.now(),
            'url': f"https://twitter.com/{username}/status/{tweet.id}",
            'likes': metrics.get('like_count', 0),
            'retweets': metrics.get('retweet_count', 0),
            'replies': metrics.get('reply_count', 0),
            'quotes': metrics.get('quote_count', 0),
            'language': tweet.lang if hasattr(tweet, 'lang') else None,
            'is_retweet': is_retweet,
            'is_reply': is_reply,
            'metadata': {
                'raw_metrics': metrics
            }
        }

    def _passes_quality_filter(self, tweet: Dict[str, Any]) -> bool:
        """
        检查推文是否通过质量过滤

        Args:
            tweet: 推文字典

        Returns:
            是否通过过滤
        """
        # 检查点赞数
        if tweet['likes'] < self.min_likes:
            return False

        # 检查转发数
        if tweet['retweets'] < self.min_retweets:
            return False

        # 检查内容长度
        if len(tweet['content']) < self.min_length:
            return False

        return True

    def get_user_info(self, username: str) -> Optional[Dict[str, Any]]:
        """
        获取用户信息

        Args:
            username: 用户名

        Returns:
            用户信息字典或 None
        """
        self._rate_limit()

        try:
            user = self.client.get_user(
                username=username,
                user_fields=['description', 'public_metrics', 'created_at']
            )

            if not user.data:
                return None

            return {
                'id': str(user.data.id),
                'username': user.data.username,
                'name': user.data.name,
                'description': user.data.description if hasattr(user.data, 'description') else None,
                'followers': user.data.public_metrics.get('followers_count', 0) if hasattr(user.data, 'public_metrics') else 0,
                'following': user.data.public_metrics.get('following_count', 0) if hasattr(user.data, 'public_metrics') else 0,
                'tweet_count': user.data.public_metrics.get('tweet_count', 0) if hasattr(user.data, 'public_metrics') else 0,
                'created_at': user.data.created_at if hasattr(user.data, 'created_at') else None
            }

        except tweepy.TweepyException as e:
            print(f"获取用户信息失败 ({username})：{e}")
            return None
