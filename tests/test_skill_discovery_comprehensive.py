#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""技能发现系统测试"""

import pytest
import sys
import tempfile
import shutil
from pathlib import Path

# 确保项目根目录和src目录在Python路径中
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from leo_subagents.skills_bridge.skill_discovery_simple import SkillDiscoverySystem, SkillMetadata

class TestSkillDiscoverySystem:
    """技能发现系统测试"""
    
    @pytest.fixture
    def temp_workspace(self, tmp_path):
        """创建临时工作空间"""
        return tmp_path
    
    @pytest.fixture
    def mock_skill_structure(self, temp_workspace):
        """创建模拟技能结构"""
        skills_dir = temp_workspace / "leo_skills"
        skills_dir.mkdir()
        
        # 创建测试技能
        test_skill = skills_dir / "test-category" / "test-skill"
        test_skill.mkdir(parents=True)
        
        # SKILL.md - 需要足够长的内容才能通过验证
        skill_content = """# Test Skill

This is a comprehensive test skill description that meets the minimum length requirement.
It provides sufficient content to pass the validation check that requires at least 50 characters.
This skill is designed for testing purposes and demonstrates the proper structure of a Leo skill.

## Features
- Test feature 1
- Test feature 2

## Usage
This skill can be used to test the skill discovery system.
"""
        (test_skill / "SKILL.md").write_text(skill_content)
        
        # scripts/main.py
        scripts_dir = test_skill / "scripts"
        scripts_dir.mkdir()
        (scripts_dir / "main.py").write_text('def main():\\n    print("Hello from test skill")')
        
        # README.md
        (test_skill / "README.md").write_text("# Test Skill README")
        
        return skills_dir
    
    @pytest.fixture
    def discovery_system(self, mock_skill_structure):
        """创建技能发现系统实例"""
        system = SkillDiscoverySystem(mock_skill_structure.parent)
        # 确保目录存在
        system.registry_path.parent.mkdir(exist_ok=True)
        system.cache_dir.mkdir(exist_ok=True)
        return system
    
    def test_discovery_initialization(self, mock_skill_structure):
        """测试系统初始化"""
        discovery = SkillDiscoverySystem(mock_skill_structure.parent)
        
        assert discovery.project_root == mock_skill_structure.parent
        assert discovery.skills_path == mock_skill_structure
        assert discovery.registry_path.exists()
        assert discovery.cache_dir.exists()
        assert isinstance(discovery.registry, dict)
    
    def test_calculate_checksum(self, discovery_system, mock_skill_structure):
        """测试校验和计算"""
        skill_path = mock_skill_structure / "test-category" / "test-skill"
        checksum1 = discovery_system._calculate_checksum(skill_path)
        checksum2 = discovery_system._calculate_checksum(skill_path)
        
        # 相同文件应该有相同的校验和
        assert checksum1 == checksum2
        assert len(checksum1) == 32  # MD5 hash length
        
        # 修改文件后校验和应该改变
        (skill_path / "SKILL.md").write_text("# Modified Test Skill")
        checksum3 = discovery_system._calculate_checksum(skill_path)
        assert checksum3 != checksum1
    
    def test_validate_skill_valid(self, discovery_system, mock_skill_structure):
        """测试有效技能验证"""
        skill_path = mock_skill_structure / "test-category" / "test-skill"
        is_valid, errors = discovery_system._validate_skill(skill_path)
        
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_skill_missing_skill_md(self, discovery_system, mock_skill_structure):
        """测试缺少SKILL.md的技能验证"""
        skill_path = mock_skill_structure / "test-category" / "test-skill"
        (skill_path / "SKILL.md").unlink()
        
        is_valid, errors = discovery_system._validate_skill(skill_path)
        
        assert is_valid is False
        assert len(errors) > 0
        assert any("SKILL.md" in error for error in errors)
    
    def test_validate_skill_missing_entry_point(self, discovery_system, mock_skill_structure):
        """测试缺少入口点的技能验证"""
        skill_path = mock_skill_structure / "test-category" / "test-skill"
        shutil.rmtree(skill_path / "scripts")
        
        is_valid, errors = discovery_system._validate_skill(skill_path)
        
        assert is_valid is False
        assert len(errors) > 0
        assert any("entry point" in error for error in errors)
    
    def test_discover_skills(self, discovery_system):
        """测试技能发现"""
        skills = discovery_system.discover_skills()
        
        assert len(skills) > 0
        skill_key = "test-category/test-skill"
        assert skill_key in skills
        
        skill_data = skills[skill_key]
        assert skill_data['name'] == 'test-skill'
        assert skill_data['category'] == 'test-category'
        assert skill_data['is_valid'] is True
        assert len(skill_data['validation_errors']) == 0
    
    def test_update_registry(self, discovery_system):
        """测试注册表更新"""
        result = discovery_system.update_registry()
        
        assert 'total_skills' in result
        assert 'new_skills' in result
        assert 'updated_skills' in result
        assert 'removed_skills' in result
        
        # 应该发现新技能
        assert result['total_skills'] > 0
        assert len(result['new_skills']) > 0
    
    def test_search_skills(self, discovery_system):
        """测试技能搜索"""
        # 先更新注册表
        discovery_system.update_registry()
        
        # 搜索存在的技能
        results = discovery_system.search_skills('test')
        assert len(results) > 0
        
        # 搜索不存在的技能
        results = discovery_system.search_skills('nonexistent')
        assert len(results) == 0
    
    def test_get_status_report(self, discovery_system):
        """测试状态报告"""
        # 先更新注册表
        discovery_system.update_registry()
        
        report = discovery_system.get_status_report()
        
        assert 'total_skills' in report
        assert 'valid_skills' in report
        assert 'invalid_skills' in report
        assert 'categories' in report
        assert 'last_updated' in report
        
        assert report['total_skills'] >= 0
        assert report['valid_skills'] >= 0
        assert report['invalid_skills'] >= 0
    
    def test_generate_claude_skills_directory(self, discovery_system, temp_workspace):
        """测试Claude技能目录生成"""
        # 先更新注册表
        discovery_system.update_registry()
        
        # 生成到临时目录
        target_dir = temp_workspace / "claude_skills"
        success = discovery_system.generate_claude_skills_directory(target_dir)
        
        assert success is True
        assert target_dir.exists()
        
        # 检查生成的文件
        index_file = target_dir / "leo_skills_index.json"
        assert index_file.exists()
        
        # 检查技能入口文件
        skill_entry = target_dir / "leo_test_skill.py"
        assert skill_entry.exists()

class TestSkillMetadata:
    """技能元数据测试"""
    
    def test_skill_metadata_creation(self):
        """测试技能元数据创建"""
        metadata = SkillMetadata(
            name="test-skill",
            path="/test/path",
            category="test"
        )
        
        assert metadata.name == "test-skill"
        assert metadata.path == "/test/path"
        assert metadata.category == "test"
        assert metadata.version == "1.0.0"
        assert metadata.author == "Leo Liu"
        assert metadata.keywords == []
        assert metadata.activation_keywords == []
        assert metadata.dependencies == []
        assert metadata.validation_errors == []
        assert metadata.is_valid is False
    
    def test_skill_metadata_with_custom_values(self):
        """测试自定义值的技能元数据"""
        metadata = SkillMetadata(
            name="custom-skill",
            path="/custom/path",
            category="custom",
            version="2.0.0",
            description="Custom skill description",
            keywords=["test", "custom"],
            activation_keywords=["activate", "run"],
            dependencies=["dependency1", "dependency2"]
        )
        
        assert metadata.version == "2.0.0"
        assert metadata.description == "Custom skill description"
        assert metadata.keywords == ["test", "custom"]
        assert metadata.activation_keywords == ["activate", "run"]
        assert metadata.dependencies == ["dependency1", "dependency2"]

class TestIntegration:
    """集成测试"""
    
    def test_full_workflow(self, tmp_path):
        """测试完整工作流程"""
        # 1. 创建项目结构
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        skills_dir = project_root / "leo_skills" / "integration-test" / "integration-skill"
        skills_dir.mkdir(parents=True)
        
        # 2. 创建技能文件 - 需要足够长的内容
        skill_content = """# Integration Test Skill

This is a comprehensive integration test skill that meets the minimum length requirement.
It provides sufficient content to pass validation check that requires at least 50 characters.
This skill is designed for integration testing and demonstrates proper structure of a Leo skill.

## Features
- Integration test feature 1
- Integration test feature 2

## Usage
This skill can be used to test the complete workflow of the skill discovery system.
It ensures that all components work together correctly from discovery to registration.
"""
        (skills_dir / "SKILL.md").write_text(skill_content)
        (skills_dir / "scripts").mkdir(exist_ok=True)
        (skills_dir / "scripts" / "main.py").write_text("def main():\\n    return 'integration test'")
        
        # 3. 创建发现系统
        discovery = SkillDiscoverySystem(project_root)
        
        # 4. 更新注册表
        result = discovery.update_registry()
        assert result['total_skills'] == 1
        assert len(result['new_skills']) == 1
        
        # 5. 搜索技能
        results = discovery.search_skills('integration')
        assert len(results) == 1
        
        # 6. 获取状态
        status = discovery.get_status_report()
        assert status['total_skills'] == 1
        assert status['valid_skills'] == 1
        assert status['invalid_skills'] == 0
        
        # 7. 生成Claude目录
        claude_dir = tmp_path / "claude_skills"
        success = discovery.generate_claude_skills_directory(claude_dir)
        assert success is True
        assert (claude_dir / "leo_integration_skill.py").exists()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])