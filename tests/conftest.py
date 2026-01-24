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
        skills=["content-layout-leo-cskill"],
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
