#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
from pathlib import Path

def safe_print(text):
    """安全打印，避免编码错误"""
    try:
        print(text)
    except UnicodeEncodeError:
        safe_text = text.encode('ascii', 'ignore').decode('ascii')
        print(safe_text)

def install_test_dependencies():
    """安装测试依赖"""
    safe_print("Installing test dependencies...")
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", 
            "-r", "requirements-test.txt"
        ], check=True, capture_output=True, text=True)
        
        safe_print("[SUCCESS] Test dependencies installed")
        return True
        
    except subprocess.CalledProcessError as e:
        safe_print(f"[ERROR] Failed to install dependencies: {e}")
        safe_print(f"STDOUT: {e.stdout}")
        safe_print(f"STDERR: {e.stderr}")
        return False

def run_initial_tests():
    """运行初始测试"""
    safe_print("Running initial test setup...")
    
    # 确保tests目录存在
    tests_dir = Path("tests")
    tests_dir.mkdir(exist_ok=True)
    
    # 创建__init__.py
    init_file = tests_dir / "__init__.py"
    if not init_file.exists():
        init_file.write_text("# Tests package")
    
    # 创建conftest.py
    conftest_file = tests_dir / "conftest.py"
    if not conftest_file.exists():
        conftest_file.write_text('''"""Pytest configuration and fixtures."""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest
import tempfile
import shutil

@pytest.fixture(scope="session")
def temp_workspace():
    """Create a temporary workspace for tests."""
    temp_dir = tempfile.mkdtemp(prefix="leo_test_")
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)

@pytest.fixture(scope="session")
def project_root():
    """Get the project root directory."""
    return Path(__file__).parent.parent

@pytest.fixture
def mock_skill_dir(temp_workspace):
    """Create a mock skill directory for testing."""
    skill_dir = Path(temp_workspace) / "test_skill"
    skill_dir.mkdir(parents=True)
    
    # Create minimal skill structure
    (skill_dir / "SKILL.md").write_text("# Test Skill\\nTest description")
    (skill_dir / "scripts").mkdir()
    (skill_dir / "scripts" / "main.py").write_text("# Test main script")
    
    return skill_dir

@pytest.fixture
def safe_print():
    """Safe print function for tests."""
    def _safe_print(text):
        try:
            print(text)
        except UnicodeEncodeError:
            safe_text = text.encode('ascii', 'ignore').decode('ascii')
            print(safe_text)
    return _safe_print
''')
    
    safe_print("[SUCCESS] Test structure created")
    return True

def main():
    """主函数"""
    project_root = Path.cwd()
    
    # 检查是否在正确的目录
    if not (project_root / "leo_skills").exists():
        safe_print("[ERROR] Please run this script from the project root directory")
        return False
    
    # 安装依赖
    if not install_test_dependencies():
        return False
    
    # 创建测试结构
    if not run_initial_tests():
        return False
    
    # 运行pytest检查
    safe_print("Running pytest check...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "--version"
        ], check=True, capture_output=True, text=True)
        
        safe_print("[SUCCESS] Pytest setup completed!")
        safe_print("You can now run tests with: pytest")
        return True
        
    except subprocess.CalledProcessError as e:
        safe_print(f"[ERROR] Pytest check failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)