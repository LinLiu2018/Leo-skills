# Government Collector Module
# 政府网站采集器模块

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from .base_collector import BaseCollector
from utils.logger import get_logger

logger = get_logger(__name__)


class GovernmentCollector(BaseCollector):
    """政府网站信息采集器"""

    def __init__(self, config: Dict[str, Any], http_client=None):
        super().__init__(config, http_client)
        self.region = config.get("region", "ningbo")

    def collect(self, keywords: List[str] = None,
                days_back: int = 7) -> List[Dict[str, Any]]:
        """
        采集政府网站信息

        Args:
            keywords: 搜索关键词列表
            days_back: 回溯天数

        Returns:
            采集到的信息列表
        """
        if not self.enabled:
            logger.info(f"政府采集器 {self.name} 已禁用")
            return []

        logger.info(f"开始采集政府网站: {self.name}")
        results = []

        try:
            # 请求主页面
            response = self.http_client.get(self.url)
            if not response:
                logger.error(f"无法访问 {self.name}: {self.url}")
                return results

            # 解析 HTML
            soup = BeautifulSoup(response.text, 'lxml')

            # 根据配置的选择器提取信息
            selectors = self.config.get("selectors", {})
            items = self._extract_items(soup, selectors)

            # 处理每个信息项
            for item in items:
                try:
                    # 提取详细信息
                    detail = self._extract_detail(item)

                    # 检查日期
                    if not self._is_within_days(detail.get("publish_date"), days_back):
                        continue

                    # 检查关键词匹配
                    if keywords and not self._matches_keywords(detail, keywords):
                        continue

                    results.append(detail)

                except Exception as e:
                    logger.error(f"处理信息项失败: {e}")
                    continue

            logger.info(f"从 {self.name} 采集到 {len(results)} 条信息")

        except Exception as e:
            logger.error(f"采集政府网站失败 {self.name}: {e}")

        return results

    def _extract_items(self, soup: BeautifulSoup,
                       selectors: Dict[str, str]) -> List:
        """从页面提取信息项列表"""
        list_selector = selectors.get("list", "ul li, div.item")
        items = soup.select(list_selector)
        return items[:20]  # 限制返回数量

    def _extract_detail(self, item) -> Dict[str, Any]:
        """从信息项提取详细信息"""
        selectors = self.config.get("selectors", {})

        # 提取标题和链接
        title_elem = item.select_one(selectors.get("title", "a"))
        title = self._extract_text(title_elem) if title_elem else "无标题"

        # 构建完整 URL
        relative_url = title_elem.get("href", "") if title_elem else ""
        full_url = urljoin(self.url, relative_url)

        # 提取日期
        date_elem = item.select_one(selectors.get("date", ".date, .time, span.date"))
        publish_date = None
        if date_elem:
            date_str = self._extract_text(date_elem)
            publish_date = self._parse_date(date_str)

        # 尝试获取详细内容
        content = ""
        if full_url:
            content = self._fetch_content(full_url)

        return self._create_item(
            title=title,
            url=full_url,
            content=content,
            publish_date=publish_date,
            source=self.name,
            category="policy"
        )

    def _fetch_content(self, url: str) -> str:
        """获取详细页面内容"""
        try:
            response = self.http_client.get(url)
            if response:
                soup = BeautifulSoup(response.text, 'lxml')
                # 常见的内容选择器
                content_selectors = [
                    ".article-content",
                    ".content",
                    ".article-body",
                    "#content",
                    ".detail-content",
                    "article"
                ]
                for selector in content_selectors:
                    elem = soup.select_one(selector)
                    if elem:
                        return self.clean_html(str(elem))
        except Exception as e:
            logger.warning(f"获取详细内容失败 {url}: {e}")

        return ""

    def _matches_keywords(self, item: Dict[str, Any],
                          keywords: List[str]) -> bool:
        """检查信息是否匹配关键词"""
        text = (item.get("title", "") + " " + item.get("content", "")).lower()

        for keyword in keywords:
            if keyword.lower() in text:
                return True

        return False


def collect_ninghousing_bureau(config: Dict[str, Any],
                               keywords: List[str] = None) -> List[Dict[str, Any]]:
    """采集宁波市住建局信息"""
    config["name"] = "宁波市住建局"
    config["region"] = "ningbo"
    collector = GovernmentCollector(config)
    return collector.collect(keywords)


def collect_yuyao_gov(config: Dict[str, Any],
                      keywords: List[str] = None) -> List[Dict[str, Any]]:
    """采集余姚市政府信息"""
    config["name"] = "余姚市政府"
    config["region"] = "yuyao"
    collector = GovernmentCollector(config)
    return collector.collect(keywords)


def collect_zhenhai_gov(config: Dict[str, Any],
                        keywords: List[str] = None) -> List[Dict[str, Any]]:
    """采集镇海区政府信息"""
    config["name"] = "镇海区政府"
    config["region"] = "zhenhai"
    collector = GovernmentCollector(config)
    return collector.collect(keywords)


def collect_fenghua_gov(config: Dict[str, Any],
                        keywords: List[str] = None) -> List[Dict[str, Any]]:
    """采集奉化区政府信息"""
    config["name"] = "奉化区政府"
    config["region"] = "fenghua"
    collector = GovernmentCollector(config)
    return collector.collect(keywords)
