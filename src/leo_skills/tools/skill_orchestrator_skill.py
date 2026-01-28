"""
技能协作编排器 (Skill Orchestrator)

协调 github_to_skills、skill_manager、skill_evolution_manager 三个技能协同工作。

工作流：
1. github_to_skills → 创建新技能
2. skill_manager → 维护和审计
3. skill_evolution_manager → 持续改进

使用示例：
    from skill_orchestrator import SkillOrchestrator

    orchestrator = SkillOrchestrator()

    # 一键创建并初始化技能
    result = orchestrator.create_and_init(
        repo_url="https://github.com/owner/repo",
        category="development"
    )

    # 完整工作流：创建 → 审计 → 优化
    result = orchestrator.full_workflow(
        repo_url="https://github.com/owner/repo"
    )
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from leo_skills.core.evolution import EvolvableSkill


class SkillOrchestrator(EvolvableSkill):
    """
    技能协作编排器

    协调三个 Khazix-Skills 技能协同工作。
    """

    def __init__(self, skill_name: str = "skill_orchestrator"):
        super().__init__(skill_name, Path(__file__).parent / "evolution.json")

    def execute(self, action: str = "full_workflow", **kwargs) -> Dict[str, Any]:
        """
        执行编排操作

        Args:
            action: 操作类型
                - full_workflow: 完整工作流（创建→审计→优化）
                - create_and_init: 创建并初始化
                - audit_and_report: 审计并报告
                - batch_optimize: 批量优化
                - analyze_system: 分析系统
            repo_url: 仓库URL
            category: 分类
        """
        actions = {
            "full_workflow": self._full_workflow,
            "create_and_init": self._create_and_init,
            "audit_and_report": self._audit_and_report,
            "batch_optimize": self._batch_optimize,
            "analyze_system": self._analyze_system,
        }

        if action not in actions:
            return {"success": False, "error": f"Unknown action: {action}"}

        return actions[action](**kwargs)

    def _full_workflow(self, repo_url: str, **kwargs) -> Dict[str, Any]:
        """
        完整工作流：创建 → 审计 → 优化
        """
        from leo_skills.tools.github_to_skills_skill import GitHubToSkillsSkill
        from leo_skills.tools.skill_manager_skill import SkillManagerSkill
        from leo_skills.tools.skill_evolution_manager_skill import SkillEvolutionManagerSkill

        results = {}

        # Step 1: 创建技能
        print("[1/3] Converting GitHub repo to skill...")
        github_skill = GitHubToSkillsSkill()
        create_result = github_skill.execute(
            action="convert",
            repo_url=repo_url
        )
        results["create"] = create_result

        if not create_result.get("success"):
            return {
                "success": False,
                "error": "Failed to create skill",
                "step": "create",
                "details": create_result
            }

        skill_name = create_result.get("skill_name")

        # Step 2: 审计技能
        print("[2/3] Auditing new skill...")
        manager_skill = SkillManagerSkill()
        audit_result = manager_skill.execute(action="audit")
        results["audit"] = audit_result

        # Step 3: 优化技能
        print("[3/3] Initializing evolution for skill...")
        evolution_skill = SkillEvolutionManagerSkill()
        evolution_result = evolution_skill.execute(
            action="evolve_from_feedback",
            skill_name=skill_name,
            feedback="Initial setup from github-to-skills conversion"
        )
        results["evolution"] = evolution_result

        self.learn(f"Full workflow completed for {skill_name}")

        return {
            "success": True,
            "skill_name": skill_name,
            "workflow": "create → audit → evolve",
            "results": results
        }

    def _create_and_init(self, repo_url: str, category: str = "tools", **kwargs) -> Dict[str, Any]:
        """创建并初始化技能"""
        from leo_skills.tools.github_to_skills_skill import GitHubToSkillsSkill

        github_skill = GitHubToSkillsSkill()

        result = github_skill.execute(
            action="convert",
            repo_url=repo_url,
            output_dir=f"src/leo_skills/{category}"
        )

        if result.get("success"):
            self.learn(f"Created and initialized skill: {result.get('skill_name')}")

        return result

    def _audit_and_report(self, **kwargs) -> Dict[str, Any]:
        """审计并生成报告"""
        from leo_skills.tools.skill_manager_skill import SkillManagerSkill

        manager_skill = SkillManagerSkill()

        # 执行审计
        audit_result = manager_skill.execute(action="audit")

        # 生成报告
        report_result = manager_skill.execute(action="report")

        return {
            "success": True,
            "audit": audit_result,
            "report": report_result
        }

    def _batch_optimize(self, **kwargs) -> Dict[str, Any]:
        """批量优化"""
        from leo_skills.tools.skill_evolution_manager_skill import SkillEvolutionManagerSkill

        evolution_skill = SkillEvolutionManagerSkill()

        # 分析进化模式
        patterns = evolution_skill.execute(action="analyze_patterns")

        # 批量进化
        batch_result = evolution_skill.execute(action="batch_evolve")

        return {
            "success": True,
            "patterns": patterns,
            "batch": batch_result
        }

    def _analyze_system(self, **kwargs) -> Dict[str, Any]:
        """分析整个技能系统"""
        from leo_skills.tools.skill_manager_skill import SkillManagerSkill
        from leo_skills.tools.skill_evolution_manager_skill import SkillEvolutionManagerSkill

        manager_skill = SkillManagerSkill()
        evolution_skill = SkillEvolutionManagerSkill()

        # 获取技能列表
        skills = manager_skill.execute(action="list")

        # 分析进化模式
        patterns = evolution_skill.execute(action="analyze_patterns")

        return {
            "success": True,
            "skills": skills,
            "evolution_patterns": patterns
        }


# 便捷函数
def create_skill_from_github(repo_url: str, category: str = "tools") -> Dict[str, Any]:
    """从GitHub仓库创建技能"""
    orchestrator = SkillOrchestrator()
    return orchestrator.execute(
        action="create_and_init",
        repo_url=repo_url,
        category=category
    )


def run_full_workflow(repo_url: str) -> Dict[str, Any]:
    """运行完整工作流"""
    orchestrator = SkillOrchestrator()
    return orchestrator.execute(
        action="full_workflow",
        repo_url=repo_url
    )


def audit_all_skills() -> Dict[str, Any]:
    """审计所有技能"""
    orchestrator = SkillOrchestrator()
    return orchestrator.execute(action="audit_and_report")


if __name__ == "__main__":
    # 示例用法
    orchestrator = SkillOrchestrator()

    # 查看系统状态
    result = orchestrator.execute(action="analyze_system")
    print(f"Total skills: {result.get('skills', {}).get('total', 0)}")
