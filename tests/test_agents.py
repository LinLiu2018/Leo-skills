"""
Agents 单元测试
===============
测试所有 Agents 的基础功能
"""


import pytest


@pytest.mark.unit
@pytest.mark.agents
class TestAgentDiscovery:
    """AgentDiscovery 测试"""

    def test_discovery_initialization(self, agents_dir):
        """测试 AgentDiscovery 初始化"""
        from leo_subagents.agents.agent_discovery import AgentDiscovery

        discovery = AgentDiscovery(agents_dir)
        assert discovery is not None
        assert discovery.agents_dir == agents_dir

    def test_discover_all_agents(self, agents_dir):
        """测试发现所有 Agents"""
        from leo_subagents.agents.agent_discovery import AgentDiscovery

        discovery = AgentDiscovery(agents_dir)
        agents = discovery.discover_all()

        assert isinstance(agents, dict)
        assert len(agents) >= 1, "应该发现至少 1 个 Agent"

    def test_infer_class_name(self, agents_dir):
        """测试类名推断"""
        from leo_subagents.agents.agent_discovery import AgentDiscovery

        discovery = AgentDiscovery(agents_dir)

        # 测试各种命名格式
        assert discovery._infer_class_name("research_agent") == "ResearchAgent"
        assert discovery._infer_class_name("task-agent") == "TaskAgent"
        assert discovery._infer_class_name("creative") == "CreativeAgent"

    def test_infer_agent_type(self, agents_dir):
        """测试 Agent 类型推断"""
        from leo_subagents.agents.agent_discovery import AgentDiscovery

        discovery = AgentDiscovery(agents_dir)

        assert discovery._infer_agent_type("research_agent") == "researcher"
        assert discovery._infer_agent_type("analysis_agent") == "analyzer"
        assert discovery._infer_agent_type("creative_agent") == "creator"


@pytest.mark.unit
@pytest.mark.agents
class TestBaseAgent:
    """BaseAgent 测试"""

    def test_agent_config_dataclass(self):
        """测试 AgentConfig 数据类"""
        from leo_subagents.agents.base_agent import AgentConfig

        config = AgentConfig(
            name="test-agent", type="executor", priority=1, skills=["skill1", "skill2"]
        )

        assert config.name == "test-agent"
        assert config.type == "executor"
        assert config.priority == 1
        assert len(config.skills) == 2
        assert config.enabled == True  # 默认值

    def test_agent_factory_register(self, agent_factory):
        """测试 AgentFactory 注册"""
        from leo_subagents.agents.base_agent import BaseAgent

        class MockAgent(BaseAgent):
            def can_handle(self, task: str) -> float:
                return 0.5

            def execute(self, task: str, **kwargs):
                return {"status": "completed"}

        # 注册 Mock Agent
        agent_factory.register_agent_class("mock", MockAgent)

        # 验证注册成功
        assert "mock" in agent_factory._agent_classes

    def test_agent_factory_create(self, agent_factory):
        """测试 AgentFactory 创建 Agent"""
        from leo_subagents.agents.base_agent import AgentConfig, BaseAgent

        class TestAgent(BaseAgent):
            def can_handle(self, task: str) -> float:
                return 0.5

            def execute(self, task: str, **kwargs):
                return {"status": "completed", "task": task}

        agent_factory.register_agent_class("test_type", TestAgent)

        config = AgentConfig(name="test-created-agent", type="test_type", priority=1, skills=[])

        agent = agent_factory.create_agent(config)

        assert agent is not None
        assert agent.config.name == "test-created-agent"


@pytest.mark.unit
@pytest.mark.agents
class TestAgentsDirectory:
    """Agents 目录结构测试"""

    def test_agents_dir_exists(self, agents_dir):
        """测试 Agents 目录存在"""
        assert agents_dir.exists(), f"Agents 目录不存在: {agents_dir}"

    def test_base_agent_exists(self, agents_dir):
        """测试 base_agent.py 存在"""
        base_agent = agents_dir / "base_agent.py"
        assert base_agent.exists(), "base_agent.py 不存在"

    def test_task_agent_exists(self, agents_dir):
        """测试 task_agent.py 存在"""
        task_agent = agents_dir / "task_agent.py"
        assert task_agent.exists(), "task_agent.py 不存在"

    def test_agent_subdirectories(self, agents_dir):
        """测试 Agent 子目录结构"""
        expected_agents = [
            "research_agent",
            "analysis_agent",
            "creative_agent",
        ]

        for agent_name in expected_agents:
            agent_dir = agents_dir / agent_name
            assert agent_dir.exists(), f"Agent 目录不存在: {agent_name}"

            # 检查是否有对应的 .py 文件
            agent_file = agent_dir / f"{agent_name}.py"
            assert agent_file.exists(), f"Agent 文件不存在: {agent_file}"


# ==================== 新增 Agent 测试 ====================


@pytest.mark.unit
@pytest.mark.agents
class TestArchitectAgent:
    """架构师代理测试"""

    def test_architect_agent_exists(self, agents_dir):
        """测试 ArchitectAgent 文件存在"""
        agent_dir = agents_dir / "architect_agent"
        assert agent_dir.exists(), "architect_agent 目录不存在"

    def test_architect_agent_can_handle(self):
        """测试 ArchitectAgent 任务识别"""
        from leo_subagents.agents.architect_agent.architect_agent import ArchitectAgent
        from leo_subagents.agents.base_agent import AgentConfig

        config = AgentConfig(name="test-architect", type="architect", priority=2, skills=[])
        agent = ArchitectAgent(config)
        score = agent.can_handle("设计用户管理系统数据库")
        assert score >= 0.5, "应识别为架构任务"


@pytest.mark.unit
@pytest.mark.agents
class TestMobileAgent:
    """移动开发代理测试"""

    def test_mobile_agent_exists(self, agents_dir):
        """测试 MobileAgent 文件存在"""
        agent_dir = agents_dir / "mobile_agent"
        assert agent_dir.exists(), "mobile_agent 目录不存在"

    def test_mobile_agent_can_handle(self):
        """测试 MobileAgent 任务识别"""
        from leo_subagents.agents.base_agent import AgentConfig
        from leo_subagents.agents.mobile_agent.mobile_agent import MobileAgent

        config = AgentConfig(name="test-mobile", type="mobile", priority=16, skills=[])
        agent = MobileAgent(config)
        score = agent.can_handle("创建微信小程序首页")
        assert score >= 0.5, "应识别为移动开发任务"


@pytest.mark.unit
@pytest.mark.agents
class TestProductManagerAgent:
    """产品经理代理测试"""

    def test_product_manager_agent_exists(self, agents_dir):
        """测试 ProductManagerAgent 文件存在"""
        agent_dir = agents_dir / "product_manager_agent"
        assert agent_dir.exists(), "product_manager_agent 目录不存在"


# ==================== 扩展测试类 ====================


@pytest.mark.unit
@pytest.mark.agents
class TestBaseAgentExtended:
    """BaseAgent 扩展测试"""

    def test_agent_get_available_skills(self):
        """测试获取可用技能列表"""
        from leo_subagents.agents.base_agent import BaseAgent, AgentConfig

        class TestAgent(BaseAgent):
            def can_handle(self, task: str) -> float:
                return 0.5

            def execute(self, task: str, **kwargs):
                return {}

        config = AgentConfig(
            name="test-agent", type="test", priority=1, skills=["skill1", "skill2"]
        )
        agent = TestAgent(config)

        skills = agent.get_available_skills()
        assert skills == ["skill1", "skill2"]

    def test_agent_has_skill(self):
        """测试检查是否拥有特定技能"""
        from leo_subagents.agents.base_agent import BaseAgent, AgentConfig

        class TestAgent(BaseAgent):
            def can_handle(self, task: str) -> float:
                return 0.5

            def execute(self, task: str, **kwargs):
                return {}

        config = AgentConfig(
            name="test-agent", type="test", priority=1, skills=["skill1", "skill2"]
        )
        agent = TestAgent(config)

        assert agent.has_skill("skill1") is True
        assert agent.has_skill("skill3") is False

    def test_agent_log_task(self):
        """测试记录任务执行历史"""
        from leo_subagents.agents.base_agent import BaseAgent, AgentConfig

        class TestAgent(BaseAgent):
            def can_handle(self, task: str) -> float:
                return 0.5

            def execute(self, task: str, **kwargs):
                return {"status": "completed"}

        config = AgentConfig(name="test-agent", type="test", priority=1, skills=[])
        agent = TestAgent(config)

        agent.log_task("test task", {"status": "completed"})
        assert len(agent.task_history) == 1
        assert agent.task_history[0]["task"] == "test task"

    def test_agent_get_status(self):
        """测试获取Agent状态"""
        from leo_subagents.agents.base_agent import BaseAgent, AgentConfig

        class TestAgent(BaseAgent):
            def can_handle(self, task: str) -> float:
                return 0.5

            def execute(self, task: str, **kwargs):
                return {}

        config = AgentConfig(
            name="test-agent",
            type="test",
            priority=1,
            skills=["skill1"],
            enabled=True,
        )
        agent = TestAgent(config)

        status = agent.get_status()
        assert status["name"] == "test-agent"
        assert status["type"] == "test"
        assert status["enabled"] is True
        assert status["priority"] == 1
        assert status["skills"] == ["skill1"]
        assert status["tasks_completed"] == 0

    def test_agent_repr(self):
        """测试Agent字符串表示"""
        from leo_subagents.agents.base_agent import BaseAgent, AgentConfig

        class TestAgent(BaseAgent):
            def can_handle(self, task: str) -> float:
                return 0.5

            def execute(self, task: str, **kwargs):
                return {}

        config = AgentConfig(
            name="test-agent", type="test", priority=1, skills=["skill1", "skill2"]
        )
        agent = TestAgent(config)

        repr_str = repr(agent)
        assert "test-agent" in repr_str
        assert "test" in repr_str


@pytest.mark.unit
@pytest.mark.agents
class TestAgentFactoryExtended:
    """AgentFactory 扩展测试"""

    def test_factory_get_agent_not_found(self):
        """测试获取不存在的Agent"""
        from leo_subagents.agents.base_agent import AgentFactory

        result = AgentFactory.get_agent("non_existent_agent")
        assert result is None

    def test_factory_list_agents(self):
        """测试列出所有Agent"""
        from leo_subagents.agents.base_agent import BaseAgent, AgentConfig, AgentFactory

        class TestAgent(BaseAgent):
            def can_handle(self, task: str) -> float:
                return 0.5

            def execute(self, task: str, **kwargs):
                return {}

        AgentFactory.register_agent_class("test_type_ext", TestAgent)
        config = AgentConfig(
            name="test-agent-ext", type="test_type_ext", priority=1, skills=[]
        )
        AgentFactory.create_agent(config)

        agents = AgentFactory.list_agents()
        assert "test-agent-ext" in agents


@pytest.mark.unit
@pytest.mark.agents
class TestAgentConfigExtended:
    """AgentConfig 扩展测试"""

    def test_config_defaults(self):
        """测试配置默认值的正确性"""
        from leo_subagents.agents.base_agent import AgentConfig

        config = AgentConfig(name="test", type="simple", priority=1, skills=[])
        assert config.description == ""
        assert config.enabled is True
        assert config.max_retries == 3
        assert config.timeout == 300

    def test_config_with_optional_fields(self):
        """测试带可选参数的配置"""
        from leo_subagents.agents.base_agent import AgentConfig

        config = AgentConfig(
            name="test-agent",
            type="executor",
            priority=1,
            skills=["skill1"],
            description="A test agent",
            max_retries=5,
            timeout=600,
        )
        assert config.description == "A test agent"
        assert config.max_retries == 5
        assert config.timeout == 600
