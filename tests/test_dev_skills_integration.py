"""
开发 Skills 集成测试
===================
测试第一阶段开发 Skills（基于原 test_dev_skills.py 改造）
"""

import pytest
import sys
from pathlib import Path


# ==================== 测试数据 ====================

LEAD_ENTITY_FIELDS = [
    {'name': 'name', 'type': 'string', 'required': True, 'max_length': 100, 'description': '客户姓名'},
    {'name': 'phone', 'type': 'string', 'required': True, 'max_length': 20, 'description': '手机号'},
    {'name': 'parent_id', 'type': 'integer', 'foreign_key': 'leads.id', 'description': '推荐人ID'},
    {'name': 'status', 'type': 'string', 'default': 'new', 'description': '状态'},
    {'name': 'depth', 'type': 'integer', 'default': 0, 'description': '裂变层级'},
    {'name': 'source', 'type': 'string', 'max_length': 50, 'description': '来源渠道'}
]

LEAD_RELATIONSHIPS = [
    {'name': 'parent', 'type': 'self_referential', 'back_ref': 'children'}
]

REGISTER_PAGE_DATA_BINDINGS = [
    {'name': 'name', 'type': 'input', 'label': '姓名', 'required': True, 'placeholder': '请输入您的姓名'},
    {'name': 'phone', 'type': 'input', 'label': '手机号', 'required': True, 'placeholder': '请输入手机号'},
    {'name': 'source', 'type': 'picker', 'label': '了解渠道', 'options': ['朋友推荐', '广告', '路过']}
]


# ==================== 工具函数 ====================

def setup_dev_skills_paths(project_root: Path):
    """设置开发 Skills 的导入路径"""
    dev_skills_base = project_root / "leo_skills" / "development"
    
    paths = [
        dev_skills_base / "backend" / "flask-api-generator-cskill" / "scripts",
        dev_skills_base / "backend" / "database-model-generator-cskill" / "scripts",
        dev_skills_base / "frontend" / "miniprogram-page-generator-cskill" / "scripts",
        dev_skills_base / "deployment" / "dockerfile-generator-cskill" / "scripts",
    ]
    
    for path in paths:
        if path.exists() and str(path) not in sys.path:
            sys.path.insert(0, str(path))


# ==================== 集成测试 ====================

@pytest.mark.integration
@pytest.mark.slow
class TestDatabaseModelGenerator:
    """数据库模型生成器测试"""
    
    @pytest.fixture(autouse=True)
    def setup(self, project_root, temp_output_dir):
        """设置测试环境"""
        setup_dev_skills_paths(project_root)
        self.output_dir = temp_output_dir
        self.project_root = project_root
    
    def test_generator_import(self):
        """测试生成器可以导入"""
        try:
            # 尝试从开发目录导入
            dev_path = self.project_root / "leo_skills" / "development" / "backend" / "database-model-generator-cskill" / "scripts"
            if dev_path.exists():
                sys.path.insert(0, str(dev_path))
                from main import DatabaseModelGenerator
                assert DatabaseModelGenerator is not None
        except ImportError:
            pytest.skip("DatabaseModelGenerator 未安装或路径不正确")
    
    def test_generate_lead_model(self):
        """测试生成 Lead 模型"""
        try:
            dev_path = self.project_root / "leo_skills" / "development" / "backend" / "database-model-generator-cskill" / "scripts"
            if not dev_path.exists():
                pytest.skip("database-model-generator-cskill 不存在")
            
            sys.path.insert(0, str(dev_path))
            from main import DatabaseModelGenerator
            
            generator = DatabaseModelGenerator(output_dir=str(self.output_dir), orm="sqlalchemy")
            
            results = generator.generate(
                entity_name='Lead',
                fields=LEAD_ENTITY_FIELDS,
                relationships=LEAD_RELATIONSHIPS,
                indexes=['status', 'phone', 'parent_id']
            )
            
            assert 'model' in results
            assert 'migration' in results
            assert len(results['model']) > 0
            assert len(results['migration']) > 0
            
        except ImportError:
            pytest.skip("DatabaseModelGenerator 未安装")


@pytest.mark.integration
@pytest.mark.slow
class TestMiniprogramPageGenerator:
    """小程序页面生成器测试"""
    
    @pytest.fixture(autouse=True)
    def setup(self, project_root, temp_output_dir):
        """设置测试环境"""
        setup_dev_skills_paths(project_root)
        self.output_dir = temp_output_dir
        self.project_root = project_root
    
    def test_generator_import(self):
        """测试生成器可以导入"""
        try:
            dev_path = self.project_root / "leo_skills" / "development" / "frontend" / "miniprogram-page-generator-cskill" / "scripts"
            if dev_path.exists():
                sys.path.insert(0, str(dev_path))
                from main import MiniprogramPageGenerator
                assert MiniprogramPageGenerator is not None
        except ImportError:
            pytest.skip("MiniprogramPageGenerator 未安装或路径不正确")
    
    def test_generate_register_page(self):
        """测试生成注册页面"""
        try:
            dev_path = self.project_root / "leo_skills" / "development" / "frontend" / "miniprogram-page-generator-cskill" / "scripts"
            if not dev_path.exists():
                pytest.skip("miniprogram-page-generator-cskill 不存在")
            
            sys.path.insert(0, str(dev_path))
            from main import MiniprogramPageGenerator
            
            generator = MiniprogramPageGenerator(output_dir=str(self.output_dir))
            
            api_endpoints = [
                {'name': 'submit', 'url': '/api/leads', 'method': 'POST'}
            ]
            
            results = generator.generate(
                page_name='register',
                page_type='form',
                data_bindings=REGISTER_PAGE_DATA_BINDINGS,
                api_endpoints=api_endpoints,
                features=['validation', 'loading']
            )
            
            assert 'wxml' in results
            assert 'wxss' in results
            assert 'js' in results
            assert 'json' in results
            
        except ImportError:
            pytest.skip("MiniprogramPageGenerator 未安装")


@pytest.mark.integration
@pytest.mark.slow
class TestDockerfileGenerator:
    """Dockerfile 生成器测试"""
    
    @pytest.fixture(autouse=True)
    def setup(self, project_root, temp_output_dir):
        """设置测试环境"""
        setup_dev_skills_paths(project_root)
        self.output_dir = temp_output_dir
        self.project_root = project_root
    
    def test_generator_import(self):
        """测试生成器可以导入"""
        try:
            dev_path = self.project_root / "leo_skills" / "development" / "deployment" / "dockerfile-generator-cskill" / "scripts"
            if dev_path.exists():
                sys.path.insert(0, str(dev_path))
                from main import DockerfileGenerator
                assert DockerfileGenerator is not None
        except ImportError:
            pytest.skip("DockerfileGenerator 未安装或路径不正确")
    
    def test_generate_flask_dockerfile(self):
        """测试生成 Flask Dockerfile"""
        try:
            dev_path = self.project_root / "leo_skills" / "development" / "deployment" / "dockerfile-generator-cskill" / "scripts"
            if not dev_path.exists():
                pytest.skip("dockerfile-generator-cskill 不存在")
            
            sys.path.insert(0, str(dev_path))
            from main import DockerfileGenerator
            
            generator = DockerfileGenerator(output_dir=str(self.output_dir))
            
            results = generator.generate(
                app_type='flask',
                runtime='python:3.9-slim',
                port=5000,
                multi_stage=True,
                with_compose=True,
                services=['mysql', 'redis', 'nginx']
            )
            
            assert 'dockerfile' in results
            assert 'dockerignore' in results
            assert 'compose' in results
            
        except ImportError:
            pytest.skip("DockerfileGenerator 未安装")
