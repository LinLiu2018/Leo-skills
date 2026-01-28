# Relevance Scorer Module
# 相关性评分模块

from typing import Dict, Any, List
from utils.logger import get_logger

logger = get_logger(__name__)


class RelevanceScorer:
    """相关性评分器"""

    def __init__(self, keywords_config: Dict[str, Any],
                 priority_config: Dict[str, int] = None,
                 source_config: Dict[str, int] = None):
        """
        初始化相关性评分器

        Args:
            keywords_config: 关键词配置
            priority_config: 优先级配置
            source_config: 来源可信度配置
        """
        self.keywords_config = keywords_config
        self.keyword_weights = keywords_config.get("keyword_weights", {})

        # 默认优先级配置
        self.priority_config = priority_config or {
            "policy": 10,
            "market": 7,
            "regional": 5,
            "product": 3
        }

        # 默认来源可信度配置
        self.source_config = source_config or {
            "government": 10,
            "news": 7,
            "industry": 5,
            "social": 3
        }

    def score(self, item: Dict[str, Any], analysis: Dict[str, Any] = None) -> float:
        """
        计算信息项的相关性得分

        Args:
            item: 信息项
            analysis: 已有的分析结果

        Returns:
            相关性得分 (0-1)
        """
        if analysis is None:
            from .content_analyzer import ContentAnalyzer
            analyzer = ContentAnalyzer(self.keywords_config)
            analysis = analyzer.analyze(item)

        # 计算各个维度的得分
        keyword_score = self._score_keywords(analysis)
        category_score = self._score_category(item)
        source_score = self._score_source(item)
        region_score = self._score_region(analysis)

        # 加权计算总分
        total_score = (
            keyword_score * 0.4 +
            category_score * 0.25 +
            source_score * 0.2 +
            region_score * 0.15
        )

        return round(min(total_score, 1.0), 3)

    def _score_keywords(self, analysis: Dict[str, Any]) -> float:
        """根据关键词评分"""
        detected_keywords = analysis.get("detected_keywords", [])
        if not detected_keywords:
            return 0.0

        # 计算关键词权重得分
        total_weight = 0
        for keyword in detected_keywords:
            # 查找关键词对应的权重
            weight = self._find_keyword_weight(keyword)
            total_weight += weight

        # 标准化到 0-1
        max_possible = len(detected_keywords) * 1.0
        return min(total_weight / max_possible, 1.0) if max_possible > 0 else 0.0

    def _find_keyword_weight(self, keyword: str) -> float:
        """查找关键词的权重"""
        for category, weight in self.keyword_weights.items():
            if keyword in str(self.keywords_config.get(category.replace("_keywords", ""), {})):
                return weight / 10.0  # 标准化到 0-1
        return 0.5  # 默认权重

    def _score_category(self, item: Dict[str, Any]) -> float:
        """根据分类评分"""
        category = item.get("category", "")
        priority = item.get("priority", self.priority_config.get(category, 5))

        # 标准化到 0-1
        return min(priority / 10.0, 1.0)

    def _score_source(self, item: Dict[str, Any]) -> float:
        """根据来源评分"""
        # 这里可以根据来源名称或类型评分
        source = item.get("source", "")

        # 简单判断来源类型
        if "政府" in source or "gov" in source.lower():
            source_type = "government"
        elif "新闻" in source or "news" in source.lower():
            source_type = "news"
        elif "研究院" in source or "research" in source.lower():
            source_type = "industry"
        else:
            source_type = "social"

        credibility = self.source_config.get(source_type, 5)
        return min(credibility / 10.0, 1.0)

    def _score_region(self, analysis: Dict[str, Any]) -> float:
        """根据区域相关性评分"""
        regions = analysis.get("regions", [])

        # 宁波及其区县得高分
        ningbo_regions = ["宁波", "余姚", "镇海", "奉化", "牟山", "九龙湖", "溪口"]
        has_ningbo_region = any(region in regions for region in ningbo_regions)

        if has_ningbo_region:
            return 1.0
        elif regions:
            return 0.5
        return 0.0

    def batch_score(self, items: List[Dict[str, Any]],
                    min_score: float = 0.6) -> List[Dict[str, Any]]:
        """
        批量评分并过滤

        Args:
            items: 信息项列表
            min_score: 最低得分阈值

        Returns:
            过滤后的信息项列表
        """
        scored_items = []

        for item in items:
            analysis = item.get("analysis")
            if not analysis:
                continue

            score = self.score(item, analysis)
            item["relevance_score"] = score

            if score >= min_score:
                scored_items.append(item)

        # 按得分排序
        scored_items.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)

        return scored_items
