"""
Leo统一API
===================
提供简洁的API接口来注册和使用Skills与Subagents

设计理念：
- 极简API，3行代码完成注册
- 自动发现，无需手动配置
- 统一调用，一个接口处理所有
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
from .registry import UnifiedRegistry, get_registry, SkillRegistration, AgentRegistration


class LeoAPI:
    """
    Leo统一API
    ==========
    提供简单易用的接口来管理Skills和Subagents
    """

    def __init__(self, base_path: str = None):
        """
        初始化API

        Args:
            base_path: 项目根路径，默认为当前目录
        """
        if base_path is None:
            base_path = Path(__file__).parent.parent

        self.base_path = Path(base_path)
        self.registry = get_registry()

        # 自动发现和注册
        self._auto_init()

    # ==================== 极简注册API ====================

    def register(self, what: str, name: str, **kwargs) -> bool:
        """
        通用注册接口 - 一个方法注册所有类型

        Args:
            what: 类型 ("skill" 或 "agent")
            name: 名称
            **kwargs: 其他参数

        Returns:
            bool: 是否注册成功

        Examples:
            # 注册Skill
            api.register("skill", "my-skill",
                        path="leo_skills/content-creation/my-skill",
                        category="content-creation")

            # 注册Agent
            api.register("agent", "my-agent",
                        type="executor",
                        priority=1)
        """
        if what.lower() == "skill":
            return self.registry.register_skill(name=name, **kwargs)
        elif what.lower() == "agent":
            return self.registry.register_agent(name=name, **kwargs)
        else:
            print(f"❌ 未知类型: {what}，必须是 'skill' 或 'agent'")
            return False

    # ==================== 自动发现 ====================

    def auto_discover(self) -> int:
        """
        自动发现所有Skills并注册

        Returns:
            int: 发现并注册的Skill数量
        """
        skills_path = self.base_path / "leo_skills"
        return self.registry.auto_discover_skills(str(skills_path))

    def _auto_init(self):
        """初始化时自动发现"""
        self.auto_discover()

    # ==================== 查询API ====================

    def list(self, what: str, **filters) -> List:
        """
        通用查询接口

        Args:
            what: 类型 ("skills" 或 "agents")
            **filters: 筛选条件

        Returns:
            List: 注册对象列表

        Examples:
            # 列出所有Skills
            api.list("skills")

            # 列出content-creation分类的Skills
            api.list("skills", category="content-creation")

            # 列出所有Agents
            api.list("agents")
        """
        if what.lower() == "skills":
            return self.registry.list_skills(**filters)
        elif what.lower() == "agents":
            return self.registry.list_agents(**filters)
        else:
            return []

    def get(self, what: str, name: str) -> Optional[Any]:
        """
        获取单个注册对象

        Args:
            what: 类型 ("skill" 或 "agent")
            name: 名称

        Returns:
            注册对象或None
        """
        if what.lower() == "skill":
            return self.registry.get_skill(name)
        elif what.lower() == "agent":
            return self.registry.get_agent(name)
        return None

    # ==================== 启用/禁用 ====================

    def enable(self, what: str, name: str) -> bool:
        """启用Skill或Agent"""
        if what.lower() == "skill":
            return self.registry.enable_skill(name)
        return False

    def disable(self, what: str, name: str) -> bool:
        """禁用Skill或Agent"""
        if what.lower() == "skill":
            return self.registry.disable_skill(name)
        return False

    # ==================== 调用API ====================

    def call(self, skill_name: str, action: str, **kwargs) -> Any:
        """
        调用Skill执行操作

        Args:
            skill_name: Skill名称
            action: 操作名称
            **kwargs: 操作参数

        Returns:
            操作结果

        Examples:
            # 调用content-layout-leo-cskill进行排版
            result = api.call("content-layout-leo-cskill",
                             "layout",
                             content="...", style="data_driven")
        """
        skill = self.registry.get_skill(skill_name)

        if not skill:
            print(f"❌ Skill不存在: {skill_name}")
            return None

        if not skill.enabled:
            print(f"❌ Skill已禁用: {skill_name}")
            return None

        # TODO: 实现实际的Skill调用逻辑
        print(f"🔧 调用Skill: {skill_name} - {action}")
        return f"执行{action}操作（待实现）"

    def run_agent(self, agent_name: str, task: str, **kwargs) -> Any:
        """
        运行Agent执行任务

        Args:
            agent_name: Agent名称
            task: 任务描述
            **kwargs: 任务参数

        Returns:
            任务结果

        Examples:
            # 使用task-agent执行任务
            result = api.run_agent("task-agent",
                                  "生成营销文档",
                                  project_info={...})
        """
        agent = self.registry.get_agent(agent_name)

        if not agent:
            print(f"❌ Agent不存在: {agent_name}")
            return None

        if not agent.enabled:
            print(f"❌ Agent已禁用: {agent_name}")
            return None

        # TODO: 实现实际的Agent调用逻辑
        print(f"🤖 运行Agent: {agent_name} - {task}")
        return f"执行{task}任务（待实现）"

    # ==================== 工作流API ====================

    def run_workflow(self, workflow_name: str, agents: Dict[str, Any] = None, **kwargs) -> Any:
        """
        运行预定义工作流

        Args:
            workflow_name: 工作流名称
            agents: Agent字典（可选，用于实际执行）
            **kwargs: 工作流参数

        Returns:
            工作流结果

        Examples:
            # 运行内容生产线
            result = api.run_workflow("content-pipeline",
                                     agents=system.agents,
                                     topic="房地产市场分析")
        """
        workflow = self.registry.get_workflow(workflow_name)

        if not workflow:
            print(f"❌ Workflow不存在: {workflow_name}")
            return None

        # 如果提供了agents，执行实际工作流
        if agents:
            # 动态导入WorkflowEngine
            import importlib.util
            from pathlib import Path

            workflow_engine_path = Path(__file__).parent / "workflow_engine.py"
            spec = importlib.util.spec_from_file_location("workflow_engine", workflow_engine_path)
            workflow_engine_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(workflow_engine_module)

            WorkflowEngine = workflow_engine_module.WorkflowEngine
            engine = WorkflowEngine(agents)
            return engine.execute(workflow, **kwargs)
        else:
            # 仅返回工作流配置
            print(f"🔄 工作流配置: {workflow_name}")
            return workflow

    # ==================== 统计信息 ====================

    def stats(self):
        """打印统计信息"""
        self.registry.print_stats()

    def summary(self) -> Dict[str, Any]:
        """
        获取统计摘要

        Returns:
            包含统计信息的字典
        """
        enabled_skills = [s for s in self.registry.skills.values() if s.enabled]
        enabled_agents = [a for a in self.registry.agents.values() if a.enabled]

        return {
            "skills": {
                "total": len(self.registry.skills),
                "enabled": len(enabled_skills),
                "by_category": self._group_by_category(enabled_skills)
            },
            "agents": {
                "total": len(self.registry.agents),
                "enabled": len(enabled_agents),
                "by_type": self._group_by_type(enabled_agents)
            },
            "workflows": {
                "total": len(self.registry.workflows),
                "names": list(self.registry.workflows.keys())
            }
        }

    def _group_by_category(self, skills: List[SkillRegistration]) -> Dict[str, int]:
        """按分类统计Skills"""
        result = {}
        for skill in skills:
            result[skill.category] = result.get(skill.category, 0) + 1
        return result

    def _group_by_type(self, agents: List[AgentRegistration]) -> Dict[str, int]:
        """按类型统计Agents"""
        result = {}
        for agent in agents:
            result[agent.type] = result.get(agent.type, 0) + 1
        return result


# ==================== 全局实例 ====================

# 创建全局API实例
leo = LeoAPI()


# ==================== 极简使用示例 ====================

def example_usage():
    """
    使用示例
    =========
    展示如何使用Leo API
    """

    # ========== 1. 查询已注册的内容 ==========

    # 列出所有Skills
    print("所有Skills:")
    for skill in leo.list("skills"):
        print(f"  • {skill}")

    # 列出特定分类的Skills
    print("\n内容创作类Skills:")
    for skill in leo.list("skills", category="content-creation"):
        print(f"  • {skill}")

    # 列出所有Agents
    print("\n所有Agents:")
    for agent in leo.list("agents"):
        print(f"  • {agent}")

    # ========== 2. 注册新的Skill ==========

    # 手动注册
    leo.register(
        "skill",
        "my-custom-skill",
        path="leo_skills/content-creation/my-custom-skill",
        category="content-creation"
    )

    # ========== 3. 启用/禁用 ==========

    leo.disable("skill", "my-custom-skill")
    leo.enable("skill", "my-custom-skill")

    # ========== 4. 调用 ==========

    # 调用Skill
    result = leo.call(
        "content-layout-leo-cskill",
        "layout",
        content="测试内容",
        style="data_driven"
    )

    # 运行Agent
    result = leo.run_agent(
        "task-agent",
        "生成营销文档",
        project_info={"name": "菜市场项目"}
    )

    # 运行工作流
    result = leo.run_workflow(
        "content-pipeline",
        topic="房地产市场分析"
    )

    # ========== 5. 统计信息 ==========

    # 打印详细统计
    leo.stats()

    # 获取统计摘要
    summary = leo.summary()
    print(f"\n统计摘要: {summary}")


if __name__ == "__main__":
    example_usage()
