#!/usr/bin/env python3
"""
书籍提取模块 - 从 PDF/EPUB 提取文本并识别章节结构

支持 PDF（PyMuPDF/pdfplumber）和 EPUB（ebooklib）格式，
自动识别中英文章节标题，输出结构化的章节内容。
"""

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# 检查可用的 PDF 库
try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False

try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False

try:
    import ebooklib
    from ebooklib import epub
    from bs4 import BeautifulSoup
    HAS_EPUB = True
except ImportError:
    HAS_EPUB = False


@dataclass
class Chapter:
    """章节信息"""
    title: str
    level: int  # 1=一级标题, 2=二级标题...
    content: str
    page_start: int = 0
    page_end: int = 0
    word_count: int = 0


@dataclass
class BookContent:
    """书籍内容"""
    title: str
    author: str
    chapters: List[Chapter]
    metadata: Dict[str, Any]
    total_pages: int = 0
    total_words: int = 0
    raw_text: str = ""


class BookExtractor:
    """书籍内容提取器 - 支持 PDF 和 EPUB 格式"""

    # 主章节模式（Chapter/Part/第X章 级别）
    MAJOR_CHAPTER_PATTERNS = [
        re.compile(r'^第[一二三四五六七八九十百千\d]+[章篇部][\s:：]*(.*)', re.MULTILINE),
        # "Chapter X\nTitle" 格式（标题在下一行，以大写字母开头）
        re.compile(r'^Chapter\s+\d+\n([A-Z][A-Za-z\s,\-:]+)$', re.MULTILINE),
        # "Chapter X: Title" 或 "Chapter X. Title" 单行格式
        re.compile(r'^Chapter\s+\d+[\s:：.]\s*([A-Z][A-Za-z\s,\-]{3,})', re.MULTILINE),
        re.compile(r'^Part\s+[IVXLCDM\d]+[\s:：.]\s*(.*)', re.IGNORECASE | re.MULTILINE),
        re.compile(r'^CHAPTER\s+[IVXLCDM\d]+[\s:：.]\s*(.*)', re.MULTILINE),
    ]

    # 顶级数字编号模式（"1. Introduction" 等，需要标题是 Title Case 或全大写）
    TOP_LEVEL_NUM_PATTERN = re.compile(
        r'^(\d{1,2})\.\s+([A-Z][a-zA-Z\s,\-]{3,60})\s*$', re.MULTILINE
    )

    # 子节模式（1.1, 1.2 级别，仅在主章节不足时使用）
    SECTION_PATTERNS = [
        re.compile(r'^第[一二三四五六七八九十百千\d]+[节][\s:：]*(.*)', re.MULTILINE),
        re.compile(r'^[（(]?[一二三四五六七八九十]+[）)][\s、.．]*(.*)', re.MULTILINE),
    ]

    # 最大章节数限制（避免 API 调用爆炸）
    MAX_CHAPTERS = 30

    def __init__(self):
        """初始化提取器，检查可用库"""
        available = []
        if HAS_PYMUPDF:
            available.append("PyMuPDF")
        if HAS_PDFPLUMBER:
            available.append("pdfplumber")
        if HAS_EPUB:
            available.append("ebooklib")

        if not available:
            logger.warning(
                "未安装任何提取库。安装命令:\n"
                "  pip install PyMuPDF pdfplumber ebooklib beautifulsoup4"
            )
        else:
            logger.info(f"可用提取库: {', '.join(available)}")

    def extract(self, file_path: str) -> BookContent:
        """
        提取书籍内容。

        Args:
            file_path: PDF 或 EPUB 文件路径

        Returns:
            BookContent 对象
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        ext = path.suffix.lower()
        if ext == '.pdf':
            return self._extract_pdf(str(path))
        elif ext in ('.epub', '.epub3'):
            return self._extract_epub(str(path))
        else:
            raise ValueError(f"不支持的格式: {ext}，仅支持 PDF 和 EPUB")

    def _extract_pdf(self, pdf_path: str) -> BookContent:
        """使用 PyMuPDF 或 pdfplumber 提取 PDF"""
        if HAS_PYMUPDF:
            return self._extract_pdf_pymupdf(pdf_path)
        elif HAS_PDFPLUMBER:
            return self._extract_pdf_pdfplumber(pdf_path)
        else:
            raise ImportError("需要安装 PyMuPDF 或 pdfplumber: pip install PyMuPDF")

    def _extract_pdf_pymupdf(self, pdf_path: str) -> BookContent:
        """使用 PyMuPDF (fitz) 提取 PDF - 速度快，质量好"""
        logger.info(f"使用 PyMuPDF 提取: {pdf_path}")

        doc = fitz.open(pdf_path)
        metadata = doc.metadata or {}

        # 提取所有页面文本
        pages_text = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            if text.strip():
                pages_text.append((page_num + 1, text))

        # 优先使用 PDF 内置目录（TOC）
        toc = doc.get_toc()
        total_pages = len(doc)
        doc.close()

        raw_text = "\n".join(text for _, text in pages_text)
        title = metadata.get("title", "") or self._guess_title(raw_text, pdf_path)
        author = metadata.get("author", "") or "未知作者"

        # 识别章节：优先 TOC，其次正则
        if toc and len(toc) >= 3:
            chapters = self._chapters_from_toc(toc, pages_text, total_pages)
        else:
            chapters = self._detect_chapters(pages_text)

        total_words = sum(len(ch.content) for ch in chapters) if chapters else len(raw_text)

        return BookContent(
            title=title,
            author=author,
            chapters=chapters,
            metadata=metadata,
            total_pages=len(pages_text),
            total_words=total_words,
            raw_text=raw_text,
        )

    def _chapters_from_toc(self, toc: list, pages_text: list, total_pages: int) -> List[Chapter]:
        """从 PDF 内置目录提取主章节（只取 Level 1）"""
        # 只取 level 1 的条目，过滤掉封面、版权、目录等
        skip_titles = {'cover', 'contents', 'preface', 'acknowledgements',
                       'exercises', 'bibliography', 'references', 'index',
                       'notation', 'copyright', '©'}
        main_chapters = []
        for level, title, page in toc:
            if level == 1:
                clean = title.strip()
                if clean.lower() not in skip_titles and len(clean) > 1:
                    main_chapters.append((clean, page))

        # 如果 level 1 太少（可能 level 2 才是主章节）
        if len(main_chapters) < 5:
            main_chapters = []
            for level, title, page in toc:
                if level <= 2:
                    clean = title.strip()
                    if clean.lower() not in skip_titles and len(clean) > 1:
                        main_chapters.append((clean, page))

        # 限制最大章节数
        if len(main_chapters) > self.MAX_CHAPTERS:
            # 只保留 level 1
            l1_only = [(t, p) for level, t, p in toc if level == 1
                       and t.strip().lower() not in skip_titles and len(t.strip()) > 1]
            if len(l1_only) >= 3:
                main_chapters = l1_only[:self.MAX_CHAPTERS]
            else:
                main_chapters = main_chapters[:self.MAX_CHAPTERS]

        # 构建页码到文本的映射
        page_text_map = {}
        for page_num, text in pages_text:
            page_text_map[page_num] = text

        # 构建章节内容
        chapters = []
        for i, (title, start_page) in enumerate(main_chapters):
            end_page = main_chapters[i + 1][1] - 1 if i + 1 < len(main_chapters) else total_pages
            end_page = max(end_page, start_page)

            content_parts = []
            for p in range(start_page, end_page + 1):
                if p in page_text_map:
                    content_parts.append(page_text_map[p])

            content = "\n".join(content_parts)
            chapters.append(Chapter(
                title=title,
                level=1,
                content=content,
                page_start=start_page,
                page_end=end_page,
                word_count=len(content),
            ))

        logger.info(f"从 TOC 提取 {len(chapters)} 个主章节")
        return chapters

    def _extract_pdf_pdfplumber(self, pdf_path: str) -> BookContent:
        """使用 pdfplumber 提取 PDF - 备选方案"""
        logger.info(f"使用 pdfplumber 提取: {pdf_path}")

        pages_text = []
        metadata = {}

        with pdfplumber.open(pdf_path) as pdf:
            if pdf.metadata:
                metadata = dict(pdf.metadata)
            for page_num, page in enumerate(pdf.pages, 1):
                text = page.extract_text()
                if text and text.strip():
                    pages_text.append((page_num, text))

        raw_text = "\n".join(text for _, text in pages_text)
        title = metadata.get("Title", "") or self._guess_title(raw_text, pdf_path)
        author = metadata.get("Author", "") or "未知作者"

        chapters = self._detect_chapters(pages_text)
        total_words = sum(len(ch.content) for ch in chapters) if chapters else len(raw_text)

        return BookContent(
            title=title,
            author=author,
            chapters=chapters,
            metadata=metadata,
            total_pages=len(pages_text),
            total_words=total_words,
            raw_text=raw_text,
        )

    def _extract_epub(self, epub_path: str) -> BookContent:
        """提取 EPUB 格式书籍"""
        if not HAS_EPUB:
            raise ImportError("需要安装 ebooklib: pip install ebooklib beautifulsoup4")

        logger.info(f"提取 EPUB: {epub_path}")

        book = epub.read_epub(epub_path)

        # 提取元数据
        title = book.get_metadata('DC', 'title')
        title = title[0][0] if title else Path(epub_path).stem
        author = book.get_metadata('DC', 'creator')
        author = author[0][0] if author else "未知作者"

        # 提取章节内容
        chapters = []
        for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
            soup = BeautifulSoup(item.get_content(), 'html.parser')
            text = soup.get_text(separator='\n', strip=True)
            if text and len(text) > 100:  # 跳过太短的内容（目录页等）
                # 尝试从 HTML 标题标签获取章节名
                heading = soup.find(['h1', 'h2', 'h3'])
                ch_title = heading.get_text(strip=True) if heading else f"章节 {len(chapters) + 1}"

                chapters.append(Chapter(
                    title=ch_title,
                    level=1,
                    content=text,
                    word_count=len(text),
                ))

        raw_text = "\n\n".join(ch.content for ch in chapters)

        return BookContent(
            title=title,
            author=author,
            chapters=chapters,
            metadata={"format": "epub"},
            total_pages=len(chapters),
            total_words=sum(ch.word_count for ch in chapters),
            raw_text=raw_text,
        )

    def _detect_chapters(self, pages_text: List[tuple]) -> List[Chapter]:
        """
        从页面文本中检测章节结构。
        优先识别主章节（Chapter级别），子节内容合并到主章节中。
        限制最大章节数避免 API 调用爆炸。
        """
        full_text = ""
        page_offsets = []
        for page_num, text in pages_text:
            page_offsets.append((len(full_text), page_num))
            full_text += text + "\n"

        # 第一步：尝试匹配主章节（Chapter/Part/第X章）
        chapter_positions = self._match_patterns(full_text, self.MAJOR_CHAPTER_PATTERNS, level=1)

        # 第一步半：尝试顶级数字编号（"1. Introduction" 等）
        if len(chapter_positions) < 3:
            for match in self.TOP_LEVEL_NUM_PATTERN.finditer(full_text):
                pos = match.start()
                num = match.group(1)
                title = match.group(0).strip()[:200]
                chapter_positions.append((pos, title, 1))

        # 第二步：如果主章节太少（<3），加入子节模式
        if len(chapter_positions) < 3:
            section_positions = self._match_patterns(full_text, self.SECTION_PATTERNS, level=2)
            chapter_positions.extend(section_positions)

        if not chapter_positions:
            logger.info("未检测到章节标题，按页数分块")
            return self._split_by_pages(pages_text, pages_per_chunk=30)

        # 排序去重
        chapter_positions.sort(key=lambda x: x[0])
        seen_titles = set()
        unique = []
        for pos, title, level in chapter_positions:
            clean_title = title.strip()[:100]
            # 过滤掉太短或纯数字的标题
            if len(clean_title) < 2 or clean_title.replace('.', '').replace(' ', '').isdigit():
                continue
            if clean_title not in seen_titles:
                seen_titles.add(clean_title)
                unique.append((pos, clean_title, level))

        # 第三步：如果章节太多，只保留 level=1 的主章节
        if len(unique) > self.MAX_CHAPTERS:
            major_only = [c for c in unique if c[2] == 1]
            if len(major_only) >= 3:
                unique = major_only

        # 第四步：如果仍然太多，合并相邻章节
        if len(unique) > self.MAX_CHAPTERS:
            unique = self._merge_chapters(unique, self.MAX_CHAPTERS)

        # 构建章节内容
        chapters = []
        for i, (pos, title, level) in enumerate(unique):
            end_pos = unique[i + 1][0] if i + 1 < len(unique) else len(full_text)
            content = full_text[pos:end_pos].strip()

            # 跳过内容太少的章节（可能是误匹配）
            if len(content) < 200:
                continue

            page_start = page_end = 1
            for offset, page_num in page_offsets:
                if offset <= pos:
                    page_start = page_num
                if offset <= end_pos:
                    page_end = page_num

            chapters.append(Chapter(
                title=title,
                level=level,
                content=content,
                page_start=page_start,
                page_end=page_end,
                word_count=len(content),
            ))

        logger.info(f"检测到 {len(chapters)} 个章节")
        return chapters

    def _match_patterns(self, text: str, patterns: list, level: int) -> List[tuple]:
        """用一组模式匹配文本，返回 (position, title, level) 列表"""
        results = []
        for pattern in patterns:
            for match in pattern.finditer(text):
                pos = match.start()
                title = match.group(0).strip()[:200]
                results.append((pos, title, level))
        return results

    def _merge_chapters(self, chapters: List[tuple], target: int) -> List[tuple]:
        """合并章节直到数量 <= target，保留均匀分布"""
        if len(chapters) <= target:
            return chapters
        step = max(1, len(chapters) // target)
        merged = []
        for i in range(0, len(chapters), step):
            merged.append(chapters[i])
            if len(merged) >= target:
                break
        return merged

    def _split_by_pages(self, pages_text: List[tuple], pages_per_chunk: int = 20) -> List[Chapter]:
        """当无法检测章节时，按固定页数分块"""
        chapters = []
        for i in range(0, len(pages_text), pages_per_chunk):
            chunk = pages_text[i:i + pages_per_chunk]
            content = "\n".join(text for _, text in chunk)
            page_start = chunk[0][0]
            page_end = chunk[-1][0]

            chapters.append(Chapter(
                title=f"第 {page_start}-{page_end} 页",
                level=1,
                content=content,
                page_start=page_start,
                page_end=page_end,
                word_count=len(content),
            ))

        return chapters

    def _guess_title(self, text: str, file_path: str) -> str:
        """从文本或文件名猜测书名"""
        # 尝试从前几行提取
        lines = text.split('\n')
        for line in lines[:30]:
            line = line.strip()
            if 10 < len(line) < 100 and not line.startswith('---'):
                return line

        # 用文件名
        return Path(file_path).stem
