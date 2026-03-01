#!/usr/bin/env python3
"""
Obsidian 导出模块 - 将书籍分析结果输出为 Obsidian 笔记

生成结构化的 Obsidian 笔记，包含：
- 书籍 MOC（Map of Content）主页
- 分章节知识点笔记
- 学习大纲笔记
- 自动添加 frontmatter、标签、双向链接
"""

import logging
import re
from datetime import datetime
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)


class ObsidianExporter:
    """Obsidian 笔记导出器"""

    def __init__(self, vault_path: str = None, output_folder: str = "30-Resources/Books"):
        """
        初始化导出器。

        Args:
            vault_path: Obsidian Vault 路径
            output_folder: 书籍笔记存放的子目录
        """
        self.vault_path = Path(vault_path) if vault_path else None
        self.output_folder = output_folder

    def export(self, analysis, output_dir: str = None) -> dict:
        """
        将书籍分析结果导出为 Obsidian 笔记。

        Args:
            analysis: BookAnalysis 对象
            output_dir: 输出目录（覆盖 vault_path）

        Returns:
            {"success": True, "files": [...], "output_dir": "..."}
        """
        # 确定输出目录
        if output_dir:
            base_dir = Path(output_dir)
        elif self.vault_path:
            base_dir = self.vault_path / self.output_folder
        else:
            base_dir = Path.cwd() / "output" / "book_notes"

        # 使用中文翻译书名作为目录名（如果有）
        display_title = self._get_display_title(analysis)
        safe_title = self._safe_filename(display_title)
        book_dir = base_dir / safe_title
        book_dir.mkdir(parents=True, exist_ok=True)

        created_files = []

        # 1. 生成书籍 MOC 主页
        moc_path = self._create_moc(analysis, book_dir)
        created_files.append(str(moc_path))

        # 2. 生成学习大纲笔记
        outline_path = self._create_outline(analysis, book_dir)
        created_files.append(str(outline_path))

        # 3. 生成各章节知识点笔记
        for i, chapter in enumerate(analysis.chapters, 1):
            ch_path = self._create_chapter_note(
                analysis, chapter, i, len(analysis.chapters), book_dir
            )
            created_files.append(str(ch_path))

        logger.info(f"导出完成: {len(created_files)} 个文件 -> {book_dir}")

        return {
            "success": True,
            "files": created_files,
            "output_dir": str(book_dir),
        }

    @staticmethod
    def _get_display_title(analysis) -> str:
        """获取显示用的书名（中文翻译优先）"""
        book_title_cn = getattr(analysis, "book_title_cn", None)
        if book_title_cn and book_title_cn != analysis.book_title:
            # 英文书有中文翻译：格式为 "中文名 (英文名)"
            return f"{book_title_cn} ({analysis.book_title})"
        return analysis.book_title

    @staticmethod
    def _get_chapter_display_title(chapter) -> str:
        """获取章节显示标题（中文翻译优先）"""
        ch_cn = getattr(chapter, "chapter_title_cn", None)
        if ch_cn and ch_cn != chapter.chapter_title:
            return f"{ch_cn} ({chapter.chapter_title})"
        return chapter.chapter_title

    def _create_moc(self, analysis, book_dir: Path) -> Path:
        """创建书籍 MOC（Map of Content）主页"""
        display_title = self._get_display_title(analysis)
        safe_title = self._safe_filename(display_title)
        now = datetime.now().strftime("%Y-%m-%d")

        # 章节链接列表
        chapter_links = []
        for i, ch in enumerate(analysis.chapters, 1):
            ch_filename = self._safe_filename(f"{safe_title}-第{i}章")
            kp_count = len(ch.knowledge_points)
            difficulty = ch.difficulty_level
            ch_display = self._get_chapter_display_title(ch)
            chapter_links.append(
                f"- [[{ch_filename}|第{i}章 {ch_display}]] "
                f"({kp_count}个知识点, {difficulty})"
            )

        content = f"""---
title: "《{display_title}》学习笔记"
author: "{analysis.author}"
tags: [book, 学习笔记, {safe_title}]
created: {now}
status: in-progress
type: book-moc
total_knowledge_points: {analysis.total_knowledge_points}
---

# 《{display_title}》

作者: {analysis.author}
知识点总数: {analysis.total_knowledge_points}

## 全书概述

{analysis.overall_summary}

## 章节导航

{chr(10).join(chapter_links)}

## 学习大纲

[[{safe_title}-学习大纲|查看完整学习大纲 →]]

## 学习进度

- [ ] 开始阅读
- [ ] 完成第一遍通读
- [ ] 整理知识点
- [ ] 复习巩固
"""

        filepath = book_dir / f"{safe_title}.md"
        filepath.write_text(content, encoding="utf-8")
        logger.info(f"创建 MOC: {filepath}")
        return filepath

    def _create_outline(self, analysis, book_dir: Path) -> Path:
        """创建学习大纲笔记"""
        display_title = self._get_display_title(analysis)
        safe_title = self._safe_filename(display_title)
        now = datetime.now().strftime("%Y-%m-%d")

        content = f"""---
title: "《{display_title}》学习大纲"
tags: [book, 学习大纲, {safe_title}]
created: {now}
parent: "[[{safe_title}]]"
type: book-outline
---

# 《{display_title}》学习大纲

{analysis.learning_outline}

---
返回: [[{safe_title}|书籍主页]]
"""

        filepath = book_dir / f"{safe_title}-学习大纲.md"
        filepath.write_text(content, encoding="utf-8")
        logger.info(f"创建大纲: {filepath}")
        return filepath

    def _create_chapter_note(self, analysis, chapter_analysis,
                             chapter_num: int, total_chapters: int,
                             book_dir: Path) -> Path:
        """创建章节知识点笔记"""
        display_title = self._get_display_title(analysis)
        safe_title = self._safe_filename(display_title)
        safe_ch = self._safe_filename(f"{safe_title}-第{chapter_num}章")
        now = datetime.now().strftime("%Y-%m-%d")
        ch_display = self._get_chapter_display_title(chapter_analysis)

        # 知识点列表
        kp_lines = []
        for kp in chapter_analysis.knowledge_points:
            importance_stars = "⭐" * kp.importance
            difficult_mark = " ⚠️难点" if kp.is_difficult else ""
            related = f" (相关: {', '.join(kp.related_concepts)})" if kp.related_concepts else ""
            kp_lines.append(
                f"### {kp.title} {importance_stars}{difficult_mark}\n\n"
                f"{kp.description}{related}\n"
            )

        # 复习问题
        questions = ""
        if chapter_analysis.review_questions:
            q_lines = [f"{i}. {q}" for i, q in enumerate(chapter_analysis.review_questions, 1)]
            questions = "## 复习问题\n\n" + "\n".join(q_lines)

        # 导航链接
        nav_links = [f"返回: [[{safe_title}|书籍主页]]"]
        if chapter_num > 1:
            prev_ch = self._safe_filename(f"{safe_title}-第{chapter_num - 1}章")
            nav_links.append(f"上一章: [[{prev_ch}]]")
        if chapter_num < total_chapters:
            next_ch = self._safe_filename(f"{safe_title}-第{chapter_num + 1}章")
            nav_links.append(f"下一章: [[{next_ch}]]")

        # 核心概念标签
        concept_tags = ", ".join(chapter_analysis.key_concepts[:5]) if chapter_analysis.key_concepts else ""

        content = f"""---
title: "第{chapter_num}章 {ch_display}"
tags: [book, {safe_title}, 第{chapter_num}章]
created: {now}
parent: "[[{safe_title}]]"
difficulty: {chapter_analysis.difficulty_level}
type: book-chapter
---

# 第{chapter_num}章 {ch_display}

难度: {chapter_analysis.difficulty_level} | 知识点: {len(chapter_analysis.knowledge_points)}个
核心概念: {concept_tags}

## 章节摘要

{chapter_analysis.summary}

## 核心知识点

{chr(10).join(kp_lines)}

{questions}

---
{' | '.join(nav_links)}
"""

        filepath = book_dir / f"{safe_ch}.md"
        filepath.write_text(content, encoding="utf-8")
        logger.info(f"创建章节笔记: {filepath}")
        return filepath

    def _safe_filename(self, name: str) -> str:
        """生成安全的文件名"""
        # 移除换行符和非法字符
        safe = name.replace('\n', ' ').replace('\r', '')
        safe = re.sub(r'[<>:"/\\|?*]', '', safe)
        # 压缩连续空格
        safe = re.sub(r'\s+', ' ', safe)
        # 限制长度
        return safe[:80].strip()
