# -*- coding: utf-8 -*-
"""
视频号上传器 - 基于 Playwright 自动化
参考: docs/reference/social-auto-upload/uploader/tencent_uploader/
"""

import logging
from typing import Dict, Optional
from playwright.async_api import async_playwright

logger = logging.getLogger(__name__)

SHIPINHAO_URL = "https://channels.weixin.qq.com/platform/post/create"


async def upload_shipinhao(
    video_path: str,
    content: Dict[str, str],
    cookie_file: str,
) -> Optional[str]:
    """上传视频到微信视频号

    Args:
        video_path: 视频文件路径
        content: 适配后的内容
        cookie_file: Cookie 文件路径

    Returns:
        发布后的 URL
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(storage_state=cookie_file)
        page = await context.new_page()

        try:
            await page.goto(SHIPINHAO_URL)
            await page.wait_for_load_state("networkidle")

            # 上传视频
            upload_input = page.locator('input[type="file"]')
            await upload_input.set_input_files(video_path)
            logger.info("视频号: 视频文件已选择")

            # 等待上传完成
            await page.wait_for_timeout(10000)

            # 填写描述
            desc_area = page.locator("textarea").first
            if desc_area:
                desc_text = f"{content['title']}\n{content['description']}\n{content['tags_text']}"
                await desc_area.fill(desc_text)

            # 点击发表
            publish_btn = page.locator('button:has-text("发表")')
            await publish_btn.click()

            await page.wait_for_timeout(5000)
            logger.info("视频号发布成功")
            return None

        except Exception as e:
            logger.error(f"视频号上传失败: {e}")
            raise
        finally:
            await browser.close()
