"""
Task Agent
==========
任务执行代理 - 负责执行具体任务，调用相关Skills
"""

from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentConfig, AgentFactory


class TaskAgent(BaseAgent):
    """
    Task Agent
    ==========
    任务执行代理，擅长：
    - 内容排版
    - 文档发布
    - 营销文档生成
    - 流程执行
    """

    # 激活关键词
    ACTIVATION_KEYWORDS = [
        "执行", "运行", "任务", "流程",
        "排版", "发布", "生成", "创建"
    ]

    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.capabilities = {
            "content_layout": "content-layout-leo-cskill",
            "news_publish": "realestate-news-publisher-cskill",
            "marketing_doc": "project-marketing-doc-generator-cskill"
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

        if any(kw in task_lower for kw in ["排版", "格式", "布局"]):
            capability_score += 0.3
        if any(kw in task_lower for kw in ["发布", "新闻", "资讯"]):
            capability_score += 0.3
        if any(kw in task_lower for kw in ["营销", "文档", "手册", "生成器"]):
            capability_score += 0.3

        # 计算总分
        score = min(1.0, 0.3 + keyword_matches * 0.1 + capability_score)

        return score

    def execute(self, task: str, **kwargs) -> Dict[str, Any]:
        """
        执行任务

        Args:
            task: 任务描述
            **kwargs: 任务参数

        Returns:
            执行结果
        """
        # 1. 分析任务
        task_type = self._analyze_task(task, **kwargs)

        # 2. 规划执行步骤
        steps = self.plan_execution(task, task_type=task_type, **kwargs)

        # 3. 执行步骤
        results = []
        for step in steps:
            step_result = self._execute_step(step)
            results.append(step_result)

        # 4. 汇总结果
        final_result = {
            "task": task,
            "task_type": task_type,
            "steps_completed": len(results),
            "successful": all(r.get("success", False) for r in results),
            "results": results
        }

        # 记录任务
        self.log_task(task, final_result)

        return final_result

    def _analyze_task(self, task: str, **kwargs) -> str:
        """
        分析任务类型

        Args:
            task: 任务描述
            **kwargs: 任务参数

        Returns:
            任务类型
        """
        task_lower = task.lower()

        if "排版" in task_lower or "layout" in task_lower:
            return "content_layout"
        elif "发布" in task_lower or "publish" in task_lower:
            return "news_publish"
        elif "营销" in task_lower or "marketing" in task_lower:
            return "marketing_doc"
        elif kwargs.get("project_type"):
            return "marketing_doc"
        else:
            return "general"

    def plan_execution(self,
                      task: str,
                      task_type: str = "general",
                      **kwargs) -> List[Dict[str, Any]]:
        """
        规划执行步骤

        Args:
            task: 任务描述
            task_type: 任务类型
            **kwargs: 任务参数

        Returns:
            执行步骤列表
        """
        steps = []

        if task_type == "content_layout":
            # 内容排版任务
            steps.append({
                "step": 1,
                "skill": "content-layout-leo-cskill",
                "action": "layout",
                "params": {
                    "content": kwargs.get("content", ""),
                    "style": kwargs.get("style", "data_driven")
                }
            })

        elif task_type == "news_publish":
            # 新闻发布任务
            steps.append({
                "step": 1,
                "skill": "realestate-news-publisher-cskill",
                "action": "publish",
                "params": {
                    "title": kwargs.get("title", ""),
                    "content": kwargs.get("content", ""),
                    "platform": kwargs.get("platform", "all")
                }
            })

        elif task_type == "marketing_doc":
            # 营销文档生成任务
            steps.append({
                "step": 1,
                "skill": "project-marketing-doc-generator-cskill",
                "action": "generate",
                "params": {
                    "project_name": kwargs.get("project_name", ""),
                    "project_type": kwargs.get("project_type", ""),
                    "features": kwargs.get("features", [])
                }
            })

        else:
            # 通用任务：尝试所有可用的Skills
            for skill_name in self.config.skills:
                steps.append({
                    "step": len(steps) + 1,
                    "skill": skill_name,
                    "action": "execute",
                    "params": kwargs
                })

        return steps

    def _execute_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行单个步骤

        Args:
            step: 步骤定义

        Returns:
            步骤执行结果
        """
        skill_name = step["skill"]
        action = step["action"]
        params = step.get("params", {})

        try:
            result = self.use_skill(skill_name, action, **params)

            return {
                "step": step["step"],
                "skill": skill_name,
                "action": action,
                "success": result.success if hasattr(result, 'success') else True,
                "result": result
            }

        except Exception as e:
            return {
                "step": step["step"],
                "skill": skill_name,
                "action": action,
                "success": False,
                "error": str(e)
            }

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
Task Agent 帮助
===============

能力:
1. 内容排版 - 使用 content-layout-leo-cskill
2. 新闻发布 - 使用 realestate-news-publisher-cskill
3. 营销文档生成 - 使用 project-marketing-doc-generator-cskill

激活关键词:
{', '.join(self.ACTIVATION_KEYWORDS)}

使用示例:
- agent.execute("帮我排版这篇文章", content="...", style="data_driven")
- agent.execute("发布房产资讯", title="...", content="...")
- agent.execute("生成营销文档", project_name="菜市场项目", project_type="农贸市场")
"""


# 注册到工厂
AgentFactory.register_agent_class("executor", TaskAgent)


# ==================== 使用示例 ====================

if __name__ == "__main__":
    # 创建配置
    config = AgentConfig(
        name="task-agent",
        type="executor",
        priority=1,
        skills=[
            "content-layout-leo-cskill",
            "realestate-news-publisher-cskill",
            "project-marketing-doc-generator-cskill"
        ],
        description="任务执行代理"
    )

    # 创建Agent
    agent = TaskAgent(config)

    # 测试能力判断
    print("能力判断测试:")
    print(f"- 排版任务: {agent.can_handle('帮我排版这篇文章')}")
    print(f"- 发布任务: {agent.can_handle('发布房产资讯')}")
    print(f"- 营销文档: {agent.can_handle('生成营销文档')}")

    # 获取帮助
    print(agent.get_help_text())

    # 获取状态
    print(f"\nAgent状态: {agent.get_status()}")
