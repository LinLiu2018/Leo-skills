# -*- coding: utf-8 -*-
"""
小红书上传器 - 基于 Playwright 自动化
参考: docs/reference/social-auto-upload/uploader/xhs_uploader/
"""

import logging
from typing import Dict, List, Optional
from playwright.async_api import async_playwright

logger = logging.getLogger(__name__)

XHS_CREATOR_URL = "https://creator.xiaohongshu.com/publish/publish"


async def upload_xhs(
    video_path: str,
    content: Dict[str, str],
    cookie_file: str,
) -> Optional[str]:
    """上传视频到小红书

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
            await page.goto(XHS_CREATOR_URL)
            await page.wait_for_load_state("networkidle")

            # 切换到视频标签
            video_tab = page.locator('text="上传视频"')
            if await video_tab.count() > 0:
                await video_tab.click()

            # 上传视频
            upload_input = page.locator('input[type="file"]')
            await upload_input.set_input_files(video_path)
            logger.info("小红书: 视频文件已选择")

            # 等待上传
            await page.wait_for_timeout(15000)

            # 填写标题
            title_input = page.locator('input[placeholder*="标题"]').first
            if await title_input.count() > 0:
                await title_input.fill(content["title"])

            # 填写描述
            desc_area = page.locator('[contenteditable="true"]').first
            if await desc_area.count() > 0:
                desc_text = f"{content['description']}\n{content['tags_text']}"
                await desc_area.fill(desc_text)

            # 点击发布
            publish_btn = page.locator('button:has-text("发布")')
            await publish_btn.click()

            await page.wait_for_timeout(5000)
            logger.info("小红书发布成功")
            return None

        except Exception as e:
            logger.error(f"小红书上传失败: {e}")
            raise
        finally:
            await browser.close()


async def upload_xhs_note(
    images: List[str],
    content: Dict[str, str],
    cookie_file: str = "",
) -> Optional[str]:
    """上传图文笔记到小红书

    Args:
        images: 图片路径列表
        content: 适配后的内容
        cookie_file: Cookie 文件路径

    Returns:
        发布后的 URL
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            storage_state=cookie_file if cookie_file else None
        )
        page = await context.new_page()

        try:
            await page.goto(XHS_CREATOR_URL)
            await page.wait_for_load_state("networkidle")

            # 上传图片
            upload_input = page.locator('input[type="file"]')
            await upload_input.set_input_files(images)
            logger.info(f"小红书: 已选择 {len(images)} 张图片")

            await page.wait_for_timeout(10000)

            # 填写标题
            title_input = page.locator('input[placeholder*="标题"]').first
            if await title_input.count() > 0:
                await title_input.fill(content["title"])

            # 填写正文
            desc_area = page.locator('[contenteditable="true"]').first
            if await desc_area.count() > 0:
                desc_text = f"{content['description']}\n{content['tags_text']}"
                await desc_area.fill(desc_text)

            # 发布
            publish_btn = page.locator('button:has-text("发布")')
            await publish_btn.click()

            await page.wait_for_timeout(5000)
            logger.info("小红书图文笔记发布成功")
            return None

        except Exception as e:
            logger.error(f"小红书图文上传失败: {e}")
            raise
        finally:
            await browser.close()
