#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信公众号格式化器
Author: Leo Liu
"""

from typing import Dict, Any, List
import re


class WeChatFormatter:
    """微信公众号格式化器"""

    def __init__(self, style_config: Dict[str, Any]):
        self.style_config = style_config

    def format(self, content: str, style_name: str = "data_driven",
              title: str = None, author: str = None) -> str:
        """格式化为微信公众号格式"""
        style = self._get_style(style_name)
        sections = self._parse_sections(content)
        
        html_parts = []
        html_parts.append(self._generate_css(style))
        
        if title:
            html_parts.append(self._format_title(title, style))
        
        if author:
            html_parts.append(f'<p class="meta">作者：{author}</p>')
        
        html_parts.append('<section class="content">')
        
        for section in sections:
            formatted_section = self._format_section(section, style)
            html_parts.append(formatted_section)
        
        html_parts.append('</section>')
        html_parts.append(self._format_footer(style))
        
        return '\n'.join(html_parts)

    def _get_style(self, style_name: str) -> Dict[str, Any]:
        """获取样式配置"""
        styles = self.style_config.get("styles", [])
        for style in styles:
            if style.get("name") == style_name:
                return style
        return styles[0] if styles else {}

    def _parse_sections(self, content: str) -> List[Dict[str, Any]]:
        """解析内容章节"""
        sections = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.rstrip()
            if not line:
                continue
            
            # 检测标题（支持# 和##）
            if line.startswith('#'):
                heading_level = len(line) - len(line.lstrip('#'))
                heading_text = line.lstrip('#').strip()
                sections.append({
                    "type": "heading",
                    "level": heading_level,
                    "title": heading_text,
                    "content": heading_text
                })
            else:
                # 普通段落
                sections.append({
                    "type": "body",
                    "content": line
                })
        
        return sections

    def _format_section(self, section: Dict[str, Any], style: Dict[str, Any]) -> str:
        """格式化章节"""
        section_type = section.get("type", "body")
        typography = style.get("typography", {})
        
        if section_type == "heading":
            level = section.get("level", 2)
            title = section.get("title", "")
            heading_style = typography.get("heading", {})
            styles = self._build_css(heading_style)
            return f'<h{level} style="{styles}">{title}</h{level}>'
        
        elif section_type == "body":
            content = section.get("content", "")
            body_style = typography.get("body", {})
            
            # 检测是否为高亮内容
            if self._is_highlight(content):
                highlight_style = typography.get("highlight", {})
                return f'<p style="{self._build_css(highlight_style)}">{content}</p>'
            else:
                return f'<p style="{self._build_css(body_style)}">{content}</p>'
        
        return ""

    def _is_highlight(self, text: str) -> bool:
        """判断是否为高亮内容"""
        return any(indicator in text for indicator in ["**", "我想说的是", "说实话", "数据不会骗人"])

    def _format_title(self, title: str, style: Dict[str, Any]) -> str:
        """格式化标题"""
        title_style = style.get("typography", {}).get("title", {})
        styles = self._build_css(title_style)
        return f'<h1 style="{styles}">{title}</h1>'

    def _format_footer(self, style: Dict[str, Any]) -> str:
        """格式化结尾"""
        return '''
<div class="footer" style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #e0e0e0;">
    <p style="color: #999999; font-size: 14px; text-align: center;">
        数据来源：国家统计局、宁波市住建委
    </p>
    <p style="color: #999999; font-size: 12px; text-align: center;">
        本文仅供参考，不构成投资建议
    </p>
</div>
'''

    def _generate_css(self, style: Dict[str, Any]) -> str:
        """生成CSS样式"""
        typography = style.get("typography", {})
        color_scheme = style.get("color_scheme", {})
        
        body_color = typography.get("body", {}).get("color", "#333333")
        body_line_height = typography.get("body", {}).get("line_height", "1.8")
        
        return f'''
<style>
    body {{
        font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", Arial, sans-serif;
        max-width: 677px;
        margin: 0 auto;
        padding: 20px;
        color: {body_color};
        line-height: {body_line_height};
    }}
    .content {{
        margin: 20px 0;
    }}
    img {{
        max-width: 100%;
        height: auto;
        display: block;
        margin: 15px 0;
        border-radius: 4px;
    }}
    .meta {{
        color: #999999;
        font-size: 14px;
        margin: 10px 0;
    }}
</style>
'''

    def _build_css(self, style_dict: Dict[str, Any]) -> str:
        """构建CSS字符串"""
        css_parts = []
        for key, value in style_dict.items():
            if key == "font_size":
                css_parts.append(f"font-size: {value}")
            elif key == "font_weight":
                css_parts.append(f"font-weight: {value}")
            elif key == "color":
                css_parts.append(f"color: {value}")
            elif key == "line_height":
                css_parts.append(f"line-height: {value}")
            elif key == "background":
                css_parts.append(f"background: {value}")
            elif key == "padding":
                css_parts.append(f"padding: {value}")
            elif key == "margin":
                css_parts.append(f"margin: {value}")
            elif key == "border_radius":
                css_parts.append(f"border-radius: {value}")
            elif key == "border_left":
                css_parts.append(f"border-left: {value}")
            elif key == "border_bottom":
                css_parts.append(f"border-bottom: {value}")
            elif key == "padding_bottom":
                css_parts.append(f"padding-bottom: {value}")
            elif key == "padding_left":
                css_parts.append(f"padding-left: {value}")
            elif key == "text_align":
                css_parts.append(f"text-align: {value}")
            elif key == "text_transform":
                css_parts.append(f"text-transform: {value}")
            elif key == "letter_spacing":
                css_parts.append(f"letter-spacing: {value}")
            elif key == "margin_top":
                css_parts.append(f"margin-top: {value}")
            elif key == "margin_bottom":
                css_parts.append(f"margin-bottom: {value}")
            else:
                css_key = key.replace('_', '-')
                css_parts.append(f"{css_key}: {value}")
        
        return '; '.join(css_parts)
