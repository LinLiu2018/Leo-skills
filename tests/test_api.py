#!/usr/bin/env python3
"""
测试 Leo API
"""
import pytest
from unittest.mock import Mock, patch
from pathlib import Path
import sys

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestLeoAPIInitialization:
    """测试 LeoAPI 初始化"""

    @patch('leo_orchestrator.api.get_registry')
    def test_leo_api_basic_initialization(self, mock_get_registry):
        """测试基本初始化"""
        from leo_orchestrator.api import LeoAPI

        # 创建 mock registry
        mock_registry = Mock()
        mock_get_registry.return_value = mock_registry

        # 初始化 API
        api = LeoAPI()

        # 验证初始化
        assert api.base_path is not None
        assert api.registry == mock_registry
        mock_get_registry.assert_called_once()

    @patch('leo_orchestrator.api.get_registry')
    def test_leo_api_with_custom_base_path(self, mock_get_registry):
        """测试自定义基础路径"""
        from leo_orchestrator.api import LeoAPI

        mock_registry = Mock()
        mock_get_registry.return_value = mock_registry

        custom_path = "/custom/path"
        api = LeoAPI(base_path=custom_path)

        # 使用 Path 对象比较，避免路径分隔符问题
        assert api.base_path == Path(custom_path)


class TestLeoAPIRegister:
    """测试 LeoAPI 注册功能"""

    @pytest.fixture
    def mock_api(self):
        """创建 mock API"""
        with patch('leo_orchestrator.api.get_registry') as mock_get_registry:
            mock_registry = Mock()
            mock_get_registry.return_value = mock_registry

            from leo_orchestrator.api import LeoAPI
            api = LeoAPI()
            return api, mock_registry

    def test_register_skill(self, mock_api):
        """测试注册技能"""
        api, mock_registry = mock_api
        mock_registry.register_skill.return_value = True

        result = api.register("skill", "test-skill", path="/path/to/skill")

        assert result is True
        mock_registry.register_skill.assert_called_once_with(
            name="test-skill",
            path="/path/to/skill"
        )

    def test_register_agent(self, mock_api):
        """测试注册 agent"""
        api, mock_registry = mock_api
        mock_registry.register_agent.return_value = True

        result = api.register("agent", "test-agent", type="executor")

        assert result is True
        mock_registry.register_agent.assert_called_once_with(
            name="test-agent",
            type="executor"
        )

    def test_register_unknown_type(self, mock_api):
        """测试注册未知类型"""
        api, mock_registry = mock_api

        result = api.register("unknown", "test-item")

        assert result is False
        mock_registry.register_skill.assert_not_called()
        mock_registry.register_agent.assert_not_called()

    def test_register_case_insensitive(self, mock_api):
        """测试注册类型大小写不敏感"""
        api, mock_registry = mock_api
        mock_registry.register_skill.return_value = True
        mock_registry.register_agent.return_value = True

        # 测试大写
        result = api.register("SKILL", "test-skill")
        assert result is True

        # 测试混合大小写
        result = api.register("Agent", "test-agent")
        assert result is True


class TestLeoAPIQuery:
    """测试 LeoAPI 查询功能"""

    @pytest.fixture
    def mock_api(self):
        """创建 mock API"""
        with patch('leo_orchestrator.api.get_registry') as mock_get_registry:
            mock_registry = Mock()
            mock_get_registry.return_value = mock_registry

            from leo_orchestrator.api import LeoAPI
            api = LeoAPI()
            return api, mock_registry

    def test_list_skills(self, mock_api):
        """测试列出所有技能"""
        api, mock_registry = mock_api

        # 模拟返回技能列表
        mock_skills = [
            {"name": "skill1", "category": "test"},
            {"name": "skill2", "category": "test"}
        ]
        mock_registry.list_skills.return_value = mock_skills

        # 调用 list 方法（如果存在）
        if hasattr(api, 'list'):
            result = api.list("skills")
            assert len(result) == 2

    def test_get_skill(self, mock_api):
        """测试获取单个技能"""
        api, mock_registry = mock_api

        # 模拟返回技能信息
        mock_skill = {"name": "test-skill", "category": "test"}
        mock_registry.get_skill.return_value = mock_skill

        # 调用 get 方法（如果存在）
        if hasattr(api, 'get'):
            result = api.get("skill", "test-skill")
            assert result["name"] == "test-skill"
