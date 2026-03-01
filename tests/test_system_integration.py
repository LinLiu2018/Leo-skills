"""
系统集成测试（pytest 兼容）
==========================
验证 Skills、Agents、Workflows 的文件结构和基本导入
"""
import sys
from pathlib import Path
import pytest

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))


@pytest.fixture
def src_dir():
    return PROJECT_ROOT / "src"


class TestAgentStructure:
    """测试 Agent 文件结构完整性"""

    @pytest.mark.parametrize("agent_name", [
        "research_agent",
        "realestate_agent",
        "analysis_agent",
        "creative_agent",
    ])
    def test_agent_files_exist(self, src_dir, agent_name):
        """每个 Agent 应有完整的文件结构"""
        agent_dir = src_dir / "leo_subagents" / "agents" / agent_name
        assert agent_dir.exists(), f"{agent_name} 目录不存在"
        assert (agent_dir / "__init__.py").exists(), f"{agent_name} 缺少 __init__.py"
        assert (agent_dir / f"{agent_name}.py").exists(), f"{agent_name} 缺少主文件"
        assert (agent_dir / "AGENT.md").exists(), f"{agent_name} 缺少 AGENT.md"


class TestWorkflowStructure:
    """测试 Workflow 文件结构"""

    def test_content_pipeline_exists(self, src_dir):
        workflow_dir = src_dir / "leo_workflows" / "workflows" / "content_pipeline"
        assert workflow_dir.exists()
        assert (workflow_dir / "__init__.py").exists()

    def test_workflow_definitions_exist(self, src_dir):
        defs_dir = src_dir / "leo_workflows" / "definitions"
        if not defs_dir.exists():
            pytest.skip("definitions 目录不存在")
        yaml_files = list(defs_dir.glob("*.yaml"))
        assert len(yaml_files) > 0, "应至少有一个工作流定义"


class TestSkillStructure:
    """测试核心 Skill 文件结构"""

    def test_base_skill_importable(self, src_dir):
        """BaseSkill 基类应可导入"""
        from leo_skills.base import BaseSkill, SkillResult
        assert BaseSkill is not None
        assert SkillResult is not None

    def test_skill_result_ok(self):
        """SkillResult.ok() 应返回成功结果"""
        from leo_skills.base import SkillResult
        result = SkillResult.ok(data={"test": True})
        assert result.success is True
        assert result.data == {"test": True}
        assert result.error is None

    def test_skill_result_fail(self):
        """SkillResult.fail() 应返回失败结果"""
        from leo_skills.base import SkillResult
        result = SkillResult.fail("something went wrong")
        assert result.success is False
        assert result.error == "something went wrong"
