"""
Creative Agent
==============
创作代理 - 负责内容创作、文案生成、创意输出

参考: claude-code-subagents/official/claude-agent-sdk-demos/research-agent/
      (Report Writer子代理)
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


class CreativeAgent(BaseAgent):
    """
    Creative Agent
    ==============
    创作代理，擅长：
    - 内容创作和文案生成
    - 营销文案撰写
    - 文章和报告撰写
    - 创意策划

    参考官方Report Writer子代理实现
    """

    # 激活关键词
    ACTIVATION_KEYWORDS = [
        "创作", "撰写", "生成", "编写",
        "文案", "内容", "文章", "报告"
    ]

    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.capabilities = {
            "content_creation": "content-layout-leo-cskill",
            "article_writing": "article-to-prototype-cskill",
            "marketing_copy": "project-marketing-doc-generator-cskill"
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

        if any(kw in task_lower for kw in ["创作", "撰写", "编写", "write", "create"]):
            capability_score += 0.4
        if any(kw in task_lower for kw in ["文案", "营销", "marketing", "copy"]):
            capability_score += 0.3
        if any(kw in task_lower for kw in ["文章", "报告", "article", "report"]):
            capability_score += 0.2
        if any(kw in task_lower for kw in ["内容", "content"]):
            capability_score += 0.1

        # 计算总分
        score = min(1.0, 0.3 + keyword_matches * 0.1 + capability_score)

        return score

    def execute(self, task: str, **kwargs) -> Dict[str, Any]:
        """
        执行创作任务

        Args:
            task: 任务描述
            **kwargs: 任务参数
                - content_type: 内容类型 (article, marketing, report)
                - style: 写作风格 (professional, casual, technical)
                - length: 内容长度 (short, medium, long)
                - topic: 主题
                - requirements: 特殊要求

        Returns:
            执行结果
        """
        # 1. 确定创作类型
        content_type = self._determine_content_type(task, **kwargs)

        # 2. 规划创作步骤
        steps = self._plan_creation(task, content_type, **kwargs)

        # 3. 执行创作步骤
        results = []
        for step in steps:
            step_result = self._execute_creation_step(step)
            results.append(step_result)

        # 4. 汇总和优化内容
        final_result = self._finalize_content(task, content_type, results, **kwargs)

        # 记录任务
        self.log_task(task, final_result)

        return final_result

    def _determine_content_type(self, task: str, **kwargs) -> str:
        """
        确定内容类型

        Args:
            task: 任务描述
            **kwargs: 任务参数

        Returns:
            内容类型
        """
        if "content_type" in kwargs:
            return kwargs["content_type"]

        task_lower = task.lower()

        if any(kw in task_lower for kw in ["营销", "推广", "marketing"]):
            return "marketing"
        elif any(kw in task_lower for kw in ["报告", "分析", "report"]):
            return "report"
        elif any(kw in task_lower for kw in ["文章", "博客", "article", "blog"]):
            return "article"
        else:
            return "general"

    def _plan_creation(self,
                      task: str,
                      content_type: str,
                      **kwargs) -> List[Dict[str, Any]]:
        """
        规划创作步骤

        Args:
            task: 任务描述
            content_type: 内容类型
            **kwargs: 任务参数

        Returns:
            创作步骤列表
        """
        steps = []

        if content_type == "marketing":
            # 营销文案创作
            steps.append({
                "step": 1,
                "name": "生成营销文档",
                "skill": "project-marketing-doc-generator-cskill",
                "action": "generate",
                "params": {
                    "project_name": kwargs.get("project_name", ""),
                    "project_type": kwargs.get("project_type", ""),
                    "features": kwargs.get("features", [])
                }
            })

        elif content_type == "article":
            # 文章创作
            steps.append({
                "step": 1,
                "name": "文章原型生成",
                "skill": "article-to-prototype-cskill",
                "action": "create",
                "params": {
                    "topic": kwargs.get("topic", task),
                    "style": kwargs.get("style", "professional")
                }
            })
            steps.append({
                "step": 2,
                "name": "内容排版",
                "skill": "content-layout-leo-cskill",
                "action": "layout",
                "params": {
                    "content": "",  # 将从上一步获取
                    "style": kwargs.get("style", "data_driven")
                }
            })

        elif content_type == "report":
            # 报告创作
            steps.append({
                "step": 1,
                "name": "报告内容生成",
                "skill": "content-layout-leo-cskill",
                "action": "layout",
                "params": {
                    "content": kwargs.get("content", ""),
                    "style": "professional"
                }
            })

        else:
            # 通用内容创作
            steps.append({
                "step": 1,
                "name": "内容生成",
                "skill": "content-layout-leo-cskill",
                "action": "layout",
                "params": {
                    "content": kwargs.get("content", task),
                    "style": kwargs.get("style", "data_driven")
                }
            })

        return steps

    def _execute_creation_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行单个创作步骤

        Args:
            step: 步骤定义

        Returns:
            步骤执行结果
        """
        skill_name = step["skill"]
        action = step["action"]
        params = step.get("params", {})

        try:
            # 调用相应的Skill
            result = self.use_skill(skill_name, action, **params)

            return {
                "step": step["step"],
                "name": step["name"],
                "success": True,
                "result": result
            }

        except Exception as e:
            return {
                "step": step["step"],
                "name": step["name"],
                "success": False,
                "error": str(e)
            }

    def _finalize_content(self,
                         task: str,
                         content_type: str,
                         results: List[Dict[str, Any]],
                         **kwargs) -> Dict[str, Any]:
        """
        汇总和优化内容

        Args:
            task: 任务描述
            content_type: 内容类型
            results: 创作结果列表
            **kwargs: 任务参数

        Returns:
            最终内容
        """
        successful_results = [r for r in results if r.get("success", False)]
        failed_results = [r for r in results if not r.get("success", False)]

        # 提取所有创作内容
        content_pieces = []
        for result in successful_results:
            content_pieces.append({
                "step_name": result["name"],
                "content": result.get("result", "")
            })

        # 生成最终内容
        final_content = self._merge_content(content_pieces)

        return {
            "task": task,
            "content_type": content_type,
            "total_steps": len(results),
            "successful_steps": len(successful_results),
            "failed_steps": len(failed_results),
            "final_content": final_content,
            "content_pieces": content_pieces,
            "errors": [r.get("error") for r in failed_results] if failed_results else []
        }

    def _merge_content(self, content_pieces: List[Dict[str, Any]]) -> str:
        """
        合并内容片段

        Args:
            content_pieces: 内容片段列表

        Returns:
            合并后的内容
        """
        if not content_pieces:
            return ""

        merged_parts = []
        for piece in content_pieces:
            merged_parts.append(f"## {piece['step_name']}\n")
            merged_parts.append(str(piece['content']))
            merged_parts.append("\n")

        return "\n".join(merged_parts)

    def get_capabilities(self) -> Dict[str, str]:
        """获取能力列表"""
        return self.capabilities

    def get_help_text(self) -> str:
        """获取帮助文本"""
        return f"""
Creative Agent 帮助
===================

能力:
1. 内容创作 - 使用 content-layout-leo-cskill
2. 文章撰写 - 使用 article-to-prototype-cskill
3. 营销文案 - 使用 project-marketing-doc-generator-cskill

激活关键词:
{', '.join(self.ACTIVATION_KEYWORDS)}

使用示例:
- agent.execute("创作一篇关于AI的文章", content_type="article", topic="人工智能")
- agent.execute("生成营销文案", content_type="marketing", project_name="智慧农贸")
- agent.execute("撰写分析报告", content_type="report", content="...")

参数说明:
- content_type: 内容类型
  - article: 文章
  - marketing: 营销文案
  - report: 报告
  - general: 通用内容
- style: 写作风格（professional, casual, technical）
- length: 内容长度（short, medium, long）
- topic: 主题
- requirements: 特殊要求
"""


# 注册到工厂
AgentFactory.register_agent_class("creator", CreativeAgent)


# ==================== 使用示例 ====================

if __name__ == "__main__":
    # 创建配置
    config = AgentConfig(
        name="creative-agent",
        type="creator",
        priority=4,
        skills=[
            "content-layout-leo-cskill",
            "article-to-prototype-cskill",
            "project-marketing-doc-generator-cskill"
        ],
        description="创作代理"
    )

    # 创建Agent
    agent = CreativeAgent(config)

    # 测试能力判断
    print("能力判断测试:")
    print(f"- 创作任务: {agent.can_handle('创作一篇文章')}")
    print(f"- 文案任务: {agent.can_handle('生成营销文案')}")
    print(f"- 报告任务: {agent.can_handle('撰写分析报告')}")

    # 获取帮助
    print(agent.get_help_text())

    # 获取状态
    print(f"\nAgent状态: {agent.get_status()}")
