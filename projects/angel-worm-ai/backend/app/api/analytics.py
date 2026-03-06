# 数据分析API
from fastapi import APIRouter
from typing import Optional

router = APIRouter()


@router.get("/overview")
async def get_overview(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """获取数据概览"""
    return {
        "total_plays": 1258000,
        "total_likes": 45800,
        "total_comments": 8900,
        "total_shares": 3200,
        "trends": {
            "plays": "+15%",
            "likes": "+8%",
            "comments": "-2%",
            "shares": "+12%"
        }
    }


@router.get("/platform")
async def get_platform_stats(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """获取平台数据"""
    return [
        {"platform": "抖音", "plays": 580000, "likes": 25000, "comments": 4200, "shares": 1800},
        {"platform": "快手", "plays": 320000, "likes": 12000, "comments": 2100, "shares": 800},
        {"platform": "视频号", "plays": 210000, "likes": 6000, "comments": 1500, "shares": 400},
        {"platform": "小红书", "plays": 148000, "likes": 2800, "comments": 1100, "shares": 200}
    ]


@router.get("/trend")
async def get_trend_data(
    metric: str = "plays",
    days: int = 7
):
    """获取趋势数据"""
    return [
        {"date": "02-24", "value": 120000, "type": "播放量"},
        {"date": "02-25", "value": 150000, "type": "播放量"},
        {"date": "02-26", "value": 135000, "type": "播放量"},
        {"date": "02-27", "value": 180000, "type": "播放量"},
        {"date": "02-28", "value": 220000, "type": "播放量"},
        {"date": "03-01", "value": 195000, "type": "播放量"},
        {"date": "03-02", "value": 258000, "type": "播放量"}
    ]


@router.get("/ranking")
async def get_content_ranking(
    platform: Optional[str] = None,
    metric: str = "plays",
    limit: int = 10
):
    """获取内容排行"""
    return [
        {"id": 1, "title": "宁波别墅市场分析", "platform": "抖音", "plays": 125000, "likes": 5800, "date": "2026-03-01"},
        {"id": 2, "title": "法拍房避坑指南", "platform": "快手", "plays": 98000, "likes": 4200, "date": "2026-03-01"},
        {"id": 3, "title": "商业投资推荐", "platform": "视频号", "plays": 76000, "likes": 3100, "date": "2026-02-28"},
        {"id": 4, "title": "别墅装修案例", "platform": "小红书", "plays": 45000, "likes": 1800, "date": "2026-02-28"},
        {"id": 5, "title": "房产政策解读", "platform": "抖音", "plays": 42000, "likes": 1500, "date": "2026-02-27"}
    ]


@router.get("/report")
async def generate_report(
    start_date: str,
    end_date: str,
    format: str = "json"
):
    """生成数据报告"""
    return {
        "period": f"{start_date} 至 {end_date}",
        "summary": {
            "total_content": 45,
            "total_plays": 1258000,
            "total_interactions": 57900
        },
        "platform_breakdown": [
            {"platform": "抖音", "percentage": 46},
            {"platform": "快手", "percentage": 26},
            {"platform": "视频号", "percentage": 17},
            {"platform": "小红书", "percentage": 11}
        ]
    }
