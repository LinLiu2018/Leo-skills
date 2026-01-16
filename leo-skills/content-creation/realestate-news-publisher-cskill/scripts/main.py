# Real Estate News Publisher - Main Entry Point
# 房产资讯自动化发布代理 - 主程序入口

import sys
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.config_loader import ConfigLoader
from utils.logger import get_logger, Logger
from utils.http_client import HTTPClient

from collectors.government_collector import (
    collect_ninghousing_bureau,
    collect_yuyao_gov,
    collect_zhenhai_gov,
    collect_fenghua_gov
)
from collectors.news_collector import (
    collect_xinhua_property,
    collect_people_property,
    collect_zhejiang_online,
    collect_ningbo_daily
)
from analyzers.content_analyzer import ContentAnalyzer
from analyzers.relevance_scorer import RelevanceScorer
from analyzers.deduplicator import Deduplicator
from generators.article_generator import ArticleGenerator
from publishers.wechat_publisher import WeChatPublisher
from publishers.multi_platform_publisher import MultiPlatformPublisher
from trackers.analytics_collector import AnalyticsCollector
from trackers.optimizer import Optimizer



from core.evolution import EvolvableSkill
class RealEstateNewsPublisher:
    """房产资讯自动化发布代理"""

    def __init__(self, config_path: str = None):

        super().__init__(
            skill_name="realestate-news-publisher-cskill",
            config_path=str(Path(__file__).parent.parent / "config" / "config.yaml")
        )
        """
        初始化发布代理

        Args:
            config_path: 配置文件路径
        """
        # 加载配置
        self.config_loader = ConfigLoader(config_path)
        self.config = self.config_loader.config

        # 设置日志
        log_config = self.config_loader.logging_config
        self.logger = Logger()
        self.logger.setup(
            log_file=log_config.get("file"),
            level=log_config.get("level", "INFO")
        )
        self.logger = get_logger("realestate_publisher")

        self.logger.info("=" * 60)
        self.logger.info("房产资讯自动化发布代理启动")
        self.logger.info("=" * 60)

        # 初始化组件
        self._init_components()

    def _init_components(self):
        """初始化各个组件"""
        # HTTP 客户端
        http_config = self.config_loader.http_config
        self.http_client = HTTPClient(
            timeout=http_config.get("timeout", 30),
            max_retries=http_config.get("max_retries", 3),
            retry_delay=http_config.get("retry_delay", 5),
            user_agent=http_config.get("user_agent"),
            rate_limit_delay=http_config.get("rate_limit_delay", 2)
        )

        # 分析器
        self.content_analyzer = ContentAnalyzer(
            self.config_loader.keywords
        )

        self.relevance_scorer = RelevanceScorer(
            self.config_loader.keywords,
            self.config.get("priority"),
            self.config.get("source_credibility")
        )

        self.deduplicator = Deduplicator(
            similarity_threshold=0.85
        )

        # 生成器
        self.article_generator = ArticleGenerator(
            self.config_loader.ai_config,
            self.config_loader.content_config,
            self.config_loader.keywords,
            self.config.get("projects", [])
        )

        # 发布器
        self.publisher = MultiPlatformPublisher(self.config_loader.wechat_config)

        # 追踪器
        self.analytics = AnalyticsCollector(self.config)
        self.optimizer = Optimizer(self.config)

        self.logger.info("所有组件初始化完成")

    def collect(self, keywords: List[str] = None,
                days_back: int = 7) -> List[Dict[str, Any]]:
        """
        采集信息

        Args:
            keywords: 搜索关键词
            days_back: 回溯天数

        Returns:
            采集到的信息列表
        """
        self.logger.info("开始信息采集...")

        all_items = []
        sources_config = self.config_loader.sources

        # 获取所有关键词
        if keywords is None:
            keywords = self._get_all_keywords()

        # 采集政府网站
        for source in sources_config.get("government_sources", []):
            if not source.get("enabled", True):
                continue

            try:
                if "ningbo" in source.get("name", "").lower():
                    items = collect_ninghousing_bureau(source, keywords)
                elif "yuyao" in source.get("name", "").lower():
                    items = collect_yuyao_gov(source, keywords)
                elif "zhenhai" in source.get("name", "").lower():
                    items = collect_zhenhai_gov(source, keywords)
                elif "fenghua" in source.get("name", "").lower():
                    items = collect_fenghua_gov(source, keywords)
                else:
                    continue

                all_items.extend(items)
            except Exception as e:
                self.logger.error(f"采集 {source.get('name')} 失败: {e}")

        # 采集新闻网站
        for source in sources_config.get("news_sources", []):
            if not source.get("enabled", True):
                continue

            try:
                if "xinhua" in source.get("name", "").lower():
                    items = collect_xinhua_property(source, keywords)
                elif "people" in source.get("name", "").lower():
                    items = collect_people_property(source, keywords)
                elif "zhejiang" in source.get("name", "").lower():
                    items = collect_zhejiang_online(source, keywords)
                elif "ningbo" in source.get("name", "").lower() and "daily" in source.get("name", "").lower():
                    items = collect_ningbo_daily(source, keywords)
                else:
                    continue

                all_items.extend(items)
            except Exception as e:
                self.logger.error(f"采集 {source.get('name')} 失败: {e}")

        self.logger.info(f"信息采集完成，共获取 {len(all_items)} 条信息")
        return all_items

    def _get_all_keywords(self) -> List[str]:
        """获取所有关键词"""
        keywords_config = self.config_loader.keywords
        all_keywords = []

        for category, keywords in keywords_config.items():
            if isinstance(keywords, dict):
                for kw_list in keywords.values():
                    all_keywords.extend(kw_list)
            elif isinstance(keywords, list):
                all_keywords.extend(keywords)

        return list(set(all_keywords))

    def analyze(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        分析信息

        Args:
            items: 信息列表

        Returns:
            分析后的信息列表
        """
        self.logger.info("开始内容分析...")

        # 内容分析
        items = self.content_analyzer.batch_analyze(items)

        # 相关性评分
        content_config = self.config_loader.content_config
        min_score = content_config.get("min_relevance_score", 0.6)
        items = self.relevance_scorer.batch_score(items, min_score)

        self.logger.info(f"内容分析完成，筛选后剩余 {len(items)} 条信息")
        return items

    def generate(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        生成文章

        Args:
            items: 信息列表

        Returns:
            生成的文章列表
        """
        self.logger.info("开始文章生成...")

        content_config = self.config_loader.content_config
        max_articles = content_config.get("articles_per_run", 3)

        # 限制文章数量
        items = items[:max_articles]

        articles = []
        for item in items:
            try:
                analysis = item.get("analysis", {})
                article = self.article_generator.generate(item, analysis)
                articles.append(article)
                self.logger.info(f"文章生成成功: {article.get('title', '')}")
            except Exception as e:
                self.logger.error(f"文章生成失败: {e}")
                continue

        self.logger.info(f"文章生成完成，共生成 {len(articles)} 篇")
        return articles

    def publish(self, articles: List[Dict[str, Any]],
                platforms: List[str] = None) -> Dict[str, Any]:
        """
        发布文章

        Args:
            articles: 文章列表
            platforms: 平台列表

        Returns:
            发布结果
        """
        self.logger.info("开始文章发布...")

        results = {}
        for article in articles:
            try:
                result = self.publisher.publish_to_all(article, platforms)
                results[article.get("title", "")] = result

                if result.get("wechat", {}).get("success"):
                    self.logger.info(f"文章发布成功: {article.get('title', '')}")
                else:
                    self.logger.warning(f"文章发布失败: {article.get('title', '')}")

            except Exception as e:
                self.logger.error(f"文章发布异常: {e}")
                results[article.get("title", "")] = {"success": False, "error": str(e)}

        return results

    def _execute_core(self, keywords: List[str] = None,
            days_back: int = 7,
            publish: bool = True) -> Dict[str, Any]:
        """
        运行完整流程

        Args:
            keywords: 搜索关键词
            days_back: 回溯天数
            publish: 是否发布

        Returns:
            运行结果
        """
        start_time = datetime.now()

        try:
            # 1. 采集信息
            items = self.collect(keywords, days_back)

            if not items:
                self.logger.warning("未采集到任何信息")
                return {"success": False, "message": "未采集到任何信息"}

            # 2. 分析内容
            items = self.analyze(items)

            if not items:
                self.logger.warning("没有信息通过筛选")
                return {"success": False, "message": "没有信息通过筛选"}

            # 3. 去重
            items = self.deduplicator.deduplicate(items)

            # 4. 生成文章
            articles = self.generate(items)

            if not articles:
                self.logger.warning("没有生成任何文章")
                return {"success": False, "message": "没有生成任何文章"}

            result = {
                "success": True,
                "collected": len(items),
                "generated": len(articles),
                "articles": articles
            }

            # 5. 发布文章
            if publish:
                publish_results = self.publish(articles)
                result["publish_results"] = publish_results

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            self.logger.info("=" * 60)
            self.logger.info(f"流程完成，耗时 {duration:.2f} 秒")
            self.logger.info(f"采集: {len(items)} 条 | 生成: {len(articles)} 篇")
            self.logger.info("=" * 60)

            return result

        except Exception as e:
            self.logger.error(f"运行流程失败: {e}")
            return {"success": False, "error": str(e)}

        finally:
            # 清理资源
            if hasattr(self, 'http_client'):
                self.http_client.close()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="房产资讯自动化发布代理"
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="配置文件路径"
    )
    parser.add_argument(
        "--keywords",
        type=str,
        nargs="*",
        default=None,
        help="搜索关键词"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="回溯天数"
    )
    parser.add_argument(
        "--no-publish",
        action="store_true",
        help="不发布文章（仅生成）"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="测试模式"
    )

    args = parser.parse_args()

    # 创建发布代理
    publisher = RealEstateNewsPublisher(config_path=args.config)

    # 运行流程
    result = publisher.run(
        keywords=args.keywords,
        days_back=args.days,
        publish=not args.no_publish and not args.test
    )

    # 输出结果
    if result.get("success"):
        print("\n" + "=" * 60)
        print("执行成功！")
        print(f"采集: {result.get('collected', 0)} 条")
        print(f"生成: {result.get('generated', 0)} 篇")
        print("=" * 60)
        return 0
    else:
        print("\n" + "=" * 60)
        print(f"执行失败: {result.get('message', result.get('error', '未知错误'))}")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
