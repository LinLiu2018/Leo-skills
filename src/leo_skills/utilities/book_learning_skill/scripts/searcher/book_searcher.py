#!/usr/bin/env python3
"""
书籍搜索模块 - 从 LibGen 搜索和下载书籍 PDF

使用 libgen-api-enhanced 库搜索 Library Genesis 数据库，
支持按书名、作者搜索，并下载 PDF/EPUB 文件。
"""

import logging
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

logger = logging.getLogger(__name__)


@dataclass
class BookInfo:
    """书籍信息"""
    title: str
    author: str
    year: str = ""
    publisher: str = ""
    language: str = ""
    pages: str = ""
    size: str = ""
    extension: str = ""
    md5: str = ""
    download_url: str = ""
    mirrors: List[str] = field(default_factory=list)
    _raw: Any = field(default=None, repr=False)  # 原始 Book 对象


class BookSearcher:
    """书籍搜索器 - 从 LibGen 搜索和下载书籍"""

    def __init__(self, download_dir: str = None):
        """
        初始化书籍搜索器。

        Args:
            download_dir: 下载目录，默认为技能目录下的 downloads/
        """
        if download_dir:
            self.download_dir = Path(download_dir)
        else:
            self.download_dir = Path(__file__).parent.parent.parent / "downloads"
        self.download_dir.mkdir(parents=True, exist_ok=True)

        # 检查 libgen-api-enhanced 是否可用
        self._has_libgen = False
        try:
            from libgen_api_enhanced import LibgenSearch
            self._libgen = LibgenSearch()
            self._has_libgen = True
            logger.info("LibGen API 已加载")
        except ImportError:
            logger.warning(
                "libgen-api-enhanced 未安装，书籍搜索功能不可用。"
                "安装命令: pip install libgen-api-enhanced"
            )

    def search(
        self,
        query: str,
        search_type: str = "title",
        max_results: int = 10,
        filters: Optional[Dict[str, str]] = None,
    ) -> List[BookInfo]:
        """
        搜索书籍。

        Args:
            query: 搜索关键词（书名、作者等）
            search_type: 搜索类型 - "title" 或 "author"
            max_results: 最大返回结果数
            filters: 过滤条件，如 {"extension": "pdf", "language": "Chinese"}

        Returns:
            BookInfo 列表
        """
        if not self._has_libgen:
            logger.error("LibGen API 不可用，请先安装: pip install libgen-api-enhanced")
            return []

        logger.info(f"搜索书籍: '{query}' (类型: {search_type})")

        try:
            from libgen_api_enhanced import LibgenSearch
            s = LibgenSearch()

            # 根据搜索类型和过滤条件选择方法
            if filters:
                if search_type == "author":
                    results = s.search_author_filtered(query, filters)
                else:
                    results = s.search_title_filtered(query, filters)
            else:
                if search_type == "author":
                    results = s.search_author(query)
                else:
                    results = s.search_title(query)

            # 转换为 BookInfo 列表
            books = []
            for item in results[:max_results]:
                # libgen-api-enhanced 返回的是 Book 对象或字典
                if hasattr(item, 'title'):
                    book = BookInfo(
                        title=getattr(item, 'title', ''),
                        author=getattr(item, 'author', ''),
                        year=getattr(item, 'year', ''),
                        publisher=getattr(item, 'publisher', ''),
                        language=getattr(item, 'language', ''),
                        pages=getattr(item, 'pages', ''),
                        size=getattr(item, 'size', ''),
                        extension=getattr(item, 'extension', ''),
                        md5=getattr(item, 'md5', ''),
                        mirrors=getattr(item, 'mirrors', []),
                        _raw=item,
                    )
                else:
                    # 字典格式
                    book = BookInfo(
                        title=item.get('Title', ''),
                        author=item.get('Author', ''),
                        year=item.get('Year', ''),
                        publisher=item.get('Publisher', ''),
                        language=item.get('Language', ''),
                        pages=item.get('Pages', ''),
                        size=item.get('Size', ''),
                        extension=item.get('Extension', ''),
                        md5=item.get('MD5', ''),
                        mirrors=item.get('Mirror_1', '').split(',') if item.get('Mirror_1') else [],
                    )
                books.append(book)

            logger.info(f"找到 {len(books)} 本书")
            return books

        except Exception as e:
            logger.error(f"搜索失败: {e}")
            return []

    def download(self, book: BookInfo, filename: str = None) -> Optional[Path]:
        """
        下载书籍文件。

        Args:
            book: 书籍信息对象
            filename: 自定义文件名，默认使用书名

        Returns:
            下载文件的路径，失败返回 None
        """
        if not filename:
            safe_title = re.sub(r'[<>:"/\\|?*\n\r]', '_', book.title)[:100].strip()
            filename = f"{safe_title}.{book.extension or 'pdf'}"

        filepath = self.download_dir / filename

        if filepath.exists() and filepath.stat().st_size > 10000:
            logger.info(f"文件已存在: {filepath}")
            return filepath

        # 收集所有可能的下载链接
        urls = self._collect_download_urls(book)
        if not urls:
            logger.error("无法获取任何下载链接")
            return None

        # 禁用 SSL 警告
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        # 逐个尝试下载
        for i, url in enumerate(urls):
            logger.info(f"尝试下载 ({i+1}/{len(urls)}): {url[:80]}...")
            try:
                resp = requests.get(
                    url, stream=True, timeout=180,
                    verify=False, allow_redirects=True,
                    headers={"User-Agent": "Mozilla/5.0"}
                )
                resp.raise_for_status()

                # 验证返回的是文件而非 HTML
                content_type = resp.headers.get('content-type', '')
                if 'text/html' in content_type:
                    logger.warning(f"返回 HTML 而非文件，跳过")
                    resp.close()
                    continue

                total_size = int(resp.headers.get('content-length', 0))
                downloaded = 0

                with open(filepath, 'wb') as f:
                    for chunk in resp.iter_content(chunk_size=65536):
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0 and downloaded % (5 * 1024 * 1024) < 65536:
                            pct = downloaded / total_size * 100
                            logger.info(f"下载进度: {pct:.0f}% ({downloaded // 1024 // 1024}MB/{total_size // 1024 // 1024}MB)")

                # 验证文件有效性
                if filepath.stat().st_size < 10000:
                    logger.warning(f"文件太小 ({filepath.stat().st_size} bytes)，可能无效")
                    filepath.unlink()
                    continue

                logger.info(f"下载完成: {filepath.name} ({downloaded / 1024 / 1024:.1f} MB)")
                return filepath

            except Exception as e:
                logger.warning(f"下载失败: {e}")
                if filepath.exists():
                    filepath.unlink()
                continue

        logger.error(f"所有下载源均失败")
        return None

    def _collect_download_urls(self, book: BookInfo) -> List[str]:
        """收集所有可能的下载链接，按优先级排序"""
        urls = []

        # 已有的直接链接
        if book.download_url:
            urls.append(book.download_url)

        # 方法1: 内置 resolve（最可靠）
        if book._raw and hasattr(book._raw, 'resolve_direct_download_link'):
            try:
                book._raw.resolve_direct_download_link()
                if book._raw.resolved_download_link:
                    urls.append(book._raw.resolved_download_link)
                    logger.info(f"内置解析成功: {book._raw.resolved_download_link[:60]}...")
            except Exception as e:
                logger.debug(f"内置解析失败: {e}")

        # 方法2: Anna's Archive（备用）
        for mirror in book.mirrors:
            if 'annas-archive' in mirror:
                urls.append(mirror)

        # 方法3: libgen.li/get.php 直接构造
        if book.md5:
            urls.append(f"https://libgen.li/get.php?md5={book.md5}")

        # 方法4: 从 mirror 页面解析
        for mirror in book.mirrors:
            if not mirror or not mirror.startswith('http'):
                continue
            if mirror in urls:
                continue
            try:
                resp = requests.get(mirror, timeout=15, verify=False,
                                    headers={"User-Agent": "Mozilla/5.0"})
                if resp.status_code == 200:
                    match = re.search(r'href="(https?://[^"]+)"[^>]*>\s*GET', resp.text)
                    if match:
                        urls.append(match.group(1))
                    match = re.search(r'href="(https?://download[^"]+)"', resp.text)
                    if match and match.group(1) not in urls:
                        urls.append(match.group(1))
            except Exception:
                continue

        # 去重
        seen = set()
        unique = []
        for u in urls:
            if u not in seen:
                seen.add(u)
                unique.append(u)

        return unique

    def search_and_list(self, query: str, **kwargs) -> str:
        """
        搜索并返回格式化的结果列表（方便用户选择）。

        Args:
            query: 搜索关键词

        Returns:
            格式化的搜索结果字符串
        """
        books = self.search(query, **kwargs)
        if not books:
            return f"未找到与 '{query}' 相关的书籍"

        lines = [f"搜索 '{query}' 找到 {len(books)} 本书:\n"]
        for i, book in enumerate(books, 1):
            lines.append(
                f"  [{i}] {book.title}\n"
                f"      作者: {book.author} | 年份: {book.year} | "
                f"格式: {book.extension} | 大小: {book.size} | "
                f"语言: {book.language}"
            )
        return "\n".join(lines)
