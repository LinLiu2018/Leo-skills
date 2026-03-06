# -*- coding: utf-8 -*-
"""
效果追踪分析模块

持续追踪改进效果
"""

import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class Change:
    """变更记录"""
    change_id: str
    skill_path: str
    change_type: str  # code, config, deployment
    description: str
    timestamp: datetime = field(default_factory=datetime.now)
    before: Dict = field(default_factory=dict)
    after: Dict = field(default_factory=dict)


@dataclass
class ImpactReport:
    """影响报告"""
    skill_path: str
    change_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    improvements: List[Dict] = field(default_factory=list)
    regressions: List[Dict] = field(default_factory=list)
    roi: float = 0.0
    confidence: float = 0.0


class EffectTracker:
    """
    效果追踪器

    功能：
    - 改进对比分析
    - 趋势可视化
    - ROI 计算
    - 报告生成
    """

    def __init__(self, storage_path: str = ".leo_effects"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.changes: List[Change] = []
        self.impact_reports: List[ImpactReport] = []

    def track_improvement(
        self,
        skill: str,
        change_id: str,
        before_metrics: Dict[str, float],
        after_metrics: Dict[str, float]
    ) -> ImpactReport:
        """
        追踪改进效果

        Args:
            skill: 技能路径
            change_id: 变更ID
            before_metrics: 改进前指标
            after_metrics: 改进后指标

        Returns:
            影响报告
        """
        improvements = []
        regressions = []

        # 对比每个指标
        for metric_name in before_metrics:
            if metric_name not in after_metrics:
                continue

            before = before_metrics[metric_name]
            after = after_metrics[metric_name]

            if before == 0:
                continue

            # 计算变化百分比
            change_percent = ((after - before) / before) * 100

            # 判断是改进还是退步
            # 对于延迟/错误率：降低 = 改进
            # 对于成功率/吞吐量：增加 = 改进
            if "time" in metric_name.lower() or "latency" in metric_name.lower() or "error" in metric_name.lower():
                if change_percent < 0:
                    improvements.append({
                        "metric": metric_name,
                        "before": before,
                        "after": after,
                        "change_percent": change_percent
                    })
                else:
                    regressions.append({
                        "metric": metric_name,
                        "before": before,
                        "after": after,
                        "change_percent": change_percent
                    })
            else:
                if change_percent > 0:
                    improvements.append({
                        "metric": metric_name,
                        "before": before,
                        "after": after,
                        "change_percent": change_percent
                    })
                else:
                    regressions.append({
                        "metric": metric_name,
                        "before": before,
                        "after": after,
                        "change_percent": change_percent
                    })

        # 计算 ROI
        roi = self._calculate_roi(improvements, regressions)

        # 计算置信度
        confidence = self._calculate_confidence(improvements, regressions)

        report = ImpactReport(
            skill_path=skill,
            change_id=change_id,
            improvements=improvements,
            regressions=regressions,
            roi=roi,
            confidence=confidence
        )

        # 保存报告
        self.impact_reports.append(report)

        return report

    def record_change(
        self,
        skill_path: str,
        change_id: str,
        change_type: str,
        description: str,
        before: Optional[Dict] = None,
        after: Optional[Dict] = None
    ) -> Change:
        """
        记录变更

        Args:
            skill_path: 技能路径
            change_id: 变更ID
            change_type: 变更类型
            description: 描述
            before: 变更前状态
            after: 变更后状态

        Returns:
            变更记录
        """
        change = Change(
            change_id=change_id,
            skill_path=skill_path,
            change_type=change_type,
            description=description,
            before=before or {},
            after=after or {}
        )

        self.changes.append(change)

        return change

    def calculate_roi(
        self,
        changes: List[Change],
        time_period_days: int = 30
    ) -> Dict[str, Any]:
        """
        计算投资回报

        Args:
            changes: 变更列表
            time_period_days: 时间周期（天）

        Returns:
            ROI 报告
        """
        since = datetime.now() - timedelta(days=time_period_days)

        # 筛选时间范围内的变更
        recent_changes = [c for c in changes if c.timestamp >= since]

        # 统计改进
        improvements = []
        for change in recent_changes:
            report = self.get_latest_report(change.skill_path)
            if report:
                improvements.extend(report.improvements)

        # 计算综合 ROI
        total_improvement_score = sum(
            abs(i.get("change_percent", 0)) / 100
            for i in improvements
        )

        # 假设成本（简化计算）
        cost_per_change = 1.0
        total_cost = len(recent_changes) * cost_per_change

        roi = (total_improvement_score - total_cost) / total_cost * 100 if total_cost > 0 else 0

        return {
            "time_period_days": time_period_days,
            "changes_count": len(recent_changes),
            "improvements_count": len(improvements),
            "total_improvement_score": round(total_improvement_score, 2),
            "estimated_cost": total_cost,
            "roi_percent": round(roi, 2)
        }

    def generate_insights(
        self,
        period: str = "30d"
    ) -> List[Dict[str, Any]]:
        """
        生成洞察

        Args:
            period: 时间段

        Returns:
            洞察列表
        """
        period_map = {
            "7d": 7,
            "30d": 30,
            "90d": 90
        }
        days = period_map.get(period, 30)

        since = datetime.now() - timedelta(days=days)

        # 获取时间范围内的报告
        reports = [
            r for r in self.impact_reports
            if r.timestamp >= since
        ]

        insights = []

        # 按技能分组
        by_skill = {}
        for report in reports:
            if report.skill_path not in by_skill:
                by_skill[report.skill_path] = []
            by_skill[report.skill_path].append(report)

        # 生成洞察
        for skill, skill_reports in by_skill.items():
            # 计算平均改进
            total_improvements = sum(len(r.improvements) for r in skill_reports)
            total_regressions = sum(len(r.regressions) for r in skill_reports)

            avg_confidence = sum(r.confidence for r in skill_reports) / len(skill_reports)

            if total_improvements > total_regressions:
                insights.append({
                    "type": "positive_trend",
                    "skill": skill,
                    "message": f"技能 '{skill}' 呈现正向趋势：{total_improvements} 项改进 vs {total_regressions} 项退步",
                    "confidence": avg_confidence
                })
            elif total_improvements < total_regressions:
                insights.append({
                    "type": "negative_trend",
                    "skill": skill,
                    "message": f"技能 '{skill}' 需要关注：{total_improvements} 项改进 vs {total_regressions} 项退步",
                    "confidence": avg_confidence
                })

        # 排序
        insights.sort(key=lambda x: x.get("confidence", 0), reverse=True)

        return insights[:10]

    def create_dashboard(self) -> Dict[str, Any]:
        """
        创建分析面板

        Returns:
            仪表板数据
        """
        # 统计
        total_changes = len(self.changes)
        total_reports = len(self.impact_reports)

        # 按类型统计变更
        by_type = {}
        for change in self.changes:
            t = change.change_type
            by_type[t] = by_type.get(t, 0) + 1

        # 按技能统计
        by_skill = {}
        for change in self.changes:
            s = change.skill_path
            by_skill[s] = by_skill.get(s, 0) + 1

        # 最近改进
        recent_reports = sorted(
            self.impact_reports,
            key=lambda x: x.timestamp,
            reverse=True
        )[:5]

        recent_improvements = []
        for report in recent_reports:
            recent_improvements.extend([
                {
                    "skill": report.skill_path,
                    "metric": i["metric"],
                    "change": f"{i['change_percent']:.1f}%",
                    "timestamp": report.timestamp.isoformat()
                }
                for i in report.improvements[:3]
            ])

        # ROI
        roi = self.calculate_roi(self.changes)

        # 洞察
        insights = self.generate_insights("30d")

        return {
            "summary": {
                "total_changes": total_changes,
                "total_reports": total_reports,
                "by_type": by_type,
                "by_skill": by_skill
            },
            "roi": roi,
            "recent_improvements": recent_improvements,
            "insights": insights,
            "timestamp": datetime.now().isoformat()
        }

    # ========== 辅助方法 ==========

    def _calculate_roi(
        self,
        improvements: List[Dict],
        regressions: List[Dict]
    ) -> float:
        """计算 ROI"""
        if not improvements and not regressions:
            return 0.0

        # 简单计算：改进分数 - 退步分数
        improvement_score = sum(abs(i.get("change_percent", 0)) for i in improvements)
        regression_score = sum(abs(r.get("change_percent", 0)) for r in regressions)

        return improvement_score - regression_score

    def _calculate_confidence(
        self,
        improvements: List[Dict],
        regressions: List[Dict]
    ) -> float:
        """计算置信度"""
        total = len(improvements) + len(regressions)
        if total == 0:
            return 0.0

        # 改进占比越高，置信度越高
        improvement_ratio = len(improvements) / total

        return improvement_ratio

    def get_latest_report(self, skill_path: str) -> Optional[ImpactReport]:
        """获取最新报告"""
        for report in reversed(self.impact_reports):
            if report.skill_path == skill_path:
                return report
        return None

    def get_reports(
        self,
        skill_path: Optional[str] = None,
        limit: int = 20
    ) -> List[ImpactReport]:
        """获取报告列表"""
        reports = self.impact_reports

        if skill_path:
            reports = [r for r in reports if r.skill_path == skill_path]

        return reports[-limit:]

    # ========== 持久化 ==========

    def save(self):
        """保存追踪数据"""
        date_str = datetime.now().strftime("%Y%m%d")
        file_path = self.storage_path / f"effects_{date_str}.json"

        data = {
            "changes": [
                {
                    "change_id": c.change_id,
                    "skill_path": c.skill_path,
                    "change_type": c.change_type,
                    "description": c.description,
                    "timestamp": c.timestamp.isoformat()
                }
                for c in self.changes[-100:]
            ]
        }

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


# 全局实例
_global_tracker: Optional[EffectTracker] = None


def get_effect_tracker() -> EffectTracker:
    """获取全局效果追踪器"""
    global _global_tracker
    if _global_tracker is None:
        _global_tracker = EffectTracker()
    return _global_tracker
