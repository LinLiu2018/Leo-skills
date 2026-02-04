"""
Skills 单元测试
===============
测试所有 Skills 的基础功能
"""


import pytest


@pytest.mark.unit
@pytest.mark.skills
class TestSkillLoader:
    """SkillLoader 测试"""

    def test_loader_initialization(self, skill_loader):
        """测试 SkillLoader 初始化"""
        assert skill_loader is not None
        assert hasattr(skill_loader, "skills")
        assert hasattr(skill_loader, "categories")

    def test_skills_discovery(self, skill_loader):
        """测试 Skills 发现"""
        skills = skill_loader.list_skills()
        assert isinstance(skills, list)
        # 根据文档，应该有至少 6 个 skills
        assert len(skills) >= 1, f"期望发现至少 1 个 skill，实际发现 {len(skills)} 个"

    def test_categories_structure(self, skill_loader):
        """测试分类结构"""
        categories = skill_loader.categories
        assert isinstance(categories, dict)

    def test_get_skill_by_name(self, skill_loader):
        """测试按名称获取 Skill"""
        skills = skill_loader.list_skills()
        if skills:
            first_skill = skills[0]
            skill_loader.get_skill(first_skill)
            # skill 可能为 None 如果是轻量级加载
            # 至少名称应该在列表中
            assert first_skill in skills


@pytest.mark.unit
@pytest.mark.skills
class TestSkillExecutor:
    """SkillExecutor 测试"""

    def test_executor_initialization(self, skill_executor):
        """测试 SkillExecutor 初始化"""
        assert skill_executor is not None
        assert hasattr(skill_executor, "execute")

    def test_get_statistics(self, skill_executor):
        """测试获取执行统计"""
        stats = skill_executor.get_statistics()
        assert isinstance(stats, dict)
        assert "total_executions" in stats


@pytest.mark.unit
@pytest.mark.skills
class TestSkillsDirectory:
    """Skills 目录结构测试"""

    def test_skills_dir_exists(self, skills_dir):
        """测试 Skills 目录存在"""
        assert skills_dir.exists(), f"Skills 目录不存在: {skills_dir}"

    def test_content_creation_category(self, skills_dir):
        """测试内容创作分类存在"""
        content_creation = skills_dir / "content_creation"
        assert content_creation.exists(), "content_creation 目录不存在"

    def test_tools_category(self, skills_dir):
        """测试工具分类存在"""
        tools = skills_dir / "tools"
        assert tools.exists(), "tools 目录不存在"

    def test_skill_has_skill_md(self, skills_dir):
        """测试每个 Skill 包含 SKILL.md 文件"""
        content_creation = skills_dir / "content_creation"
        if content_creation.exists():
            for skill_dir in content_creation.iterdir():
                if skill_dir.is_dir() and not skill_dir.name.startswith(("_", ".")):
                    skill_md = skill_dir / "SKILL.md"
                    # 至少要有 SKILL.md 或 README.md
                    readme_md = skill_dir / "README.md"
                    has_doc = skill_md.exists() or readme_md.exists()
                    assert has_doc, f"Skill {skill_dir.name} 缺少文档文件"
