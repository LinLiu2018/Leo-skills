#!/usr/bin/env python3
"""
学习器模块 - 收集和分析技能执行数据
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime, timedelta

from .metrics import ExecutionMetrics, AnalysisResult

logger = logging.getLogger(__name__)


class SkillLearner:
    """技能学习器 - 收集和分析执行数据"""

    def __init__(self, skill_name: str, data_dir: str = None):
        self.skill_name = skill_name
        self.data_dir = Path(data_dir) if data_dir else Path(f"leo-skills/.evolution_data/{skill_name}")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.history_file = self.data_dir / "execution_history.jsonl"

    def collect_execution_data(self, execution_result: Dict[str, Any]) -> ExecutionMetrics:
        """收集执行数据"""
        metrics = ExecutionMetrics(
            skill_name=self.skill_name,
            timestamp=datetime.now(),
            success=execution_result.get('success', False),
            duration=execution_result.get('duration', 0),
            quality_score=execution_result.get('quality_score', 0.0),
            user_feedback=execution_result.get('user_feedback'),
            parameters=execution_result.get('parameters', {}),
            output_metrics=execution_result.get('output_metrics', {}),
            error_message=execution_result.get('error')
        )

        # 保存到历史文件
        self._save_metrics(metrics)

        return metrics

    def _save_metrics(self, metrics: ExecutionMetrics):
        """保存指标到文件"""
        try:
            with open(self.history_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(metrics.to_dict(), ensure_ascii=False) + '\n')
        except Exception as e:
            logger.error(f"保存指标失败: {e}")

    def load_history(self, limit: int = None) -> List[ExecutionMetrics]:
        """加载历史执行数据"""
        history = []

        if not self.history_file.exists():
            return history

        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if limit:
                    lines = lines[-limit:]  # 只取最近的N条

                for line in lines:
                    data = json.loads(line.strip())
                    metrics = ExecutionMetrics(
                        skill_name=data['skill_name'],
                        timestamp=datetime.fromisoformat(data['timestamp']),
                        success=data['success'],
                        duration=data['duration'],
                        quality_score=data.get('quality_score', 0.0),
                        user_feedback=data.get('user_feedback'),
                        parameters=data.get('parameters', {}),
                        output_metrics=data.get('output_metrics', {}),
                        error_message=data.get('error_message')
                    )
                    history.append(metrics)
        except Exception as e:
            logger.error(f"加载历史数据失败: {e}")

        return history

    def analyze_patterns(self, history: List[ExecutionMetrics]) -> AnalysisResult:
        """分析执行模式"""
        if not history:
            return AnalysisResult(
                success_rate=0.0,
                avg_duration=0.0,
                avg_quality_score=0.0
            )

        # 基础统计
        success_count = sum(1 for m in history if m.success)
        success_rate = success_count / len(history)
        avg_duration = sum(m.duration for m in history) / len(history)
        avg_quality_score = sum(m.quality_score for m in history) / len(history)

        # 分析最优参数
        optimal_parameters = self._find_optimal_parameters(history)

        # 识别失败模式
        failure_patterns = self._identify_failure_patterns(history)

        # 分析性能趋势
        performance_trends = self._analyze_trends(history)

        # 发现改进机会
        improvement_opportunities = self._find_improvements(history, success_rate, avg_quality_score)

        return AnalysisResult(
            success_rate=success_rate,
            avg_duration=avg_duration,
            avg_quality_score=avg_quality_score,
            optimal_parameters=optimal_parameters,
            failure_patterns=failure_patterns,
            performance_trends=performance_trends,
            improvement_opportunities=improvement_opportunities,
            confidence_scores=self._calculate_confidence(history)
        )

    def _find_optimal_parameters(self, history: List[ExecutionMetrics]) -> Dict[str, Any]:
        """找出最优参数组合"""
        # 只分析成功的执行
        successful = [m for m in history if m.success and m.quality_score > 0.7]

        if not successful:
            return {}

        # 统计每个参数值的平均质量分数
        param_scores = {}

        for metrics in successful:
            for param, value in metrics.parameters.items():
                key = f"{param}={value}"
                if key not in param_scores:
                    param_scores[key] = []
                param_scores[key].append(metrics.quality_score)

        # 找出平均分数最高的参数值
        optimal = {}
        for key, scores in param_scores.items():
            if len(scores) >= 3:  # 至少3次才认为可靠
                param_name = key.split('=')[0]
                avg_score = sum(scores) / len(scores)
                if param_name not in optimal or avg_score > optimal[param_name]['score']:
                    optimal[param_name] = {
                        'value': key.split('=', 1)[1],
                        'score': avg_score,
                        'count': len(scores)
                    }

        return {k: v['value'] for k, v in optimal.items()}

    def _identify_failure_patterns(self, history: List[ExecutionMetrics]) -> List[Dict[str, Any]]:
        """识别失败模式"""
        failures = [m for m in history if not m.success]

        if not failures:
            return []

        # 统计错误类型
        error_types = {}
        for metrics in failures:
            error = metrics.error_message or "Unknown"
            if error not in error_types:
                error_types[error] = []
            error_types[error].append(metrics)

        patterns = []
        for error, occurrences in error_types.items():
            if len(occurrences) >= 2:  # 至少出现2次
                patterns.append({
                    'error': error,
                    'count': len(occurrences),
                    'frequency': len(occurrences) / len(history),
                    'common_parameters': self._find_common_parameters(occurrences)
                })

        return patterns

    def _find_common_parameters(self, metrics_list: List[ExecutionMetrics]) -> Dict[str, Any]:
        """找出共同参数"""
        if not metrics_list:
            return {}

        # 找出所有执行都有的参数
        common = {}
        first_params = metrics_list[0].parameters

        for param, value in first_params.items():
            if all(m.parameters.get(param) == value for m in metrics_list):
                common[param] = value

        return common

    def _analyze_trends(self, history: List[ExecutionMetrics]) -> Dict[str, Any]:
        """分析性能趋势"""
        if len(history) < 5:
            return {'trend': 'insufficient_data'}

        # 取最近的一半和前一半对比
        mid = len(history) // 2
        recent = history[mid:]
        earlier = history[:mid]

        recent_success_rate = sum(1 for m in recent if m.success) / len(recent)
        earlier_success_rate = sum(1 for m in earlier if m.success) / len(earlier)

        recent_quality = sum(m.quality_score for m in recent) / len(recent)
        earlier_quality = sum(m.quality_score for m in earlier) / len(earlier)

        return {
            'success_rate_change': recent_success_rate - earlier_success_rate,
            'quality_score_change': recent_quality - earlier_quality,
            'trend': 'improving' if recent_success_rate > earlier_success_rate else 'declining'
        }

    def _find_improvements(self, history: List[ExecutionMetrics],
                          success_rate: float, avg_quality: float) -> List[Dict[str, Any]]:
        """发现改进机会"""
        opportunities = []

        # 如果成功率低于80%
        if success_rate < 0.8:
            opportunities.append({
                'type': 'success_rate',
                'current': success_rate,
                'target': 0.85,
                'suggestion': '分析失败模式，调整参数或增加错误处理'
            })

        # 如果质量分数低于0.7
        if avg_quality < 0.7:
            opportunities.append({
                'type': 'quality_score',
                'current': avg_quality,
                'target': 0.8,
                'suggestion': '优化输出质量，参考高分案例的参数配置'
            })

        # 如果执行时间过长
        avg_duration = sum(m.duration for m in history) / len(history)
        if avg_duration > 60:  # 超过60秒
            opportunities.append({
                'type': 'performance',
                'current': avg_duration,
                'target': 30,
                'suggestion': '优化执行流程，考虑并行处理或缓存'
            })

        return opportunities

    def _calculate_confidence(self, history: List[ExecutionMetrics]) -> Dict[str, float]:
        """计算置信度分数"""
        sample_size = len(history)

        # 样本量越大，置信度越高
        if sample_size < 5:
            base_confidence = 0.3
        elif sample_size < 10:
            base_confidence = 0.5
        elif sample_size < 20:
            base_confidence = 0.7
        else:
            base_confidence = 0.9

        return {
            'overall': base_confidence,
            'sample_size': sample_size
        }
