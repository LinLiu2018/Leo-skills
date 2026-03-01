"""
Obsidian 知识库同步技能

将 Leo 系统知识库、Claude 对话、技能输出同步到 Obsidian Vault。
支持快速捕获、结构化笔记、日记、MOC 管理、搜索等功能。
"""

from __future__ import annotations

import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from leo_skills.core.base_executor import BaseExecutor

logger = logging.getLogger(__name__)


# 内置模板
_TEMPLATES = {
    "default": """---
created: {{datetime}}
tags: [{{tags}}]
---

# {{title}}

{{content}}

## 相关链接
{{links}}
""",
    "daily": """---
created: {{datetime}}
tags: [日记, {{tags}}]
---

# {{date}} {{weekday}}

## 今日计划
{{plan}}

## 记录
{{content}}

## 复盘
- 今日最大收获：
- 明天改进：
""",
    "research": """---
created: {{datetime}}
source: {{source}}
tags: [研究, {{tags}}]
---

# {{title}}

## 核心观点
{{summary}}

## 详细内容
{{content}}

## 我的思考


## 行动项
- [ ]
""",
    "claude": """---
created: {{datetime}}
source: Claude对话
tags: [claude笔记, {{tags}}]
---

# {{title}}

## 问题/需求
{{question}}

## Claude回答摘要
{{content}}

## 行动项
- [ ]
""",
    "leo-output": """---
created: {{datetime}}
source: Leo-System
skill: {{skill_name}}
tags: [leo-output, {{skill_name}}, {{tags}}]
---

# {{title}}

{{content}}

---
*由 Leo System {{skill_name}} 自动生成*
""",
    "project": """---
created: {{datetime}}
status: active
tags: [项目, {{tags}}]
---

# {{title}}

## 项目概述
{{content}}

## 目标
-

## 进度
- [ ]
""",
    "moc": """---
created: {{datetime}}
tags: [MOC, 索引]
---

# {{title}} MOC

## 概述
这是关于{{title}}的内容地图。

## 核心概念
{{links}}

---
*最后更新: {{datetime}}*
""",
}

# 推荐文件夹结构
_DEFAULT_FOLDERS = [
    "00-Inbox", "01-Daily", "10-Projects", "20-Areas",
    "30-Resources", "40-Archives", "Leo-Outputs/content-layout",
    "Leo-Outputs/research", "Leo-Outputs/marketing", "Leo-Outputs/analysis",
    "Claude-Notes", "MOCs", "Templates",
]

_WEEKDAYS = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]


class ObsidianSync(BaseExecutor):
    """Obsidian 知识库同步技能。

    支持的操作：
        - quick_capture:   快速捕获到 Inbox
        - create_note:     创建结构化笔记
        - create_daily:    创建日记
        - save_leo_output: 保存 Leo 技能输出
        - save_claude:     保存 Claude 对话笔记
        - update_moc:      更新 MOC 内容地图
        - search:          搜索笔记
        - recent:          获取最近笔记
    """

    def __init__(self, vault_path: Optional[str] = None) -> None:
        self.name = "obsidian_sync_skill"
        self._config: Optional[Dict[str, Any]] = None
        self._vault_path: Optional[Path] = Path(vault_path) if vault_path else None

    # ------------------------------------------------------------------ #
    #  BaseExecutor 接口
    # ------------------------------------------------------------------ #

    def execute(
        self,
        action: str = "quick_capture",
        context: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = dict(context or {})
        params.update(kwargs)

        actions = {
            "quick_capture": self.quick_capture,
            "create_note": self.create_note,
            "create_daily": self.create_daily_note,
            "save_leo_output": self.save_leo_output,
            "save_claude": self.save_claude_note,
            "update_moc": self.update_moc,
            "search": self.search_notes,
            "recent": self.get_recent_notes,
            "run": self.quick_capture,
        }
        handler = actions.get(action)
        if handler is None:
            return {"status": "error", "message": f"未知操作: {action}"}
        return handler(**params)

    # ------------------------------------------------------------------ #
    #  配置与初始化
    # ------------------------------------------------------------------ #

    @property
    def vault_path(self) -> Path:
        if self._vault_path and self._vault_path.exists():
            return self._vault_path
        config = self._load_config()
        vp = config.get("vault_path", "")
        if vp:
            self._vault_path = Path(vp)
        return self._vault_path or Path(".")

    def _load_config(self) -> Dict[str, Any]:
        if self._config is not None:
            return self._config
        config_path = Path(__file__).parent / "config" / "config.yaml"
        if config_path.exists():
            try:
                import yaml
                with open(config_path, "r", encoding="utf-8") as f:
                    self._config = yaml.safe_load(f) or {}
            except Exception:
                self._config = {}
        else:
            self._config = {
                "vault_path": "", "default_folder": "00-Inbox",
                "auto_create_folders": True, "default_tags": ["claude生成"],
                "leo_output_folder": "Leo-Outputs", "daily_folder": "01-Daily",
                "moc_folder": "MOCs",
            }
        return self._config

    def _ensure_folder(self, folder: str) -> Path:
        fp = self.vault_path / folder
        fp.mkdir(parents=True, exist_ok=True)
        return fp

    def _init_folders(self) -> None:
        if self.vault_path.exists():
            for f in _DEFAULT_FOLDERS:
                (self.vault_path / f).mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------ #
    #  模板渲染
    # ------------------------------------------------------------------ #

    @staticmethod
    def _render(template_name: str, variables: Dict[str, Any]) -> str:
        template = _TEMPLATES.get(template_name, _TEMPLATES["default"])
        now = datetime.now()
        variables.setdefault("date", now.strftime("%Y-%m-%d"))
        variables.setdefault("time", now.strftime("%H:%M"))
        variables.setdefault("datetime", now.strftime("%Y-%m-%d %H:%M"))
        variables.setdefault("weekday", _WEEKDAYS[now.weekday()])

        tags = variables.get("tags", [])
        if isinstance(tags, list):
            variables["tags"] = ", ".join(tags)

        links = variables.get("links", [])
        if isinstance(links, list):
            variables["links"] = "\n".join(f"- [[{lk}]]" for lk in links) if links else ""

        plan = variables.get("plan", [])
        if isinstance(plan, list):
            variables["plan"] = "\n".join(f"- [ ] {it}" for it in plan) if plan else "- [ ] "

        result = template
        for k, v in variables.items():
            result = result.replace("{{" + k + "}}", str(v) if v else "")
        result = re.sub(r"\{\{\w+\}\}", "", result)
        return result

    @staticmethod
    def _sanitize(filename: str) -> str:
        for ch in '<>:"/\\|?*':
            filename = filename.replace(ch, "")
        return filename.strip()

    # ------------------------------------------------------------------ #
    #  核心功能
    # ------------------------------------------------------------------ #

    def quick_capture(self, content: str = "", title: Optional[str] = None,
                      tags: Optional[List[str]] = None, folder: Optional[str] = None,
                      **kwargs) -> Dict[str, Any]:
        """快速捕获内容到 Inbox。"""
        if not self.vault_path.exists():
            return {"status": "error", "message": f"Vault 路径不存在: {self.vault_path}"}

        if not title:
            title = f"快速笔记_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        title = self._sanitize(title)

        config = self._load_config()
        all_tags = list(config.get("default_tags", []))
        if tags:
            all_tags.extend(tags)
        all_tags = list(set(all_tags))

        note = self._render("default", {"title": title, "content": content, "tags": all_tags, "links": []})
        target = folder or config.get("default_folder", "00-Inbox")
        fp = self._ensure_folder(target) / f"{title}.md"

        try:
            fp.write_text(note, encoding="utf-8")
            return {"status": "success", "path": str(fp), "title": title, "folder": target}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def create_note(self, title: str = "", content: str = "", template: str = "default",
                    folder: Optional[str] = None, tags: Optional[List[str]] = None,
                    links: Optional[List[str]] = None, **kwargs) -> Dict[str, Any]:
        """创建结构化笔记。"""
        if not self.vault_path.exists():
            return {"status": "error", "message": "Vault 路径不存在"}
        title = self._sanitize(title or "未命名笔记")
        variables = {"title": title, "content": content, "tags": tags or [], "links": links or [], **kwargs}
        note = self._render(template, variables)
        target = folder or self._load_config().get("default_folder", "00-Inbox")
        fp = self._ensure_folder(target) / f"{title}.md"
        try:
            fp.write_text(note, encoding="utf-8")
            return {"status": "success", "path": str(fp), "title": title, "template": template}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def create_daily_note(self, date: Optional[str] = None, plan: Optional[List[str]] = None,
                          notes: str = "", tags: Optional[List[str]] = None,
                          **kwargs) -> Dict[str, Any]:
        """创建日记。"""
        if not self.vault_path.exists():
            return {"status": "error", "message": "Vault 路径不存在"}
        if date:
            try:
                nd = datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                nd = datetime.now()
        else:
            nd = datetime.now()
        ds = nd.strftime("%Y-%m-%d")
        wd = _WEEKDAYS[nd.weekday()]
        variables = {"title": ds, "date": ds, "weekday": wd, "plan": plan or [],
                     "content": notes, "tags": tags or []}
        note = self._render("daily", variables)
        daily_folder = self._load_config().get("daily_folder", "01-Daily")
        fp = self._ensure_folder(daily_folder) / f"{ds}.md"
        try:
            fp.write_text(note, encoding="utf-8")
            return {"status": "success", "path": str(fp), "date": ds}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def save_leo_output(self, content: Union[str, Dict, Any] = "", skill_name: str = "unknown",
                        title: Optional[str] = None, folder: Optional[str] = None,
                        tags: Optional[List[str]] = None, **kwargs) -> Dict[str, Any]:
        """保存 Leo 技能输出。"""
        if not self.vault_path.exists():
            return {"status": "error", "message": "Vault 路径不存在"}
        if isinstance(content, dict):
            try:
                import yaml
                content_str = yaml.dump(content, allow_unicode=True, default_flow_style=False)
            except Exception:
                content_str = str(content)
        else:
            content_str = str(content)

        if not title:
            ds = datetime.now().strftime("%Y-%m-%d")
            topic = kwargs.get("topic", "")
            title = f"{ds}_{topic}_{skill_name}" if topic else f"{skill_name}_{ds}"
        title = self._sanitize(title)

        if not folder:
            config = self._load_config()
            leo_folder = config.get("leo_output_folder", "Leo-Outputs")
            sub = skill_name.replace("-cskill", "").replace("_skill", "")
            folder = f"{leo_folder}/{sub}"

        variables = {"title": title, "content": content_str, "skill_name": skill_name,
                     "tags": tags or [], **kwargs}
        note = self._render("leo-output", variables)
        fp = self._ensure_folder(folder) / f"{title}.md"
        try:
            fp.write_text(note, encoding="utf-8")
            return {"status": "success", "path": str(fp), "title": title, "skill": skill_name}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def save_claude_note(self, content: str = "", title: str = "Claude对话",
                         question: str = "", tags: Optional[List[str]] = None,
                         links: Optional[List[str]] = None, **kwargs) -> Dict[str, Any]:
        """保存 Claude 对话笔记。"""
        return self.create_note(
            title=title, content=content, template="claude",
            folder="Claude-Notes", tags=tags, links=links, question=question,
        )

    def update_moc(self, moc_name: str = "", add_links: Optional[List[str]] = None,
                   remove_links: Optional[List[str]] = None, **kwargs) -> Dict[str, Any]:
        """更新 MOC（内容地图）。"""
        if not self.vault_path.exists():
            return {"status": "error", "message": "Vault 路径不存在"}
        if not moc_name:
            return {"status": "error", "message": "缺少 moc_name 参数"}

        moc_folder = self._load_config().get("moc_folder", "MOCs")
        moc_path = self.vault_path / moc_folder / f"{moc_name}.md"

        if not moc_path.exists():
            content = self._render("moc", {"title": moc_name, "links": add_links or []})
            self._ensure_folder(moc_folder)
            moc_path.write_text(content, encoding="utf-8")
            return {"status": "success", "path": str(moc_path), "action": "created"}

        content = moc_path.read_text(encoding="utf-8")
        if add_links:
            for lk in add_links:
                link_str = f"- [[{lk}]]"
                if link_str not in content:
                    if "## 核心概念" in content:
                        content = content.replace("## 核心概念\n", f"## 核心概念\n{link_str}\n")
                    else:
                        content += f"\n{link_str}"
        if remove_links:
            for lk in remove_links:
                content = content.replace(f"- [[{lk}]]\n", "").replace(f"- [[{lk}]]", "")

        content = re.sub(r"\*最后更新: .*\*",
                         f'*最后更新: {datetime.now().strftime("%Y-%m-%d %H:%M")}*', content)
        try:
            moc_path.write_text(content, encoding="utf-8")
            return {"status": "success", "path": str(moc_path), "action": "updated",
                    "added": add_links, "removed": remove_links}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def search_notes(self, query: str = "", folder: Optional[str] = None,
                     limit: int = 20, **kwargs) -> Dict[str, Any]:
        """搜索笔记。"""
        if not self.vault_path.exists():
            return {"status": "error", "message": "Vault 路径不存在"}
        if not query:
            return {"status": "error", "message": "缺少 query 参数"}

        search_path = self.vault_path / folder if folder else self.vault_path
        results: List[Dict[str, str]] = []
        for md in search_path.rglob("*.md"):
            try:
                text = md.read_text(encoding="utf-8")
                if query.lower() in text.lower():
                    idx = text.lower().find(query.lower())
                    ctx = text[max(0, idx - 50):idx + len(query) + 50]
                    results.append({
                        "path": str(md.relative_to(self.vault_path)),
                        "title": md.stem, "context": f"...{ctx}...",
                    })
                    if len(results) >= limit:
                        break
            except Exception:
                continue
        return {"status": "success", "query": query, "results": results, "total": len(results)}

    def get_recent_notes(self, limit: int = 10, folder: Optional[str] = None,
                         **kwargs) -> Dict[str, Any]:
        """获取最近修改的笔记。"""
        if not self.vault_path.exists():
            return {"status": "error", "message": "Vault 路径不存在"}
        search_path = self.vault_path / folder if folder else self.vault_path
        notes: List[Dict[str, Any]] = []
        for md in search_path.rglob("*.md"):
            notes.append({
                "path": str(md.relative_to(self.vault_path)),
                "title": md.stem, "modified": md.stat().st_mtime,
            })
        notes.sort(key=lambda x: x["modified"], reverse=True)
        for n in notes[:limit]:
            n["modified"] = datetime.fromtimestamp(n["modified"]).strftime("%Y-%m-%d %H:%M")
        return {"status": "success", "notes": notes[:limit], "total": len(notes)}


__all__ = ["ObsidianSync"]
