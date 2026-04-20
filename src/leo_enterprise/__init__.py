# -*- coding: utf-8 -*-
"""
企业版模块

功能:
- 多租户支持
- 权限管理
- SaaS 部署配置
- 企业级特性
"""

from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from pydantic import BaseModel


class TenantStatus(str, Enum):
    """租户状态"""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    PENDING = "pending"
    CANCELLED = "cancelled"


class UserRole(str, Enum):
    """用户角色"""
    OWNER = "owner"           # 所有者
    ADMIN = "admin"           # 管理员
    MEMBER = "member"         # 成员
    VIEWER = "viewer"         # 只读


class Permission(str, Enum):
    """权限"""
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    ADMIN = "admin"
    MANAGE_USERS = "manage_users"
    MANAGE_BILLING = "manage_billing"


# 角色权限映射
ROLE_PERMISSIONS = {
    UserRole.OWNER: [p for p in Permission],
    UserRole.ADMIN: [Permission.READ, Permission.WRITE, Permission.EXECUTE, Permission.MANAGE_USERS],
    UserRole.MEMBER: [Permission.READ, Permission.WRITE, Permission.EXECUTE],
    UserRole.VIEWER: [Permission.READ],
}


@dataclass
class Tenant:
    """租户"""
    id: str
    name: str
    status: TenantStatus = TenantStatus.ACTIVE
    plan: str = "free"  # free, pro, enterprise
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    expires_at: Optional[str] = None
    settings: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class User:
    """用户"""
    id: str
    tenant_id: str
    email: str
    name: str
    role: UserRole = UserRole.MEMBER
    permissions: List[Permission] = field(default_factory=list)
    api_key: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_login: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class TenantManager:
    """
    租户管理器

    功能:
    - 租户 CRUD
    - 配额管理
    - 计费管理
    """

    def __init__(self, storage_dir: Optional[Path] = None):
        if storage_dir is None:
            project_root = Path(__file__).parent.parent.parent
            self.storage_dir = project_root / "data" / "enterprise" / "tenants"
        else:
            self.storage_dir = Path(storage_dir)

        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.tenants: Dict[str, Tenant] = {}
        self._load_tenants()

    def _load_tenants(self):
        """加载租户"""
        for tenant_file in self.storage_dir.glob("*.yaml"):
            try:
                with open(tenant_file, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    tenant = Tenant(
                        id=data["id"],
                        name=data["name"],
                        status=TenantStatus(data.get("status", "active")),
                        plan=data.get("plan", "free"),
                        created_at=data.get("created_at", datetime.now().isoformat()),
                        expires_at=data.get("expires_at"),
                        settings=data.get("settings", {}),
                        metadata=data.get("metadata", {}),
                    )
                    self.tenants[tenant.id] = tenant
            except Exception as e:
                pass

    def _save_tenant(self, tenant: Tenant):
        """保存租户"""
        data = {
            "id": tenant.id,
            "name": tenant.name,
            "status": tenant.status.value,
            "plan": tenant.plan,
            "created_at": tenant.created_at,
            "expires_at": tenant.expires_at,
            "settings": tenant.settings,
            "metadata": tenant.metadata,
        }
        with open(self.storage_dir / f"{tenant.id}.yaml", "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True)

    def create_tenant(self, name: str, plan: str = "free") -> Tenant:
        """创建租户"""
        tenant_id = hashlib.md5(
            f"{name}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:12]

        tenant = Tenant(
            id=tenant_id,
            name=name,
            plan=plan,
        )

        self.tenants[tenant_id] = tenant
        self._save_tenant(tenant)
        return tenant

    def get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        """获取租户"""
        return self.tenants.get(tenant_id)

    def update_tenant(self, tenant_id: str, **kwargs) -> Optional[Tenant]:
        """更新租户"""
        tenant = self.tenants.get(tenant_id)
        if not tenant:
            return None

        for key, value in kwargs.items():
            if hasattr(tenant, key):
                setattr(tenant, key, value)

        self._save_tenant(tenant)
        return tenant

    def delete_tenant(self, tenant_id: str) -> bool:
        """删除租户"""
        if tenant_id in self.tenants:
            del self.tenants[tenant_id]
            tenant_file = self.storage_dir / f"{tenant_id}.yaml"
            if tenant_file.exists():
                tenant_file.unlink()
            return True
        return False


class UserManager:
    """
    用户管理器

    功能:
    - 用户 CRUD
    - 角色管理
    - 权限验证
    - API Key 管理
    """

    def __init__(self, storage_dir: Optional[Path] = None):
        if storage_dir is None:
            project_root = Path(__file__).parent.parent.parent
            self.storage_dir = project_root / "data" / "enterprise" / "users"
        else:
            self.storage_dir = Path(storage_dir)

        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.users: Dict[str, User] = {}
        self._load_users()

    def _load_users(self):
        """加载用户"""
        for user_file in self.storage_dir.glob("*.yaml"):
            try:
                with open(user_file, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    user = User(
                        id=data["id"],
                        tenant_id=data["tenant_id"],
                        email=data["email"],
                        name=data["name"],
                        role=UserRole(data.get("role", "member")),
                        permissions=[Permission(p) for p in data.get("permissions", [])],
                        api_key=data.get("api_key"),
                        created_at=data.get("created_at", datetime.now().isoformat()),
                        last_login=data.get("last_login"),
                        metadata=data.get("metadata", {}),
                    )
                    self.users[user.id] = user
            except Exception as e:
                pass

    def _save_user(self, user: User):
        """保存用户"""
        data = {
            "id": user.id,
            "tenant_id": user.tenant_id,
            "email": user.email,
            "name": user.name,
            "role": user.role.value,
            "permissions": [p.value for p in user.permissions],
            "api_key": user.api_key,
            "created_at": user.created_at,
            "last_login": user.last_login,
            "metadata": user.metadata,
        }
        with open(self.storage_dir / f"{user.id}.yaml", "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True)

    def create_user(
        self,
        tenant_id: str,
        email: str,
        name: str,
        role: UserRole = UserRole.MEMBER
    ) -> User:
        """创建用户"""
        user_id = hashlib.md5(
            f"{email}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:12]

        user = User(
            id=user_id,
            tenant_id=tenant_id,
            email=email,
            name=name,
            role=role,
            permissions=ROLE_PERMISSIONS[role],
        )

        self.users[user_id] = user
        self._save_user(user)
        return user

    def generate_api_key(self, user_id: str) -> Optional[str]:
        """生成 API Key"""
        user = self.users.get(user_id)
        if not user:
            return None

        api_key = f"leo_{secrets.token_urlsafe(32)}"
        user.api_key = api_key
        self._save_user(user)
        return api_key

    def verify_permission(self, user_id: str, permission: Permission) -> bool:
        """验证权限"""
        user = self.users.get(user_id)
        if not user:
            return False
        return permission in user.permissions


class EnterpriseConfig:
    """
    企业配置

    功能:
    - SaaS 配置
    - 安全策略
    - 审计日志
    """

    # 计划配额
    PLANS = {
        "free": {
            "max_users": 3,
            "max_api_calls": 1000,
            "storage_mb": 100,
            "support": "community",
        },
        "pro": {
            "max_users": 10,
            "max_api_calls": 10000,
            "storage_mb": 1000,
            "support": "email",
        },
        "enterprise": {
            "max_users": -1,  # 无限制
            "max_api_calls": -1,
            "storage_mb": -1,
            "support": "dedicated",
        },
    }

    @classmethod
    def get_quota(cls, plan: str) -> Dict[str, Any]:
        """获取计划配额"""
        return cls.PLANS.get(plan, cls.PLANS["free"])

    @classmethod
    def check_quota(cls, tenant: Tenant, resource: str, value: int) -> bool:
        """检查配额"""
        quota = cls.get_quota(plan=tenant.plan)
        limit = quota.get(resource, 0)

        if limit == -1:
            return True

        return value <= limit


# 便捷函数
def get_tenant_manager() -> TenantManager:
    """获取租户管理器"""
    return TenantManager()


def get_user_manager() -> UserManager:
    """获取用户管理器"""
    return UserManager()
