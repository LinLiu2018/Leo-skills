"""
模块化上下文测试（pytest 兼容）
==============================
测试 Agent 的上下文加载机制
"""
import sys
from pathlib import Path
import pytest

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))


class TestModularContext:
    """测试模块化上下文加载"""

    def test_agent_config_creation(self):
        """AgentConfig 应能正常创建"""
        from leo_subagents.agents.base_agent import AgentConfig
        config = AgentConfig(
            name="test-agent",
            type="researcher",
            priority=1,
            skills=["research_assistant_skill"],
            description="Test Agent",
        )
        assert config.name == "test-agent"
        assert config.type == "researcher"

    def test_product_manager_agent_exists(self):
        """ProductManagerAgent 文件应存在"""
        agent_file = (
            project_root / "src" / "leo_subagents" / "agents"
            / "product_manager_agent" / "product_manager_agent.py"
        )
        assert agent_file.exists(), "ProductManagerAgent 文件不存在"

    def test_knowledge_templates_exist(self):
        """知识库模板文件应存在"""
        templates_dir = project_root / "leo_knowledge" / "templates"
        assert templates_dir.exists(), "templates 目录不存在"
        prd_template = templates_dir / "prd_template.md"
        assert prd_template.exists(), "PRD 模板不存在"
