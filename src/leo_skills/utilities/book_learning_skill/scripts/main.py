#!/usr/bin/env python3
"""
书籍学习助手 - 主编排器

串联搜索 → 提取 → 分析 → 导出的完整流程。
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from .searcher.book_searcher import BookSearcher
from .extractor.book_extractor import BookExtractor
from .analyzer.knowledge_analyzer import KnowledgeAnalyzer
from .exporter.obsidian_exporter import ObsidianExporter

logger = logging.getLogger(__name__)


class BookLearning:
    """书籍学习助手 - 从搜索到 Obsidian 笔记的完整流程"""

    def __init__(
        self,
        vault_path: str = None,
        download_dir: str = None,
        llm_provider: str = "anthropic",
    ):
        """
        初始化书籍学习助手。

        Args:
            vault_path: Obsidian Vault 路径（留空则从 config.yaml 读取）
            download_dir: 书籍下载目录
            llm_provider: AI 提供商 ("anthropic", "openai", "local")
        """
        # 从 config.yaml 读取默认配置
        config = self._load_config()
        vault_path = vault_path or config.get("vault_path", "")
        download_dir = download_dir or config.get("download_dir", "")
        llm_provider = llm_provider or config.get("llm_provider", "anthropic")
        output_folder = config.get("obsidian_output_folder", "30-Resources/Books")

        self.searcher = BookSearcher(download_dir=download_dir or None)
        self.extractor = BookExtractor()
        self.analyzer = KnowledgeAnalyzer(llm_provider=llm_provider)
        self.exporter = ObsidianExporter(
            vault_path=vault_path or None,
            output_folder=output_folder,
        )

    @staticmethod
    def _load_config() -> dict:
        """从 config.yaml 读取配置"""
        import yaml
        config_path = Path(__file__).parent.parent / "config" / "config.yaml"
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        return {}

    def search_books(self, query: str, **kwargs) -> str:
        """搜索书籍，返回格式化列表"""
        return self.searcher.search_and_list(query, **kwargs)

    def process_local_pdf(
        self,
        pdf_path: str,
        output_dir: str = None,
        max_chapters: int = None,
    ) -> Dict[str, Any]:
        """
        处理本地 PDF/EPUB 文件，生成 Obsidian 笔记。

        Args:
            pdf_path: PDF/EPUB 文件路径
            output_dir: 输出目录（默认用 Obsidian Vault）
            max_chapters: 最大处理章节数（用于测试）

        Returns:
            处理结果字典
        """
        logger.info(f"开始处理: {pdf_path}")

        # 1. 提取书籍内容
        logger.info("步骤 1/3: 提取书籍内容...")
        book_content = self.extractor.extract(pdf_path)
        logger.info(
            f"提取完成: 《{book_content.title}》"
            f" {len(book_content.chapters)} 章, "
            f"{book_content.total_words} 字"
        )

        # 限制章节数（用于测试）
        chapters = book_content.chapters
        if max_chapters:
            chapters = chapters[:max_chapters]

        # 2. AI 分析知识点
        logger.info("步骤 2/3: AI 分析知识点...")
        analysis = self.analyzer.analyze_book(
            book_title=book_content.title,
            author=book_content.author,
            chapters=chapters,
        )
        logger.info(
            f"分析完成: {analysis.total_knowledge_points} 个知识点"
        )

        # 3. 导出到 Obsidian
        logger.info("步骤 3/3: 导出 Obsidian 笔记...")
        result = self.exporter.export(analysis, output_dir=output_dir)
        logger.info(f"导出完成: {len(result['files'])} 个文件")

        return {
            "success": True,
            "book_title": book_content.title,
            "author": book_content.author,
            "chapters_processed": len(chapters),
            "knowledge_points": analysis.total_knowledge_points,
            "files_created": result["files"],
            "output_dir": result["output_dir"],
        }

    def search_and_process(
        self,
        query: str,
        book_index: int = 0,
        output_dir: str = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        搜索书籍 → 下载 → 分析 → 导出的完整流程。

        Args:
            query: 搜索关键词
            book_index: 选择第几本书（0-based）
            output_dir: 输出目录

        Returns:
            处理结果字典
        """
        # 1. 搜索
        books = self.searcher.search(query, **kwargs)
        if not books:
            return {"success": False, "error": f"未找到与 '{query}' 相关的书籍"}

        if book_index >= len(books):
            return {"success": False, "error": f"索引超出范围，共找到 {len(books)} 本"}

        book = books[book_index]
        logger.info(f"选择: {book.title} by {book.author}")

        # 2. 下载
        filepath = self.searcher.download(book)
        if not filepath:
            return {"success": False, "error": "下载失败"}

        # 3. 处理
        return self.process_local_pdf(str(filepath), output_dir=output_dir)


def main():
    """CLI 入口"""
    parser = argparse.ArgumentParser(description="书籍学习助手 - PDF → 知识点 → Obsidian")
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # search 子命令
    search_parser = subparsers.add_parser("search", help="搜索书籍")
    search_parser.add_argument("query", help="搜索关键词")
    search_parser.add_argument("--type", default="title", choices=["title", "author"])
    search_parser.add_argument("--max", type=int, default=10, help="最大结果数")

    # process 子命令
    process_parser = subparsers.add_parser("process", help="处理本地 PDF/EPUB")
    process_parser.add_argument("file", help="PDF/EPUB 文件路径")
    process_parser.add_argument("-o", "--output", help="输出目录")
    process_parser.add_argument("--vault", help="Obsidian Vault 路径")
    process_parser.add_argument("--llm", default="anthropic", choices=["anthropic", "openai", "local"])
    process_parser.add_argument("--max-chapters", type=int, help="最大处理章节数")

    # full 子命令（搜索+下载+处理）
    full_parser = subparsers.add_parser("full", help="搜索 → 下载 → 分析 → 导出")
    full_parser.add_argument("query", help="搜索关键词")
    full_parser.add_argument("-i", "--index", type=int, default=0, help="选择第几本书")
    full_parser.add_argument("-o", "--output", help="输出目录")
    full_parser.add_argument("--vault", help="Obsidian Vault 路径")
    full_parser.add_argument("--llm", default="anthropic", choices=["anthropic", "openai", "local"])

    args = parser.parse_args()

    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    if args.command == "search":
        bl = BookLearning()
        print(bl.search_books(args.query, search_type=args.type, max_results=args.max))

    elif args.command == "process":
        bl = BookLearning(vault_path=args.vault, llm_provider=args.llm)
        result = bl.process_local_pdf(args.file, output_dir=args.output, max_chapters=args.max_chapters)
        if result["success"]:
            print(f"\n处理完成!")
            print(f"  书名: 《{result['book_title']}》")
            print(f"  章节: {result['chapters_processed']} 章")
            print(f"  知识点: {result['knowledge_points']} 个")
            print(f"  输出目录: {result['output_dir']}")
        else:
            print(f"处理失败: {result.get('error', '未知错误')}")
            return 1

    elif args.command == "full":
        bl = BookLearning(vault_path=args.vault, llm_provider=args.llm)
        result = bl.search_and_process(args.query, book_index=args.index, output_dir=args.output)
        if result["success"]:
            print(f"\n完成! 《{result['book_title']}》→ {result['output_dir']}")
        else:
            print(f"失败: {result.get('error')}")
            return 1

    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())
