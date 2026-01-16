#!/usr/bin/env python3
"""
指标定义模块 - 定义技能进化所需的核心数据结构
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List, Optional


@dataclass
class ExecutionMetrics:
    """执行指标 - 记录单次技能执行的数据"""
    skill_name: str
    timestamp: datetime
    success: bool
    duration: float  # 执行时长（秒）
    quality_score: float = 0.0  # 输出质量评分 (0-1)
    user_feedback: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    output_metrics: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'skill_name': self.skill_name,
            'timestamp': self.timestamp.isoformat(),
            'success': self.success,
            'duration': self.duration,
            'quality_score': self.quality_score,
            'user_feedback': self.user_feedback,
            'parameters': self.parameters,
            'output_metrics': self.output_metrics,
            'error_message': self.error_message
        }


@dataclass
class AnalysisResult:
    """分析结果 - 从历史执行中分析出的模式"""
    success_rate: float
    avg_duration: float
    avg_quality_score: float
    optimal_parameters: Dict[str, Any] = field(default_factory=dict)
    failure_patterns: List[Dict[str, Any]] = field(default_factory=list)
    performance_trends: Dict[str, Any] = field(default_factory=dict)
    improvement_opportunities: List[Dict[str, Any]] = field(default_factory=list)
    confidence_scores: Dict[str, float] = field(default_factory=dict)


@dataclass
class BestPractice:
    """最佳实践 - 从成功案例中提取的知识"""
    name: str
    description: str
    conditions: Dict[str, Any]  # 适用条件
    actions: Dict[str, Any]  # 推荐动作
    expected_improvement: float  # 预期提升
    success_rate: float = 0.0
    usage_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'description': self.description,
            'conditions': self.conditions,
            'actions': self.actions,
            'expected_improvement': self.expected_improvement,
            'success_rate': self.success_rate,
            'usage_count': self.usage_count
        }


@dataclass
class OptimizationRule:
    """优化规则 - 具体的优化动作"""
    name: str
    type: str  # parameter, workflow, config
    target: str  # 目标参数或组件
    action: str  # adjust, replace, add, remove
    value: Any  # 新值
    confidence: float  # 置信度 (0-1)
    expected_gain: float = 0.0  # 预期收益

    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'type': self.type,
            'target': self.target,
            'action': self.action,
            'value': self.value,
            'confidence': self.confidence,
            'expected_gain': self.expected_gain
        }


@dataclass
class ExecutionResult:
    """执行结果 - 技能执行的返回值"""
    success: bool
    data: Any
    duration: float
    metrics: Optional[ExecutionMetrics] = None
    error: Optional[str] = None
