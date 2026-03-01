#!/usr/bin/env python3
"""
知识点分析模块 - 使用 AI 从章节文本中提取知识点

逐章分析书籍内容，提取核心知识点、重点难点，
生成学习大纲和复习问题。
"""

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class KnowledgePoint:
    """单个知识点"""
    title: str
    description: str
    importance: int = 3  # 1-5，5 最重要
    is_difficult: bool = False
    related_concepts: List[str] = field(default_factory=list)


@dataclass
class ChapterAnalysis:
    """章节分析结果"""
    chapter_title: str
    chapter_title_cn: str  # 章节标题中文翻译
    summary: str
    knowledge_points: List[KnowledgePoint]
    key_concepts: List[str]
    review_questions: List[str]
    difficulty_level: str = "中等"  # 简单/中等/困难


@dataclass
class BookAnalysis:
    """全书分析结果"""
    book_title: str
    book_title_cn: str  # 书名中文翻译
    author: str
    overall_summary: str
    learning_outline: str  # Markdown 格式大纲
    chapters: List[ChapterAnalysis]
    total_knowledge_points: int = 0
    recommended_reading_order: List[str] = field(default_factory=list)


# 章节分析提示词模板
CHAPTER_ANALYSIS_PROMPT = """你是一位专业的学习助手。请分析以下书籍章节内容，提取核心知识点。

书名：{book_title}
章节：{chapter_title}

内容：
{content}

请按以下 JSON 格式输出分析结果（直接输出 JSON，不要包裹在代码块中）：
{{
    "chapter_title_cn": "章节标题的简体中文翻译（如果原标题已是中文则原样返回）",
    "summary": "本章摘要（2-3句话，用简体中文）",
    "knowledge_points": [
        {{
            "title": "知识点标题（用简体中文）",
            "description": "知识点详细说明（1-2句话，用简体中文）",
            "importance": 3,
            "is_difficult": false,
            "related_concepts": ["相关概念1", "相关概念2"]
        }}
    ],
    "key_concepts": ["核心概念1", "核心概念2"],
    "review_questions": ["复习问题1？", "复习问题2？"],
    "difficulty_level": "中等"
}}

要求：
1. 知识点数量 3-8 个，抓重点不要面面俱到
2. importance 用 1-5 评分，5 最重要
3. 复习问题 2-4 个，帮助检验理解
4. difficulty_level 只能是：简单/中等/困难
5. 【强制】所有输出必须使用简体中文，包括 chapter_title_cn、summary、知识点标题和描述
6. 【强制】chapter_title_cn 必须是章节标题的准确中文翻译
"""

OUTLINE_PROMPT = """你是一位专业的学习规划师。根据以下书籍各章节的分析结果，生成一份完整的学习大纲。

书名：{book_title}
作者：{author}

各章节分析：
{chapters_summary}

请生成 Markdown 格式的学习大纲，包含：
1. 全书概述（3-5句话）
2. 各章节的核心知识点层级结构
3. 重点和难点标注（用 ⭐ 标注重点，用 ⚠️ 标注难点）
4. 建议的学习顺序

直接输出 Markdown 内容，不要包裹在代码块中。
"""


class KnowledgeAnalyzer:
    """知识点分析器 - 使用 AI 提取书籍知识点"""

    def __init__(self, llm_provider: str = "anthropic", max_chunk_size: int = 4000):
        """
        初始化知识点分析器。

        Args:
            llm_provider: LLM 提供商 ("anthropic", "openai", "local")
            max_chunk_size: 每次发送给 AI 的最大字符数
        """
        self.llm_provider = llm_provider
        self.max_chunk_size = max_chunk_size
        self._client = None
        self._title_translations = self._load_title_translations()

    @staticmethod
    def _load_title_translations() -> dict:
        """从 config.yaml 加载书名翻译映射"""
        import yaml
        config_path = Path(__file__).parent.parent.parent / "config" / "config.yaml"
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f) or {}
            return config.get("title_translations", {})
        return {}

    def _translate_title(self, title: str) -> str:
        """翻译书名：优先查映射表，否则返回原标题"""
        # 精确匹配
        if title in self._title_translations:
            return self._title_translations[title]
        # 模糊匹配（忽略大小写和多余空格）
        normalized = " ".join(title.lower().split())
        for en, cn in self._title_translations.items():
            if " ".join(en.lower().split()) == normalized:
                return cn
        return title

    @staticmethod
    def _is_english(text: str) -> bool:
        """判断文本是否主要是英文"""
        ascii_count = sum(1 for c in text if c.isascii() and c.isalpha())
        total_alpha = sum(1 for c in text if c.isalpha())
        if total_alpha == 0:
            return False
        return ascii_count / total_alpha > 0.7

    def analyze_chapter(self, book_title: str, chapter_title: str, content: str) -> ChapterAnalysis:
        """
        分析单个章节，提取知识点。

        Args:
            book_title: 书名
            chapter_title: 章节标题
            content: 章节文本内容

        Returns:
            ChapterAnalysis 对象
        """
        logger.info(f"分析章节: {chapter_title}")

        # 如果内容太长，截取核心部分
        if len(content) > self.max_chunk_size:
            content = self._smart_truncate(content, self.max_chunk_size)

        prompt = CHAPTER_ANALYSIS_PROMPT.format(
            book_title=book_title,
            chapter_title=chapter_title,
            content=content,
        )

        # 调用 AI 分析
        response = self._call_llm(prompt)

        # 解析 JSON 响应
        try:
            data = self._parse_json_response(response)
        except Exception as e:
            logger.warning(f"解析 AI 响应失败: {e}，使用基础分析")
            return self._basic_analysis(chapter_title, content)

        # 构建 ChapterAnalysis
        knowledge_points = []
        for kp in data.get("knowledge_points", []):
            knowledge_points.append(KnowledgePoint(
                title=kp.get("title", ""),
                description=kp.get("description", ""),
                importance=kp.get("importance", 3),
                is_difficult=kp.get("is_difficult", False),
                related_concepts=kp.get("related_concepts", []),
            ))

        return ChapterAnalysis(
            chapter_title=chapter_title,
            chapter_title_cn=data.get("chapter_title_cn", chapter_title),
            summary=data.get("summary", ""),
            knowledge_points=knowledge_points,
            key_concepts=data.get("key_concepts", []),
            review_questions=data.get("review_questions", []),
            difficulty_level=data.get("difficulty_level", "中等"),
        )

    def analyze_book(self, book_title: str, author: str,
                     chapters: list) -> BookAnalysis:
        """
        分析整本书，生成完整的知识点和学习大纲。

        Args:
            book_title: 书名
            author: 作者
            chapters: Chapter 对象列表（来自 BookExtractor）

        Returns:
            BookAnalysis 对象
        """
        logger.info(f"开始分析书籍: 《{book_title}》 共 {len(chapters)} 章")

        # 自动翻译书名
        book_title_cn = self._translate_title(book_title)
        if book_title_cn == book_title and self._is_english(book_title):
            # 映射表没有，用 AI 翻译
            prompt = f"请将以下英文书名翻译为简体中文（只输出翻译结果，不要其他内容）：\n{book_title}"
            ai_cn = self._call_llm(prompt).strip().strip('"').strip("'").strip("《》")
            if ai_cn:
                book_title_cn = ai_cn
                logger.info(f"AI 翻译书名: {book_title} → {book_title_cn}")

        # 逐章分析
        chapter_analyses = []
        for i, chapter in enumerate(chapters):
            logger.info(f"分析进度: {i + 1}/{len(chapters)} - {chapter.title}")
            analysis = self.analyze_chapter(book_title, chapter.title, chapter.content)
            chapter_analyses.append(analysis)

        # 生成全书大纲
        outline = self._generate_outline(book_title, author, chapter_analyses)

        # 生成全书摘要
        overall_summary = self._generate_overall_summary(book_title, chapter_analyses)

        total_kp = sum(len(ca.knowledge_points) for ca in chapter_analyses)

        return BookAnalysis(
            book_title=book_title,
            book_title_cn=book_title_cn,
            author=author,
            overall_summary=overall_summary,
            learning_outline=outline,
            chapters=chapter_analyses,
            total_knowledge_points=total_kp,
        )

    def _generate_outline(self, book_title: str, author: str,
                          chapters: List[ChapterAnalysis]) -> str:
        """生成学习大纲"""
        # 构建章节摘要
        summaries = []
        for ch in chapters:
            kp_list = "\n".join(f"  - {kp.title}" for kp in ch.knowledge_points)
            summaries.append(f"### {ch.chapter_title}\n摘要: {ch.summary}\n知识点:\n{kp_list}")

        chapters_summary = "\n\n".join(summaries)

        prompt = OUTLINE_PROMPT.format(
            book_title=book_title,
            author=author,
            chapters_summary=chapters_summary,
        )

        return self._call_llm(prompt)

    def _generate_overall_summary(self, book_title: str,
                                  chapters: List[ChapterAnalysis]) -> str:
        """从各章摘要生成全书概述"""
        ch_summaries = [f"- {ch.chapter_title}: {ch.summary}" for ch in chapters]
        return f"《{book_title}》共 {len(chapters)} 章。\n" + "\n".join(ch_summaries)

    def _call_llm(self, prompt: str) -> str:
        """
        调用 LLM API。

        支持 Anthropic Claude 和 OpenAI，
        也支持本地模型（通过 OpenAI 兼容 API）。
        """
        if self.llm_provider == "anthropic":
            return self._call_anthropic(prompt)
        elif self.llm_provider == "openai":
            return self._call_openai(prompt)
        elif self.llm_provider == "local":
            return self._call_local(prompt)
        else:
            # 降级：返回基础提取结果
            logger.warning(f"未知 LLM 提供商: {self.llm_provider}，使用基础提取")
            return ""

    def _call_anthropic(self, prompt: str) -> str:
        """调用 Anthropic Claude API"""
        try:
            import anthropic
            if not self._client:
                self._client = anthropic.Anthropic()

            message = self._client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}],
            )
            return message.content[0].text
        except ImportError:
            logger.error("anthropic 库未安装: pip install anthropic")
            return ""
        except Exception as e:
            logger.error(f"Anthropic API 调用失败: {e}")
            return ""

    def _call_openai(self, prompt: str) -> str:
        """调用 OpenAI API"""
        try:
            import openai
            if not self._client:
                self._client = openai.OpenAI()

            response = self._client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=4096,
            )
            return response.choices[0].message.content
        except ImportError:
            logger.error("openai 库未安装: pip install openai")
            return ""
        except Exception as e:
            logger.error(f"OpenAI API 调用失败: {e}")
            return ""

    def _call_local(self, prompt: str) -> str:
        """调用本地 OpenAI 兼容 API（如 Ollama、LM Studio）"""
        try:
            import openai
            if not self._client:
                self._client = openai.OpenAI(
                    base_url="http://localhost:11434/v1",
                    api_key="ollama",
                )

            response = self._client.chat.completions.create(
                model="qwen2.5:14b",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=4096,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"本地 LLM 调用失败: {e}")
            return ""

    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """从 AI 响应中解析 JSON"""
        if not response:
            return {}

        # 尝试直接解析
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass

        # 尝试从代码块中提取
        import re
        json_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        # 尝试找到第一个 { 和最后一个 }
        start = response.find('{')
        end = response.rfind('}')
        if start != -1 and end != -1:
            try:
                return json.loads(response[start:end + 1])
            except json.JSONDecodeError:
                pass

        raise ValueError(f"无法从响应中解析 JSON")

    def _smart_truncate(self, text: str, max_length: int) -> str:
        """智能截断文本，保留开头和结尾"""
        if len(text) <= max_length:
            return text

        # 保留前 70% 和后 20%，中间用省略号
        head_len = int(max_length * 0.7)
        tail_len = int(max_length * 0.2)
        return text[:head_len] + "\n\n...(中间内容省略)...\n\n" + text[-tail_len:]

    def _basic_analysis(self, chapter_title: str, content: str) -> ChapterAnalysis:
        """基础分析（不依赖 AI）- 作为降级方案"""
        # 简单提取：按段落分割，取前几段作为摘要
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip() and len(p.strip()) > 20]
        summary = paragraphs[0][:200] if paragraphs else "无摘要"

        return ChapterAnalysis(
            chapter_title=chapter_title,
            chapter_title_cn=chapter_title,
            summary=summary,
            knowledge_points=[],
            key_concepts=[],
            review_questions=[],
            difficulty_level="中等",
        )
