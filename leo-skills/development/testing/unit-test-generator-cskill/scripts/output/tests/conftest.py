"""
Pytest配置文件
"""
import pytest


@pytest.fixture
def sample_data():
    """示例数据fixture"""
    return {
        'id': 1,
        'name': 'test'
    }


@pytest.fixture
def mock_db(mocker):
    """Mock数据库"""
    return mocker.MagicMock()
