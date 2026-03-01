"""
Leo统一API
===================
提供简洁的API接口来注册和使用Skills与Subagents

设计理念：
- 极简API，3行代码完成注册
- 自动发现，无需手动配置
- 统一调用，一个接口处理所有
"""

import importlib
import sys
import warnings
from pathlib import Path
from typing import Any, Dict, List, Optional

# 抑制循环导入警告
warnings.filterwarnings('ignore', message='.*partially initialized module.*')
warnings.filterwarnings('ignore', category=DeprecationWarning)

# 添加父目录到路径
parent_path = Path(__file__).parent.parent
if str(parent_path) not in sys.path:
    sys.path.insert(0, str(parent_path))

# 延迟导入，避免循环导入问题
from .registry import AgentRegistration, SkillRegistration, get_registry

# 延迟导入 logger
_logger = None

def _get_logger():
    global _logger
    if _logger is None:
        try:
            from leo_system.logger import get_logger as _get_logger
            _logger = _get_logger(__name__)
        except Exception:
            import logging
            _logger = logging.getLogger(__name__)
    return _logger

class _LoggerProxy:
    """Logger 代理类，支持延迟初始化"""
    def __getattr__(self, name):
        return getattr(_get_logger(), name)

logger = _LoggerProxy()


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
            logger.error(f"未知类型: {what}，必须是 'skill' 或 'agent'")
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
            # 调用content_layout_leo_skill进行排版
            result = api.call("content_layout_leo_skill",
                             "layout",
                             content="...", style="data_driven")
        """
        skill = self.registry.get_skill(skill_name)

        if not skill:
            logger.error(f"Skill不存在: {skill_name}")
            return None

        if not skill.enabled:
            logger.error(f"Skill已禁用: {skill_name}")
            return None

        # 实际调用逻辑
        try:
            from leo_subagents.skills_bridge.skill_executor import get_executor

            executor = get_executor()

            logger.info(f"调用Skill: {skill_name} - {action}")
            result = executor.execute(skill_name, action, **kwargs)
            return result
        except ImportError:
            logger.error(f"依赖错误: 无法导入 SkillExecutor")
            return None
        except Exception as e:
            logger.error(f"Skill调用失败: {e}")
            return None

    def _ensure_agent_type_loaded(self, agent_name: str, agent_type: str) -> bool:
        """Best-effort load agent modules so AgentFactory has the target type."""
        from leo_subagents.agents.base_agent import AgentFactory

        if agent_type in AgentFactory._agent_classes:
            return True

        normalized = agent_name.replace("-", "_")
        candidates = [
            f"leo_subagents.agents.{normalized}.{normalized}",
            f"leo_subagents.agents.{normalized}",
            "leo_subagents.agents.task_agent",
        ]
        for module_name in candidates:
            try:
                importlib.import_module(module_name)
            except Exception:
                continue
            if agent_type in AgentFactory._agent_classes:
                return True
        return agent_type in AgentFactory._agent_classes

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
            logger.error(f"Agent不存在: {agent_name}")
            return None

        if not agent.enabled:
            logger.error(f"Agent已禁用: {agent_name}")
            return None

        # 实际调用逻辑
        try:
            from leo_subagents.agents.base_agent import AgentConfig, AgentFactory

            logger.info(f"运行Agent: {agent_name} - {task}")

            # 1. 尝试获取现有实例
            agent_instance = AgentFactory.get_agent(agent_name)

            # 2. 如果不存在，则根据Registry信息临时创建
            if not agent_instance:
                resolved_type = agent.type
                self._ensure_agent_type_loaded(agent.name, resolved_type)
                if resolved_type not in AgentFactory._agent_classes:
                    logger.warning(
                        f"Agent type not registered: {resolved_type}, fallback to executor"
                    )
                    self._ensure_agent_type_loaded("task_agent", "executor")
                    resolved_type = "executor"
                # 重建配置
                config = AgentConfig(
                    name=agent.name,
                    type=resolved_type,
                    priority=agent.priority or 1,
                    skills=list(agent.skills) if agent.skills else [],
                    description=str((agent.metadata or {}).get("description", "")),
                )
                agent_instance = AgentFactory.create_agent(config)

            # 3. 执行任务
            result = agent_instance.execute(task, **kwargs)
            return result

        except ImportError:
            logger.error(f"依赖错误: 无法导入 AgentFactory")
            return None
        except Exception as e:
            logger.error(f"Agent运行失败: {e}")
            return None

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
            logger.error(f"Workflow不存在: {workflow_name}")
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
            logger.info(f"工作流配置: {workflow_name}")
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
                "by_category": self._group_by_category(enabled_skills),
            },
            "agents": {
                "total": len(self.registry.agents),
                "enabled": len(enabled_agents),
                "by_type": self._group_by_type(enabled_agents),
            },
            "workflows": {
                "total": len(self.registry.workflows),
                "names": list(self.registry.workflows.keys()),
            },
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


# ==================== 全局实例（惰性加载）====================

_leo_api: Optional[LeoAPI] = None


def get_leo_api() -> LeoAPI:
    """获取全局 LeoAPI 实例（惰性加载，线程安全）"""
    global _leo_api
    if _leo_api is None:
        from leo_system.singleton import thread_safe_singleton
        _leo_api = thread_safe_singleton("leo_api", _leo_api, LeoAPI)
    return _leo_api


# 向后兼容：延迟属性访问
class _LazyLeoAPI:
    """惰性代理，避免模块导入时触发磁盘扫描"""
    def __getattr__(self, name):
        return getattr(get_leo_api(), name)

leo = _LazyLeoAPI()


# ==================== 极简使用示例 ====================


def example_usage():
    """
    使用示例
    =========
    展示如何使用Leo API
    """

    # ========== 1. 查询已注册的内容 ==========

    # 列出所有Skills
    logger.info("所有Skills:")
    for skill in leo.list("skills"):
        logger.info(f"  • {skill}")

    # 列出特定分类的Skills
    logger.info("内容创作类Skills:")
    for skill in leo.list("skills", category="content-creation"):
        logger.info(f"  • {skill}")

    # 列出所有Agents
    logger.info("所有Agents:")
    for agent in leo.list("agents"):
        logger.info(f"  • {agent}")

    # ========== 2. 注册新的Skill ==========

    # 手动注册
    leo.register(
        "skill",
        "my-custom-skill",
        path="leo_skills/content-creation/my-custom-skill",
        category="content-creation",
    )

    # ========== 3. 启用/禁用 ==========

    leo.disable("skill", "my-custom-skill")
    leo.enable("skill", "my-custom-skill")

    # ========== 4. 调用 ==========

    # 调用Skill
    result = leo.call(
        "content_layout_leo_skill", "layout", content="测试内容", style="data_driven"
    )

    # 运行Agent
    result = leo.run_agent("task-agent", "生成营销文档", project_info={"name": "菜市场项目"})

    # 运行工作流
    result = leo.run_workflow("content-pipeline", topic="房地产市场分析")

    # ========== 5. 统计信息 ==========

    # 打印详细统计
    leo.stats()

    # 获取统计摘要
    summary = leo.summary()
    logger.info(f"统计摘要: {summary}")


if __name__ == "__main__":
    example_usage()
