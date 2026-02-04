"""
Leo系统核心逻辑
===============
包含 LeoSystem 主类，负责系统的初始化、组件协调和任务分发。
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from .errors import InitializationError, SkillExecutionError

# 导入日志和错误处理
from .logger import get_logger
from .metrics import track_time

# 创建日志记录器
logger = get_logger(__name__)

# 导入内部组件 - 使用安全的导入方式
LeoAPI = None
SKILL_LOADER_CLASS = None
SkillExecutor = None
AgentConfig = None
AgentFactory = None
get_registry = None

try:
    from leo_orchestrator.api import LeoAPI as LeoAPIClass
    LeoAPI = LeoAPIClass
except ImportError as e:
    logger.warning(f"LeoAPI 导入失败: {e}")

try:
    from leo_orchestrator.registry import get_registry as get_reg
    get_registry = get_reg
except ImportError as e:
    logger.warning(f"get_registry 导入失败: {e}")

try:
    from leo_subagents.agents.base_agent import AgentConfig as AgentConfigClass, AgentFactory as AgentFactoryClass
    AgentConfig = AgentConfigClass
    AgentFactory = AgentFactoryClass
except ImportError as e:
    logger.warning(f"AgentConfig/AgentFactory 导入失败: {e}")

try:
    from leo_subagents.skills_bridge.skill_executor import SkillExecutor as SkillExecutorClass
    SkillExecutor = SkillExecutorClass
except ImportError as e:
    logger.warning(f"SkillExecutor 导入失败: {e}")

try:
    from leo_subagents.skills_bridge.skill_loader import SkillLoader
    SKILL_LOADER_CLASS = SkillLoader
except ImportError as e:
    logger.warning(f"SkillLoader 导入失败: {e}")

try:
    from leo_subagents.skills_bridge.enhanced_skill_loader import EnhancedSkillLoader
    SKILL_LOADER_CLASS = EnhancedSkillLoader
except ImportError:
    pass


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
        logger.info("Initializing Leo System...")
        self.base_path = base_path or Path(__file__).parent.parent
        
        # 初始化 api
        self.api = None
        if LeoAPI:
            try:
                self.api = LeoAPI()
            except Exception as e:
                logger.warning(f"LeoAPI 初始化失败: {e}")

        # 初始化 skill_loader
        self.skill_loader = None
        skills_path = self.base_path / "leo_skills"
        
        if SKILL_LOADER_CLASS:
            try:
                self.skill_loader = SKILL_LOADER_CLASS(base_path=skills_path)
            except Exception as e:
                logger.warning(f"SkillLoader 初始化失败: {e}")

        # 初始化 skill_executor
        self.skill_executor = None
        if SkillExecutor and self.skill_loader:
            try:
                self.skill_executor = SkillExecutor(self.skill_loader)
            except Exception as e:
                logger.warning(f"SkillExecutor 初始化失败: {e}")

        self.agents: Dict[str, Any] = {}

        # 注册核心 Agents
        self._register_core_agents()

        # 初始化系统
        self._initialize()

        logger.info("Leo System initialized successfully")

    def _register_core_agents(self):
        """注册核心 Agent 类到工厂"""
        if not AgentFactory:
            return
            
        agent_paths = {
            "researcher": ("leo_subagents.agents.research_agent.research_agent", "ResearchAgent"),
            "analyzer": ("leo_subagents.agents.analysis_agent.analysis_agent", "AnalysisAgent"),
            "creator": ("leo_subagents.agents.creative_agent.creative_agent", "CreativeAgent"),
            "realestate": (
                "leo_subagents.agents.realestate_agent.realestate_agent",
                "RealEstateAgent",
            ),
        }

        import importlib

        for type_name, (module_path, class_name) in agent_paths.items():
            try:
                module = importlib.import_module(module_path)
                agent_class = getattr(module, class_name)
                AgentFactory.register_agent_class(type_name, agent_class)
                logger.debug(f"Registered agent class: {class_name}")
            except Exception as e:
                logger.debug(f"Failed to load agent {class_name}: {e}")

    def _initialize(self):
        """初始化系统组件"""
        # 加载 Skills
        if self.skill_loader and hasattr(self.skill_loader, 'discover_and_load'):
            try:
                self.skill_loader.discover_and_load()
                logger.info("Skills loaded successfully")
            except Exception as e:
                logger.warning(f"Skills loading warning: {e}")

        # 创建 Agents
        self._create_agents()

    def _create_agents(self):
        """从配置创建 Agents"""
        if not get_registry or not AgentConfig or not AgentFactory:
            return

        try:
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
                    description=agent_reg.metadata.get("description", "") if agent_reg.metadata else "",
                )

                try:
                    agent = AgentFactory.create_agent(config)
                    self.agents[agent_name] = agent
                    logger.debug(f"Created agent: {agent_name}")
                except Exception as e:
                    logger.debug(f"Failed to create agent {agent_name}: {e}")
        except Exception as e:
            logger.warning(f"Agent creation warning: {e}")

    @track_time
    def execute_task(self, task: str, agent_name: str = None, **kwargs) -> Dict[str, Any]:
        """执行任务"""
        logger.info(f"Executing task: {task[:50]}... (agent: {agent_name or 'auto'})")

        # 1. 指定 Agent
        if agent_name:
            clean_name = agent_name.replace("🤖 ", "").strip()
            if clean_name in self.agents:
                result = self.agents[clean_name].execute(task, **kwargs)
                logger.info(
                    f"Task executed by {clean_name}: success={result.get('success', False)}"
                )
                return result
            error_msg = f"Agent不存在: {clean_name}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}

        # 2. 自动选择
        best_agent = self._select_agent(task)
        if best_agent:
            result = best_agent.execute(task, **kwargs)
            logger.info(
                f"Task executed by auto-selected agent: success={result.get('success', False)}"
            )
            return result

        error_msg = "没有合适的Agent可以处理此任务"
        logger.warning(error_msg)
        return {"success": False, "error": error_msg}

    def _select_agent(self, task: str) -> Optional[Any]:
        """选择最佳 Agent"""
        if not self.agents:
            return None
            
        best_agent = None
        best_score = 0.0

        for agent in self.agents.values():
            score = agent.can_handle(task)
            if score > best_score:
                best_score = score
                best_agent = agent

        return best_agent if best_score > 0.3 else None

    @track_time
    def call_skill(self, skill_name: str, action: str, **kwargs) -> Any:
        """直接调用 Skill"""
        if not self.skill_executor:
            raise SkillExecutionError(skill_name, "SkillExecutor 未初始化")
            
        logger.info(f"Calling skill: {skill_name}.{action}")
        try:
            result = self.skill_executor.execute(skill_name, action, **kwargs)
            logger.info(f"Skill {skill_name}.{action} executed successfully")
            return result
        except Exception as e:
            logger.error(f"Skill execution failed: {skill_name}.{action} - {e}")
            raise SkillExecutionError(skill_name, str(e))

    def list_skills(self, category: str = None) -> List[str]:
        if self.skill_loader and hasattr(self.skill_loader, 'list_skills'):
            return self.skill_loader.list_skills(category)
        return []

    def list_agents(self) -> List[str]:
        return list(self.agents.keys())
