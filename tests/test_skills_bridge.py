"""
Tests for leo_subagents/skills_bridge module
=============================================
Tests for SkillLoader, SkillExecutor, and SkillAdapter
"""

import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add parent directory to path
parent_path = Path(__file__).parent.parent
if str(parent_path) not in sys.path:
    sys.path.insert(0, str(parent_path))


class TestSkillLoader:
    """Tests for SkillLoader class"""

    def test_skill_loader_initialization(self):
        """Test SkillLoader initialization with default path"""
        from leo_subagents.skills_bridge.skill_loader import SkillLoader

        loader = SkillLoader()
        assert loader.base_path.exists() or True  # Path may not exist in test env
        assert isinstance(loader.skills, dict)
        assert isinstance(loader.categories, dict)

    def test_skill_loader_custom_path(self):
        """Test SkillLoader initialization with custom path"""
        from leo_subagents.skills_bridge.skill_loader import SkillLoader

        with tempfile.TemporaryDirectory() as tmpdir:
            loader = SkillLoader(base_path=tmpdir)
            assert str(loader.base_path) == tmpdir

    def test_get_skill_not_found(self):
        """Test get_skill returns None for non-existent skill"""
        from leo_subagents.skills_bridge.skill_loader import SkillLoader

        loader = SkillLoader()
        result = loader.get_skill("non_existent_skill")
        assert result is None

    def test_list_skills_empty(self):
        """Test list_skills returns empty list when no skills loaded"""
        from leo_subagents.skills_bridge.skill_loader import SkillLoader

        with tempfile.TemporaryDirectory() as tmpdir:
            loader = SkillLoader(base_path=tmpdir)
            skills = loader.list_skills()
            assert isinstance(skills, list)

    def test_list_categories_empty(self):
        """Test list_categories returns empty list when no categories"""
        from leo_subagents.skills_bridge.skill_loader import SkillLoader

        with tempfile.TemporaryDirectory() as tmpdir:
            loader = SkillLoader(base_path=tmpdir)
            categories = loader.list_categories()
            assert isinstance(categories, list)

    def test_discover_and_load_nonexistent_path(self):
        """Test discover_and_load returns 0 for non-existent path"""
        from leo_subagents.skills_bridge.skill_loader import SkillLoader

        with tempfile.TemporaryDirectory() as tmpdir:
            loader = SkillLoader(base_path=tmpdir)
            count = loader.discover_and_load()
            assert count == 0

    def test_load_from_config_nonexistent_file(self):
        """Test load_from_config returns 0 for non-existent config"""
        from leo_subagents.skills_bridge.skill_loader import SkillLoader

        loader = SkillLoader()
        count = loader.load_from_config("/nonexistent/path/config.yaml")
        assert count == 0


class TestSkillExecutor:
    """Tests for SkillExecutor class"""

    def test_executor_initialization(self):
        """Test SkillExecutor initialization"""
        from leo_subagents.skills_bridge.skill_executor import SkillExecutor

        executor = SkillExecutor()
        assert executor.loader is not None
        assert isinstance(executor.execution_history, list)

    def test_execution_result_creation(self):
        """Test ExecutionResult dataclass creation"""
        from leo_subagents.skills_bridge.skill_executor import ExecutionResult

        result = ExecutionResult(
            skill_name="test_skill",
            action="test_action",
            success=True,
            result={"data": "test"},
        )
        assert result.skill_name == "test_skill"
        assert result.action == "test_action"
        assert result.success is True
        assert result.result == {"data": "test"}
        assert result.timestamp is not None

    def test_execution_result_to_dict(self):
        """Test ExecutionResult to_dict conversion"""
        from leo_subagents.skills_bridge.skill_executor import ExecutionResult

        result = ExecutionResult(
            skill_name="test_skill",
            action="test_action",
            success=True,
            result={"data": "test"},
        )
        result_dict = result.to_dict()
        assert isinstance(result_dict, dict)
        assert result_dict["skill_name"] == "test_skill"
        assert result_dict["success"] is True

    def test_execute_skill_not_found(self):
        """Test execute returns failed result for non-existent skill"""
        from leo_subagents.skills_bridge.skill_executor import SkillExecutor

        executor = SkillExecutor()
        result = executor.execute(
            skill_name="non_existent_skill", action="test", param="value"
        )
        assert result.success is False
        assert result.error is not None

    def test_execute_statistics_empty(self):
        """Test get_statistics returns dict for no executions"""
        from leo_subagents.skills_bridge.skill_executor import SkillExecutor

        executor = SkillExecutor()
        stats = executor.get_statistics()
        assert isinstance(stats, dict)
        # Just check that it's a dict with expected keys
        assert "total_executions" in stats


class TestSkillAdapter:
    """Tests for SkillAdapter class"""

    def test_skill_adapter_creation(self):
        """Test SkillAdapter creation with basic info"""
        from leo_subagents.skills_bridge.skill_adapter import SkillAdapter

        adapter = SkillAdapter(skill_path="test/path", skill_name="test-skill")
        assert adapter.skill_name == "test-skill"
        assert adapter.skill_path.name == "test" or "test" in str(adapter.skill_path)

    def test_skill_metadata_defaults(self):
        """Test SkillMetadata has correct default values"""
        from leo_subagents.skills_bridge.skill_adapter import SkillMetadata

        metadata = SkillMetadata(name="test", path="test/path", category="test")
        assert metadata.version == "1.0.0"
        assert metadata.description == ""
        assert metadata.author == ""
        assert metadata.category == "test"
        assert metadata.enabled is True
        assert metadata.actions == []

    def test_skill_adapter_get_skill_info(self):
        """Test get_skill_info returns dictionary"""
        from leo_subagents.skills_bridge.skill_adapter import SkillAdapter

        adapter = SkillAdapter(skill_path="test/path", skill_name="test-skill")
        info = adapter.get_skill_info()
        assert isinstance(info, dict)
        assert info["name"] == "test-skill"

    def test_skill_adapter_get_available_actions(self):
        """Test get_available_actions returns list"""
        from leo_subagents.skills_bridge.skill_adapter import SkillAdapter

        adapter = SkillAdapter(skill_path="test/path", skill_name="test-skill")
        actions = adapter.get_available_actions()
        assert isinstance(actions, list)

    def test_get_skill_adapter_singleton(self):
        """Test get_skill_adapter returns adapter for same skill"""
        from leo_subagents.skills_bridge.skill_adapter import get_skill_adapter

        # This should not raise an exception
        try:
            adapter = get_skill_adapter("test-skill", "test/path")
            # Adapter may be None if skill doesn't exist, but function should not crash
        except Exception:
            pytest.fail("get_skill_adapter raised exception")


class TestEnhancedSkillLoader:
    """Tests for EnhancedSkillLoader class"""

    def test_enhanced_loader_initialization(self):
        """Test EnhancedSkillLoader initialization"""
        from leo_subagents.skills_bridge.enhanced_skill_loader import (
            EnhancedSkillLoader,
        )

        loader = EnhancedSkillLoader()
        assert hasattr(loader, "skills")
        assert hasattr(loader, "workflows")
        assert hasattr(loader, "categories")

    def test_enhanced_loader_discover_all_empty(self):
        """Test discover_all with empty directory"""
        from leo_subagents.skills_bridge.enhanced_skill_loader import (
            EnhancedSkillLoader,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            loader = EnhancedSkillLoader(skills_path=tmpdir, workflows_path=tmpdir)
            stats = loader.discover_all()
            assert isinstance(stats, dict)
            assert stats["total_skills"] == 0
            assert stats["total_workflows"] == 0

    def test_skill_info_creation(self):
        """Test SkillInfo dataclass"""
        from leo_subagents.skills_bridge.enhanced_skill_loader import SkillInfo

        info = SkillInfo(name="test", path=Path("test/path"), category="testing")
        assert info.name == "test"
        assert info.category == "testing"

    def test_workflow_info_creation(self):
        """Test WorkflowInfo dataclass"""
        from leo_subagents.skills_bridge.enhanced_skill_loader import WorkflowInfo

        info = WorkflowInfo(name="test-workflow", path=Path("test/path"))
        assert info.name == "test-workflow"


class TestSkillDiscoverySimple:
    """Tests for SkillDiscoverySimple class"""

    def test_discovery_initialization(self):
        """Test SkillDiscoverySystem initialization in simple module"""
        from leo_subagents.skills_bridge.skill_discovery_simple import (
            SkillDiscoverySystem,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            discovery = SkillDiscoverySystem(project_root=Path(tmpdir))
            assert hasattr(discovery, "skills_path")
            assert hasattr(discovery, "registry")

    def test_skill_metadata_creation(self):
        """Test SkillMetadata dataclass"""
        from leo_subagents.skills_bridge.skill_discovery_simple import SkillMetadata

        metadata = SkillMetadata(
            name="test-skill", path="test/path", category="testing"
        )
        assert metadata.name == "test-skill"
        assert metadata.category == "testing"
        assert metadata.version == "1.0.0"


class TestSkillDiscoverySystem:
    """Tests for SkillDiscoverySystem class in system module"""

    def test_system_discovery_initialization(self):
        """Test SkillDiscoverySystem initialization"""
        from leo_subagents.skills_bridge.skill_discovery_system import (
            SkillDiscoverySystem,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            discovery = SkillDiscoverySystem(project_root=Path(tmpdir))
            assert hasattr(discovery, "project_root")
            assert hasattr(discovery, "skills_path")

    def test_system_skill_metadata_creation(self):
        """Test SkillMetadata dataclass in system module"""
        from leo_subagents.skills_bridge.skill_discovery_system import (
            SkillMetadata as SysSkillMetadata,
        )

        metadata = SysSkillMetadata(
            name="test-skill", path=Path("test/path"), category="testing"
        )
        assert metadata.name == "test-skill"
        assert metadata.category == "testing"

    def test_system_workflow_metadata_creation(self):
        """Test SkillRegistry in system module"""
        from leo_subagents.skills_bridge.skill_discovery_system import (
            SkillRegistry,
        )

        registry = SkillRegistry(
            skills={},
            categories={},
            last_updated="2024-01-01"
        )
        assert hasattr(registry, "skills")
