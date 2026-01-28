#!/usr/bin/env python3
"""
Leo System - 技能使用统计模块
=============================
提供技能使用统计、分析和优化建议功能

功能：
1. 技能调用次数统计
2. 成功率分析
3. 执行时间分析
4. 低频技能识别
5. 优化建议生成
"""

import json
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from .logger import get_logger

# 统计数据存储目录
STATS_DIR = Path(__file__).parent.parent / "logs" / "stats"
STATS_DIR.mkdir(parents=True, exist_ok=True)

# 日志记录器
logger = get_logger(__name__)


@dataclass
class SkillStats:
    """技能统计数据"""
    skill_name: str
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    total_execution_time: float = 0.0
    avg_execution_time: float = 0.0
    last_called: Optional[str] = None
    actions: Dict[str, int] = field(default_factory=dict)
    error_types: Dict[str, int] = field(default_factory=dict)

    @property
    def success_rate(self) -> float:
        """成功率"""
        if self.total_calls == 0:
            return 0.0
        return (self.successful_calls / self.total_calls) * 100

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        data["success_rate"] = self.success_rate
        return data


class SkillUsageTracker:
    """
    技能使用追踪器
    ==============
    追踪和分析技能使用情况
    """

    def __init__(self):
        """初始化追踪器"""
        self.stats: Dict[str, SkillStats] = {}
        self.daily_stats: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self._load_stats()

    def _load_stats(self) -> None:
        """加载历史统计数据"""
        stats_file = STATS_DIR / "skill_usage_stats.json"
        if stats_file.exists():
            try:
                with open(stats_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for skill_name, skill_data in data.get("skills", {}).items():
                        self.stats[skill_name] = SkillStats(
                            skill_name=skill_name,
                            total_calls=skill_data.get("total_calls", 0),
                            successful_calls=skill_data.get("successful_calls", 0),
                            failed_calls=skill_data.get("failed_calls", 0),
                            total_execution_time=skill_data.get("total_execution_time", 0.0),
                            avg_execution_time=skill_data.get("avg_execution_time", 0.0),
                            last_called=skill_data.get("last_called"),
                            actions=skill_data.get("actions", {}),
                            error_types=skill_data.get("error_types", {}),
                        )
            except Exception as e:
                logger.warning(f"加载统计数据失败: {e}")

    def save_stats(self) -> None:
        """保存统计数据"""
        stats_file = STATS_DIR / "skill_usage_stats.json"
        data = {
            "updated_at": datetime.now().isoformat(),
            "skills": {name: stats.to_dict() for name, stats in self.stats.items()},
        }
        with open(stats_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def record_call(
        self,
        skill_name: str,
        action: str,
        success: bool,
        execution_time: float,
        error_type: Optional[str] = None,
    ) -> None:
        """
        记录技能调用

        Args:
            skill_name: 技能名称
            action: 动作名称
            success: 是否成功
            execution_time: 执行时间
            error_type: 错误类型（如果失败）
        """
        # 初始化统计
        if skill_name not in self.stats:
            self.stats[skill_name] = SkillStats(skill_name=skill_name)

        stats = self.stats[skill_name]

        # 更新统计
        stats.total_calls += 1
        if success:
            stats.successful_calls += 1
        else:
            stats.failed_calls += 1
            if error_type:
                stats.error_types[error_type] = stats.error_types.get(error_type, 0) + 1

        stats.total_execution_time += execution_time
        stats.avg_execution_time = stats.total_execution_time / stats.total_calls
        stats.last_called = datetime.now().isoformat()

        # 记录动作
        stats.actions[action] = stats.actions.get(action, 0) + 1

        # 记录每日统计
        today = datetime.now().strftime("%Y-%m-%d")
        self.daily_stats[today][skill_name] += 1

        # 自动保存（每10次调用保存一次）
        if sum(s.total_calls for s in self.stats.values()) % 10 == 0:
            self.save_stats()

    def get_skill_stats(self, skill_name: str) -> Optional[SkillStats]:
        """获取单个技能的统计"""
        return self.stats.get(skill_name)

    def get_all_stats(self) -> Dict[str, SkillStats]:
        """获取所有技能统计"""
        return self.stats

    def get_top_skills(self, n: int = 10) -> List[SkillStats]:
        """
        获取使用最多的技能

        Args:
            n: 返回数量

        Returns:
            技能统计列表
        """
        sorted_stats = sorted(
            self.stats.values(),
            key=lambda x: x.total_calls,
            reverse=True
        )
        return sorted_stats[:n]

    def get_low_usage_skills(self, threshold: int = 5) -> List[SkillStats]:
        """
        获取低频使用的技能

        Args:
            threshold: 调用次数阈值

        Returns:
            低频技能列表
        """
        return [
            stats for stats in self.stats.values()
            if stats.total_calls < threshold
        ]

    def get_low_success_rate_skills(self, threshold: float = 80.0) -> List[SkillStats]:
        """
        获取成功率低的技能

        Args:
            threshold: 成功率阈值（百分比）

        Returns:
            低成功率技能列表
        """
        return [
            stats for stats in self.stats.values()
            if stats.total_calls > 0 and stats.success_rate < threshold
        ]

    def get_slow_skills(self, threshold: float = 5.0) -> List[SkillStats]:
        """
        获取执行慢的技能

        Args:
            threshold: 平均执行时间阈值（秒）

        Returns:
            慢技能列表
        """
        return [
            stats for stats in self.stats.values()
            if stats.avg_execution_time > threshold
        ]

    def generate_report(self) -> Dict[str, Any]:
        """
        生成使用报告

        Returns:
            使用报告
        """
        total_calls = sum(s.total_calls for s in self.stats.values())
        total_success = sum(s.successful_calls for s in self.stats.values())

        return {
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_skills": len(self.stats),
                "total_calls": total_calls,
                "total_success": total_success,
                "overall_success_rate": (total_success / total_calls * 100) if total_calls > 0 else 0,
            },
            "top_skills": [s.to_dict() for s in self.get_top_skills(5)],
            "low_usage_skills": [s.skill_name for s in self.get_low_usage_skills()],
            "low_success_rate_skills": [
                {"name": s.skill_name, "rate": s.success_rate}
                for s in self.get_low_success_rate_skills()
            ],
            "slow_skills": [
                {"name": s.skill_name, "avg_time": s.avg_execution_time}
                for s in self.get_slow_skills()
            ],
        }

    def generate_optimization_suggestions(self) -> List[Dict[str, str]]:
        """
        生成优化建议

        Returns:
            优化建议列表
        """
        suggestions = []

        # 低频技能建议
        low_usage = self.get_low_usage_skills()
        if low_usage:
            suggestions.append({
                "type": "low_usage",
                "priority": "low",
                "title": "低频技能",
                "description": f"以下 {len(low_usage)} 个技能使用频率较低，考虑是否需要保留或整合",
                "skills": [s.skill_name for s in low_usage],
            })

        # 低成功率建议
        low_success = self.get_low_success_rate_skills()
        if low_success:
            suggestions.append({
                "type": "low_success_rate",
                "priority": "high",
                "title": "低成功率技能",
                "description": f"以下 {len(low_success)} 个技能成功率低于80%，需要优化",
                "skills": [{"name": s.skill_name, "rate": f"{s.success_rate:.1f}%"} for s in low_success],
            })

        # 慢技能建议
        slow = self.get_slow_skills()
        if slow:
            suggestions.append({
                "type": "slow_execution",
                "priority": "medium",
                "title": "执行缓慢技能",
                "description": f"以下 {len(slow)} 个技能平均执行时间超过5秒，考虑优化",
                "skills": [{"name": s.skill_name, "avg_time": f"{s.avg_execution_time:.2f}s"} for s in slow],
            })

        return suggestions


# ==================== 全局实例 ====================

_global_tracker: Optional[SkillUsageTracker] = None


def get_usage_tracker() -> SkillUsageTracker:
    """获取全局使用追踪器"""
    global _global_tracker
    if _global_tracker is None:
        _global_tracker = SkillUsageTracker()
    return _global_tracker


# ==================== 便捷函数 ====================

def record_skill_call(
    skill_name: str,
    action: str,
    success: bool,
    execution_time: float,
    error_type: Optional[str] = None,
) -> None:
    """记录技能调用"""
    get_usage_tracker().record_call(skill_name, action, success, execution_time, error_type)


def get_skill_report() -> Dict[str, Any]:
    """获取技能使用报告"""
    return get_usage_tracker().generate_report()


def get_optimization_suggestions() -> List[Dict[str, str]]:
    """获取优化建议"""
    return get_usage_tracker().generate_optimization_suggestions()


def print_skill_report() -> None:
    """打印技能使用报告"""
    report = get_skill_report()

    print("\n" + "=" * 60)
    print("技能使用统计报告")
    print("=" * 60)

    summary = report["summary"]
    print(f"\n总技能数: {summary['total_skills']}")
    print(f"总调用次数: {summary['total_calls']}")
    print(f"总成功次数: {summary['total_success']}")
    print(f"整体成功率: {summary['overall_success_rate']:.1f}%")

    print("\n--- Top 5 技能 ---")
    for i, skill in enumerate(report["top_skills"], 1):
        print(f"{i}. {skill['skill_name']}: {skill['total_calls']}次 (成功率: {skill['success_rate']:.1f}%)")

    if report["low_usage_skills"]:
        print(f"\n--- 低频技能 ({len(report['low_usage_skills'])}个) ---")
        print(", ".join(report["low_usage_skills"][:5]))

    if report["low_success_rate_skills"]:
        print(f"\n--- 低成功率技能 ---")
        for skill in report["low_success_rate_skills"]:
            print(f"  - {skill['name']}: {skill['rate']:.1f}%")

    print("\n" + "=" * 60)
