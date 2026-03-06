# -*- coding: utf-8 -*-
"""
向量记忆检索系统 (Vector Memory)

基于 ChromaDB 的语义搜索，实现：
- 向量存储和检索
- 语义相似度匹配
- 混合搜索 (关键词 + 向量)
"""

import hashlib
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class VectorEntry:
    """向量记忆条目"""
    id: str
    content: str
    embedding: List[float]
    metadata: Dict[str, Any]
    similarity: float = 0.0


class SimpleEmbedding:
    """
    简单嵌入生成器 (基于词频的简化实现)

    实际生产环境应使用:
    - sentence-transformers
    - OpenAI Embeddings
    - 或其他预训练模型
    """

    def __init__(self, dim: int = 384):
        self.dim = dim
        # 常见中文词的简单哈希映射
        self.vocab = {}

    def _tokenize(self, text: str) -> List[str]:
        """简单分词 (按字符和常见词)"""
        # 简单实现：按字分词 + 2-gram
        chars = list(text.lower())
        bigrams = [chars[i] + chars[i+1] for i in range(len(chars)-1)]
        return chars + bigrams

    def encode(self, text: str) -> List[float]:
        """
        生成文本嵌入向量

        Args:
            text: 输入文本

        Returns:
            嵌入向量
        """
        tokens = self._tokenize(text)

        # 基于哈希的简单嵌入
        vector = np.zeros(self.dim)

        for token in tokens:
            # 使用哈希确定位置
            hash_val = int(hashlib.md5(token.encode()).hexdigest(), 16)
            idx = hash_val % self.dim

            # TF-IDF 风格的权重
            weight = 1.0 / len(tokens)
            vector[idx] += weight

        # L2 归一化
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm

        return vector.tolist()

    def similarity(self, emb1: List[float], emb2: List[float]) -> float:
        """计算余弦相似度"""
        v1 = np.array(emb1)
        v2 = np.array(emb2)

        dot = np.dot(v1, v2)
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return float(dot / (norm1 * norm2))


class VectorMemory:
    """
    向量记忆系统

    支持语义搜索的长期记忆存储。
    """

    def __init__(
        self,
        storage_dir: Optional[Path] = None,
        embedding_dim: int = 384
    ):
        """
        初始化向量记忆

        Args:
            storage_dir: 存储目录
            embedding_dim: 嵌入维度
        """
        if storage_dir is None:
            project_root = Path(__file__).parent.parent
            self.storage_dir = project_root / "data" / "vector_memory"
        else:
            self.storage_dir = Path(storage_dir)

        self.storage_dir.mkdir(parents=True, exist_ok=True)

        self.embedding = SimpleEmbedding(dim=embedding_dim)
        self.entries: Dict[str, VectorEntry] = {}

        # 加载已有数据
        self._load()

    def _get_data_file(self) -> Path:
        """获取数据文件路径"""
        return self.storage_dir / "vectors.json"

    def _load(self):
        """加载存储的数据"""
        data_file = self._get_data_file()

        if not data_file.exists():
            return

        try:
            with open(data_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            for item in data:
                entry = VectorEntry(
                    id=item["id"],
                    content=item["content"],
                    embedding=item["embedding"],
                    metadata=item.get("metadata", {}),
                    similarity=0.0
                )
                self.entries[entry.id] = entry

            logger.info(f"Loaded {len(self.entries)} vector entries")

        except Exception as e:
            logger.error(f"Failed to load vector memory: {e}")

    def _save(self):
        """保存数据到文件"""
        try:
            data = [
                {
                    "id": e.id,
                    "content": e.content,
                    "embedding": e.embedding,
                    "metadata": e.metadata
                }
                for e in self.entries.values()
            ]

            with open(self._get_data_file(), "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            logger.error(f"Failed to save vector memory: {e}")

    def remember(
        self,
        content: str,
        category: str = "general",
        importance: int = 3,
        **metadata
    ) -> str:
        """
        保存内容到向量记忆

        Args:
            content: 内容文本
            category: 分类
            importance: 重要性
            **metadata: 额外元数据

        Returns:
            条目ID
        """
        # 生成ID
        entry_id = hashlib.md5(
            f"{content}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]

        # 生成嵌入
        embedding = self.embedding.encode(content)

        # 构建元数据
        meta = {
            "category": category,
            "importance": importance,
            "created_at": datetime.now().isoformat(),
            "content_length": len(content),
            **metadata
        }

        # 保存条目
        entry = VectorEntry(
            id=entry_id,
            content=content,
            embedding=embedding,
            metadata=meta
        )

        self.entries[entry_id] = entry
        self._save()

        logger.info(f"Stored vector entry: {entry_id} ({category})")
        return entry_id

    def search(
        self,
        query: str,
        top_k: int = 5,
        min_similarity: float = 0.5,
        category: Optional[str] = None
    ) -> List[VectorEntry]:
        """
        语义搜索

        Args:
            query: 查询文本
            top_k: 返回数量
            min_similarity: 最小相似度
            category: 分类过滤

        Returns:
            匹配结果
        """
        if not self.entries:
            return []

        # 生成查询嵌入
        query_embedding = self.embedding.encode(query)

        # 计算相似度
        scored_entries = []

        for entry in self.entries.values():
            # 分类过滤
            if category and entry.metadata.get("category") != category:
                continue

            # 计算相似度
            sim = self.embedding.similarity(query_embedding, entry.embedding)

            if sim >= min_similarity:
                entry.similarity = sim
                scored_entries.append(entry)

        # 排序并返回
        scored_entries.sort(key=lambda x: x.similarity, reverse=True)
        return scored_entries[:top_k]

    def hybrid_search(
        self,
        query: str,
        top_k: int = 5,
        keyword_weight: float = 0.3,
        vector_weight: float = 0.7
    ) -> List[VectorEntry]:
        """
        混合搜索 (关键词 + 向量)

        Args:
            query: 查询文本
            top_k: 返回数量
            keyword_weight: 关键词权重
            vector_weight: 向量权重

        Returns:
            匹配结果
        """
        if not self.entries:
            return []

        query_lower = query.lower()
        query_embedding = self.embedding.encode(query)

        scored_entries = []

        for entry in self.entries.values():
            # 向量相似度
            vector_sim = self.embedding.similarity(query_embedding, entry.embedding)

            # 关键词匹配度
            content_lower = entry.content.lower()
            if query_lower in content_lower:
                keyword_sim = 1.0
            else:
                # 计算词重叠度
                query_words = set(query_lower.split())
                content_words = set(content_lower.split())
                overlap = len(query_words & content_words)
                keyword_sim = overlap / max(len(query_words), 1)

            # 混合分数
            combined_score = (
                vector_weight * vector_sim +
                keyword_weight * keyword_sim
            )

            entry.similarity = combined_score
            scored_entries.append(entry)

        # 排序
        scored_entries.sort(key=lambda x: x.similarity, reverse=True)
        return scored_entries[:top_k]

    def get_by_id(self, entry_id: str) -> Optional[VectorEntry]:
        """通过ID获取条目"""
        return self.entries.get(entry_id)

    def delete(self, entry_id: str) -> bool:
        """删除条目"""
        if entry_id in self.entries:
            del self.entries[entry_id]
            self._save()
            return True
        return False

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        categories = {}
        for entry in self.entries.values():
            cat = entry.metadata.get("category", "unknown")
            categories[cat] = categories.get(cat, 0) + 1

        return {
            "total_entries": len(self.entries),
            "categories": categories,
            "embedding_dim": self.embedding.dim,
            "storage_path": str(self.storage_dir)
        }

    def cleanup_old(self, days: int = 90) -> int:
        """
        清理过期条目

        Args:
            days: 保留天数

        Returns:
            清理数量
        """
        cutoff = datetime.now().timestamp() - days * 24 * 3600
        to_delete = []

        for entry_id, entry in self.entries.items():
            created = entry.metadata.get("created_at", "")
            try:
                created_ts = datetime.fromisoformat(created).timestamp()
                if created_ts < cutoff and entry.metadata.get("importance", 3) < 4:
                    to_delete.append(entry_id)
            except:
                pass

        for entry_id in to_delete:
            del self.entries[entry_id]

        if to_delete:
            self._save()

        logger.info(f"Cleaned up {len(to_delete)} old entries")
        return len(to_delete)


# 便捷函数
def get_vector_memory() -> VectorMemory:
    """获取全局向量记忆实例"""
    return VectorMemory()


if __name__ == "__main__":
    # 测试
    vm = VectorMemory()

    # 存储一些内容
    vm.remember("Python 是一种流行的编程语言", category="tech")
    vm.remember("JavaScript 用于网页开发", category="tech")
    vm.remember("房产价格受地段影响很大", category="realestate")
    vm.remember("贷款利率影响月供金额", category="loan")

    # 搜索
    results = vm.search("编程语言", top_k=3)
    print(f"\n搜索 '编程语言':")
    for r in results:
        print(f"  - {r.content[:30]}... (相似度: {r.similarity:.3f})")

    # 混合搜索
    results = vm.hybrid_search("网页开发")
    print(f"\n混合搜索 '网页开发':")
    for r in results:
        print(f"  - {r.content[:30]}... (相似度: {r.similarity:.3f})")
