"""
项目路径常量
集中管理所有文件和目录路径，避免硬编码路径导致的问题
"""
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.resolve()

# 核心目录
LEO_SKILLS = PROJECT_ROOT / "leo_skills"
LEO_SUBAGENTS = PROJECT_ROOT / "leo_subagents"
LEO_WORKFLOWS = PROJECT_ROOT / "leo_workflows"
LEO_ORCHESTRATOR = PROJECT_ROOT / "leo_orchestrator"
LEO_KNOWLEDGE = PROJECT_ROOT / "leo_knowledge"
LEO_INTERFACE = PROJECT_ROOT / "leo_interface"
LEO_CONFIG = PROJECT_ROOT / "leo_config"
LEO_SYSTEM = PROJECT_ROOT / "leo_system"

# 主要文件
LEO_SYSTEM_PY = PROJECT_ROOT / "leo_system.py"  # 注意：使用下划线
CLAUDE_MD = PROJECT_ROOT / "CLAUDE.md"
README_MD = PROJECT_ROOT / "README.md"

# 文档目录
DOCS_DIR = PROJECT_ROOT / "docs"
DOCS_GUIDES = DOCS_DIR / "guides"
DOCS_REFERENCE = DOCS_DIR / "reference"
DOCS_PLANNING = DOCS_DIR / "planning"

# 脚本目录
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
CLEANUP_SCRIPT = SCRIPTS_DIR / "cleanup_skills.py"
VALIDATE_SCRIPT = SCRIPTS_DIR / "validate_structure.py"

# 测试目录
TESTS_DIR = PROJECT_ROOT / "tests"

# 归档目录
ARCHIVE_DIR = PROJECT_ROOT / "archive"

# 知识库上下文
CONTEXT_DIR = LEO_KNOWLEDGE / "context"
USER_PROFILE = CONTEXT_DIR / "user_profile.md"
SYSTEM_ARCHITECTURE = CONTEXT_DIR / "system_architecture.md"
CAPABILITY_INDEX = CONTEXT_DIR / "capability_index.md"
PROJECT_STRUCTURE = CONTEXT_DIR / "project_structure.md"


def validate_paths():
    """验证关键路径是否存在"""
    critical_paths = [
        PROJECT_ROOT,
        LEO_SKILLS,
        LEO_SYSTEM_PY,
        CLAUDE_MD,
        SCRIPTS_DIR,
    ]

    missing = []
    for path in critical_paths:
        if not path.exists():
            missing.append(str(path))

    if missing:
        raise FileNotFoundError(
            f"关键路径不存在:\n" + "\n".join(f"  - {p}" for p in missing)
        )

    return True


# 在导入时验证路径
if __name__ != "__main__":
    try:
        validate_paths()
    except FileNotFoundError as e:
        print(f"警告: {e}")


if __name__ == "__main__":
    # 测试模式：打印所有路径
    print("项目路径配置:")
    print("=" * 60)
    print(f"项目根目录: {PROJECT_ROOT}")
    print(f"\n核心目录:")
    print(f"  - leo_skills: {LEO_SKILLS}")
    print(f"  - leo_subagents: {LEO_SUBAGENTS}")
    print(f"  - leo_workflows: {LEO_WORKFLOWS}")
    print(f"  - leo_orchestrator: {LEO_ORCHESTRATOR}")
    print(f"\n主要文件:")
    print(f"  - leo_system.py: {LEO_SYSTEM_PY}")
    print(f"  - CLAUDE.md: {CLAUDE_MD}")
    print("=" * 60)

    # 验证路径
    try:
        validate_paths()
        print("\n✅ 所有关键路径验证通过")
    except FileNotFoundError as e:
        print(f"\n❌ 路径验证失败:\n{e}")
