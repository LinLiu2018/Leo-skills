"""
房地产新闻发布技能

自动采集房地产资讯，进行内容分析、去重、文章生成和多平台发布。
完整流程：采集 → 分析 → 去重 → 生成 → 发布。
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from leo_skills.core.base_executor import BaseExecutor

logger = logging.getLogger(__name__)


class RealEstateNewsPublisher(BaseExecutor):
    """房产资讯自动化发布技能。

    支持的操作：
        - run:       运行完整流程（采集→分析→生成→发布）
        - collect:   仅采集信息
        - analyze:   分析已采集的信息
        - generate:  生成文章
        - publish:   发布文章
    """

    def __init__(self) -> None:
        self.name = "realestate_news_publisher_skill"
        self._config: Optional[Dict[str, Any]] = None
        self._initialized = False

    # ------------------------------------------------------------------ #
    #  BaseExecutor 接口
    # ------------------------------------------------------------------ #

    def execute(
        self,
        action: str = "run",
        context: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = dict(context or {})
        params.update(kwargs)

        action_map = {
            "run": self._action_run,
            "collect": self._action_collect,
            "analyze": self._action_analyze,
            "generate": self._action_generate,
            "publish": self._action_publish,
        }

        handler = action_map.get(action)
        if handler is None:
            return {"status": "error", "message": f"未知操作: {action}"}
        return handler(params)

    # ------------------------------------------------------------------ #
    #  配置管理
    # ------------------------------------------------------------------ #

    def _load_config(self) -> Dict[str, Any]:
        """加载配置（惰性初始化）。"""
        if self._config is not None:
            return self._config

        config_path = Path(__file__).parent / "config" / "config.yaml"
        if config_path.exists():
            try:
                import yaml
                with open(config_path, "r", encoding="utf-8") as f:
                    self._config = yaml.safe_load(f) or {}
            except Exception as e:
                logger.warning(f"加载配置失败: {e}")
                self._config = {}
        else:
            self._config = self._default_config()
        return self._config

    @staticmethod
    def _default_config() -> Dict[str, Any]:
        """默认配置。"""
        return {
            "keywords": {
                "primary": ["房产", "楼市", "宁波", "购房"],
                "secondary": ["政策", "利率", "学区", "二手房"],
            },
            "sources": {
                "government_sources": [],
                "news_sources": [],
            },
            "content": {
                "min_relevance_score": 0.6,
                "articles_per_run": 3,
                "similarity_threshold": 0.85,
            },
            "platforms": ["wechat"],
        }

    def _get_all_keywords(self) -> List[str]:
        """从配置中汇总所有关键词。"""
        config = self._load_config()
        keywords_cfg = config.get("keywords", {})
        all_kw: List[str] = []
        for _category, kw_list in keywords_cfg.items():
            if isinstance(kw_list, list):
                all_kw.extend(kw_list)
            elif isinstance(kw_list, dict):
                for sub_list in kw_list.values():
                    if isinstance(sub_list, list):
                        all_kw.extend(sub_list)
        return list(set(all_kw))

    # ------------------------------------------------------------------ #
    #  动作：运行完整流程
    # ------------------------------------------------------------------ #

    def _action_run(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """运行完整流程：采集 → 分析 → 去重 → 生成 → 发布。"""
        start = datetime.now()
        keywords = params.get("keywords") or self._get_all_keywords()
        days_back = params.get("days_back", 7)
        do_publish = params.get("publish", True)

        try:
            # 1. 采集
            items = self._collect_items(keywords, days_back)
            if not items:
                return {"status": "warning", "message": "未采集到任何信息", "collected": 0}

            # 2. 分析 + 评分
            items = self._analyze_items(items)
            if not items:
                return {"status": "warning", "message": "没有信息通过筛选", "collected": 0}

            # 3. 去重
            items = self._deduplicate(items)

            # 4. 生成文章
            config = self._load_config()
            max_articles = config.get("content", {}).get("articles_per_run", 3)
            articles = self._generate_articles(items[:max_articles])
            if not articles:
                return {"status": "warning", "message": "没有生成任何文章"}

            result: Dict[str, Any] = {
                "status": "success",
                "collected": len(items),
                "generated": len(articles),
                "articles": [{"title": a.get("title", ""), "length": len(a.get("content", ""))} for a in articles],
            }

            # 5. 发布
            if do_publish:
                pub_results = self._publish_articles(articles, params.get("platforms"))
                result["publish_results"] = pub_results

            duration = (datetime.now() - start).total_seconds()
            result["duration_seconds"] = round(duration, 2)
            logger.info(f"流程完成: 采集 {len(items)} 条，生成 {len(articles)} 篇，耗时 {duration:.1f}s")
            return result

        except Exception as e:
            logger.error(f"运行流程失败: {e}")
            return {"status": "error", "error": str(e)}

    # ------------------------------------------------------------------ #
    #  动作：采集
    # ------------------------------------------------------------------ #

    def _action_collect(self, params: Dict[str, Any]) -> Dict[str, Any]:
        keywords = params.get("keywords") or self._get_all_keywords()
        days_back = params.get("days_back", 7)
        items = self._collect_items(keywords, days_back)
        return {
            "status": "success",
            "action": "collect",
            "items": len(items),
            "data": items,
        }

    def _collect_items(self, keywords: List[str], days_back: int = 7) -> List[Dict[str, Any]]:
        """从各来源采集信息。

        注意：实际采集需要配置数据源和网络请求。这里提供框架结构，
        真正的采集逻辑需要根据具体数据源实现 collectors。
        """
        logger.info(f"开始采集，关键词: {keywords[:5]}..., 回溯 {days_back} 天")
        config = self._load_config()
        sources = config.get("sources", {})
        all_items: List[Dict[str, Any]] = []

        # 尝试加载采集器模块（如果存在）
        try:
            from .scripts.publishers.multi_platform_publisher import MultiPlatformPublisher
            # 采集器已有实现时调用
        except ImportError:
            pass

        # 遍历政府网站源
        for source in sources.get("government_sources", []):
            if not source.get("enabled", True):
                continue
            try:
                items = self._collect_from_source(source, keywords)
                all_items.extend(items)
            except Exception as e:
                logger.error(f"采集 {source.get('name', '未知')} 失败: {e}")

        # 遍历新闻网站源
        for source in sources.get("news_sources", []):
            if not source.get("enabled", True):
                continue
            try:
                items = self._collect_from_source(source, keywords)
                all_items.extend(items)
            except Exception as e:
                logger.error(f"采集 {source.get('name', '未知')} 失败: {e}")

        logger.info(f"采集完成: 共 {len(all_items)} 条信息")
        return all_items

    @staticmethod
    def _collect_from_source(source: Dict[str, Any], keywords: List[str]) -> List[Dict[str, Any]]:
        """从单个来源采集（框架方法，需子类或配置实现）。"""
        # 这是一个框架方法。真正的实现应该使用 HTTP 客户端
        # 访问 source['url']，解析页面内容，过滤包含关键词的条目
        return []

    # ------------------------------------------------------------------ #
    #  动作：分析
    # ------------------------------------------------------------------ #

    def _action_analyze(self, params: Dict[str, Any]) -> Dict[str, Any]:
        items = params.get("items", [])
        analyzed = self._analyze_items(items)
        return {
            "status": "success",
            "action": "analyze",
            "input_count": len(items),
            "output_count": len(analyzed),
            "data": analyzed,
        }

    def _analyze_items(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """分析信息项：提取摘要、计算相关性分数。"""
        config = self._load_config()
        min_score = config.get("content", {}).get("min_relevance_score", 0.6)
        keywords = self._get_all_keywords()

        analyzed: List[Dict[str, Any]] = []
        for item in items:
            content = item.get("content", "") + " " + item.get("title", "")
            content_lower = content.lower()

            # 计算关键词命中率作为相关性分数
            hits = sum(1 for kw in keywords if kw.lower() in content_lower)
            score = min(1.0, hits / max(len(keywords) * 0.3, 1))

            if score >= min_score:
                item["relevance_score"] = round(score, 3)
                item["analysis"] = {
                    "keyword_hits": hits,
                    "content_length": len(content),
                    "category": self._categorize_content(content),
                }
                analyzed.append(item)

        # 按相关性排序
        analyzed.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        return analyzed

    @staticmethod
    def _categorize_content(content: str) -> str:
        """简单分类内容。"""
        content_lower = content.lower()
        if any(w in content_lower for w in ["政策", "调控", "限购", "利率"]):
            return "policy"
        elif any(w in content_lower for w in ["开盘", "认购", "销售", "成交"]):
            return "market"
        elif any(w in content_lower for w in ["学区", "教育", "学校"]):
            return "education"
        elif any(w in content_lower for w in ["装修", "户型", "配套"]):
            return "lifestyle"
        return "general"

    # ------------------------------------------------------------------ #
    #  去重
    # ------------------------------------------------------------------ #

    def _deduplicate(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """基于标题相似度去重。"""
        config = self._load_config()
        threshold = config.get("content", {}).get("similarity_threshold", 0.85)

        seen_titles: List[str] = []
        unique: List[Dict[str, Any]] = []

        for item in items:
            title = item.get("title", "")
            is_dup = False
            for seen in seen_titles:
                if self._title_similarity(title, seen) > threshold:
                    is_dup = True
                    break
            if not is_dup:
                seen_titles.append(title)
                unique.append(item)

        return unique

    @staticmethod
    def _title_similarity(a: str, b: str) -> float:
        """计算两个标题的字符级 Jaccard 相似度。"""
        if not a or not b:
            return 0.0
        set_a = set(a)
        set_b = set(b)
        intersection = set_a & set_b
        union = set_a | set_b
        return len(intersection) / len(union) if union else 0.0

    # ------------------------------------------------------------------ #
    #  动作：生成文章
    # ------------------------------------------------------------------ #

    def _action_generate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        items = params.get("items", [])
        articles = self._generate_articles(items)
        return {
            "status": "success",
            "action": "generate",
            "articles": len(articles),
            "data": articles,
        }

    def _generate_articles(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """根据采集信息生成文章。"""
        articles: List[Dict[str, Any]] = []
        for item in items:
            try:
                article = self._compose_article(item)
                articles.append(article)
                logger.info(f"文章生成成功: {article.get('title', '')}")
            except Exception as e:
                logger.error(f"文章生成失败: {e}")
        return articles

    @staticmethod
    def _compose_article(item: Dict[str, Any]) -> Dict[str, Any]:
        """从单条信息组装成文章。"""
        title = item.get("title", "房产资讯")
        content = item.get("content", "")
        source = item.get("source", "")
        category = item.get("analysis", {}).get("category", "general")

        # 构建文章结构
        article_content = f"# {title}\n\n"
        if source:
            article_content += f"> 来源: {source}\n\n"
        article_content += content
        article_content += f"\n\n---\n*由 Leo AI 房产资讯系统自动生成 | {datetime.now().strftime('%Y-%m-%d')}*\n"

        return {
            "title": title,
            "content": article_content,
            "source": source,
            "category": category,
            "generated_at": datetime.now().isoformat(),
        }

    # ------------------------------------------------------------------ #
    #  动作：发布
    # ------------------------------------------------------------------ #

    def _action_publish(self, params: Dict[str, Any]) -> Dict[str, Any]:
        articles = params.get("articles", [])
        platforms = params.get("platforms")
        results = self._publish_articles(articles, platforms)
        return {
            "status": "success",
            "action": "publish",
            "results": results,
        }

    def _publish_articles(
        self,
        articles: List[Dict[str, Any]],
        platforms: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """发布文章到指定平台。"""
        config = self._load_config()
        target_platforms = platforms or config.get("platforms", ["wechat"])

        results: Dict[str, Any] = {}
        for article in articles:
            title = article.get("title", "")
            article_result: Dict[str, Any] = {}

            for platform in target_platforms:
                try:
                    pub_result = self._publish_to_platform(article, platform)
                    article_result[platform] = pub_result
                except Exception as e:
                    logger.error(f"发布 {title} 到 {platform} 失败: {e}")
                    article_result[platform] = {"success": False, "error": str(e)}

            results[title] = article_result

        return results

    @staticmethod
    def _publish_to_platform(article: Dict[str, Any], platform: str) -> Dict[str, Any]:
        """发布到指定平台（框架方法）。

        实际发布需要配置各平台 API 凭证。
        """
        logger.info(f"准备发布到 {platform}: {article.get('title', '')}")
        # 实际实现需要调用各平台 API
        # 这里返回待实现状态
        return {
            "success": False,
            "platform": platform,
            "message": f"平台 {platform} 的发布接口需要配置 API 凭证",
        }


__all__ = ["RealEstateNewsPublisher"]
