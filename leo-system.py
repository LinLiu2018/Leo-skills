"""
Leo AI Agent System - 主入口
============================
统一的Skills和Subagents管理系统
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional, List

# 设置输出编码为UTF-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加路径
current_path = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_path))

# 使用importlib直接加载模块
import importlib.util

def load_module_from_file(module_name: str, file_path: str):
    """从文件直接加载模块"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

# 加载registry模块
registry = load_module_from_file("leo_orchestrator.registry", str(current_path / "leo-orchestrator" / "registry.py"))
api = load_module_from_file("leo_orchestrator.api", str(current_path / "leo-orchestrator" / "api.py"))

# 导入所需的类和函数
UnifiedRegistry = registry.UnifiedRegistry
get_registry = registry.get_registry
SkillRegistration = registry.SkillRegistration
AgentRegistration = registry.AgentRegistration
LeoAPI = api.LeoAPI

# 加载subagents模块
base_agent = load_module_from_file("leo_subagents.agents.base_agent", str(current_path / "leo-subagents" / "agents" / "base_agent.py"))
AgentFactory = base_agent.AgentFactory
AgentConfig = base_agent.AgentConfig

skill_adapter = load_module_from_file("leo_subagents.skills_bridge.skill_adapter", str(current_path / "leo-subagents" / "skills-bridge" / "skill_adapter.py"))
skill_loader = load_module_from_file("leo_subagents.skills_bridge.skill_loader", str(current_path / "leo-subagents" / "skills-bridge" / "skill_loader.py"))
skill_executor_module = load_module_from_file("leo_subagents.skills_bridge.skill_executor", str(current_path / "leo-subagents" / "skills-bridge" / "skill_executor.py"))

SkillLoader = skill_loader.SkillLoader
SkillExecutor = skill_executor_module.SkillExecutor

# 创建task_agent模块的依赖
task_agent_module = load_module_from_file("leo_subagents.agents.task_agent", str(current_path / "leo-subagents" / "agents" / "task_agent.py"))
TaskAgent = task_agent_module.TaskAgent


class LeoSystem:
    """
    Leo系统主类
    ===========
    提供统一的接口来管理Skills和Subagents
    """

    def __init__(self):
        """初始化系统"""
        self.api = LeoAPI()
        self.skill_loader = SkillLoader()
        self.skill_executor = SkillExecutor(self.skill_loader)
        self.agents: Dict[str, Any] = {}

        # 初始化系统
        self._initialize()

    def _initialize(self):
        """初始化系统组件"""
        print("🚀 初始化Leo系统...")

        # 加载Skills
        skills_count = self.skill_loader.discover_and_load()

        # 创建Agents
        self._create_agents()

        # 打印系统状态
        print(f"\n✅ 系统初始化完成！")
        print(f"   - {skills_count} 个Skills已加载")
        print(f"   - {len(self.agents)} 个Agents已创建")

    def _create_agents(self):
        """从配置创建Agents"""
        registry = get_registry()

        for agent_name, agent_reg in registry.agents.items():
            if not agent_reg.enabled:
                continue

            config = AgentConfig(
                name=agent_name,
                type=agent_reg.type,
                priority=agent_reg.priority,
                skills=agent_reg.skills,
                enabled=agent_reg.enabled,
                description=agent_reg.metadata.get('description', '') if agent_reg.metadata else ''
            )

            try:
                agent = AgentFactory.create_agent(config)
                self.agents[agent_name] = agent
                print(f"  ✅ 创建Agent: {agent_name} ({agent_reg.type})")
            except Exception as e:
                print(f"  ⚠️  创建Agent失败 {agent_name}: {e}")

    def execute_task(self,
                    task: str,
                    agent_name: str = None,
                    **kwargs) -> Dict[str, Any]:
        """
        执行任务

        Args:
            task: 任务描述
            agent_name: 指定Agent（可选）
            **kwargs: 任务参数

        Returns:
            执行结果
        """
        # 如果指定了Agent，直接使用
        if agent_name:
            if agent_name not in self.agents:
                return {
                    "success": False,
                    "error": f"Agent不存在: {agent_name}"
                }
            agent = self.agents[agent_name]
            return agent.execute(task, **kwargs)

        # 自动选择最合适的Agent
        best_agent = self._select_agent(task)

        if not best_agent:
            return {
                "success": False,
                "error": "没有合适的Agent可以处理此任务"
            }

        print(f"🤖 使用 {best_agent.config.name} 处理任务")
        return best_agent.execute(task, **kwargs)

    def _select_agent(self, task: str) -> Optional[Any]:
        """
        选择最合适的Agent

        Args:
            task: 任务描述

        Returns:
            最佳Agent或None
        """
        best_agent = None
        best_score = 0.0

        for agent in self.agents.values():
            score = agent.can_handle(task)
            if score > best_score:
                best_score = score
                best_agent = agent

        # 只有当置信度超过阈值时才返回
        if best_score > 0.3:
            return best_agent

        return None

    def call_skill(self,
                  skill_name: str,
                  action: str,
                  **kwargs) -> Any:
        """
        直接调用Skill

        Args:
            skill_name: Skill名称
            action: 操作名称
            **kwargs: 参数

        Returns:
            执行结果
        """
        return self.skill_executor.execute(skill_name, action, **kwargs)

    def list_skills(self, category: str = None) -> List[str]:
        """
        列出Skills

        Args:
            category: 分类筛选（可选）

        Returns:
            Skill名称列表
        """
        return self.skill_loader.list_skills(category)

    def list_agents(self) -> List[str]:
        """
        列出Agents

        Returns:
            Agent名称列表
        """
        return list(self.agents.keys())

    def get_system_status(self) -> Dict[str, Any]:
        """
        获取系统状态

        Returns:
            系统状态字典
        """
        return {
            "skills": {
                "total": len(self.skill_loader.skills),
                "by_category": self.skill_loader.categories
            },
            "agents": {
                "total": len(self.agents),
                "names": list(self.agents.keys())
            },
            "statistics": self.skill_executor.get_statistics()
        }

    def print_status(self):
        """打印系统状态"""
        print("\n" + "=" * 60)
        print("📊 Leo系统状态")
        print("=" * 60)

        # Skills统计
        print(f"\n🎯 Skills: {len(self.skill_loader.skills)} 个")
        for category, skills in self.skill_loader.categories.items():
            print(f"  📁 {category}: {len(skills)} 个")

        # Agents统计
        print(f"\n🤖 Agents: {len(self.agents)} 个")
        for agent_name, agent in self.agents.items():
            print(f"  • {agent_name} ({agent.config.type}) - {len(agent.config.skills)} skills")

        # 执行统计
        stats = self.skill_executor.get_statistics()
        print(f"\n📈 执行统计:")
        print(f"  总执行次数: {stats['total_executions']}")
        if stats['total_executions'] > 0:
            print(f"  成功率: {stats['success_rate']:.1f}%")

        print("=" * 60 + "\n")


# ==================== 全局系统实例 ====================

_system: Optional[LeoSystem] = None


def get_system() -> LeoSystem:
    """
    获取全局系统实例

    Returns:
        Leo系统实例
    """
    global _system
    if _system is None:
        _system = LeoSystem()
    return _system


# ==================== 便捷函数 ====================

def execute(task: str, agent: str = None, **kwargs) -> Dict[str, Any]:
    """
    便捷函数：执行任务

    Args:
        task: 任务描述
        agent: 指定Agent（可选）
        **kwargs: 任务参数

    Returns:
        执行结果
    """
    system = get_system()
    return system.execute_task(task, agent, **kwargs)


def call(skill_name: str, action: str, **kwargs) -> Any:
    """
    便捷函数：调用Skill

    Args:
        skill_name: Skill名称
        action: 操作名称
        **kwargs: 参数

    Returns:
        执行结果
    """
    system = get_system()
    return system.call_skill(skill_name, action, **kwargs)


# ==================== 命令行接口 ====================

def main():
    """命令行主入口"""
    import argparse

    parser = argparse.ArgumentParser(description="Leo AI Agent System")
    parser.add_argument("--status", action="store_true", help="显示系统状态")
    parser.add_argument("--list", choices=["skills", "agents"], help="列出Skills或Agents")
    parser.add_argument("--execute", type=str, help="执行任务")
    parser.add_argument("--agent", type=str, help="指定Agent")
    parser.add_argument("--call", type=str, help="调用Skill (格式: skill_name:action)")

    args = parser.parse_args()

    # 获取系统实例
    system = get_system()

    if args.status:
        system.print_status()

    elif args.list == "skills":
        print("\n📚 所有Skills:")
        for skill in system.list_skills():
            print(f"  • {skill}")

    elif args.list == "agents":
        print("\n🤖 所有Agents:")
        for agent in system.list_agents():
            print(f"  • {agent}")

    elif args.execute:
        result = system.execute_task(args.execute, args.agent)
        print(f"\n✅ 执行结果:")
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif args.call:
        if ":" not in args.call:
            print("❌ 格式错误，应为 skill_name:action")
            return

        skill_name, action = args.call.split(":", 1)
        result = system.call_skill(skill_name, action)
        print(f"\n✅ 调用结果:")
        print(result)

    else:
        # 默认：显示状态
        system.print_status()


# ==================== 使用示例 ====================

if __name__ == "__main__":
    # 示例1：获取系统
    system = get_system()

    # 示例2：执行任务
    print("\n📝 示例：执行任务")
    result = system.execute_task("帮我排版这篇文章")
    print(f"结果: {json.dumps(result, indent=2, ensure_ascii=False)}")

    # 示例3：调用Skill
    print("\n📝 示例：调用Skill")
    result = system.call_skill(
        "content-layout-leo-cskill",
        "layout",
        content="测试内容",
        style="data_driven"
    )
    print(f"结果: {result}")

    # 示例4：显示状态
    system.print_status()
