# -*- coding: utf-8 -*-
"""
日志分析器

提供日志分析和报告生成能力
"""

from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from .logger import LogEntry, LogLevel, UnifiedLogger


@dataclass
class LogPattern:
    """日志模式"""
    pattern: str
    count: int
    first_seen: datetime
    last_seen: datetime
    examples: List[str]


@dataclass
class LogReport:
    """日志分析报告"""
    period_start: datetime
    period_end: datetime
    total_logs: int
    error_count: int
    warning_count: int
    top_errors: List[Dict]
    top_skills: List[Dict]
    patterns: List[LogPattern]
    recommendations: List[str]
    generated_at: datetime


class LogAnalyzer:
    """
    日志分析器

    提供：
    - 模式识别
    - 异常检测
    - 趋势分析
    - 报告生成
    """

    def __init__(self, logger: Optional[UnifiedLogger] = None):
        self.logger = logger or UnifiedLogger()

    def analyze(
        self,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        skill: Optional[str] = None
    ) -> LogReport:
        """
        分析日志

        Args:
            since: 分析起始时间
            until: 分析结束时间
            skill: 可选的技能筛选

        Returns:
            分析报告
        """
        since = since or (datetime.now() - timedelta(hours=24))
        until = until or datetime.now()

        # 获取日志
        logs = self.logger.query(since=since, until=until)
        if skill:
            logs = [l for l in logs if l.skill == skill]

        # 统计分析
        error_logs = [l for l in logs if l.level == LogLevel.ERROR]
        warning_logs = [l for l in logs if l.level == LogLevel.WARNING]

        # Top 错误
        top_errors = self._get_top_errors(error_logs)

        # Top 技能
        top_skills = self._get_top_skills(logs)

        # 模式识别
        patterns = self._identify_patterns(logs)

        # 生成建议
        recommendations = self._generate_recommendations(
            logs, error_logs, warning_logs
        )

        return LogReport(
            period_start=since,
            period_end=until,
            total_logs=len(logs),
            error_count=len(error_logs),
            warning_count=len(warning_logs),
            top_errors=top_errors,
            top_skills=top_skills,
            patterns=patterns,
            recommendations=recommendations,
            generated_at=datetime.now()
        )

    def _get_top_errors(self, error_logs: List[LogEntry], limit: int = 10) -> List[Dict]:
        """获取最常见的错误"""
        error_messages = [l.message for l in error_logs]
        counter = Counter(error_messages)

        results = []
        for message, count in counter.most_common(limit):
            # 获取首次和最后一次出现
            first = min(l.timestamp for l in error_logs if l.message == message)
            last = max(l.timestamp for l in error_logs if l.message == message)

            results.append({
                "message": message,
                "count": count,
                "first_seen": first.isoformat(),
                "last_seen": last.isoformat()
            })

        return results

    def _get_top_skills(self, logs: List[LogEntry], limit: int = 10) -> List[Dict]:
        """获取最活跃的技能"""
        skill_counts = Counter(l.skill for l in logs if l.skill)

        results = []
        for skill, count in skill_counts.most_common(limit):
            # 计算错误率
            skill_logs = [l for l in logs if l.skill == skill]
            error_count = sum(1 for l in skill_logs if l.level == LogLevel.ERROR)
            error_rate = error_count / len(skill_logs) * 100 if skill_logs else 0

            results.append({
                "skill": skill,
                "total_executions": count,
                "error_count": error_count,
                "error_rate": round(error_rate, 2)
            })

        return results

    def _identify_patterns(self, logs: List[LogEntry], limit: int = 5) -> List[LogPattern]:
        """识别日志模式"""
        # 简单模式：提取错误消息前缀
        error_messages = [l.message for l in logs if l.level in [LogLevel.ERROR, LogLevel.CRITICAL]]

        # 按前缀分组
        prefixes = defaultdict(list)
        for msg in error_messages:
            # 提取前缀（前50字符或到第一个特殊字符）
            prefix = msg[:50].split('(')[0].split(':')[0].strip()
            if len(prefix) > 10:
                prefixes[prefix].append(msg)

        # 转换为模式
        patterns = []
        for prefix, messages in sorted(prefixes.items(), key=lambda x: len(x[1]), reverse=True)[:limit]:
            timestamps = [l.timestamp for l in logs if l.message in messages]

            patterns.append(LogPattern(
                pattern=prefix,
                count=len(messages),
                first_seen=min(timestamps),
                last_seen=max(timestamps),
                examples=messages[:3]
            ))

        return patterns

    def _generate_recommendations(
        self,
        logs: List[LogEntry],
        error_logs: List[LogEntry],
        warning_logs: List[LogEntry]
    ) -> List[str]:
        """生成改进建议"""
        recommendations = []

        # 错误率分析
        if logs:
            error_rate = len(error_logs) / len(logs) * 100
            if error_rate > 10:
                recommendations.append(f"错误率较高 ({error_rate:.1f}%)，建议检查高错误技能")
            elif error_rate > 5:
                recommendations.append(f"错误率中等 ({error_rate:.1f}%)，建议持续监控")

        # 技能错误分析
        skill_errors = Counter(l.skill for l in error_logs if l.skill)
        if skill_errors:
            top_error_skill = skill_errors.most_common(1)[0]
            if top_error_skill[1] > 5:
                recommendations.append(
                    f"技能 '{top_error_skill[0]}' 错误最多 ({top_error_skill[1]}次)，建议优先排查"
                )

        # 重复错误分析
        error_messages = [l.message for l in error_logs]
        if error_messages:
            counter = Counter(error_messages)
            repeated = [(msg, count) for msg, count in counter.items() if count > 3]
            if repeated:
                recommendations.append(
                    f"发现 {len(repeated)} 个重复错误，建议添加错误处理或修复根本原因"
                )

        # 响应时间分析
        duration_logs = [l for l in logs if l.duration_ms > 0]
        if duration_logs:
            avg_duration = sum(l.duration_ms for l in duration_logs) / len(duration_logs)
            slow_logs = [l for l in duration_logs if l.duration_ms > avg_duration * 3]

            if slow_logs:
                slow_skills = Counter(l.skill for l in slow_logs if l.skill)
                if slow_skills:
                    recommendations.append(
                        f"发现 {len(slow_logs)} 条慢执行日志，技能 '{slow_skills.most_common(1)[0][0]}' 可能有性能问题"
                    )

        # 告警级别
        critical_logs = [l for l in logs if l.level == LogLevel.CRITICAL]
        if critical_logs:
            recommendations.append(
                f"发现 {len(critical_logs)} 条严重错误日志，需要立即处理"
            )

        # 无问题
        if not recommendations:
            recommendations.append("系统运行正常，未发现需要关注的问题")

        return recommendations

    # ========== 趋势分析 ==========

    def get_trend(
        self,
        metric: str,
        since: datetime,
        until: Optional[datetime] = None,
        interval: str = "hour"
    ) -> Dict[str, Any]:
        """
        获取指标趋势

        Args:
            metric: 指标名 (error/warning/success)
            since: 起始时间
            until: 结束时间
            interval: 间隔 (hour/day)

        Returns:
            趋势数据
        """
        until = until or datetime.now()

        logs = self.logger.query(since=since, until=until)

        # 按时间分组
        if interval == "hour":
            format_str = "%Y-%m-%d %H:00"
        else:
            format_str = "%Y-%m-%d"

        # 过滤对应级别
        if metric == "error":
            logs = [l for l in logs if l.level == LogLevel.ERROR]
        elif metric == "warning":
            logs = [l for l in logs if l.level == LogLevel.WARNING]
        elif metric == "success":
            logs = [l for l in logs if l.level == LogLevel.INFO]

        # 统计
        counts = Counter(l.timestamp.strftime(format_str) for l in logs)

        # 填充空缺
        trend = []
        current = since
        while current <= until:
            key = current.strftime(format_str)
            trend.append({
                "time": key,
                "count": counts.get(key, 0)
            })

            if interval == "hour":
                current += timedelta(hours=1)
            else:
                current += timedelta(days=1)

        return {
            "metric": metric,
            "since": since.isoformat(),
            "until": until.isoformat(),
            "interval": interval,
            "data": trend,
            "total": sum(t["count"] for t in trend)
        }

    # ========== 异常检测 ==========

    def detect_anomalies(
        self,
        threshold: float = 2.0,
        since: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        检测异常日志模式

        Args:
            threshold: 异常阈值（标准差倍数）
            since: 分析起始时间

        Returns:
            异常列表
        """
        since = since or (datetime.now() - timedelta(hours=24))
        logs = self.logger.query(since=since)

        # 按技能统计错误
        skill_errors = defaultdict(list)
        for log in logs:
            if log.level in [LogLevel.ERROR, LogLevel.CRITICAL] and log.skill:
                skill_errors[log.skill].append(log)

        # 计算平均值和标准差
        error_counts = [len(v) for v in skill_errors.values()]
        if not error_counts:
            return []

        avg = sum(error_counts) / len(error_counts)
        variance = sum((x - avg) ** 2 for x in error_counts) / len(error_counts)
        std = variance ** 0.5

        # 找出异常
        anomalies = []
        for skill, error_logs in skill_errors.items():
            count = len(error_logs)
            if count > avg + threshold * std:
                anomalies.append({
                    "skill": skill,
                    "error_count": count,
                    "expected_avg": round(avg, 2),
                    "threshold": round(avg + threshold * std, 2),
                    "severity": "high" if count > avg + 3 * std else "medium"
                })

        return sorted(anomalies, key=lambda x: x["error_count"], reverse=True)

    # ========== 报告生成 ==========

    def generate_report(
        self,
        period: str = "24h",
        skill: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        生成日志报告

        Args:
            period: 时间段 (24h/7d/30d)
            skill: 可选的技能筛选

        Returns:
            报告数据
        """
        # 解析时间段
        period_map = {
            "24h": timedelta(hours=24),
            "7d": timedelta(days=7),
            "30d": timedelta(days=30)
        }
        delta = period_map.get(period, timedelta(hours=24))

        since = datetime.now() - delta

        # 分析
        report = self.analyze(since=since, skill=skill)

        # 趋势
        error_trend = self.get_trend("error", since)
        warning_trend = self.get_trend("warning", since)

        # 异常
        anomalies = self.detect_anomalies(since=since)

        return {
            "period": period,
            "since": since.isoformat(),
            "until": datetime.now().isoformat(),
            "summary": {
                "total_logs": report.total_logs,
                "error_count": report.error_count,
                "warning_count": report.warning_count,
                "error_rate": round(report.error_count / report.total_logs * 100, 2) if report.total_logs > 0 else 0
            },
            "top_errors": report.top_errors,
            "top_skills": report.top_skills,
            "patterns": [
                {
                    "pattern": p.pattern,
                    "count": p.count,
                    "examples": p.examples
                }
                for p in report.patterns
            ],
            "recommendations": report.recommendations,
            "trends": {
                "errors": error_trend["data"],
                "warnings": warning_trend["data"]
            },
            "anomalies": anomalies,
            "generated_at": datetime.now().isoformat()
        }
