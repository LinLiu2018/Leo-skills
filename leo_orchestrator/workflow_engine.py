"""
Workflow Engine
===============
工作流执行引擎 - 负责编排和执行多Agent协作流程

功能:
- 多步骤顺序执行
- 条件分支
- 并行执行
- 重试机制
- 超时控制
- Agent间数据传递
- 执行状态跟踪
"""

from typing import Dict, Any, List, Optional, Callable
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
import sys
import time

# 添加父目录到路径
parent_path = Path(__file__).parent.parent
if str(parent_path) not in sys.path:
    sys.path.insert(0, str(parent_path))


class WorkflowEngine:
    """
    Workflow Engine
    ===============
    工作流执行引擎，负责：
    - 执行多步骤工作流
    - 条件分支支持
    - 并行执行支持
    - 重试机制
    - 超时控制
    - Agent间数据传递
    - 错误处理
    - 执行状态跟踪
    """

    def __init__(self, agents: Dict[str, Any], max_workers: int = 4):
        """
        初始化工作流引擎

        Args:
            agents: Agent字典 {agent_name: agent_instance}
            max_workers: 并行执行的最大工作线程数
        """
        self.agents = agents
        self.execution_history = []
        self.max_workers = max_workers

    def execute(self, workflow: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        执行工作流

        Args:
            workflow: 工作流配置
            **kwargs: 初始参数

        Returns:
            执行结果
        """
        workflow_name = workflow.get('name', 'Unknown')
        steps = workflow.get('steps', [])

        print(f"\n[Workflow] 开始执行工作流: {workflow_name}")
        print(f"   描述: {workflow.get('description', '')}")
        print(f"   步骤数: {len(steps)}")

        results = []
        context = kwargs.copy()  # 初始上下文

        i = 0
        while i < len(steps):
            step = steps[i]
            step_name = step.get('name', f'step_{i+1}')
            step_type = step.get('type', 'sequential')  # sequential, parallel, conditional

            print(f"\n[Step {i+1}/{len(steps)}] {step_name} (类型: {step_type})")

            try:
                if step_type == 'parallel':
                    # 并行执行
                    step_result = self._execute_parallel_step(step, context)
                elif step_type == 'conditional':
                    # 条件分支
                    step_result, next_step = self._execute_conditional_step(step, context)
                    if next_step is not None:
                        # 跳转到指定步骤
                        i = self._find_step_index(steps, next_step)
                        if i == -1:
                            raise ValueError(f"条件分支目标步骤不存在: {next_step}")
                        continue
                else:
                    # 顺序执行（支持重试和超时）
                    step_result = self._execute_step_with_retry(step, context)

                # 记录结果
                results.append({
                    'step': step_name,
                    'type': step_type,
                    'success': True,
                    'result': step_result
                })

                # 更新上下文
                if isinstance(step_result, dict):
                    context.update(step_result)

                print(f"   [OK] 步骤完成")

            except Exception as e:
                print(f"   [FAIL] 步骤失败: {e}")
                results.append({
                    'step': step_name,
                    'type': step_type,
                    'success': False,
                    'error': str(e)
                })

                if not workflow.get('continue_on_error', False):
                    print(f"\n[Workflow] 工作流中断（步骤失败）")
                    break

            i += 1

        # 生成最终结果
        final_result = self._generate_final_result(workflow_name, results, context)

        # 记录执行历史
        self.execution_history.append({
            'workflow': workflow_name,
            'result': final_result
        })

        return final_result

    def _execute_step_with_retry(self, step: Dict[str, Any], context: Dict[str, Any]) -> Any:
        """
        执行步骤（支持重试和超时）

        Args:
            step: 步骤配置
            context: 上下文数据

        Returns:
            步骤执行结果
        """
        agent_name = step.get('agent')
        step_name = step.get('name', 'unknown')
        max_retries = step.get('retries', 1)
        timeout = step.get('timeout', None)  # 秒

        last_error = None

        for attempt in range(max_retries):
            if attempt > 0:
                print(f"   [Retry] 第 {attempt + 1} 次重试...")

            try:
                if timeout:
                    result = self._execute_with_timeout(agent_name, step_name, context, timeout)
                else:
                    result = self._execute_step(agent_name, step_name, context)
                return result

            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    time.sleep(1)  # 重试前等待1秒

        raise last_error

    def _execute_with_timeout(self, agent_name: str, step_name: str, context: Dict[str, Any], timeout: int) -> Any:
        """
        带超时的步骤执行

        Args:
            agent_name: Agent名称
            step_name: 步骤名称
            context: 上下文数据
            timeout: 超时时间（秒）

        Returns:
            步骤执行结果
        """
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(self._execute_step, agent_name, step_name, context)
            try:
                return future.result(timeout=timeout)
            except FuturesTimeoutError:
                raise TimeoutError(f"步骤 '{step_name}' 执行超时（{timeout}秒）")

    def _execute_parallel_step(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        并行执行多个子步骤

        Args:
            step: 步骤配置（包含 parallel_steps 列表）
            context: 上下文数据

        Returns:
            所有子步骤的合并结果
        """
        parallel_steps = step.get('parallel_steps', [])
        if not parallel_steps:
            return {}

        print(f"   [Parallel] 并行执行 {len(parallel_steps)} 个子步骤")

        results = {}
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {}
            for sub_step in parallel_steps:
                agent_name = sub_step.get('agent')
                sub_step_name = sub_step.get('name', 'unknown')
                future = executor.submit(self._execute_step, agent_name, sub_step_name, context)
                futures[future] = sub_step_name

            for future in futures:
                sub_step_name = futures[future]
                try:
                    result = future.result()
                    results[sub_step_name] = result
                    print(f"      [OK] {sub_step_name} 完成")
                except Exception as e:
                    results[sub_step_name] = {'error': str(e)}
                    print(f"      [FAIL] {sub_step_name} 失败: {e}")

        return results

    def _execute_conditional_step(self, step: Dict[str, Any], context: Dict[str, Any]) -> tuple:
        """
        执行条件分支步骤

        Args:
            step: 步骤配置（包含 condition 和 branches）
            context: 上下文数据

        Returns:
            (执行结果, 下一步骤名称或None)
        """
        condition_key = step.get('condition_key')  # 上下文中的键
        branches = step.get('branches', {})  # {value: step_name}
        default_branch = step.get('default', None)

        # 获取条件值
        condition_value = context.get(condition_key)
        print(f"   [Condition] {condition_key} = {condition_value}")

        # 查找匹配的分支
        next_step = branches.get(str(condition_value), default_branch)

        if next_step:
            print(f"   [Branch] 跳转到: {next_step}")
        else:
            print(f"   [Branch] 无匹配分支，继续顺序执行")

        return {'condition': condition_key, 'value': condition_value, 'branch': next_step}, next_step

    def _find_step_index(self, steps: List[Dict[str, Any]], step_name: str) -> int:
        """
        查找步骤索引

        Args:
            steps: 步骤列表
            step_name: 步骤名称

        Returns:
            步骤索引，未找到返回 -1
        """
        for i, step in enumerate(steps):
            if step.get('name') == step_name:
                return i
        return -1

    def _execute_step(self, agent_name: str, step_name: str, context: Dict[str, Any]) -> Any:
        """
        执行单个步骤

        Args:
            agent_name: Agent名称
            step_name: 步骤名称
            context: 上下文数据

        Returns:
            步骤执行结果
        """
        # 获取Agent
        agent = self.agents.get(agent_name)

        if not agent:
            raise ValueError(f"Agent不存在: {agent_name}")

        # 构造任务描述
        task = context.get('task', step_name)

        # 从context中移除task，避免重复传递
        context_copy = context.copy()
        context_copy.pop('task', None)

        # 执行Agent
        result = agent.execute(task, **context_copy)

        return result

    def _generate_final_result(self,
                               workflow_name: str,
                               results: List[Dict[str, Any]],
                               context: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成最终结果

        Args:
            workflow_name: 工作流名称
            results: 步骤结果列表
            context: 最终上下文

        Returns:
            最终结果字典
        """
        successful_steps = [r for r in results if r.get('success', False)]
        failed_steps = [r for r in results if not r.get('success', False)]

        print(f"\n{'='*60}")
        print(f"[Workflow] 执行完成: {workflow_name}")
        print(f"{'='*60}")
        print(f"总步骤数: {len(results)}")
        print(f"成功: {len(successful_steps)}")
        print(f"失败: {len(failed_steps)}")

        return {
            'workflow': workflow_name,
            'total_steps': len(results),
            'successful_steps': len(successful_steps),
            'failed_steps': len(failed_steps),
            'success': len(failed_steps) == 0,
            'results': results,
            'context': context
        }

    def get_execution_history(self) -> List[Dict[str, Any]]:
        """获取执行历史"""
        return self.execution_history


# ==================== 使用示例 ====================

if __name__ == "__main__":
    # 模拟测试
    class MockAgent:
        def __init__(self, name):
            self.name = name

        def execute(self, task, **kwargs):
            return {
                'agent': self.name,
                'task': task,
                'result': f'{self.name}执行完成'
            }

    # 创建模拟Agents
    agents = {
        'research-agent': MockAgent('research-agent'),
        'creative-agent': MockAgent('creative-agent'),
        'analysis-agent': MockAgent('analysis-agent'),
        'task-agent': MockAgent('task-agent')
    }

    # 创建引擎
    engine = WorkflowEngine(agents)

    # 测试1: 基础顺序工作流
    print("\n" + "="*60)
    print("测试1: 基础顺序工作流")
    print("="*60)

    workflow1 = {
        'name': '内容生产线',
        'description': '研究->创作->发布',
        'steps': [
            {'name': 'research', 'agent': 'research-agent', 'description': '信息收集'},
            {'name': 'create', 'agent': 'creative-agent', 'description': '内容创作'},
            {'name': 'publish', 'agent': 'task-agent', 'description': '发布推广'}
        ]
    }
    result1 = engine.execute(workflow1, task='生成房地产分析文章')

    # 测试2: 并行执行工作流
    print("\n" + "="*60)
    print("测试2: 并行执行工作流")
    print("="*60)

    workflow2 = {
        'name': '并行分析流程',
        'description': '同时执行多个分析任务',
        'steps': [
            {
                'name': 'parallel_analysis',
                'type': 'parallel',
                'parallel_steps': [
                    {'name': 'market_analysis', 'agent': 'analysis-agent'},
                    {'name': 'competitor_analysis', 'agent': 'research-agent'},
                    {'name': 'trend_analysis', 'agent': 'analysis-agent'}
                ]
            },
            {'name': 'summarize', 'agent': 'creative-agent', 'description': '汇总分析结果'}
        ]
    }
    result2 = engine.execute(workflow2, task='综合市场分析')

    # 测试3: 带重试的工作流
    print("\n" + "="*60)
    print("测试3: 带重试和超时的工作流")
    print("="*60)

    workflow3 = {
        'name': '可靠执行流程',
        'description': '带重试机制的工作流',
        'steps': [
            {'name': 'fetch_data', 'agent': 'research-agent', 'retries': 3, 'timeout': 30},
            {'name': 'process', 'agent': 'analysis-agent', 'retries': 2}
        ]
    }
    result3 = engine.execute(workflow3, task='获取并处理数据')

    print("\n所有测试完成!")
