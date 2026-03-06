# AI指令API
from fastapi import APIRouter
from typing import List, Optional

router = APIRouter()


@router.post("/execute")
async def execute_command(
    command: str,
    context: Optional[dict] = None
):
    """执行AI指令"""
    # 模拟指令解析和执行
    return {
        "task_id": "task_789",
        "command": command,
        "intent": "content_generation_and_publish",
        "steps": [
            {"id": 1, "name": "解析指令意图", "status": "completed", "detail": "识别为：内容生成+多平台发布任务"},
            {"id": 2, "name": "生成视频内容", "status": "running", "detail": "调用Sora 2 API生成视频..."},
            {"id": 3, "name": "配置发布计划", "status": "pending"},
            {"id": 4, "name": "执行矩阵发布", "status": "pending"}
        ],
        "estimated_time": 35
    }


@router.get("/status/{task_id}")
async def get_command_status(task_id: str):
    """获取指令执行状态"""
    return {
        "task_id": task_id,
        "status": "executing",
        "progress": 65,
        "current_step": "生成视频内容",
        "result": None
    }


@router.get("/suggestions")
async def get_command_suggestions(
    query: Optional[str] = None
):
    """获取指令建议"""
    suggestions = [
        {"id": 1, "name": "生成房产视频", "icon": "🎬", "prompt": "帮我做一个关于宁波别墅的视频"},
        {"id": 2, "name": "监控竞品账号", "icon": "👀", "prompt": "监控抖音账号\"XXX\"最近10条视频数据"},
        {"id": 3, "name": "批量发布内容", "icon": "🚀", "prompt": "将最新视频发布到所有平台"},
        {"id": 4, "name": "获取客户线索", "icon": "👥", "prompt": "把评论区要买的人都加到微信"},
        {"id": 5, "name": "生成爆款文案", "icon": "✍️", "prompt": "帮我写5个房产视频的爆款标题"},
        {"id": 6, "name": "数据分析报告", "icon": "📊", "prompt": "生成本周运营数据分析报告"}
    ]

    if query:
        suggestions = [s for s in suggestions if query in s["name"] or query in s["prompt"]]

    return suggestions


@router.get("/history")
async def get_command_history(
    skip: int = 0,
    limit: int = 20
):
    """获取指令历史"""
    return [
        {
            "id": 1,
            "command": "帮我做一个关于咖啡的视频",
            "status": "completed",
            "time": "10分钟前",
            "result": "视频生成成功"
        },
        {
            "id": 2,
            "command": "监控竞品账号数据",
            "status": "completed",
            "time": "1小时前",
            "result": "数据已更新"
        }
    ]
