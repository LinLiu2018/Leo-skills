# -*- coding: utf-8 -*-
"""
多平台自动发布技能 - 核心模块
基于 social-auto-upload 集成，支持抖音/视频号/小红书等平台
"""

import os
import json
import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

import yaml

logger = logging.getLogger(__name__)

SKILL_DIR = Path(__file__).parent.resolve()
CONFIG_DIR = SKILL_DIR / "config"
COOKIES_DIR = SKILL_DIR / "cookies"
LOGS_DIR = SKILL_DIR / "logs"


class ContentAdapter:
    """内容适配器 - 根据平台特性自动调整内容"""

    # 平台风格模板
    PLATFORM_STYLES = {
        "douyin": {
            "title_max": 30,
            "style": "钩子开头，制造悬念，引导看完",
            "emoji": False,
            "tag_prefix": "#",
            "tag_max": 5,
        },
        "shipinhao": {
            "title_max": 20,
            "style": "建立信任感，专业深度内容",
            "emoji": False,
            "tag_prefix": "#",
            "tag_max": 3,
        },
        "xiaohongshu": {
            "title_max": 20,
            "style": "种草风格，多用emoji，亲切口吻",
            "emoji": True,
            "tag_prefix": "#",
            "tag_max": 10,
        },
        "xianyu": {
            "title_max": 30,
            "style": "直接给价格和卖点，简洁明了",
            "emoji": False,
            "tag_prefix": "",
            "tag_max": 5,
        },
    }

    @classmethod
    def adapt(
        cls,
        platform: str,
        title: str,
        description: str,
        tags: List[str],
    ) -> Dict[str, str]:
        """根据平台适配内容"""
        style = cls.PLATFORM_STYLES.get(platform, cls.PLATFORM_STYLES["douyin"])

        # 截断标题
        adapted_title = title[: style["title_max"]]

        # 适配标签
        prefix = style["tag_prefix"]
        adapted_tags = [
            f"{prefix}{t}" for t in tags[: style["tag_max"]]
        ]

        # 适配描述
        adapted_desc = description
        if style["emoji"] and platform == "xiaohongshu":
            adapted_desc = cls._add_xhs_emojis(description)

        return {
            "title": adapted_title,
            "description": adapted_desc,
            "tags": adapted_tags,
            "tags_text": " ".join(adapted_tags),
        }

    @staticmethod
    def _add_xhs_emojis(text: str) -> str:
        """为小红书内容添加 emoji"""
        emoji_map = {
            "推荐": "💯推荐",
            "别墅": "🏡别墅",
            "度假": "🌴度假",
            "养老": "🏖️养老",
            "实拍": "📸实拍",
            "价格": "💰价格",
            "交通": "🚗交通",
            "环境": "🌿环境",
        }
        for keyword, replacement in emoji_map.items():
            text = text.replace(keyword, replacement, 1)
        return text


class PublishResult:
    """发布结果"""

    def __init__(self, platform: str, success: bool, message: str = "", url: str = ""):
        self.platform = platform
        self.success = success
        self.message = message
        self.url = url
        self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "platform": self.platform,
            "success": self.success,
            "message": self.message,
            "url": self.url,
            "timestamp": self.timestamp,
        }


class SocialAutoPublisher:
    """多平台自动发布器

    集成 social-auto-upload 项目，通过 Playwright 浏览器自动化
    实现视频/图文内容的多平台自动发布。

    支持平台: 抖音、视频号、小红书、快手、B站、闲鱼
    """

    def __init__(self, config_path: Optional[str] = None):
        """初始化发布器

        Args:
            config_path: 配置文件路径，默认使用 config/config.yaml
        """
        if config_path is None:
            config_path = str(CONFIG_DIR / "config.yaml")

        with open(config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)

        self.platforms_config = self.config.get("platforms", {})
        self.publish_strategy = self.config.get("publish_strategy", {})

        # 确保目录存在
        COOKIES_DIR.mkdir(exist_ok=True)
        LOGS_DIR.mkdir(exist_ok=True)

        # 上传器注册表
        self._uploaders: Dict[str, Any] = {}
        self._init_uploaders()

    def _init_uploaders(self):
        """初始化各平台上传器（延迟加载）"""
        # 参考实现路径
        sau_path = Path(SKILL_DIR).parent.parent.parent.parent / "docs" / "reference" / "social-auto-upload"

        for platform, cfg in self.platforms_config.items():
            if cfg.get("enabled", False):
                self._uploaders[platform] = {
                    "config": cfg,
                    "sau_path": sau_path,
                    "loaded": False,
                }
                logger.info(f"已注册平台: {platform}")

    def get_enabled_platforms(self) -> List[str]:
        """获取已启用的平台列表"""
        return [p for p, cfg in self.platforms_config.items() if cfg.get("enabled")]

    async def check_cookie(self, platform: str) -> bool:
        """检查平台 Cookie 是否有效

        Args:
            platform: 平台名称

        Returns:
            Cookie 是否有效
        """
        cfg = self.platforms_config.get(platform, {})
        cookie_file = COOKIES_DIR / cfg.get("cookie_file", f"{platform}_cookie.json")

        if not cookie_file.exists():
            logger.warning(f"{platform} Cookie 文件不存在: {cookie_file}")
            return False

        # 检查文件是否过期（7天）
        mtime = datetime.fromtimestamp(cookie_file.stat().st_mtime)
        age_days = (datetime.now() - mtime).days
        if age_days > 7:
            logger.warning(f"{platform} Cookie 已过期 ({age_days} 天)")
            return False

        return True

    async def login_platform(self, platform: str) -> bool:
        """登录平台（打开浏览器扫码）

        Args:
            platform: 平台名称

        Returns:
            登录是否成功
        """
        logger.info(f"正在打开 {platform} 登录页面，请扫码登录...")

        try:
            from playwright.async_api import async_playwright

            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=False)
                context = await browser.new_context()
                page = await context.new_page()

                # 各平台登录 URL
                login_urls = {
                    "douyin": "https://creator.douyin.com/",
                    "shipinhao": "https://channels.weixin.qq.com/",
                    "xiaohongshu": "https://creator.xiaohongshu.com/",
                    "kuaishou": "https://cp.kuaishou.com/",
                    "xianyu": "https://www.goofish.com/",
                }

                url = login_urls.get(platform)
                if not url:
                    logger.error(f"不支持的平台: {platform}")
                    return False

                await page.goto(url)
                # 等待用户扫码登录（最多等 120 秒）
                logger.info("请在浏览器中完成登录，等待最多 120 秒...")
                await page.wait_for_timeout(120000)

                # 保存 Cookie
                cookie_file = COOKIES_DIR / f"{platform}_cookie.json"
                storage = await context.storage_state()
                with open(cookie_file, "w", encoding="utf-8") as f:
                    json.dump(storage, f, ensure_ascii=False, indent=2)

                logger.info(f"{platform} 登录成功，Cookie 已保存")
                await browser.close()
                return True

        except Exception as e:
            logger.error(f"{platform} 登录失败: {e}")
            return False

    def publish_video(
        self,
        video_path: str,
        title: str,
        description: str,
        tags: Optional[List[str]] = None,
        platforms: Optional[List[str]] = None,
    ) -> List[PublishResult]:
        """发布视频到多个平台

        Args:
            video_path: 视频文件路径
            title: 视频标题
            description: 视频描述
            tags: 标签列表
            platforms: 目标平台列表，None 表示所有已启用平台

        Returns:
            各平台发布结果列表
        """
        if tags is None:
            tags = []
        if platforms is None:
            platforms = self.get_enabled_platforms()

        results = []
        for platform in platforms:
            adapted = ContentAdapter.adapt(platform, title, description, tags)
            result = asyncio.run(
                self._upload_video(platform, video_path, adapted)
            )
            results.append(result)
            self._log_result(result)

        return results

    def publish_note(
        self,
        images: List[str],
        title: str,
        content: str,
        tags: Optional[List[str]] = None,
        platform: str = "xiaohongshu",
    ) -> PublishResult:
        """发布图文笔记（主要用于小红书）

        Args:
            images: 图片路径列表
            title: 标题
            content: 正文内容
            tags: 标签列表
            platform: 目标平台

        Returns:
            发布结果
        """
        if tags is None:
            tags = []

        adapted = ContentAdapter.adapt(platform, title, content, tags)
        result = asyncio.run(
            self._upload_note(platform, images, adapted)
        )
        self._log_result(result)
        return result

    async def _upload_video(
        self, platform: str, video_path: str, content: Dict[str, str]
    ) -> PublishResult:
        """上传视频到指定平台（内部方法）"""
        try:
            if not await self.check_cookie(platform):
                return PublishResult(
                    platform=platform,
                    success=False,
                    message="Cookie 无效，请先登录",
                )

            cookie_file = str(
                COOKIES_DIR / self.platforms_config[platform].get(
                    "cookie_file", f"{platform}_cookie.json"
                )
            )

            # 根据平台调用对应的上传器
            if platform == "douyin":
                from .scripts.uploaders.douyin_uploader import upload_douyin
                url = await upload_douyin(video_path, content, cookie_file)
            elif platform == "shipinhao":
                from .scripts.uploaders.shipinhao_uploader import upload_shipinhao
                url = await upload_shipinhao(video_path, content, cookie_file)
            elif platform == "xiaohongshu":
                from .scripts.uploaders.xhs_uploader import upload_xhs
                url = await upload_xhs(video_path, content, cookie_file)
            else:
                return PublishResult(
                    platform=platform,
                    success=False,
                    message=f"平台 {platform} 上传器未实现",
                )

            return PublishResult(
                platform=platform, success=True, message="发布成功", url=url or ""
            )

        except Exception as e:
            logger.error(f"上传到 {platform} 失败: {e}")
            return PublishResult(
                platform=platform, success=False, message=str(e)
            )

    async def _upload_note(
        self, platform: str, images: List[str], content: Dict[str, str]
    ) -> PublishResult:
        """上传图文到指定平台（内部方法）"""
        try:
            if not await self.check_cookie(platform):
                return PublishResult(
                    platform=platform,
                    success=False,
                    message="Cookie 无效，请先登录",
                )

            # 目前仅小红书支持图文
            if platform == "xiaohongshu":
                from .scripts.uploaders.xhs_uploader import upload_xhs_note
                url = await upload_xhs_note(images, content)
                return PublishResult(
                    platform=platform, success=True, message="发布成功", url=url or ""
                )

            return PublishResult(
                platform=platform,
                success=False,
                message=f"平台 {platform} 不支持图文发布",
            )

        except Exception as e:
            logger.error(f"上传图文到 {platform} 失败: {e}")
            return PublishResult(
                platform=platform, success=False, message=str(e)
            )

    def _log_result(self, result: PublishResult):
        """记录发布结果到日志文件"""
        log_file = LOGS_DIR / f"publish_{datetime.now().strftime('%Y%m%d')}.jsonl"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(result.to_dict(), ensure_ascii=False) + "\n")

    def get_publish_history(self, days: int = 7) -> List[Dict[str, Any]]:
        """获取发布历史

        Args:
            days: 查询最近几天的记录

        Returns:
            发布记录列表
        """
        records = []
        for i in range(days):
            date = datetime.now().replace(hour=0, minute=0, second=0)
            date_str = date.strftime("%Y%m%d")
            log_file = LOGS_DIR / f"publish_{date_str}.jsonl"
            if log_file.exists():
                with open(log_file, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip():
                            records.append(json.loads(line))
        return records
