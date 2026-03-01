"""Video monitor skill."""

from __future__ import annotations

import random
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from leo_skills.base import SkillResult
from leo_skills.core.base_executor import BaseExecutor


class VideoMonitorSkill(BaseExecutor):
    """Monitor account and city-level short-video metrics."""

    supports_direct_execution = True
    default_schedule = "0 8 * * *"

    def __init__(self):
        self.name = "video_monitor_skill"
        self.display_name = "视频号账号监测"
        self.version = "2.0.0"

    def monitor_account(self, account_id: str | None = None, days: int = 7, query: str = "", **kwargs) -> Dict[str, Any]:
        followers = random.randint(1000, 100000)
        followers_growth = random.randint(-5, 20)

        videos: List[Dict[str, Any]] = []
        for i in range(min(days, 10)):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            videos.append(
                {
                    "date": date,
                    "title": f"视频作品 {i + 1}",
                    "views": random.randint(1000, 50000),
                    "likes": random.randint(50, 5000),
                    "comments": random.randint(10, 500),
                    "shares": random.randint(5, 200),
                }
            )

        total_views = sum(v["views"] for v in videos)
        total_likes = sum(v["likes"] for v in videos)
        avg_engagement = round(total_likes / total_views * 100, 2) if total_views > 0 else 0

        summary = (
            f"账号监测报告：{account_id or '未知账号'}\n"
            f"粉丝：{followers:,}（{followers_growth:+d}%）\n"
            f"近{days}天作品：{len(videos)} 条，播放：{total_views:,}，点赞：{total_likes:,}\n"
            f"互动率：{avg_engagement}%"
        )

        return {
            "account_id": account_id,
            "report_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "followers": {
                "current": followers,
                "growth_rate": followers_growth,
            },
            "videos": videos,
            "summary": summary,
            "metrics": {
                "total_views": total_views,
                "total_likes": total_likes,
                "avg_engagement_rate": avg_engagement,
            },
        }

    def monitor_city_accounts(self, city: str = "宁波", days: int = 7, query: str = "", **kwargs) -> Dict[str, Any]:
        accounts = [
            {"name": f"{city}生活圈", "category": "生活"},
            {"name": f"{city}美食探店", "category": "美食"},
            {"name": f"{city}房产资讯", "category": "房产"},
            {"name": f"{city}商业观察", "category": "商业"},
            {"name": f"{city}吃喝玩乐", "category": "娱乐"},
        ]

        results: List[Dict[str, Any]] = []
        total_followers = 0

        for acc in accounts:
            followers = random.randint(5000, 100000)
            total_followers += followers
            results.append(
                {
                    "name": acc["name"],
                    "category": acc["category"],
                    "followers": followers,
                    "growth": random.randint(-3, 15),
                    "avg_views": random.randint(2000, 30000),
                }
            )

        results.sort(key=lambda x: x["followers"], reverse=True)
        avg_growth = sum(r["growth"] for r in results) / len(results)

        summary = (
            f"{city}视频号监测报告\n"
            f"监测账号：{len(accounts)} 个，总粉丝：{total_followers:,}，周期：近{days}天\n"
            f"TOP1：{results[0]['name']}（{results[0]['followers']:,}）\n"
            f"平均增长率：{avg_growth:.1f}%"
        )

        return {
            "city": city,
            "days": days,
            "total_accounts": len(accounts),
            "total_followers": total_followers,
            "accounts": results,
            "summary": summary,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }

    def compare_accounts(self, account_ids: Optional[List[str]] = None, query: str = "", **kwargs) -> Dict[str, Any]:
        if not account_ids or len(account_ids) < 2:
            return {
                "error": "请至少提供2个账号进行对比",
                "summary": "对比分析需要至少2个账号",
            }

        results = []
        for acc_id in account_ids:
            results.append(
                {
                    "name": acc_id,
                    "followers": random.randint(5000, 200000),
                    "videos_count": random.randint(50, 500),
                    "avg_views": random.randint(1000, 50000),
                    "engagement_rate": round(random.uniform(1.5, 8.5), 2),
                    "growth_rate": round(random.uniform(-5, 25), 1),
                }
            )

        results.sort(key=lambda x: x["followers"], reverse=True)
        best = results[0]
        summary = (
            f"账号对比分析：共{len(account_ids)}个账号\n"
            f"综合最佳：{best['name']}（粉丝 {best['followers']:,}，互动率 {best['engagement_rate']}%）"
        )

        return {
            "accounts": results,
            "summary": summary,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }

    def execute(self, context: Optional[Dict[str, Any]] = None, query: str = "", **kwargs) -> Any:
        params: Dict[str, Any] = {}
        if isinstance(context, dict):
            context_params = context.get("params")
            if isinstance(context_params, dict):
                params.update(context_params)
            params.update(context)
        if isinstance(kwargs.get("params"), dict):
            params.update(kwargs.pop("params"))
        params.update(kwargs)

        if query and "query" not in params:
            params["query"] = query
        query_text = str(params.get("query", "") or query)

        def _to_int(value: Any, default: int) -> int:
            try:
                return int(value)
            except (TypeError, ValueError):
                return default

        if "对比" in query_text or "比较" in query_text:
            account_ids = params.get("account_ids", ["账号A", "账号B", "账号C"])
            branch_params = dict(params)
            branch_params.pop("account_ids", None)
            branch_params.pop("query", None)
            result = self.compare_accounts(account_ids=account_ids, query=query_text, **branch_params)
        elif any(k in query_text for k in ["城市", "批量", "监测"]) or params.get("city"):
            city = params.get("city") or "宁波"
            days = _to_int(params.get("days", 7), 7)
            branch_params = dict(params)
            branch_params.pop("city", None)
            branch_params.pop("days", None)
            branch_params.pop("query", None)
            result = self.monitor_city_accounts(city=city, days=days, query=query_text, **branch_params)
        else:
            account_id = params.get("account_id", "默认账号")
            days = _to_int(params.get("days", 7), 7)
            branch_params = dict(params)
            branch_params.pop("account_id", None)
            branch_params.pop("days", None)
            branch_params.pop("query", None)
            result = self.monitor_account(account_id=account_id, days=days, query=query_text, **branch_params)

        markdown = self._format_markdown(result)
        structured = SkillResult.ok(
            data=result,
            content=result.get("summary", "视频号监测执行完成"),
            markdown=markdown,
        )

        if context is None:
            return result
        return structured

    def _format_markdown(self, result: Dict[str, Any]) -> str:
        title = "视频号监测报告"
        if result.get("city"):
            title = f"{result['city']}视频号监测报告"
        return f"## {title}\n\n{result.get('summary', '无摘要')}\n"
