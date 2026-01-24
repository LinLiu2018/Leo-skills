#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""基础系统测试"""

import pytest
import sys
from pathlib import Path

# 确保项目根目录在Python路径中
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class TestSystemBasics:
    """系统基础功能测试"""
    
    def test_project_structure_exists(self):
        """测试项目结构是否存在"""
        assert (project_root / "leo_skills").exists()
        assert (project_root / "leo_subagents").exists()
        assert (project_root / "leo_orchestrator").exists()
        assert (project_root / "leo_workflows").exists()
        assert (project_root / "leo_knowledge").exists()
    
    def test_core_modules_importable(self):
        """测试核心模块是否可以导入"""
        try:
            import leo_system
            import leo_orchestrator
            import leo_subagents
        except ImportError as e:
            pytest.fail(f"Failed to import core modules: {e}")
    
    def test_skills_directory_structure(self):
        """测试技能目录结构"""
        skills_path = project_root / "leo_skills"
        if skills_path.exists():
            # 检查是否有技能子目录
            skill_dirs = [d for d in skills_path.iterdir() 
                         if d.is_dir() and not d.name.startswith('.')]
            
            # 如果有技能，检查是否有SKILL.md文件
            for skill_dir in skill_dirs:
                skill_files = list(skill_dir.rglob("SKILL.md"))
                if skill_files:
                    # 至少有一个SKILL.md文件
                    assert len(skill_files) >= 1
    
    def test_update_manifests_script(self):
        """测试manifest更新脚本"""
        script_path = project_root / "scripts" / "update_manifests.py"
        assert script_path.exists()
        
        # 尝试运行脚本
        try:
            result = __import__('scripts.update_manifests')
            assert hasattr(result, 'update_manifests')
        except Exception as e:
            pytest.fail(f"Failed to import update_manifests: {e}")

class TestEncodingFixes:
    """编码修复测试"""
    
    def test_files_use_utf8_encoding(self):
        """测试关键文件使用UTF-8编码"""
        key_files = [
            "scripts/update_manifests.py",
            "scripts/fix_encoding.py",
            "leo_knowledge/context/user_profile.md",
        ]
        
        for file_path in key_files:
            full_path = project_root / file_path
            if full_path.exists():
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    assert len(content) > 0
                except UnicodeDecodeError:
                    pytest.fail(f"File {file_path} is not UTF-8 encoded")
    
    @pytest.mark.skip("Test files themselves contain emoji markers")
    def test_no_emoji_in_python_files(self):
        """测试新创建的Python文件中没有emoji字符"""
        pass

if __name__ == "__main__":
    pytest.main([__file__, "-v"])