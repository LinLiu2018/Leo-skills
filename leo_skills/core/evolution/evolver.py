#!/usr/bin/env python3
"""
进化器模块 - 从经验中提取知识并生成优化规则
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List

from .metrics import AnalysisResult, BestPractice, OptimizationRule

logger = logging.getLogger(__name__)


class SkillEvolver:
    """技能进化器 - 从经验中提取知识"""

    def __init__(self, skill_name: str, data_dir: str = None):
        self.skill_name = skill_name
        self.data_dir = Path(data_dir) if data_dir else Path(f"leo-skills/.evolution_data/{skill_name}")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.practices_file = self.data_dir / "best_practices.json"
        self.rules_file = self.data_dir / "optimization_rules.json"

    def extract_best_practices(self, analysis: AnalysisResult) -> List[BestPractice]:
        """从分析结果中提取最佳实践"""
        practices = []

        # 从最优参数中提取
        if analysis.optimal_parameters and analysis.success_rate > 0.7:
            for param, value in analysis.optimal_parameters.items():
                practice = BestPractice(
                    name=f"optimal_{param}",
                    description=f"使用最优参数 {param}={value}",
                    conditions={'context': 'general'},
                    actions={param: value},
                    expected_improvement=0.1,
                    success_rate=analysis.success_rate
                )
                practices.append(practice)

        # 从性能趋势中提取
        if analysis.performance_trends.get('trend') == 'improving':
            practice = BestPractice(
                name="performance_improving",
                description="当前配置表现良好，继续保持",
                conditions={'trend': 'improving'},
                actions={'maintain': 'current_config'},
                expected_improvement=0.05,
                success_rate=analysis.success_rate
            )
            practices.append(practice)

        return practices

    def generate_optimization_rules(self, analysis: AnalysisResult) -> List[OptimizationRule]:
        """生成优化规则"""
        rules = []

        # 参数优化规则
        for param, value in analysis.optimal_parameters.items():
            confidence = analysis.confidence_scores.get('overall', 0.5)
            if confidence > 0.6:  # 只有置信度足够高才生成规则
                rule = OptimizationRule(
                    name=f"optimize_{param}",
                    type="parameter",
                    target=param,
                    action="adjust",
                    value=value,
                    confidence=confidence,
                    expected_gain=0.1
                )
                rules.append(rule)

        # 基于改进机会生成规则
        for opportunity in analysis.improvement_opportunities:
            if opportunity['type'] == 'success_rate' and analysis.success_rate < 0.8:
                # 建议增加重试机制
                rule = OptimizationRule(
                    name="improve_success_rate",
                    type="config",
                    target="retry_config",
                    action="add",
                    value={'max_retries': 3, 'retry_delay': 1},
                    confidence=0.7,
                    expected_gain=0.15
                )
                rules.append(rule)

        return rules

    def store_knowledge(self, practices: List[BestPractice], rules: List[OptimizationRule]):
        """存储知识到本地文件"""
        try:
            # 存储最佳实践
            if practices:
                practices_data = [p.to_dict() for p in practices]
                with open(self.practices_file, 'w', encoding='utf-8') as f:
                    json.dump(practices_data, f, indent=2, ensure_ascii=False)
                logger.info(f"已存储 {len(practices)} 条最佳实践")

            # 存储优化规则
            if rules:
                rules_data = [r.to_dict() for r in rules]
                with open(self.rules_file, 'w', encoding='utf-8') as f:
                    json.dump(rules_data, f, indent=2, ensure_ascii=False)
                logger.info(f"已存储 {len(rules)} 条优化规则")

        except Exception as e:
            logger.error(f"存储知识失败: {e}")

    def load_best_practices(self) -> List[BestPractice]:
        """加载最佳实践"""
        if not self.practices_file.exists():
            return []

        try:
            with open(self.practices_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                practices = []
                for item in data:
                    practice = BestPractice(
                        name=item['name'],
                        description=item['description'],
                        conditions=item['conditions'],
                        actions=item['actions'],
                        expected_improvement=item['expected_improvement'],
                        success_rate=item.get('success_rate', 0.0),
                        usage_count=item.get('usage_count', 0)
                    )
                    practices.append(practice)
                return practices
        except Exception as e:
            logger.error(f"加载最佳实践失败: {e}")
            return []

    def load_optimization_rules(self) -> List[OptimizationRule]:
        """加载优化规则"""
        if not self.rules_file.exists():
            return []

        try:
            with open(self.rules_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                rules = []
                for item in data:
                    rule = OptimizationRule(
                        name=item['name'],
                        type=item['type'],
                        target=item['target'],
                        action=item['action'],
                        value=item['value'],
                        confidence=item['confidence'],
                        expected_gain=item.get('expected_gain', 0.0)
                    )
                    rules.append(rule)
                return rules
        except Exception as e:
            logger.error(f"加载优化规则失败: {e}")
            return []
