# 自动化运营API
from fastapi import APIRouter
from typing import List, Optional

router = APIRouter()


@router.get("/tasks")
async def get_auto_tasks():
    """获取自动化任务"""
    return [
        {
            "id": 1,
            "name": "智能养号-抖音",
            "type": "nurturing",
            "platform": "douyin",
            "status": "running",
            "progress": 65
        },
        {
            "id": 2,
            "name": "评论截流-小红书",
            "type": "intercept",
            "platform": "xiaohongshu",
            "status": "running",
            "progress": 42
        },
        {
            "id": 3,
            "name": "自动获客-快手",
            "type": "customer",
            "platform": "kuaishou",
            "status": "paused",
            "progress": 0
        }
    ]


@router.post("/tasks")
async def create_auto_task(
    name: str,
    task_type: str,
    platform: str,
    config: dict
):
    """创建自动化任务"""
    return {
        "id": 4,
        "name": name,
        "type": task_type,
        "platform": platform,
        "status": "pending",
        "config": config
    }


@router.post("/tasks/{task_id}/start")
async def start_task(task_id: int):
    """启动任务"""
    return {"message": "任务已启动", "task_id": task_id}


@router.post("/tasks/{task_id}/pause")
async def pause_task(task_id: int):
    """暂停任务"""
    return {"message": "任务已暂停", "task_id": task_id}


@router.delete("/tasks/{task_id}")
async def delete_task(task_id: int):
    """删除任务"""
    return {"message": "任务已删除", "task_id": task_id}


@router.get("/stats")
async def get_auto_ops_stats():
    """获取运营统计数据"""
    return {
        "views_today": 1258,
        "likes_today": 126,
        "comments_intercepted": 38,
        "customers_acquired": 12
    }


@router.get("/keywords")
async def get_intercept_keywords():
    """获取截流关键词"""
    return ["怎么买", "多少钱", "联系方式", "加微信", "电话多少"]


@router.post("/keywords")
async def update_intercept_keywords(keywords: List[str]):
    """更新截流关键词"""
    return {"message": "关键词已更新", "keywords": keywords}
