# -*- coding: utf-8 -*-
"""
自动回滚机制

实现异常自动回滚
"""

import json
import shutil
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


class RollbackReason(str, Enum):
    """回滚原因"""
    TEST_FAILED = "test_failed"
    PERFORMANCE_DEGRADED = "performance_degraded"
    ERROR_RATE_INCREASED = "error_rate_increased"
    HEALTH_CHECK_FAILED = "health_check_failed"
    MANUAL = "manual"
    TIMEOUT = "timeout"
    UNKNOWN = "unknown"


@dataclass
class RollbackEvent:
    """回滚事件"""
    event_id: str
    deployment_id: str
    reason: RollbackReason
    timestamp: datetime = field(default_factory=datetime.now)
    details: Dict[str, Any] = field(default_factory=dict)
    success: bool = False
    duration_seconds: float = 0


class AutoRollback:
    """
    自动回滚

    功能：
    - 状态快照
    - 回滚触发器
    - 增量回滚
    - 回滚验证
    """

    def __init__(self, snapshot_dir: str = ".leo_snapshots"):
        self.snapshot_dir = Path(snapshot_dir)
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)

        self.rollback_events: List[RollbackEvent] = []
        self.rollback_count = 0

    def create_snapshot(
        self,
        skill_path: str,
        version: str,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        创建快照

        Args:
            skill_path: 技能路径
            version: 版本号
            metadata: 额外元数据

        Returns:
            快照ID
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        snapshot_id = f"snapshot_{skill_path.replace('/', '_')}_{version}_{timestamp}"

        source_path = Path("src/leo_skills") / skill_path
        if not source_path.exists():
            raise FileNotFoundError(f"Source path not found: {skill_path}")

        # 创建快照目录
        snapshot_path = self.snapshot_dir / snapshot_id
        snapshot_path.mkdir(parents=True, exist_ok=True)

        # 复制文件
        shutil.copytree(source_path, snapshot_path / "code")

        # 保存元数据
        meta = {
            "snapshot_id": snapshot_id,
            "skill_path": skill_path,
            "version": version,
            "created_at": datetime.now().isoformat(),
            "metadata": metadata or {}
        }

        with open(snapshot_path / "metadata.json", 'w', encoding='utf-8') as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)

        return snapshot_id

    def get_snapshot(self, snapshot_id: str) -> Optional[Path]:
        """获取快照路径"""
        snapshot_path = self.snapshot_dir / snapshot_id

        if snapshot_path.exists():
            return snapshot_path

        return None

    def monitor_for_rollback(
        self,
        deployment_id: str,
        metrics_checker: Callable[[], Dict],
        config: Optional[Dict] = None
    ) -> Optional[RollbackEvent]:
        """
        监控回滚条件

        Args:
            deployment_id: 部署ID
            metrics_checker: 指标检查函数
            config: 配置

        Returns:
            回滚事件（如果需要回滚）
        """
        config = config or {}
        test_failure_threshold = config.get("test_failure_threshold", 0.1)  # 10%
        performance_threshold = config.get("performance_threshold", 0.2)  # 20%
        error_rate_threshold = config.get("error_rate_threshold", 0.05)  # 5%

        metrics = metrics_checker()

        # 检查各项指标
        reason = None

        # 测试失败率
        if "test_failure_rate" in metrics:
            if metrics["test_failure_rate"] > test_failure_threshold:
                reason = RollbackReason.TEST_FAILED

        # 性能下降
        if "performance_degradation" in metrics:
            if metrics["performance_degradation"] > performance_threshold:
                reason = RollbackReason.PERFORMANCE_DEGRADED

        # 错误率上升
        if "error_rate_increase" in metrics:
            if metrics["error_rate_increase"] > error_rate_threshold:
                reason = RollbackReason.ERROR_RATE_INCREASED

        # 健康检查失败
        if "health_check_passed" in metrics and not metrics["health_check_passed"]:
            reason = RollbackReason.HEALTH_CHECK_FAILED

        # 如果需要回滚
        if reason:
            return self._create_rollback_event(deployment_id, reason, metrics)

        return None

    def execute_rollback(
        self,
        snapshot_id: str,
        skill_path: str
    ) -> bool:
        """
        执行回滚

        Args:
            snapshot_id: 快照ID
            skill_path: 技能路径

        Returns:
            是否成功
        """
        start_time = time.time()

        snapshot_path = self.get_snapshot(snapshot_id)
        if not snapshot_path:
            return False

        target_path = Path("src/leo_skills") / skill_path

        try:
            # 备份当前版本
            current_backup = self.snapshot_dir / f"backup_{skill_path.replace('/', '_')}_{int(time.time())}"
            if target_path.exists():
                shutil.copytree(target_path, current_backup)

            # 恢复快照
            snapshot_code = snapshot_path / "code"

            if target_path.exists():
                shutil.rmtree(target_path)

            shutil.copytree(snapshot_code, target_path)

            duration = time.time() - start_time

            # 记录回滚事件
            self.rollback_count += 1
            event = RollbackEvent(
                event_id=f"rollback_{self.rollback_count:08d}",
                deployment_id=snapshot_id,
                reason=RollbackReason.MANUAL,
                success=True,
                duration_seconds=duration
            )
            self.rollback_events.append(event)

            return True

        except Exception as e:
            duration = time.time() - start_time

            # 记录失败
            self.rollback_count += 1
            event = RollbackEvent(
                event_id=f"rollback_{self.rollback_count:08d}",
                deployment_id=snapshot_id,
                reason=RollbackReason.MANUAL,
                success=False,
                details={"error": str(e)},
                duration_seconds=duration
            )
            self.rollback_events.append(event)

            return False

    def verify_rollback(self, skill_path: str) -> bool:
        """
        验证回滚

        Args:
            skill_path: 技能路径

        Returns:
            是否验证成功
        """
        target_path = Path("src/leo_skills") / skill_path

        if not target_path.exists():
            return False

        # 简单的语法检查
        for py_file in target_path.glob("*.py"):
            if py_file.name.startswith("_"):
                continue

            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    code = f.read()
                    compile(code, str(py_file), 'exec')
            except SyntaxError:
                return False

        return True

    def list_snapshots(
        self,
        skill_path: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict]:
        """列出快照"""
        snapshots = []

        for snapshot_dir in sorted(self.snapshot_dir.iterdir(), reverse=True):
            if not snapshot_dir.is_dir():
                continue

            metadata_file = snapshot_dir / "metadata.json"
            if not metadata_file.exists():
                continue

            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    meta = json.load(f)

                if skill_path and meta.get("skill_path") != skill_path:
                    continue

                snapshots.append(meta)
            except:
                pass

            if len(snapshots) >= limit:
                break

        return snapshots

    def cleanup_old_snapshots(
        self,
        keep_count: int = 5,
        skill_path: Optional[str] = None
    ) -> int:
        """清理旧快照"""
        snapshots = self.list_snapshots(skill_path, limit=100)

        if len(snapshots) <= keep_count:
            return 0

        # 删除旧的
        to_delete = snapshots[keep_count:]
        deleted = 0

        for snapshot in to_delete:
            snapshot_id = snapshot.get("snapshot_id")
            if snapshot_id:
                snapshot_path = self.snapshot_dir / snapshot_id
                if snapshot_path.exists():
                    try:
                        shutil.rmtree(snapshot_path)
                        deleted += 1
                    except:
                        pass

        return deleted

    # ========== 辅助方法 ==========

    def _create_rollback_event(
        self,
        deployment_id: str,
        reason: RollbackReason,
        details: Dict
    ) -> RollbackEvent:
        """创建回滚事件"""
        self.rollback_count += 1

        event = RollbackEvent(
            event_id=f"rollback_{self.rollback_count:08d}",
            deployment_id=deployment_id,
            reason=reason,
            details=details
        )

        self.rollback_events.append(event)

        return event

    def get_rollback_stats(self) -> Dict[str, Any]:
        """获取回滚统计"""
        total = len(self.rollback_events)
        success = sum(1 for e in self.rollback_events if e.success)

        # 按原因统计
        by_reason = {}
        for reason in RollbackReason:
            count = sum(1 for e in self.rollback_events if e.reason == reason)
            by_reason[reason.value] = count

        return {
            "total": total,
            "successful": success,
            "failed": total - success,
            "success_rate": round(success / total * 100, 2) if total > 0 else 0,
            "by_reason": by_reason
        }


# 全局实例
_global_rollback: Optional[AutoRollback] = None


def get_auto_rollback() -> AutoRollback:
    """获取全局回滚器"""
    global _global_rollback
    if _global_rollback is None:
        _global_rollback = AutoRollback()
    return _global_rollback
