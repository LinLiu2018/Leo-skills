"""
Analysis Agent
==============
分析代理 - 负责数据分析、趋势分析、报告生成

参考: claude-code-subagents/official/claude-agent-sdk-demos/research-agent/
      (Data Analyst子代理)
"""

from typing import Dict, Any, List
import sys
from pathlib import Path

# 添加父目录到路径
parent_path = Path(__file__).parent.parent.parent
if str(parent_path) not in sys.path:
    sys.path.insert(0, str(parent_path))

# 使用绝对导入
from leo_subagents.agents.base_agent import BaseAgent, AgentConfig, AgentFactory


class AnalysisAgent(BaseAgent):
    """
    Analysis Agent
    ==============
    分析代理，擅长：
    - 数据分析和处理
    - 趋势分析和预测
    - 报告生成
    - 决策建议

    参考官方Data Analyst子代理实现
    """

    # 激活关键词
    ACTIVATION_KEYWORDS = [
        "分析", "统计", "趋势", "报告",
        "数据", "指标", "评估", "对比"
    ]

    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.capabilities = {
            "data_analysis": "data-analyzer-cskill",
            "trend_analysis": "data-analyzer-cskill",
            "report_generation": "data-analyzer-cskill"
        }

    def can_handle(self, task: str) -> float:
        """
        判断是否能处理此任务

        Args:
            task: 任务描述

        Returns:
            置信度 (0.0 - 1.0)
        """
        task_lower = task.lower()

        # 检查激活关键词
        keyword_matches = sum(1 for kw in self.ACTIVATION_KEYWORDS if kw in task_lower)

        # 检查能力匹配
        capability_score = 0.0

        if any(kw in task_lower for kw in ["分析", "analysis", "analyze"]):
            capability_score += 0.4
        if any(kw in task_lower for kw in ["数据", "统计", "data", "statistics"]):
            capability_score += 0.3
        if any(kw in task_lower for kw in ["趋势", "预测", "trend", "forecast"]):
            capability_score += 0.2
        if any(kw in task_lower for kw in ["报告", "report"]):
            capability_score += 0.1

        # 计算总分
        score = min(1.0, 0.3 + keyword_matches * 0.1 + capability_score)

        return score

    def execute(self, task: str, **kwargs) -> Dict[str, Any]:
        """
        执行分析任务

        Args:
            task: 任务描述
            **kwargs: 任务参数
                - data: 待分析数据
                - analysis_type: 分析类型 (descriptive, trend, comparative)
                - output_format: 输出格式 (text, json, markdown)

        Returns:
            执行结果
        """
        # 1. 分析任务类型
        analysis_type = self._determine_analysis_type(task, **kwargs)

        # 从 kwargs 中移除 analysis_type 避免重复传递
        plan_kwargs = {k: v for k, v in kwargs.items() if k != 'analysis_type'}

        # 2. 规划分析步骤
        steps = self._plan_analysis(task, analysis_type, **plan_kwargs)

        # 3. 执行分析步骤
        results = []
        for step in steps:
            step_result = self._execute_analysis_step(step)
            results.append(step_result)

        # 4. 生成分析报告
        final_result = self._generate_analysis_report(task, analysis_type, results, **plan_kwargs)

        # 记录任务
        self.log_task(task, final_result)

        return final_result

    def _determine_analysis_type(self, task: str, **kwargs) -> str:
        """
        确定分析类型

        Args:
            task: 任务描述
            **kwargs: 任务参数

        Returns:
            分析类型
        """
        if "analysis_type" in kwargs:
            return kwargs["analysis_type"]

        task_lower = task.lower()

        if any(kw in task_lower for kw in ["趋势", "变化", "发展", "trend"]):
            return "trend"
        elif any(kw in task_lower for kw in ["对比", "比较", "comparative"]):
            return "comparative"
        else:
            return "descriptive"

    def _plan_analysis(self,
                      task: str,
                      analysis_type: str,
                      **kwargs) -> List[Dict[str, Any]]:
        """
        规划分析步骤

        Args:
            task: 任务描述
            analysis_type: 分析类型
            **kwargs: 任务参数

        Returns:
            分析步骤列表
        """
        steps = []

        if analysis_type == "descriptive":
            # 描述性分析
            steps.append({
                "step": 1,
                "name": "数据概览",
                "action": "summarize_data",
                "params": kwargs
            })
            steps.append({
                "step": 2,
                "name": "关键指标提取",
                "action": "extract_metrics",
                "params": kwargs
            })

        elif analysis_type == "trend":
            # 趋势分析
            steps.append({
                "step": 1,
                "name": "数据收集",
                "action": "collect_data",
                "params": kwargs
            })
            steps.append({
                "step": 2,
                "name": "趋势识别",
                "action": "identify_trends",
                "params": kwargs
            })
            steps.append({
                "step": 3,
                "name": "预测生成",
                "action": "generate_forecast",
                "params": kwargs
            })

        elif analysis_type == "comparative":
            # 对比分析
            steps.append({
                "step": 1,
                "name": "数据对比",
                "action": "compare_data",
                "params": kwargs
            })
            steps.append({
                "step": 2,
                "name": "差异分析",
                "action": "analyze_differences",
                "params": kwargs
            })

        return steps

    def _execute_analysis_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行单个分析步骤

        Args:
            step: 步骤定义

        Returns:
            步骤执行结果
        """
        action = step["action"]
        params = step.get("params", {})
        skill_name = "data-analyzer-cskill"

        try:
            # 映射 action 到 skill 方法
            action_mapping = {
                "summarize_data": ("analyze", {"analysis_type": "descriptive"}),
                "extract_metrics": ("analyze", {"analysis_type": "descriptive"}),
                "collect_data": ("analyze", {"analysis_type": "descriptive"}),
                "identify_trends": ("analyze", {"analysis_type": "trend"}),
                "generate_forecast": ("analyze", {"analysis_type": "trend"}),
                "compare_data": ("compare", {}),
                "analyze_differences": ("analyze", {"analysis_type": "comparative"}),
            }

            if action in action_mapping:
                skill_action, extra_params = action_mapping[action]
                # 合并参数
                call_params = {**params, **extra_params}
                # 调用 data-analyzer-cskill
                execution_result = self.use_skill(skill_name, skill_action, **call_params)
                # 处理 ExecutionResult 对象
                if hasattr(execution_result, 'result'):
                    result = execution_result.result if isinstance(execution_result.result, dict) else {"data": execution_result.result}
                    result["success"] = execution_result.success
                else:
                    result = execution_result if isinstance(execution_result, dict) else {"data": execution_result, "success": True}
            else:
                result = {"message": f"未知操作: {action}", "success": False}

            return {
                "step": step["step"],
                "name": step["name"],
                "success": result.get("success", True) if isinstance(result, dict) else True,
                "result": result
            }

        except Exception as e:
            return {
                "step": step["step"],
                "name": step["name"],
                "success": False,
                "error": str(e)
            }

    def _generate_analysis_report(self,
                                  task: str,
                                  analysis_type: str,
                                  results: List[Dict[str, Any]],
                                  **kwargs) -> Dict[str, Any]:
        """
        生成分析报告

        Args:
            task: 任务描述
            analysis_type: 分析类型
            results: 分析结果列表
            **kwargs: 任务参数

        Returns:
            分析报告
        """
        successful_results = [r for r in results if r.get("success", False)]
        failed_results = [r for r in results if not r.get("success", False)]

        # 生成报告摘要
        summary = self._create_report_summary(task, analysis_type, successful_results)

        return {
            "task": task,
            "analysis_type": analysis_type,
            "total_steps": len(results),
            "successful_steps": len(successful_results),
            "failed_steps": len(failed_results),
            "summary": summary,
            "detailed_results": successful_results,
            "errors": [r.get("error") for r in failed_results] if failed_results else []
        }

    def _create_report_summary(self,
                              task: str,
                              analysis_type: str,
                              results: List[Dict[str, Any]]) -> str:
        """
        创建报告摘要

        Args:
            task: 任务描述
            analysis_type: 分析类型
            results: 结果列表

        Returns:
            摘要文本
        """
        summary_parts = [
            f"分析任务: {task}",
            f"分析类型: {analysis_type}",
            f"完成步骤: {len(results)}",
            "\n分析步骤:"
        ]

        for result in results:
            summary_parts.append(f"- {result['name']}: 完成")

        return "\n".join(summary_parts)

    def get_capabilities(self) -> Dict[str, str]:
        """获取能力列表"""
        return self.capabilities

    def get_help_text(self) -> str:
        """获取帮助文本"""
        return f"""
Analysis Agent 帮助
===================

能力:
1. 数据分析 - 描述性统计和数据处理
2. 趋势分析 - 识别趋势和生成预测
3. 对比分析 - 多维度数据对比
4. 报告生成 - 生成分析报告

激活关键词:
{', '.join(self.ACTIVATION_KEYWORDS)}

使用示例:
- agent.execute("分析销售数据", data=sales_data, analysis_type="descriptive")
- agent.execute("分析市场趋势", analysis_type="trend")
- agent.execute("对比产品性能", analysis_type="comparative")

参数说明:
- data: 待分析数据（可选）
- analysis_type: 分析类型
  - descriptive: 描述性分析
  - trend: 趋势分析
  - comparative: 对比分析
- output_format: 输出格式（默认text）
"""


# 注册到工厂
AgentFactory.register_agent_class("analyzer", AnalysisAgent)


# ==================== 使用示例 ====================

if __name__ == "__main__":
    # 创建配置
    config = AgentConfig(
        name="analysis-agent",
        type="analyzer",
        priority=3,
        skills=[],
        description="分析代理"
    )

    # 创建Agent
    agent = AnalysisAgent(config)

    # 测试能力判断
    print("能力判断测试:")
    print(f"- 分析任务: {agent.can_handle('分析销售数据')}")
    print(f"- 趋势任务: {agent.can_handle('分析市场趋势')}")
    print(f"- 对比任务: {agent.can_handle('对比产品性能')}")

    # 获取帮助
    print(agent.get_help_text())

    # 获取状态
    print(f"\nAgent状态: {agent.get_status()}")
