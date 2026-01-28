# Social Collector Module
# 社交媒体采集器模块

from typing import List, Dict, Any
from .base_collector import BaseCollector
from utils.logger import get_logger

logger = get_logger(__name__)


class SocialCollector(BaseCollector):
    """社交媒体信息采集器"""

    def __init__(self, config: Dict[str, Any], http_client=None):
        super().__init__(config, http_client)
        self.platform = config.get("platform", "unknown")

    def collect(self, keywords: List[str] = None,
                days_back: int = 7) -> List[Dict[str, Any]]:
        """采集社交媒体信息"""
        if not self.enabled:
            logger.info(f"社交媒体采集器 {self.name} 已禁用")
            return []

        logger.info(f"开始采集社交媒体: {self.name}")

        # 社交媒体通常需要 API 访问
        # 这里提供框架，实际实现需要对应平台的 API

        logger.warning(f"{self.name}: 需要 API 访问权限")

        return []


def collect_weibo_topics(config: Dict[str, Any], keywords: List[str] = None) -> List[Dict[str, Any]]:
    """采集微博房产话题"""
    config["name"] = "微博房产话题"
    config["platform"] = "weibo"
    collector = SocialCollector(config)
    return collector.collect(keywords)


def collect_zhihu_qa(config: Dict[str, Any], keywords: List[str] = None) -> List[Dict[str, Any]]:
    """采集知乎房产问答"""
    config["name"] = "知乎房产问答"
    config["platform"] = "zhihu"
    collector = SocialCollector(config)
    return collector.collect(keywords)
