"""
智能内容排版技能

支持微信公众号、小红书等多平台智能排版。
将 Markdown 内容转换为平台特定的格式化输出。
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from leo_skills.core.base_executor import BaseExecutor


class ContentLayoutSkill(BaseExecutor):
    """智能内容排版技能。

    支持的操作：
        - format_wechat:       微信公众号格式化
        - format_xiaohongshu:  小红书格式化
        - format_weibo:        微博格式化
        - format_blog:         博客格式化
        - generate_image_prompts: 生成 AI 图片提示词
    """

    # 平台特定的样式配置
    PLATFORM_STYLES = {
        "wechat": {
            "heading_color": "#1a1a2e",
            "accent_color": "#e94560",
            "body_font_size": "16px",
            "line_height": "1.8",
            "max_width": "600px",
        },
        "xiaohongshu": {
            "emoji_density": "high",
            "hashtag_style": "inline",
            "max_length": 1000,
        },
        "weibo": {
            "max_length": 2000,
            "hashtag_style": "bracket",
        },
        "blog": {
            "heading_style": "markdown",
            "code_highlight": True,
        },
    }

    def __init__(self) -> None:
        self.name = "content_layout_leo_skill"
        self._config: Optional[Dict[str, Any]] = None

    # ------------------------------------------------------------------ #
    #  BaseExecutor 接口
    # ------------------------------------------------------------------ #

    def execute(
        self,
        action: str = "format_wechat",
        context: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = dict(context or {})
        params.update(kwargs)

        action_map = {
            "format_wechat": self.format_for_wechat,
            "format_xiaohongshu": self.format_for_xiaohongshu,
            "format_weibo": self.format_for_weibo,
            "format_blog": self.format_for_blog,
            "generate_image_prompts": self.generate_image_prompts,
        }

        handler = action_map.get(action)
        if handler is None:
            return {"status": "error", "message": f"未知操作: {action}，可用操作: {list(action_map.keys())}"}

        return handler(**params)

    # ------------------------------------------------------------------ #
    #  配置加载
    # ------------------------------------------------------------------ #

    def _load_config(self) -> Dict[str, Any]:
        """懒加载配置文件。"""
        if self._config is not None:
            return self._config
        config_path = Path(__file__).parent / "config" / "style_profiles.yaml"
        if config_path.exists():
            try:
                import yaml
                with open(config_path, "r", encoding="utf-8") as f:
                    self._config = yaml.safe_load(f) or {}
            except Exception:
                self._config = {}
        else:
            self._config = {}
        return self._config

    # ------------------------------------------------------------------ #
    #  微信公众号排版
    # ------------------------------------------------------------------ #

    def format_for_wechat(
        self,
        content: str = "",
        style: str = "data_driven",
        title: Optional[str] = None,
        author: str = "Leo",
        **kwargs,
    ) -> Dict[str, Any]:
        """将 Markdown 内容格式化为微信公众号 HTML。"""
        try:
            style_cfg = self.PLATFORM_STYLES["wechat"]
            html_parts: List[str] = []

            # 头部容器
            html_parts.append(f'<section style="max-width:{style_cfg["max_width"]};margin:0 auto;padding:20px;">')

            # 标题
            if title:
                html_parts.append(
                    f'<h1 style="color:{style_cfg["heading_color"]};font-size:24px;'
                    f'font-weight:bold;text-align:center;margin-bottom:20px;">{title}</h1>'
                )
                html_parts.append(
                    f'<p style="text-align:center;color:#999;font-size:14px;margin-bottom:30px;">'
                    f'{author}</p>'
                )

            # 逐行解析 Markdown
            lines = content.split("\n")
            in_code_block = False
            for line in lines:
                stripped = line.strip()
                if not stripped:
                    html_parts.append("<br/>")
                    continue

                # 代码块
                if stripped.startswith("```"):
                    in_code_block = not in_code_block
                    if in_code_block:
                        html_parts.append(
                            '<pre style="background:#f5f5f5;padding:15px;border-radius:5px;'
                            'overflow-x:auto;font-size:14px;line-height:1.5;">'
                        )
                    else:
                        html_parts.append("</pre>")
                    continue

                if in_code_block:
                    html_parts.append(f"{self._escape_html(stripped)}\n")
                    continue

                # 标题级别
                if stripped.startswith("### "):
                    heading = stripped[4:]
                    html_parts.append(
                        f'<h3 style="color:{style_cfg["heading_color"]};font-size:18px;'
                        f'margin:20px 0 10px;border-left:3px solid {style_cfg["accent_color"]};'
                        f'padding-left:10px;">{heading}</h3>'
                    )
                elif stripped.startswith("## "):
                    heading = stripped[3:]
                    html_parts.append(
                        f'<h2 style="color:{style_cfg["heading_color"]};font-size:20px;'
                        f'margin:25px 0 15px;font-weight:bold;">{heading}</h2>'
                    )
                elif stripped.startswith("# "):
                    heading = stripped[2:]
                    html_parts.append(
                        f'<h1 style="color:{style_cfg["heading_color"]};font-size:24px;'
                        f'margin:30px 0 15px;font-weight:bold;">{heading}</h1>'
                    )
                elif stripped.startswith("- ") or stripped.startswith("* "):
                    item = stripped[2:]
                    html_parts.append(
                        f'<p style="font-size:{style_cfg["body_font_size"]};'
                        f'line-height:{style_cfg["line_height"]};padding-left:20px;">'
                        f'<span style="color:{style_cfg["accent_color"]};">●</span> {item}</p>'
                    )
                elif stripped.startswith("> "):
                    quote = stripped[2:]
                    html_parts.append(
                        f'<blockquote style="border-left:3px solid {style_cfg["accent_color"]};'
                        f'padding:10px 15px;background:#f9f9f9;margin:15px 0;color:#666;">'
                        f'{quote}</blockquote>'
                    )
                else:
                    # 处理行内样式（加粗、行内代码）
                    text = self._inline_styles_html(stripped, style_cfg)
                    html_parts.append(
                        f'<p style="font-size:{style_cfg["body_font_size"]};'
                        f'line-height:{style_cfg["line_height"]};margin:10px 0;">{text}</p>'
                    )

            html_parts.append("</section>")
            result_html = "\n".join(html_parts)

            return {
                "status": "success",
                "result": result_html,
                "platform": "wechat",
                "style": style,
                "char_count": len(result_html),
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    # ------------------------------------------------------------------ #
    #  小红书排版
    # ------------------------------------------------------------------ #

    def format_for_xiaohongshu(
        self,
        content: str = "",
        style: str = "vibrant_attention",
        title: Optional[str] = None,
        tags: Optional[List[str]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """将内容格式化为小红书风格文本。"""
        try:
            formatted: List[str] = []
            if title:
                formatted.append(f"{'='*30}\n  {title}\n{'='*30}\n")

            lines = content.split("\n")
            for line in lines:
                stripped = line.strip()
                if not stripped:
                    continue
                if stripped.startswith("#"):
                    heading = stripped.lstrip("#").strip()
                    formatted.append(f"\n{'='*30}\n  {heading}\n{'='*30}\n")
                elif stripped.startswith("- ") or stripped.startswith("* "):
                    item = stripped[2:]
                    formatted.append(f"  {item}")
                else:
                    formatted.append(stripped)

            # 分隔线 + 标签
            formatted.append("\n" + "-" * 30)
            default_tags = tags or ["房产", "楼市", "宁波", "购房指南"]
            tag_line = " ".join([f"#{t}" for t in default_tags])
            formatted.append(f"\n{tag_line}")

            result = "\n".join(formatted)

            return {
                "status": "success",
                "result": result,
                "platform": "xiaohongshu",
                "style": style,
                "char_count": len(result),
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    # ------------------------------------------------------------------ #
    #  微博排版
    # ------------------------------------------------------------------ #

    def format_for_weibo(
        self,
        content: str = "",
        title: Optional[str] = None,
        tags: Optional[List[str]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """将内容格式化为微博风格。"""
        try:
            parts: List[str] = []
            if title:
                parts.append(f"【{title}】")

            # 微博以简洁为主，去掉 Markdown 格式
            cleaned = re.sub(r"#{1,6}\s*", "", content)
            cleaned = re.sub(r"\*\*(.*?)\*\*", r"\1", cleaned)
            cleaned = re.sub(r"`(.*?)`", r"\1", cleaned)
            cleaned = re.sub(r"^\s*[-*]\s+", "- ", cleaned, flags=re.MULTILINE)
            parts.append(cleaned.strip())

            # 标签
            default_tags = tags or ["热点"]
            tag_line = " ".join([f"#{t}#" for t in default_tags])
            parts.append(f"\n{tag_line}")

            result = "\n".join(parts)
            max_len = self.PLATFORM_STYLES["weibo"]["max_length"]
            if len(result) > max_len:
                result = result[:max_len - 3] + "..."

            return {
                "status": "success",
                "result": result,
                "platform": "weibo",
                "char_count": len(result),
                "truncated": len(result) >= max_len,
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    # ------------------------------------------------------------------ #
    #  博客排版
    # ------------------------------------------------------------------ #

    def format_for_blog(
        self,
        content: str = "",
        title: Optional[str] = None,
        author: str = "Leo",
        **kwargs,
    ) -> Dict[str, Any]:
        """将内容格式化为博客 Markdown（添加 frontmatter）。"""
        try:
            from datetime import datetime
            now = datetime.now().strftime("%Y-%m-%d %H:%M")

            frontmatter = f"""---
title: "{title or '未命名文章'}"
author: "{author}"
date: "{now}"
---

"""
            result = frontmatter + content
            return {
                "status": "success",
                "result": result,
                "platform": "blog",
                "char_count": len(result),
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    # ------------------------------------------------------------------ #
    #  AI 图片提示词生成
    # ------------------------------------------------------------------ #

    def generate_image_prompts(
        self,
        content: str = "",
        style: str = "professional",
        count: int = 3,
        **kwargs,
    ) -> Dict[str, Any]:
        """根据内容分析生成 AI 图片提示词。"""
        try:
            # 提取关键句和主题
            sentences = [s.strip() for s in re.split(r"[。！？\n]", content) if len(s.strip()) > 10]
            topics = self._extract_topics(content)

            style_prefixes = {
                "professional": "Professional, clean, modern corporate style,",
                "creative": "Creative, colorful, artistic illustration style,",
                "minimalist": "Minimalist, white space, simple elegant design,",
                "tech": "Futuristic, technology-inspired, digital art style,",
            }
            prefix = style_prefixes.get(style, style_prefixes["professional"])

            prompts: List[Dict[str, str]] = []
            for i, topic in enumerate(topics[:count]):
                prompt = f"{prefix} {topic}, high quality, detailed, 4K resolution"
                prompts.append({
                    "index": i + 1,
                    "topic": topic,
                    "prompt": prompt,
                    "negative_prompt": "blurry, low quality, distorted, text, watermark",
                })

            return {
                "status": "success",
                "prompts": prompts,
                "count": len(prompts),
                "style": style,
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    # ------------------------------------------------------------------ #
    #  辅助方法
    # ------------------------------------------------------------------ #

    @staticmethod
    def _escape_html(text: str) -> str:
        """转义 HTML 特殊字符。"""
        return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    @staticmethod
    def _inline_styles_html(text: str, style_cfg: Dict) -> str:
        """处理行内 Markdown 样式（加粗、行内代码）。"""
        # 加粗
        text = re.sub(
            r"\*\*(.*?)\*\*",
            rf'<strong style="color:{style_cfg["accent_color"]};">\1</strong>',
            text,
        )
        # 行内代码
        text = re.sub(
            r"`(.*?)`",
            r'<code style="background:#f0f0f0;padding:2px 6px;border-radius:3px;font-size:14px;">\1</code>',
            text,
        )
        return text

    @staticmethod
    def _extract_topics(content: str) -> List[str]:
        """从内容中提取关键主题用于图片生成。"""
        topics: List[str] = []
        lines = content.split("\n")
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("#"):
                topic = stripped.lstrip("#").strip()
                if topic and len(topic) > 2:
                    topics.append(topic)
            elif len(stripped) > 20:
                # 截取核心短语
                topics.append(stripped[:50])
        return topics or ["abstract visual content"]


__all__ = ["ContentLayoutSkill"]
