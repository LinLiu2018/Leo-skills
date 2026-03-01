"""
文章转原型技能

从文章（PDF / Markdown / Jupyter Notebook / URL）中提取算法和技术方案，
自动分析内容域、复杂度，选择目标语言，生成可运行的代码原型。
"""

from __future__ import annotations

import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from leo_skills.core.base_executor import BaseExecutor

logger = logging.getLogger(__name__)


class ArticleToPrototype(BaseExecutor):
    """文章转原型技能。

    支持的操作：
        - process:  完整流程（提取 → 分析 → 选择语言 → 生成原型）
        - extract:  仅提取内容
        - analyze:  仅分析内容
    """

    SUPPORTED_EXTENSIONS = {".pdf", ".md", ".markdown", ".txt", ".ipynb"}

    DOMAIN_KEYWORDS = {
        "machine_learning": ["neural network", "deep learning", "gradient", "loss function",
                             "training", "epoch", "classifier", "regression",
                             "机器学习", "深度学习", "神经网络"],
        "data_science": ["dataset", "visualization", "pandas", "numpy", "statistics",
                         "数据分析", "可视化", "统计"],
        "web_development": ["api", "rest", "http", "frontend", "backend", "database",
                            "前端", "后端", "接口"],
        "algorithms": ["algorithm", "complexity", "sort", "search", "graph", "tree",
                       "dynamic programming", "算法", "排序"],
        "devops": ["docker", "kubernetes", "ci/cd", "deployment", "container",
                   "部署", "容器"],
    }

    LANGUAGE_HINTS = {
        "python": ["import ", "def ", "class ", "pip install", "python", ".py",
                   "pandas", "numpy", "flask", "django"],
        "javascript": ["const ", "let ", "var ", "function ", "npm ", "node",
                       "react", "vue", "express"],
        "typescript": ["interface ", "type ", ": string", ": number", "tsx"],
        "rust": ["fn ", "let mut", "impl ", "cargo", "struct "],
        "go": ["func ", "package ", "go mod", "goroutine"],
    }

    def __init__(self) -> None:
        self.name = "article_to_prototype_skill"

    # ------------------------------------------------------------------ #
    #  BaseExecutor 接口
    # ------------------------------------------------------------------ #

    def execute(
        self,
        action: str = "process",
        context: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = dict(context or {})
        params.update(kwargs)

        if action in ("process", "run"):
            return self._action_process(params)
        elif action == "extract":
            return self._action_extract(params)
        elif action == "analyze":
            return self._action_analyze(params)
        else:
            return {"status": "error", "message": f"未知操作: {action}"}

    # ------------------------------------------------------------------ #
    #  完整流程
    # ------------------------------------------------------------------ #

    def _action_process(self, params: Dict[str, Any]) -> Dict[str, Any]:
        source = params.get("source", "")
        output_dir = params.get("output_dir", "./output")
        language_hint = params.get("language")

        if not source:
            return {"status": "error", "message": "缺少 source 参数"}
        return self.process(source, output_dir, language_hint)

    def process(self, source: str, output_dir: str = "./output",
                language_hint: Optional[str] = None) -> Dict[str, Any]:
        """完整处理流程。"""
        try:
            content = self._extract_content(source)
            if not content.get("text"):
                return {"status": "error", "message": "未能提取到有效内容"}

            analysis = self._analyze_content(content["text"])
            code_fragments = self._detect_code_fragments(content["text"])
            analysis["code_fragments_count"] = len(code_fragments)

            language = language_hint or self._select_language(content["text"], analysis)
            result = self._generate_prototype(content, analysis, code_fragments, language, output_dir, source)

            return {
                "status": "success",
                "output_dir": output_dir,
                "language": language,
                "domain": analysis.get("domain", "unknown"),
                "complexity": analysis.get("complexity", "medium"),
                "algorithms_detected": len(analysis.get("algorithms", [])),
                "code_fragments": len(code_fragments),
                "files_created": result.get("files", []),
                "entry_point": result.get("entry_point", ""),
                "confidence": analysis.get("confidence", 0.5),
            }
        except Exception as e:
            logger.error(f"处理失败: {e}", exc_info=True)
            return {"status": "error", "error": str(e), "error_type": type(e).__name__}

    # ------------------------------------------------------------------ #
    #  提取内容
    # ------------------------------------------------------------------ #

    def _action_extract(self, params: Dict[str, Any]) -> Dict[str, Any]:
        source = params.get("source", "")
        if not source:
            return {"status": "error", "message": "缺少 source 参数"}
        return {"status": "success", "data": self._extract_content(source)}

    def _extract_content(self, source: str) -> Dict[str, Any]:
        if source.startswith(("http://", "https://")):
            return self._extract_url(source)
        path = Path(source)
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {source}")
        ext = path.suffix.lower()
        if ext == ".pdf":
            return self._extract_pdf(path)
        elif ext == ".ipynb":
            return self._extract_notebook(path)
        else:
            return self._extract_text(path)

    @staticmethod
    def _extract_text(path: Path) -> Dict[str, Any]:
        text = path.read_text(encoding="utf-8")
        title = path.stem
        for line in text.split("\n"):
            if line.startswith("# "):
                title = line[2:].strip()
                break
        return {"title": title, "text": text, "source_type": "markdown",
                "source_path": str(path), "extraction_date": datetime.now().isoformat()}

    @staticmethod
    def _extract_pdf(path: Path) -> Dict[str, Any]:
        text = ""
        try:
            import fitz
            doc = fitz.open(str(path))
            for page in doc:
                text += page.get_text()
            doc.close()
        except ImportError:
            try:
                import pdfplumber
                with pdfplumber.open(str(path)) as pdf:
                    for page in pdf.pages:
                        t = page.extract_text()
                        if t:
                            text += t + "\n"
            except ImportError:
                raise ImportError("需要 pymupdf 或 pdfplumber: pip install pymupdf")
        return {"title": path.stem, "text": text, "source_type": "pdf",
                "source_path": str(path), "extraction_date": datetime.now().isoformat()}

    @staticmethod
    def _extract_notebook(path: Path) -> Dict[str, Any]:
        import json
        nb = json.loads(path.read_text(encoding="utf-8"))
        parts: List[str] = []
        for cell in nb.get("cells", []):
            src = "".join(cell.get("source", []))
            if cell["cell_type"] == "markdown":
                parts.append(src)
            elif cell["cell_type"] == "code":
                parts.append(f"```python\n{src}\n```")
        return {"title": path.stem, "text": "\n\n".join(parts), "source_type": "notebook",
                "source_path": str(path), "extraction_date": datetime.now().isoformat()}

    @staticmethod
    def _extract_url(url: str) -> Dict[str, Any]:
        try:
            import requests
            from bs4 import BeautifulSoup
        except ImportError:
            raise ImportError("需要 requests 和 beautifulsoup4")
        resp = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        title = soup.title.string if soup.title else url
        return {"title": title, "text": soup.get_text(separator="\n", strip=True),
                "source_type": "web", "source_url": url,
                "extraction_date": datetime.now().isoformat()}

    # ------------------------------------------------------------------ #
    #  内容分析
    # ------------------------------------------------------------------ #

    def _action_analyze(self, params: Dict[str, Any]) -> Dict[str, Any]:
        text = params.get("text", "")
        if not text:
            return {"status": "error", "message": "缺少 text 参数"}
        return {"status": "success", "data": self._analyze_content(text)}

    def _analyze_content(self, text: str) -> Dict[str, Any]:
        text_lower = text.lower()
        domain_scores: Dict[str, int] = {}
        for domain, kws in self.DOMAIN_KEYWORDS.items():
            score = sum(1 for kw in kws if kw.lower() in text_lower)
            if score > 0:
                domain_scores[domain] = score
        domain = max(domain_scores, key=domain_scores.get) if domain_scores else "general"

        math_count = len(re.findall(r"equation|formula|theorem|\$.*\$", text_lower))
        code_blocks = text.count("```")
        refs = len(re.findall(r"\[\d+\]|\(\d{4}\)", text))
        sections = len(re.findall(r"^#{1,3}\s", text, re.MULTILINE))

        score = (min(math_count * 0.15, 0.3) + min(code_blocks * 0.1, 0.2) +
                 min(refs * 0.02, 0.2) + min(sections * 0.03, 0.15) +
                 min(len(text) / 20000, 0.15))
        complexity = "high" if score > 0.6 else ("medium" if score > 0.3 else "low")

        algo_pats = [r"algorithm\s+\d+", r"step\s+\d+", r"procedure\s+\w+"]
        algorithms = []
        for pat in algo_pats:
            algorithms.extend(re.findall(pat, text_lower)[:3])

        confidence = min(1.0, (len(domain_scores) * 0.2 + score) / 1.5)
        return {"domain": domain, "domain_scores": domain_scores,
                "complexity": complexity, "complexity_score": round(score, 3),
                "algorithms": list(set(algorithms))[:10], "confidence": round(confidence, 3)}

    @staticmethod
    def _detect_code_fragments(text: str) -> List[Dict[str, str]]:
        fragments: List[Dict[str, str]] = []
        for m in re.finditer(r"```(\w*)\n(.*?)```", text, re.DOTALL):
            lang, code = m.group(1) or "unknown", m.group(2).strip()
            if len(code) > 10:
                fragments.append({"language": lang, "code": code[:500]})
        return fragments

    def _select_language(self, text: str, analysis: Dict[str, Any]) -> str:
        text_lower = text.lower()
        scores: Dict[str, int] = {}
        for lang, kws in self.LANGUAGE_HINTS.items():
            s = sum(1 for kw in kws if kw.lower() in text_lower)
            if s > 0:
                scores[lang] = s
        if scores:
            return max(scores, key=scores.get)
        defaults = {"machine_learning": "python", "data_science": "python",
                     "web_development": "javascript", "algorithms": "python"}
        return defaults.get(analysis.get("domain", ""), "python")

    # ------------------------------------------------------------------ #
    #  原型生成
    # ------------------------------------------------------------------ #

    def _generate_prototype(self, content: Dict, analysis: Dict, fragments: List,
                            language: str, output_dir: str, source: str) -> Dict[str, Any]:
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        title = content.get("title", "prototype")
        domain = analysis.get("domain", "general")
        files: List[str] = []

        if language == "python":
            entry = "main.py"
            cls_name = self._to_class_name(title)
            code = f'''#!/usr/bin/env python3
"""
{title} - 自动生成的原型
来源: {source}
域: {domain}
生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M")}
"""
import logging
from typing import Any, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class {cls_name}:
    """从文章提取的核心逻辑原型。"""

    def __init__(self):
        self.config = {{}}
        logger.info("{title} 原型初始化")

    def run(self, data: Any = None) -> Dict[str, Any]:
        logger.info("开始执行...")
        result = self.process(data)
        return {{"success": True, "result": result}}

    def process(self, data: Any = None) -> Any:
        """核心处理逻辑（TODO: 根据文章内容实现）。"""
        raise NotImplementedError("请根据文章内容实现此方法")


def main():
    instance = {cls_name}()
    result = instance.run()
    print(f"结果: {{result}}")


if __name__ == "__main__":
    main()
'''
            (out / entry).write_text(code, encoding="utf-8")
            files.append(entry)
            if fragments:
                extracted = "# 从文章中提取的代码片段\\n\\n"
                for i, f in enumerate(fragments[:10], 1):
                    extracted += f"# --- 片段 {i} ({f['language']}) ---\\n{f['code']}\\n\\n"
                (out / "extracted_code.py").write_text(extracted, encoding="utf-8")
                files.append("extracted_code.py")
            (out / "requirements.txt").write_text("# 根据实际需要添加依赖\\n", encoding="utf-8")
            files.append("requirements.txt")
        else:
            entry = f"index.{'ts' if language == 'typescript' else 'js'}"
            code = f"// {title} - 自动生成的原型\\n// 来源: {source}\\n// TODO: 实现\\n"
            (out / entry).write_text(code, encoding="utf-8")
            files.append(entry)

        readme = f"""# {title}

> 由 Article-to-Prototype 技能自动生成

- **来源**: {source}
- **域**: {domain}
- **复杂度**: {analysis.get('complexity', 'medium')}
- **目标语言**: {language}
- **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""
        (out / "README.md").write_text(readme, encoding="utf-8")
        files.append("README.md")
        return {"files": files, "entry_point": entry}

    @staticmethod
    def _to_class_name(text: str) -> str:
        words = re.sub(r"[^a-zA-Z0-9\u4e00-\u9fff]+", " ", text).split()
        return "".join(w.capitalize() for w in words[:4]) if words else "Prototype"


__all__ = ["ArticleToPrototype"]
