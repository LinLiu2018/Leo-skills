"""
元技能管理器
============
封装元技能 (Meta-Skills) 的管理和调用逻辑
专门处理：创建技能、进化技能、优化提示词等自我进化能力
"""

from pathlib import Path
from typing import Any, Dict, List, Optional


class MetaSkillsManager:
    """
    元技能管理器
    ===========
    系统的自我进化引擎
    """

    META_SKILLS = {
        "creator": "agent_skill_creator_skill",
        "evolver": "skill_evolution_assistant_skill",
        "optimizer": "claude-prompt-engineering-skills",
    }

    def __init__(self, system_instance=None):
        """
        初始化管理器

        Args:
            system_instance: LeoSystem 实例（可选，如果未提供则自动获取）
        """
        self.system = system_instance
        if not self.system:
            # 延迟导入以避免循环依赖
            import sys

            project_root = Path(__file__).parent.parent.parent
            sys.path.insert(0, str(project_root))
            import leo_system

            self.system = leo_system.get_system()

    def create_skill(
        self, name: str, description: str, domain: str, requirements: str, interactive: bool = False
    ) -> Dict[str, Any]:
        """
        创建新技能 (Meta-Skill: agent_skill_creator_skill)

        Args:
            name: 技能名称
            description: 技能描述
            domain: 领域 (e.g. backend, frontend)
            requirements: 详细需求
            interactive: 是否交互式创建

        Returns:
            创建结果
        """
        skill_name = self.META_SKILLS["creator"]

        # 构造创建指令
        prompt = f"""
        Create a new specialized agent skill for {domain}.
        Name: {name}
        Description: {description}
        Requirements:
        {requirements}
        """

        print(f"🧬 调用元技能 [{skill_name}] 创建新技能: {name}")

        try:
            # 调用 agent_skill_creator_skill
            # 注意：实际调用可能需要根据该 Skill 的具体接口调整
            result = self.system.call_skill(
                skill_name, "create_agent", prompt=prompt, interactive=interactive
            )
            return {"success": True, "data": result, "message": f"技能 {name} 创建成功"}
        except Exception as e:
            return {"success": False, "error": str(e), "message": f"创建技能失败: {e}"}

    def evolve_skill(
        self, target_skill: str, feedback: str, optimization_goals: List[str]
    ) -> Dict[str, Any]:
        """
        进化现有技能 (Meta-Skill: skill-evolution-assistant)

        Args:
            target_skill: 目标技能名称
            feedback: 用户反馈或改进建议
            optimization_goals: 优化目标列表

        Returns:
            进化结果
        """
        skill_name = self.META_SKILLS["evolver"]

        print(f"🧬 调用元技能 [{skill_name}] 进化技能: {target_skill}")

        try:
            result = self.system.call_skill(
                skill_name,
                "evolve",
                target_skill=target_skill,
                feedback=feedback,
                goals=optimization_goals,
            )
            return {"success": True, "data": result, "message": f"技能 {target_skill} 进化成功"}
        except Exception as e:
            return {"success": False, "error": str(e), "message": f"进化技能失败: {e}"}

    def optimize_prompt(self, original_prompt: str, goal: str = "clarity") -> Dict[str, Any]:
        """
        优化提示词 (Meta-Skill: claude-prompt-engineering)

        Args:
            original_prompt: 原始提示词
            goal: 优化目标 (clarity, robustness, creativity)

        Returns:
            优化后的提示词
        """
        skill_name = self.META_SKILLS["optimizer"]

        print(f"🧬 调用元技能 [{skill_name}] 优化提示词")

        try:
            result = self.system.call_skill(
                skill_name, "optimize", prompt=original_prompt, goal=goal
            )
            return {
                "success": True,
                "optimized_prompt": result.get("optimized_prompt", original_prompt),
                "explanation": result.get("explanation", ""),
            }
        except Exception as e:
            return {"success": False, "error": str(e), "optimized_prompt": original_prompt}


# ==================== 全局实例 ====================

_meta_manager: Optional[MetaSkillsManager] = None


def get_meta_manager() -> MetaSkillsManager:
    """获取全局元技能管理器"""
    global _meta_manager
    if _meta_manager is None:
        _meta_manager = MetaSkillsManager()
    return _meta_manager
