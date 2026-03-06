# -*- coding: utf-8 -*-
"""
调度器管理界面 API

提供任务管理和监控的 REST API
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional


class SchedulerDashboard:
    """
    调度器管理界面

    提供：
    - 任务概览
    - 实时状态
    - 执行统计
    - 日志查询
    """

    def __init__(self, scheduler):
        """
        初始化仪表板

        Args:
            scheduler: UnifiedScheduler 实例
        """
        self.scheduler = scheduler

    def get_overview(self) -> Dict[str, Any]:
        """
        获取任务概览

        Returns:
            概览数据
        """
        tasks = self.scheduler.registry.list_all()
        enabled_tasks = [t for t in tasks if t.enabled]

        # 统计
        stats = {
            "total": len(tasks),
            "enabled": len(enabled_tasks),
            "disabled": len(tasks) - len(enabled_tasks),
            "running": 0,
            "success": 0,
            "failed": 0,
            "pending": 0,
        }

        for task in tasks:
            status = task.status.value
            if status in stats:
                stats[status] += 1

        return {
            "stats": stats,
            "scheduler_running": self.scheduler._running,
            "timestamp": datetime.now().isoformat()
        }

    def get_task_detail(self, task_id: str) -> Dict[str, Any]:
        """
        获取任务详情

        Args:
            task_id: 任务ID

        Returns:
            任务详情
        """
        task = self.scheduler.registry.get(task_id)
        if not task:
            return {"error": f"Task not found: {task_id}"}

        # 获取该任务的执行历史
        history = [
            r for r in self.scheduler.execution_records
            if r.task_id == task_id
        ]
        history = sorted(history, key=lambda x: x.start_time, reverse=True)
        history = history[:20]

        return {
            "task": task.to_dict(),
            "history": [r.to_dict() for r in history],
            "stats": self._calculate_task_stats(history)
        }

    def _calculate_task_stats(self, history: List) -> Dict[str, Any]:
        """计算任务统计"""
        if not history:
            return {
                "total_runs": 0,
                "success_rate": 0,
                "avg_duration_ms": 0,
                "last_run": None
            }

        total = len(history)
        success = sum(1 for r in history if r.status.value == "success")
        failed = sum(1 for r in history if r.status.value == "failed")

        durations = [
            (r.end_time - r.start_time).total_seconds() * 1000
            for r in history
            if r.end_time
        ]

        return {
            "total_runs": total,
            "success": success,
            "failed": failed,
            "success_rate": round(success / total * 100, 2) if total > 0 else 0,
            "avg_duration_ms": round(sum(durations) / len(durations), 2) if durations else 0,
            "min_duration_ms": min(durations) if durations else 0,
            "max_duration_ms": max(durations) if durations else 0,
            "last_run": history[0].start_time.isoformat() if history else None
        }

    def get_upcoming_tasks(self, limit: int = 10) -> Dict[str, Any]:
        """
        获取即将执行的任务

        Args:
            limit: 返回数量限制

        Returns:
            即将执行的任务列表
        """
        tasks = self.scheduler.registry.list_enabled()
        now = datetime.now()

        upcoming = [
            {
                "task_id": t.task_id,
                "name": t.name,
                "next_run": t.next_run.isoformat() if t.next_run else None,
                "delay_seconds": (t.next_run - now).total_seconds() if t.next_run else None
            }
            for t in tasks
            if t.next_run and t.next_run > now
        ]

        upcoming.sort(key=lambda x: x.get("delay_seconds", float('inf')))
        upcoming = upcoming[:limit]

        return {
            "upcoming": upcoming,
            "count": len(upcoming)
        }

    def get_recent_executions(self, limit: int = 20) -> Dict[str, Any]:
        """
        获取最近执行记录

        Args:
            limit: 返回数量限制

        Returns:
            执行记录列表
        """
        records = self.scheduler.execution_records
        records = sorted(records, key=lambda x: x.start_time, reverse=True)
        records = records[:limit]

        return {
            "executions": [r.to_dict() for r in records],
            "count": len(records)
        }

    def get_execution_timeline(
        self,
        hours: int = 24,
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取执行时间线

        Args:
            hours: 回溯小时数
            task_id: 可选的任务ID筛选

        Returns:
            时间线数据
        """
        since = datetime.now() - timedelta(hours=hours)

        records = [
            r for r in self.scheduler.execution_records
            if r.start_time >= since
        ]

        if task_id:
            records = [r for r in records if r.task_id == task_id]

        # 按小时分组
        timeline = {}
        for record in records:
            hour_key = record.start_time.strftime("%Y-%m-%d %H:00")

            if hour_key not in timeline:
                timeline[hour_key] = {
                    "total": 0,
                    "success": 0,
                    "failed": 0,
                    "tasks": set()
                }

            timeline[hour_key]["total"] += 1
            if record.status.value == "success":
                timeline[hour_key]["success"] += 1
            elif record.status.value == "failed":
                timeline[hour_key]["failed"] += 1
            timeline[hour_key]["tasks"].add(record.task_id)

        # 转换为列表
        result = []
        for hour, data in sorted(timeline.items()):
            result.append({
                "hour": hour,
                "total": data["total"],
                "success": data["success"],
                "failed": data["failed"],
                "success_rate": round(
                    data["success"] / data["total"] * 100, 2
                ) if data["total"] > 0 else 0,
                "unique_tasks": len(data["tasks"])
            })

        return {
            "timeline": result,
            "period_hours": hours,
            "total_executions": len(records)
        }

    def get_failed_tasks(self, since_hours: int = 24) -> Dict[str, Any]:
        """
        获取失败的任务

        Args:
            since_hours: 回溯小时数

        Returns:
            失败任务列表
        """
        since = datetime.now() - timedelta(hours=since_hours)

        failed = [
            r for r in self.scheduler.execution_records
            if r.start_time >= since
            and r.status.value == "failed"
        ]

        # 按任务分组
        failed_by_task = {}
        for record in failed:
            if record.task_id not in failed_by_task:
                failed_by_task[record.task_id] = []
            failed_by_task[record.task_id].append(record)

        # 转换为列表
        result = []
        for task_id, records in failed_by_task.items():
            task = self.scheduler.registry.get(task_id)
            result.append({
                "task_id": task_id,
                "task_name": task.name if task else "Unknown",
                "failure_count": len(records),
                "last_error": records[-1].error,
                "last_attempt": records[-1].start_time.isoformat()
            })

        # 按失败次数排序
        result.sort(key=lambda x: x["failure_count"], reverse=True)

        return {
            "failed_tasks": result,
            "total_failures": len(failed),
            "period_hours": since_hours
        }

    def get_task_health(self) -> Dict[str, Any]:
        """
        获取任务健康状态

        Returns:
            健康状态数据
        """
        tasks = self.scheduler.registry.list_all()

        healthy = []
        warning = []
        critical = []

        for task in tasks:
            # 获取该任务的最近执行
            task_history = [
                r for r in self.scheduler.execution_records
                if r.task_id == task.task_id
            ]
            task_history = sorted(task_history, key=lambda x: x.start_time, reverse=True)
            task_history = task_history[:10]

            if not task_history:
                status = "unknown"
            else:
                recent_failures = sum(
                    1 for r in task_history
                    if r.status.value == "failed"
                )

                if recent_failures == 0:
                    status = "healthy"
                elif recent_failures <= 2:
                    status = "warning"
                else:
                    status = "critical"

            entry = {
                "task_id": task.task_id,
                "task_name": task.name,
                "status": status,
                "enabled": task.enabled,
                "recent_failures": recent_failures,
                "total_runs": len(task_history)
            }

            if status == "healthy":
                healthy.append(entry)
            elif status == "warning":
                warning.append(entry)
            else:
                critical.append(entry)

        return {
            "healthy": healthy,
            "warning": warning,
            "critical": critical,
            "unknown": [t for t in tasks if not any(
                t.task_id == e["task_id"]
                for e in healthy + warning + critical
            )],
            "summary": {
                "healthy": len(healthy),
                "warning": len(warning),
                "critical": len(critical),
                "total": len(tasks)
            }
        }

    def search_tasks(self, query: str) -> Dict[str, Any]:
        """
        搜索任务

        Args:
            query: 搜索关键词

        Returns:
            匹配的任务列表
        """
        tasks = self.scheduler.registry.list_all()
        query_lower = query.lower()

        matched = [
            t.to_dict() for t in tasks
            if query_lower in t.name.lower()
            or query_lower in t.task_id.lower()
            or query_lower in t.skill_path.lower()
        ]

        return {
            "query": query,
            "results": matched,
            "count": len(matched)
        }
