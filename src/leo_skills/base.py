"""
Leo Skills — 统一基类和接口契约
================================
所有 Skill 应继承 BaseSkill 并实现 execute() 方法。
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import time

from .core.base_executor import BaseExecutor


@dataclass
class SkillResult:
    """
    技能执行结果的标准格式

    所有 Skill 的 execute() 方法应返回此类型。
    """
    success: bool
    data: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    duration_ms: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典（向后兼容旧的 Dict 返回格式）"""
        result = {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "metadata": self.metadata,
            "duration_ms": self.duration_ms,
            "timestamp": self.timestamp,
        }
        # 兼容旧代码中直接访问 result["status"] 的模式
        result["status"] = "success" if self.success else "error"
        return result

    @classmethod
    def ok(cls, data: Any = None, **metadata) -> "SkillResult":
        """快捷创建成功结果"""
        return cls(success=True, data=data, metadata=metadata)

    @classmethod
    def fail(cls, error: str, **metadata) -> "SkillResult":
        """快捷创建失败结果"""
        return cls(success=False, error=error, metadata=metadata)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "SkillResult":
        """从旧格式 Dict 构造 SkillResult（迁移桥接）"""
        success = d.get("success", d.get("status") == "success")
        return cls(
            success=bool(success),
            data=d.get("data", {k: v for k, v in d.items()
                                 if k not in ("success", "status", "error")}),
            error=d.get("error"),
        )


@dataclass
class SkillMetadata:
    """技能元数据（从 SKILL.md frontmatter 解析）"""
    name: str
    version: str = "1.0.0"
    description: str = ""
    category: str = "general"
    activation_keywords: List[str] = field(default_factory=list)
    enabled: bool = True


class BaseSkill(BaseExecutor, ABC):
    """
    技能抽象基类

    所有 Skill 应继承此类并实现 execute() 方法。
    提供统一的接口契约，使 SkillExecutor 能以一致的方式调用任何技能。

    Usage:
        class MySkill(BaseSkill):
            @property
            def name(self) -> str:
                return "my_skill"

            def execute(self, action: str = "default", **kwargs) -> SkillResult:
                return SkillResult.ok(data={"result": "done"})
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """技能唯一标识名"""
        ...

    @abstractmethod
    def execute(self, action: str = "default", **kwargs) -> SkillResult:
        """
        执行技能

        Args:
            action: 操作名称（技能可支持多个操作）
            **kwargs: 操作参数

        Returns:
            SkillResult 标准结果
        """
        ...

    def get_actions(self) -> List[str]:
        """返回支持的操作列表（子类可覆盖）"""
        return ["default"]

    def safe_execute(self, action: str = "default", **kwargs) -> SkillResult:
        """带异常捕获和计时的执行包装"""
        start = time.time()
        try:
            result = self.execute(action, **kwargs)
            result.duration_ms = (time.time() - start) * 1000
            return result
        except Exception as e:
            return SkillResult.fail(
                error=f"{self.name}.{action} 执行失败: {e}",
                duration_ms=(time.time() - start) * 1000,
            )

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name}>"
