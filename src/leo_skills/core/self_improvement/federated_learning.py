# -*- coding: utf-8 -*-
"""
跨用户学习模块 (Federated Learning)

模拟联邦学习框架，实现跨用户模式提取：
- 匿名化模式聚合
- 全局技能优化
- 隐私保护
"""

import hashlib
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Set

logger = logging.getLogger(__name__)


@dataclass
class PatternAggregation:
    """模式聚合结果"""
    pattern_type: str
    frequency: int
    confidence: float
    contributing_users: int
    example_data: List[str]
    global_relevance: float


@dataclass
class GlobalOptimization:
    """全局优化建议"""
    target_skill: str
    optimization_type: str  # "parameter", "logic", "structure"
    current_performance: float
    estimated_improvement: float
    rationale: str
    application_count: int


class PrivacyPreserver:
    """
    隐私保护器

    确保用户数据匿名化。
    """

    @staticmethod
    def anonymize_user_id(user_id: str) -> str:
        """匿名化用户ID"""
        return hashlib.sha256(f"user_{user_id}".encode()).hexdigest()[:16]

    @staticmethod
    def filter_sensitive_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """过滤敏感数据"""
        sensitive_keys = {'password', 'token', 'secret', 'key', 'api_key', 'private'}
        filtered = {}

        for key, value in data.items():
            if any(s in key.lower() for s in sensitive_keys):
                filtered[key] = "***REDACTED***"
            elif isinstance(value, dict):
                filtered[key] = PrivacyPreserver.filter_sensitive_data(value)
            else:
                filtered[key] = value

        return filtered

    @staticmethod
    def extract_patterns_only(raw_data: List[Dict]) -> List[Dict]:
        """仅提取模式，去除个人标识"""
        patterns = []

        for item in raw_data:
            # 提取意图类别、关键词频率、使用时段等统计特征
            pattern = {
                "intent_category": item.get("intent_category"),
                "keyword_frequency": item.get("keyword_frequency"),
                "usage_hour": item.get("usage_hour"),
                "skill_category": item.get("skill_category"),
                "success_indicator": item.get("success_indicator"),
            }
            patterns.append(pattern)

        return patterns


class CrossUserLearning:
    """
    跨用户学习引擎

    聚合多用户数据，提取通用模式。
    """

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent.parent.parent
        self.aggregated_data_dir = self.project_root / "data" / "federated"
        self.aggregated_data_dir.mkdir(parents=True, exist_ok=True)

        self.privacy = PrivacyPreserver()

    def contribute_patterns(
        self,
        user_id: str,
        patterns: List[Dict[str, Any]],
        local_stats: Dict[str, Any]
    ) -> bool:
        """
        贡献匿名化模式

        Args:
            user_id: 用户ID（将被匿名化）
            patterns: 本地提取的模式
            local_stats: 本地统计

        Returns:
            是否成功
        """
        try:
            # 匿名化
            anon_id = self.privacy.anonymize_user_id(user_id)

            # 过滤敏感数据
            safe_patterns = [
                self.privacy.filter_sensitive_data(p) for p in patterns
            ]

            # 保存贡献
            contribution = {
                "contributor_hash": anon_id,
                "timestamp": datetime.now().isoformat(),
                "patterns": safe_patterns,
                "stats": {
                    "total_interactions": local_stats.get("total", 0),
                    "unique_skills_used": local_stats.get("unique_skills", 0),
                    "avg_session_length": local_stats.get("avg_session", 0),
                }
            }

            # 按日期存储
            date_str = datetime.now().strftime("%Y%m%d")
            contrib_file = self.aggregated_data_dir / f"contributions_{date_str}.jsonl"

            with open(contrib_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(contribution, ensure_ascii=False) + "\n")

            logger.info(f"Recorded contribution from {anon_id[:8]}...")
            return True

        except Exception as e:
            logger.error(f"Failed to record contribution: {e}")
            return False

    def aggregate_patterns(
        self,
        days: int = 30,
        min_contributors: int = 3
    ) -> List[PatternAggregation]:
        """
        聚合跨用户模式

        Args:
            days: 统计天数
            min_contributors: 最小贡献者数

        Returns:
            聚合模式列表
        """
        from collections import Counter, defaultdict

        cutoff = datetime.now().timestamp() - days * 24 * 3600

        # 加载所有贡献
        all_contributions = []

        for contrib_file in self.aggregated_data_dir.glob("contributions_*.jsonl"):
            try:
                mtime = contrib_file.stat().st_mtime
                if mtime < cutoff:
                    continue

                with open(contrib_file, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip():
                            all_contributions.append(json.loads(line))
            except Exception as e:
                logger.debug(f"Failed to load {contrib_file}: {e}")

        if len(all_contributions) < min_contributors:
            logger.info(f"Not enough contributors ({len(all_contributions)} < {min_contributors})")
            return []

        logger.info(f"Aggregating patterns from {len(all_contributions)} contributions")

        # 按类型聚合
        intent_patterns = defaultdict(lambda: {"count": 0, "users": set(), "examples": []})
        skill_usage_patterns = defaultdict(lambda: {"count": 0, "users": set()})

        for contrib in all_contributions:
            user_hash = contrib.get("contributor_hash", "unknown")

            for pattern in contrib.get("patterns", []):
                # 聚合意图模式
                intent = pattern.get("intent_category")
                if intent:
                    intent_patterns[intent]["count"] += 1
                    intent_patterns[intent]["users"].add(user_hash)
                    if len(intent_patterns[intent]["examples"]) < 5:
                        intent_patterns[intent]["examples"].append(
                            str(pattern.get("keyword_frequency", ""))
                        )

                # 聚合技能使用模式
                skill_cat = pattern.get("skill_category")
                if skill_cat:
                    skill_usage_patterns[skill_cat]["count"] += 1
                    skill_usage_patterns[skill_cat]["users"].add(user_hash)

        # 构建聚合结果
        aggregations = []

        # 意图模式
        for intent, data in intent_patterns.items():
            if len(data["users"]) >= min_contributors:
                aggregations.append(PatternAggregation(
                    pattern_type="intent",
                    frequency=data["count"],
                    confidence=min(0.95, len(data["users"]) / len(all_contributions)),
                    contributing_users=len(data["users"]),
                    example_data=data["examples"],
                    global_relevance=data["count"] / len(all_contributions)
                ))

        # 技能使用模式
        for skill_cat, data in skill_usage_patterns.items():
            if len(data["users"]) >= min_contributors:
                aggregations.append(PatternAggregation(
                    pattern_type="skill_category",
                    frequency=data["count"],
                    confidence=min(0.95, len(data["users"]) / len(all_contributions)),
                    contributing_users=len(data["users"]),
                    example_data=[skill_cat],
                    global_relevance=data["count"] / len(all_contributions)
                ))

        # 按相关性排序
        aggregations.sort(key=lambda x: x.global_relevance, reverse=True)

        return aggregations

    def generate_global_optimizations(
        self,
        aggregations: List[PatternAggregation]
    ) -> List[GlobalOptimization]:
        """
        生成全局优化建议

        Args:
            aggregations: 聚合模式

        Returns:
            优化建议列表
        """
        optimizations = []

        for agg in aggregations[:10]:  # 只处理前10个高频模式
            if agg.pattern_type == "intent" and agg.frequency > 50:
                # 高频意图，建议优化对应技能
                optimizations.append(GlobalOptimization(
                    target_skill=f"{agg.example_data[0]}_skill" if agg.example_data else "general",
                    optimization_type="structure",
                    current_performance=0.7,
                    estimated_improvement=0.15,
                    rationale=f"Cross-user analysis shows {agg.frequency} occurrences across {agg.contributing_users} users",
                    application_count=agg.contributing_users
                ))

            elif agg.pattern_type == "skill_category":
                # 技能类别优化
                optimizations.append(GlobalOptimization(
                    target_skill=f"category_{agg.example_data[0]}",
                    optimization_type="parameter",
                    current_performance=0.8,
                    estimated_improvement=0.1,
                    rationale=f"Widely used category with {agg.frequency} total usages",
                    application_count=agg.contributing_users
                ))

        return optimizations

    def apply_global_optimizations(
        self,
        optimizations: List[GlobalOptimization],
        dry_run: bool = True
    ) -> Dict[str, Any]:
        """
        应用全局优化

        Args:
            optimizations: 优化建议
            dry_run: 是否仅模拟

        Returns:
            应用结果
        """
        results = {
            "applied": [],
            "skipped": [],
            "failed": [],
            "dry_run": dry_run
        }

        for opt in optimizations:
            if opt.application_count < 5:
                results["skipped"].append({
                    "target": opt.target_skill,
                    "reason": "Not enough users for global optimization"
                })
                continue

            if dry_run:
                results["applied"].append({
                    "target": opt.target_skill,
                    "type": opt.optimization_type,
                    "estimated_improvement": opt.estimated_improvement,
                    "note": "Simulated (dry_run)"
                })
            else:
                # 实际应用优化
                try:
                    # TODO: 实现实际优化逻辑
                    results["applied"].append({
                        "target": opt.target_skill,
                        "type": opt.optimization_type,
                        "status": "applied"
                    })
                except Exception as e:
                    results["failed"].append({
                        "target": opt.target_skill,
                        "error": str(e)
                    })

        return results

    def generate_global_report(self, days: int = 30) -> Dict[str, Any]:
        """
        生成全局学习报告

        Args:
            days: 统计天数

        Returns:
            报告数据
        """
        aggregations = self.aggregate_patterns(days=days)
        optimizations = self.generate_global_optimizations(aggregations)

        # 统计贡献者
        contributor_hashes = set()
        for contrib_file in self.aggregated_data_dir.glob("contributions_*.jsonl"):
            try:
                with open(contrib_file, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip():
                            data = json.loads(line)
                            contributor_hashes.add(data.get("contributor_hash", ""))
            except:
                pass

        return {
            "generated_at": datetime.now().isoformat(),
            "period_days": days,
            "contributors": len(contributor_hashes),
            "aggregated_patterns": len(aggregations),
            "top_patterns": [
                {
                    "type": a.pattern_type,
                    "frequency": a.frequency,
                    "users": a.contributing_users,
                    "relevance": a.global_relevance
                }
                for a in aggregations[:10]
            ],
            "optimization_opportunities": len(optimizations),
            "suggested_optimizations": [
                {
                    "target": o.target_skill,
                    "improvement": o.estimated_improvement,
                    "rationale": o.rationale
                }
                for o in optimizations[:5]
            ]
        }


# 便捷函数
def contribute_user_patterns(user_id: str, patterns: List[Dict], stats: Dict) -> bool:
    """快速贡献入口"""
    learning = CrossUserLearning()
    return learning.contribute_patterns(user_id, patterns, stats)


def get_global_insights(days: int = 30) -> Dict[str, Any]:
    """获取全局洞察"""
    learning = CrossUserLearning()
    return learning.generate_global_report(days=days)


if __name__ == "__main__":
    # 测试
    learning = CrossUserLearning()

    # 模拟贡献
    test_patterns = [
        {"intent_category": "development", "skill_category": "coding"},
        {"intent_category": "content", "skill_category": "writing"},
    ]
    test_stats = {"total": 100, "unique_skills": 10, "avg_session": 5.5}

    contribute_user_patterns("user_001", test_patterns, test_stats)
    contribute_user_patterns("user_002", test_patterns, test_stats)
    contribute_user_patterns("user_003", test_patterns, test_stats)

    # 获取洞察
    insights = get_global_insights(days=7)
    print(f"\n贡献者数: {insights['contributors']}")
    print(f"聚合模式: {insights['aggregated_patterns']}")
    print(f"优化机会: {insights['optimization_opportunities']}")
