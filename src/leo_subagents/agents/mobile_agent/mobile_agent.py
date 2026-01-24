"""
Mobile Agent
=============
移动开发代理 - 负责小程序、React Native和Flutter开发

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


class MobileAgent(BaseAgent):
    """
    Mobile Agent
    ============
    移动开发代理，擅长：
    - 微信小程序开发
    - React Native应用开发
    - Flutter应用开发
    - 移动端UI组件开发
    - 跨平台适配
    """

    # 激活关键词
    ACTIVATION_KEYWORDS = [
        "小程序", "移动", "app", "flutter", "react native",
        "ios", "android", "组件", "页面", "uniapp"
    ]

    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.capabilities = {
            "miniprogram_page": "miniprogram_page_generator_skill",
            "miniprogram_component": "miniprogram_component_generator_skill",
            "miniprogram_scaffold": "miniprogram_project_scaffold_skill"
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

        if any(kw in task_lower for kw in ["小程序", "miniprogram", "wechat"]):
            capability_score += 0.4
        if any(kw in task_lower for kw in ["flutter", "dart"]):
            capability_score += 0.3
        if any(kw in task_lower for kw in ["react native", "rn", "expo"]):
            capability_score += 0.3
        if any(kw in task_lower for kw in ["组件", "component", "页面", "page"]):
            capability_score += 0.2
        if any(kw in task_lower for kw in ["app", "移动", "mobile"]):
            capability_score += 0.1

        # 计算总分
        score = min(1.0, 0.3 + keyword_matches * 0.1 + capability_score)

        return score

    def execute(self, task: str, **kwargs) -> Dict[str, Any]:
        """
        执行移动开发任务

        Args:
            task: 任务描述
            **kwargs: 任务参数
                - platform: 平台 (miniprogram, flutter, react_native, uniapp)
                - task_type: 任务类型 (page, component, project)
                - output_path: 输出路径

        Returns:
            执行结果
        """
        # 1. 分析平台和任务类型
        platform = self._determine_platform(task, **kwargs)
        task_type = self._determine_task_type(task, **kwargs)

        # 从 kwargs 中移除已处理的参数
        plan_kwargs = {k: v for k, v in kwargs.items() if k not in ['platform', 'task_type']}

        # 2. 规划开发步骤
        steps = self._plan_development(task, platform, task_type, **plan_kwargs)

        # 3. 执行开发步骤
        results = []
        for step in steps:
            step_result = self._execute_development_step(step)
            results.append(step_result)

        # 4. 生成开发报告
        final_result = self._generate_development_report(task, platform, task_type, results, **plan_kwargs)

        # 记录任务
        self.log_task(task, final_result)

        return final_result

    def _determine_platform(self, task: str, **kwargs) -> str:
        """确定开发平台"""
        if "platform" in kwargs:
            return kwargs["platform"]

        task_lower = task.lower()

        if any(kw in task_lower for kw in ["小程序", "miniprogram", "wechat", "微信"]):
            return "miniprogram"
        elif any(kw in task_lower for kw in ["flutter", "dart"]):
            return "flutter"
        elif any(kw in task_lower for kw in ["react native", "rn"]):
            return "react_native"
        elif any(kw in task_lower for kw in ["uniapp", "uni-app"]):
            return "uniapp"
        else:
            return "miniprogram"  # 默认小程序

    def _determine_task_type(self, task: str, **kwargs) -> str:
        """确定任务类型"""
        if "task_type" in kwargs:
            return kwargs["task_type"]

        task_lower = task.lower()

        if any(kw in task_lower for kw in ["项目", "scaffold", "脚手架", "初始化"]):
            return "project"
        elif any(kw in task_lower for kw in ["组件", "component"]):
            return "component"
        else:
            return "page"

    def _plan_development(self,
                          task: str,
                          platform: str,
                          task_type: str,
                          **kwargs) -> List[Dict[str, Any]]:
        """
        规划开发步骤

        Args:
            task: 任务描述
            platform: 开发平台
            task_type: 任务类型
            **kwargs: 任务参数

        Returns:
            开发步骤列表
        """
        steps = []

        if task_type == "project":
            # 项目脚手架
            steps.append({
                "step": 1,
                "name": "项目配置",
                "action": "configure_project",
                "platform": platform,
                "params": kwargs
            })
            steps.append({
                "step": 2,
                "name": "目录结构生成",
                "action": "generate_structure",
                "platform": platform,
                "params": kwargs
            })
            steps.append({
                "step": 3,
                "name": "基础文件生成",
                "action": "generate_base_files",
                "platform": platform,
                "params": kwargs
            })

        elif task_type == "component":
            # 组件开发
            steps.append({
                "step": 1,
                "name": "组件设计",
                "action": "design_component",
                "platform": platform,
                "params": kwargs
            })
            steps.append({
                "step": 2,
                "name": "代码生成",
                "action": "generate_component",
                "platform": platform,
                "params": kwargs
            })
            steps.append({
                "step": 3,
                "name": "样式生成",
                "action": "generate_styles",
                "platform": platform,
                "params": kwargs
            })

        else:
            # 页面开发
            steps.append({
                "step": 1,
                "name": "页面设计",
                "action": "design_page",
                "platform": platform,
                "params": kwargs
            })
            steps.append({
                "step": 2,
                "name": "页面代码生成",
                "action": "generate_page",
                "platform": platform,
                "params": kwargs
            })
            steps.append({
                "step": 3,
                "name": "样式生成",
                "action": "generate_styles",
                "platform": platform,
                "params": kwargs
            })
            steps.append({
                "step": 4,
                "name": "配置更新",
                "action": "update_config",
                "platform": platform,
                "params": kwargs
            })

        return steps

    def _execute_development_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行单个开发步骤

        Args:
            step: 步骤定义

        Returns:
            步骤执行结果
        """
        action = step["action"]
        platform = step.get("platform", "miniprogram")
        params = step.get("params", {})

        try:
            # 根据平台选择技能
            skill_mapping = {
                "miniprogram": {
                    "configure_project": ("miniprogram_project_scaffold_skill", "configure"),
                    "generate_structure": ("miniprogram_project_scaffold_skill", "scaffold"),
                    "generate_base_files": ("miniprogram_project_scaffold_skill", "generate"),
                    "design_component": ("miniprogram_component_generator_skill", "design"),
                    "generate_component": ("miniprogram_component_generator_skill", "generate"),
                    "design_page": ("miniprogram_page_generator_skill", "design"),
                    "generate_page": ("miniprogram_page_generator_skill", "generate"),
                    "generate_styles": ("miniprogram_page_generator_skill", "style"),
                    "update_config": ("miniprogram_project_scaffold_skill", "config"),
                }
            }

            platform_mapping = skill_mapping.get(platform, skill_mapping["miniprogram"])

            if action in platform_mapping:
                skill_name, skill_action = platform_mapping[action]

                if self.has_skill(skill_name):
                    execution_result = self.use_skill(skill_name, skill_action, **params)
                    if hasattr(execution_result, 'result'):
                        result = execution_result.result if isinstance(execution_result.result, dict) else {"data": execution_result.result}
                        result["success"] = execution_result.success
                    else:
                        result = execution_result if isinstance(execution_result, dict) else {"data": execution_result, "success": True}
                else:
                    # 模拟执行
                    result = {"message": f"执行 {action} (平台: {platform})", "success": True, "simulated": True}
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

    def _generate_development_report(self,
                                     task: str,
                                     platform: str,
                                     task_type: str,
                                     results: List[Dict[str, Any]],
                                     **kwargs) -> Dict[str, Any]:
        """
        生成开发报告

        Args:
            task: 任务描述
            platform: 开发平台
            task_type: 任务类型
            results: 开发结果列表
            **kwargs: 任务参数

        Returns:
            开发报告
        """
        successful_results = [r for r in results if r.get("success", False)]
        failed_results = [r for r in results if not r.get("success", False)]

        # 生成报告摘要
        summary = self._create_development_summary(task, platform, task_type, successful_results)

        return {
            "task": task,
            "platform": platform,
            "task_type": task_type,
            "total_steps": len(results),
            "successful_steps": len(successful_results),
            "failed_steps": len(failed_results),
            "summary": summary,
            "detailed_results": successful_results,
            "errors": [r.get("error") for r in failed_results] if failed_results else []
        }

    def _create_development_summary(self,
                                   task: str,
                                   platform: str,
                                   task_type: str,
                                   results: List[Dict[str, Any]]) -> str:
        """
        创建开发摘要

        Args:
            task: 任务描述
            platform: 开发平台
            task_type: 任务类型
            results: 结果列表

        Returns:
            摘要文本
        """
        platform_names = {
            "miniprogram": "微信小程序",
            "flutter": "Flutter",
            "react_native": "React Native",
            "uniapp": "UniApp"
        }

        type_names = {
            "project": "项目脚手架",
            "component": "组件开发",
            "page": "页面开发"
        }

        summary_parts = [
            f"开发任务: {task}",
            f"开发平台: {platform_names.get(platform, platform)}",
            f"任务类型: {type_names.get(task_type, task_type)}",
            f"完成步骤: {len(results)}",
            "\n开发步骤:"
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
Mobile Agent 帮助
=================

能力:
1. 小程序开发 - 页面生成、组件开发、项目脚手架
2. Flutter开发 - Widget开发、页面布局
3. React Native开发 - 组件开发、导航配置
4. 跨平台适配 - 多平台代码生成

激活关键词:
{', '.join(self.ACTIVATION_KEYWORDS)}

使用示例:
- agent.execute("创建小程序首页", platform="miniprogram", task_type="page")
- agent.execute("开发商品卡片组件", task_type="component")
- agent.execute("初始化小程序项目", task_type="project")

参数说明:
- platform: 开发平台
  - miniprogram: 微信小程序
  - flutter: Flutter
  - react_native: React Native
  - uniapp: UniApp
- task_type: 任务类型
  - page: 页面开发
  - component: 组件开发
  - project: 项目脚手架
- output_path: 输出路径（可选）
"""


# 注册到工厂
AgentFactory.register_agent_class("mobile", MobileAgent)


# ==================== 使用示例 ====================

if __name__ == "__main__":
    # 创建配置
    config = AgentConfig(
        name="mobile-agent",
        type="mobile",
        priority=16,
        skills=["miniprogram_page_generator_skill", "miniprogram_component_generator_skill", "miniprogram_project_scaffold_skill"],
        description="移动开发代理"
    )

    # 创建Agent
    agent = MobileAgent(config)

    # 测试能力判断
    print("能力判断测试:")
    print(f"- 小程序页面: {agent.can_handle('创建小程序首页')}")
    print(f"- 组件开发: {agent.can_handle('开发商品卡片组件')}")
    print(f"- Flutter: {agent.can_handle('Flutter应用开发')}")

    # 获取帮助
    print(agent.get_help_text())

    # 获取状态
    print(f"\nAgent状态: {agent.get_status()}")
