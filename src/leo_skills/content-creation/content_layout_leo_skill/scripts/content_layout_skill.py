#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Content Layout Skill - 智能内容排版技能（可进化版本）
"""

import sys
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

# 添加leo-skills到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from core.evolution import EvolvableSkill
from formatters.wechat_formatter import WeChatFormatter
from image_matchers.intelligent_matcher import ImageMatcher


class ContentLayoutSkill(EvolvableSkill):
    """智能内容排版技能"""

    def __init__(self):
        super().__init__(
            skill_name="content_layout_leo_skill",
            config_path=str(Path(__file__).parent.parent / "config" / "config.yaml"),
        )
        self.skill_root = Path(__file__).parent.parent
        self.config_dir = self.skill_root / "config"

    def _execute_core(self, action: str = "format", **kwargs) -> Dict[str, Any]:
        """核心执行逻辑"""
        if action == "format_wechat":
            return self.format_for_wechat(**kwargs)
        elif action == "format_xiaohongshu":
            return self.format_for_xiaohongshu(**kwargs)
        elif action == "generate_image_prompts":
            return self.generate_image_prompts(**kwargs)
        else:
            return {"success": False, "error": f"Unknown action: {action}", "quality_score": 0.0}

    def load_config(self) -> Dict[str, Any]:
        """加载配置"""
        config_path = self.config_dir / "style_profiles.yaml"
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        return {}

    def format_for_wechat(
        self,
        content: str,
        style: str = "data_driven",
        title: Optional[str] = None,
        author: str = "Leo",
    ) -> Dict[str, Any]:
        """格式化为微信公众号格式"""
        try:
            config = self.load_config()
            formatter = WeChatFormatter(config)
            html_content = formatter.format(
                content=content, style_name=style, title=title, author=author
            )

            return {
                "success": True,
                "result": html_content,
                "platform": "wechat",
                "style": style,
                "quality_score": 0.9,
            }
        except Exception as e:
            return {"success": False, "error": str(e), "quality_score": 0.0}

    def format_for_xiaohongshu(
        self, content: str, style: str = "vibrant_attention", title: Optional[str] = None
    ) -> Dict[str, Any]:
        """格式化为小红书格式"""
        try:
            formatted = []
            if title:
                formatted.append(f"📌 {title}\n")

            lines = content.split("\n")
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                if line.startswith("#"):
                    heading = line.lstrip("#").strip()
                    formatted.append(f"\n{'='*30}\n  {heading}\n{'='*30}\n")
                else:
                    formatted.append(line + "\n")

            formatted.append("\n" + "─" * 30)
            formatted.append("\n🏷️  #房产 #楼市 #宁波 #购房指南")

            result = "\n".join(formatted)

            return {
                "success": True,
                "result": result,
                "platform": "xiaohongshu",
                "style": style,
                "quality_score": 0.85,
            }
        except Exception as e:
            return {"success": False, "error": str(e), "quality_score": 0.0}

    def generate_image_prompts(self, content: str, style: str = "professional") -> Dict[str, Any]:
        """生成AI图片提示词"""
        try:
            config = self.load_config()
            image_rules = config.get("image_matching_rules", {})
            matcher = ImageMatcher(image_rules)
            prompts = matcher.generate_image_prompts(content, style)

            return {
                "success": True,
                "prompts": prompts,
                "count": len(prompts),
                "quality_score": 0.8,
            }
        except Exception as e:
            return {"success": False, "error": str(e), "quality_score": 0.0}
