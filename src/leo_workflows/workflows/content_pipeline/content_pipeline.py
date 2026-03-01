"""
Content Pipeline - 内容创作工作流
=================================
配置来源：definitions/content_pipeline.yaml（统一 YAML）
"""

from typing import Any, Dict, List

from leo_workflows.pipeline_base import PipelineBase


class ContentPipeline(PipelineBase):
    """内容创作工作流，配置统一从 definitions/content_pipeline.yaml 加载。"""

    yaml_name = "content_pipeline"

    def run(self, orchestrator, topic: str = "", content_type: str = "article",
            platform: str = "wechat", style: str = "professional",
            word_count: int = 1000, **kwargs) -> Dict[str, Any]:
        if not topic:
            raise ValueError("缺少必要参数: topic")
        inputs = {"topic": topic, "content_type": content_type, "platform": platform,
                  "style": style, "word_count": word_count, **kwargs}
        return orchestrator.run_workflow(self.config, inputs)

    # ---- 领域快捷方法 ----

    def quick_create(self, orchestrator, topic: str, platform: str = "wechat") -> Dict[str, Any]:
        """快速创作（基础文章）"""
        return self.run(orchestrator, topic=topic, platform=platform, style="casual", word_count=800)

    def create_article(self, orchestrator, topic: str, word_count: int = 1500, style: str = "professional") -> Dict[str, Any]:
        """创建文章"""
        return self.run(orchestrator, topic=topic, style=style, word_count=word_count)

    def create_short_post(self, orchestrator, topic: str, platform: str = "xiaohongshu") -> Dict[str, Any]:
        """创建短内容（小红书/微博）"""
        return self.run(orchestrator, topic=topic, content_type="post", platform=platform, style="casual", word_count=300)

    def create_video_script(self, orchestrator, topic: str, duration: int = 60, platform: str = "douyin") -> Dict[str, Any]:
        """创建视频脚本"""
        return self.run(orchestrator, topic=topic, content_type="video_script", platform=platform,
                        style="storytelling", word_count=duration * 3, duration=duration)

    def batch_create(self, orchestrator, topics: List[str], platform: str = "wechat") -> Dict[str, Any]:
        """批量创作"""
        results = [{"topic": t, "result": self.quick_create(orchestrator, t, platform)} for t in topics]
        return {"total": len(topics), "completed": len(results), "results": results}

    def get_required_skills(self) -> List[str]:
        return ["content_layout_leo_skill", "text_generator_skill"]


def create_pipeline() -> ContentPipeline:
    return ContentPipeline()

content_pipeline = ContentPipeline()
