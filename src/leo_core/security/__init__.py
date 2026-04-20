"""
Leo Core Security - 安全模块

提供输入验证、敏感数据过滤、速率限制等安全功能。
"""

from __future__ import annotations

import os
import re
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Union
import hashlib
import hmac
import json

from leo_core.logging import get_logger

logger = get_logger(__name__)


# ============================================================
# 安全配置
# ============================================================

@dataclass
class SecurityConfig:
    """安全配置"""
    enable_input_validation: bool = True
    enable_rate_limiting: bool = True
    enable_sensitive_filter: bool = True
    max_input_length: int = 10000
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # 秒


# ============================================================
# 验证器
# ============================================================

class ValidationResult:
    """验证结果"""

    def __init__(self, valid: bool, message: str = "", field: Optional[str] = None):
        self.valid = valid
        self.message = message
        self.field = field

    def __bool__(self) -> bool:
        return self.valid


class InputValidator:
    """输入验证器"""

    # 危险模式
    DANGEROUS_PATTERNS = [
        r'<script[^>]*>.*?</script>',  # XSS
        r'eval\s*\(',                     # eval()
        r'exec\s*\(',                     # exec()
        r'import\s+os',                   # os import
        r'__import__',                    # dynamic import
        r'subprocess',                    # subprocess
        r'os\.system',                    # os.system
        r'shell=True',                    # shell injection
    ]

    # 编译危险模式
    _compiled_patterns = [re.compile(p, re.IGNORECASE) for p in DANGEROUS_PATTERNS]

    @classmethod
    def validate_input(
        cls,
        value: str,
        field_name: str = "input",
        max_length: int = 10000,
        allow_empty: bool = False,
    ) -> ValidationResult:
        """验证输入"""
        # 检查是否为空
        if not value or not value.strip():
            if allow_empty:
                return ValidationResult(True)
            return ValidationResult(False, "输入不能为空", field_name)

        # 检查长度
        if len(value) > max_length:
            return ValidationResult(
                False,
                f"输入长度不能超过 {max_length} 字符",
                field_name
            )

        # 检查危险模式
        for pattern in cls._compiled_patterns:
            if pattern.search(value):
                return ValidationResult(
                    False,
                    f"输入包含危险内容",
                    field_name
                )

        return ValidationResult(True)

    @classmethod
    def validate_email(cls, email: str) -> ValidationResult:
        """验证邮箱"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(pattern, email):
            return ValidationResult(True)
        return ValidationResult(False, "邮箱格式不正确", "email")

    @classmethod
    def validate_phone(cls, phone: str) -> ValidationResult:
        """验证手机号（中国）"""
        pattern = r'^1[3-9]\d{9}$'
        if re.match(pattern, phone):
            return ValidationResult(True)
        return ValidationResult(False, "手机号格式不正确", "phone")

    @classmethod
    def validate_url(cls, url: str) -> ValidationResult:
        """验证URL"""
        pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        if re.match(pattern, url, re.IGNORECASE):
            return ValidationResult(True)
        return ValidationResult(False, "URL格式不正确", "url")


# ============================================================
# 敏感数据过滤器
# ============================================================

class SensitiveDataFilter:
    """敏感数据过滤器"""

    # 敏感数据模式
    PATTERNS = {
        'api_key': re.compile(
            r'(?i)(api[_-]?key|apikey|secret[_-]?key|access[_-]?key)\s*[:=]\s*[\'"]?([a-zA-Z0-9_\-]{20,})',
            re.IGNORECASE
        ),
        'password': re.compile(
            r'(?i)(password|passwd|pwd|secret)\s*[:=]\s*[\'"]?([^\s\'"]{6,50})',
            re.IGNORECASE
        ),
        'token': re.compile(
            r'(?i)(bearer\s+|token\s*[:=]\s*)[\'"]?([a-zA-Z0-9_\-\.]{20,})',
            re.IGNORECASE
        ),
        'private_key': re.compile(
            r'-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----',
            re.IGNORECASE
        ),
        'credit_card': re.compile(
            r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'
        ),
        'ssn': re.compile(
            r'\b\d{3}[\s-]?\d{2}[\s-]?\d{4}\b'
        ),
        'phone': re.compile(
            r'\b1[3-9]\d[\s-]?\d{4}[\s-]?\d{4}\b'
        ),
        'email': re.compile(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        ),
    }

    # 需要过滤的响应字段
    SENSITIVE_FIELDS = {
        'password', 'passwd', 'pwd', 'secret', 'token',
        'api_key', 'apikey', 'access_token', 'refresh_token',
        'private_key', 'credit_card', 'ssn', 'phone',
    }

    @classmethod
    def filter(cls, data: Any, strict: bool = True) -> Any:
        """过滤敏感数据"""
        if isinstance(data, dict):
            return cls._filter_dict(data, strict)
        elif isinstance(data, list):
            return [cls.filter(item, strict) for item in data]
        elif isinstance(data, str):
            return cls._filter_string(data)
        return data

    @classmethod
    def _filter_dict(cls, data: dict, strict: bool) -> dict:
        """过滤字典中的敏感数据"""
        result = {}
        for key, value in data.items():
            # 检查键名是否敏感
            key_lower = key.lower()
            if key_lower in cls.SENSITIVE_FIELDS:
                result[key] = "[REDACTED]"
            elif isinstance(value, dict):
                result[key] = cls._filter_dict(value, strict)
            elif isinstance(value, str):
                result[key] = cls._filter_string(value)
            else:
                result[key] = value
        return result

    @classmethod
    def _filter_string(cls, text: str) -> str:
        """过滤字符串中的敏感数据"""
        result = text

        # 替换各种敏感模式
        for name, pattern in cls.PATTERNS.items():
            if name == 'email':
                # 邮箱只保留首尾字符
                result = pattern.sub(lambda m: m.group(0)[0] + '***' + m.group(0)[-1], result)
            elif name == 'phone':
                # 手机号只保留后4位
                result = pattern.sub(lambda m: '1***' + m.group(0)[-4:], result)
            else:
                result = pattern.sub(f'[REDACTED:{name}]', result)

        return result

    @classmethod
    def mask_value(cls, value: str, visible_chars: int = 4) -> str:
        """遮蔽值，只显示后几位"""
        if len(value) <= visible_chars:
            return '*' * len(value)
        return '*' * (len(value) - visible_chars) + value[-visible_chars:]


# ============================================================
# 速率限制器
# ============================================================

class RateLimiter:
    """速率限制器"""

    def __init__(
        self,
        max_requests: int = 100,
        window_seconds: int = 60,
        block_duration: int = 300,
    ):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.block_duration = block_duration

        self._requests: Dict[str, List[float]] = defaultdict(list)
        self._blocked: Dict[str, float] = {}
        self._lock = None

    def _get_lock(self):
        if self._lock is None:
            import asyncio
            self._lock = asyncio.Lock()
        return self._lock

    def is_allowed(self, client_id: str) -> bool:
        """检查是否允许请求"""
        # 检查是否被阻止
        if client_id in self._blocked:
            block_time = self._blocked[client_id]
            if time.time() < block_time:
                return False
            else:
                # 解除阻止
                del self._blocked[client_id]

        # 清理过期请求
        now = time.time()
        window_start = now - self.window_seconds
        self._requests[client_id] = [
            t for t in self._requests[client_id]
            if t >= window_start
        ]

        # 检查限制
        if len(self._requests[client_id]) >= self.max_requests:
            # 阻止客户端
            self._blocked[client_id] = time.time() + self.block_duration
            return False

        # 记录请求
        self._requests[client_id].append(now)
        return True

    def get_remaining(self, client_id: str) -> int:
        """获取剩余请求数"""
        now = time.time()
        window_start = now - self.window_seconds

        recent_requests = [
            t for t in self._requests.get(client_id, [])
            if t >= window_start
        ]

        return max(0, self.max_requests - len(recent_requests))

    def get_reset_time(self, client_id: str) -> int:
        """获取重置时间（秒）"""
        if client_id not in self._requests or not self._requests[client_id]:
            return 0

        oldest = min(self._requests[client_id])
        return max(0, int(oldest + self.window_seconds - time.time()))

    def unblock(self, client_id: str) -> bool:
        """解除阻止"""
        if client_id in self._blocked:
            del self._blocked[client_id]
            return True
        return False

    def clear(self) -> None:
        """清除所有限制"""
        self._requests.clear()
        self._blocked.clear()


# ============================================================
# API 密钥管理
# ============================================================

class KeyManager:
    """API 密钥管理器"""

    def __init__(self):
        self._keys: Dict[str, Dict[str, Any]] = {}
        self._key_hash: Dict[str, str] = {}

    def create_key(
        self,
        name: str,
        permissions: Optional[List[str]] = None,
        expires_in: Optional[int] = None,
    ) -> str:
        """创建 API 密钥"""
        import secrets
        key = f"leo_{secrets.token_urlsafe(32)}"

        # 存储密钥信息
        self._keys[key] = {
            "name": name,
            "permissions": permissions or [],
            "created_at": time.time(),
            "expires_at": time.time() + expires_in if expires_in else None,
            "last_used": None,
            "usage_count": 0,
        }

        # 存储密钥哈希
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        self._key_hash[key_hash] = key

        return key

    def validate_key(self, key: str) -> bool:
        """验证 API 密钥"""
        if not key or not key.startswith("leo_"):
            return False

        key_hash = hashlib.sha256(key.encode()).hexdigest()
        real_key = self._key_hash.get(key_hash)

        if real_key != key:
            return False

        key_info = self._keys.get(key)
        if not key_info:
            return False

        # 检查过期
        if key_info["expires_at"] and time.time() > key_info["expires_at"]:
            return False

        # 更新使用信息
        key_info["last_used"] = time.time()
        key_info["usage_count"] += 1

        return True

    def revoke_key(self, key: str) -> bool:
        """撤销 API 密钥"""
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        real_key = self._key_hash.get(key_hash)

        if real_key and real_key in self._keys:
            del self._keys[real_key]
            del self._key_hash[key_hash]
            return True

        return False

    def get_key_info(self, key: str) -> Optional[Dict[str, Any]]:
        """获取密钥信息"""
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        real_key = self._key_hash.get(key_hash)
        return self._keys.get(real_key)


# ============================================================
# 安全工具函数
# ============================================================

def safe_get_env(key: str, default: Optional[str] = None) -> str:
    """安全获取环境变量"""
    value = os.getenv(key, default)
    if value is None:
        raise ValueError(f"Required environment variable {key} is not set")
    return value


def hash_password(password: str, salt: Optional[str] = None) -> tuple:
    """密码哈希"""
    import secrets
    if salt is None:
        salt = secrets.token_hex(16)

    hashed = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000
    )
    return hashed.hex(), salt


def verify_password(password: str, hashed: str, salt: str) -> bool:
    """验证密码"""
    new_hash, _ = hash_password(password, salt)
    return hmac.compare_digest(new_hash, hashed)


def generate_token(length: int = 32) -> str:
    """生成随机令牌"""
    import secrets
    return secrets.token_urlsafe(length)


# ============================================================
# 全局实例
# ============================================================

_rate_limiter: Optional[RateLimiter] = None
_key_manager: Optional[KeyManager] = None


def get_rate_limiter(config: Optional[SecurityConfig] = None) -> RateLimiter:
    """获取全局速率限制器"""
    global _rate_limiter
    if _rate_limiter is None:
        cfg = config or SecurityConfig()
        _rate_limiter = RateLimiter(
            max_requests=cfg.rate_limit_requests,
            window_seconds=cfg.rate_limit_window,
        )
    return _rate_limiter


def get_key_manager() -> KeyManager:
    """获取全局密钥管理器"""
    global _key_manager
    if _key_manager is None:
        _key_manager = KeyManager()
    return _key_manager
