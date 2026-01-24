#!/usr/bin/env python3
"""
测试 Workflow Engine
"""
import pytest
import time
from unittest.mock import Mock
from pathlib import Path
import sys

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

        return {
            "agent1": agent1,
            "agent2": agent2
        }

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
                {
                    "name": "step1",
                    "type": "sequential",
                    "agent": "agent1"
                },
                {
                    "name": "step2",
                    "type": "sequential",
                    "agent": "agent2"
                }
            ]
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
        workflow = {
            "name": "context_workflow",
            "steps": [
                {
                    "name": "step1",
                    "agent": "agent1"
                }
            ]
        }

        result = workflow_engine.execute(workflow, initial_data="test_data")

        assert result["success"] is True

    def test_workflow_error_handling(self, workflow_engine, mock_agents):
        """测试工作流错误处理"""
        # 设置 agent1 抛出异常
        mock_agents["agent1"].execute = Mock(side_effect=Exception("Test error"))

        workflow = {
            "name": "error_workflow",
            "steps": [
                {
                    "name": "failing_step",
                    "agent": "agent1"
                }
            ]
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
                {
                    "name": "failing_step",
                    "agent": "agent1"
                },
                {
                    "name": "success_step",
                    "agent": "agent2"
                }
            ]
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
            "steps": [
                {
                    "name": "retry_step",
                    "agent": "agent1",
                    "retries": 2
                }
            ]
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
            "slow_agent": Mock(execute=Mock(side_effect=lambda *args, **kwargs: (time.sleep(2), {"result": "slow"})[1]))
        }

    @pytest.fixture
    def workflow_engine(self, mock_agents):
        """创建工作流引擎实例"""
        return WorkflowEngine(agents=mock_agents, max_workers=2)

    def test_workflow_timeout(self, workflow_engine):
        """测试工作流超时控制"""
        workflow = {
            "name": "timeout_workflow",
            "steps": [
                {
                    "name": "timeout_step",
                    "agent": "slow_agent",
                    "timeout": 1  # 1秒超时
                }
            ]
        }

        result = workflow_engine.execute(workflow)

        # 验证超时错误
        assert result["success"] is False
        assert result["failed_steps"] == 1

    def test_empty_workflow(self, workflow_engine):
        """测试空工作流"""
        workflow = {
            "name": "empty_workflow",
            "steps": []
        }

        result = workflow_engine.execute(workflow)

        assert result["success"] is True
        assert result["total_steps"] == 0

    def test_workflow_execution_history(self, workflow_engine):
        """测试工作流执行历史记录"""
        workflow1 = {
            "name": "workflow1",
            "steps": [{"name": "step1", "agent": "fast_agent"}]
        }

        workflow2 = {
            "name": "workflow2",
            "steps": [{"name": "step1", "agent": "fast_agent"}]
        }

        workflow_engine.execute(workflow1)
        workflow_engine.execute(workflow2)

        # 验证执行历史
        assert len(workflow_engine.execution_history) == 2
        assert workflow_engine.execution_history[0]["workflow"] == "workflow1"
        assert workflow_engine.execution_history[1]["workflow"] == "workflow2"

