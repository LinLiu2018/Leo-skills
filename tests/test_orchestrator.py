"""Leo Orchestrator 单元测试"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest

# 确保项目路径正确
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(SRC_ROOT))


class TestRegistry:
    """测试注册中心"""

    def test_get_registry_singleton(self):
        """测试注册中心单例模式"""
        from leo_orchestrator.registry import get_registry

        registry1 = get_registry()
        registry2 = get_registry()

        assert registry1 is registry2

    def test_register_skill(self):
        """测试注册 Skill"""
        from leo_orchestrator.registry import get_registry

        registry = get_registry()
        result = registry.register_skill(
            name="test-skill",
            path="test/path",
            category="test"
        )

        assert result is True
        assert "test-skill" in registry.skills

        # 清理
        if "test-skill" in registry.skills:
            del registry.skills["test-skill"]

    def test_register_agent(self):
        """测试注册 Agent"""
        from leo_orchestrator.registry import get_registry

        registry = get_registry()
        result = registry.register_agent(
            name="test-agent",
            type="executor",
            priority=1
        )

        assert result is True

        # 清理
        if "test-agent" in registry.agents:
            del registry.agents["test-agent"]

    def test_list_skills(self):
        """测试列出 Skills"""
        from leo_orchestrator.registry import get_registry

        registry = get_registry()
        skills = registry.list_skills()

        assert isinstance(skills, list)

    def test_list_agents(self):
        """测试列出 Agents"""
        from leo_orchestrator.registry import get_registry

        registry = get_registry()
        agents = registry.list_agents()

        assert isinstance(agents, list)


class TestIntentRecognizer:
    """测试意图识别器"""

    def test_intent_recognizer_init(self):
        """测试意图识别器初始化"""
        from leo_orchestrator.intent_recognizer import IntentRecognizer

        recognizer = IntentRecognizer()
        assert recognizer is not None

    @patch('leo_orchestrator.intent_recognizer.get_leo_api')
    def test_recognize_intent(self, mock_get_api):
        """测试意图识别"""
        from leo_orchestrator.intent_recognizer import IntentRecognizer

        # Mock API
        mock_api = MagicMock()
        mock_api.run_agent.return_value = {"intent": "research", "confidence": 0.9}
        mock_get_api.return_value = mock_api

        recognizer = IntentRecognizer()
        result = recognizer.recognize("分析房地产市场趋势")

        assert result is not None


class TestWorkflowEngine:
    """测试工作流引擎"""

    def test_workflow_engine_init(self):
        """测试工作流引擎初始化"""
        from leo_orchestrator.workflow_engine import WorkflowEngine

        engine = WorkflowEngine(agents={})
        assert engine is not None
        assert engine.agents == {}

    def test_execute_workflow_with_mock(self):
        """测试执行工作流（使用 Mock）"""
        from leo_orchestrator.workflow_engine import WorkflowEngine

        # Mock agents
        mock_agent = MagicMock()
        mock_agent.execute.return_value = {"result": "success"}

        engine = WorkflowEngine(agents={"test-agent": mock_agent})

        # Mock workflow
        mock_workflow = MagicMock()
        mock_workflow.steps = [
            {"agent": "test-agent", "action": "execute"}
        ]

        result = engine.execute(mock_workflow, test_param="value")

        assert result is not None


class TestLeoAPI:
    """测试 Leo API"""

    def test_leo_api_init(self):
        """测试 LeoAPI 初始化"""
        from leo_orchestrator.api import LeoAPI

        api = LeoAPI(base_path=str(PROJECT_ROOT))
        assert api is not None
        assert api.base_path == PROJECT_ROOT

    def test_leo_api_list_skills(self):
        """测试列出 Skills"""
        from leo_orchestrator.api import LeoAPI

        api = LeoAPI(base_path=str(PROJECT_ROOT))
        skills = api.list("skills")

        assert isinstance(skills, list)

    def test_leo_api_list_agents(self):
        """测试列出 Agents"""
        from leo_orchestrator.api import LeoAPI

        api = LeoAPI(base_path=str(PROJECT_ROOT))
        agents = api.list("agents")

        assert isinstance(agents, list)

    def test_leo_api_summary(self):
        """测试获取摘要"""
        from leo_orchestrator.api import LeoAPI

        api = LeoAPI(base_path=str(PROJECT_ROOT))
        summary = api.summary()

        assert isinstance(summary, dict)
        assert "skills" in summary
        assert "agents" in summary
        assert "workflows" in summary


class TestWingmanPipeline:
    """测试僚机流水线"""

    def test_wingman_pipeline_init(self):
        """测试僚机流水线初始化"""
        from leo_orchestrator.wingman_pipeline import WingmanPipeline

        pipeline = WingmanPipeline()
        assert pipeline is not None


class TestSkillRegistration:
    """测试 Skill 注册"""

    def test_skill_registration_model(self):
        """测试 Skill 注册模型"""
        from leo_orchestrator.registry import SkillRegistration

        registration = SkillRegistration(
            name="test-skill",
            path="test/path",
            category="test-category",
            enabled=True
        )

        assert registration.name == "test-skill"
        assert registration.category == "test-category"
        assert registration.enabled is True


class TestAgentRegistration:
    """测试 Agent 注册"""

    def test_agent_registration_model(self):
        """测试 Agent 注册模型"""
        from leo_orchestrator.registry import AgentRegistration

        registration = AgentRegistration(
            name="test-agent",
            type="executor",
            priority=1,
            enabled=True
        )

        assert registration.name == "test-agent"
        assert registration.type == "executor"
        assert registration.priority == 1
        assert registration.enabled is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
