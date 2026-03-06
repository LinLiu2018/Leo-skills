# 内容创作API
from fastapi import APIRouter, UploadFile, File, Form
from typing import List, Optional

router = APIRouter()


@router.post("/generate/video")
async def generate_video(
    prompt: str = Form(...),
    video_type: str = Form(...),  # t2v, i2v, avatar, mix
    duration: int = Form(15),
    ratio: str = Form("9:16"),
    quality: str = Form("standard"),
    image: Optional[UploadFile] = File(None)
):
    """生成视频"""
    return {
        "task_id": "task_123456",
        "status": "processing",
        "message": "视频生成任务已提交",
        "estimated_time": 30
    }


@router.get("/generate/status/{task_id}")
async def get_generation_status(task_id: str):
    """获取生成状态"""
    return {
        "task_id": task_id,
        "status": "processing",
        "progress": 65,
        "result_url": None
    }


@router.post("/generate/copy")
async def generate_copy(
    topic: str,
    style: str = "professional",
    count: int = 3
):
    """生成文案"""
    return {
        "copies": [
            f"【{topic}】宁波别墅市场最新分析，买房必看！",
            f"【{topic}】揭秘宁波高端住宅市场，这些区域值得关注",
            f"【{topic}】2026年宁波房产投资指南"
        ]
    }


@router.get("/history")
async def get_generation_history(
    skip: int = 0,
    limit: int = 20
):
    """获取生成历史"""
    return [
        {
            "id": 1,
            "type": "t2v",
            "title": "宁波别墅市场分析",
            "status": "completed",
            "time": "10分钟前",
            "duration": "45秒"
        },
        {
            "id": 2,
            "type": "avatar",
            "title": "法拍房避坑指南",
            "status": "generating",
            "progress": 65,
            "time": "进行中"
        }
    ]


@router.post("/upload")
async def upload_content(
    file: UploadFile = File(...),
    category: str = Form("default")
):
    """上传素材"""
    return {
        "filename": file.filename,
        "url": f"/uploads/{file.filename}",
        "category": category
    }
