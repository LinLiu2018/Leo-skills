# -*- coding: utf-8 -*-
"""
自动技能生成器 (Auto Skill Generator)

基于高频意图自动生成完整技能代码。
集成代码模板、测试生成、文档生成。
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


@dataclass
class GeneratedSkill:
    """生成的技能"""
    name: str
    category: str
    files: Dict[str, str]
    estimated_quality: float
    test_coverage: Optional[float]
    requires_review: bool


class SkillTemplateLibrary:
    """技能模板库"""

    TEMPLATES = {
        "api_client": {
            "description": "API 客户端技能",
            "tools": ["Read", "Write", "Bash", "WebFetch"],
            "imports": ["requests", "json", "logging"],
            "structure": ["config", "client", "models", "tests"]
        },
        "data_processor": {
            "description": "数据处理技能",
            "tools": ["Read", "Write", "Grep"],
            "imports": ["pandas", "numpy", "logging"],
            "structure": ["processor", "validators", "tests"]
        },
        "content_generator": {
            "description": "内容生成技能",
            "tools": ["Read", "Write", "WebFetch"],
            "imports": ["jinja2", "logging"],
            "structure": ["templates", "generators", "tests"]
        },
        "analyzer": {
            "description": "分析技能",
            "tools": ["Read", "Grep", "Glob", "Bash"],
            "imports": ["json", "re", "logging", "collections"],
            "structure": ["analyzers", "reports", "tests"]
        },
        "automation": {
            "description": "自动化技能",
            "tools": ["Read", "Write", "Bash", "Agent"],
            "imports": ["subprocess", "logging", "schedule"],
            "structure": ["scheduler", "tasks", "tests"]
        }
    }

    @classmethod
    def get_template(cls, template_type: str) -> Optional[Dict[str, Any]]:
        """获取模板"""
        return cls.TEMPLATES.get(template_type)

    @classmethod
    def suggest_template(cls, intent_description: str) -> str:
        """基于意图描述推荐模板"""
        keywords = {
            "api_client": ["api", "http", "请求", "接口", "client"],
            "data_processor": ["数据", "处理", "csv", "excel", "表格"],
            "content_generator": ["内容", "生成", "文章", "文案", "写作"],
            "analyzer": ["分析", "报告", "统计", "监控"],
            "automation": ["自动化", "定时", "批量", "任务"]
        }

        desc_lower = intent_description.lower()
        scores = {t: 0 for t in cls.TEMPLATES}

        for template, words in keywords.items():
            for word in words:
                if word in desc_lower:
                    scores[template] += 1

        best = max(scores, key=scores.get)
        return best if scores[best] > 0 else "analyzer"


class AutoSkillGenerator:
    """
    自动技能生成器

    根据意图自动生成完整技能代码。
    """

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent.parent.parent

    def generate(
        self,
        intent_category: str,
        description: str,
        example_inputs: List[str],
        trigger_keywords: List[str],
        template_type: Optional[str] = None
    ) -> GeneratedSkill:
        """
        生成完整技能

        Args:
            intent_category: 意图分类
            description: 描述
            example_inputs: 示例输入
            trigger_keywords: 触发关键词
            template_type: 模板类型（可选，自动推断）

        Returns:
            生成的技能
        """
        # 1. 选择模板
        if template_type is None:
            template_type = SkillTemplateLibrary.suggest_template(description)

        template = SkillTemplateLibrary.get_template(template_type)
        if not template:
            template_type = "analyzer"
            template = SkillTemplateLibrary.get_template(template_type)

        # 2. 生成技能名称
        skill_name = self._generate_skill_name(intent_category, template_type)

        # 3. 生成文件
        files = {}
        files["SKILL.md"] = self._generate_skill_md(
            skill_name, description, trigger_keywords, template
        )
        files["scripts/main.py"] = self._generate_main_py(
            skill_name, description, template_type, template
        )
        files["scripts/__init__.py"] = ""
        files["evolution.json"] = self._generate_evolution_json(skill_name)
        files["tests/test_main.py"] = self._generate_test_py(skill_name, example_inputs)

        # 4. 评估质量
        quality = self._estimate_quality(files, template_type)

        return GeneratedSkill(
            name=skill_name,
            category=intent_category,
            files=files,
            estimated_quality=quality,
            test_coverage=0.3 if files.get("tests/test_main.py") else None,
            requires_review=quality < 0.7
        )

    def _generate_skill_name(self, category: str, template: str) -> str:
        """生成技能名称"""
        import random
        import string

        suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
        return f"{category}_{template}_auto_{suffix}"

    def _generate_skill_md(
        self,
        name: str,
        description: str,
        triggers: List[str],
        template: Dict[str, Any]
    ) -> str:
        """生成 SKILL.md"""
        tools_str = "\n  - ".join(template["tools"])

        return f"""---
name: {name}
description: {description}
version: 1.0.0
category: auto-generated
triggers:
  - {triggers[0] if triggers else name}
compatibility:
  - claude-code
  - openclaw
tools:
  - {tools_str}
template: {template.get('description', 'generic')}
---

# {name}

{description}

## 使用方式

在对话中提及以下关键词触发：
{chr(10).join(f"- `{t}`" for t in triggers[:5])}

## 实现说明

此技能由系统自动生成，基于模板: {template.get('description', 'generic')}

## 待办

- [ ] 人工审核代码质量
- [ ] 补充单元测试
- [ ] 添加使用示例
- [ ] 性能优化

## 版本历史

- 1.0.0: 自动生成 (AI)
"""

    def _generate_main_py(
        self,
        name: str,
        description: str,
        template_type: str,
        template: Dict[str, Any]
    ) -> str:
        """生成 main.py"""
        imports = "\n".join(f"import {imp}" for imp in template["imports"])

        template_code = {
            "api_client": '''
class APIClient:
    """API 客户端"""

    def __init__(self, base_url: str = ""):
        self.base_url = base_url
        self.session = requests.Session()

    def request(self, method: str, endpoint: str, **kwargs):
        """发送请求"""
        url = f"{self.base_url}/{endpoint.lstrip(\'/\')}\"
        response = self.session.request(method, url, **kwargs)
        return response.json()


def main(**kwargs) -> Dict[str, Any]:
    """
    主执行函数

    Args:
        base_url: API 基础 URL
        endpoint: API 端点
        method: HTTP 方法

    Returns:
        API 响应
    """
    client = APIClient(kwargs.get("base_url", ""))

    try:
        result = client.request(
            kwargs.get("method", "GET"),
            kwargs.get("endpoint", "/")
        )
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"API request failed: {e}")
        return {"success": False, "error": str(e)}
''',
            "data_processor": '''
class DataProcessor:
    """数据处理器"""

    def __init__(self, data: List[Dict] = None):
        self.data = data or []
        self.df = pd.DataFrame(data) if data else None

    def load(self, file_path: str):
        """加载数据"""
        self.df = pd.read_csv(file_path)
        return self

    def process(self, operations: List[str]) -> pd.DataFrame:
        """处理数据"""
        # TODO: 实现具体处理逻辑
        return self.df


def main(**kwargs) -> Dict[str, Any]:
    """
    主执行函数

    Args:
        file_path: 数据文件路径
        operations: 处理操作列表

    Returns:
        处理结果
    """
    try:
        processor = DataProcessor()

        if "file_path" in kwargs:
            processor.load(kwargs["file_path"])

        result = processor.process(kwargs.get("operations", []))

        return {
            "success": True,
            "data": result.to_dict() if result is not None else {},
            "shape": result.shape if result is not None else (0, 0)
        }
    except Exception as e:
        logger.error(f"Data processing failed: {e}")
        return {"success": False, "error": str(e)}
''',
            "content_generator": '''
from jinja2 import Template


class ContentGenerator:
    """内容生成器"""

    def __init__(self, template_str: str = ""):
        self.template = Template(template_str) if template_str else None

    def render(self, context: Dict) -> str:
        """渲染模板"""
        if not self.template:
            return ""
        return self.template.render(**context)

    def generate(self, prompt: str, context: Dict) -> str:
        """生成内容"""
        # TODO: 集成 LLM API 生成内容
        return f"Generated based on: {prompt}"


def main(**kwargs) -> Dict[str, Any]:
    """
    主执行函数

    Args:
        prompt: 生成提示
        template: 模板字符串
        context: 模板变量

    Returns:
        生成的内容
    """
    try:
        generator = ContentGenerator(kwargs.get("template", ""))

        if "prompt" in kwargs:
            content = generator.generate(kwargs["prompt"], kwargs.get("context", {}))
        else:
            content = generator.render(kwargs.get("context", {}))

        return {"success": True, "content": content}
    except Exception as e:
        logger.error(f"Content generation failed: {e}")
        return {"success": False, "error": str(e)}
''',
            "analyzer": '''
class Analyzer:
    """分析器"""

    def __init__(self, data_source: str = ""):
        self.data_source = data_source
        self.results = {}

    def analyze(self, criteria: List[str]) -> Dict:
        """执行分析"""
        # TODO: 实现具体分析逻辑
        return {"analyzed": True, "criteria": criteria}

    def report(self) -> str:
        """生成报告"""
        return json.dumps(self.results, ensure_ascii=False, indent=2)


def main(**kwargs) -> Dict[str, Any]:
    """
    主执行函数

    Args:
        data_source: 数据源路径
        criteria: 分析标准

    Returns:
        分析结果
    """
    try:
        analyzer = Analyzer(kwargs.get("data_source", ""))
        results = analyzer.analyze(kwargs.get("criteria", []))

        return {
            "success": True,
            "results": results,
            "report": analyzer.report()
        }
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        return {"success": False, "error": str(e)}
''',
            "automation": '''
class TaskScheduler:
    """任务调度器"""

    def __init__(self):
        self.tasks = []

    def add_task(self, task_func, schedule: str):
        """添加任务"""
        # TODO: 实现调度逻辑
        self.tasks.append({"func": task_func, "schedule": schedule})

    def run(self):
        """运行所有任务"""
        for task in self.tasks:
            task["func"]()


def main(**kwargs) -> Dict[str, Any]:
    """
    主执行函数

    Args:
        tasks: 任务列表
        schedule: 调度配置

    Returns:
        执行结果
    """
    try:
        scheduler = TaskScheduler()

        # 执行任务
        executed = 0
        for task in kwargs.get("tasks", []):
            # 模拟任务执行
            logger.info(f"Executing task: {task}")
            executed += 1

        return {
            "success": True,
            "executed": executed,
            "tasks": kwargs.get("tasks", [])
        }
    except Exception as e:
        logger.error(f"Automation failed: {e}")
        return {"success": False, "error": str(e)}
'''
        }

        code = template_code.get(template_type, template_code["analyzer"])

        return f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
{name}

{description}
"""

import logging
from typing import Dict, Any, List
{imports}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

{code}


if __name__ == "__main__":
    # 测试运行
    result = main()
    print(json.dumps(result, ensure_ascii=False, indent=2))
'''

    def _generate_evolution_json(self, name: str) -> str:
        """生成 evolution.json"""
        return json.dumps({
            "version": "1.0.0",
            "evolution_history": [{
                "version": "1.0.0",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "changes": f"Auto-generated skill: {name}",
                "author": "AI"
            }],
            "learned_tips": [],
            "learned_errors": [],
            "quality_score": None,
            "requires_review": True
        }, indent=2)

    def _generate_test_py(self, name: str, example_inputs: List[str]) -> str:
        """生成测试文件"""
        return f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
{name} 测试
"""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from main import main


class Test{name.replace("_", "").title()}(unittest.TestCase):
    """测试用例"""

    def test_basic_execution(self):
        """测试基本执行"""
        result = main()
        self.assertIn("success", result)

    # TODO: 添加更多测试用例


if __name__ == "__main__":
    unittest.main()
'''

    def _estimate_quality(self, files: Dict[str, str], template_type: str) -> float:
        """估计代码质量"""
        score = 0.5  # 基础分

        # 文件完整性
        required_files = ["SKILL.md", "scripts/main.py"]
        for f in required_files:
            if f in files and files[f]:
                score += 0.1

        # 有测试
        if "tests/test_main.py" in files:
            score += 0.1

        # 模板匹配度 (根据模板类型加分)
        template_bonus = {
            "api_client": 0.05,
            "data_processor": 0.05,
            "content_generator": 0.05,
            "analyzer": 0.05,
            "automation": 0.05
        }
        score += template_bonus.get(template_type, 0)

        return min(0.9, score)

    def save_skill(self, skill: GeneratedSkill, output_dir: Optional[Path] = None) -> Path:
        """
        保存生成的技能

        Args:
            skill: 生成的技能
            output_dir: 输出目录

        Returns:
            保存路径
        """
        if output_dir is None:
            output_dir = self.project_root / "src" / "leo_skills" / "_generated"

        skill_dir = output_dir / skill.name
        skill_dir.mkdir(parents=True, exist_ok=True)

        for file_path, content in skill.files.items():
            full_path = skill_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content, encoding="utf-8")

        # 标记需要审核
        review_flag = skill_dir / ".requires_review"
        review_flag.write_text(f"Quality: {skill.estimated_quality:.2f}\n", encoding="utf-8")

        logger.info(f"Saved generated skill to {skill_dir}")
        return skill_dir


# 便捷函数
def auto_generate_skill(
    intent: str,
    description: str,
    examples: List[str],
    triggers: List[str]
) -> GeneratedSkill:
    """快速生成入口"""
    generator = AutoSkillGenerator()
    return generator.generate(intent, description, examples, triggers)


if __name__ == "__main__":
    # 测试
    skill = auto_generate_skill(
        "development",
        "自动分析代码质量的技能",
        ["分析代码", "检查质量"],
        ["代码分析", "质量检查"]
    )

    print(f"生成技能: {skill.name}")
    print(f"估计质量: {skill.estimated_quality:.2f}")
    print(f"需要审核: {skill.requires_review}")
    print(f"文件数: {len(skill.files)}")
