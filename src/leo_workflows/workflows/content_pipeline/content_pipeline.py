"""
Content Pipeline - 内容创作工作流
=================================
提供内容创作全流程自动化：
- 内容策划
- 素材收集
- 内容创作
- 排版优化
- 去AI化处理
- 质量检查
- 发布准备
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


class ContentPipeline:
    """
    内容创作工作流
    ==============
    提供内容创作全流程自动化
    """

    def __init__(self):
        """初始化工作流"""
        self.workflow_dir = Path(__file__).parent
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """加载工作流配置"""
        config_path = self.workflow_dir / "workflow.yaml"
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        return {}

    def run(
        self,
        orchestrator,
        topic: str,
        content_type: str = "article",
        platform: str = "wechat",
        style: str = "professional",
        word_count: int = 1000,
        **kwargs
    ) -> Dict[str, Any]:
        """
        执行内容创作工作流

        Args:
            orchestrator: 编排器实例
            topic: 主题
            content_type: 内容类型 (article/post/video_script)
            platform: 目标平台 (wechat/xiaohongshu/douyin)
            style: 风格 (professional/casual/storytelling)
            word_count: 字数
            **kwargs: 其他参数

        Returns:
            执行结果
        """
        # 验证必要参数
        if not topic:
            raise ValueError("缺少必要参数: topic")

        # 准备输入参数
        inputs = {
            "topic": topic,
            "content_type": content_type,
            "platform": platform,
            "style": style,
            "word_count": word_count,
            **kwargs
        }

        # 执行工作流
        return orchestrator.run_workflow(self.config, inputs)

    def quick_create(
        self,
        orchestrator,
        topic: str,
        platform: str = "wechat",
    ) -> Dict[str, Any]:
        """
        快速创作（基础文章）

        Args:
            orchestrator: 编排器实例
            topic: 主题
            platform: 目标平台

        Returns:
            执行结果
        """
        return self.run(
            orchestrator,
            topic=topic,
            content_type="article",
            platform=platform,
            style="casual",
            word_count=800,
        )

    def create_article(
        self,
        orchestrator,
        topic: str,
        word_count: int = 1500,
        style: str = "professional",
    ) -> Dict[str, Any]:
        """
        创建文章

        Args:
            orchestrator: 编排器实例
            topic: 主题
            word_count: 字数
            style: 风格

        Returns:
            执行结果
        """
        return self.run(
            orchestrator,
            topic=topic,
            content_type="article",
            platform="wechat",
            style=style,
            word_count=word_count,
        )

    def create_short_post(
        self,
        orchestrator,
        topic: str,
        platform: str = "xiaohongshu",
    ) -> Dict[str, Any]:
        """
        创建短内容（小红书/微博）

        Args:
            orchestrator: 编排器实例
            topic: 主题
            platform: 平台

        Returns:
            执行结果
        """
        return self.run(
            orchestrator,
            topic=topic,
            content_type="post",
            platform=platform,
            style="casual",
            word_count=300,
        )

    def create_video_script(
        self,
        orchestrator,
        topic: str,
        duration: int = 60,
        platform: str = "douyin",
    ) -> Dict[str, Any]:
        """
        创建视频脚本

        Args:
            orchestrator: 编排器实例
            topic: 主题
            duration: 视频时长（秒）
            platform: 平台

        Returns:
            执行结果
        """
        word_count = duration * 3  # 约每秒3个字
        return self.run(
            orchestrator,
            topic=topic,
            content_type="video_script",
            platform=platform,
            style="storytelling",
            word_count=word_count,
            duration=duration,
        )

    def batch_create(
        self,
        orchestrator,
        topics: List[str],
        platform: str = "wechat",
    ) -> Dict[str, Any]:
        """
        批量创作

        Args:
            orchestrator: 编排器实例
            topics: 主题列表
            platform: 平台

        Returns:
            执行结果
        """
        results = []
        for topic in topics:
            result = self.quick_create(orchestrator, topic, platform)
            results.append({"topic": topic, "result": result})

        return {
            "total": len(topics),
            "completed": len(results),
            "results": results
        }

    def get_info(self) -> Dict[str, Any]:
        """
        获取工作流信息

        Returns:
            工作流基本信息
        """
        return {
            "name": self.config.get("name", "content-pipeline"),
            "description": self.config.get("description", "内容创作工作流"),
            "version": self.config.get("version", "1.0.0"),
            "steps_count": len(self.config.get("steps", [])),
            "triggers": self.config.get("triggers", []),
            "inputs": list(self.config.get("inputs", {}).keys()),
            "outputs": list(self.config.get("outputs", {}).keys()),
            "supported_content_types": ["article", "post", "video_script"],
            "supported_platforms": ["wechat", "xiaohongshu", "douyin"],
        }

    def get_required_agents(self) -> List[str]:
        """获取所需代理"""
        return ["creative_agent"]

    def get_required_skills(self) -> List[str]:
        """获取所需技能"""
        return ["content_layout_leo_skill", "text_generator_skill"]


# 便捷函数
def create_pipeline() -> ContentPipeline:
    """创建内容创作工作流实例"""
    return ContentPipeline()


# 导出实例
content_pipeline = ContentPipeline()
