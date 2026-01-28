"""
AiNewsSummaryAgent

AI新闻摘要代理，自动收集和生成AI相关新闻摘要
"""

import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List

# 添加父目录到路径
parent_path = Path(__file__).parent.parent.parent
if str(parent_path) not in sys.path:
    sys.path.insert(0, str(parent_path))

if TYPE_CHECKING:
    from leo_subagents.agents.base_agent import BaseAgent, AgentConfig
else:
    from leo_subagents.agents.base_agent import BaseAgent, AgentConfig

from leo_subagents.agents.base_agent import logger
from leo_system.metrics import track_time


class AiNewsSummaryAgent(BaseAgent):
    """
    AiNewsSummaryAgent

    AI新闻摘要代理，自动收集和生成AI相关新闻摘要
    """

    def __init__(self, config: AgentConfig):
        """初始化 Agent"""
        super().__init__(config)
        self.agent_name = "ai_news_summary"

    def can_handle(self, task: str) -> float:
        """
        判断是否能处理此任务

        Args:
            task: 任务描述

        Returns:
            置信度 (0.0 - 1.0)
        """
        task_lower = task.lower()

        # 定义关键词匹配
        keywords = [
            "ai_news_summary",
            "AI新闻摘要代理，自动收集和生成AI相关"
        ]

        for keyword in keywords:
            if keyword.lower() in task_lower:
                return 0.9

        # 检查是否需要使用的技能
        for skill in self.config.skills:
            if skill.lower() in task_lower:
                return 0.7

        return 0.3

    @track_time
    def execute(self, task: str, **kwargs) -> Dict[str, Any]:
        """
        执行任务

        Args:
            task: 任务描述
            **kwargs: 任务参数

        Returns:
            执行结果
        """
        try:
            # 记录任务
            self.log_task(task, {"status": "started"})

            # 规划执行步骤
            plan = self.plan_execution(task, **kwargs)

            # 执行计划
            results = []
            for step in plan:
                step_result = {
                    "step": step["step"],
                    "skill": step.get("skill", ""),
                    "status": "pending"
                }

                # 如果有技能，使用技能执行
                if step.get("skill"):
                    try:
                        skill_result = self.use_skill(
                            step["skill"],
                            step.get("action", "execute"),
                            **step.get("params", {})
                        )
                        step_result["result"] = skill_result
                        step_result["status"] = "completed"
                    except Exception as e:
                        step_result["error"] = str(e)
                        step_result["status"] = "failed"

                results.append(step_result)

            # 汇总结果
            success_count = sum(1 for r in results if r["status"] == "completed")
            total_count = len(results)

            final_result = {
                "task": task,
                "status": "completed" if success_count == total_count else "partial",
                "total_steps": total_count,
                "completed_steps": success_count,
                "results": results,
                "agent": self.agent_name
            }

            # 记录完成
            self.log_task(task, final_result)

            return final_result

        except Exception as e:
            error_result = {
                "task": task,
                "status": "failed",
                "error": str(e),
                "agent": self.agent_name
            }
            self.log_task(task, error_result)
            logger.error(f"Agent execution failed: {e}")
            return error_result


# ==================== 注册 ====================

# 在 AgentFactory 中注册此 Agent
# AGENT_TYPE = "researcher"
