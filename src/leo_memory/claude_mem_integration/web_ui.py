# -*- coding: utf-8 -*-
"""
Leo Memory Worker - HTTP服务器和Web UI
======================================

提供记忆系统的HTTP API和Web查看界面

端口: 37777
Web UI: http://localhost:37777
API: http://localhost:37777/api/

Author: Leo AI System
"""

import json
import threading
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from leo_memory.claude_mem_integration.worker import get_claude_mem, ClaudeMemIntegration

logger = logging.getLogger(__name__)


class MemoryAPIHandler(BaseHTTPRequestHandler):
    """记忆API请求处理器"""

    def log_message(self, format, *args):
        """抑制默认日志"""
        pass

    def do_GET(self):
        """处理GET请求"""
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        if path == "/" or path == "/index.html":
            self._serve_html()
        elif path == "/api/observations/recent":
            self._api_recent(query)
        elif path == "/api/observations/search":
            self._api_search(query)
        elif path == "/api/observations/timeline":
            self._api_timeline(query)
        elif path == "/api/stats":
            self._api_stats()
        elif path == "/api/session":
            self._api_session()
        elif path.startswith("/api/observation/"):
            obs_id = path.split("/")[-1]
            self._api_observation(obs_id)
        else:
            self._send_json({"error": "Not found"}, 404)

    def do_POST(self):
        """处理POST请求"""
        parsed = urlparse(self.path)
        path = parsed.path

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"

        try:
            data = json.loads(body)
        except:
            data = {}

        if path == "/api/capture":
            self._api_capture(data)
        else:
            self._send_json({"error": "Not found"}, 404)

    def _serve_html(self):
        """提供Web UI"""
        html = self._generate_dashboard_html()
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def _generate_dashboard_html(self) -> str:
        """生成仪表盘HTML"""
        return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Leo Memory Viewer</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #eee;
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px;
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            margin-bottom: 20px;
        }
        h1 { color: #00d4ff; font-size: 1.8em; }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        .stat-card {
            background: rgba(255,255,255,0.05);
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }
        .stat-value { font-size: 2em; color: #00d4ff; font-weight: bold; }
        .stat-label { color: #888; margin-top: 5px; }
        .search-box {
            width: 100%;
            padding: 15px;
            font-size: 16px;
            background: rgba(255,255,255,0.1);
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 8px;
            color: #fff;
            margin-bottom: 20px;
        }
        .search-box:focus { outline: none; border-color: #00d4ff; }
        .observations {
            display: grid;
            gap: 15px;
        }
        .observation {
            background: rgba(255,255,255,0.05);
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #00d4ff;
            transition: transform 0.2s;
        }
        .observation:hover { transform: translateX(5px); }
        .observation.error { border-left-color: #ff4757; }
        .observation.tool { border-left-color: #2ed573; }
        .observation.user { border-left-color: #ffa502; }
        .meta {
            display: flex;
            gap: 15px;
            color: #888;
            font-size: 0.85em;
            margin-bottom: 10px;
        }
        .tag {
            background: rgba(0,212,255,0.2);
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            display: inline-block;
            margin-right: 5px;
        }
        .content { line-height: 1.6; }
        .empty { text-align: center; color: #888; padding: 40px; }
        .refresh-btn {
            background: #00d4ff;
            color: #1a1a2e;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
        }
        .refresh-btn:hover { background: #00b8e6; }
        #loading { text-align: center; padding: 20px; color: #888; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🧠 Leo Memory Viewer</h1>
            <div>
                <span id="session-info" style="color:#888;margin-right:15px;"></span>
                <button class="refresh-btn" onclick="loadRecent()">🔄 刷新</button>
            </div>
        </header>

        <div class="stats" id="stats">
            <div class="stat-card">
                <div class="stat-value" id="total-count">-</div>
                <div class="stat-label">总记忆数</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="session-count">-</div>
                <div class="stat-label">本次会话</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="tool-count">-</div>
                <div class="stat-label">工具调用</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="error-count">-</div>
                <div class="stat-label">错误记录</div>
            </div>
        </div>

        <input type="text" class="search-box" id="search" placeholder="🔍 搜索记忆... (按Enter搜索)">

        <div id="loading">加载中...</div>
        <div class="observations" id="observations"></div>
    </div>

    <script>
        const API_BASE = '/api';
        let allObservations = [];

        async function loadStats() {
            try {
                const res = await fetch(`${API_BASE}/stats`);
                const data = await res.json();
                document.getElementById('total-count').textContent = data.total_observations || 0;
                document.getElementById('session-count').textContent = data.session_count || 0;
                document.getElementById('tool-count').textContent = data.tool_calls || 0;
                document.getElementById('error-count').textContent = data.errors || 0;
            } catch (e) {
                console.error('Stats load failed:', e);
            }
        }

        async function loadSession() {
            try {
                const res = await fetch(`${API_BASE}/session`);
                const data = await res.json();
                document.getElementById('session-info').textContent = `Session: ${data.session_id || 'N/A'}`;
            } catch (e) {
                console.error('Session load failed:', e);
            }
        }

        async function loadRecent() {
            document.getElementById('loading').style.display = 'block';
            document.getElementById('observations').innerHTML = '';

            try {
                const res = await fetch(`${API_BASE}/observations/recent?limit=50`);
                const data = await res.json();
                allObservations = data;
                renderObservations(data);
            } catch (e) {
                console.error('Load failed:', e);
                document.getElementById('observations').innerHTML = '<div class="empty">加载失败</div>';
            }

            document.getElementById('loading').style.display = 'none';
        }

        async function searchObservations(query) {
            if (!query.trim()) {
                loadRecent();
                return;
            }

            document.getElementById('loading').style.display = 'block';

            try {
                const res = await fetch(`${API_BASE}/observations/search?query=${encodeURIComponent(query)}`);
                const data = await res.json();
                renderObservations(data.results || []);
            } catch (e) {
                console.error('Search failed:', e);
            }

            document.getElementById('loading').style.display = 'none';
        }

        function renderObservations(observations) {
            const container = document.getElementById('observations');

            if (!observations || observations.length === 0) {
                container.innerHTML = '<div class="empty">暂无记忆记录</div>';
                return;
            }

            container.innerHTML = observations.map(obs => {
                const typeClass = obs.event_type === 'error' ? 'error' :
                                  obs.event_type === 'tool_call' ? 'tool' :
                                  obs.event_type === 'user_input' ? 'user' : '';
                const tags = obs.tags ? JSON.parse(obs.tags) : [];
                const content = obs.content || obs.content_text || '';

                return `
                    <div class="observation ${typeClass}">
                        <div class="meta">
                            <span>⏰ ${formatTime(obs.timestamp)}</span>
                            <span>📁 ${obs.event_type}</span>
                            <span>#${obs.id}</span>
                        </div>
                        <div class="content">${escapeHtml(content.substring(0, 300))}${content.length > 300 ? '...' : ''}</div>
                        ${tags.length > 0 ? `<div style="margin-top:10px">${tags.map(t => `<span class="tag">${t}</span>`).join('')}</div>` : ''}
                    </div>
                `;
            }).join('');
        }

        function formatTime(timestamp) {
            if (!timestamp) return 'N/A';
            const d = new Date(timestamp);
            return d.toLocaleString('zh-CN');
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        // Event listeners
        document.getElementById('search').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                searchObservations(e.target.value);
            }
        });

        // Initial load
        loadStats();
        loadSession();
        loadRecent();

        // Auto refresh every 30s
        setInterval(() => {
            loadStats();
            loadRecent();
        }, 30000);
    </script>
</body>
</html>"""

    def _api_recent(self, query):
        """获取最近的记忆"""
        mem = get_claude_mem()
        limit = int(query.get("limit", [50])[0])
        recent = mem.db.get_recent(limit=limit)
        self._send_json(recent)

    def _api_search(self, query):
        """搜索记忆"""
        q = query.get("query", [""])[0]
        mem = get_claude_mem()
        results = mem.search(q, limit=20)
        self._send_json({"results": results, "query": q})

    def _api_timeline(self, query):
        """获取时间线"""
        q = query.get("query", [""])[0]
        mem = get_claude_mem()
        timeline = mem.timeline(q)
        self._send_json({"timeline": timeline})

    def _api_stats(self):
        """获取统计信息"""
        mem = get_claude_mem()
        session = mem.db.get_session_summary(mem.current_session_id)
        recent = mem.db.get_recent(limit=1000)

        stats = {
            "total_observations": len(recent),
            "session_count": recent[0]["session_id"] if recent else "N/A",
            "tool_calls": sum(1 for o in recent if o.get("event_type") == "tool_call"),
            "errors": sum(1 for o in recent if "error" in o.get("event_type", "").lower())
        }
        self._send_json(stats)

    def _api_session(self):
        """获取会话信息"""
        mem = get_claude_mem()
        self._send_json({
            "session_id": mem.current_session_id,
            "timestamp": datetime.now().isoformat()
        })

    def _api_observation(self, obs_id):
        """获取单个观察详情"""
        mem = get_claude_mem()
        obs = mem.get_observations([obs_id])
        if obs:
            self._send_json(obs[0])
        else:
            self._send_json({"error": "Not found"}, 404)

    def _api_capture(self, data):
        """捕获新观察"""
        event_type = data.get("event_type", "manual")
        content = data.get("content", "")
        tags = data.get("tags", [])

        mem = get_claude_mem()
        obs_id = mem.capture(event_type, content, tags=tags)
        self._send_json({"id": obs_id, "status": "captured"})

    def _send_json(self, data, status=200):
        """发送JSON响应"""
        if isinstance(data, tuple):
            data, status = data

        self.send_response(status)
        self.send_header("Content-type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))


class MemoryServer(HTTPServer):
    """记忆服务器"""

    def __init__(self, port=37777):
        super().__init__(("0.0.0.0", port), MemoryAPIHandler)
        self.port = port

    def start_background(self):
        """后台启动服务器"""
        thread = threading.Thread(target=self.serve, daemon=True)
        thread.start()
        logger.info(f"Memory Worker已启动: http://localhost:{self.port}")
        return self

    def run_forever(self):
        """同步运行"""
        logger.info(f"Memory Worker运行中: http://localhost:{self.port}")
        self.serve_forever()


def start_memory_server(port: int = 37777) -> MemoryServer:
    """
    启动记忆服务器

    Args:
        port: 端口号，默认37777

    Returns:
        MemoryServer实例
    """
    server = MemoryServer(port=port)
    return server


def main():
    """主入口"""
    import argparse

    parser = argparse.ArgumentParser(description="Leo Memory Worker")
    parser.add_argument("--port", type=int, default=37777, help="服务端口")
    parser.add_argument("--background", action="store_true", help="后台运行")
    args = parser.parse_args()

    server = start_memory_server(args.port)

    if args.background:
        server.start_background()
        print(f"Memory Worker已在后台启动: http://localhost:{args.port}")
    else:
        try:
            server.run_forever()
        except KeyboardInterrupt:
            print("\n服务器已停止")
            server.shutdown()


if __name__ == "__main__":
    main()