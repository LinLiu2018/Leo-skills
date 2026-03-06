# -*- coding: utf-8 -*-
"""
补偿事务模块

确保操作最终一致性
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


class TransactionStatus(str, Enum):
    """事务状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMMITTED = "committed"
    COMPENSATED = "compensated"
    FAILED = "failed"


@dataclass
class Operation:
    """操作"""
    op_id: str
    name: str
    action: Callable
    compensation: Optional[Callable] = None
    params: Dict[str, Any] = field(default_factory=dict)
    result: Any = None
    error: str = ""
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Transaction:
    """事务"""
    tx_id: str
    status: TransactionStatus = TransactionStatus.PENDING
    operations: List[Operation] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    committed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "tx_id": self.tx_id,
            "status": self.status.value,
            "operations": [
                {
                    "op_id": op.op_id,
                    "name": op.name,
                    "result": str(op.result)[:100],
                    "error": op.error
                }
                for op in self.operations
            ],
            "created_at": self.created_at.isoformat(),
            "committed_at": self.committed_at.isoformat() if self.committed_at else None,
            "metadata": self.metadata
        }


class CompensationManager:
    """
    补偿事务管理器

    功能：
    - 记录操作链
    - 自动补偿失败
    - 事务日志审计
    """

    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = storage_path or ".leo_transactions"
        self.active_transactions: Dict[str, Transaction] = {}
        self.transaction_history: List[Transaction] = []

        # 创建存储目录
        Path(self.storage_path).mkdir(parents=True, exist_ok=True)

    # ========== 事务管理 ==========

    def begin_transaction(
        self,
        tx_id: str,
        metadata: Optional[Dict] = None
    ) -> Transaction:
        """
        开始事务

        Args:
            tx_id: 事务ID
            metadata: 事务元数据

        Returns:
            事务对象
        """
        tx = Transaction(
            tx_id=tx_id,
            metadata=metadata or {}
        )

        self.active_transactions[tx_id] = tx

        return tx

    def add_operation(
        self,
        tx_id: str,
        op_id: str,
        name: str,
        action: Callable,
        compensation: Optional[Callable] = None,
        params: Optional[Dict] = None
    ) -> Operation:
        """
        添加操作到事务

        Args:
            tx_id: 事务ID
            op_id: 操作ID
            name: 操作名称
            action: 执行函数
            compensation: 补偿函数
            params: 参数

        Returns:
            操作对象
        """
        tx = self.active_transactions.get(tx_id)
        if not tx:
            raise ValueError(f"Transaction not found: {tx_id}")

        op = Operation(
            op_id=op_id,
            name=name,
            action=action,
            compensation=compensation,
            params=params or {}
        )

        tx.operations.append(op)
        tx.status = TransactionStatus.RUNNING

        return op

    def commit(self, tx_id: str) -> bool:
        """
        提交事务

        Args:
            tx_id: 事务ID

        Returns:
            是否成功
        """
        tx = self.active_transactions.get(tx_id)
        if not tx:
            raise ValueError(f"Transaction not found: {tx_id}")

        try:
            # 验证所有操作都成功
            for op in tx.operations:
                if op.error:
                    raise ValueError(f"Operation {op.op_id} has error: {op.error}")

            tx.status = TransactionStatus.COMMITTED
            tx.committed_at = datetime.now()

            # 保存到历史
            self.transaction_history.append(tx)

            # 清理活跃事务
            del self.active_transactions[tx_id]

            # 持久化
            self._persist_transaction(tx)

            return True

        except Exception as e:
            # 失败则回滚
            self.compensate(tx_id)
            return False

    def compensate(self, tx_id: str) -> bool:
        """
        执行补偿

        Args:
            tx_id: 事务ID

        Returns:
            是否成功
        """
        tx = self.active_transactions.get(tx_id)
        if not tx:
            # 尝试从历史中获取
            for t in reversed(self.transaction_history):
                if t.tx_id == tx_id:
                    tx = t
                    break

            if not tx:
                raise ValueError(f"Transaction not found: {tx_id}")

        try:
            # 逆序执行补偿
            for op in reversed(tx.operations):
                if op.compensation:
                    try:
                        op.compensation(op.result, **op.params)
                    except Exception as e:
                        op.error = str(e)

            tx.status = TransactionStatus.COMPENSATED

            # 如果是活跃事务，清理
            if tx_id in self.active_transactions:
                del self.active_transactions[tx_id]

            # 保存到历史
            if tx not in self.transaction_history:
                self.transaction_history.append(tx)

            return True

        except Exception as e:
            tx.status = TransactionStatus.FAILED
            return False

    def rollback(self, tx_id: str) -> bool:
        """
        回滚事务

        Args:
            tx_id: 事务ID

        Returns:
            是否成功
        """
        return self.compensate(tx_id)

    # ========== 便捷方法 ==========

    def execute_with_transaction(
        self,
        tx_id: str,
        operations: List[Dict[str, Any]],
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        执行带事务的操作

        Args:
            tx_id: 事务ID
            operations: 操作列表，格式：
                [
                    {
                        "name": "op1",
                        "action": func,
                        "compensation": comp_func,
                        "params": {...}
                    },
                    ...
                ]
            metadata: 事务元数据

        Returns:
            执行结果
        """
        # 开始事务
        self.begin_transaction(tx_id, metadata)

        try:
            # 添加并执行操作
            for i, op_spec in enumerate(operations):
                op_id = f"op_{i}"

                # 执行操作
                action = op_spec.get("action")
                params = op_spec.get("params", {})

                op = self.add_operation(
                    tx_id=tx_id,
                    op_id=op_id,
                    name=op_spec.get("name", op_id),
                    action=action,
                    compensation=op_spec.get("compensation"),
                    params=params
                )

                try:
                    # 执行
                    if action:
                        op.result = action(**params)
                    else:
                        op.result = None
                except Exception as e:
                    op.error = str(e)
                    # 失败，补偿
                    self.compensate(tx_id)
                    return {
                        "success": False,
                        "tx_id": tx_id,
                        "failed_at": op_id,
                        "error": str(e)
                    }

            # 提交
            self.commit(tx_id)

            return {
                "success": True,
                "tx_id": tx_id,
                "operations": len(operations)
            }

        except Exception as e:
            self.compensate(tx_id)
            return {
                "success": False,
                "tx_id": tx_id,
                "error": str(e)
            }

    # ========== 查询 ==========

    def get_transaction(self, tx_id: str) -> Optional[Transaction]:
        """获取事务"""
        # 活跃事务
        if tx_id in self.active_transactions:
            return self.active_transactions[tx_id]

        # 历史事务
        for tx in reversed(self.transaction_history):
            if tx.tx_id == tx_id:
                return tx

        return None

    def get_active_transactions(self) -> List[Transaction]:
        """获取活跃事务"""
        return list(self.active_transactions.values())

    def get_transaction_history(
        self,
        status: Optional[TransactionStatus] = None,
        limit: int = 50
    ) -> List[Transaction]:
        """获取事务历史"""
        history = self.transaction_history

        if status:
            history = [tx for tx in history if tx.status == status]

        return history[-limit:]

    def get_transaction_stats(self) -> Dict[str, Any]:
        """获取事务统计"""
        total = len(self.transaction_history)
        committed = sum(
            1 for tx in self.transaction_history
            if tx.status == TransactionStatus.COMMITTED
        )
        compensated = sum(
            1 for tx in self.transaction_history
            if tx.status == TransactionStatus.COMPENSATED
        )
        failed = sum(
            1 for tx in self.transaction_history
            if tx.status == TransactionStatus.FAILED
        )

        return {
            "total": total,
            "committed": committed,
            "compensated": compensated,
            "failed": failed,
            "active": len(self.active_transactions),
            "success_rate": round(committed / total * 100, 2) if total > 0 else 0
        }

    # ========== 持久化 ==========

    def _persist_transaction(self, tx: Transaction):
        """持久化事务"""
        date_str = datetime.now().strftime("%Y%m%d")
        file_path = Path(self.storage_path) / f"tx_{date_str}.jsonl"

        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(tx.to_dict(), ensure_ascii=False) + "\n")

    def load_transactions(self, date: Optional[str] = None) -> List[Transaction]:
        """加载指定日期的事务"""
        date_str = date or datetime.now().strftime("%Y%m%d")
        file_path = Path(self.storage_path) / f"tx_{date_str}.jsonl"

        if not file_path.exists():
            return []

        transactions = []

        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue

                data = json.loads(line)
                tx = Transaction(
                    tx_id=data["tx_id"],
                    status=TransactionStatus(data["status"]),
                    created_at=datetime.fromisoformat(data["created_at"]),
                    metadata=data.get("metadata", {})
                )

                if data.get("committed_at"):
                    tx.committed_at = datetime.fromisoformat(data["committed_at"])

                transactions.append(tx)

        return transactions


# 全局实例
_global_compensation_manager: Optional[CompensationManager] = None


def get_compensation_manager() -> CompensationManager:
    """获取全局补偿管理器"""
    global _global_compensation_manager
    if _global_compensation_manager is None:
        _global_compensation_manager = CompensationManager()
    return _global_compensation_manager
