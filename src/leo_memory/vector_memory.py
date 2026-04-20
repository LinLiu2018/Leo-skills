# -*- coding: utf-8 -*-
"""
向量记忆检索系统 (Vector Memory) - 增强版

支持多种嵌入方式:
- SimpleEmbedding: 基于词频的简化实现（默认）
- SentenceTransformerEmbedding: sentence-transformers 模型
- OpenAIEmbedding: OpenAI Embeddings API

功能:
- 向量存储和检索
- 语义相似度匹配
- 混合搜索 (关键词 + 向量)
- ChromaDB 持久化（可选）
"""

import hashlib
import json
import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

import numpy as np

logger = logging.getLogger(__name__)


class EmbeddingType(Enum):
    """嵌入类型枚举"""
    SIMPLE = "simple"
    SENTENCE_TRANSFORMERS = "sentence_transformers"
    OPENAI = "openai"


@dataclass
class VectorEntry:
    """向量记忆条目"""
    id: str
    content: str
    embedding: List[float]
    metadata: Dict[str, Any]
    similarity: float = 0.0


class BaseEmbedding(ABC):
    """嵌入基类"""

    @abstractmethod
    def encode(self, text: str) -> List[float]:
        """生成文本嵌入向量"""
        pass

    @abstractmethod
    def similarity(self, emb1: List[float], emb2: List[float]) -> float:
        """计算余弦相似度"""
        pass


class SimpleEmbedding(BaseEmbedding):
    """
    简单嵌入生成器 (基于词频的简化实现)

    适用于：快速原型、无需外部依赖的场景
    """

    def __init__(self, dim: int = 384):
        self.dim = dim

    def _tokenize(self, text: str) -> List[str]:
        """简单分词 (按字符和常见词)"""
        chars = list(text.lower())
        bigrams = [chars[i] + chars[i+1] for i in range(len(chars)-1)]
        return chars + bigrams

    def encode(self, text: str) -> List[float]:
        """生成文本嵌入向量"""
        tokens = self._tokenize(text)
        vector = np.zeros(self.dim)

        for token in tokens:
            hash_val = int(hashlib.md5(token.encode()).hexdigest(), 16)
            idx = hash_val % self.dim
            weight = 1.0 / max(len(tokens), 1)
            vector[idx] += weight

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


class SentenceTransformerEmbedding(BaseEmbedding):
    """
    Sentence-Transformers 嵌入

    适用于：需要高质量语义理解的场景
    需要安装: pip install sentence-transformers
    """

    def __init__(
        self,
        model_name: str = "paraphrase-multilingual-MiniLM-L12-v2",
        device: str = "cpu"
    ):
        self.model_name = model_name
        self.device = device
        self.model = None
        self._load_model()

    def _load_model(self):
        """加载模型"""
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name, device=self.device)
            logger.info(f"Loaded sentence-transformers model: {self.model_name}")
        except ImportError:
            logger.warning(
                "sentence-transformers not installed. "
                "Falling back to SimpleEmbedding. "
                "Install with: pip install sentence-transformers"
            )
            self.model = None

    def encode(self, text: str) -> List[float]:
        """生成文本嵌入向量"""
        if self.model is None:
            # 回退到简单嵌入
            fallback = SimpleEmbedding()
            return fallback.encode(text)

        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

    def encode_batch(self, texts: List[str]) -> List[List[float]]:
        """批量编码"""
        if self.model is None:
            fallback = SimpleEmbedding()
            return [fallback.encode(t) for t in texts]

        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return [e.tolist() for e in embeddings]

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


class OpenAIEmbedding(BaseEmbedding):
    """
    OpenAI Embeddings 嵌入

    适用于：生产环境，需要 OpenAI API
    需要设置环境变量: OPENAI_API_KEY
    """

    def __init__(
        self,
        model: str = "text-embedding-3-small",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        self.model = model
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url or os.getenv("OPENAI_EMBEDDING_BASE_URL")
        self.client = None
        self._init_client()

    def _init_client(self):
        """初始化 OpenAI 客户端"""
        if not self.api_key:
            logger.warning(
                "OpenAI API key not set. "
                "Falling back to SimpleEmbedding. "
                "Set OPENAI_API_KEY environment variable."
            )
            return

        try:
            from openai import OpenAI
            kwargs = {"api_key": self.api_key}
            if self.base_url:
                kwargs["base_url"] = self.base_url
            self.client = OpenAI(**kwargs)
            logger.info(f"Initialized OpenAI embedding client: {self.model}")
        except Exception as e:
            logger.warning(f"Failed to initialize OpenAI client: {e}")
            self.client = None

    def encode(self, text: str) -> List[float]:
        """生成文本嵌入向量"""
        if self.client is None:
            fallback = SimpleEmbedding()
            return fallback.encode(text)

        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"OpenAI embedding error: {e}")
            fallback = SimpleEmbedding()
            return fallback.encode(text)

    def encode_batch(self, texts: List[str]) -> List[List[float]]:
        """批量编码"""
        if self.client is None:
            fallback = SimpleEmbedding()
            return [fallback.encode(t) for t in texts]

        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=texts
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            logger.error(f"OpenAI batch embedding error: {e}")
            fallback = SimpleEmbedding()
            return [fallback.encode(t) for t in texts]

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


def create_embedding(
    embedding_type: str = "simple",
    **kwargs
) -> BaseEmbedding:
    """
    工厂函数：创建嵌入实例

    Args:
        embedding_type: 嵌入类型 ("simple", "sentence_transformers", "openai")
        **kwargs: 传递给嵌入类的参数

    Returns:
        嵌入实例

    Examples:
        >>> embedding = create_embedding("simple", dim=384)
        >>> embedding = create_embedding("sentence_transformers", model_name="paraphrase-multilingual-MiniLM-L12-v2")
        >>> embedding = create_embedding("openai", model="text-embedding-3-small")
    """
    embedding_type = embedding_type.lower()

    if embedding_type == EmbeddingType.SIMPLE.value:
        return SimpleEmbedding(**kwargs)
    elif embedding_type == EmbeddingType.SENTENCE_TRANSFORMERS.value:
        return SentenceTransformerEmbedding(**kwargs)
    elif embedding_type == EmbeddingType.OPENAI.value:
        return OpenAIEmbedding(**kwargs)
    else:
        logger.warning(f"Unknown embedding type: {embedding_type}, using SimpleEmbedding")
        return SimpleEmbedding(**kwargs)


class VectorMemory:
    """
    向量记忆系统 - 增强版

    支持多种嵌入方式和持久化选项。
    """

    def __init__(
        self,
        storage_dir: Optional[Path] = None,
        embedding_type: str = "simple",
        embedding_dim: int = 384,
        use_chromadb: bool = False,
        **embedding_kwargs
    ):
        """
        初始化向量记忆

        Args:
            storage_dir: 存储目录
            embedding_type: 嵌入类型 ("simple", "sentence_transformers", "openai")
            embedding_dim: 嵌入维度
            use_chromadb: 是否使用 ChromaDB（可选）
            **embedding_kwargs: 传递给嵌入类的参数
        """
        if storage_dir is None:
            project_root = Path(__file__).parent.parent
            self.storage_dir = project_root / "data" / "vector_memory"
        else:
            self.storage_dir = Path(storage_dir)

        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # 创建嵌入实例
        self.embedding = create_embedding(
            embedding_type,
            dim=embedding_dim,
            **embedding_kwargs
        )
        self.embedding_type = embedding_type
        self.embedding_dim = embedding_dim

        # ChromaDB 支持
        self.use_chromadb = use_chromadb
        self.chromadb_client = None
        if use_chromadb:
            self._init_chromadb()

        self.entries: Dict[str, VectorEntry] = {}

        # 加载已有数据
        self._load()

    def _init_chromadb(self):
        """初始化 ChromaDB"""
        try:
            import chromadb
            self.chromadb_client = chromadb.PersistentClient(
                path=str(self.storage_dir / "chromadb")
            )
            self.chromadb_collection = self.chromadb_client.get_or_create_collection(
                "leo_memory"
            )
            logger.info("Initialized ChromaDB client")
        except ImportError:
            logger.warning(
                "chromadb not installed. "
                "Falling back to JSON storage. "
                "Install with: pip install chromadb"
            )
            self.use_chromadb = False
        except Exception as e:
            logger.warning(f"Failed to initialize ChromaDB: {e}")
            self.use_chromadb = False

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
            importance: 重要性 (1-5)
            **metadata: 额外元数据

        Returns:
            条目ID
        """
        entry_id = hashlib.md5(
            f"{content}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]

        embedding = self.embedding.encode(content)

        meta = {
            "category": category,
            "importance": importance,
            "created_at": datetime.now().isoformat(),
            "content_length": len(content),
            "embedding_type": self.embedding_type,
            **metadata
        }

        entry = VectorEntry(
            id=entry_id,
            content=content,
            embedding=embedding,
            metadata=meta
        )

        self.entries[entry_id] = entry

        # ChromaDB 同步
        if self.use_chromadb and self.chromadb_collection is not None:
            try:
                self.chromadb_collection.upsert(
                    ids=[entry_id],
                    documents=[content],
                    metadatas=[meta]
                )
            except Exception as e:
                logger.error(f"ChromaDB upsert error: {e}")

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

        query_embedding = self.embedding.encode(query)

        scored_entries = []

        for entry in self.entries.values():
            if category and entry.metadata.get("category") != category:
                continue

            sim = self.embedding.similarity(query_embedding, entry.embedding)

            if sim >= min_similarity:
                entry.similarity = sim
                scored_entries.append(entry)

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
        """
        if not self.entries:
            return []

        query_lower = query.lower()
        query_embedding = self.embedding.encode(query)

        scored_entries = []

        for entry in self.entries.values():
            vector_sim = self.embedding.similarity(query_embedding, entry.embedding)

            content_lower = entry.content.lower()
            if query_lower in content_lower:
                keyword_sim = 1.0
            else:
                query_words = set(query_lower.split())
                content_words = set(content_lower.split())
                overlap = len(query_words & content_words)
                keyword_sim = overlap / max(len(query_words), 1)

            combined_score = (
                vector_weight * vector_sim +
                keyword_weight * keyword_sim
            )

            entry.similarity = combined_score
            scored_entries.append(entry)

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
            "embedding_type": self.embedding_type,
            "embedding_dim": self.embedding_dim,
            "use_chromadb": self.use_chromadb,
            "storage_path": str(self.storage_dir)
        }

    def cleanup_old(self, days: int = 90) -> int:
        """清理过期条目"""
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
def get_vector_memory(
    embedding_type: str = "simple",
    **kwargs
) -> VectorMemory:
    """
    获取全局向量记忆实例

    Args:
        embedding_type: 嵌入类型
        **kwargs: 其他参数

    Returns:
        VectorMemory 实例
    """
    return VectorMemory(embedding_type=embedding_type, **kwargs)


if __name__ == "__main__":
    # 测试不同嵌入类型
    print("=" * 50)
    print("测试 SimpleEmbedding")
    print("=" * 50)

    vm_simple = VectorMemory(embedding_type="simple")
    vm_simple.remember("Python 是一种流行的编程语言", category="tech")
    vm_simple.remember("JavaScript 用于网页开发", category="tech")

    results = vm_simple.search("编程语言", top_k=3)
    for r in results:
        print(f"  - {r.content[:30]}... (相似度: {r.similarity:.3f})")

    print(f"\n统计: {vm_simple.get_stats()}")

    print("\n" + "=" * 50)
    print("配置说明")
    print("=" * 50)
    print("""
使用不同的嵌入类型:

1. SimpleEmbedding (默认):
   vm = VectorMemory(embedding_type="simple")

2. Sentence-Transformers:
   vm = VectorMemory(
       embedding_type="sentence_transformers",
       model_name="paraphrase-multilingual-MiniLM-L12-v2"
   )
   # 需要: pip install sentence-transformers

3. OpenAI Embeddings:
   vm = VectorMemory(embedding_type="openai")
   # 需要: 设置 OPENAI_API_KEY 环境变量
   """)
