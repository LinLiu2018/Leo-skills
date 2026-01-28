# Optimizer Module
# 优化器模块

from typing import Dict, Any, List
from datetime import datetime
from utils.logger import get_logger

logger = get_logger(__name__)


class Optimizer:
    """内容优化器"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化优化器

        Args:
            config: 配置
        """
        self.config = config
        self.optimization_config = config.get("optimization", {})
        self.enabled = self.optimization_config.get("enabled", True)
        self.min_articles = self.optimization_config.get("min_articles_for_analysis", 10)

        # 历史数据
        self.article_history = []
        self.optimization_suggestions = []

    def analyze_performance(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        分析文章表现

        Args:
            articles: 文章列表（包含统计数据）

        Returns:
            分析结果
        """
        if len(articles) < self.min_articles:
            logger.info(f"文章数量不足 {self.min_articles}，跳过分析")
            return {"ready": False, "reason": "文章数量不足"}

        analysis = {
            "ready": True,
            "total_articles": len(articles),
            "total_reads": sum(a.get("read_count", 0) for a in articles),
            "avg_reads": sum(a.get("read_count", 0) for a in articles) / len(articles),
            "top_topics": self._analyze_top_topics(articles),
            "best_publishing_times": self._analyze_best_times(articles),
            "title_analysis": self._analyze_titles(articles),
            "content_length_analysis": self._analyze_content_length(articles),
            "suggestions": []
        }

        # 生成优化建议
        suggestions = self._generate_suggestions(analysis)
        analysis["suggestions"] = suggestions
        self.optimization_suggestions = suggestions

        return analysis

    def _analyze_top_topics(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """分析最受欢迎的主题"""
        topic_stats = {}

        for article in articles:
            keywords = article.get("keywords", [])
            reads = article.get("read_count", 0)

            for keyword in keywords:
                if keyword not in topic_stats:
                    topic_stats[keyword] = {"count": 0, "total_reads": 0}
                topic_stats[keyword]["count"] += 1
                topic_stats[keyword]["total_reads"] += reads

        # 计算平均阅读量并排序
        top_topics = []
        for topic, stats in topic_stats.items():
            avg_reads = stats["total_reads"] / stats["count"]
            top_topics.append({
                "topic": topic,
                "article_count": stats["count"],
                "avg_reads": avg_reads
            })

        return sorted(top_topics, key=lambda x: x["avg_reads"], reverse=True)[:5]

    def _analyze_best_times(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """分析最佳发布时间"""
        time_stats = {}

        for article in articles:
            publish_time = article.get("publish_time", "")
            if not publish_time:
                continue

            # 提取小时（简化处理）
            try:
                hour = datetime.fromisoformat(publish_time).hour
                reads = article.get("read_count", 0)

                if hour not in time_stats:
                    time_stats[hour] = {"count": 0, "total_reads": 0}
                time_stats[hour]["count"] += 1
                time_stats[hour]["total_reads"] += reads
            except:
                continue

        # 计算平均阅读量
        best_times = []
        for hour, stats in time_stats.items():
            avg_reads = stats["total_reads"] / stats["count"]
            best_times.append({
                "hour": hour,
                "avg_reads": avg_reads,
                "count": stats["count"]
            })

        return sorted(best_times, key=lambda x: x["avg_reads"], reverse=True)[:5]

    def _analyze_titles(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析标题特征"""
        title_patterns = {
            "question_format": {"count": 0, "total_reads": 0},
            "number_format": {"count": 0, "total_reads": 0},
            "urgent_format": {"count": 0, "total_reads": 0},
            "benefit_format": {"count": 0, "total_reads": 0}
        }

        for article in articles:
            title = article.get("title", "")
            reads = article.get("read_count", 0)

            if "？" in title or "吗" in title:
                title_patterns["question_format"]["count"] += 1
                title_patterns["question_format"]["total_reads"] += reads
            elif any(char in title for char in "0123456789"):
                title_patterns["number_format"]["count"] += 1
                title_patterns["number_format"]["total_reads"] += reads
            elif "紧急" in title or "必看" in title or "注意" in title:
                title_patterns["urgent_format"]["count"] += 1
                title_patterns["urgent_format"]["total_reads"] += reads
            elif "利好" in title or "优惠" in title or "福利" in title:
                title_patterns["benefit_format"]["count"] += 1
                title_patterns["benefit_format"]["total_reads"] += reads

        # 计算平均表现
        for pattern, stats in title_patterns.items():
            if stats["count"] > 0:
                stats["avg_reads"] = stats["total_reads"] / stats["count"]
            else:
                stats["avg_reads"] = 0

        return title_patterns

    def _analyze_content_length(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析内容长度效果"""
        length_stats = {
            "short": {"count": 0, "total_reads": 0},  # < 800 字
            "medium": {"count": 0, "total_reads": 0},  # 800-1200 字
            "long": {"count": 0, "total_reads": 0}  # > 1200 字
        }

        for article in articles:
            content = article.get("content", "")
            reads = article.get("read_count", 0)
            length = len(content)

            if length < 800:
                length_stats["short"]["count"] += 1
                length_stats["short"]["total_reads"] += reads
            elif length < 1200:
                length_stats["medium"]["count"] += 1
                length_stats["medium"]["total_reads"] += reads
            else:
                length_stats["long"]["count"] += 1
                length_stats["long"]["total_reads"] += reads

        # 计算平均值
        for length_type, stats in length_stats.items():
            if stats["count"] > 0:
                stats["avg_reads"] = stats["total_reads"] / stats["count"]
            else:
                stats["avg_reads"] = 0

        return length_stats

    def _generate_suggestions(self, analysis: Dict[str, Any]) -> List[str]:
        """生成优化建议"""
        suggestions = []

        # 主题建议
        top_topics = analysis.get("top_topics", [])
        if top_topics:
            suggestions.append(
                f"建议增加关于「{top_topics[0]['topic']}」的内容，"
                f"该主题平均阅读量 {top_topics[0]['avg_reads']:.0f}"
            )

        # 发布时间建议
        best_times = analysis.get("best_publishing_times", [])
        if best_times:
            suggestions.append(
                f"建议在 {best_times[0]['hour']}:00 发布文章，"
                f"该时段平均阅读量更高"
            )

        # 标题建议
        title_analysis = analysis.get("title_analysis", {})
        best_title_format = max(
            title_analysis.items(),
            key=lambda x: x[1].get("avg_reads", 0)
        )
        if best_title_format[1].get("avg_reads", 0) > 0:
            format_names = {
                "question_format": "疑问式",
                "number_format": "数字式",
                "urgent_format": "紧迫式",
                "benefit_format": "利益式"
            }
            suggestions.append(
                f"建议使用 {format_names.get(best_title_format[0], best_title_format[0])} 标题"
            )

        # 内容长度建议
        length_analysis = analysis.get("content_length_analysis", {})
        best_length = max(
            length_analysis.items(),
            key=lambda x: x[1].get("avg_reads", 0)
        )
        if best_length[1].get("avg_reads", 0) > 0:
            length_names = {
                "short": "短篇 (<800字)",
                "medium": "中篇 (800-1200字)",
                "long": "长篇 (>1200字)"
            }
            suggestions.append(
                f"建议使用 {length_names.get(best_length[0], best_length[0])} 内容"
            )

        return suggestions

    def get_suggestions(self) -> List[str]:
        """获取优化建议"""
        return self.optimization_suggestions

    def auto_adjust_schedule(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """自动调整发布计划"""
        if not self.optimization_config.get("auto_adjust_schedule", False):
            return {"adjusted": False, "reason": "自动调整未启用"}

        best_times = analysis.get("best_publishing_times", [])
        if not best_times:
            return {"adjusted": False, "reason": "无可用数据"}

        # 获取最佳发布时间
        best_hour = best_times[0]["hour"]

        # 生成新的发布计划
        new_schedule = f"0 {best_hour} * * 1-5"  # 工作日最佳时间发布

        return {
            "adjusted": True,
            "new_schedule": new_schedule,
            "best_hour": best_hour,
            "expected_improvement": f"{best_times[0]['avg_reads']:.0f} 平均阅读量"
        }
