#!/usr/bin/env python3
"""
测试 Workflow Engine
"""
import sys
import time
from pathlib import Path
from unittest.mock import Mock

import pytest

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from leo_orchestrator.workflow_engine import WorkflowEngine


class TestWorkflowEngine:
    """测试工作流引擎"""

    @pytest.fixture
    def mock_agents(self):
        """创建 mock agents"""
        agent1 = Mock()
        agent1.execute = Mock(return_value={"result": "agent1_result"})

        agent2 = Mock()
        agent2.execute = Mock(return_value={"result": "agent2_result"})

        return {"agent1": agent1, "agent2": agent2}

    @pytest.fixture
    def workflow_engine(self, mock_agents):
        """创建工作流引擎实例"""
        return WorkflowEngine(agents=mock_agents, max_workers=2)

    def test_workflow_engine_initialization(self, mock_agents):
        """测试工作流引擎初始化"""
        engine = WorkflowEngine(agents=mock_agents, max_workers=4)

        assert engine.agents == mock_agents
        assert engine.max_workers == 4
        assert engine.execution_history == []

    def test_simple_sequential_workflow(self, workflow_engine, mock_agents):
        """测试简单的顺序工作流"""
        workflow = {
            "name": "test_workflow",
            "description": "测试工作流",
            "steps": [
                {"name": "step1", "type": "sequential", "agent": "agent1"},
                {"name": "step2", "type": "sequential", "agent": "agent2"},
            ],
        }

        result = workflow_engine.execute(workflow)

        # 验证结果
        assert result["success"] is True
        assert result["workflow"] == "test_workflow"
        assert result["total_steps"] == 2
        assert result["successful_steps"] == 2
        assert result["failed_steps"] == 0

        # 验证执行历史
        assert len(workflow_engine.execution_history) == 1

    def test_workflow_with_initial_context(self, workflow_engine):
        """测试带初始上下文的工作流"""
        workflow = {"name": "context_workflow", "steps": [{"name": "step1", "agent": "agent1"}]}

        result = workflow_engine.execute(workflow, initial_data="test_data")

        assert result["success"] is True

    def test_workflow_error_handling(self, workflow_engine, mock_agents):
        """测试工作流错误处理"""
        # 设置 agent1 抛出异常
        mock_agents["agent1"].execute = Mock(side_effect=Exception("Test error"))

        workflow = {
            "name": "error_workflow",
            "steps": [{"name": "failing_step", "agent": "agent1"}],
        }

        result = workflow_engine.execute(workflow)

        # 验证错误被捕获
        assert result["success"] is False
        assert result["total_steps"] == 1
        assert result["successful_steps"] == 0
        assert result["failed_steps"] == 1

    def test_workflow_continue_on_error(self, workflow_engine, mock_agents):
        """测试工作流在错误时继续执行"""
        # 设置 agent1 抛出异常
        mock_agents["agent1"].execute = Mock(side_effect=Exception("Test error"))

        workflow = {
            "name": "continue_workflow",
            "continue_on_error": True,
            "steps": [
                {"name": "failing_step", "agent": "agent1"},
                {"name": "success_step", "agent": "agent2"},
            ],
        }

        result = workflow_engine.execute(workflow)

        # 验证两个步骤都执行了
        assert result["total_steps"] == 2
        assert result["successful_steps"] == 1
        assert result["failed_steps"] == 1

    def test_workflow_with_retry(self, workflow_engine, mock_agents):
        """测试工作流重试机制"""
        # 设置 agent1 第一次失败，第二次成功
        mock_agents["agent1"].execute = Mock(
            side_effect=[Exception("First attempt"), {"result": "success"}]
        )

        workflow = {
            "name": "retry_workflow",
            "steps": [{"name": "retry_step", "agent": "agent1", "retries": 2}],
        }

        result = workflow_engine.execute(workflow)

        # 验证重试成功
        assert result["success"] is True
        assert mock_agents["agent1"].execute.call_count == 2


class TestWorkflowEngineAdvanced:
    """测试工作流引擎高级功能"""

    @pytest.fixture
    def mock_agents(self):
        """创建 mock agents"""
        return {
            "fast_agent": Mock(execute=Mock(return_value={"result": "fast"})),
            "slow_agent": Mock(
                execute=Mock(
                    side_effect=lambda *args, **kwargs: (time.sleep(2), {"result": "slow"})[1]
                )
            ),
        }

    @pytest.fixture
    def workflow_engine(self, mock_agents):
        """创建工作流引擎实例"""
        return WorkflowEngine(agents=mock_agents, max_workers=2)

    def test_workflow_timeout(self, workflow_engine):
        """测试工作流超时控制"""
        workflow = {
            "name": "timeout_workflow",
            "steps": [{"name": "timeout_step", "agent": "slow_agent", "timeout": 1}],  # 1秒超时
        }

        result = workflow_engine.execute(workflow)

        # 验证超时错误
        assert result["success"] is False
        assert result["failed_steps"] == 1

    def test_empty_workflow(self, workflow_engine):
        """测试空工作流"""
        workflow = {"name": "empty_workflow", "steps": []}

        result = workflow_engine.execute(workflow)

        assert result["success"] is True
        assert result["total_steps"] == 0

    def test_workflow_execution_history(self, workflow_engine):
        """测试工作流执行历史记录"""
        workflow1 = {"name": "workflow1", "steps": [{"name": "step1", "agent": "fast_agent"}]}

        workflow2 = {"name": "workflow2", "steps": [{"name": "step1", "agent": "fast_agent"}]}

        workflow_engine.execute(workflow1)
        workflow_engine.execute(workflow2)

        # 验证执行历史
        assert len(workflow_engine.execution_history) == 2
        assert workflow_engine.execution_history[0]["workflow"] == "workflow1"
        assert workflow_engine.execution_history[1]["workflow"] == "workflow2"


class TestWorkflowEdgeCases:
    """工作流边缘情况测试"""

    @pytest.fixture
    def mock_agents(self):
        """创建 mock agents"""
        return {
            "agent1": Mock(execute=Mock(return_value={"result": "agent1"})),
            "agent2": Mock(execute=Mock(return_value={"result": "agent2"})),
        }

    def test_workflow_nonexistent_agent(self, mock_agents):
        """测试不存在的agent处理"""
        engine = WorkflowEngine(agents=mock_agents)

        workflow = {
            "name": "nonexistent_agent_workflow",
            "steps": [{"name": "step1", "agent": "nonexistent_agent"}],
        }

        result = engine.execute(workflow)

        assert result["success"] is False
        assert result["failed_steps"] == 1

    def test_workflow_missing_agent_field(self, mock_agents):
        """测试缺少agent字段的处理"""
        engine = WorkflowEngine(agents=mock_agents)

        workflow = {
            "name": "missing_agent_workflow",
            "steps": [{"name": "step1"}],  # 缺少agent字段
        }

        result = engine.execute(workflow)

        assert result["success"] is False
        assert result["failed_steps"] == 1

    def test_workflow_parallel_execution(self, mock_agents):
        """测试并行执行"""
        engine = WorkflowEngine(agents=mock_agents, max_workers=4)

        workflow = {
            "name": "parallel_workflow",
            "steps": [
                {"name": "step1", "type": "parallel", "agents": ["agent1", "agent2"]},
            ],
        }

        result = engine.execute(workflow)

        assert result["success"] is True

    def test_workflow_conditional_branch(self, mock_agents):
        """测试条件分支"""
        engine = WorkflowEngine(agents=mock_agents)

        # 模拟条件为true的情况
        mock_agents["agent1"].execute = Mock(return_value={"condition": True})

        workflow = {
            "name": "conditional_workflow",
            "steps": [
                {"name": "step1", "agent": "agent1"},
                {
                    "name": "step2",
                    "type": "conditional",
                    "condition": "${step1.condition}",
                    "then": "step3",
                    "else": "step4",
                },
            ],
        }

        result = engine.execute(workflow)

        assert result["success"] is True

    def test_workflow_context_passing(self, mock_agents):
        """测试上下文传递"""
        engine = WorkflowEngine(agents=mock_agents)

        workflow = {
            "name": "context_workflow",
            "steps": [
                {"name": "step1", "agent": "agent1"},
                {"name": "step2", "agent": "agent2"},
            ],
        }

        result = engine.execute(workflow, initial_data={"key": "value"})

        assert result["success"] is True
        assert "context" in result


class TestUnifiedRegistry:
    """统一注册表测试"""

    def test_registry_initialization(self):
        """测试注册表初始化"""
        from leo_orchestrator.registry import UnifiedRegistry

        registry = UnifiedRegistry()
        assert isinstance(registry.skills, dict)
        assert isinstance(registry.agents, dict)
        assert isinstance(registry.workflows, dict)

    def test_register_skill(self):
        """测试注册Skill"""
        from leo_orchestrator.registry import UnifiedRegistry

        registry = UnifiedRegistry()

        result = registry.register_skill(
            name="test-skill",
            path="leo_skills/test/test-skill",
            category="testing",
        )

        assert result is True
        assert "test-skill" in registry.skills

    def test_register_duplicate_skill(self):
        """测试重复注册Skill"""
        from leo_orchestrator.registry import UnifiedRegistry

        registry = UnifiedRegistry()

        registry.register_skill(
            name="duplicate-skill",
            path="path1",
            category="test",
        )

        result = registry.register_skill(
            name="duplicate-skill",
            path="path2",
            category="test",
        )

        assert result is False

    def test_unregister_skill(self):
        """测试注销Skill"""
        from leo_orchestrator.registry import UnifiedRegistry

        registry = UnifiedRegistry()

        registry.register_skill(name="remove-skill", path="path", category="test")
        result = registry.unregister_skill("remove-skill")

        assert result is True
        assert "remove-skill" not in registry.skills

    def test_unregister_nonexistent_skill(self):
        """测试注销不存在的Skill"""
        from leo_orchestrator.registry import UnifiedRegistry

        registry = UnifiedRegistry()

        result = registry.unregister_skill("nonexistent")

        assert result is False

    def test_get_skill(self):
        """测试获取Skill"""
        from leo_orchestrator.registry import UnifiedRegistry

        registry = UnifiedRegistry()

        registry.register_skill(name="get-skill", path="path", category="test")
        skill = registry.get_skill("get-skill")

        assert skill is not None
        assert skill.name == "get-skill"

    def test_get_skill_not_found(self):
        """测试获取不存在的Skill"""
        from leo_orchestrator.registry import UnifiedRegistry

        registry = UnifiedRegistry()

        skill = registry.get_skill("nonexistent")

        assert skill is None

    def test_list_skills(self):
        """测试列出Skills"""
        from leo_orchestrator.registry import UnifiedRegistry

        registry = UnifiedRegistry()

        registry.register_skill(name="skill1", path="path1", category="cat1")
        registry.register_skill(name="skill2", path="path2", category="cat2")

        skills = registry.list_skills()

        assert len(skills) >= 2

    def test_list_skills_by_category(self):
        """测试按分类列出Skills"""
        from leo_orchestrator.registry import UnifiedRegistry

        registry = UnifiedRegistry()

        registry.register_skill(name="skill1", path="path1", category="content")
        registry.register_skill(name="skill2", path="path2", category="content")
        registry.register_skill(name="skill3", path="path3", category="development")

        content_skills = registry.list_skills(category="content")

        assert len(content_skills) >= 2

    def test_enable_disable_skill(self):
        """测试启用/禁用Skill"""
        from leo_orchestrator.registry import UnifiedRegistry

        registry = UnifiedRegistry()

        registry.register_skill(name="toggle-skill", path="path", category="test")

        assert registry.skills["toggle-skill"].enabled is True

        registry.disable_skill("toggle-skill")
        assert registry.skills["toggle-skill"].enabled is False

        registry.enable_skill("toggle-skill")
        assert registry.skills["toggle-skill"].enabled is True

    def test_register_agent(self):
        """测试注册Agent"""
        from leo_orchestrator.registry import UnifiedRegistry

        registry = UnifiedRegistry()

        # Use a unique name to avoid conflict with existing agents
        result = registry.register_agent(
            name="test-agent-unique-12345",
            type="executor",
            priority=99,
            skills=["skill1"],
        )

        assert result is True
        assert "test-agent-unique-12345" in registry.agents

    def test_register_workflow(self):
        """测试注册Workflow"""
        from leo_orchestrator.registry import UnifiedRegistry

        registry = UnifiedRegistry()

        workflow = {"name": "test-workflow", "steps": []}
        result = registry.register_workflow("test-workflow", workflow)

        assert result is True
        assert "test-workflow" in registry.workflows

    def test_list_workflows(self):
        """测试列出Workflows"""
        from leo_orchestrator.registry import UnifiedRegistry

        registry = UnifiedRegistry()

        registry.register_workflow("wf1", {})
        registry.register_workflow("wf2", {})

        workflows = registry.list_workflows()

        assert "wf1" in workflows
        assert "wf2" in workflows
