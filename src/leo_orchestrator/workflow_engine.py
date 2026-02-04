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
- YAML工作流定义支持
"""

import sys
import time
import yaml
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FuturesTimeoutError
from pathlib import Path
from typing import Any, Dict, List, Optional

# 添加父目录到路径
parent_path = Path(__file__).parent.parent
if str(parent_path) not in sys.path:
    sys.path.insert(0, str(parent_path))

# 导入日志和错误处理
from leo_system.logger import get_logger
from leo_system.errors import WorkflowExecutionError, AgentNotFoundError
from leo_system.metrics import track_time
from leo_system.interaction_logger import get_interaction_logger

# 创建日志记录器
logger = get_logger(__name__)


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

    @track_time
    def execute(self, workflow: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        执行工作流

        Args:
            workflow: 工作流配置
            **kwargs: 初始参数

        Returns:
            执行结果
        """
        workflow_name = workflow.get("name", "Unknown")
        steps = workflow.get("steps", [])

        logger.info(f"开始执行工作流: {workflow_name}")
        logger.info(f"描述: {workflow.get('description', '')}")
        logger.info(f"步骤数: {len(steps)}")

        # 记录工作流开始
        interaction_logger = get_interaction_logger()
        workflow_id = interaction_logger.log_workflow_start(
            workflow_name=workflow_name,
            inputs=kwargs,
            total_steps=len(steps)
        )
        workflow_start_time = time.time()

        results = []
        context = kwargs.copy()  # 初始上下文

        i = 0
        while i < len(steps):
            step = steps[i]
            step_name = step.get("name", f"step_{i+1}")
            step_type = step.get("type", "sequential")  # sequential, parallel, conditional

            logger.info(f"执行步骤 {i+1}/{len(steps)}: {step_name} (类型: {step_type})")
            step_start_time = time.time()

            try:
                if step_type == "parallel":
                    # 并行执行
                    step_result = self._execute_parallel_step(step, context)
                elif step_type == "conditional":
                    # 条件分支
                    step_result, next_step = self._execute_conditional_step(step, context)
                    if next_step is not None:
                        # 跳转到指定步骤
                        i = self._find_step_index(steps, next_step)
                        if i == -1:
                            raise WorkflowExecutionError(
                                workflow_name, step_name, f"条件分支目标步骤不存在: {next_step}"
                            )
                        continue
                else:
                    # 顺序执行（支持重试和超时）
                    step_result = self._execute_step_with_retry(step, context)

                # 记录结果
                results.append(
                    {"step": step_name, "type": step_type, "success": True, "result": step_result}
                )

                # 更新上下文
                if isinstance(step_result, dict):
                    context.update(step_result)

                logger.info(f"步骤 {step_name} 完成")

                # 记录步骤完成
                step_time = time.time() - step_start_time
                interaction_logger.log_workflow_step(
                    step_name=step_name,
                    step_number=i + 1,
                    agent=step.get("agent", "unknown"),
                    status="completed",
                    result_summary=str(step_result)[:200] if step_result else None,
                    execution_time=step_time
                )

            except Exception as e:
                logger.error(f"步骤 {step_name} 失败: {e}")
                results.append(
                    {"step": step_name, "type": step_type, "success": False, "error": str(e)}
                )

                # 记录步骤失败
                step_time = time.time() - step_start_time
                interaction_logger.log_workflow_step(
                    step_name=step_name,
                    step_number=i + 1,
                    agent=step.get("agent", "unknown"),
                    status="failed",
                    result_summary=str(e),
                    execution_time=step_time
                )

                if not workflow.get("continue_on_error", False):
                    logger.warning(f"工作流 {workflow_name} 中断（步骤失败）")
                    break

            i += 1

        # 生成最终结果
        final_result = self._generate_final_result(workflow_name, results, context)

        # 记录执行历史
        self.execution_history.append({"workflow": workflow_name, "result": final_result})

        # 记录工作流结束
        total_time = time.time() - workflow_start_time
        completed_steps = sum(1 for r in results if r.get("success", False))
        interaction_logger.log_workflow_end(
            success=final_result.get("success", False),
            total_time=total_time,
            completed_steps=completed_steps,
            output_summary=str(final_result.get("output", ""))[:200]
        )

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
        agent_name = step.get("agent")
        step_name = step.get("name", "unknown")
        max_retries = step.get("retries", 1)
        timeout = step.get("timeout", None)  # 秒

        last_error = None

        for attempt in range(max_retries):
            if attempt > 0:
                logger.info(f"步骤 {step_name} 第 {attempt + 1} 次重试...")

            try:
                if timeout:
                    result = self._execute_with_timeout(agent_name, step_name, context, timeout)
                else:
                    result = self._execute_step(agent_name, step_name, context)
                return result

            except Exception as e:
                last_error = e
                logger.warning(f"步骤 {step_name} 尝试 {attempt + 1} 失败: {e}")
                if attempt < max_retries - 1:
                    time.sleep(1)  # 重试前等待1秒

        raise last_error

    def _execute_with_timeout(
        self, agent_name: str, step_name: str, context: Dict[str, Any], timeout: int
    ) -> Any:
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

    def _execute_parallel_step(
        self, step: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        并行执行多个子步骤

        Args:
            step: 步骤配置（包含 parallel_steps 列表）
            context: 上下文数据

        Returns:
            所有子步骤的合并结果
        """
        parallel_steps = step.get("parallel_steps", [])
        if not parallel_steps:
            return {}

        logger.info(f"并行执行 {len(parallel_steps)} 个子步骤")

        results = {}
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {}
            for sub_step in parallel_steps:
                agent_name = sub_step.get("agent")
                sub_step_name = sub_step.get("name", "unknown")
                future = executor.submit(self._execute_step, agent_name, sub_step_name, context)
                futures[future] = sub_step_name

            for future in futures:
                sub_step_name = futures[future]
                try:
                    result = future.result()
                    results[sub_step_name] = result
                    logger.info(f"并行子步骤 {sub_step_name} 完成")
                except Exception as e:
                    results[sub_step_name] = {"error": str(e)}
                    logger.error(f"并行子步骤 {sub_step_name} 失败: {e}")

        return results

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
        condition_key = step.get("condition_key")  # 上下文中的键
        branches = step.get("branches", {})  # {value: step_name}
        default_branch = step.get("default", None)

        # 获取条件值
        condition_value = context.get(condition_key)
        logger.info(f"条件分支: {condition_key} = {condition_value}")

        # 查找匹配的分支
        next_step = branches.get(str(condition_value), default_branch)

        if next_step:
            logger.info(f"跳转到步骤: {next_step}")
        else:
            logger.info("无匹配分支，继续顺序执行")

        return {
            "condition": condition_key,
            "value": condition_value,
            "branch": next_step,
        }, next_step

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
            if step.get("name") == step_name:
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
            raise AgentNotFoundError(agent_name)

        # 构造任务描述
        task = context.get("task", step_name)

        # 从context中移除task，避免重复传递
        context_copy = context.copy()
        context_copy.pop("task", None)

        # 执行Agent
        logger.debug(f"执行 Agent {agent_name} 处理任务: {task}")
        result = agent.execute(task, **context_copy)

        return result

    def _generate_final_result(
        self, workflow_name: str, results: List[Dict[str, Any]], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        生成最终结果

        Args:
            workflow_name: 工作流名称
            results: 步骤结果列表
            context: 最终上下文

        Returns:
            最终结果字典
        """
        successful_steps = [r for r in results if r.get("success", False)]
        failed_steps = [r for r in results if not r.get("success", False)]

        logger.info(f"工作流 {workflow_name} 执行完成")
        logger.info(f"总步骤数: {len(results)}, 成功: {len(successful_steps)}, 失败: {len(failed_steps)}")

        return {
            "workflow": workflow_name,
            "total_steps": len(results),
            "successful_steps": len(successful_steps),
            "failed_steps": len(failed_steps),
            "success": len(failed_steps) == 0,
            "results": results,
            "context": context,
        }

    def get_execution_history(self) -> List[Dict[str, Any]]:
        """获取执行历史"""
        return self.execution_history

    def load_workflow_from_yaml(self, yaml_path: str) -> Dict[str, Any]:
        """
        从YAML文件加载工作流定义

        Args:
            yaml_path: YAML文件路径

        Returns:
            工作流配置字典
        """
        path = Path(yaml_path)
        if not path.exists():
            raise FileNotFoundError(f"工作流文件不存在: {yaml_path}")

        with open(path, 'r', encoding='utf-8') as f:
            workflow = yaml.safe_load(f)

        logger.info(f"从 {yaml_path} 加载工作流: {workflow.get('name', 'Unknown')}")
        return workflow

    def execute_from_yaml(self, yaml_path: str, **kwargs) -> Dict[str, Any]:
        """
        从YAML文件加载并执行工作流

        Args:
            yaml_path: YAML文件路径
            **kwargs: 工作流参数

        Returns:
            执行结果
        """
        workflow = self.load_workflow_from_yaml(yaml_path)
        return self.execute(workflow, **kwargs)


class WorkflowDefinition:
    """
    工作流定义类
    =============
    用于创建和验证工作流定义
    """

    @staticmethod
    def create(
        name: str,
        description: str,
        steps: List[Dict[str, Any]],
        continue_on_error: bool = False
    ) -> Dict[str, Any]:
        """
        创建工作流定义

        Args:
            name: 工作流名称
            description: 工作流描述
            steps: 步骤列表
            continue_on_error: 错误时是否继续

        Returns:
            工作流定义字典
        """
        return {
            "name": name,
            "description": description,
            "steps": steps,
            "continue_on_error": continue_on_error,
            "version": "1.0"
        }

    @staticmethod
    def save_to_yaml(workflow: Dict[str, Any], yaml_path: str):
        """
        保存工作流到YAML文件

        Args:
            workflow: 工作流定义
            yaml_path: 保存路径
        """
        path = Path(yaml_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(workflow, f, allow_unicode=True, sort_keys=False)

        logger.info(f"工作流已保存到: {yaml_path}")


# ==================== 使用示例 ====================

if __name__ == "__main__":
    # 模拟测试
    class MockAgent:
        def __init__(self, name):
            self.name = name

        def execute(self, task, **kwargs):
            return {"agent": self.name, "task": task, "result": f"{self.name}执行完成"}

    # 创建模拟Agents
    agents = {
        "research-agent": MockAgent("research-agent"),
        "creative-agent": MockAgent("creative-agent"),
        "analysis-agent": MockAgent("analysis-agent"),
        "task-agent": MockAgent("task-agent"),
    }

    # 创建引擎
    engine = WorkflowEngine(agents)

    # 测试1: 基础顺序工作流
    logger.info("=" * 60)
    logger.info("测试1: 基础顺序工作流")
    logger.info("=" * 60)

    workflow1 = {
        "name": "内容生产线",
        "description": "研究->创作->发布",
        "steps": [
            {"name": "research", "agent": "research-agent", "description": "信息收集"},
            {"name": "create", "agent": "creative-agent", "description": "内容创作"},
            {"name": "publish", "agent": "task-agent", "description": "发布推广"},
        ],
    }
    result1 = engine.execute(workflow1, task="生成房地产分析文章")

    # 测试2: 并行执行工作流
    logger.info("=" * 60)
    logger.info("测试2: 并行执行工作流")
    logger.info("=" * 60)

    workflow2 = {
        "name": "并行分析流程",
        "description": "同时执行多个分析任务",
        "steps": [
            {
                "name": "parallel_analysis",
                "type": "parallel",
                "parallel_steps": [
                    {"name": "market_analysis", "agent": "analysis-agent"},
                    {"name": "competitor_analysis", "agent": "research-agent"},
                    {"name": "trend_analysis", "agent": "analysis-agent"},
                ],
            },
            {"name": "summarize", "agent": "creative-agent", "description": "汇总分析结果"},
        ],
    }
    result2 = engine.execute(workflow2, task="综合市场分析")

    # 测试3: 带重试的工作流
    logger.info("=" * 60)
    logger.info("测试3: 带重试和超时的工作流")
    logger.info("=" * 60)

    workflow3 = {
        "name": "可靠执行流程",
        "description": "带重试机制的工作流",
        "steps": [
            {"name": "fetch_data", "agent": "research-agent", "retries": 3, "timeout": 30},
            {"name": "process", "agent": "analysis-agent", "retries": 2},
        ],
    }
    result3 = engine.execute(workflow3, task="获取并处理数据")

    logger.info("所有测试完成!")
