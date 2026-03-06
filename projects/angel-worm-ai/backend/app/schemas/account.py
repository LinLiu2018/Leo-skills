# 账号相关数据模型
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class AccountBase(BaseModel):
    platform: str = Field(..., description="平台类型: douyin, kuaishou等")
    nickname: str = Field(..., description="账号昵称")
    avatar: Optional[str] = Field(None, description="头像URL")
    account_id: Optional[str] = Field(None, description="平台账号ID")


class AccountCreate(AccountBase):
    device: str = Field(default="phone", description="设备类型: phone/emulator")
    config: Optional[dict] = Field(None, description="账号配置")


class AccountUpdate(BaseModel):
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    status: Optional[str] = None
    device: Optional[str] = None
    config: Optional[dict] = None


class AccountResponse(AccountBase):
    id: int
    fans: int = Field(default=0, description="粉丝数")
    status: str = Field(default="offline", description="状态: online/offline/warning/error")
    device: str = Field(default="phone", description="设备类型")
    last_active: str = Field(default="", description="最后活跃时间")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
