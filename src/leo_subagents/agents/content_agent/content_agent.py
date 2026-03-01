# -*- coding: utf-8 -*-
"""
内容创意 Agent - 专注社交媒体内容、视频脚本、多平台分发
"""

from pathlib import Path
from typing import Any, Dict, Optional


class ContentAgent:
    """Agent for content creation and distribution."""

    def __init__(self, workspace: Optional[str] = None):
        self.name = "content_agent"
        self.display_name = "内容创意顾问"
        self.emoji = "✨"
        self.workspace = Path(workspace) if workspace else Path.home() / ".openclaw" / "workspace-content"
        self.model = "qwen3.5-plus"
        self.workspace.mkdir(parents=True, exist_ok=True)

        self.triggers = [
            "内容",
            "文案",
            "视频",
            "脚本",
            "小红书",
            "抖音",
            "朋友圈",
            "分发",
            "爆款",
        ]

    def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        context = context or {}
        task_lower = task.lower()

        if any(k in task_lower for k in ["视频", "脚本", "拍摄"]):
            return self._create_video_content(task, context)
        if any(k in task_lower for k in ["文案", "小红书", "抖音", "朋友圈"]):
            return self._create_social_content(task, context)
        if any(k in task_lower for k in ["分发", "发布", "多平台"]):
            return self._distribute_content(task, context)
        if any(k in task_lower for k in ["爆款", "热门", "趋势"]):
            return self._analyze_trends(task, context)
        return self._general_response(task, context)

    def _create_video_content(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        topic = context.get("topic", task)
        duration = context.get("duration", 60)
        platform = context.get("platform", "douyin")

        return {
            "status": "success",
            "agent": self.name,
            "action": "video_content_creation",
            "message": f"正在为您创作{duration}秒{platform}视频脚本：{topic}",
            "result": {
                "topic": topic,
                "duration": duration,
                "platform": platform,
                "hook": f"3秒黄金开场钩子（{topic}相关）",
                "script_structure": ["开场钩子", "痛点共鸣", "解决方案", "行动号召"],
                "shot_list": ["特写开场", "产品展示", "场景切换", "结尾引导"],
                "bgm_suggestion": "热门BGM",
            },
        }

    def _create_social_content(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        platform = context.get("platform", "xiaohongshu")
        product = context.get("product", task)

        templates = {
            "xiaohongshu": {
                "title": f"🔥被问爆了！这个{product}真的绝了",
                "structure": ["痛点引入", "产品展示", "使用体验", "购买建议"],
                "hashtags": ["#好物分享", "#种草", f"#{product}"],
            },
            "douyin": {
                "opening": f"姐妹们！我发现了一个超棒的{product}",
                "hook": "3秒必留人",
                "cta": "点赞关注不迷路",
            },
        }

        return {
            "status": "success",
            "agent": self.name,
            "action": "social_content_creation",
            "message": f"已生成{platform}平台文案：{product}",
            "result": {
                "platform": platform,
                "product": product,
                "template": templates.get(platform, {}),
                "copy_variants": 3,
            },
        }

    def _distribute_content(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        content = context.get("content", task)
        platforms = context.get("platforms", ["wechat", "xiaohongshu", "douyin"])

        distribution_plan = []
        for platform in platforms:
            if platform == "wechat":
                distribution_plan.append({"platform": "朋友圈", "format": "图文", "best_time": "12:00或18:00"})
            elif platform == "xiaohongshu":
                distribution_plan.append({"platform": "小红书", "format": "图文笔记", "best_time": "10:00或20:00"})
            elif platform == "douyin":
                distribution_plan.append({"platform": "抖音", "format": "短视频", "best_time": "12:00或21:00"})

        return {
            "status": "success",
            "agent": self.name,
            "action": "content_distribution",
            "message": f"已为{len(platforms)}个平台制定分发计划",
            "result": {
                "content": content,
                "distribution_plan": distribution_plan,
                "automation_enabled": True,
            },
        }

    def _analyze_trends(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        category = context.get("category", "general")

        return {
            "status": "success",
            "agent": self.name,
            "action": "trend_analysis",
            "message": f"正在分析{category}领域的热门趋势",
            "result": {
                "category": category,
                "trending_topics": ["话题1", "话题2", "话题3"],
                "hot_hashtags": ["#热门标签1", "#热门标签2"],
                "content_gaps": ["未覆盖的机会点"],
                "recommendation": "建议跟进热门话题",
            },
        }

    def _general_response(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "success",
            "agent": self.name,
            "action": "general",
            "message": f"内容创意顾问收到任务：{task}",
            "next_steps": [
                "分析内容需求",
                "选择合适平台",
                "创作内容",
                "制定分发计划",
            ],
        }

    def get_status(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "display_name": self.display_name,
            "emoji": self.emoji,
            "model": self.model,
            "workspace": str(self.workspace),
            "triggers": self.triggers,
            "status": "active",
        }


__all__ = ["ContentAgent"]
