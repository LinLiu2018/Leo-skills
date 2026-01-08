# Deduplicator Module
# 去重模块

from typing import List, Dict, Any
import hashlib
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from utils.logger import get_logger

logger = get_logger(__name__)


class Deduplicator:
    """内容去重器"""

    def __init__(self, similarity_threshold: float = 0.85):
        """
        初始化去重器

        Args:
            similarity_threshold: 相似度阈值（0-1）
        """
        self.similarity_threshold = similarity_threshold
        self.seen_hashes = set()
        self.seen_urls = set()

    def deduplicate(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        去除重复和相似内容

        Args:
            items: 信息项列表

        Returns:
            去重后的信息项列表
        """
        logger.info(f"开始去重，原始数量: {len(items)}")

        # 第一阶段：URL 去重
        unique_items = self._deduplicate_by_url(items)

        # 第二阶段：内容哈希去重
        unique_items = self._deduplicate_by_hash(unique_items)

        # 第三阶段：相似内容去重
        unique_items = self._deduplicate_by_similarity(unique_items)

        logger.info(f"去重完成，剩余数量: {len(unique_items)}")

        return unique_items

    def _deduplicate_by_url(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """根据 URL 去重"""
        unique_items = []
        for item in items:
            url = item.get("url", "")
            # 规范化 URL（移除尾部斜杠、查询参数等）
            normalized_url = self._normalize_url(url)

            if normalized_url not in self.seen_urls:
                self.seen_urls.add(normalized_url)
                unique_items.append(item)

        return unique_items

    def _normalize_url(self, url: str) -> str:
        """规范化 URL"""
        if not url:
            return ""

        # 移除尾部斜杠
        url = url.rstrip("/")

        # 移除常见的跟踪参数
        import re
        url = re.sub(r'[?&](utm_|ref|share).*$', '', url)

        return url.lower()

    def _deduplicate_by_hash(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """根据内容哈希去重"""
        unique_items = []
        for item in items:
            # 使用标题和部分内容生成哈希
            title = item.get("title", "")
            content = item.get("content", "")[:500]  # 只使用前500字符
            combined = f"{title}{content}"

            content_hash = hashlib.md5(combined.encode('utf-8')).hexdigest()

            if content_hash not in self.seen_hashes:
                self.seen_hashes.add(content_hash)
                unique_items.append(item)

        return unique_items

    def _deduplicate_by_similarity(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """基于相似度去重"""
        if len(items) <= 1:
            return items

        # 提取文本
        texts = []
        for item in items:
            text = item.get("title", "") + " " + item.get("content", "")[:500]
            texts.append(text)

        # 计算TF-IDF和余弦相似度
        try:
            vectorizer = TfidfVectorizer(
                max_features=1000,
                ngram_range=(1, 2),
                stop_words=None  # 中文需要自定义停用词
            )
            tfidf_matrix = vectorizer.fit_transform(texts)
            similarity_matrix = cosine_similarity(tfidf_matrix)

            # 找出相似的文章并标记
            to_remove = set()
            for i in range(len(items)):
                if i in to_remove:
                    continue
                for j in range(i + 1, len(items)):
                    if j in to_remove:
                        continue
                    if similarity_matrix[i][j] >= self.similarity_threshold:
                        # 保留优先级更高的
                        if items[i].get("priority", 5) >= items[j].get("priority", 5):
                            to_remove.add(j)
                        else:
                            to_remove.add(i)
                            break

            unique_items = [item for i, item in enumerate(items) if i not in to_remove]
            return unique_items

        except Exception as e:
            logger.warning(f"相似度计算失败: {e}，跳过相似度去重")
            return items

    def reset(self):
        """重置去重器状态"""
        self.seen_hashes.clear()
        self.seen_urls.clear()
