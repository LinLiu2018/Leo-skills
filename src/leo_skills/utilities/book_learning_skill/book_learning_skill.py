#!/usr/bin/env python3
"""
书籍学习技能 - EvolvableSkill 包装

将 BookLearning 编排器包装为 Leo 系统标准技能，
支持自我进化和执行追踪。
"""

import logging
from pathlib import Path
from typing import Any, Dict

from leo_skills.evolution import EvolvableSkill

logger = logging.getLogger(__name__)


class BookLearningSkill(EvolvableSkill):
    """书籍学习技能 - 从 PDF 提取知识点并输出到 Obsidian"""

    def __init__(self):
        config_path = str(Path(__file__).parent / "config" / "config.yaml")
        super().__init__(
            skill_name="book_learning_skill",
            config_path=config_path,
        )

        # 延迟初始化（避免导入时报错）
        self._book_learning = None

    def _get_book_learning(self):
        """延迟初始化 BookLearning 实例"""
        if self._book_learning is None:
            from .scripts.main import BookLearning

            import yaml
            config = {}
            config_path = Path(__file__).parent / "config" / "config.yaml"
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f) or {}

            self._book_learning = BookLearning(
                vault_path=config.get("vault_path"),
                download_dir=config.get("download_dir"),
                llm_provider=config.get("llm_provider", "anthropic"),
            )
        return self._book_learning

    def _execute_core(self, *args, **kwargs) -> Dict[str, Any]:
        """
        核心执行逻辑。

        支持的 action:
        - search: 搜索书籍
        - process: 处理本地 PDF
        - full: 搜索+下载+处理完整流程
        """
        action = kwargs.get("action", "process")
        bl = self._get_book_learning()

        if action == "search":
            query = kwargs.get("query", "")
            result_text = bl.search_books(query, **{
                k: v for k, v in kwargs.items()
                if k in ("search_type", "max_results", "filters")
            })
            return {"success": True, "output": result_text}

        elif action == "process":
            pdf_path = kwargs.get("pdf_path") or kwargs.get("file")
            if not pdf_path:
                return {"success": False, "error": "需要提供 pdf_path 参数"}
            return bl.process_local_pdf(
                pdf_path,
                output_dir=kwargs.get("output_dir"),
                max_chapters=kwargs.get("max_chapters"),
            )

        elif action == "full":
            query = kwargs.get("query", "")
            if not query:
                return {"success": False, "error": "需要提供 query 参数"}
            return bl.search_and_process(
                query,
                book_index=kwargs.get("book_index", 0),
                output_dir=kwargs.get("output_dir"),
            )

        else:
            return {"success": False, "error": f"未知 action: {action}"}
