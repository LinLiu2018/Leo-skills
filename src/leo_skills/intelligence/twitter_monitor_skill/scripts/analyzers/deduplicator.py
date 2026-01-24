"""
推文去重器
使用三层去重策略：URL → 哈希 → 相似度
"""

import hashlib
import re
from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class Deduplicator:
    """推文去重器"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化去重器

        Args:
            config: 配置字典
        """
        dedup_config = config.get('deduplication', {})
        self.similarity_threshold = dedup_config.get('similarity_threshold', 0.85)
        self.enable_hash_dedup = dedup_config.get('enable_hash_dedup', True)
        self.enable_url_dedup = dedup_config.get('enable_url_dedup', True)
        self.enable_similarity_dedup = dedup_config.get('enable_similarity_dedup', True)

        # 已见过的哈希和 URL
        self.seen_hashes = set()
        self.seen_urls = set()

    def deduplicate(self, tweets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        对推文列表进行去重

        Args:
            tweets: 推文列表

        Returns:
            去重后的推文列表
        """
        if not tweets:
            return []

        print(f"开始去重，原始推文数：{len(tweets)}")

        # 第一阶段：URL 去重
        if self.enable_url_dedup:
            tweets = self._deduplicate_by_url(tweets)
            print(f"URL 去重后：{len(tweets)} 条")

        # 第二阶段：内容哈希去重
        if self.enable_hash_dedup:
            tweets = self._deduplicate_by_hash(tweets)
            print(f"哈希去重后：{len(tweets)} 条")

        # 第三阶段：相似度去重
        if self.enable_similarity_dedup and len(tweets) > 1:
            tweets = self._deduplicate_by_similarity(tweets)
            print(f"相似度去重后：{len(tweets)} 条")

        print(f"去重完成，最终推文数：{len(tweets)}")
        return tweets

    def _deduplicate_by_url(self, tweets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        基于 URL 去重

        Args:
            tweets: 推文列表

        Returns:
            去重后的推文列表
        """
        unique_tweets = []

        for tweet in tweets:
            url = tweet.get('url', '')
            normalized_url = self._normalize_url(url)

            if normalized_url not in self.seen_urls:
                self.seen_urls.add(normalized_url)
                unique_tweets.append(tweet)

        return unique_tweets

    def _deduplicate_by_hash(self, tweets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        基于内容哈希去重

        Args:
            tweets: 推文列表

        Returns:
            去重后的推文列表
        """
        unique_tweets = []

        for tweet in tweets:
            content = tweet.get('content', '')
            # 只使用前 500 字符计算哈希
            content_hash = hashlib.md5(content[:500].encode('utf-8')).hexdigest()

            if content_hash not in self.seen_hashes:
                self.seen_hashes.add(content_hash)
                unique_tweets.append(tweet)

        return unique_tweets

    def _deduplicate_by_similarity(self, tweets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        基于 TF-IDF 和余弦相似度去重

        Args:
            tweets: 推文列表

        Returns:
            去重后的推文列表
        """
        if len(tweets) < 2:
            return tweets

        try:
            # 提取文本
            texts = [tweet.get('content', '')[:500] for tweet in tweets]

            # 计算 TF-IDF 向量
            vectorizer = TfidfVectorizer(
                max_features=1000,
                ngram_range=(1, 2),
                stop_words=None  # 中文需要自定义停用词
            )
            tfidf_matrix = vectorizer.fit_transform(texts)

            # 计算余弦相似度矩阵
            similarity_matrix = cosine_similarity(tfidf_matrix)

            # 标记要移除的推文
            to_remove = set()
            for i in range(len(tweets)):
                if i in to_remove:
                    continue

                for j in range(i + 1, len(tweets)):
                    if j in to_remove:
                        continue

                    # 如果相似度超过阈值
                    if similarity_matrix[i][j] >= self.similarity_threshold:
                        # 保留优先级更高的（点赞数更多的）
                        if tweets[i].get('likes', 0) >= tweets[j].get('likes', 0):
                            to_remove.add(j)
                        else:
                            to_remove.add(i)
                            break

            # 返回未被标记的推文
            return [tweet for i, tweet in enumerate(tweets) if i not in to_remove]

        except Exception as e:
            print(f"相似度去重失败：{e}")
            return tweets

    def _normalize_url(self, url: str) -> str:
        """
        规范化 URL

        Args:
            url: 原始 URL

        Returns:
            规范化后的 URL
        """
        # 移除末尾斜杠
        url = url.rstrip('/')

        # 移除常见的跟踪参数
        url = re.sub(r'[?&](utm_|ref|share|fbclid|gclid).*$', '', url)

        # 转换为小写
        return url.lower()

    def reset(self):
        """重置去重器状态"""
        self.seen_hashes.clear()
        self.seen_urls.clear()
        print("去重器状态已重置")
