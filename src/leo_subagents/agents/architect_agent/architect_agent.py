"""
Architect Agent
================
架构师代理 - 负责技术选型、系统设计和数据库设计

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


class ArchitectAgent(BaseAgent):
    """
    Architect Agent
    ===============
    架构师代理，擅长：
    - 技术选型与评估
    - 系统架构设计
    - 数据库模型设计
    - API接口设计
    - 技术文档编写
    """

    # 激活关键词
    ACTIVATION_KEYWORDS = [
        "架构", "设计", "技术选型", "数据库",
        "API", "接口", "系统", "模型", "ER图"
    ]

    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.capabilities = {
            "database_design": "database-model-generator-cskill",
            "api_design": "api-doc-generator-cskill",
            "tech_research": "research-assistant-cskill"
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

        if any(kw in task_lower for kw in ["架构", "architecture", "系统设计"]):
            capability_score += 0.4
        if any(kw in task_lower for kw in ["数据库", "database", "模型", "model"]):
            capability_score += 0.3
        if any(kw in task_lower for kw in ["api", "接口", "interface"]):
            capability_score += 0.2
        if any(kw in task_lower for kw in ["技术选型", "选型", "评估"]):
            capability_score += 0.1

        # 计算总分
        score = min(1.0, 0.3 + keyword_matches * 0.1 + capability_score)

        return score

    def execute(self, task: str, **kwargs) -> Dict[str, Any]:
        """
        执行架构设计任务

        Args:
            task: 任务描述
            **kwargs: 任务参数
                - design_type: 设计类型 (database, api, system, tech_selection)
                - output_format: 输出格式 (text, json, markdown, mermaid)

        Returns:
            执行结果
        """
        # 1. 分析设计类型
        design_type = self._determine_design_type(task, **kwargs)

        # 从 kwargs 中移除 design_type 避免重复传递
        plan_kwargs = {k: v for k, v in kwargs.items() if k != 'design_type'}

        # 2. 规划设计步骤
        steps = self._plan_design(task, design_type, **plan_kwargs)

        # 3. 执行设计步骤
        results = []
        for step in steps:
            step_result = self._execute_design_step(step)
            results.append(step_result)

        # 4. 生成设计文档
        final_result = self._generate_design_document(task, design_type, results, **plan_kwargs)

        # 记录任务
        self.log_task(task, final_result)

        return final_result

    def _determine_design_type(self, task: str, **kwargs) -> str:
        """
        确定设计类型

        Args:
            task: 任务描述
            **kwargs: 任务参数

        Returns:
            设计类型
        """
        if "design_type" in kwargs:
            return kwargs["design_type"]

        task_lower = task.lower()

        if any(kw in task_lower for kw in ["数据库", "database", "表", "er图"]):
            return "database"
        elif any(kw in task_lower for kw in ["api", "接口", "restful"]):
            return "api"
        elif any(kw in task_lower for kw in ["技术选型", "选型", "框架"]):
            return "tech_selection"
        else:
            return "system"

    def _plan_design(self,
                     task: str,
                     design_type: str,
                     **kwargs) -> List[Dict[str, Any]]:
        """
        规划设计步骤

        Args:
            task: 任务描述
            design_type: 设计类型
            **kwargs: 任务参数

        Returns:
            设计步骤列表
        """
        steps = []

        if design_type == "database":
            # 数据库设计
            steps.append({
                "step": 1,
                "name": "需求分析",
                "action": "analyze_requirements",
                "params": kwargs
            })
            steps.append({
                "step": 2,
                "name": "实体识别",
                "action": "identify_entities",
                "params": kwargs
            })
            steps.append({
                "step": 3,
                "name": "关系建模",
                "action": "model_relationships",
                "params": kwargs
            })
            steps.append({
                "step": 4,
                "name": "生成ER图",
                "action": "generate_er_diagram",
                "params": kwargs
            })

        elif design_type == "api":
            # API设计
            steps.append({
                "step": 1,
                "name": "资源识别",
                "action": "identify_resources",
                "params": kwargs
            })
            steps.append({
                "step": 2,
                "name": "端点设计",
                "action": "design_endpoints",
                "params": kwargs
            })
            steps.append({
                "step": 3,
                "name": "生成API文档",
                "action": "generate_api_doc",
                "params": kwargs
            })

        elif design_type == "tech_selection":
            # 技术选型
            steps.append({
                "step": 1,
                "name": "需求分析",
                "action": "analyze_requirements",
                "params": kwargs
            })
            steps.append({
                "step": 2,
                "name": "技术调研",
                "action": "research_technologies",
                "params": kwargs
            })
            steps.append({
                "step": 3,
                "name": "对比评估",
                "action": "compare_options",
                "params": kwargs
            })
            steps.append({
                "step": 4,
                "name": "生成报告",
                "action": "generate_report",
                "params": kwargs
            })

        else:
            # 系统架构设计
            steps.append({
                "step": 1,
                "name": "需求分析",
                "action": "analyze_requirements",
                "params": kwargs
            })
            steps.append({
                "step": 2,
                "name": "架构设计",
                "action": "design_architecture",
                "params": kwargs
            })
            steps.append({
                "step": 3,
                "name": "组件拆分",
                "action": "decompose_components",
                "params": kwargs
            })
            steps.append({
                "step": 4,
                "name": "生成架构图",
                "action": "generate_diagram",
                "params": kwargs
            })

        return steps

    def _execute_design_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行单个设计步骤

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
                "analyze_requirements": ("research-assistant-cskill", "research", {}),
                "identify_entities": ("database-model-generator-cskill", "analyze", {}),
                "model_relationships": ("database-model-generator-cskill", "model", {}),
                "generate_er_diagram": ("database-model-generator-cskill", "generate", {"format": "mermaid"}),
                "identify_resources": ("api-doc-generator-cskill", "analyze", {}),
                "design_endpoints": ("api-doc-generator-cskill", "design", {}),
                "generate_api_doc": ("api-doc-generator-cskill", "generate", {"format": "openapi"}),
                "research_technologies": ("research-assistant-cskill", "research", {}),
                "compare_options": ("research-assistant-cskill", "compare", {}),
                "generate_report": ("research-assistant-cskill", "report", {}),
                "design_architecture": ("research-assistant-cskill", "design", {}),
                "decompose_components": ("research-assistant-cskill", "decompose", {}),
                "generate_diagram": ("research-assistant-cskill", "diagram", {"format": "mermaid"}),
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

    def _generate_design_document(self,
                                  task: str,
                                  design_type: str,
                                  results: List[Dict[str, Any]],
                                  **kwargs) -> Dict[str, Any]:
        """
        生成设计文档

        Args:
            task: 任务描述
            design_type: 设计类型
            results: 设计结果列表
            **kwargs: 任务参数

        Returns:
            设计文档
        """
        successful_results = [r for r in results if r.get("success", False)]
        failed_results = [r for r in results if not r.get("success", False)]

        # 生成文档摘要
        summary = self._create_design_summary(task, design_type, successful_results)

        return {
            "task": task,
            "design_type": design_type,
            "total_steps": len(results),
            "successful_steps": len(successful_results),
            "failed_steps": len(failed_results),
            "summary": summary,
            "detailed_results": successful_results,
            "errors": [r.get("error") for r in failed_results] if failed_results else []
        }

    def _create_design_summary(self,
                              task: str,
                              design_type: str,
                              results: List[Dict[str, Any]]) -> str:
        """
        创建设计摘要

        Args:
            task: 任务描述
            design_type: 设计类型
            results: 结果列表

        Returns:
            摘要文本
        """
        type_names = {
            "database": "数据库设计",
            "api": "API设计",
            "tech_selection": "技术选型",
            "system": "系统架构设计"
        }

        summary_parts = [
            f"设计任务: {task}",
            f"设计类型: {type_names.get(design_type, design_type)}",
            f"完成步骤: {len(results)}",
            "\n设计步骤:"
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
Architect Agent 帮助
====================

能力:
1. 数据库设计 - 实体建模、关系设计、ER图生成
2. API设计 - RESTful接口设计、OpenAPI文档生成
3. 系统架构 - 组件拆分、架构图生成
4. 技术选型 - 技术调研、方案对比

激活关键词:
{', '.join(self.ACTIVATION_KEYWORDS)}

使用示例:
- agent.execute("设计用户管理系统数据库", design_type="database")
- agent.execute("设计订单API接口", design_type="api")
- agent.execute("后端框架技术选型", design_type="tech_selection")

参数说明:
- design_type: 设计类型
  - database: 数据库设计
  - api: API设计
  - system: 系统架构设计
  - tech_selection: 技术选型
- output_format: 输出格式（默认markdown）
"""


# 注册到工厂
AgentFactory.register_agent_class("architect", ArchitectAgent)


# ==================== 使用示例 ====================

if __name__ == "__main__":
    # 创建配置
    config = AgentConfig(
        name="architect-agent",
        type="architect",
        priority=2,
        skills=["database-model-generator-cskill", "api-doc-generator-cskill", "research-assistant-cskill"],
        description="架构师代理"
    )

    # 创建Agent
    agent = ArchitectAgent(config)

    # 测试能力判断
    print("能力判断测试:")
    print(f"- 数据库设计: {agent.can_handle('设计用户管理系统数据库')}")
    print(f"- API设计: {agent.can_handle('设计订单API接口')}")
    print(f"- 技术选型: {agent.can_handle('后端框架技术选型')}")

    # 获取帮助
    print(agent.get_help_text())

    # 获取状态
    print(f"\nAgent状态: {agent.get_status()}")
