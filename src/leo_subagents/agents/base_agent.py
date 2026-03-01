"""
Subagent基类
============
所有Subagent的基础类
"""

import sys
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

# 添加父目录到路径
parent_path = Path(__file__).parent.parent.parent
if str(parent_path) not in sys.path:
    sys.path.insert(0, str(parent_path))

if TYPE_CHECKING:
    pass

# 导入日志和错误处理
from leo_system.logger import get_logger
from leo_system.errors import AgentError, AgentDispatchError
from leo_system.metrics import track_time

# 导入 LLM 适配器
try:
    from ..core.llm_adapter import LLMAdapter, get_llm
except ImportError:
    # 如果 core 模块不存在，提供降级
    LLMAdapter = None
    def get_llm(*args, **kwargs):
        return None

# 创建日志记录器
logger = get_logger(__name__)


@dataclass
class AgentConfig:
    """Agent配置"""

    name: str
    type: str
    priority: int
    skills: List[str]
    description: str = ""
    enabled: bool = True
    max_retries: int = 3
    timeout: int = 300


class BaseAgent(ABC):
    """
    Subagent基类
    ============
    定义所有Agent必须实现的接口
    """

    def __init__(self, config: AgentConfig):
        """
        初始化Agent

        Args:
            config: Agent配置
        """
        from ..skills_bridge.skill_executor import get_executor
        from ..skills_bridge.skill_loader import get_loader

        self.config = config
        self.skill_loader = get_loader()
        self.skill_executor = get_executor()
        self.task_history: List[Dict[str, Any]] = []
        self.context_cache: Dict[str, str] = {}  # Modular Context 缓存

    @abstractmethod
    def can_handle(self, task: str) -> float:
        """
        判断是否能处理此任务

        Args:
            task: 任务描述

        Returns:
            置信度 (0.0 - 1.0)
        """

    @abstractmethod
    @track_time
    def execute(self, task: str, **kwargs) -> Dict[str, Any]:
        """
        执行任务

        Args:
            task: 任务描述
            **kwargs: 任务参数

        Returns:
            执行结果
        """

    def get_available_skills(self) -> List[str]:
        """
        获取可用的Skills

        Returns:
            Skill名称列表
        """
        return self.config.skills

    def has_skill(self, skill_name: str) -> bool:
        """
        检查是否有某个Skill

        Args:
            skill_name: Skill名称

        Returns:
            是否拥有此Skill
        """
        return skill_name in self.config.skills

    def use_skill(self, skill_name: str, action: str, **kwargs) -> Any:
        """
        调用Skill

        Args:
            skill_name: Skill名称
            action: 操作名称
            **kwargs: 参数

        Returns:
            Skill执行结果
        """
        if not self.has_skill(skill_name):
            logger.error(f"Agent '{self.config.name}' 没有 Skill '{skill_name}'")
            raise AgentDispatchError(self.config.name, skill_name, "Skill not available")

        result = self.skill_executor.execute(skill_name, action, **kwargs)

        return result

    def load_context(self, path: str) -> str:
        """
        加载知识上下文 (Modular Context)

        Args:
            path: 相对路径 (e.g., "templates/prd_template.md")

        Returns:
            文件内容
        """
        from pathlib import Path

        # 缓存检查
        if path in self.context_cache:
            return self.context_cache[path]

        # 路径解析 (Project Root)
        # base_agent.py 在 leo_subagents/agents/base_agent.py
        # root 在 ../../../
        root_path = Path(__file__).parent.parent.parent
        knowledge_path = root_path / "leo_knowledge" / path

        if not knowledge_path.exists():
            logger.warning(f"Context file not found: {knowledge_path}")
            return ""

        try:
            with open(knowledge_path, "r", encoding="utf-8") as f:
                content = f.read()
                self.context_cache[path] = content
                return content
        except Exception as e:
            logger.error(f"Error loading context {path}: {e}")
            return ""

    def plan_execution(self, task: str, **kwargs) -> List[Dict[str, Any]]:
        """
        规划任务执行步骤

        Args:
            task: 任务描述
            **kwargs: 任务参数

        Returns:
            执行步骤列表
        """
        # 默认实现：简单规划
        # 子类可以重写此方法以实现更复杂的规划

        # 尝试将任务映射到合适的Skill
        steps = []

        for skill_name in self.config.skills:
            # 这里应该有更智能的匹配逻辑
            # 简化实现：每个Skill一个步骤
            steps.append(
                {"step": len(steps) + 1, "skill": skill_name, "action": "execute", "params": kwargs}
            )

        return steps

    def log_task(self, task: str, result: Dict[str, Any]):
        """
        记录任务执行历史

        Args:
            task: 任务描述
            result: 执行结果
        """
        self.task_history.append(
            {"timestamp": datetime.now().isoformat(), "task": task, "result": result}
        )

    def get_status(self) -> Dict[str, Any]:
        """
        获取Agent状态

        Returns:
            状态信息字典
        """
        return {
            "name": self.config.name,
            "type": self.config.type,
            "enabled": self.config.enabled,
            "priority": self.config.priority,
            "skills": self.config.skills,
            "tasks_completed": len(self.task_history),
        }

    def __repr__(self):
        return (
            f"Agent({self.config.name}, type={self.config.type}, skills={len(self.config.skills)})"
        )

    # ==================== LLM 驱动执行（新增）====================

    def execute_with_llm(self, task: str, **kwargs) -> Dict[str, Any]:
        """
        LLM 驱动的任务执行

        这是 Wingman 模式的核心方法：
        1. 加载用户画像和项目上下文
        2. 构建包含技能的 Prompt
        3. 调用 LLM 分析任务
        4. 解析并执行技能调用
        5. 返回完整结果

        Args:
            task: 任务描述
            **kwargs: 任务参数

        Returns:
            执行结果字典
        """
        logger.info(f"Agent '{self.config.name}' 开始 LLM 驱动执行任务: {task}")

        # 1. 加载上下文
        user_context = self._load_user_context()
        project_context = self._load_project_context()

        # 2. 构建 Prompt
        prompt = self._build_llm_prompt(task, user_context, project_context, kwargs)
        system_prompt = self._build_system_prompt()

        # 3. 调用 LLM
        try:
            if LLMAdapter:
                llm = LLMAdapter(provider=kwargs.get("llm_provider", "claude"))
                response = llm.call(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    max_tokens=kwargs.get("max_tokens", 4000),
                    temperature=kwargs.get("temperature", 0.7)
                )
                llm_output = response.content
            else:
                # 降级到模拟模式
                llm_output = self._mock_llm_response(task)
        except Exception as e:
            logger.error(f"LLM 调用失败: {e}")
            return {"status": "error", "error": str(e), "task": task}

        # 4. 解析 LLM 输出
        try:
            actions = self._parse_llm_output(llm_output)
        except json.JSONDecodeError as e:
            logger.error(f"LLM 输出解析失败: {e}")
            # 尝试直接使用文本输出
            actions = [{"type": "output", "content": llm_output}]

        # 5. 执行动作
        results = []
        for action in actions:
            try:
                result = self._execute_action(action, task, kwargs)
                results.append(result)
            except Exception as e:
                logger.error(f"动作执行失败: {action}, 错误: {e}")
                results.append({"status": "error", "action": action, "error": str(e)})

        # 6. 组装最终响应
        final_result = {
            "status": "completed" if all(r.get("status") != "error" for r in results) else "partial",
            "task": task,
            "agent": self.config.name,
            "actions_executed": len(results),
            "results": results,
            "llm_response": llm_output[:500] if len(llm_output) > 500 else llm_output  # 截断日志
        }

        # 7. 记录任务
        self.log_task(task, final_result)

        logger.info(f"Agent '{self.config.name}' 任务执行完成: {task}")
        return final_result

    def _load_user_context(self) -> str:
        """加载用户画像上下文"""
        try:
            return self.load_context("context/user_profile.md")
        except Exception:
            return ""

    def _load_project_context(self) -> str:
        """加载项目上下文"""
        try:
            return self.load_context("context/project_context.md")
        except Exception:
            return ""

    def _build_system_prompt(self) -> str:
        """构建系统提示词"""
        return f"""你是一个 {self.config.type} 类型的 AI 代理，名为 {self.config.name}。

{self.config.description}

你的可用技能：
{chr(10).join(f"- {skill}" for skill in self.config.skills)}

你的任务是分析用户输入，规划执行步骤，并返回结构化的执行计划。

输出格式必须是 JSON：
{{
    "analysis": "任务分析",
    "plan": ["步骤1", "步骤2", ...],
    "actions": [
        {{"type": "use_skill", "skill": "技能名", "action": "操作", "params": {{}}}}
    ],
    "output": "直接输出内容（如果不需要调用技能）"
}}"""

    def _build_llm_prompt(self, task: str, user_context: str, project_context: str, kwargs: Dict) -> str:
        """构建 LLM 提示词"""
        context_parts = []

        if user_context:
            context_parts.append(f"用户画像:\n{user_context[:1000]}")  # 限制长度

        if project_context:
            context_parts.append(f"项目上下文:\n{project_context[:1000]}")

        if kwargs:
            context_parts.append(f"额外参数:\n{json.dumps(kwargs, ensure_ascii=False, indent=2)[:500]}")

        context_str = "\n\n".join(context_parts) if context_parts else "无额外上下文"

        return f"""任务: {task}

{context_str}

请分析这个任务并返回执行计划（JSON 格式）：
{{
    "analysis": "简要分析用户意图",
    "plan": ["执行步骤1", "执行步骤2"],
    "actions": [
        {{"type": "use_skill", "skill": "技能名", "action": "操作", "params": {{"key": "value"}}}},
        {{"type": "output", "content": "直接输出内容"}}
    ],
    "expected_output": "预期输出格式"
}}"""

    def _parse_llm_output(self, output: str) -> List[Dict]:
        """解析 LLM 输出"""
        # 尝试提取 JSON
        try:
            # 查找 JSON 块
            if "```json" in output:
                json_str = output.split("```json")[1].split("```")[0].strip()
            elif "```" in output:
                json_str = output.split("```")[1].split("```")[0].strip()
            else:
                json_str = output.strip()

            data = json.loads(json_str)

            # 返回动作列表
            if "actions" in data:
                return data["actions"]
            elif "output" in data:
                return [{"type": "output", "content": data["output"]}]
            else:
                return [{"type": "output", "content": json.dumps(data, ensure_ascii=False)}]

        except json.JSONDecodeError:
            # 如果不是 JSON，直接返回文本输出
            return [{"type": "output", "content": output}]

    def _execute_action(self, action: Dict, task: str, kwargs: Dict) -> Dict:
        """执行单个动作"""
        action_type = action.get("type")

        if action_type == "use_skill":
            skill_name = action.get("skill")
            action_name = action.get("action", "execute")
            params = action.get("params", {})

            if not self.has_skill(skill_name):
                return {"status": "error", "error": f"Agent 没有技能: {skill_name}"}

            result = self.use_skill(skill_name, action_name, **params)
            return {"status": "success", "type": "skill", "skill": skill_name, "result": result}

        elif action_type == "output":
            return {"status": "success", "type": "output", "content": action.get("content", "")}

        elif action_type == "plan":
            # 只是规划，不执行
            return {"status": "success", "type": "plan", "steps": action.get("steps", [])}

        else:
            return {"status": "error", "error": f"未知动作类型: {action_type}"}

    def _mock_llm_response(self, task: str) -> str:
        """模拟 LLM 响应（用于测试）"""
        # 基于任务关键词返回模拟响应
        mock_actions = []

        if "研究" in task or "调研" in task:
            mock_actions.append({
                "type": "use_skill",
                "skill": "research_assistant_skill",
                "action": "research",
                "params": {"query": task}
            })

        if "分析" in task:
            mock_actions.append({
                "type": "use_skill",
                "skill": "data_analyzer_skill",
                "action": "analyze",
                "params": {"data": task}
            })

        if "生成" in task or "创建" in task:
            mock_actions.append({
                "type": "use_skill",
                "skill": "content_layout_leo_skill",
                "action": "generate",
                "params": {"topic": task}
            })

        if not mock_actions:
            mock_actions.append({
                "type": "output",
                "content": f"收到任务: {task}。这是一个示例响应，实际运行时将调用 LLM 生成完整结果。"
            })

        return json.dumps({
            "analysis": f"分析任务: {task[:50]}...",
            "plan": ["分析需求", "调用技能", "返回结果"],
            "actions": mock_actions,
            "expected_output": "结构化结果"
        }, ensure_ascii=False, indent=2)


# ==================== Agent工厂 ====================


class AgentFactory:
    """
    Agent工厂
    =========
    负责创建和管理Agent实例
    """

    _agents: Dict[str, BaseAgent] = {}
    _agent_classes: Dict[str, type] = {}

    @classmethod
    def register_agent_class(cls, agent_type: str, agent_class: type):
        """
        注册Agent类

        Args:
            agent_type: Agent类型
            agent_class: Agent类
        """
        cls._agent_classes[agent_type] = agent_class

    @classmethod
    def create_agent(cls, config: AgentConfig) -> BaseAgent:
        """
        创建Agent实例

        Args:
            config: Agent配置

        Returns:
            Agent实例
        """
        agent_class = cls._agent_classes.get(config.type)

        if not agent_class:
            logger.error(f"未知的Agent类型: {config.type}")
            raise AgentError(f"Unknown agent type: {config.type}")

        agent = agent_class(config)
        cls._agents[config.name] = agent

        return agent

    @classmethod
    def get_agent(cls, name: str) -> Optional[BaseAgent]:
        """
        获取Agent实例

        Args:
            name: Agent名称

        Returns:
            Agent实例或None
        """
        return cls._agents.get(name)

    @classmethod
    def list_agents(cls) -> List[str]:
        """
        列出所有已创建的Agent

        Returns:
            Agent名称列表
        """
        return list(cls._agents.keys())


# ==================== 使用示例 ====================

if __name__ == "__main__":
    # 示例：创建一个简单的Agent类
    class SimpleAgent(BaseAgent):
        def can_handle(self, task: str) -> float:
            return 0.8

        def execute(self, task: str, **kwargs) -> Dict[str, Any]:
            result = {"task": task, "status": "completed", "message": f"任务 '{task}' 已完成"}
            self.log_task(task, result)
            return result

    # 创建配置
    config = AgentConfig(
        name="simple-agent", type="simple", priority=1, skills=["skill1", "skill2"]
    )

    # 创建Agent
    agent = SimpleAgent(config)

    # 执行任务
    result = agent.execute("测试任务")
    logger.info(f"执行结果: {result}")
