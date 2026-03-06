# 认证API
from fastapi import APIRouter, HTTPException
from datetime import timedelta

from app.core.config import settings

router = APIRouter()


@router.post("/login")
async def login(
    username: str,
    password: str
):
    """用户登录"""
    # 模拟登录验证
    if username == "admin" and password == "admin":
        return {
            "access_token": "mock_token_123",
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": {
                "id": 1,
                "username": username,
                "nickname": "管理员",
                "avatar": ""
            }
        }
    raise HTTPException(status_code=401, detail="用户名或密码错误")


@router.post("/register")
async def register(
    username: str,
    password: str,
    email: Optional[str] = None
):
    """用户注册"""
    return {
        "message": "注册成功",
        "user": {
            "id": 1,
            "username": username,
            "email": email
        }
    }


@router.get("/me")
async def get_current_user():
    """获取当前用户信息"""
    return {
        "id": 1,
        "username": "admin",
        "nickname": "Leo",
        "email": "admin@example.com",
        "avatar": "",
        "role": "admin"
    }


@router.post("/logout")
async def logout():
    """用户登出"""
    return {"message": "登出成功"}


from typing import Optional
