#!/usr/bin/env python3
"""
浏览器自动化工具封装
提供 OpenCLI 和 CDP Proxy 的统一调用接口

使用方式:
    from browser_tools import OpenCLIClient, CDPClient

    # OpenCLI 调用
    client = OpenCLIClient()
    data = client.bilibili_hot(limit=10)
    data = client.xiaohongshu_search("关键词")

    # CDP 调用
    cdp = CDPClient()
    tabs = cdp.list_tabs()
    cdp.screenshot(tab_id, "/tmp/shot.png")
"""

import subprocess
import json
import requests
from typing import Optional, List, Dict, Any

# CDP Proxy 地址
CDP_BASE = "http://localhost:3456"


import platform
import os

class OpenCLIClient:
    """OpenCLI 客户端封装"""

    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        # Windows 上使用 .cmd 后缀
        self._opencli = "opencli.cmd" if os.name == 'nt' else "opencli"

    def _run(self, platform: str, cmd: str, *args, limit: int = 10, format: str = "json") -> Dict[str, Any]:
        """执行 OpenCLI 命令"""
        cmd_list = [self._opencli, platform, cmd, "-f", format, "--limit", str(limit), *args]
        try:
            result = subprocess.run(cmd_list, capture_output=True, timeout=self.timeout, encoding='utf-8', errors='replace')
            if result.returncode == 0 and result.stdout:
                return json.loads(result.stdout)
            return {"error": result.stderr or "No output", "returncode": result.returncode}
        except Exception as e:
            return {"error": str(e)}

    def bilibili_hot(self, limit: int = 10) -> Dict[str, Any]:
        """B站热门视频"""
        return self._run("bilibili", "hot", limit=limit)

    def bilibili_search(self, keyword: str, limit: int = 10) -> Dict[str, Any]:
        """B站搜索"""
        return self._run("bilibili", "search", keyword, limit=limit)

    def xiaohongshu_search(self, keyword: str, limit: int = 10) -> Dict[str, Any]:
        """小红书搜索"""
        return self._run("xiaohongshu", "search", keyword, limit=limit)

    def xiaohongshu_download(self, note_url: str, output: str = "./downloads") -> Dict[str, Any]:
        """小红书下载"""
        return self._run("xiaohongshu", "download", note_url, "--output", output, limit=1)

    def twitter_trending(self, limit: int = 10) -> Dict[str, Any]:
        """Twitter 趋势"""
        return self._run("twitter", "trending", limit=limit)

    def twitter_search(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Twitter 搜索"""
        return self._run("twitter", "search", query, limit=limit)

    def reddit_hot(self, limit: int = 10) -> Dict[str, Any]:
        """Reddit 热门"""
        return self._run("reddit", "hot", limit=limit)

    def hackernews_top(self, limit: int = 10) -> Dict[str, Any]:
        """HackerNews Top"""
        return self._run("hackernews", "top", limit=limit)

    def v2ex_hot(self, limit: int = 10) -> Dict[str, Any]:
        """V2EX 热榜"""
        return self._run("v2ex", "hot", limit=limit)

    def amazon_bestsellers(self, category: str = "electronics", limit: int = 10) -> Dict[str, Any]:
        """Amazon 畅销榜"""
        return self._run("amazon", "bestsellers", category, limit=limit)

    def amazon_search(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Amazon 搜索"""
        return self._run("amazon", "search", query, limit=limit)

    def zhihu_hot(self, limit: int = 10) -> Dict[str, Any]:
        """知乎热榜"""
        return self._run("zhihu", "hot", limit=limit)

    def youtube_search(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """YouTube 搜索"""
        return self._run("youtube", "search", query, limit=limit)

    def yahoo_finance_quote(self, symbol: str) -> Dict[str, Any]:
        """Yahoo Finance 股票行情"""
        return self._run("yahoo-finance", "quote", symbol, limit=1)

    def xueqiu_hot(self, limit: int = 10) -> Dict[str, Any]:
        """雪球热门"""
        return self._run("xueqiu", "hot", limit=limit)

    def generic(self, platform: str, cmd: str, *args, limit: int = 10) -> Dict[str, Any]:
        """通用命令接口"""
        return self._run(platform, cmd, *args, limit=limit)

    def list_platforms(self) -> List[str]:
        """列出所有平台"""
        result = subprocess.run([self._opencli, "list", "-f", "json"], capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return [c["name"] for c in data.get("commands", [])]
        return []

    def doctor(self) -> Dict[str, Any]:
        """检查 OpenCLI 状态"""
        result = subprocess.run([self._opencli, "doctor"], capture_output=True, text=True, timeout=10)
        return {"output": result.stdout, "error": result.stderr, "returncode": result.returncode}


class CDPClient:
    """CDP Proxy 客户端封装"""

    def __init__(self, base_url: str = CDP_BASE):
        self.base_url = base_url

    def _get(self, endpoint: str) -> Dict[str, Any]:
        """GET 请求"""
        try:
            resp = requests.get(f"{self.base_url}{endpoint}", timeout=30)
            return resp.json()
        except Exception as e:
            return {"error": str(e)}

    def _post(self, endpoint: str, data: str) -> Dict[str, Any]:
        """POST 请求"""
        try:
            resp = requests.post(f"{self.base_url}{endpoint}", data=data, timeout=30)
            return resp.json()
        except Exception as e:
            return {"error": str(e)}

    def list_tabs(self) -> List[Dict[str, Any]]:
        """列出所有标签页"""
        result = self._get("/targets")
        return result if isinstance(result, list) else []

    def get_tab_by_url(self, url_pattern: str) -> Optional[Dict[str, Any]]:
        """根据 URL 模式查找标签页"""
        tabs = self.list_tabs()
        for tab in tabs:
            if url_pattern in tab.get("url", ""):
                return tab
        return None

    def get_info(self, target_id: str) -> Dict[str, Any]:
        """获取标签页信息"""
        return self._get(f"/info?target={target_id}")

    def eval_js(self, target_id: str, js: str) -> Dict[str, Any]:
        """执行 JavaScript"""
        return self._post(f"/eval?target={target_id}", js)

    def navigate(self, target_id: str, url: str) -> Dict[str, Any]:
        """导航到 URL"""
        return self._get(f"/navigate?target={target_id}&url={requests.utils.quote(url)}")

    def click(self, target_id: str, selector: str) -> Dict[str, Any]:
        """点击元素"""
        return self._post(f"/click?target={target_id}", selector)

    def type_text(self, target_id: str, selector: str, text: str) -> Dict[str, Any]:
        """输入文本"""
        return self._post(f"/type?target={target_id}&text={requests.utils.quote(text)}", selector)

    def screenshot(self, target_id: str, filepath: str, format: str = "png") -> Dict[str, Any]:
        """截图"""
        return self._get(f"/screenshot?target={target_id}&file={filepath}&format={format}")

    def scroll(self, target_id: str, direction: str = "down", amount: int = 500) -> Dict[str, Any]:
        """滚动页面"""
        return self._get(f"/scroll?target={target_id}&direction={direction}&y={amount}")

    def new_tab(self, url: str) -> Dict[str, Any]:
        """打开新标签页"""
        return self._get(f"/new?url={requests.utils.quote(url)}")

    def close_tab(self, target_id: str) -> Dict[str, Any]:
        """关闭标签页"""
        return self._get(f"/close?target={target_id}")

    def health(self) -> Dict[str, Any]:
        """检查连接状态"""
        return self._get("/health")


def demo():
    """演示用法"""
    import sys
    # 设置输出为 UTF-8
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

    print("=== OpenCLI 演示 ===")
    client = OpenCLIClient()

    # 检查状态
    status = client.doctor()
    print("OpenCLI 状态:", status.get('output', 'N/A').strip().replace('\n', ' | '))

    # B站热门
    print("\n[B站热门 Top5]")
    data = client.bilibili_hot(limit=5)
    if isinstance(data, list):
        for item in data[:5]:
            rank = item.get('rank', '?')
            title = item.get('title', 'N/A')[:40]
            print(f"  {rank}. {title}")
    else:
        print("  Error:", data.get('error', 'Unknown'))

    # CDP 演示
    print("\n[CDP Proxy 标签页]")
    cdp = CDPClient()
    tabs = cdp.list_tabs()
    print(f"  共 {len(tabs)} 个标签页")
    for tab in tabs[:3]:
        title = tab.get('title', 'N/A')[:40]
        print(f"  - {title}")


if __name__ == "__main__":
    demo()
