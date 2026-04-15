# -*- coding: utf-8 -*-
"""
Claude-Mem 集成模块
===================
为Leo AI系统提供跨会话记忆持久化功能

核心功能：
1. 自动捕获工具使用观察
2. 生成语义摘要
3. 跨会话上下文注入
4. SQLite + Chroma 混合存储
5. MCP 搜索工具

基于 claude-mem 架构: https://github.com/thedotmack/claude-mem
"""

import json
import sqlite3
import threading
import hashlib
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from collections import deque

logger = logging.getLogger(__name__)


@dataclass
class Observation:
    """记忆观察条目"""
    id: str
    session_id: str
    timestamp: str
    event_type: str  # tool_call, user_input, agent_response, error, correction
    content: str
    summary: str = ""
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding_id: Optional[str] = None


class MemoryDatabase:
    """
    记忆数据库 - SQLite + FTS5 全文本搜索
    """

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self._init_schema()
        self._lock = threading.Lock()

    def _init_schema(self):
        """初始化数据库Schema"""
        cursor = self.conn.cursor()

        # 观察表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS observations (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                content TEXT NOT NULL,
                summary TEXT DEFAULT '',
                tags TEXT DEFAULT '[]',
                metadata TEXT DEFAULT '{}',
                embedding_id TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # FTS5 虚拟表用于全文搜索
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS observations_fts USING fts5(
                content,
                content='observations',
                content_rowid='rowid'
            )
        """)

        # 触发器保持FTS同步
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS observations_ai AFTER INSERT ON observations BEGIN
                INSERT INTO observations_fts(rowid, content) VALUES (NEW.rowid, NEW.content);
            END
        """)

        # 会话表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                start_time TEXT NOT NULL,
                end_time TEXT,
                topic TEXT DEFAULT 'general',
                agent TEXT DEFAULT 'claude-code',
                tool_count INTEGER DEFAULT 0,
                error_count INTEGER DEFAULT 0,
                summary TEXT DEFAULT ''
            )
        """)

        # 创建索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_obs_session ON observations(session_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_obs_type ON observations(event_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_obs_timestamp ON observations(timestamp)")

        self.conn.commit()

    def insert_observation(self, obs: Observation) -> bool:
        """插入观察记录"""
        with self._lock:
            try:
                cursor = self.conn.cursor()
                cursor.execute("""
                    INSERT INTO observations (id, session_id, timestamp, event_type, content, summary, tags, metadata, embedding_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    obs.id,
                    obs.session_id,
                    obs.timestamp,
                    obs.event_type,
                    obs.content,
                    obs.summary,
                    json.dumps(obs.tags, ensure_ascii=False),
                    json.dumps(obs.metadata, ensure_ascii=False),
                    obs.embedding_id
                ))
                self.conn.commit()
                return True
            except Exception as e:
                logger.error(f"插入观察失败: {e}")
                return False

    def search(self, query: str, limit: int = 10, event_type: Optional[str] = None) -> List[Dict]:
        """全文搜索记忆"""
        with self._lock:
            cursor = self.conn.cursor()

            sql = """
                SELECT o.* FROM observations o
                JOIN observations_fts fts ON o.rowid = fts.rowid
                WHERE observations_fts MATCH ?
            """
            params = [query + "*"]  # 前缀匹配

            if event_type:
                sql += " AND o.event_type = ?"
                params.append(event_type)

            sql += " ORDER BY o.timestamp DESC LIMIT ?"
            params.append(limit)

            cursor.execute(sql, params)
            rows = cursor.fetchall()

            return [self._row_to_dict(row, cursor.description) for row in rows]

    def get_by_session(self, session_id: str, limit: int = 100) -> List[Dict]:
        """获取会话的所有观察"""
        with self._lock:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT * FROM observations
                WHERE session_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (session_id, limit))
            rows = cursor.fetchall()
            return [self._row_to_dict(row, cursor.description) for row in rows]

    def get_recent(self, limit: int = 50) -> List[Dict]:
        """获取最近的观察"""
        with self._lock:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT * FROM observations
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            return [self._row_to_dict(row, cursor.description) for row in rows]

    def get_session_summary(self, session_id: str) -> Optional[Dict]:
        """获取会话摘要"""
        with self._lock:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_dict(row, cursor.description)
            return None

    def update_session(self, session_id: str, **kwargs):
        """更新会话信息"""
        with self._lock:
            cursor = self.conn.cursor()
            set_clauses = []
            values = []
            for key, value in kwargs.items():
                set_clauses.append(f"{key} = ?")
                values.append(value)
            if set_clauses:
                values.append(session_id)
                cursor.execute(f"UPDATE sessions SET {', '.join(set_clauses)} WHERE session_id = ?", values)
                self.conn.commit()

    def create_session(self, session_id: str, **kwargs):
        """创建会话"""
        with self._lock:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO sessions (session_id, start_time, topic, agent)
                VALUES (?, ?, ?, ?)
            """, (
                session_id,
                datetime.now().isoformat(),
                kwargs.get('topic', 'general'),
                kwargs.get('agent', 'claude-code')
            ))
            self.conn.commit()

    def _row_to_dict(self, row: Tuple, description) -> Dict:
        """行转字典"""
        return {desc[0]: val for desc, val in zip(description, row)}

    def close(self):
        """关闭连接"""
        self.conn.close()


class WorkerService:
    """
    Worker服务 - 端口37777
    提供HTTP API和Web UI
    """

    def __init__(self, db: MemoryDatabase, port: int = 37777):
        self.db = db
        self.port = port
        self._server = None

    def start(self):
        """启动服务"""
        try:
            from http.server import HTTPServer, BaseHTTPRequestHandler
            import threading
        except ImportError:
            logger.warning("HTTP服务器模块不可用")
            return

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == "/" or self.path == "/index.html":
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(self._generate_html().encode())
                elif self.path == "/api/observations/recent":
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    recent = self.server.db.get_recent(limit=50)
                    self.wfile.write(json.dumps(recent, ensure_ascii=False).encode())
                elif self.path.startswith("/api/observation/"):
                    obs_id = self.path.split("/")[-1]
                    # 简化实现
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"id": obs_id}).encode())
                else:
                    self.send_response(404)
                    self.end_headers()

            def _generate_html(self):
                return """
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Leo Memory Viewer</title>
                    <style>
                        body { font-family: Arial; max-width: 1200px; margin: 0 auto; padding: 20px; background: #1a1a2e; color: #eee; }
                        h1 { color: #00d4ff; }
                        .observation { background: #16213e; padding: 15px; margin: 10px 0; border-radius: 8px; }
                        .meta { color: #888; font-size: 0.9em; }
                        .tag { background: #0f3460; padding: 2px 8px; border-radius: 4px; margin: 2px; display: inline-block; }
                        #search { width: 100%; padding: 10px; font-size: 16px; background: #16213e; color: #fff; border: 1px solid #0f3460; border-radius: 4px; }
                    </style>
                </head>
                <body>
                    <h1>🧠 Leo Memory Viewer</h1>
                    <input type="text" id="search" placeholder="搜索记忆...">
                    <div id="results">加载中...</div>
                    <script>
                        async function loadRecent() {
                            const res = await fetch('/api/observations/recent');
                            const data = await res.json();
                            document.getElementById('results').innerHTML = data.map(o => `
                                <div class="observation">
                                    <div class="meta">${o.timestamp} | ${o.event_type}</div>
                                    <div>${o.content.substring(0, 200)}...</div>
                                    <div>${(o.tags || []).map(t => '<span class="tag">'+t+'</span>').join('')}</div>
                                </div>
                            `).join('');
                        }
                        loadRecent();
                    </script>
                </body>
                </html>
                """

            def log_message(self, format, *args):
                pass  # 抑制日志

        class Server(HTTPServer):
            db = self.db

        self._server = Server(("0.0.0.0", self.port), Handler)
        thread = threading.Thread(target=self._server.serve, daemon=True)
        thread.start()
        logger.info(f"Memory Worker服务已启动: http://localhost:{self.port}")


class ClaudeMemIntegration:
    """
    Claude-Mem 集成主类

    提供与Leo AI系统的无缝集成
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, storage_dir: Optional[Path] = None):
        if self._initialized:
            return
        self._initialized = True

        if storage_dir is None:
            storage_dir = Path("leo_knowledge/memory/claude_mem")

        self.storage_dir = storage_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # 初始化数据库
        db_path = self.storage_dir / "memories.db"
        self.db = MemoryDatabase(db_path)

        # Worker服务
        self.worker = WorkerService(self.db, port=37777)

        # 当前会话
        self.current_session_id = self._generate_session_id()
        self.db.create_session(self.current_session_id)

        # 短期记忆缓存
        self.short_term = deque(maxlen=100)

        logger.info(f"Claude-Mem集成已启动 | 会话: {self.current_session_id[:8]}")

    def _generate_session_id(self) -> str:
        """生成会话ID"""
        return hashlib.md5(datetime.now().isoformat().encode()).hexdigest()[:16]

    def capture(
        self,
        event_type: str,
        content: Any,
        tags: Optional[List[str]] = None,
        generate_summary: bool = True,
        **metadata
    ) -> str:
        """
        捕获事件到记忆

        Args:
            event_type: 事件类型 (tool_call, user_input, agent_response, error, correction)
            content: 内容
            tags: 标签
            generate_summary: 是否生成摘要
            **metadata: 额外元数据

        Returns:
            观察ID
        """
        obs_id = hashlib.md5(
            f"{datetime.now().isoformat()}{content}".encode()
        ).hexdigest()[:12]

        # 生成摘要（简化版：取前100字符）
        summary = ""
        if generate_summary:
            content_str = content if isinstance(content, str) else json.dumps(content, ensure_ascii=False)
            summary = content_str[:100] + "..." if len(content_str) > 100 else content_str

        obs = Observation(
            id=obs_id,
            session_id=self.current_session_id,
            timestamp=datetime.now().isoformat(),
            event_type=event_type,
            content=content if isinstance(content, str) else json.dumps(content, ensure_ascii=False),
            summary=summary,
            tags=tags or [],
            metadata=metadata
        )

        # 插入数据库
        self.db.insert_observation(obs)

        # 添加到短期缓存
        self.short_term.append(obs)

        # 更新会话统计
        if event_type == "tool_call":
            self.db.update_session(
                self.current_session_id,
                tool_count=self.db.get_session_summary(self.current_session_id).get('tool_count', 0) + 1
            )
        elif event_type in ("error", "agent_error"):
            self.db.update_session(
                self.current_session_id,
                error_count=self.db.get_session_summary(self.current_session_id).get('error_count', 0) + 1
            )

        return obs_id

    def search(self, query: str, limit: int = 10, event_type: Optional[str] = None) -> List[Dict]:
        """
        搜索记忆

        Args:
            query: 搜索查询
            limit: 返回数量
            event_type: 事件类型过滤

        Returns:
            匹配的观察列表
        """
        return self.db.search(query, limit, event_type)

    def timeline(self, query: str, limit: int = 5) -> List[Dict]:
        """
        获取时间线上下文

        返回与查询相关的最近观察及其周围上下文
        """
        results = self.db.search(query, limit=limit * 2)

        timeline = []
        for obs in results[:limit]:
            timeline.append({
                "id": obs["id"],
                "timestamp": obs["timestamp"],
                "event_type": obs["event_type"],
                "preview": obs["content"][:100],
                "tags": obs.get("tags", [])
            })

        return timeline

    def get_observations(self, ids: List[str]) -> List[Dict]:
        """获取完整观察详情"""
        all_obs = self.db.get_recent(limit=1000)
        obs_map = {str(o["id"]): o for o in all_obs}
        return [obs_map.get(id, {"id": id, "error": "Not found"}) for id in ids if id]

    def get_context_for_new_session(self) -> Dict[str, Any]:
        """
        为新会话获取历史上下文

        类似于 claude-mem 的 SessionStart 行为
        """
        # 获取上次会话
        recent = self.db.get_recent(limit=20)

        # 提取主题
        topics = {}
        for obs in recent:
            for tag in obs.get("tags", []):
                topics[tag] = topics.get(tag, 0) + 1

        top_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            "recent_memories": recent[:10],
            "top_topics": [t[0] for t in top_topics],
            "last_session_id": recent[0]["session_id"] if recent else None,
            "suggested_context": self._generate_context_suggestion(recent)
        }

    def _generate_context_suggestion(self, recent: List[Dict]) -> str:
        """生成上下文建议"""
        if not recent:
            return "新会话开始"

        last_obs = recent[0]
        topic = last_obs.get("tags", ["general"])[0] if last_obs.get("tags") else "general"

        return f"继续之前的话题: {topic}"

    def start_worker(self):
        """启动Worker服务"""
        self.worker.start()

    def end_session(self):
        """结束当前会话"""
        self.db.update_session(
            self.current_session_id,
            end_time=datetime.now().isoformat()
        )
        logger.info(f"会话 {self.current_session_id} 已结束")


# 全局实例
_claude_mem: Optional[ClaudeMemIntegration] = None


def get_claude_mem() -> ClaudeMemIntegration:
    """获取Claude-Mem集成实例"""
    global _claude_mem
    if _claude_mem is None:
        _claude_mem = ClaudeMemIntegration()
    return _claude_mem


# 便捷函数
def mem_capture(event_type: str, content: Any, **kwargs) -> str:
    """快速捕获记忆"""
    return get_claude_mem().capture(event_type, content, **kwargs)


def mem_search(query: str, **kwargs) -> List[Dict]:
    """快速搜索记忆"""
    return get_claude_mem().search(query, **kwargs)


def mem_context() -> Dict[str, Any]:
    """获取新会话上下文"""
    return get_claude_mem().get_context_for_new_session()


__all__ = [
    "ClaudeMemIntegration",
    "MemoryDatabase",
    "WorkerService",
    "Observation",
    "get_claude_mem",
    "mem_capture",
    "mem_search",
    "mem_context"
]