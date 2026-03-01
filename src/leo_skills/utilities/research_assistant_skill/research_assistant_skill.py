"""
research_assistant_skill - 研究助手技能

辅助学术/商业调研，支持文献搜索、论文分析、摘要生成和引用管理。
"""

import json
import re
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from leo_skills.core.base_executor import BaseExecutor


@dataclass
class Paper:
    """论文/研究文献数据"""
    paper_id: str
    title: str
    authors: List[str]
    year: int
    venue: str = ""
    abstract: str = ""
    citation_count: int = 0
    url: str = ""
    doi: str = ""
    topics: List[str] = field(default_factory=list)
    methodology: str = ""
    key_findings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_citation(self, style: str = "apa") -> str:
        """生成引用格式"""
        authors_str = ", ".join(self.authors[:3])
        if len(self.authors) > 3:
            authors_str += " et al."

        if style == "apa":
            return f"{authors_str} ({self.year}). {self.title}. {self.venue}."
        elif style == "mla":
            return f'{authors_str}. "{self.title}." {self.venue}, {self.year}.'
        elif style == "chicago":
            return f'{authors_str}. "{self.title}." {self.venue} ({self.year}).'
        elif style == "bibtex":
            key = re.sub(r'\W+', '', self.authors[0].split()[-1] if self.authors else "unknown")
            return (
                f"@article{{{key}{self.year},\n"
                f"  title = {{{self.title}}},\n"
                f"  author = {{{' and '.join(self.authors)}}},\n"
                f"  year = {{{self.year}}},\n"
                f"  journal = {{{self.venue}}}\n"
                f"}}"
            )
        return f"{authors_str} ({self.year}). {self.title}."


@dataclass
class ResearchProject:
    """研究项目"""
    name: str
    topic: str
    papers: List[Paper] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "topic": self.topic,
            "papers": [p.to_dict() for p in self.papers],
            "notes": self.notes,
            "created_at": self.created_at,
            "paper_count": len(self.papers),
        }


class ResearchAssistant(BaseExecutor):
    """
    研究助手技能

    支持操作：
    - search: 搜索文献并给出搜索建议
    - analyze: 分析论文或文本的关键信息
    - summarize: 生成研究摘要
    - cite: 生成 APA/MLA/Chicago/BibTeX 引用格式
    - review: 生成文献综述框架
    - project: 管理研究项目（创建/列表/添加笔记/导出）
    - extract_topics: 从文本中提取主题分类
    """

    # 常见学术/技术关键词分类
    TOPIC_KEYWORDS = {
        "ai": ["机器学习", "深度学习", "神经网络", "transformer", "llm", "大模型",
               "自然语言处理", "计算机视觉", "强化学习", "生成式ai"],
        "web": ["react", "vue", "angular", "typescript", "node.js", "前端",
                "后端", "全栈", "微服务", "api"],
        "data": ["数据分析", "数据挖掘", "大数据", "数据库", "sql", "nosql",
                 "数据可视化", "etl", "数据仓库"],
        "cloud": ["云计算", "docker", "kubernetes", "serverless", "aws",
                  "azure", "devops", "ci/cd"],
        "security": ["网络安全", "加密", "认证", "授权", "零信任", "渗透测试"],
        "business": ["商业分析", "市场调研", "竞品分析", "用户研究", "增长策略"],
    }

    def __init__(self, output_dir: str = "output/research") -> None:
        self.name = "research_assistant_skill"
        self.output_dir = Path(output_dir)
        self.projects: Dict[str, ResearchProject] = {}

    def execute(
        self,
        action: str = "search",
        context: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """统一执行入口"""
        params = dict(context or {})
        params.update(kwargs)

        actions = {
            "search": self._search,
            "analyze": self._analyze,
            "summarize": self._summarize,
            "cite": self._cite,
            "review": self._generate_review,
            "project": self._manage_project,
            "extract_topics": self._extract_topics,
        }

        handler = actions.get(action)
        if not handler:
            return {"status": "error", "message": f"不支持的操作: {action}，可用: {list(actions.keys())}"}

        return handler(**params)

    def _search(self, query: str = "", topic: str = "", **_) -> Dict[str, Any]:
        """搜索文献并给出搜索建议"""
        if not query and not topic:
            return {"status": "error", "message": "请提供 query（搜索词）或 topic（主题）"}

        search_term = (query or topic).lower()

        # 识别主题分类
        matched_topics = []
        for cat, keywords in self.TOPIC_KEYWORDS.items():
            if any(kw in search_term for kw in keywords):
                matched_topics.append(cat)

        # 生成搜索引擎建议
        encoded_query = query or topic
        suggestions = {
            "search_engines": [
                {"name": "Google Scholar", "url": f"https://scholar.google.com/scholar?q={encoded_query}"},
                {"name": "Semantic Scholar", "url": f"https://www.semanticscholar.org/search?q={encoded_query}"},
                {"name": "arXiv", "url": f"https://arxiv.org/search/?query={encoded_query}"},
                {"name": "CNKI (知网)", "url": f"https://scholar.cnki.net/search?q={encoded_query}"},
            ],
            "related_topics": matched_topics,
            "search_tips": [
                f'使用引号精确搜索: "{encoded_query}"',
                "添加 filetype:pdf 限制为 PDF 文献",
                "使用 site:arxiv.org 限定 arXiv 来源",
                "加年份范围缩小范围: 2024..2026",
            ],
        }

        return {
            "status": "success",
            "action": "search",
            "query": encoded_query,
            "matched_topics": matched_topics,
            "suggestions": suggestions,
            "tip": "建议使用上述搜索引擎获取真实文献，然后用 analyze 操作分析",
        }

    def _analyze(self, paper: Optional[Dict] = None, text: str = "", **_) -> Dict[str, Any]:
        """分析论文或文本的关键信息"""
        if paper:
            p = Paper(**paper) if isinstance(paper, dict) else paper
            return {
                "status": "success",
                "analysis": {
                    "title": p.title,
                    "authors": p.authors,
                    "year": p.year,
                    "topics": p.topics or self._extract_topics_from_text(p.abstract or p.title),
                    "citation": p.to_citation("apa"),
                    "summary": f"该论文由 {', '.join(p.authors[:2])} 等人于 {p.year} 年发表在 {p.venue}。",
                },
            }

        if text:
            topics = self._extract_topics_from_text(text)
            word_count = len(text)
            sentences = [s.strip() for s in re.split(r'[.。!！?？]', text) if s.strip()]

            return {
                "status": "success",
                "analysis": {
                    "word_count": word_count,
                    "sentence_count": len(sentences),
                    "detected_topics": topics,
                    "key_sentences": sentences[:5],
                    "reading_time_minutes": max(1, word_count // 300),
                },
            }

        return {"status": "error", "message": "请提供 paper（论文数据）或 text（文本内容）"}

    def _summarize(self, papers: Optional[List[Dict]] = None, text: str = "",
                   style: str = "brief", **_) -> Dict[str, Any]:
        """生成研究摘要"""
        if papers:
            paper_objs = [Paper(**p) if isinstance(p, dict) else p for p in papers]
            paper_objs.sort(key=lambda x: x.year, reverse=True)

            lines = [f"# 文献综述摘要\n", f"> 共 {len(paper_objs)} 篇文献\n"]
            for i, p in enumerate(paper_objs, 1):
                lines.append(f"## {i}. {p.title}")
                lines.append(f"- **作者**: {', '.join(p.authors[:3])}")
                lines.append(f"- **年份**: {p.year}")
                lines.append(f"- **来源**: {p.venue}")
                if p.abstract:
                    abstract = p.abstract[:200] + "..." if len(p.abstract) > 200 else p.abstract
                    lines.append(f"- **摘要**: {abstract}")
                if p.key_findings:
                    lines.append("- **关键发现**:")
                    for finding in p.key_findings:
                        lines.append(f"  - {finding}")
                lines.append("")

            return {"status": "success", "summary": "\n".join(lines), "paper_count": len(paper_objs)}

        if text:
            sentences = [s.strip() for s in re.split(r'[.。]', text) if len(s.strip()) > 10]
            key_sentences = sentences[:5] if style == "brief" else sentences[:10]
            return {
                "status": "success",
                "summary": "。".join(key_sentences) + "。",
                "original_length": len(text),
                "summary_length": sum(len(s) for s in key_sentences),
            }

        return {"status": "error", "message": "请提供 papers（论文列表）或 text（文本）"}

    def _cite(self, papers: Optional[List[Dict]] = None, style: str = "apa", **_) -> Dict[str, Any]:
        """生成引用列表"""
        if not papers:
            return {"status": "error", "message": "请提供 papers（论文列表）"}

        paper_objs = [Paper(**p) if isinstance(p, dict) else p for p in papers]
        citations = [p.to_citation(style) for p in paper_objs]

        return {
            "status": "success",
            "style": style,
            "citations": citations,
            "formatted": "\n\n".join(f"[{i+1}] {c}" for i, c in enumerate(citations)),
        }

    def _generate_review(self, topic: str = "", papers: Optional[List[Dict]] = None, **_) -> Dict[str, Any]:
        """生成文献综述框架"""
        if not topic:
            return {"status": "error", "message": "请提供 topic（研究主题）"}

        review = f"""# {topic} - 文献综述

## 1. 引言
本文对 {topic} 领域的研究进展进行了系统性综述。

## 2. 研究背景
### 2.1 发展历程
### 2.2 核心概念

## 3. 研究现状
### 3.1 主要研究方向
### 3.2 关键方法与技术
### 3.3 代表性成果

## 4. 分析与讨论
### 4.1 研究趋势
### 4.2 存在问题
### 4.3 未来方向

## 5. 结论

## 参考文献
"""
        result = {"status": "success", "review_template": review, "topic": topic}
        if papers:
            paper_objs = [Paper(**p) if isinstance(p, dict) else p for p in papers]
            result["paper_count"] = len(paper_objs)
            result["citations"] = [p.to_citation("apa") for p in paper_objs]
        return result

    def _manage_project(self, operation: str = "create", project_name: str = "",
                        topic: str = "", note: str = "", **_) -> Dict[str, Any]:
        """管理研究项目"""
        if operation == "create":
            if not project_name:
                return {"status": "error", "message": "请提供 project_name"}
            project = ResearchProject(name=project_name, topic=topic or project_name)
            self.projects[project_name] = project
            return {"status": "success", "message": f"项目 '{project_name}' 已创建", "project": project.to_dict()}

        elif operation == "list":
            return {"status": "success", "projects": {k: v.to_dict() for k, v in self.projects.items()}}

        elif operation == "add_note":
            if project_name not in self.projects:
                return {"status": "error", "message": f"项目 '{project_name}' 不存在"}
            self.projects[project_name].notes.append(note or "(空笔记)")
            return {"status": "success", "message": "笔记已添加"}

        elif operation == "export":
            if project_name not in self.projects:
                return {"status": "error", "message": f"项目 '{project_name}' 不存在"}
            project = self.projects[project_name]
            self.output_dir.mkdir(parents=True, exist_ok=True)
            output_file = self.output_dir / f"{project_name}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(project.to_dict(), f, ensure_ascii=False, indent=2)
            return {"status": "success", "message": f"已导出到 {output_file}"}

        return {"status": "error", "message": f"不支持的操作: {operation}，可用: create/list/add_note/export"}

    def _extract_topics(self, text: str = "", **_) -> Dict[str, Any]:
        """从文本中提取主题分类"""
        if not text:
            return {"status": "error", "message": "请提供 text（文本内容）"}
        return {"status": "success", "topics": self._extract_topics_from_text(text)}

    def _extract_topics_from_text(self, text: str) -> List[str]:
        """内部方法：从文本中提取主题关键词"""
        text_lower = text.lower()
        found = []
        for category, keywords in self.TOPIC_KEYWORDS.items():
            if any(kw in text_lower for kw in keywords):
                found.append(category)
        return found


__all__ = ["ResearchAssistant"]
