# 账号管理API
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.db.database import get_db
from app.schemas.account import AccountCreate, AccountResponse, AccountUpdate

router = APIRouter()


@router.get("/", response_model=List[AccountResponse])
async def list_accounts(
    platform: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """获取账号列表"""
    # 模拟数据
    return [
        {
            "id": 1,
            "platform": "douyin",
            "nickname": "Leo说房",
            "avatar": "",
            "fans": 128000,
            "status": "online",
            "device": "phone",
            "last_active": "2分钟前"
        },
        {
            "id": 2,
            "platform": "douyin",
            "nickname": "宁波房产观察",
            "avatar": "",
            "fans": 85000,
            "status": "online",
            "device": "phone",
            "last_active": "5分钟前"
        }
    ]


@router.post("/", response_model=AccountResponse)
async def create_account(
    account: AccountCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建账号"""
    return {
        "id": 3,
        **account.dict(),
        "status": "offline",
        "last_active": "刚刚"
    }


@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取账号详情"""
    return {
        "id": account_id,
        "platform": "douyin",
        "nickname": "Leo说房",
        "avatar": "",
        "fans": 128000,
        "status": "online",
        "device": "phone",
        "last_active": "2分钟前"
    }


@router.put("/{account_id}", response_model=AccountResponse)
async def update_account(
    account_id: int,
    account: AccountUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新账号"""
    return {
        "id": account_id,
        "platform": "douyin",
        "nickname": "Leo说房",
        "avatar": "",
        "fans": 128000,
        "status": "online",
        "device": "phone",
        "last_active": "刚刚"
    }


@router.delete("/{account_id}")
async def delete_account(
    account_id: int,
    db: AsyncSession = Depends(get_db)
):
    """删除账号"""
    return {"message": "账号已删除"}


@router.post("/{account_id}/sync")
async def sync_account(
    account_id: int,
    db: AsyncSession = Depends(get_db)
):
    """同步账号数据"""
    return {"message": "同步成功", "account_id": account_id}
