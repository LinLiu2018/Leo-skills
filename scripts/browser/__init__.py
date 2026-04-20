"""
浏览器自动化工具包
提供 OpenCLI 和 CDP Proxy 的统一调用接口

使用方式:
    from scripts.browser import OpenCLIClient, CDPClient

    # OpenCLI 调用
    client = OpenCLIClient()
    data = client.bilibili_hot(limit=10)
    data = client.xiaohongshu_search("关键词")

    # CDP 调用
    cdp = CDPClient()
    tabs = cdp.list_tabs()
    cdp.screenshot(tab_id, "/tmp/shot.png")
"""

from .browser_tools import OpenCLIClient, CDPClient

__all__ = ['OpenCLIClient', 'CDPClient']
