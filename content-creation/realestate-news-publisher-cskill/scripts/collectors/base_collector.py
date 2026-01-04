# Base Collector Module
# 基础采集器模块

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from utils.http_client import HTTPClient
from utils.logger import get_logger

logger = get_logger(__name__)


class BaseCollector(ABC):
    """采集器基类"""

    def __init__(self, config: Dict[str, Any], http_client: HTTPClient = None):
        """
        初始化采集器

        Args:
            config: 采集器配置
            http_client: HTTP 客户端实例
        """
        self.config = config
        self.http_client = http_client or HTTPClient(
            timeout=config.get("timeout", 30),
            rate_limit_delay=config.get("rate_limit_delay", 2)
        )
        self.name = config.get("name", "Unknown")
        self.url = config.get("url", "")
        self.priority = config.get("priority", 5)
        self.enabled = config.get("enabled", True)

    @abstractmethod
    def collect(self, keywords: List[str] = None,
                days_back: int = 7) -> List[Dict[str, Any]]:
        """
        采集信息

        Args:
            keywords: 搜索关键词列表
            days_back: 回溯天数

        Returns:
            采集到的信息列表
        """
        pass

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """解析日期字符串"""
        date_formats = [
            "%Y-%m-%d",
            "%Y/%m/%d",
            "%Y年%m月%d日",
            "%Y-%m-%d %H:%M:%S",
            "%Y/%m/%d %H:%M:%S",
        ]

        for fmt in date_formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue

        logger.warning(f"无法解析日期: {date_str}")
        return None

    def _is_within_days(self, date: Optional[datetime],
                        days: int) -> bool:
        """检查日期是否在指定天数内"""
        if date is None:
            return True

        cutoff_date = datetime.now() - timedelta(days=days)
        return date >= cutoff_date

    def _create_item(self, title: str, url: str, content: str,
                     publish_date: Optional[datetime],
                     source: str, category: str,
                     priority: int = None) -> Dict[str, Any]:
        """
        创建标准化的信息项

        Args:
            title: 标题
            url: 来源链接
            content: 内容
            publish_date: 发布日期
            source: 来源
            category: 分类
            priority: 优先级

        Returns:
            标准化的信息项字典
        """
        return {
            "title": title.strip(),
            "url": url,
            "content": content.strip() if content else "",
            "publish_date": publish_date,
            "source": source,
            "category": category,
            "priority": priority or self.priority,
            "collected_at": datetime.now().isoformat()
        }

    def _extract_text(self, element) -> str:
        """提取元素的文本内容"""
        if element is None:
            return ""
        return element.get_text(separator=" ", strip=True)

    def clean_html(self, html: str) -> str:
        """清理 HTML，保留纯文本"""
        soup = BeautifulSoup(html, 'lxml')

        # 移除脚本和样式
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()

        # 获取文本
        text = soup.get_text(separator="\n")

        # 清理空白行
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return "\n".join(lines)
