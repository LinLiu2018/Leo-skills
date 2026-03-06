# 私域管理API
from fastapi import APIRouter
from typing import List, Optional

router = APIRouter()


@router.get("/friends/requests")
async def get_friend_requests(
    status: Optional[str] = "pending"
):
    """获取好友申请"""
    return [
        {
            "id": 1,
            "nickname": "张先生",
            "avatar": "",
            "source": "抖音私信",
            "message": "想了解宁波别墅",
            "time": "2分钟前",
            "status": "pending"
        },
        {
            "id": 2,
            "nickname": "李女士",
            "avatar": "",
            "source": "视频号",
            "message": "法拍房咨询",
            "time": "5分钟前",
            "status": "pending"
        }
    ]


@router.post("/friends/requests/{request_id}/accept")
async def accept_friend_request(request_id: int):
    """通过好友申请"""
    return {"message": "已通过好友申请", "request_id": request_id}


@router.get("/moments")
async def get_moments(
    skip: int = 0,
    limit: int = 20
):
    """获取朋友圈列表"""
    return [
        {
            "id": 1,
            "content": "今日推荐：鄞州区独栋别墅，带花园，价格美丽",
            "images": 3,
            "likes": 28,
            "comments": 5,
            "time": "1小时前"
        },
        {
            "id": 2,
            "content": "法拍房避坑指南，新手必看！",
            "images": 6,
            "likes": 45,
            "comments": 12,
            "time": "3小时前"
        }
    ]


@router.post("/moments")
async def create_moment(
    content: str,
    images: Optional[List[str]] = None,
    schedule: Optional[str] = None
):
    """发布朋友圈"""
    return {
        "id": 3,
        "content": content,
        "images": len(images) if images else 0,
        "time": schedule if schedule else "刚刚",
        "status": "scheduled" if schedule else "published"
    }


@router.get("/stats")
async def get_private_domain_stats():
    """获取私域统计数据"""
    return {
        "new_friends_today": 12,
        "total_friends": 2580,
        "interactions_today": 86,
        "conversion_rate": 3.2
    }


@router.get("/auto-tasks")
async def get_auto_tasks():
    """获取自动任务状态"""
    return [
        {"id": 1, "name": "自动通过好友", "status": True, "count": 12},
        {"id": 2, "name": "自动回复欢迎语", "status": True, "count": 45},
        {"id": 3, "name": "自动点赞朋友圈", "status": False, "count": 0},
        {"id": 4, "name": "定时发布朋友圈", "status": True, "count": 3}
    ]
