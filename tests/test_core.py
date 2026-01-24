#!/usr/bin/env python3
"""
测试 Leo System Core
"""
import sys
from pathlib import Path
from unittest.mock import Mock, patch


# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestLeoSystemInitialization:
    """测试 LeoSystem 初始化"""

    @patch("leo_system.core.LeoAPI")
    @patch("leo_system.core.SKILL_LOADER_CLASS")
    @patch("leo_system.core.SkillExecutor")
    def test_leo_system_basic_initialization(self, mock_executor, mock_loader, mock_api):
        """测试基本初始化"""
        from leo_system.core import LeoSystem

        # 创建 mock 实例
        mock_api_instance = Mock()
        mock_api.return_value = mock_api_instance

        mock_loader_instance = Mock()
        mock_loader.return_value = mock_loader_instance

        mock_executor_instance = Mock()
        mock_executor.return_value = mock_executor_instance

        # 初始化系统
        system = LeoSystem()

        # 验证初始化
        assert system.base_path is not None
        assert system.api == mock_api_instance
        assert system.skill_loader == mock_loader_instance
        assert system.skill_executor == mock_executor_instance
        assert isinstance(system.agents, dict)

    @patch("leo_system.core.LeoAPI")
    @patch("leo_system.core.SKILL_LOADER_CLASS")
    @patch("leo_system.core.SkillExecutor")
    def test_leo_system_with_custom_base_path(self, mock_executor, mock_loader, mock_api):
        """测试自定义基础路径"""
        from leo_system.core import LeoSystem

        custom_path = Path("/custom/path")
        system = LeoSystem(base_path=custom_path)

        assert system.base_path == custom_path

    @patch("leo_system.core.LeoAPI")
    @patch("leo_system.core.SKILL_LOADER_CLASS")
    @patch("leo_system.core.SkillExecutor")
    def test_leo_system_agents_dict_initialized(self, mock_executor, mock_loader, mock_api):
        """测试 agents 字典初始化"""
        from leo_system.core import LeoSystem

        system = LeoSystem()

        # 验证 agents 字典存在且为空或包含核心 agents
        assert hasattr(system, "agents")
        assert isinstance(system.agents, dict)


class TestLeoSystemPaths:
    """测试 LeoSystem 路径管理"""

    @patch("leo_system.core.LeoAPI")
    @patch("leo_system.core.SKILL_LOADER_CLASS")
    @patch("leo_system.core.SkillExecutor")
    def test_skills_path_construction(self, mock_executor, mock_loader, mock_api):
        """测试技能路径构建"""
        from leo_system.core import LeoSystem

        system = LeoSystem()

        # 验证技能路径
        system.base_path / "leo_skills"

        # 检查 skill_loader 是否使用正确的路径初始化
        mock_loader.assert_called_once()
        call_kwargs = mock_loader.call_args[1]

        # 验证路径参数（可能是 skills_path 或 base_path）
        assert "skills_path" in call_kwargs or "base_path" in call_kwargs


class TestLeoSystemComponents:
    """测试 LeoSystem 组件集成"""

    @patch("leo_system.core.LeoAPI")
    @patch("leo_system.core.SKILL_LOADER_CLASS")
    @patch("leo_system.core.SkillExecutor")
    def test_api_component_integration(self, mock_executor, mock_loader, mock_api):
        """测试 API 组件集成"""
        from leo_system.core import LeoSystem

        mock_api_instance = Mock()
        mock_api.return_value = mock_api_instance

        system = LeoSystem()

        # 验证 API 实例
        assert system.api == mock_api_instance
        mock_api.assert_called_once()

    @patch("leo_system.core.LeoAPI")
    @patch("leo_system.core.SKILL_LOADER_CLASS")
    @patch("leo_system.core.SkillExecutor")
    def test_skill_executor_integration(self, mock_executor, mock_loader, mock_api):
        """测试技能执行器集成"""
        from leo_system.core import LeoSystem

        mock_loader_instance = Mock()
        mock_loader.return_value = mock_loader_instance

        mock_executor_instance = Mock()
        mock_executor.return_value = mock_executor_instance

        system = LeoSystem()

        # 验证 skill_executor 使用 skill_loader 初始化
        assert system.skill_executor == mock_executor_instance
        mock_executor.assert_called_once_with(mock_loader_instance)
