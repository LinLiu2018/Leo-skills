# -*- coding: utf-8 -*-
"""
全自动共享记忆系统
==================
无需用户干预，自动记录、共享、检索记忆

功能：
1. 自动记录所有交互
2. 跨 Agent 实时共享
3. 主动回忆相关上下文
4. 自动记忆压缩和归档
5. 智能记忆关联
"""

import json
import hashlib
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from collections import deque
import logging

logger = logging.getLogger(__name__)


class AutoMemoryManager:
    """
    全自动记忆管理器

    自动捕获、存储、共享所有交互记忆
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True
        self.memory_dir = Path("leo_knowledge/memory/auto_storage")
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        # 内存缓存（最近100条）
        self.short_term_memory = deque(maxlen=100)

        # 长期记忆索引
        self.memory_index = self._load_index()

        # 当前会话上下文
        self.current_session = {
            "session_id": self._generate_session_id(),
            "start_time": datetime.now().isoformat(),
            "active_agents": set(),
            "context_chain": []
        }

        # 自动保存触发器
        self._setup_auto_save()

        logger.info(f"🧠 全自动记忆系统已启动 | 会话: {self.current_session['session_id'][:8]}")

    def _generate_session_id(self) -> str:
        """生成会话ID"""
        return hashlib.md5(
            datetime.now().isoformat().encode()
        ).hexdigest()[:16]

    def _load_index(self) -> Dict:
        """加载记忆索引"""
        index_file = self.memory_dir / "memory_index.json"
        if index_file.exists():
            with open(index_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"entries": [], "agent_usage": {}, "topic_clusters": {}}

    def _save_index(self):
        """保存记忆索引"""
        index_file = self.memory_dir / "memory_index.json"
        with open(index_file, "w", encoding="utf-8") as f:
            json.dump(self.memory_index, f, ensure_ascii=False, indent=2)

    def _setup_auto_save(self):
        """设置自动保存机制"""
        # 每10条记忆自动保存
        self.auto_save_threshold = 10
        self._memory_counter = 0

    def auto_record(
        self,
        event_type: str,
        content: Any,
        agent: str = "system",
        importance: int = 3,
        tags: Optional[List[str]] = None,
        context: Optional[Dict] = None
    ) -> str:
        """
        自动记录事件到记忆

        无需用户调用，系统自动捕获
        """
        memory_entry = {
            "id": hashlib.md5(
                f"{datetime.now().isoformat()}{content}".encode()
            ).hexdigest()[:12],
            "timestamp": datetime.now().isoformat(),
            "session_id": self.current_session["session_id"],
            "event_type": event_type,  # user_input, agent_response, tool_call, error, correction
            "agent": agent,
            "content": self._serialize_content(content),
            "importance": importance,  # 1-5
            "tags": tags or [],
            "context": context or {},
            "related_memories": self._find_related(content, top_k=3)
        }

        # 添加到短期记忆
        self.short_term_memory.append(memory_entry)

        # 更新索引
        self._update_index(memory_entry)

        # 自动保存检查
        self._memory_counter += 1
        if self._memory_counter >= self.auto_save_threshold:
            self._persist_memory()
            self._memory_counter = 0

        # 记录活跃Agent
        if agent != "system":
            self.current_session["active_agents"].add(agent)

        return memory_entry["id"]

    def _serialize_content(self, content: Any) -> str:
        """序列化内容"""
        if isinstance(content, str):
            return content
        try:
            return json.dumps(content, ensure_ascii=False)
        except:
            return str(content)

    def _find_related(self, content: Any, top_k: int = 3) -> List[str]:
        """查找相关记忆ID"""
        content_str = self._serialize_content(content).lower()
        keywords = set(content_str.split())

        scores = []
        for mem in self.short_term_memory:
            mem_content = mem.get("content", "").lower()
            mem_keywords = set(mem_content.split())

            # 计算关键词重叠
            overlap = len(keywords & mem_keywords)
            if overlap > 0:
                scores.append((mem["id"], overlap))

        # 按相关度排序
        scores.sort(key=lambda x: x[1], reverse=True)
        return [mid for mid, _ in scores[:top_k]]

    def _update_index(self, entry: Dict):
        """更新记忆索引"""
        # 添加到条目列表
        self.memory_index["entries"].append({
            "id": entry["id"],
            "timestamp": entry["timestamp"],
            "event_type": entry["event_type"],
            "agent": entry["agent"],
            "tags": entry["tags"]
        })

        # 更新Agent使用统计
        agent = entry["agent"]
        if agent not in self.memory_index["agent_usage"]:
            self.memory_index["agent_usage"][agent] = {"count": 0, "last_used": ""}
        self.memory_index["agent_usage"][agent]["count"] += 1
        self.memory_index["agent_usage"][agent]["last_used"] = entry["timestamp"]

        # 更新话题聚类
        for tag in entry["tags"]:
            if tag not in self.memory_index["topic_clusters"]:
                self.memory_index["topic_clusters"][tag] = []
            self.memory_index["topic_clusters"][tag].append(entry["id"])

    def _persist_memory(self):
        """持久化记忆到文件"""
        session_file = self.memory_dir / f"session_{self.current_session['session_id']}.json"

        # 转换 set 为 list 以便 JSON 序列化
        session_info = dict(self.current_session)
        session_info["active_agents"] = list(session_info["active_agents"])

        memory_data = {
            "session_info": session_info,
            "memories": list(self.short_term_memory)
        }

        with open(session_file, "w", encoding="utf-8") as f:
            json.dump(memory_data, f, ensure_ascii=False, indent=2)

        self._save_index()
        logger.debug(f"💾 已自动保存 {len(self.short_term_memory)} 条记忆")

    def recall(
        self,
        query: Optional[str] = None,
        agent: Optional[str] = None,
        event_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        time_range: Optional[int] = None,  # 小时
        top_k: int = 5
    ) -> List[Dict]:
        """
        主动回忆相关记忆

        系统自动调用，为Agent提供上下文
        """
        results = []

        # 从短期记忆搜索
        for mem in reversed(self.short_term_memory):
            score = self._calculate_relevance(mem, query, agent, event_type, tags, time_range)
            if score > 0:
                results.append((mem, score))

        # 按相关度排序
        results.sort(key=lambda x: x[1], reverse=True)

        return [mem for mem, _ in results[:top_k]]

    def _calculate_relevance(
        self,
        mem: Dict,
        query: Optional[str],
        agent: Optional[str],
        event_type: Optional[str],
        tags: Optional[List[str]],
        time_range: Optional[int]
    ) -> float:
        """计算记忆相关性得分"""
        score = 0.0

        # Agent匹配
        if agent and mem.get("agent") == agent:
            score += 2.0

        # 事件类型匹配
        if event_type and mem.get("event_type") == event_type:
            score += 1.5

        # 标签匹配
        if tags:
            mem_tags = set(mem.get("tags", []))
            overlap = len(mem_tags & set(tags))
            score += overlap * 1.0

        # 查询文本匹配
        if query:
            query_lower = query.lower()
            content = mem.get("content", "").lower()
            if query_lower in content:
                score += 3.0
            # 关键词重叠
            query_words = set(query_lower.split())
            content_words = set(content.split())
            overlap = len(query_words & content_words)
            score += overlap * 0.5

        # 时间衰减（越新的记忆权重越高）
        if time_range:
            mem_time = datetime.fromisoformat(mem.get("timestamp", "2020-01-01"))
            hours_ago = (datetime.now() - mem_time).total_seconds() / 3600
            if hours_ago <= time_range:
                score *= (1 + (time_range - hours_ago) / time_range)
            else:
                score *= 0.5

        # 重要性加权
        importance = mem.get("importance", 3)
        score *= (importance / 3.0)

        return score

    def get_context_for_agent(self, agent_name: str, current_task: str) -> Dict[str, Any]:
        """
        为Agent获取相关上下文

        自动调用，无需Agent主动请求
        """
        # 召回相关记忆
        relevant_memories = self.recall(
            query=current_task,
            agent=agent_name,
            top_k=10
        )

        # 获取当前会话链
        context_chain = self.current_session.get("context_chain", [])[-5:]

        # 获取用户偏好
        user_prefs = self._get_user_preferences()

        return {
            "relevant_memories": relevant_memories,
            "session_context": context_chain,
            "user_preferences": user_prefs,
            "active_agents": list(self.current_session["active_agents"]),
            "suggested_actions": self._suggest_actions(agent_name, current_task)
        }

    def _get_user_preferences(self) -> Dict:
        """获取用户偏好"""
        prefs_file = Path("leo_knowledge/context/user_profile.json")
        if prefs_file.exists():
            try:
                with open(prefs_file, "r", encoding="utf-8") as f:
                    profile = json.load(f)
                    return {
                        "content_style": profile.get("content_preferences", {}),
                        "learned_patterns": profile.get("learning_system", {}).get("learned_patterns", {}),
                        "preferred_agents": profile.get("interaction_history", {}).get("frequently_used_agents", [])
                    }
            except:
                pass
        return {}

    def _suggest_actions(self, agent_name: str, task: str) -> List[str]:
        """基于记忆建议下一步行动"""
        suggestions = []

        # 查找类似任务的历史
        similar = self.recall(query=task, event_type="agent_response", top_k=3)

        if similar:
            suggestions.append(f"参考之前{len(similar)}次类似任务的处理方式")

        # 检查是否有未完成的上下文
        if len(self.current_session["context_chain"]) > 0:
            last_context = self.current_session["context_chain"][-1]
            if last_context.get("status") == "pending":
                suggestions.append(f"继续之前的任务: {last_context.get('task', '')}")

        return suggestions

    def update_context_chain(self, task: str, status: str = "active", result: Any = None):
        """更新上下文链"""
        self.current_session["context_chain"].append({
            "timestamp": datetime.now().isoformat(),
            "task": task,
            "status": status,
            "result": result is not None
        })

        # 保持链长度
        if len(self.current_session["context_chain"]) > 20:
            self.current_session["context_chain"] = self.current_session["context_chain"][-20:]

    def get_session_summary(self) -> Dict:
        """获取当前会话摘要"""
        return {
            "session_id": self.current_session["session_id"],
            "duration_minutes": self._calculate_session_duration(),
            "memory_count": len(self.short_term_memory),
            "active_agents": list(self.current_session["active_agents"]),
            "context_depth": len(self.current_session["context_chain"]),
            "topics": self._extract_session_topics()
        }

    def _calculate_session_duration(self) -> int:
        """计算会话持续时间"""
        start = datetime.fromisoformat(self.current_session["start_time"])
        return int((datetime.now() - start).total_seconds() / 60)

    def _extract_session_topics(self) -> List[str]:
        """提取会话主题"""
        topics = set()
        for mem in self.short_term_memory:
            topics.update(mem.get("tags", []))
        return list(topics)[:10]

    def compress_old_memories(self, days: int = 7):
        """压缩旧记忆"""
        cutoff = datetime.now() - timedelta(days=days)

        # 找到需要压缩的记忆
        to_compress = []
        for mem in list(self.short_term_memory):
            mem_time = datetime.fromisoformat(mem.get("timestamp", "2020-01-01"))
            if mem_time < cutoff:
                to_compress.append(mem)

        if to_compress:
            # 生成摘要
            summary = self._generate_summary(to_compress)

            # 保存到归档
            archive_file = self.memory_dir / f"archive_{datetime.now().strftime('%Y%m')}.json"
            with open(archive_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(summary, ensure_ascii=False) + "\n")

            logger.info(f"📦 已压缩 {len(to_compress)} 条旧记忆")

    def _generate_summary(self, memories: List[Dict]) -> Dict:
        """生成记忆摘要"""
        agents_used = set()
        topics = set()

        for mem in memories:
            agents_used.add(mem.get("agent", "unknown"))
            topics.update(mem.get("tags", []))

        return {
            "period": f"{memories[0]['timestamp']} to {memories[-1]['timestamp']}",
            "memory_count": len(memories),
            "agents_involved": list(agents_used),
            "topics_covered": list(topics),
            "summary": f"期间涉及{len(agents_used)}个Agent，处理{len(topics)}个主题"
        }


# 全局实例
_auto_memory: Optional[AutoMemoryManager] = None


def get_auto_memory() -> AutoMemoryManager:
    """获取全自动记忆管理器"""
    global _auto_memory
    if _auto_memory is None:
        _auto_memory = AutoMemoryManager()
    return _auto_memory


# 便捷函数
def auto_record(*args, **kwargs) -> str:
    """自动记录（无需显式调用）"""
    return get_auto_memory().auto_record(*args, **kwargs)


def auto_recall(*args, **kwargs) -> List[Dict]:
    """自动回忆"""
    return get_auto_memory().recall(*args, **kwargs)


def get_context(*args, **kwargs) -> Dict:
    """获取上下文"""
    return get_auto_memory().get_context_for_agent(*args, **kwargs)


__all__ = [
    "AutoMemoryManager",
    "get_auto_memory",
    "auto_record",
    "auto_recall",
    "get_context"
]
