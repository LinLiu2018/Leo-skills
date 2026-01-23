"""
Leo系统核心逻辑
===============
包含 LeoSystem 主类，负责系统的初始化、组件协调和任务分发。
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional, List

# 导入内部组件
# 注意：这里假设 leo_subagents 和 leo_orchestrator 已经在路径中或已安装
try:
    from leo_orchestrator.registry import get_registry
    from leo_orchestrator.api import LeoAPI
    from leo_subagents.agents.base_agent import AgentFactory, AgentConfig
    from leo_subagents.skills_bridge.skill_loader import SkillLoader
    from leo_subagents.skills_bridge.skill_executor import SkillExecutor
    
    # 动态加载增强版加载器（如果存在）
    try:
        from leo_subagents.skills_bridge.enhanced_skill_loader import EnhancedSkillLoader
        SKILL_LOADER_CLASS = EnhancedSkillLoader
    except ImportError:
        SKILL_LOADER_CLASS = SkillLoader

    # 尝试导入特定 Agent 类以便注册
    # 注意：在重构后的结构中，建议使用更动态的注册机制
    from leo_subagents.agents.task_agent import TaskAgent
except ImportError as e:
    print(f"⚠️ 核心依赖导入失败: {e}")
    # 提供空实现或抛出错误，视情况而定


class LeoSystem:
    """
    Leo系统主类 (Central Nervous System)
    ====================================
    单一事实来源，管理所有 Skills, Agents 和 Workflows。
    """

    def __init__(self, base_path: Optional[Path] = None):
        """
        初始化系统
        
        Args:
            base_path: 项目根目录。如果未提供，自动推断。
        """
        self.base_path = base_path or Path(__file__).parent.parent
        self.api = LeoAPI()
        
        # 使用增强版加载器（如果可用）
        skills_path = self.base_path / "leo_skills"
        workflows_path = self.base_path / "leo_workflows" / "workflows"
        
        try:
            self.skill_loader = SKILL_LOADER_CLASS(skills_path=skills_path, workflows_path=workflows_path)
        except TypeError:
            # 回退到旧版构造函数
            self.skill_loader = SKILL_LOADER_CLASS(base_path=skills_path)

        self.skill_executor = SkillExecutor(self.skill_loader)
        self.agents: Dict[str, Any] = {}

        # 注册核心 Agents (硬编码注册，未来应改为配置驱动)
        self._register_core_agents()

        # 初始化系统
        self._initialize()

    def _register_core_agents(self):
        """注册核心 Agent 类到工厂"""
        # 这里模拟之前 leo-system.py 中的手动注册逻辑
        # 理想情况下，这些应该在各自的模块加载时自动注册
        agent_paths = {
            "researcher": ("leo_subagents.agents.research_agent.research_agent", "ResearchAgent"),
            "analyzer": ("leo_subagents.agents.analysis_agent.analysis_agent", "AnalysisAgent"),
            "creator": ("leo_subagents.agents.creative_agent.creative_agent", "CreativeAgent"),
            "realestate": ("leo_subagents.agents.realestate_agent.realestate_agent", "RealEstateAgent")
        }
        
        import importlib
        for type_name, (module_path, class_name) in agent_paths.items():
            try:
                module = importlib.import_module(module_path)
                agent_class = getattr(module, class_name)
                AgentFactory.register_agent_class(type_name, agent_class)
            except Exception as e:
                # 静默失败或记录日志，避免阻塞启动
                # print(f"加载 Agent {class_name} 失败: {e}")
                pass

    def _initialize(self):
        """初始化系统组件"""
        # 加载 Skills
        try:
            if hasattr(self.skill_loader, 'discover_all'):
                self.skill_loader.discover_all()
            else:
                self.skill_loader.discover_and_load()
        except Exception as e:
            print(f"Skills 加载出错: {e}")

        # 创建 Agents
        self._create_agents()

    def _create_agents(self):
        """从配置创建 Agents"""
        registry = get_registry()
        
        # 确保 registry 已加载数据
        # 这里可能需要手动触发 registry 的加载，视 registry 实现而定
        
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
            except Exception as e:
                # print(f"创建 Agent {agent_name} 失败: {e}")
                pass

    def execute_task(self, task: str, agent_name: str = None, **kwargs) -> Dict[str, Any]:
        """执行任务"""
        # 1. 指定 Agent
        if agent_name:
            # 移除 emoji 前缀（如果 UI 传过来了）
            clean_name = agent_name.replace("🤖 ", "").strip()
            if clean_name in self.agents:
                return self.agents[clean_name].execute(task, **kwargs)
            return {"success": False, "error": f"Agent不存在: {clean_name}"}

        # 2. 自动选择
        best_agent = self._select_agent(task)
        if best_agent:
            return best_agent.execute(task, **kwargs)

        return {"success": False, "error": "没有合适的Agent可以处理此任务"}

    def _select_agent(self, task: str) -> Optional[Any]:
        """选择最佳 Agent"""
        best_agent = None
        best_score = 0.0

        for agent in self.agents.values():
            score = agent.can_handle(task)
            if score > best_score:
                best_score = score
                best_agent = agent

        return best_agent if best_score > 0.3 else None

    def call_skill(self, skill_name: str, action: str, **kwargs) -> Any:
        """直接调用 Skill"""
        return self.skill_executor.execute(skill_name, action, **kwargs)

    def list_skills(self, category: str = None) -> List[str]:
        return self.skill_loader.list_skills(category)

    def list_agents(self) -> List[str]:
        return list(self.agents.keys())
