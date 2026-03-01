# -*- coding: utf-8 -*-
"""
竞品内容采集技能 - 核心模块
采集抖音/小红书等平台同行爆款内容，分析内容策略
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

SKILL_DIR = Path(__file__).parent.resolve()
DATA_DIR = SKILL_DIR / "data"
REPORTS_DIR = SKILL_DIR / "reports"


@dataclass
class ContentItem:
    """采集到的内容条目"""
    platform: str
    title: str
    author: str
    url: str
    likes: int = 0
    comments: int = 0
    shares: int = 0
    collects: int = 0
    publish_time: str = ""
    tags: List[str] = None
    content_type: str = "video"  # video / note / live_clip
    description: str = ""

    def __post_init__(self):
        if self.tags is None:
            self.tags = []

    @property
    def engagement_score(self) -> float:
        """互动分数 = 点赞 + 评论*3 + 分享*5 + 收藏*2"""
        return self.likes + self.comments * 3 + self.shares * 5 + self.collects * 2


class CompetitorCrawler:
    """竞品内容采集器"""

    # 房地产专用关键词
    REALESTATE_KEYWORDS = {
        "core": ["宁波买房", "宁波别墅", "宁波新房", "度假养老"],
        "product": ["别墅", "排屋", "合院", "洋房", "公寓", "商铺"],
        "location": ["余姚", "镇海", "奉化", "牟山", "九龙湖", "溪口"],
        "topic": ["法拍房", "房贷利率", "购房政策", "养老地产"],
    }

    def __init__(self, config_path: Optional[str] = None):
        DATA_DIR.mkdir(exist_ok=True)
        REPORTS_DIR.mkdir(exist_ok=True)
        self.config = {}
        if config_path:
            import yaml
            with open(config_path, "r", encoding="utf-8") as f:
                self.config = yaml.safe_load(f)

    def search_hot_content(
        self,
        platform: str,
        keywords: Optional[List[str]] = None,
        min_likes: int = 50,
        limit: int = 30,
        days: int = 7,
    ) -> List[ContentItem]:
        """按关键词搜索平台爆款内容

        Args:
            platform: 平台名称 (xiaohongshu/douyin)
            keywords: 搜索关键词，None 使用默认房地产关键词
            min_likes: 最低点赞数
            limit: 采集数量上限
            days: 采集最近几天的内容

        Returns:
            内容条目列表（按互动分数排序）
        """
        if keywords is None:
            keywords = self.REALESTATE_KEYWORDS["core"]

        results = []
        for keyword in keywords:
            items = self._search_platform(platform, keyword, limit=limit // len(keywords))
            results.extend(items)

        # 过滤和排序
        filtered = [
            item for item in results
            if item.likes >= min_likes
        ]
        filtered.sort(key=lambda x: x.engagement_score, reverse=True)

        # 保存采集结果
        self._save_results(platform, filtered)

        return filtered[:limit]

    def monitor_accounts(
        self,
        platform: str,
        accounts: List[str],
        days: int = 7,
    ) -> Dict[str, List[ContentItem]]:
        """监控竞品账号的内容更新

        Args:
            platform: 平台名称
            accounts: 竞品账号列表
            days: 监控最近几天

        Returns:
            各账号的内容列表
        """
        results = {}
        for account in accounts:
            items = self._fetch_account_content(platform, account, days)
            results[account] = items
            logger.info(f"采集 {account} 的内容: {len(items)} 条")

        return results

    def generate_analysis_report(
        self,
        items: List[ContentItem],
        report_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """生成竞品内容分析报告

        Args:
            items: 采集到的内容列表
            report_name: 报告名称

        Returns:
            分析报告数据
        """
        if not items:
            return {"error": "没有可分析的内容"}

        # 基础统计
        total = len(items)
        avg_likes = sum(i.likes for i in items) / total
        avg_comments = sum(i.comments for i in items) / total

        # 高频标签统计
        tag_counter: Dict[str, int] = {}
        for item in items:
            for tag in item.tags:
                tag_counter[tag] = tag_counter.get(tag, 0) + 1
        top_tags = sorted(tag_counter.items(), key=lambda x: x[1], reverse=True)[:20]

        # 爆款标题分析
        top_items = sorted(items, key=lambda x: x.engagement_score, reverse=True)[:10]

        # 内容类型分布
        type_dist: Dict[str, int] = {}
        for item in items:
            type_dist[item.content_type] = type_dist.get(item.content_type, 0) + 1

        report = {
            "generated_at": datetime.now().isoformat(),
            "total_items": total,
            "statistics": {
                "avg_likes": round(avg_likes, 1),
                "avg_comments": round(avg_comments, 1),
                "max_likes": max(i.likes for i in items),
                "max_engagement": max(i.engagement_score for i in items),
            },
            "top_tags": [{"tag": t, "count": c} for t, c in top_tags],
            "top_content": [
                {
                    "title": i.title,
                    "likes": i.likes,
                    "engagement": i.engagement_score,
                    "url": i.url,
                }
                for i in top_items
            ],
            "content_type_distribution": type_dist,
            "recommendations": self._generate_recommendations(items, top_tags),
        }

        # 保存报告
        if report_name is None:
            report_name = f"competitor_analysis_{datetime.now().strftime('%Y%m%d')}"
        report_file = REPORTS_DIR / f"{report_name}.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        logger.info(f"分析报告已保存: {report_file}")
        return report

    def get_topic_suggestions(
        self,
        items: List[ContentItem],
        count: int = 10,
    ) -> List[Dict[str, str]]:
        """基于爆款内容生成选题建议

        Args:
            items: 采集到的内容列表
            count: 建议数量

        Returns:
            选题建议列表
        """
        top_items = sorted(items, key=lambda x: x.engagement_score, reverse=True)[:count]

        suggestions = []
        for item in top_items:
            suggestions.append({
                "reference_title": item.title,
                "reference_likes": item.likes,
                "suggested_angle": self._suggest_angle(item),
                "suggested_tags": item.tags[:5],
                "platform": item.platform,
            })

        return suggestions

    def _search_platform(
        self, platform: str, keyword: str, limit: int = 10
    ) -> List[ContentItem]:
        """搜索平台内容（需要 MediaCrawler 或 Playwright）"""
        logger.info(f"搜索 {platform}: {keyword} (限制 {limit} 条)")
        # 实际实现需要调用 MediaCrawler 或 Playwright
        # 这里返回空列表，等待集成 MediaCrawler
        return []

    def _fetch_account_content(
        self, platform: str, account: str, days: int
    ) -> List[ContentItem]:
        """获取账号内容"""
        logger.info(f"采集 {platform} 账号 {account} 最近 {days} 天内容")
        return []

    def _generate_recommendations(
        self, items: List[ContentItem], top_tags: List[tuple]
    ) -> List[str]:
        """生成内容策略建议"""
        recommendations = []

        if top_tags:
            tag_names = [t for t, _ in top_tags[:5]]
            recommendations.append(f"高频标签建议使用: {', '.join(tag_names)}")

        # 分析内容类型
        video_count = sum(1 for i in items if i.content_type == "video")
        note_count = sum(1 for i in items if i.content_type == "note")
        if video_count > note_count:
            recommendations.append("竞品以视频内容为主，建议加大视频产出")
        else:
            recommendations.append("竞品图文内容较多，可差异化主攻视频")

        # 分析互动
        high_engagement = [i for i in items if i.engagement_score > 1000]
        if high_engagement:
            recommendations.append(
                f"发现 {len(high_engagement)} 条高互动内容，建议分析其标题和封面策略"
            )

        return recommendations

    def _suggest_angle(self, item: ContentItem) -> str:
        """根据爆款内容建议创作角度"""
        title = item.title.lower()
        if any(kw in title for kw in ["实拍", "探盘", "看房"]):
            return "实地探访类 - 拍摄实景素材，展示真实环境"
        elif any(kw in title for kw in ["攻略", "指南", "注意"]):
            return "知识科普类 - 分享购房知识，建立专业形象"
        elif any(kw in title for kw in ["价格", "总价", "首付"]):
            return "价格分析类 - 直给价格信息，吸引精准客户"
        else:
            return "生活方式类 - 展示居住体验，引发向往"

    def _save_results(self, platform: str, items: List[ContentItem]):
        """保存采集结果"""
        data_file = DATA_DIR / f"{platform}_{datetime.now().strftime('%Y%m%d')}.jsonl"
        with open(data_file, "a", encoding="utf-8") as f:
            for item in items:
                f.write(json.dumps(asdict(item), ensure_ascii=False) + "\n")
