"""
Leo System 测试配置
==================
pytest 的共享 fixtures 和配置
"""

import sys
from pathlib import Path

import pytest

# 确保项目根目录和 src 目录在 Python 路径中
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(SRC_ROOT))


# ==================== Fixtures ====================


@pytest.fixture(scope="session")
def project_root() -> Path:
    """项目根目录"""
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def skills_dir(project_root: Path) -> Path:
    """Skills 目录（src/布局）"""
    return project_root / "src" / "leo_skills"


@pytest.fixture(scope="session")
def agents_dir(project_root: Path) -> Path:
    """Agents 目录（src/布局）"""
    return project_root / "src" / "leo_subagents" / "agents"


@pytest.fixture(scope="module")
def skill_loader():
    """SkillLoader 实例"""
    from leo_subagents.skills_bridge.skill_loader import SkillLoader

    loader = SkillLoader()
    loader.discover_and_load()
    return loader


@pytest.fixture(scope="module")
def skill_executor(skill_loader):
    """SkillExecutor 实例"""
    from leo_subagents.skills_bridge.skill_executor import SkillExecutor

    return SkillExecutor(skill_loader)


@pytest.fixture(scope="module")
def agent_factory():
    """AgentFactory 类"""
    from leo_subagents.agents.base_agent import AgentFactory

    return AgentFactory


@pytest.fixture(scope="module")
def agent_config():
    """测试用 AgentConfig"""
    from leo_subagents.agents.base_agent import AgentConfig

    return AgentConfig(
        name="test-agent",
        type="executor",
        priority=1,
        skills=["content_layout_leo_skill"],
        description="Test Agent",
    )


@pytest.fixture(scope="function")
def temp_output_dir(tmp_path: Path) -> Path:
    """临时输出目录"""
    output_dir = tmp_path / "test_output"
    output_dir.mkdir(exist_ok=True)
    return output_dir


# ==================== 标记 ====================


def pytest_configure(config):
    """配置自定义标记"""
    config.addinivalue_line("markers", "slow: 标记为慢速测试（需要较长时间运行）")
    config.addinivalue_line("markers", "integration: 标记为集成测试（需要外部依赖）")
    config.addinivalue_line("markers", "unit: 标记为单元测试")
    config.addinivalue_line("markers", "skills: Skills 相关测试")
    config.addinivalue_line("markers", "agents: Agents 相关测试")
    config.addinivalue_line("markers", "mcp: MCP 相关测试")
    config.addinivalue_line("markers", "core: 核心模块测试")


# ==================== 新增: Leo Core 测试 Fixtures ====================

@pytest.fixture
def sample_agent_request():
    """标准 Agent 请求"""
    from leo_core.types import BaseRequest
    return BaseRequest(
        input="测试输入",
        context={"user_id": "test_user"},
        parameters={"depth": "detailed"}
    )


@pytest.fixture
def sample_agent_response():
    """标准 Agent 响应"""
    from leo_core.types import BaseResponse, Status
    return BaseResponse(
        output="测试输出",
        status=Status.SUCCESS,
        metadata={"execution_time": 0.5}
    )


@pytest.fixture
def mock_llm_response():
    """Mock LLM 响应"""
    return {
        "choices": [{
            "message": {
                "content": "Test response from LLM"
            }
        }]
    }


@pytest.fixture
def sample_agent_context():
    """标准 Agent 上下文"""
    return {
        "user_id": "test_user",
        "session_id": "test_session",
        "conversation_history": []
    }


@pytest.fixture
def sample_memory_entry():
    """标准记忆条目"""
    from leo_core.types import MemoryEntry
    return MemoryEntry(
        id="test_memory_1",
        content="这是一个测试记忆",
        type="general",
        tags=["test", "sample"],
        user_id="test_user"
    )


@pytest.fixture
def sample_event():
    """标准事件"""
    from leo_core.types import Event
    from datetime import datetime
    return Event(
        type="test.event",
        payload={"data": "test"},
        source="test_source",
        timestamp=datetime.now()
    )


@pytest.fixture
def event_loop():
    """事件循环 fixture (用于异步测试)"""
    import asyncio
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
async def reset_context():
    """每个测试后重置上下文"""
    yield
    # 清理逻辑可以在此添加
