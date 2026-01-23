"""
Agents 单元测试
===============
测试所有 Agents 的基础功能
"""

import pytest
from pathlib import Path


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
            name="test-agent",
            type="executor",
            priority=1,
            skills=["skill1", "skill2"]
        )
        
        assert config.name == "test-agent"
        assert config.type == "executor"
        assert config.priority == 1
        assert len(config.skills) == 2
        assert config.enabled == True  # 默认值
    
    def test_agent_factory_register(self, agent_factory):
        """测试 AgentFactory 注册"""
        from leo_subagents.agents.base_agent import BaseAgent, AgentConfig
        
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
        from leo_subagents.agents.base_agent import BaseAgent, AgentConfig
        
        class TestAgent(BaseAgent):
            def can_handle(self, task: str) -> float:
                return 0.5
            
            def execute(self, task: str, **kwargs):
                return {"status": "completed", "task": task}
        
        agent_factory.register_agent_class("test_type", TestAgent)
        
        config = AgentConfig(
            name="test-created-agent",
            type="test_type",
            priority=1,
            skills=[]
        )
        
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
