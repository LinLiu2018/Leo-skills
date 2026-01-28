# Content Analyzer Module
# 内容分析模块

from typing import List, Dict, Any, Optional
import jieba
import re
from utils.logger import get_logger

logger = get_logger(__name__)


class ContentAnalyzer:
    """内容分析器"""

    def __init__(self, keywords_config: Dict[str, Any]):
        """
        初始化内容分析器

        Args:
            keywords_config: 关键词配置
        """
        self.keywords_config = keywords_config
        self.all_keywords = self._load_all_keywords()

    def _load_all_keywords(self) -> Dict[str, List[str]]:
        """加载所有关键词"""
        all_keywords = {}
        for category, keywords in self.keywords_config.items():
            if isinstance(keywords, dict):
                for subcategory, kw_list in keywords.items():
                    key = f"{category}_{subcategory}"
                    all_keywords[key] = kw_list
            elif isinstance(keywords, list):
                all_keywords[category] = keywords
        return all_keywords

    def analyze(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析单个信息项

        Args:
            item: 信息项字典

        Returns:
            分析结果字典
        """
        text = item.get("title", "") + " " + item.get("content", "")

        analysis = {
            "policy_points": self._extract_policy_points(text),
            "market_impact": self._analyze_market_impact(text),
            "trends": self._identify_trends(text),
            "sentiment": self._assess_sentiment(text),
            "detected_keywords": self._detect_keywords(text),
            "regions": self._detect_regions(text),
            "products": self._detect_products(text)
        }

        return analysis

    def _extract_policy_points(self, text: str) -> List[str]:
        """提取政策要点"""
        policy_points = []
        policy_keywords = self.keywords_config.get("policy_keywords", {})

        # 获取所有政策关键词
        primary = policy_keywords.get("primary", [])
        secondary = policy_keywords.get("secondary", [])
        all_policy_keywords = set(primary + secondary)

        # 使用正则表达式提取包含政策关键词的句子
        sentences = re.split(r'[。！？；]', text)
        for sentence in sentences:
            for keyword in all_policy_keywords:
                if keyword in sentence:
                    policy_points.append(sentence.strip())
                    break

        return policy_points[:5]  # 返回最多5个要点

    def _analyze_market_impact(self, text: str) -> str:
        """分析市场影响"""
        positive_keywords = self.keywords_config.get("positive_keywords", [])
        negative_keywords = self.keywords_config.get("negative_keywords", [])

        positive_count = sum(1 for kw in positive_keywords if kw in text)
        negative_count = sum(1 for kw in negative_keywords if kw in text)

        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        return "neutral"

    def _identify_trends(self, text: str) -> List[str]:
        """识别趋势"""
        trends = []
        trend_indicators = {
            "上涨": ["上涨", "涨幅", "攀升", "走高", "普涨"],
            "下跌": ["下跌", "跌幅", "下滑", "走低", "普跌"],
            "回暖": ["回暖", "复苏", "反弹", "升温"],
            "降温": ["降温", "遇冷", "下滑", "低迷"]
        }

        for trend, indicators in trend_indicators.items():
            if any(indicator in text for indicator in indicators):
                trends.append(trend)

        return trends

    def _assess_sentiment(self, text: str) -> str:
        """评估情感倾向"""
        impact = self._analyze_market_impact(text)

        sentiment_map = {
            "positive": "bullish",
            "negative": "bearish",
            "neutral": "neutral"
        }

        return sentiment_map.get(impact, "neutral")

    def _detect_keywords(self, text: str) -> List[str]:
        """检测文本中的关键词"""
        detected = []

        for category, keywords in self.all_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    detected.append(keyword)

        return list(set(detected))

    def _detect_regions(self, text: str) -> List[str]:
        """检测提到的区域"""
        regions = []
        regional_keywords = self.keywords_config.get("regional_keywords", {})

        cities = regional_keywords.get("cities", [])
        areas = regional_keywords.get("areas", [])

        for city in cities:
            if city in text:
                regions.append(city)

        for area in areas:
            if area in text:
                regions.append(area)

        return regions

    def _detect_products(self, text: str) -> List[str]:
        """检测提到的产品类型"""
        products = []
        product_keywords = self.keywords_config.get("product_keywords", {})

        primary = product_keywords.get("primary", [])
        secondary = product_keywords.get("secondary", [])

        for product in primary + secondary:
            if product in text:
                products.append(product)

        return products

    def batch_analyze(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """批量分析信息项"""
        results = []
        for item in items:
            try:
                analysis = self.analyze(item)
                item["analysis"] = analysis
                results.append(item)
            except Exception as e:
                logger.error(f"分析失败: {e}")
                continue
        return results
