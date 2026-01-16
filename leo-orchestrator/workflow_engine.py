"""
Workflow Engine
===============
工作流执行引擎 - 负责编排和执行多Agent协作流程
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import sys

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
    - Agent间数据传递
    - 错误处理和重试
    - 执行状态跟踪
    """

    def __init__(self, agents: Dict[str, Any]):
        """
        初始化工作流引擎

        Args:
            agents: Agent字典 {agent_name: agent_instance}
        """
        self.agents = agents
        self.execution_history = []

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

        print(f"\n🔄 开始执行工作流: {workflow_name}")
        print(f"   描述: {workflow.get('description', '')}")
        print(f"   步骤数: {len(steps)}")

        results = []
        context = kwargs.copy()  # 初始上下文

        for i, step in enumerate(steps, 1):
            step_name = step.get('name', f'step_{i}')
            agent_name = step.get('agent')
            description = step.get('description', '')

            print(f"\n📍 步骤 {i}/{len(steps)}: {step_name}")
            print(f"   Agent: {agent_name}")
            print(f"   描述: {description}")

            try:
                # 执行步骤
                step_result = self._execute_step(agent_name, step_name, context)

                # 记录结果
                results.append({
                    'step': step_name,
                    'agent': agent_name,
                    'success': True,
                    'result': step_result
                })

                # 更新上下文（将结果传递给下一步）
                if isinstance(step_result, dict):
                    context.update(step_result)

                print(f"   ✅ 步骤完成")

            except Exception as e:
                print(f"   ❌ 步骤失败: {e}")
                results.append({
                    'step': step_name,
                    'agent': agent_name,
                    'success': False,
                    'error': str(e)
                })

                # 决定是否继续执行
                if not workflow.get('continue_on_error', False):
                    print(f"\n⚠️  工作流中断（步骤失败）")
                    break

        # 生成最终结果
        final_result = self._generate_final_result(workflow_name, results, context)

        # 记录执行历史
        self.execution_history.append({
            'workflow': workflow_name,
            'result': final_result
        })

        return final_result

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
        print(f"📊 工作流执行完成: {workflow_name}")
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
        'task-agent': MockAgent('task-agent')
    }

    # 创建引擎
    engine = WorkflowEngine(agents)

    # 测试工作流
    workflow = {
        'name': '内容生产线',
        'description': '研究→创作→发布',
        'steps': [
            {'name': 'research', 'agent': 'research-agent', 'description': '信息收集'},
            {'name': 'create', 'agent': 'creative-agent', 'description': '内容创作'},
            {'name': 'publish', 'agent': 'task-agent', 'description': '发布推广'}
        ]
    }

    # 执行
    result = engine.execute(workflow, task='生成房地产分析文章')
    print(f"\n最终结果: {result}")
