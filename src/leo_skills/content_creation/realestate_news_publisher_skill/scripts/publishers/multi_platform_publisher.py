# Multi-Platform Publisher Module
# 多平台发布模块

from typing import Dict, Any, List
from utils.logger import get_logger

logger = get_logger(__name__)


class MultiPlatformPublisher:
    """多平台发布器"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化多平台发布器

        Args:
            config: 平台配置
        """
        self.config = config
        self.platforms_config = config.get("platforms", {})

        # 初始化各平台发布器
        self.publishers = {}
        self._init_publishers()

    def _init_publishers(self):
        """初始化各平台发布器"""
        # 微信公众号
        wechat_config = {
            "app_id": self.config.get("app_id", ""),
            "app_secret": self.config.get("app_secret", ""),
            "account_id": self.config.get("account_id", ""),
            "auto_publish": self.config.get("auto_publish", False),
            "create_as_draft": self.config.get("create_as_draft", True)
        }
        from .wechat_publisher import WeChatPublisher
        self.publishers["wechat"] = WeChatPublisher(wechat_config)

        # 其他平台（需要相应API支持）
        # self.publishers["wechat_channel"] = WeChatChannelPublisher(...)
        # self.publishers["xiaohongshu"] = XiaohongshuPublisher(...)
        # self.publishers["douyin"] = DouyinPublisher(...)

    def publish_to_all(self, article: Dict[str, Any],
                       platforms: List[str] = None) -> Dict[str, Any]:
        """
        发布到所有平台

        Args:
            article: 文章数据
            platforms: 指定平台列表，None 表示全部

        Returns:
            各平台发布结果
        """
        results = {}

        if platforms is None:
            platforms = ["wechat"]  # 默认只发布到微信公众号

        for platform in platforms:
            if platform in self.publishers:
                try:
                    result = self.publishers[platform].publish(article)
                    results[platform] = result
                except Exception as e:
                    logger.error(f"发布到 {platform} 失败: {e}")
                    results[platform] = {"success": False, "error": str(e)}
            else:
                logger.warning(f"平台 {platform} 未配置")
                results[platform] = {"success": False, "error": "平台未配置"}

        return results

    def publish_to_wechat(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """发布到微信公众号"""
        return self.publishers["wechat"].publish(article)

    def adapt_for_wechat_channel(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """适配为视频号内容"""
        # 提取关键信息
        title = article.get("title", "")
        content = article.get("content", "")

        # 生成口播文案
        script = self._generate_voice_script(title, content)

        return {
            "title": title,
            "script": script,
            "images": article.get("images", []),
            "duration": len(script) / 4  # 估算时长（秒）
        }

    def adapt_for_xiaohongshu(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """适配为小红书内容"""
        title = article.get("title", "")
        content = article.get("content", "")

        # 提取要点
        points = self._extract_key_points(content)

        # 添加表情符号
        formatted_content = self._add_emojis(points)

        return {
            "title": title,
            "content": formatted_content,
            "tags": article.get("keywords", []),
            "images": article.get("images", [])
        }

    def adapt_for_douyin(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """适配为抖音内容"""
        title = article.get("title", "")
        content = article.get("content", "")

        # 生成短视频脚本（15-60秒）
        script = self._generate_short_video_script(title, content)

        return {
            "script": script,
            "duration": script.get("duration", 30),
            "scenes": script.get("scenes", []),
            "music_suggestion": "轻松愉快的背景音乐"
        }

    def _generate_voice_script(self, title: str, content: str) -> str:
        """生成视频号口播文案"""
        # 提取关键段落
        lines = content.split("\n")
        key_lines = [line for line in lines if line.strip() and not line.startswith("#")]

        # 限制长度
        script_lines = key_lines[:10]
        return "\n".join(script_lines)

    def _extract_key_points(self, content: str) -> List[str]:
        """提取文章要点"""
        lines = content.split("\n")
        points = []

        for line in lines:
            line = line.strip()
            if line and not line.startswith("#") and len(line) > 10:
                points.append(line)
                if len(points) >= 6:
                    break

        return points

    def _add_emojis(self, points: List[str]) -> str:
        """添加表情符号"""
        emojis = ["🏠", "📍", "💰", "[HOT]", "[SPARKLE]", "🌟", "[IDEA]", "[TARGET]"]

        formatted = []
        for i, point in enumerate(points):
            emoji = emojis[i % len(emojis)]
            formatted.append(f"{emoji} {point}")

        return "\n\n".join(formatted)

    def _generate_short_video_script(self, title: str,
                                      content: str) -> Dict[str, Any]:
        """生成短视频脚本"""
        return {
            "duration": 30,
            "scenes": [
                {
                    "time": "0-3s",
                    "visual": "标题画面 + 背景音乐",
                    "text": title
                },
                {
                    "time": "3-15s",
                    "visual": "相关图片/视频剪辑",
                    "text": content[:100]
                },
                {
                    "time": "15-25s",
                    "visual": "数据图表/项目展示",
                    "text": "核心观点"
                },
                {
                    "time": "25-30s",
                    "visual": "结尾画面 + 引导关注",
                    "text": "关注我们，获取更多房产资讯"
                }
            ]
        }
