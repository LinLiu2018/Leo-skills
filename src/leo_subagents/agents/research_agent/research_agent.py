"""
Research Agent
==============
研究代理 - 负责信息收集、文献调研、知识整理

参考: claude-code-subagents/official/claude-agent-sdk-demos/research-agent/
"""

import sys
from pathlib import Path
from typing import Any, Dict, List

# 添加父目录到路径
parent_path = Path(__file__).parent.parent.parent
if str(parent_path) not in sys.path:
    sys.path.insert(0, str(parent_path))

# 使用绝对导入
from leo_subagents.agents.base_agent import AgentConfig, AgentFactory, BaseAgent


class ResearchAgent(BaseAgent):
    """
    Research Agent
    ==============
    研究代理，擅长：
    - 信息收集和整理
    - 文献调研
    - 知识库构建
    - 研究报告生成

    参考官方实现，简化为单Agent架构，通过Skills完成任务
    """

    # 激活关键词
    ACTIVATION_KEYWORDS = ["研究", "调研", "分析", "报告", "收集", "整理", "查找", "搜索"]

    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.capabilities = {
            "research": "research_assistant_skill",
            "web_search": "web_search_skill",  # 🆕 添加WebSearch能力
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

        if any(kw in task_lower for kw in ["研究", "调研", "research"]):
            capability_score += 0.4
        if any(kw in task_lower for kw in ["分析", "报告", "analysis", "report"]):
            capability_score += 0.3
        if any(kw in task_lower for kw in ["收集", "整理", "搜索", "查找"]):
            capability_score += 0.2

        # 计算总分
        score = min(1.0, 0.3 + keyword_matches * 0.1 + capability_score)

        return score

    def execute(self, task: str, **kwargs) -> Dict[str, Any]:
        """
        执行研究任务

        Args:
            task: 任务描述
            **kwargs: 任务参数
                - topic: 研究主题
                - depth: 研究深度 (1-3)
                - output_format: 输出格式 (markdown, json)

        Returns:
            执行结果
        """
        # 1. 分析任务
        research_plan = self._plan_research(task, **kwargs)

        # 2. 执行研究步骤
        results = []
        for step in research_plan:
            step_result = self._execute_research_step(step)
            results.append(step_result)

        # 3. 汇总结果
        final_result = self._synthesize_results(task, results, **kwargs)

        # 记录任务
        self.log_task(task, final_result)

        return final_result

    def _plan_research(self, task: str, **kwargs) -> List[Dict[str, Any]]:
        """
        规划研究步骤

        Args:
            task: 任务描述
            **kwargs: 任务参数

        Returns:
            研究步骤列表
        """
        topic = kwargs.get("topic", task)
        depth = kwargs.get("depth", 2)

        # 将主题分解为子主题
        subtopics = self._break_down_topic(topic, depth)

        steps = []
        for i, subtopic in enumerate(subtopics):
            steps.append(
                {
                    "step": i + 1,
                    "subtopic": subtopic,
                    "skill": "research_assistant_skill",
                    "action": "research",
                    "params": {"topic": subtopic, "depth": depth},
                }
            )

        return steps

    def _break_down_topic(self, topic: str, depth: int) -> List[str]:
        """
        将主题分解为子主题

        Args:
            topic: 主题
            depth: 深度

        Returns:
            子主题列表
        """
        # 简化实现：根据深度生成子主题
        if depth == 1:
            return [topic]
        elif depth == 2:
            return [f"{topic} - 概述", f"{topic} - 详细分析"]
        else:  # depth == 3
            return [
                f"{topic} - 背景和概述",
                f"{topic} - 当前状态和趋势",
                f"{topic} - 未来展望和建议",
            ]

    def _execute_research_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行单个研究步骤

        Args:
            step: 步骤定义

        Returns:
            步骤执行结果
        """
        skill_name = step["skill"]
        action = step["action"]
        params = step.get("params", {})

        try:
            # 调用research_assistant_skill
            result = self.use_skill(skill_name, action, **params)

            return {
                "step": step["step"],
                "subtopic": step["subtopic"],
                "success": True,
                "result": result,
            }

        except Exception as e:
            return {
                "step": step["step"],
                "subtopic": step["subtopic"],
                "success": False,
                "error": str(e),
            }

    def _synthesize_results(
        self, task: str, results: List[Dict[str, Any]], **kwargs
    ) -> Dict[str, Any]:
        """
        汇总研究结果

        Args:
            task: 任务描述
            results: 研究结果列表
            **kwargs: 任务参数

        Returns:
            汇总结果
        """
        successful_results = [r for r in results if r.get("success", False)]
        failed_results = [r for r in results if not r.get("success", False)]

        # 提取所有研究内容
        research_content = []
        for result in successful_results:
            research_content.append(
                {"subtopic": result["subtopic"], "content": result.get("result", "")}
            )

        # 生成摘要
        summary = self._generate_summary(task, research_content)

        return {
            "task": task,
            "total_steps": len(results),
            "successful_steps": len(successful_results),
            "failed_steps": len(failed_results),
            "summary": summary,
            "research_content": research_content,
            "errors": [r.get("error") for r in failed_results] if failed_results else [],
        }

    def _generate_summary(self, task: str, research_content: List[Dict[str, Any]]) -> str:
        """
        生成研究摘要

        Args:
            task: 任务描述
            research_content: 研究内容列表

        Returns:
            摘要文本
        """
        summary_parts = [f"研究主题: {task}\n"]
        summary_parts.append(f"研究子主题数量: {len(research_content)}\n")
        summary_parts.append("\n子主题列表:")

        for i, content in enumerate(research_content, 1):
            summary_parts.append(f"{i}. {content['subtopic']}")

        return "\n".join(summary_parts)

    def get_capabilities(self) -> Dict[str, str]:
        """
        获取能力列表

        Returns:
            能力字典
        """
        return self.capabilities

    def get_help_text(self) -> str:
        """
        获取帮助文本

        Returns:
            帮助文本
        """
        return f"""
Research Agent 帮助
==================

能力:
1. 信息收集 - 使用 research_assistant_skill
2. 文献调研 - 深度研究和分析
3. 知识整理 - 结构化组织信息
4. 报告生成 - 生成研究摘要

激活关键词:
{', '.join(self.ACTIVATION_KEYWORDS)}

使用示例:
- agent.execute("研究量子计算的发展", depth=2)
- agent.execute("调研人工智能市场趋势", topic="AI市场", depth=3)
- agent.execute("收集关于区块链的资料", output_format="markdown")

参数说明:
- topic: 研究主题（可选，默认使用task）
- depth: 研究深度，1-3（默认2）
  - 1: 简单概述
  - 2: 概述 + 详细分析
  - 3: 背景 + 现状 + 展望
- output_format: 输出格式（默认markdown）
"""


# 注册到工厂
AgentFactory.register_agent_class("researcher", ResearchAgent)


# ==================== 使用示例 ====================

if __name__ == "__main__":
    # 创建配置
    config = AgentConfig(
        name="research-agent",
        type="researcher",
        priority=2,
        skills=["research_assistant_skill"],
        description="研究代理",
    )

    # 创建Agent
    agent = ResearchAgent(config)

    # 测试能力判断
    print("能力判断测试:")
    print(f"- 研究任务: {agent.can_handle('帮我研究量子计算')}")
    print(f"- 调研任务: {agent.can_handle('调研AI市场趋势')}")
    print(f"- 收集任务: {agent.can_handle('收集区块链资料')}")

    # 获取帮助
    print(agent.get_help_text())

    # 获取状态
    print(f"\nAgent状态: {agent.get_status()}")
