#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Leo Web Search MCP Server - 网络搜索工具
使用 Bing RSS 源和百度搜索，无需 API Key

Usage:
    python leo_web_search.py

Configuration in .mcp.json:
    "leo-web-search": {
        "command": "python",
        "args": ["D:/桌面/leo_ai_system/.mcp/leo_web_search.py"]
    }
"""

import sys
import os
import json
import re
import asyncio
import urllib.request
import urllib.parse
import ssl

# Windows UTF-8 编码设置
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

os.environ['PYTHONIOENCODING'] = 'utf-8'


class LeoWebSearch:
    """网络搜索工具"""

    def __init__(self):
        self.timeout = 30
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

    def search_with_bing_rss(self, query: str, max_results: int = 10) -> list:
        """使用 Bing RSS 搜索"""
        try:
            url = f"https://www.bing.com/news/search?q={urllib.parse.quote(query)}&format=rss"
            req = urllib.request.Request(
                url,
                headers={'User-Agent': self.user_agent}
            )

            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

            with urllib.request.urlopen(req, timeout=self.timeout, context=ctx) as response:
                xml = response.read().decode('utf-8', errors='replace')

            results = []
            items = re.findall(r'<item>(.*?)</item>', xml, re.DOTALL)

            for item in items[:max_results]:
                title = re.search(r'<title[^>]*>([^<]*)</title>', item)
                url = re.search(r'<link[^>]*>([^<]*)</link>', item)
                desc = re.search(r'<description[^>]*>([^<]*)</description>', item)
                date = re.search(r'<pubDate[^>]*>([^<]*)</pubDate>', item)

                if title and url:
                    results.append({
                        "title": title.group(1).strip(),
                        "url": url.group(1).strip(),
                        "snippet": desc.group(1).strip()[:300] if desc else "",
                        "date": date.group(1).strip() if date else "",
                        "source": "Bing News"
                    })

            return results
        except Exception as e:
            print(f"[ERROR] Bing RSS failed: {e}", flush=True, file=sys.stderr)
            return []

    def search_with_duckduckgo(self, query: str, max_results: int = 10) -> list:
        """使用 DuckDuckGo HTML 搜索"""
        try:
            url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
            req = urllib.request.Request(
                url,
                headers={'User-Agent': self.user_agent}
            )

            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

            with urllib.request.urlopen(req, timeout=self.timeout, context=ctx) as response:
                html = response.read().decode('utf-8', errors='replace')

            results = []
            # 解析 DuckDuckGo 结果
            items = re.findall(r'<a[^>]*class="result__a"[^>]*href="([^"]*)"[^>]*>(.*?)</a>', html)

            for url, title in items[:max_results]:
                # 提取实际 URL（DuckDuckGo 使用重定向）
                actual_url = url
                if 'uddg=' in url:
                    match = re.search(r'uddg=([^&]+)', url)
                    if match:
                        actual_url = urllib.parse.unquote(match.group(1))

                results.append({
                    "title": re.sub(r'<[^>]+>', '', title).strip(),
                    "url": actual_url.strip()[:200],
                    "snippet": "",
                    "source": "DuckDuckGo"
                })

            return results
        except Exception as e:
            print(f"[ERROR] DuckDuckGo failed: {e}", flush=True, file=sys.stderr)
            return []

    def search(self, query: str, max_results: int = 10) -> dict:
        """综合搜索"""
        # 优先使用 DuckDuckGo
        results = self.search_with_duckduckgo(query, max_results)

        # 如果 DuckDuckGo 没结果，尝试 Bing
        if not results:
            results = self.search_with_bing_rss(query, max_results)

        return {
            "query": query,
            "total": len(results),
            "results": results
        }


class MCPServer:
    """MCP Server for Leo Web Search"""

    def __init__(self):
        self.searcher = LeoWebSearch()

    async def handle_request(self, request: dict) -> dict:
        """Handle MCP request"""
        method = request.get("method")
        params = request.get("params", {})

        if method == "initialize":
            return await self.handle_initialize(params)
        elif method == "tools/list":
            return await self.handle_tools_list(params)
        elif method == "tools/call":
            return await self.handle_tools_call(params)
        elif method == "ping":
            return {"result": "pong"}
        else:
            return {"error": {"code": -32601, "message": f"Method not found: {method}"}}

    async def handle_initialize(self, params: dict) -> dict:
        """Initialize"""
        return {
            "result": {
                "protocolVersion": "2024-11-05",
                "serverInfo": {
                    "name": "leo-web-search",
                    "version": "1.0.0"
                },
                "capabilities": {
                    "tools": {}
                }
            }
        }

    async def handle_tools_list(self, params: dict) -> dict:
        """List tools"""
        tools = [
            {
                "name": "web_search",
                "description": "执行网络搜索，查询互联网上的最新信息。支持 Bing News 和百度搜索。",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "搜索关键词"
                        },
                        "max_results": {
                            "type": "number",
                            "description": "最大结果数量，默认 10",
                            "default": 10
                        }
                    },
                    "required": ["query"]
                }
            }
        ]
        return {"result": tools}

    async def handle_tools_call(self, params: dict) -> dict:
        """Call tool"""
        name = params.get("name")
        arguments = params.get("arguments", {})

        if name == "web_search":
            query = arguments.get("query", "")
            max_results = arguments.get("max_results", 10)

            if not query:
                return {"error": {"code": -32602, "message": "Missing required parameter: query"}}

            result = self.searcher.search(query, max_results)

            return {
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, ensure_ascii=False, indent=2)
                        }
                    ]
                }
            }
        else:
            return {"error": {"code": -32601, "message": f"Tool not found: {name}"}}


async def main():
    """Main entry point"""
    server = MCPServer()

    # 读取初始请求
    request_line = await asyncio.get_event_loop().run_in_executor(
        None, sys.stdin.readline
    )

    # 处理请求
    try:
        request = json.loads(request_line)
        response = await server.handle_request(request)
        print(json.dumps(response), flush=True)
    except Exception as e:
        error_response = {
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        }
        print(json.dumps(error_response), flush=True)


if __name__ == "__main__":
    # 检查是否是直接运行测试
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        # 测试搜索功能
        searcher = LeoWebSearch()
        result = searcher.search("人工智能", 5)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        # MCP 服务器模式
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main())
