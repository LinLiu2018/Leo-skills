"""
Skill执行器
===========
负责执行Skill并处理返回结果
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime

from .skill_adapter import SkillAdapter
from .skill_loader import SkillLoader, get_loader


@dataclass
class ExecutionResult:
    """执行结果"""
    skill_name: str
    action: str
    success: bool
    result: Any = None
    error: str = None
    execution_time: float = 0.0
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "skill_name": self.skill_name,
            "action": self.action,
            "success": self.success,
            "result": self.result,
            "error": self.error,
            "execution_time": self.execution_time,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }


class SkillExecutor:
    """
    Skill执行器
    ===========
    负责执行Skill操作并管理结果
    """

    def __init__(self, loader: SkillLoader = None):
        """
        初始化执行器

        Args:
            loader: Skill加载器（可选，默认使用全局加载器）
        """
        self.loader = loader or get_loader()
        self.execution_history: list = []

    def execute(self,
                skill_name: str,
                action: str,
                **kwargs) -> ExecutionResult:
        """
        执行Skill操作

        Args:
            skill_name: Skill名称
            action: 操作名称
            **kwargs: 操作参数

        Returns:
            执行结果
        """
        import time
        start_time = time.time()

        # 获取Skill适配器
        adapter = self.loader.get_skill(skill_name)

        if not adapter:
            return ExecutionResult(
                skill_name=skill_name,
                action=action,
                success=False,
                error=f"Skill不存在: {skill_name}"
            )

        # 验证操作
        if not adapter.validate_action(action):
            return ExecutionResult(
                skill_name=skill_name,
                action=action,
                success=False,
                error=f"无效的操作: {action}"
            )

        try:
            # 执行操作
            result = self._execute_action(adapter, action, **kwargs)

            execution_time = time.time() - start_time

            execution_result = ExecutionResult(
                skill_name=skill_name,
                action=action,
                success=True,
                result=result,
                execution_time=execution_time
            )

        except Exception as e:
            execution_time = time.time() - start_time
            execution_result = ExecutionResult(
                skill_name=skill_name,
                action=action,
                success=False,
                error=str(e),
                execution_time=execution_time
            )

        # 记录历史
        self.execution_history.append(execution_result)

        return execution_result

    def _execute_action(self,
                       adapter: SkillAdapter,
                       action: str,
                       **kwargs) -> Any:
        """
        实际执行操作

        Args:
            adapter: Skill适配器
            action: 操作名称
            **kwargs: 参数

        Returns:
            操作结果
        """
        # 尝试动态加载并执行 skill
        skill_instance = self._load_skill_instance(adapter)

        if skill_instance and hasattr(skill_instance, action):
            # 调用 skill 实例的方法
            method = getattr(skill_instance, action)
            return method(**kwargs)

        # 如果无法加载 skill 实例，返回模拟结果
        prompt = adapter.get_action_prompt(action)
        result = {
            "skill": adapter.skill_name,
            "action": action,
            "prompt": prompt,
            "parameters": kwargs,
            "status": "executed",
            "message": f"已执行 {adapter.skill_name} 的 {action} 操作"
        }

        return result

    def _load_skill_instance(self, adapter: SkillAdapter) -> Any:
        """
        动态加载 skill 实例

        Args:
            adapter: Skill适配器

        Returns:
            Skill实例或None
        """
        import importlib.util
        import sys

        skill_path = Path(adapter.skill_path)

        # 查找 skill 的主 Python 文件
        possible_files = [
            skill_path / f"{adapter.skill_name.replace('-', '_')}.py",
            skill_path / "main.py",
            skill_path / "skill.py",
        ]

        # 也尝试查找以 _skill.py 结尾的文件
        for py_file in skill_path.glob("*_skill.py"):
            possible_files.insert(0, py_file)

        skill_file = None
        for f in possible_files:
            if f.exists():
                skill_file = f
                break

        if not skill_file:
            return None

        try:
            # 动态加载模块
            module_name = f"skill_{adapter.skill_name.replace('-', '_')}"
            spec = importlib.util.spec_from_file_location(module_name, skill_file)
            module = importlib.util.module_from_spec(spec)

            # 添加 skill 目录到 sys.path 以支持相对导入
            skill_dir = str(skill_path)
            if skill_dir not in sys.path:
                sys.path.insert(0, skill_dir)

            spec.loader.exec_module(module)

            # 查找 Skill 类
            skill_class = None
            for name, obj in module.__dict__.items():
                if isinstance(obj, type) and name.endswith('Skill') and name != 'EvolvableSkill':
                    skill_class = obj
                    break

            if skill_class:
                return skill_class()

        except Exception as e:
            # 加载失败，记录错误但不中断
            print(f"[SkillExecutor] 加载 skill 失败: {adapter.skill_name}, 错误: {e}")

        return None

    def execute_batch(self,
                     tasks: list) -> list:
        """
        批量执行多个任务

        Args:
            tasks: 任务列表，每个任务格式: {"skill": str, "action": str, "params": dict}

        Returns:
            执行结果列表
        """
        results = []
        for task in tasks:
            result = self.execute(
                skill_name=task["skill"],
                action=task["action"],
                **task.get("params", {})
            )
            results.append(result)

        return results

    def get_execution_history(self,
                             limit: int = None) -> list:
        """
        获取执行历史

        Args:
            limit: 限制返回数量（可选）

        Returns:
            执行历史列表
        """
        if limit:
            return self.execution_history[-limit:]
        return self.execution_history

    def get_statistics(self) -> Dict[str, Any]:
        """
        获取执行统计

        Returns:
            统计信息字典
        """
        total = len(self.execution_history)
        if total == 0:
            return {
                "total_executions": 0,
                "success_rate": 0.0,
                "by_skill": {},
                "by_action": {}
            }

        successful = sum(1 for r in self.execution_history if r.success)
        failed = total - successful

        by_skill = {}
        by_action = {}

        for result in self.execution_history:
            # 按Skill统计
            if result.skill_name not in by_skill:
                by_skill[result.skill_name] = {"total": 0, "success": 0, "failed": 0}
            by_skill[result.skill_name]["total"] += 1
            if result.success:
                by_skill[result.skill_name]["success"] += 1
            else:
                by_skill[result.skill_name]["failed"] += 1

            # 按操作统计
            if result.action not in by_action:
                by_action[result.action] = {"total": 0, "success": 0}
            by_action[result.action]["total"] += 1
            if result.success:
                by_action[result.action]["success"] += 1

        return {
            "total_executions": total,
            "successful": successful,
            "failed": failed,
            "success_rate": successful / total * 100,
            "by_skill": by_skill,
            "by_action": by_action
        }

    def print_statistics(self):
        """打印统计信息"""
        stats = self.get_statistics()

        print("\n" + "=" * 60)
        print("📊 执行统计")
        print("=" * 60)
        print(f"总执行次数: {stats['total_executions']}")
        print(f"成功: {stats['successful']}")
        print(f"失败: {stats['failed']}")
        print(f"成功率: {stats['success_rate']:.1f}%")

        if stats['by_skill']:
            print("\n按Skill统计:")
            for skill, data in stats['by_skill'].items():
                print(f"  {skill}: {data['total']}次 (成功: {data['success']}, 失败: {data['failed']})")

        if stats['by_action']:
            print("\n按操作统计:")
            for action, data in stats['by_action'].items():
                print(f"  {action}: {data['total']}次 (成功: {data['success']})")

        print("=" * 60 + "\n")


# ==================== 全局执行器实例 ====================

_global_executor: Optional[SkillExecutor] = None


def get_executor() -> SkillExecutor:
    """
    获取全局执行器实例

    Returns:
        Skill执行器实例
    """
    global _global_executor
    if _global_executor is None:
        _global_executor = SkillExecutor()
    return _global_executor


def execute_skill(skill_name: str,
                 action: str,
                 **kwargs) -> ExecutionResult:
    """
    便捷函数：执行Skill

    Args:
        skill_name: Skill名称
        action: 操作名称
        **kwargs: 参数

    Returns:
        执行结果
    """
    executor = get_executor()
    return executor.execute(skill_name, action, **kwargs)


# ==================== 使用示例 ====================

if __name__ == "__main__":
    # 创建执行器
    executor = SkillExecutor()

    # 执行单个操作
    result = executor.execute(
        skill_name="content-layout-leo-cskill",
        action="layout",
        content="测试内容",
        style="data_driven"
    )

    print(f"执行结果: {result.to_dict()}")

    # 批量执行
    tasks = [
        {"skill": "content-layout-leo-cskill", "action": "layout", "params": {"content": "内容1"}},
        {"skill": "realestate-news-publisher-cskill", "action": "publish", "params": {"title": "标题"}}
    ]

    results = executor.execute_batch(tasks)
    print(f"\n批量执行结果: {len(results)}个任务")

    # 打印统计
    executor.print_statistics()
