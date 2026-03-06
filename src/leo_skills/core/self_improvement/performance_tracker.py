# -*- coding: utf-8 -*-
"""
效果追踪系统 (Performance Tracker)

追踪技能执行效果，收集反馈，生成优化建议。
"""

import json
import logging
import sqlite3
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


@dataclass
class ExecutionRecord:
    """执行记录"""
    id: str
    skill_name: str
    execution_time: str
    duration_ms: int
    success: bool
    error_message: Optional[str]
    input_summary: str
    output_summary: str
    user_feedback: Optional[str]
    context: Dict[str, Any]


@dataclass
class SkillMetrics:
    """技能指标"""
    skill_name: str
    total_executions: int
    successful_executions: int
    failed_executions: int
    success_rate: float
    avg_duration_ms: float
    last_execution: Optional[str]
    user_rating_avg: Optional[float]
    trend: str  # "improving", "stable", "declining"


class PerformanceTracker:
    """
    性能追踪器

    追踪技能执行效果，支持数据持久化和分析。
    """

    def __init__(self, db_path: Optional[Path] = None):
        """
        初始化追踪器

        Args:
            db_path: 数据库文件路径，默认在项目根目录
        """
        if db_path is None:
            project_root = Path(__file__).parent.parent.parent.parent.parent
            db_dir = project_root / "data"
            db_dir.mkdir(exist_ok=True)
            self.db_path = db_dir / "performance.db"
        else:
            self.db_path = Path(db_path)

        self._init_db()

    def _init_db(self):
        """初始化数据库"""
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS executions (
                    id TEXT PRIMARY KEY,
                    skill_name TEXT NOT NULL,
                    execution_time TEXT NOT NULL,
                    duration_ms INTEGER,
                    success INTEGER,
                    error_message TEXT,
                    input_summary TEXT,
                    output_summary TEXT,
                    user_feedback TEXT,
                    context TEXT
                )
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_skill_name ON executions(skill_name)
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_execution_time ON executions(execution_time)
            """)

            conn.commit()

    def record_execution(
        self,
        skill_name: str,
        success: bool,
        duration_ms: int = 0,
        input_summary: str = "",
        output_summary: str = "",
        error_message: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        记录执行

        Args:
            skill_name: 技能名称
            success: 是否成功
            duration_ms: 执行耗时
            input_summary: 输入摘要
            output_summary: 输出摘要
            error_message: 错误信息
            context: 上下文

        Returns:
            记录ID
        """
        record_id = f"{skill_name}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute(
                """
                INSERT INTO executions
                (id, skill_name, execution_time, duration_ms, success,
                 error_message, input_summary, output_summary, context)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record_id,
                    skill_name,
                    datetime.now().isoformat(),
                    duration_ms,
                    1 if success else 0,
                    error_message,
                    input_summary[:500],  # 限制长度
                    output_summary[:500],
                    json.dumps(context or {})
                )
            )
            conn.commit()

        logger.debug(f"Recorded execution: {record_id}")
        return record_id

    def add_user_feedback(self, record_id: str, feedback: str, rating: Optional[int] = None):
        """
        添加用户反馈

        Args:
            record_id: 执行记录ID
            feedback: 反馈内容
            rating: 评分 (1-5)
        """
        feedback_data = {
            "feedback": feedback,
            "rating": rating,
            "feedback_time": datetime.now().isoformat()
        }

        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute(
                "UPDATE executions SET user_feedback = ? WHERE id = ?",
                (json.dumps(feedback_data), record_id)
            )
            conn.commit()

    def get_skill_metrics(
        self,
        skill_name: str,
        days: int = 30
    ) -> SkillMetrics:
        """
        获取技能指标

        Args:
            skill_name: 技能名称
            days: 统计天数

        Returns:
            技能指标
        """
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()

        with sqlite3.connect(str(self.db_path)) as conn:
            # 基础统计
            cursor = conn.execute(
                """
                SELECT
                    COUNT(*),
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END),
                    AVG(duration_ms),
                    MAX(execution_time)
                FROM executions
                WHERE skill_name = ? AND execution_time > ?
                """,
                (skill_name, cutoff)
            )

            row = cursor.fetchone()
            total = row[0] or 0
            successful = row[1] or 0
            avg_duration = row[2] or 0
            last_exec = row[3]

            # 计算趋势
            trend = self._calculate_trend(conn, skill_name, days)

            # 计算平均评分
            cursor = conn.execute(
                """
                SELECT user_feedback FROM executions
                WHERE skill_name = ? AND execution_time > ? AND user_feedback IS NOT NULL
                """,
                (skill_name, cutoff)
            )

            ratings = []
            for row in cursor.fetchall():
                try:
                    fb = json.loads(row[0])
                    if fb.get("rating"):
                        ratings.append(fb["rating"])
                except:
                    pass

            avg_rating = sum(ratings) / len(ratings) if ratings else None

        return SkillMetrics(
            skill_name=skill_name,
            total_executions=total,
            successful_executions=successful,
            failed_executions=total - successful,
            success_rate=successful / total if total > 0 else 0.0,
            avg_duration_ms=avg_duration,
            last_execution=last_exec,
            user_rating_avg=avg_rating,
            trend=trend
        )

    def _calculate_trend(
        self,
        conn: sqlite3.Connection,
        skill_name: str,
        days: int
    ) -> str:
        """计算趋势"""
        # 对比前半段和后半段的成功率
        half_days = days // 2
        mid_point = (datetime.now() - timedelta(days=half_days)).isoformat()
        start_point = (datetime.now() - timedelta(days=days)).isoformat()

        cursor = conn.execute(
            """
            SELECT
                AVG(CASE WHEN execution_time > ? THEN success ELSE NULL END) as recent,
                AVG(CASE WHEN execution_time <= ? AND execution_time > ? THEN success ELSE NULL END) as past
            FROM executions
            WHERE skill_name = ? AND execution_time > ?
            """,
            (mid_point, mid_point, start_point, skill_name, start_point)
        )

        row = cursor.fetchone()
        recent_rate = row[0] or 0
        past_rate = row[1] or 0

        if recent_rate > past_rate + 0.1:
            return "improving"
        elif recent_rate < past_rate - 0.1:
            return "declining"
        else:
            return "stable"

    def get_top_skills(
        self,
        days: int = 30,
        limit: int = 10,
        min_executions: int = 5
    ) -> List[Dict[str, Any]]:
        """
        获取热门技能

        Args:
            days: 统计天数
            limit: 返回数量
            min_executions: 最小执行次数

        Returns:
            技能列表
        """
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()

        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.execute(
                """
                SELECT
                    skill_name,
                    COUNT(*) as total,
                    AVG(success) as success_rate,
                    AVG(duration_ms) as avg_duration
                FROM executions
                WHERE execution_time > ?
                GROUP BY skill_name
                HAVING COUNT(*) >= ?
                ORDER BY COUNT(*) DESC
                LIMIT ?
                """,
                (cutoff, min_executions, limit)
            )

            results = []
            for row in cursor.fetchall():
                results.append({
                    "skill_name": row[0],
                    "total_executions": row[1],
                    "success_rate": row[2],
                    "avg_duration_ms": row[3]
                })

        return results

    def get_problematic_skills(
        self,
        days: int = 7,
        min_executions: int = 3,
        max_success_rate: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        获取有问题的技能（成功率低）

        Args:
            days: 统计天数
            min_executions: 最小执行次数
            max_success_rate: 最大成功率阈值

        Returns:
            问题技能列表
        """
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()

        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.execute(
                """
                SELECT
                    skill_name,
                    COUNT(*) as total,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful,
                    AVG(success) as success_rate,
                    GROUP_CONCAT(DISTINCT error_message) as errors
                FROM executions
                WHERE execution_time > ? AND success = 0
                GROUP BY skill_name
                HAVING COUNT(*) >= ? AND AVG(success) <= ?
                ORDER BY AVG(success) ASC
                """,
                (cutoff, min_executions, max_success_rate)
            )

            results = []
            for row in cursor.fetchall():
                results.append({
                    "skill_name": row[0],
                    "total_executions": row[1],
                    "successful": row[2],
                    "success_rate": row[3],
                    "common_errors": row[4][:500] if row[4] else None
                })

        return results

    def generate_report(self, days: int = 7) -> Dict[str, Any]:
        """
        生成性能报告

        Args:
            days: 报告周期

        Returns:
            报告数据
        """
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()

        with sqlite3.connect(str(self.db_path)) as conn:
            # 总体统计
            cursor = conn.execute(
                """
                SELECT
                    COUNT(*),
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END),
                    AVG(duration_ms),
                    COUNT(DISTINCT skill_name)
                FROM executions
                WHERE execution_time > ?
                """,
                (cutoff,)
            )

            total, successful, avg_duration, unique_skills = cursor.fetchone()

            # 按天统计
            cursor = conn.execute(
                """
                SELECT
                    date(execution_time) as day,
                    COUNT(*) as count,
                    AVG(success) as rate
                FROM executions
                WHERE execution_time > ?
                GROUP BY day
                ORDER BY day
                """,
                (cutoff,)
            )

            daily_stats = [
                {"day": row[0], "executions": row[1], "success_rate": row[2]}
                for row in cursor.fetchall()
            ]

        # 热门技能
        top_skills = self.get_top_skills(days=days, limit=5)

        # 问题技能
        problematic = self.get_problematic_skills(days=days)

        return {
            "period_days": days,
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_executions": total or 0,
                "successful": successful or 0,
                "failed": (total or 0) - (successful or 0),
                "success_rate": (successful or 0) / total if total else 0,
                "avg_duration_ms": avg_duration or 0,
                "unique_skills": unique_skills or 0
            },
            "daily_stats": daily_stats,
            "top_skills": top_skills,
            "problematic_skills": problematic,
            "recommendations": self._generate_recommendations(problematic)
        }

    def _generate_recommendations(
        self,
        problematic: List[Dict[str, Any]]
    ) -> List[str]:
        """生成优化建议"""
        recommendations = []

        for skill in problematic:
            name = skill["skill_name"]
            rate = skill["success_rate"]

            if rate < 0.3:
                recommendations.append(
                    f"🔴 技能 '{name}' 成功率仅 {rate:.1%}，建议重新设计或修复"
                )
            elif rate < 0.7:
                recommendations.append(
                    f"🟡 技能 '{name}' 成功率 {rate:.1%}，建议查看错误日志并优化"
                )

        return recommendations

    def export_to_json(self, output_path: Optional[Path] = None) -> Path:
        """
        导出所有数据到 JSON

        Args:
            output_path: 输出路径

        Returns:
            输出文件路径
        """
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = Path(f"performance_export_{timestamp}.json")

        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.execute("SELECT * FROM executions ORDER BY execution_time DESC")

            columns = [description[0] for description in cursor.description]
            records = []

            for row in cursor.fetchall():
                record = dict(zip(columns, row))
                # 解析 JSON 字段
                if record.get("context"):
                    try:
                        record["context"] = json.loads(record["context"])
                    except:
                        pass
                if record.get("user_feedback"):
                    try:
                        record["user_feedback"] = json.loads(record["user_feedback"])
                    except:
                        pass
                records.append(record)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=2)

        logger.info(f"Exported {len(records)} records to {output_path}")
        return output_path


# 便捷函数
def track_execution(skill_name: str, success: bool, **kwargs) -> str:
    """快速追踪入口"""
    tracker = PerformanceTracker()
    return tracker.record_execution(skill_name, success, **kwargs)


def get_skill_performance(skill_name: str, days: int = 30) -> SkillMetrics:
    """获取技能性能指标"""
    tracker = PerformanceTracker()
    return tracker.get_skill_metrics(skill_name, days)


if __name__ == "__main__":
    # 测试
    tracker = PerformanceTracker()

    # 模拟记录
    track_execution("test_skill", True, duration_ms=100)
    track_execution("test_skill", False, duration_ms=200, error_message="Test error")

    # 查看报告
    report = tracker.generate_report(days=1)
    print(f"Total executions: {report['summary']['total_executions']}")
    print(f"Success rate: {report['summary']['success_rate']:.1%}")
