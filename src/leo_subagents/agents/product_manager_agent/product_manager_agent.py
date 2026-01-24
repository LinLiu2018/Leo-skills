"""
Product Manager Agent
======================
产品经理代理 - 负责需求分析、PRD编写和用户故事设计

参考: AnalysisAgent 实现模式
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


class ProductManagerAgent(BaseAgent):
    """
    Product Manager Agent
    =====================
    产品经理代理，擅长：
    - 需求分析与梳理
    - PRD文档编写
    - 用户故事设计
    - 功能优先级排序
    - 竞品分析
    """

    # 激活关键词
    ACTIVATION_KEYWORDS = [
        "需求", "prd", "产品", "功能", "用户故事",
        "竞品", "分析", "优先级", "规划", "迭代"
    ]

    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.capabilities = {
            "market_research": "research_assistant_skill",
            "web_search": "web_search_skill"
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

        if any(kw in task_lower for kw in ["prd", "产品需求", "需求文档"]):
            capability_score += 0.4
        if any(kw in task_lower for kw in ["需求", "requirement", "功能"]):
            capability_score += 0.3
        if any(kw in task_lower for kw in ["用户故事", "user story", "story"]):
            capability_score += 0.2
        if any(kw in task_lower for kw in ["竞品", "competitor", "分析"]):
            capability_score += 0.2
        if any(kw in task_lower for kw in ["规划", "迭代", "版本"]):
            capability_score += 0.1

        # 计算总分
        score = min(1.0, 0.3 + keyword_matches * 0.1 + capability_score)

        return score

    def execute(self, task: str, **kwargs) -> Dict[str, Any]:
        """
        执行产品管理任务

        Args:
            task: 任务描述
            **kwargs: 任务参数
                - task_type: 任务类型 (prd, user_story, competitor_analysis, requirement)
                - output_format: 输出格式 (text, markdown, json)
                - project_name: 项目名称

        Returns:
            执行结果
        """
        # 1. 分析任务类型
        task_type = self._determine_task_type(task, **kwargs)

        # 从 kwargs 中移除 task_type 避免重复传递
        plan_kwargs = {k: v for k, v in kwargs.items() if k != 'task_type'}

        # 2. 规划执行步骤
        steps = self._plan_product_work(task, task_type, **plan_kwargs)

        # 3. 执行步骤
        results = []
        for step in steps:
            step_result = self._execute_product_step(step)
            results.append(step_result)

        # 4. 生成产品文档
        final_result = self._generate_product_document(task, task_type, results, **plan_kwargs)

        # 记录任务
        self.log_task(task, final_result)

        return final_result

    def _determine_task_type(self, task: str, **kwargs) -> str:
        """
        确定任务类型

        Args:
            task: 任务描述
            **kwargs: 任务参数

        Returns:
            任务类型
        """
        if "task_type" in kwargs:
            return kwargs["task_type"]

        task_lower = task.lower()

        if any(kw in task_lower for kw in ["prd", "产品需求文档", "需求文档"]):
            return "prd"
        elif any(kw in task_lower for kw in ["用户故事", "user story"]):
            return "user_story"
        elif any(kw in task_lower for kw in ["竞品", "competitor"]):
            return "competitor_analysis"
        elif any(kw in task_lower for kw in ["规划", "迭代", "版本"]):
            return "roadmap"
        else:
            return "requirement"

    def _plan_product_work(self,
                           task: str,
                           task_type: str,
                           **kwargs) -> List[Dict[str, Any]]:
        """
        规划产品工作步骤

        Args:
            task: 任务描述
            task_type: 任务类型
            **kwargs: 任务参数

        Returns:
            工作步骤列表
        """
        steps = []

        if task_type == "prd":
            # 动态加载 PRD 模板 (Modular Context)
            template_content = self.load_context("templates/prd_template.md")
            if template_content:
                print(f"📖 Context Loaded: templates/prd_template.md")
                kwargs['template_content'] = template_content
            
            # PRD编写
            steps.append({
                "step": 1,
                "name": "背景调研",
                "action": "research_background",
                "params": kwargs
            })
            steps.append({
                "step": 2,
                "name": "需求整理",
                "action": "organize_requirements",
                "params": kwargs
            })
            steps.append({
                "step": 3,
                "name": "功能设计",
                "action": "design_features",
                "params": kwargs
            })
            steps.append({
                "step": 4,
                "name": "文档生成",
                "action": "generate_prd",
                "params": kwargs
            })

        elif task_type == "user_story":
            # 用户故事
            steps.append({
                "step": 1,
                "name": "用户角色识别",
                "action": "identify_personas",
                "params": kwargs
            })
            steps.append({
                "step": 2,
                "name": "场景分析",
                "action": "analyze_scenarios",
                "params": kwargs
            })
            steps.append({
                "step": 3,
                "name": "故事编写",
                "action": "write_stories",
                "params": kwargs
            })
            steps.append({
                "step": 4,
                "name": "验收标准制定",
                "action": "define_acceptance_criteria",
                "params": kwargs
            })

        elif task_type == "competitor_analysis":
            # 竞品分析
            steps.append({
                "step": 1,
                "name": "竞品识别",
                "action": "identify_competitors",
                "params": kwargs
            })
            steps.append({
                "step": 2,
                "name": "功能对比",
                "action": "compare_features",
                "params": kwargs
            })
            steps.append({
                "step": 3,
                "name": "优劣势分析",
                "action": "swot_analysis",
                "params": kwargs
            })
            steps.append({
                "step": 4,
                "name": "报告生成",
                "action": "generate_report",
                "params": kwargs
            })

        elif task_type == "roadmap":
            # 产品规划
            steps.append({
                "step": 1,
                "name": "目标设定",
                "action": "set_goals",
                "params": kwargs
            })
            steps.append({
                "step": 2,
                "name": "功能排序",
                "action": "prioritize_features",
                "params": kwargs
            })
            steps.append({
                "step": 3,
                "name": "时间规划",
                "action": "plan_timeline",
                "params": kwargs
            })
            steps.append({
                "step": 4,
                "name": "路线图生成",
                "action": "generate_roadmap",
                "params": kwargs
            })

        else:
            # 需求分析
            steps.append({
                "step": 1,
                "name": "需求收集",
                "action": "collect_requirements",
                "params": kwargs
            })
            steps.append({
                "step": 2,
                "name": "需求分析",
                "action": "analyze_requirements",
                "params": kwargs
            })
            steps.append({
                "step": 3,
                "name": "需求确认",
                "action": "confirm_requirements",
                "params": kwargs
            })

        return steps

    def _execute_product_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行单个产品工作步骤

        Args:
            step: 步骤定义

        Returns:
            步骤执行结果
        """
        action = step["action"]
        params = step.get("params", {})

        try:
            # 映射 action 到 skill 方法
            action_mapping = {
                # Research Tasks -> research_assistant_skill
                "research_background": ("research_assistant_skill", "research", {}),
                "organize_requirements": ("research_assistant_skill", "organize", {}),
                "design_features": ("research_assistant_skill", "design", {}),
                "identify_personas": ("research_assistant_skill", "analyze", {}),
                "analyze_scenarios": ("research_assistant_skill", "analyze", {}),
                
                # Generation Tasks -> text_generator_skill (REAL GEN)
                "generate_prd": ("text_generator_skill", "generate", {"format": "prd"}),
                "write_stories": ("text_generator_skill", "generate", {"format": "user_story"}),
                "define_acceptance_criteria": ("text_generator_skill", "generate", {}),
                "generate_report": ("text_generator_skill", "generate", {}),
                "generate_roadmap": ("text_generator_skill", "generate", {"format": "roadmap"}),
                
                # Analysis Tasks -> research_assistant_skill
                "identify_competitors": ("web_search_skill", "search", {}),
                "compare_features": ("research_assistant_skill", "compare", {}),
                "swot_analysis": ("research_assistant_skill", "analyze", {"type": "swot"}),
                "set_goals": ("research_assistant_skill", "plan", {}),
                "prioritize_features": ("research_assistant_skill", "prioritize", {}),
                "plan_timeline": ("research_assistant_skill", "schedule", {}),
                "collect_requirements": ("research_assistant_skill", "collect", {}),
                "analyze_requirements": ("research_assistant_skill", "analyze", {}),
                "confirm_requirements": ("research_assistant_skill", "confirm", {}),
            }

            if action in action_mapping:
                skill_name, skill_action, extra_params = action_mapping[action]
                call_params = {**params, **extra_params}

                if self.has_skill(skill_name):
                    execution_result = self.use_skill(skill_name, skill_action, **call_params)
                    if hasattr(execution_result, 'result'):
                        result = execution_result.result if isinstance(execution_result.result, dict) else {"data": execution_result.result}
                        result["success"] = execution_result.success
                    else:
                        result = execution_result if isinstance(execution_result, dict) else {"data": execution_result, "success": True}
                else:
                    # 模拟执行
                    result = {"message": f"执行 {action}", "success": True, "simulated": True}
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

    def _generate_product_document(self,
                                   task: str,
                                   task_type: str,
                                   results: List[Dict[str, Any]],
                                   **kwargs) -> Dict[str, Any]:
        """
        生成产品文档

        Args:
            task: 任务描述
            task_type: 任务类型
            results: 工作结果列表
            **kwargs: 任务参数

        Returns:
            产品文档
        """
        successful_results = [r for r in results if r.get("success", False)]
        failed_results = [r for r in results if not r.get("success", False)]

        # 生成文档摘要
        summary = self._create_product_summary(task, task_type, successful_results)

        return {
            "task": task,
            "task_type": task_type,
            "total_steps": len(results),
            "successful_steps": len(successful_results),
            "failed_steps": len(failed_results),
            "summary": summary,
            "detailed_results": successful_results,
            "errors": [r.get("error") for r in failed_results] if failed_results else []
        }

    def _create_product_summary(self,
                               task: str,
                               task_type: str,
                               results: List[Dict[str, Any]]) -> str:
        """
        创建产品工作摘要

        Args:
            task: 任务描述
            task_type: 任务类型
            results: 结果列表

        Returns:
            摘要文本
        """
        type_names = {
            "prd": "PRD文档编写",
            "user_story": "用户故事设计",
            "competitor_analysis": "竞品分析",
            "roadmap": "产品规划",
            "requirement": "需求分析"
        }

        summary_parts = [
            f"产品任务: {task}",
            f"任务类型: {type_names.get(task_type, task_type)}",
            f"完成步骤: {len(results)}",
            "\n工作步骤:"
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
Product Manager Agent 帮助
===========================

能力:
1. PRD编写 - 产品需求文档、功能规格说明
2. 用户故事 - 场景分析、验收标准制定
3. 竞品分析 - 功能对比、SWOT分析
4. 产品规划 - 路线图、版本规划

激活关键词:
{', '.join(self.ACTIVATION_KEYWORDS)}

使用示例:
- agent.execute("编写用户管理模块PRD", task_type="prd")
- agent.execute("设计用户注册流程用户故事", task_type="user_story")
- agent.execute("分析竞品产品功能", task_type="competitor_analysis")

参数说明:
- task_type: 任务类型
  - prd: PRD文档编写
  - user_story: 用户故事设计
  - competitor_analysis: 竞品分析
  - roadmap: 产品规划
  - requirement: 需求分析
- output_format: 输出格式（默认markdown）
- project_name: 项目名称（可选）
"""


# 注册到工厂
AgentFactory.register_agent_class("product_manager", ProductManagerAgent)


# ==================== 使用示例 ====================

if __name__ == "__main__":
    # 创建配置
    config = AgentConfig(
        name="product-manager-agent",
        type="product_manager",
        priority=1,
        skills=["research_assistant_skill", "web_search_skill"],
        description="产品经理代理"
    )

    # 创建Agent
    agent = ProductManagerAgent(config)

    # 测试能力判断
    print("能力判断测试:")
    print(f"- PRD编写: {agent.can_handle('编写用户管理模块PRD')}")
    print(f"- 用户故事: {agent.can_handle('设计用户注册流程用户故事')}")
    print(f"- 竞品分析: {agent.can_handle('分析竞品产品功能')}")

    # 获取帮助
    print(agent.get_help_text())

    # 获取状态
    print(f"\nAgent状态: {agent.get_status()}")
