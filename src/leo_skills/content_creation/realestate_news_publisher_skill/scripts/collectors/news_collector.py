# News Collector Module
# 新闻网站采集器模块

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from .base_collector import BaseCollector
from utils.logger import get_logger

logger = get_logger(__name__)


class NewsCollector(BaseCollector):
    """新闻网站信息采集器"""

    def __init__(self, config: Dict[str, Any], http_client=None):
        super().__init__(config, http_client)
        self.update_frequency = config.get("update_frequency", "hourly")

    def collect(self, keywords: List[str] = None,
                days_back: int = 7) -> List[Dict[str, Any]]:
        """采集新闻网站信息"""
        if not self.enabled:
            logger.info(f"新闻采集器 {self.name} 已禁用")
            return []

        logger.info(f"开始采集新闻网站: {self.name}")
        results = []

        try:
            response = self.http_client.get(self.url)
            if not response:
                logger.error(f"无法访问 {self.name}: {self.url}")
                return results

            soup = BeautifulSoup(response.text, 'lxml')
            selectors = self.config.get("selectors", {})
            items = self._extract_items(soup, selectors)

            for item in items:
                try:
                    detail = self._extract_detail(item)

                    if not self._is_within_days(detail.get("publish_date"), days_back):
                        continue

                    if keywords and not self._matches_keywords(detail, keywords):
                        continue

                    results.append(detail)

                except Exception as e:
                    logger.error(f"处理新闻项失败: {e}")
                    continue

            logger.info(f"从 {self.name} 采集到 {len(results)} 条新闻")

        except Exception as e:
            logger.error(f"采集新闻网站失败 {self.name}: {e}")

        return results

    def _extract_items(self, soup: BeautifulSoup, selectors: Dict[str, str]) -> List:
        """从页面提取新闻项列表"""
        list_selector = selectors.get("articles", "article, .news-item, .article-item")
        items = soup.select(list_selector)
        return items[:30]

    def _extract_detail(self, item) -> Dict[str, Any]:
        """从新闻项提取详细信息"""
        selectors = self.config.get("selectors", {})

        # 提取标题和链接
        title_elem = item.select_one("h2, h3, .title a, a")
        title = self._extract_text(title_elem) if title_elem else "无标题"

        relative_url = title_elem.get("href", "") if title_elem else ""
        full_url = urljoin(self.url, relative_url)

        # 提取日期
        date_elem = item.select_one(".date, .time, .publish-time, time")
        publish_date = None
        if date_elem:
            date_str = self._extract_text(date_elem)
            publish_date = self._parse_date(date_str)

        # 获取详细内容
        content = ""
        if full_url:
            content = self._fetch_content(full_url)

        return self._create_item(
            title=title,
            url=full_url,
            content=content,
            publish_date=publish_date,
            source=self.name,
            category="market"
        )

    def _fetch_content(self, url: str) -> str:
        """获取新闻详细内容"""
        try:
            response = self.http_client.get(url)
            if response:
                soup = BeautifulSoup(response.text, 'lxml')
                content_selectors = [
                    ".article-content",
                    ".content",
                    ".article-body",
                    "#articleContent",
                    "article"
                ]
                for selector in content_selectors:
                    elem = soup.select_one(selector)
                    if elem:
                        return self.clean_html(str(elem))
        except Exception as e:
            logger.warning(f"获取新闻详细内容失败 {url}: {e}")

        return ""

    def _matches_keywords(self, item: Dict[str, Any], keywords: List[str]) -> bool:
        """检查新闻是否匹配关键词"""
        text = (item.get("title", "") + " " + item.get("content", "")).lower()
        for keyword in keywords:
            if keyword.lower() in text:
                return True
        return False


def collect_xinhua_property(config: Dict[str, Any], keywords: List[str] = None) -> List[Dict[str, Any]]:
    """采集新华网房产频道"""
    config["name"] = "新华网房产"
    collector = NewsCollector(config)
    return collector.collect(keywords)


def collect_people_property(config: Dict[str, Any], keywords: List[str] = None) -> List[Dict[str, Any]]:
    """采集人民网房产频道"""
    config["name"] = "人民网房产"
    collector = NewsCollector(config)
    return collector.collect(keywords)


def collect_zhejiang_online(config: Dict[str, Any], keywords: List[str] = None) -> List[Dict[str, Any]]:
    """采集浙江在线房产"""
    config["name"] = "浙江在线"
    collector = NewsCollector(config)
    return collector.collect(keywords)


def collect_ningbo_daily(config: Dict[str, Any], keywords: List[str] = None) -> List[Dict[str, Any]]:
    """采集宁波日报房产"""
    config["name"] = "宁波日报"
    collector = NewsCollector(config)
    return collector.collect(keywords)
