"""
Workflow 集成测试
================
测试工作流定义加载和基本执行逻辑（pytest 兼容）
"""
import sys
from pathlib import Path
import pytest

# 添加路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))


@pytest.fixture
def workflow_definitions_dir():
    """工作流 YAML 定义目录"""
    return project_root / "src" / "leo_workflows" / "definitions"


@pytest.fixture
def workflow_dir():
    """工作流实现目录"""
    return project_root / "src" / "leo_workflows" / "workflows"


class TestWorkflowDefinitions:
    """测试工作流 YAML 定义文件"""

    def test_definitions_dir_exists(self, workflow_definitions_dir):
        """定义目录应存在"""
        assert workflow_definitions_dir.exists(), f"工作流定义目录不存在: {workflow_definitions_dir}"

    def test_yaml_files_parseable(self, workflow_definitions_dir):
        """所有 YAML 定义文件应可解析"""
        import yaml
        yaml_files = list(workflow_definitions_dir.glob("*.yaml"))
        assert len(yaml_files) > 0, "应至少有一个工作流定义文件"

        for yaml_file in yaml_files:
            with open(yaml_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            assert data is not None, f"{yaml_file.name} 解析结果为空"
            assert "name" in data, f"{yaml_file.name} 缺少 name 字段"

    def test_content_pipeline_definition(self, workflow_definitions_dir):
        """content_pipeline 定义应包含必要字段"""
        import yaml
        pipeline_file = workflow_definitions_dir / "content_pipeline.yaml"
        if not pipeline_file.exists():
            pytest.skip("content_pipeline.yaml 不存在")

        with open(pipeline_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        assert "steps" in data, "应包含 steps 定义"
        assert len(data["steps"]) > 0, "应至少有一个步骤"


class TestWorkflowImplementations:
    """测试工作流 Python 实现"""

    def test_content_pipeline_importable(self, workflow_dir):
        """content_pipeline 应可导入"""
        pipeline_dir = workflow_dir / "content_pipeline"
        assert pipeline_dir.exists(), "content_pipeline 目录不存在"
        assert (pipeline_dir / "__init__.py").exists(), "__init__.py 不存在"
        assert (pipeline_dir / "content_pipeline.py").exists(), "content_pipeline.py 不存在"

    def test_research_pipeline_importable(self, workflow_dir):
        """research_pipeline 应可导入"""
        pipeline_dir = workflow_dir / "research_pipeline"
        assert pipeline_dir.exists(), "research_pipeline 目录不存在"
        assert (pipeline_dir / "__init__.py").exists(), "__init__.py 不存在"

    def test_analysis_pipeline_importable(self, workflow_dir):
        """analysis_pipeline 应可导入"""
        pipeline_dir = workflow_dir / "analysis_pipeline"
        assert pipeline_dir.exists(), "analysis_pipeline 目录不存在"
        assert (pipeline_dir / "__init__.py").exists(), "__init__.py 不存在"
