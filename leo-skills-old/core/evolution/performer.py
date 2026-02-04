#!/usr/bin/env python3
"""
执行器模块 - 可进化技能基类
"""

import time
import yaml
import logging
import threading
from pathlib import Path
from typing import Dict, Any, Optional

from .learner import SkillLearner
from .evolver import SkillEvolver
from .adapter import SkillAdapter
from .metrics import ExecutionResult, ExecutionMetrics

logger = logging.getLogger(__name__)


class EvolvableSkill:
    """可进化技能基类 - 所有技能继承此类以获得自我进化能力"""

    def __init__(self, skill_name: str, config_path: str, evolution_config_path: str = None):
        self.skill_name = skill_name
        self.config_path = config_path

        # 加载进化配置
        if evolution_config_path:
            self.evolution_config_path = Path(evolution_config_path)
        else:
            # 默认在技能目录下查找
            skill_dir = Path(config_path).parent
            self.evolution_config_path = skill_dir / "config" / "evolution_config.yaml"

        self.evolution_config = self._load_evolution_config()
        self.evolution_enabled = self.evolution_config.get('evolution', {}).get('enabled', True)

        # 初始化进化组件
        if self.evolution_enabled:
            self.learner = SkillLearner(skill_name)
            self.evolver = SkillEvolver(skill_name)
            self.adapter = SkillAdapter(skill_name, config_path)
            logger.info(f"技能 {skill_name} 的进化能力已启用")
        else:
            logger.info(f"技能 {skill_name} 的进化能力已禁用")

    def _load_evolution_config(self) -> Dict[str, Any]:
        """加载进化配置"""
        if self.evolution_config_path.exists():
            try:
                with open(self.evolution_config_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f) or {}
            except Exception as e:
                logger.warning(f"加载进化配置失败: {e}，使用默认配置")

        # 默认配置
        return {
            'evolution': {
                'enabled': True,
                'learning': {
                    'min_executions_for_learning': 10,
                    'analysis_window': 100
                },
                'optimization': {
                    'auto_optimize': False,
                    'require_approval': True
                }
            }
        }

    def execute(self, *args, **kwargs) -> ExecutionResult:
        """
        执行技能（带进化能力）

        这是统一的执行入口，会自动：
        1. 应用最佳实践
        2. 执行核心逻辑
        3. 收集执行数据
        4. 触发学习流程
        """
        # 1. 执行前：加载并应用最佳实践
        if self.evolution_enabled:
            best_practices = self.evolver.load_best_practices()
            kwargs = self._apply_best_practices(kwargs, best_practices)

        # 2. 执行核心逻辑
        start_time = time.time()
        error = None

        try:
            result = self._execute_core(*args, **kwargs)
            success = result.get('success', True)
        except Exception as e:
            logger.error(f"技能执行失败: {e}")
            result = {'error': str(e)}
            success = False
            error = str(e)

        duration = time.time() - start_time

        # 3. 执行后：收集数据
        if self.evolution_enabled:
            execution_data = {
                'success': success,
                'duration': duration,
                'parameters': kwargs,
                'result': result,
                'quality_score': result.get('quality_score', 0.0),
                'output_metrics': result.get('output_metrics', {}),
                'error': error
            }
            metrics = self.learner.collect_execution_data(execution_data)

            # 4. 触发学习流程（异步）
            self._trigger_learning(metrics)

        return ExecutionResult(
            success=success,
            data=result,
            duration=duration,
            error=error
        )

    def _execute_core(self, *args, **kwargs) -> Dict[str, Any]:
        """
        核心执行逻辑（子类必须实现）

        返回格式：
        {
            'success': True/False,
            'quality_score': 0.0-1.0,  # 可选
            'output_metrics': {},      # 可选
            ... 其他结果数据
        }
        """
        raise NotImplementedError("子类必须实现 _execute_core 方法")

    def _apply_best_practices(self, kwargs: Dict[str, Any],
                             practices: list) -> Dict[str, Any]:
        """应用最佳实践到参数"""
        if not practices:
            return kwargs

        for practice in practices:
            # 检查是否满足条件
            if self._check_conditions(practice.conditions, kwargs):
                # 应用推荐动作
                for param, value in practice.actions.items():
                    if param not in kwargs or param == 'maintain':
                        continue
                    kwargs[param] = value
                    logger.debug(f"应用最佳实践: {practice.name}, {param}={value}")

        return kwargs

    def _check_conditions(self, conditions: Dict[str, Any],
                         context: Dict[str, Any]) -> bool:
        """检查条件是否满足"""
        # 简化实现：如果条件为空或为general，总是满足
        if not conditions or conditions.get('context') == 'general':
            return True

        # 检查所有条件是否都满足
        for key, value in conditions.items():
            if context.get(key) != value:
                return False

        return True

    def _trigger_learning(self, metrics: ExecutionMetrics):
        """触发学习流程（异步）"""
        learning_config = self.evolution_config.get('evolution', {}).get('learning', {})
        min_executions = learning_config.get('min_executions_for_learning', 10)
        analysis_window = learning_config.get('analysis_window', 100)

        # 检查是否达到学习阈值
        history = self.learner.load_history(limit=analysis_window)

        if len(history) >= min_executions:
            # 异步执行学习（不阻塞主流程）
            thread = threading.Thread(target=self._learn_and_evolve, args=(history,))
            thread.daemon = True
            thread.start()

    def _learn_and_evolve(self, history: list):
        """学习和进化流程"""
        try:
            logger.info(f"开始学习流程，分析 {len(history)} 条历史记录")

            # 1. 分析模式
            analysis = self.learner.analyze_patterns(history)
            logger.info(f"分析完成: 成功率={analysis.success_rate:.2%}, "
                       f"平均质量={analysis.avg_quality_score:.2f}")

            # 2. 提取知识
            best_practices = self.evolver.extract_best_practices(analysis)
            optimization_rules = self.evolver.generate_optimization_rules(analysis)

            logger.info(f"提取了 {len(best_practices)} 条最佳实践, "
                       f"{len(optimization_rules)} 条优化规则")

            # 3. 存储知识
            self.evolver.store_knowledge(best_practices, optimization_rules)

            # 4. 应用优化（如果启用）
            optimization_config = self.evolution_config.get('evolution', {}).get('optimization', {})
            auto_optimize = optimization_config.get('auto_optimize', False)

            if auto_optimize and optimization_rules:
                logger.info("自动应用优化规则")
                result = self.adapter.apply_optimizations(optimization_rules, auto_apply=True)
                logger.info(f"优化结果: {result}")
            elif optimization_rules:
                logger.info(f"有 {len(optimization_rules)} 条优化规则待审批")

        except Exception as e:
            logger.error(f"学习和进化失败: {e}", exc_info=True)

    def get_evolution_status(self) -> Dict[str, Any]:
        """获取进化状态"""
        if not self.evolution_enabled:
            return {'enabled': False}

        history = self.learner.load_history()
        practices = self.evolver.load_best_practices()
        rules = self.evolver.load_optimization_rules()
        snapshots = self.adapter.list_snapshots()

        return {
            'enabled': True,
            'total_executions': len(history),
            'best_practices_count': len(practices),
            'optimization_rules_count': len(rules),
            'snapshots_count': len(snapshots),
            'latest_snapshot': snapshots[0] if snapshots else None
        }

    def trigger_manual_learning(self) -> Dict[str, Any]:
        """手动触发学习流程"""
        if not self.evolution_enabled:
            return {'success': False, 'reason': 'evolution_disabled'}

        history = self.learner.load_history()
        if len(history) < 5:
            return {'success': False, 'reason': 'insufficient_data', 'count': len(history)}

        self._learn_and_evolve(history)
        return {'success': True, 'analyzed_count': len(history)}
