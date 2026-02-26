#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Leo Agent Evaluation Framework

基于业界最佳实践的AI Agent评估框架，实现多层次、多维度的评估体系。
参考Anthropic、Google Cloud、Microsoft等公司的评估方法。
"""

import os
import sys
import json
import time
import asyncio
import statistics
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
import logging

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from leo_subagents.skills_bridge.skill_discovery_simple import SkillDiscoverySystem

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def safe_print(text):
    """安全打印，避免编码错误"""
    try:
        print(text)
    except UnicodeEncodeError:
        safe_text = text.encode('ascii', 'ignore').decode('ascii')
        print(safe_text)

@dataclass
class EvaluationTask:
    """评估任务"""
    name: str
    description: str
    input_data: Any
    expected_output: Optional[Any] = None
    timeout_seconds: int = 30
    category: str = "general"
    difficulty: str = "medium"  # easy, medium, hard
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []

@dataclass
class EvaluationResult:
    """评估结果"""
    task_name: str
    agent_name: str
    success: bool
    execution_time: float
    output: Any
    error_message: Optional[str] = None
    score: float = 0.0  # 0-100
    metrics: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metrics is None:
            self.metrics = {}

@dataclass
class AgentEvaluationSummary:
    """Agent评估总结"""
    agent_name: str
    total_tasks: int
    successful_tasks: int
    failed_tasks: int
    success_rate: float
    average_execution_time: float
    average_score: float
    total_score: float
    category_performance: Dict[str, Dict[str, float]]
    recommendations: List[str]
    evaluation_time: datetime
    detailed_results: List[EvaluationResult] = None

class BaseEvaluator(ABC):
    """评估器基类"""
    
    @abstractmethod
    async def evaluate_task(self, task: EvaluationTask, agent: Any) -> EvaluationResult:
        """评估单个任务"""
        pass
    
    @abstractmethod
    def calculate_score(self, task: EvaluationTask, result: EvaluationResult) -> float:
        """计算任务得分"""
        pass

class FunctionalEvaluator(BaseEvaluator):
    """功能性评估器"""
    
    def __init__(self):
        self.evaluation_methods = {
            'exact_match': self._exact_match,
            'partial_match': self._partial_match,
            'semantic_similarity': self._semantic_similarity,
            'output_validation': self._output_validation,
            'performance_check': self._performance_check
        }
    
    async def evaluate_task(self, task: EvaluationTask, agent: Any) -> EvaluationResult:
        """评估单个任务"""
        start_time = time.time()
        
        try:
            # 设置超时
            result = await asyncio.wait_for(
                self._execute_task(task, agent),
                timeout=task.timeout_seconds
            )
            
            execution_time = time.time() - start_time
            
            # 创建评估结果
            eval_result = EvaluationResult(
                task_name=task.name,
                agent_name=getattr(agent, 'name', 'unknown'),
                success=True,
                execution_time=execution_time,
                output=result,
                score=0.0
            )
            
            # 计算得分
            eval_result.score = self.calculate_score(task, eval_result)
            
            return eval_result
            
        except asyncio.TimeoutError:
            return EvaluationResult(
                task_name=task.name,
                agent_name=getattr(agent, 'name', 'unknown'),
                success=False,
                execution_time=task.timeout_seconds,
                output=None,
                error_message="Task execution timeout",
                score=0.0
            )
        except Exception as e:
            execution_time = time.time() - start_time
            return EvaluationResult(
                task_name=task.name,
                agent_name=getattr(agent, 'name', 'unknown'),
                success=False,
                execution_time=execution_time,
                output=None,
                error_message=str(e),
                score=0.0
            )
    
    async def _execute_task(self, task: EvaluationTask, agent: Any) -> Any:
        """执行任务"""
        # 这里需要根据实际的agent接口来实现
        # 简化版本：假设agent有run方法
        if hasattr(agent, 'run'):
            return await agent.run(task.input_data)
        elif hasattr(agent, 'main'):
            return agent.main(task.input_data)
        else:
            raise ValueError(f"Agent {agent} does not have a callable method")
    
    def calculate_score(self, task: EvaluationTask, result: EvaluationResult) -> float:
        """计算任务得分"""
        if not result.success:
            return 0.0
        
        base_score = 80.0  # 基础分
        
        # 性能分数
        if result.execution_time > task.timeout_seconds * 0.8:
            base_score -= 20
        elif result.execution_time > task.timeout_seconds * 0.5:
            base_score -= 10
        
        # 输出质量分数
        if task.expected_output is not None:
            if self._exact_match(result.output, task.expected_output):
                base_score += 20
            elif self._partial_match(result.output, task.expected_output):
                base_score += 10
        
        return max(0.0, min(100.0, base_score))
    
    def _exact_match(self, output: Any, expected: Any) -> bool:
        """精确匹配"""
        return str(output).strip() == str(expected).strip()
    
    def _partial_match(self, output: Any, expected: Any) -> bool:
        """部分匹配"""
        output_str = str(output).lower()
        expected_str = str(expected).lower()
        return expected_str in output_str or output_str in expected_str
    
    def _semantic_similarity(self, output: Any, expected: Any) -> float:
        """语义相似度（简化版）"""
        # 实际实现应该使用embedding或NLP模型
        output_words = set(str(output).lower().split())
        expected_words = set(str(expected).lower().split())
        
        if not output_words or not expected_words:
            return 0.0
        
        intersection = output_words.intersection(expected_words)
        union = output_words.union(expected_words)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _output_validation(self, output: Any, task: EvaluationTask) -> bool:
        """输出验证"""
        # 检查输出格式、长度等
        if output is None:
            return False
        
        output_str = str(output).strip()
        if len(output_str) == 0:
            return False
        
        # 可以根据任务类型添加更多验证逻辑
        return True
    
    def _performance_check(self, execution_time: float, task: EvaluationTask) -> bool:
        """性能检查"""
        return execution_time <= task.timeout_seconds

class PerformanceEvaluator(BaseEvaluator):
    """性能评估器"""
    
    async def evaluate_task(self, task: EvaluationTask, agent: Any) -> EvaluationResult:
        """性能评估"""
        execution_times = []
        
        # 运行多次以获得平均性能
        for i in range(3):
            start_time = time.time()
            try:
                await asyncio.wait_for(
                    self._execute_task(task, agent),
                    timeout=task.timeout_seconds
                )
                execution_time = time.time() - start_time
                execution_times.append(execution_time)
            except Exception as e:
                execution_times.append(task.timeout_seconds)
        
        avg_time = statistics.mean(execution_times)
        std_time = statistics.stdev(execution_times) if len(execution_times) > 1 else 0
        
        # 计算性能分数
        performance_score = self._calculate_performance_score(avg_time, task.timeout_seconds)
        
        return EvaluationResult(
            task_name=task.name,
            agent_name=getattr(agent, 'name', 'unknown'),
            success=len([t for t in execution_times if t < task.timeout_seconds]) > 1,
            execution_time=avg_time,
            output={'avg_time': avg_time, 'std_time': std_time, 'times': execution_times},
            score=performance_score,
            metrics={
                'avg_execution_time': avg_time,
                'std_execution_time': std_time,
                'min_execution_time': min(execution_times),
                'max_execution_time': max(execution_times),
                'timeout_rate': len([t for t in execution_times if t >= task.timeout_seconds]) / len(execution_times)
            }
        )
    
    async def _execute_task(self, task: EvaluationTask, agent: Any) -> Any:
        """执行任务"""
        if hasattr(agent, 'run'):
            return await agent.run(task.input_data)
        elif hasattr(agent, 'main'):
            return agent.main(task.input_data)
        else:
            raise ValueError(f"Agent {agent} does not have a callable method")
    
    def calculate_score(self, task: EvaluationTask, result: EvaluationResult) -> float:
        """计算性能得分"""
        return result.score
    
    def _calculate_performance_score(self, avg_time: float, timeout: float) -> float:
        """计算性能分数"""
        # 基于相对时间的评分
        ratio = avg_time / timeout
        
        if ratio <= 0.2:
            return 100.0
        elif ratio <= 0.5:
            return 80.0
        elif ratio <= 0.8:
            return 60.0
        elif ratio <= 1.0:
            return 40.0
        else:
            return 20.0

class AgentEvaluationFramework:
    """Agent评估框架"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.discovery = SkillDiscoverySystem(project_root)
        self.evaluators = {
            'functional': FunctionalEvaluator(),
            'performance': PerformanceEvaluator()
        }
        self.results_dir = project_root / ".claude" / "evaluation_results"
        self.results_dir.mkdir(exist_ok=True)
        
        # 默认评估任务集
        self.default_tasks = self._create_default_tasks()
    
    def _create_default_tasks(self) -> List[EvaluationTask]:
        """创建默认评估任务"""
        tasks = []
        
        # 基础功能测试
        tasks.append(EvaluationTask(
            name="basic_skill_discovery",
            description="测试技能发现功能",
            input_data={"action": "discover_skills"},
            expected_output={"status": "success"},
            category="functional",
            difficulty="easy",
            tags=["discovery", "basic"]
        ))
        
        tasks.append(EvaluationTask(
            name="skill_validation",
            description="测试技能验证功能",
            input_data={"action": "validate_skills"},
            category="functional",
            difficulty="medium",
            tags=["validation", "quality"]
        ))
        
        # 性能测试
        tasks.append(EvaluationTask(
            name="performance_discovery",
            description="测试技能发现性能",
            input_data={"action": "discover_skills_performance"},
            timeout_seconds=10,
            category="performance",
            difficulty="medium",
            tags=["performance", "discovery"]
        ))
        
        tasks.append(EvaluationTask(
            name="concurrent_operations",
            description="测试并发操作",
            input_data={"action": "concurrent_test", "count": 5},
            category="performance",
            difficulty="hard",
            tags=["concurrency", "performance"]
        ))
        
        # 错误处理测试
        tasks.append(EvaluationTask(
            name="error_handling",
            description="测试错误处理",
            input_data={"action": "invalid_operation"},
            expected_output=None,
            category="functional",
            difficulty="medium",
            tags=["error_handling", "robustness"]
        ))
        
        return tasks
    
    def create_evaluation_suite(self, name: str, tasks: List[EvaluationTask], 
                             evaluators: List[str] = None) -> Dict[str, Any]:
        """创建评估套件"""
        if evaluators is None:
            evaluators = ['functional', 'performance']
        
        return {
            'name': name,
            'created_at': datetime.now().isoformat(),
            'tasks': [asdict(task) for task in tasks],
            'evaluators': evaluators,
            'total_tasks': len(tasks)
        }
    
    async def evaluate_agent(self, agent: Any, agent_name: str, 
                          tasks: List[EvaluationTask] = None,
                          evaluators: List[str] = None) -> AgentEvaluationSummary:
        """评估Agent"""
        if tasks is None:
            tasks = self.default_tasks
        
        if evaluators is None:
            evaluators = ['functional', 'performance']
        
        safe_print(f"开始评估Agent: {agent_name}")
        safe_print(f"任务数量: {len(tasks)}")
        safe_print(f"评估器: {evaluators}")
        
        all_results = []
        start_time = datetime.now()
        
        # 对每个任务进行评估
        for task in tasks:
            safe_print(f"执行任务: {task.name}")
            
            # 使用指定的评估器
            task_results = []
            for evaluator_name in evaluators:
                if evaluator_name in self.evaluators:
                    evaluator = self.evaluators[evaluator_name]
                    result = await evaluator.evaluate_task(task, agent)
                    result.agent_name = agent_name
                    task_results.append(result)
                    
                    safe_print(f"  {evaluator_name}: {result.score:.1f}分 ({result.execution_time:.2f}s)")
            
            # 使用主要评估器的结果（第一个）
            if task_results:
                all_results.append(task_results[0])
        
        # 计算总结
        successful_tasks = [r for r in all_results if r.success]
        failed_tasks = [r for r in all_results if not r.success]
        
        total_tasks = len(all_results)
        success_count = len(successful_tasks)
        fail_count = len(failed_tasks)
        success_rate = (success_count / total_tasks) * 100 if total_tasks > 0 else 0
        
        execution_times = [r.execution_time for r in all_results if r.success]
        avg_execution_time = statistics.mean(execution_times) if execution_times else 0
        
        scores = [r.score for r in all_results]
        avg_score = statistics.mean(scores) if scores else 0
        total_score = sum(scores)
        
        # 按分类统计性能
        category_performance = {}
        for task in tasks:
            if task.category not in category_performance:
                category_performance[task.category] = {
                    'total': 0, 'success': 0, 'avg_score': 0.0
                }
            
            category_performance[task.category]['total'] += 1
            
            # 找到对应的结果
            task_result = next((r for r in all_results if r.task_name == task.name), None)
            if task_result and task_result.success:
                category_performance[task.category]['success'] += 1
                category_performance[task.category]['avg_score'] += task_result.score
        
        # 计算平均值
        for category, stats in category_performance.items():
            if stats['total'] > 0:
                stats['success_rate'] = (stats['success'] / stats['total']) * 100
                stats['avg_score'] = stats['avg_score'] / stats['total']
        
        # 生成建议
        recommendations = self._generate_recommendations(all_results, category_performance)
        
        summary = AgentEvaluationSummary(
            agent_name=agent_name,
            total_tasks=total_tasks,
            successful_tasks=success_count,
            failed_tasks=fail_count,
            success_rate=success_rate,
            average_execution_time=avg_execution_time,
            average_score=avg_score,
            total_score=total_score,
            category_performance=category_performance,
            recommendations=recommendations,
            evaluation_time=start_time,
            detailed_results=all_results
        )
        
        # 保存结果
        await self.save_evaluation_results(summary)
        
        return summary
    
    def _generate_recommendations(self, results: List[EvaluationResult], 
                                category_performance: Dict[str, Dict[str, float]]) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        # 基于成功率的建议
        success_rate = (len([r for r in results if r.success]) / len(results)) * 100 if results else 0
        
        if success_rate < 60:
            recommendations.append("成功率较低，建议检查基本功能和错误处理")
        elif success_rate < 80:
            recommendations.append("成功率中等，建议优化边缘情况处理")
        
        # 基于性能的建议
        execution_times = [r.execution_time for r in results if r.success]
        if execution_times:
            avg_time = statistics.mean(execution_times)
            if avg_time > 10:
                recommendations.append("执行时间较长，建议优化性能和算法效率")
        
        # 基于分类性能的建议
        for category, stats in category_performance.items():
            if stats['success_rate'] < 70:
                recommendations.append(f"{category}类任务表现较差，建议重点优化")
            if stats['avg_score'] < 60:
                recommendations.append(f"{category}类任务得分偏低，建议改进实现质量")
        
        # 基于错误类型的建议
        error_types = {}
        for result in results:
            if not result.success and result.error_message:
                error_type = result.error_message.split(':')[0] if ':' in result.error_message else 'unknown'
                error_types[error_type] = error_types.get(error_type, 0) + 1
        
        if error_types:
            most_common_error = max(error_types, key=error_types.get)
            recommendations.append(f"最常见错误类型: {most_common_error}，建议针对性修复")
        
        return recommendations
    
    async def save_evaluation_results(self, summary: AgentEvaluationSummary):
        """保存评估结果"""
        # 保存详细结果
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"evaluation_{summary.agent_name}_{timestamp}.json"
        filepath = self.results_dir / filename
        
        result_data = asdict(summary)
        result_data['evaluation_time'] = summary.evaluation_time.isoformat()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, indent=2, ensure_ascii=False)
        
        # 保存最新结果
        latest_file = self.results_dir / f"latest_{summary.agent_name}.json"
        with open(latest_file, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"评估结果已保存: {filepath}")
    
    def display_evaluation_summary(self, summary: AgentEvaluationSummary):
        """显示评估总结"""
        safe_print(f"\n{'='*60}")
        safe_print(f"Agent评估报告: {summary.agent_name}")
        safe_print(f"{'='*60}")
        
        # 总体表现
        score_color = "🟢" if summary.average_score >= 80 else "🟡" if summary.average_score >= 60 else "🔴"
        safe_print(f"\n📊 总体得分: {summary.average_score:.1f}/100 {score_color}")
        safe_print(f"🎯 成功率: {summary.success_rate:.1f}% ({summary.successful_tasks}/{summary.total_tasks})")
        safe_print(f"⏱️  平均执行时间: {summary.average_execution_time:.2f}秒")
        
        # 分类表现
        if summary.category_performance:
            safe_print(f"\n📈 分类表现:")
            for category, stats in summary.category_performance.items():
                safe_print(f"  {category}:")
                safe_print(f"    成功率: {stats.get('success_rate', 0):.1f}%")
                safe_print(f"    平均分: {stats.get('avg_score', 0):.1f}")
        
        # 优化建议
        if summary.recommendations:
            safe_print(f"\n💡 优化建议:")
            for i, rec in enumerate(summary.recommendations, 1):
                safe_print(f"  {i}. {rec}")
        
        safe_print(f"\n📅 评估时间: {summary.evaluation_time.strftime('%Y-%m-%d %H:%M:%S')}")
        safe_print(f"{'='*60}")
    
    async def compare_agents(self, agents: List[Tuple[Any, str]], 
                          tasks: List[EvaluationTask] = None) -> Dict[str, AgentEvaluationSummary]:
        """比较多个Agent"""
        safe_print(f"开始Agent对比评估，共{len(agents)}个Agent")
        
        results = {}
        
        for agent, agent_name in agents:
            safe_print(f"\n评估Agent: {agent_name}")
            summary = await self.evaluate_agent(agent, agent_name, tasks)
            results[agent_name] = summary
            
            # 短暂休息以避免系统负载过高
            await asyncio.sleep(1)
        
        # 显示对比结果
        self._display_comparison(results)
        
        return results
    
    def _display_comparison(self, results: Dict[str, AgentEvaluationSummary]):
        """显示对比结果"""
        safe_print(f"\n{'='*80}")
        safe_print(f"Agent对比报告")
        safe_print(f"{'='*80}")
        
        safe_print(f"{'Agent':<20} {'总分':<10} {'成功率':<10} {'平均时间':<12}")
        safe_print("-" * 60)
        
        for agent_name, summary in results.items():
            safe_print(f"{agent_name:<20} {summary.average_score:<10.1f} "
                       f"{summary.success_rate:<10.1f}% {summary.average_execution_time:<12.2f}s")
        
        # 找出最佳Agent
        best_agent = max(results.items(), key=lambda x: x[1].average_score)
        safe_print(f"\n🏆 最佳Agent: {best_agent[0]} (得分: {best_agent[1].average_score:.1f})")
        
        safe_print(f"{'='*80}")

async def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Leo Agent Evaluation Framework')
    parser.add_argument('--project-root', type=str, default='.', help='Project root directory')
    parser.add_argument('--agent', type=str, help='Agent name to evaluate')
    parser.add_argument('--compare', action='store_true', help='Compare multiple agents')
    parser.add_argument('--tasks-file', type=str, help='Custom tasks JSON file')
    parser.add_argument('--output-json', type=str, help='Output results to JSON file')
    
    args = parser.parse_args()
    
    # 创建评估框架
    framework = AgentEvaluationFramework(Path(args.project_root))
    
    if args.compare:
        # 比较多个Agent - 这里使用技能发现系统作为示例
        agents = [
            (framework.discovery, "SkillDiscoverySystem"),
        ]
        
        results = await framework.compare_agents(agents)
        
    else:
        # 评估单个Agent
        agent_name = args.agent or "SkillDiscoverySystem"
        agent = framework.discovery  # 示例Agent
        
        summary = await framework.evaluate_agent(agent, agent_name)
        framework.display_evaluation_summary(summary)
        
        # 保存到指定文件
        if args.output_json:
            result_data = asdict(summary)
            result_data['evaluation_time'] = summary.evaluation_time.isoformat()
            with open(args.output_json, 'w', encoding='utf-8') as f:
                json.dump(result_data, f, indent=2, ensure_ascii=False)
            safe_print(f"\n评估报告已保存到: {args.output_json}")

if __name__ == "__main__":
    asyncio.run(main())