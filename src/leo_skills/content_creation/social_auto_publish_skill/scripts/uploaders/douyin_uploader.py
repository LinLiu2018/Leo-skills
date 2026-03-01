# -*- coding: utf-8 -*-
"""
抖音上传器 - 基于 Playwright 自动化
参考: docs/reference/social-auto-upload/uploader/douyin_uploader/
"""

import logging
from typing import Dict, Optional
from playwright.async_api import async_playwright

logger = logging.getLogger(__name__)

DOUYIN_CREATOR_URL = "https://creator.douyin.com/creator-micro/content/upload"


async def upload_douyin(
    video_path: str,
    content: Dict[str, str],
    cookie_file: str,
) -> Optional[str]:
    """上传视频到抖音创作者平台

    Args:
        video_path: 视频文件路径
        content: 适配后的内容 (title, description, tags_text)
        cookie_file: Cookie 文件路径

    Returns:
        发布后的视频 URL（如果可获取）
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(storage_state=cookie_file)
        page = await context.new_page()

        try:
            await page.goto(DOUYIN_CREATOR_URL)
            await page.wait_for_load_state("networkidle")

            # 上传视频文件
            upload_input = page.locator('input[type="file"]')
            await upload_input.set_input_files(video_path)
            logger.info("视频文件已选择，等待上传...")

            # 等待上传完成
            await page.wait_for_selector(
                'text="重新上传"', timeout=300000
            )
            logger.info("视频上传完成")

            # 填写标题
            title_input = page.locator(
                '.notranslate[data-placeholder]'
            ).first
            await title_input.fill("")
            await title_input.fill(content["title"])

            # 填写描述和标签
            desc_area = page.locator(
                '.notranslate[data-placeholder]'
            ).nth(1)
            desc_text = f"{content['description']}\n{content['tags_text']}"
            await desc_area.fill(desc_text)

            # 点击发布
            publish_btn = page.locator('button:has-text("发布")')
            await publish_btn.click()

            # 等待发布完成
            await page.wait_for_url("**/manage**", timeout=30000)
            logger.info("抖音发布成功")

            return None  # 抖音不直接返回 URL

        except Exception as e:
            logger.error(f"抖音上传失败: {e}")
            raise
        finally:
            await browser.close()
