# WeChat Publisher Module
# 微信公众号发布模块

from typing import Dict, Any, Optional
from utils.logger import get_logger

logger = get_logger(__name__)


class WeChatPublisher:
    """微信公众号发布器"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化微信发布器

        Args:
            config: 微信配置
        """
        self.config = config
        self.app_id = config.get("app_id", "")
        self.app_secret = config.get("app_secret", "")
        self.account_id = config.get("account_id", "")
        self.auto_publish = config.get("auto_publish", False)
        self.create_as_draft = config.get("create_as_draft", True)

        # 初始化微信客户端
        self._init_client()

    def _init_client(self):
        """初始化微信客户端"""
        try:
            from wechatpy import WeChatClient
            self.client = WeChatClient(
                appid=self.app_id,
                appsecret=self.app_secret
            )
            logger.info("微信客户端初始化成功")
        except ImportError:
            logger.warning("wechatpy 未安装，微信发布功能不可用")
            self.client = None
        except Exception as e:
            logger.error(f"微信客户端初始化失败: {e}")
            self.client = None

    def publish(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        发布文章到微信公众号

        Args:
            article: 文章数据

        Returns:
            发布结果
        """
        if not self.client:
            logger.error("微信客户端未初始化")
            return {"success": False, "error": "微信客户端未初始化"}

        try:
            # 创建文章
            result = self._create_article(article)

            if result.get("success"):
                logger.info(f"文章 '{article.get('title', '')}' 发布成功")
            else:
                logger.error(f"文章发布失败: {result.get('error', '')}")

            return result

        except Exception as e:
            logger.error(f"发布文章时发生错误: {e}")
            return {"success": False, "error": str(e)}

    def _create_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """创建文章"""
        try:
            # 准备文章数据
            articles_data = [{
                "title": article.get("title", ""),
                "author": article.get("author", "房产资讯"),
                "digest": article.get("summary", "")[:100],
                "content": self._format_content(article.get("content", "")),
                "content_source_url": article.get("source_url", ""),
                "thumb_media_id": article.get("thumb_media_id", ""),
                "show_cover_pic": 1,
                "need_open_comment": 1,
                "only_fans_can_comment": 0
            }]

            # 创建草稿
            if self.create_as_draft:
                result = self.client.draft.add_articles(articles_data)
                media_id = result.get("media_id", "")

                # 如果设置为自动发布，则发布文章
                if self.auto_publish and media_id:
                    publish_result = self.client.draft.auto_post_id_to_media_id(media_id)
                    return {
                        "success": True,
                        "media_id": media_id,
                        "published": True,
                        "publish_id": publish_result.get("publish_id", "")
                    }

                return {
                    "success": True,
                    "media_id": media_id,
                    "published": False,
                    "message": "已创建为草稿"
                }

            # 直接发布
            else:
                result = self.client.material.add_articles(articles_data)
                return {
                    "success": True,
                    "media_id": result.get("media_id", ""),
                    "published": True
                }

        except Exception as e:
            logger.error(f"创建文章失败: {e}")
            return {"success": False, "error": str(e)}

    def _format_content(self, content: str) -> str:
        """格式化内容为微信富文本格式"""
        # 将 Markdown 转换为 HTML
        html_content = self._markdown_to_html(content)

        # 添加微信样式
        styled_content = f"""
        <section style="font-family: -apple-system, BlinkMacSystemFont, 'Helvetica Neue', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif; font-size: 16px; line-height: 1.8; color: #333; padding: 20px;">
            {html_content}
        </section>
        """

        return styled_content

    def _markdown_to_html(self, markdown: str) -> str:
        """简单的 Markdown 转 HTML"""
        html = markdown

        # 标题转换
        html = html.replace("### ", "<h3 style='margin: 20px 0 10px; font-size: 18px;'>").replace("\n", "</h3>\n", 1)
        html = html.replace("## ", "<h2 style='margin: 25px 0 15px; font-size: 20px;'>").replace("\n", "</h2>\n", 1)
        html = html.replace("# ", "<h1 style='margin: 30px 0 20px; font-size: 24px;'>").replace("\n", "</h1>\n", 1)

        # 粗体
        html = html.replace("**", "<strong>", 1).replace("**", "</strong>", 1)

        # 列表
        lines = html.split("\n")
        formatted_lines = []
        in_list = False

        for line in lines:
            if line.strip().startswith("- "):
                if not in_list:
                    formatted_lines.append("<ul style='margin: 10px 0; padding-left: 20px;'>")
                    in_list = True
                formatted_lines.append(f"<li style='margin: 5px 0;'>{line.strip()[2:]}</li>")
            else:
                if in_list:
                    formatted_lines.append("</ul>")
                    in_list = False
                formatted_lines.append(f"<p style='margin: 10px 0;'>{line}</p>")

        if in_list:
            formatted_lines.append("</ul>")

        return "\n".join(formatted_lines)

    def upload_media(self, file_path: str, media_type: str = "image") -> Optional[str]:
        """
        上传媒体文件

        Args:
            file_path: 文件路径
            media_type: 媒体类型 (image, voice, video, thumb)

        Returns:
            media_id
        """
        if not self.client:
            logger.error("微信客户端未初始化")
            return None

        try:
            with open(file_path, "rb") as f:
                result = self.client.material.add(material_type, f)
                media_id = result.get("media_id", "")
                logger.info(f"媒体文件上传成功: {media_id}")
                return media_id

        except Exception as e:
            logger.error(f"上传媒体文件失败: {e}")
            return None

    def schedule_article(self, article: Dict[str, Any],
                         publish_time: str) -> Dict[str, Any]:
        """
        定时发布文章

        Args:
            article: 文章数据
            publish_time: 发布时间 (Unix 时间戳)

        Returns:
            发布结果
        """
        # 目前微信公众号API不支持直接定时发布
        # 这里提供一个框架，实际需要配合定时任务使用
        logger.info(f"文章 '{article.get('title', '')}' 已加入定时发布队列: {publish_time}")

        return {
            "success": True,
            "scheduled": True,
            "publish_time": publish_time
        }
