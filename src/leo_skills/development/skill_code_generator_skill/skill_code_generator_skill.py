"""
技能代码生成器

根据 SKILL.md 模板和规格说明自动生成技能代码文件，包括目录结构、
主脚本、配置文件、文档和测试框架。支持从自然语言描述、模板名称
或结构化规格生成技能。
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from leo_skills.core.base_executor import BaseExecutor


@dataclass
class SkillSpec:
    """技能规格定义。"""
    name: str
    description: str
    category: str
    author: str = "Claude Code"
    version: str = "1.0.0"
    dependencies: List[str] = field(default_factory=list)
    features: List[str] = field(default_factory=list)
    inputs: List[Dict[str, Any]] = field(default_factory=list)
    outputs: List[Dict[str, Any]] = field(default_factory=list)
    configuration: Dict[str, Any] = field(default_factory=dict)
    template: str = "default"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name, "description": self.description,
            "category": self.category, "author": self.author,
            "version": self.version, "dependencies": self.dependencies,
            "features": self.features, "inputs": self.inputs,
            "outputs": self.outputs, "configuration": self.configuration,
            "template": self.template,
        }


# 预置模板
_TEMPLATES: Dict[str, Dict[str, Any]] = {
    "api-client": {
        "description": "API 客户端技能模板",
        "extra_deps": ["requests"],
        "extra_files": ["scripts/api_client.py"],
    },
    "data-processor": {
        "description": "数据处理技能模板",
        "extra_deps": ["pandas"],
        "extra_files": ["scripts/processor.py"],
    },
    "content-generator": {
        "description": "内容生成技能模板",
        "extra_deps": ["jinja2"],
        "extra_files": ["scripts/generator.py", "templates/"],
    },
    "file-handler": {
        "description": "文件处理技能模板",
        "extra_deps": [],
        "extra_files": ["scripts/file_handler.py"],
    },
    "automation": {
        "description": "自动化任务技能模板",
        "extra_deps": ["schedule"],
        "extra_files": ["scripts/scheduler.py"],
    },
}

# 支持的技能分类
_CATEGORIES = [
    "utilities", "content_creation", "development", "data_analysis",
    "monitoring", "integration", "automation", "research",
    "tools", "frontend", "backend", "devops", "testing",
    "scaffold", "security", "intelligence", "collaboration",
]


class SkillCodeGenerator(BaseExecutor):
    """技能代码生成器。

    支持的操作：
        - generate:          从规格生成技能
        - generate_from_prompt: 从自然语言描述生成
        - generate_from_template: 从模板生成
        - list_templates:    列出可用模板
        - validate:          验证已生成的技能
    """

    def __init__(self) -> None:
        self.name = "skill_code_generator_skill"

    # ------------------------------------------------------------------ #
    #  BaseExecutor 接口
    # ------------------------------------------------------------------ #

    def execute(
        self,
        action: str = "generate",
        context: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = dict(context or {})
        params.update(kwargs)

        actions = {
            "generate": self._action_generate,
            "run": self._action_generate,
            "generate_from_prompt": self._action_from_prompt,
            "generate_from_template": self._action_from_template,
            "list_templates": self._action_list_templates,
            "validate": self._action_validate,
        }
        handler = actions.get(action)
        if handler is None:
            return {"status": "error", "message": f"未知操作: {action}"}
        return handler(params)

    # ------------------------------------------------------------------ #
    #  动作方法
    # ------------------------------------------------------------------ #

    def _action_generate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """从结构化规格生成技能。"""
        name = params.get("name", "")
        description = params.get("description", "")
        category = params.get("category", "utilities")
        output_dir = params.get("output_dir", ".")

        if not name:
            return {"status": "error", "message": "缺少 name 参数"}
        if not description:
            return {"status": "error", "message": "缺少 description 参数"}

        spec = SkillSpec(
            name=self._normalize_name(name),
            description=description,
            category=category,
            author=params.get("author", "Claude Code"),
            version=params.get("version", "1.0.0"),
            dependencies=params.get("dependencies", []),
            features=params.get("features", []),
            template=params.get("template", "default"),
        )

        errors = self._validate_spec(spec)
        if errors:
            return {"status": "error", "message": "规格验证失败", "errors": errors}

        return self._generate_skill(spec, output_dir)

    def _action_from_prompt(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """从自然语言描述生成技能。"""
        prompt = params.get("prompt", "")
        if not prompt:
            return {"status": "error", "message": "缺少 prompt 参数"}

        spec = self._parse_prompt(prompt, params.get("category"))
        output_dir = params.get("output_dir", ".")
        return self._generate_skill(spec, output_dir)

    def _action_from_template(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """从预置模板生成技能。"""
        template_name = params.get("template", "")
        if template_name not in _TEMPLATES:
            return {"status": "error", "message": f"未知模板: {template_name}",
                    "available": list(_TEMPLATES.keys())}

        name = params.get("name", f"my-{template_name}")
        description = params.get("description", _TEMPLATES[template_name]["description"])

        spec = SkillSpec(
            name=self._normalize_name(name),
            description=description,
            category=params.get("category", "utilities"),
            dependencies=_TEMPLATES[template_name].get("extra_deps", []),
            template=template_name,
        )
        output_dir = params.get("output_dir", ".")
        return self._generate_skill(spec, output_dir)

    def _action_list_templates(self, _params: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "success",
            "templates": [
                {"name": k, "description": v["description"]}
                for k, v in _TEMPLATES.items()
            ],
        }

    def _action_validate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        path = params.get("skill_path", params.get("output_dir", "."))
        return self._validate_skill_dir(path)

    # ------------------------------------------------------------------ #
    #  核心生成逻辑
    # ------------------------------------------------------------------ #

    def _generate_skill(self, spec: SkillSpec, output_dir: str) -> Dict[str, Any]:
        """根据规格生成完整技能目录。"""
        skill_dir = Path(output_dir) / f"{spec.name}_skill"
        skill_dir.mkdir(parents=True, exist_ok=True)

        files_written: List[str] = []

        # 1. SKILL.md
        self._write(skill_dir / "SKILL.md", self._gen_skill_md(spec))
        files_written.append("SKILL.md")

        # 2. README.md
        self._write(skill_dir / "README.md", self._gen_readme(spec))
        files_written.append("README.md")

        # 3. __init__.py
        self._write(skill_dir / "__init__.py", self._gen_init(spec))
        files_written.append("__init__.py")

        # 4. {name}_skill.py（主实现）
        main_file = f"{spec.name}_skill.py"
        self._write(skill_dir / main_file, self._gen_main_skill(spec))
        files_written.append(main_file)

        # 5. scripts/
        scripts_dir = skill_dir / "scripts"
        scripts_dir.mkdir(exist_ok=True)
        self._write(scripts_dir / "__init__.py", "")
        self._write(scripts_dir / "main.py", self._gen_scripts_main(spec))
        files_written.extend(["scripts/__init__.py", "scripts/main.py"])

        # 6. config/
        config_dir = skill_dir / "config"
        config_dir.mkdir(exist_ok=True)
        self._write(config_dir / "config.yaml", self._gen_config_yaml(spec))
        files_written.append("config/config.yaml")

        # 7. tests/
        tests_dir = skill_dir / "tests"
        tests_dir.mkdir(exist_ok=True)
        self._write(tests_dir / "__init__.py", "")
        self._write(tests_dir / f"test_{spec.name}_skill.py", self._gen_test(spec))
        files_written.extend(["tests/__init__.py", f"tests/test_{spec.name}_skill.py"])

        return {
            "status": "success",
            "action": "generate",
            "skill_name": spec.name,
            "skill_path": str(skill_dir),
            "files_created": files_written,
            "file_count": len(files_written),
            "spec": spec.to_dict(),
        }

    # ------------------------------------------------------------------ #
    #  自然语言解析
    # ------------------------------------------------------------------ #

    def _parse_prompt(self, prompt: str, category_override: Optional[str] = None) -> SkillSpec:
        """从自然语言描述中提取技能规格。"""
        prompt_lower = prompt.lower()

        # 推断名称
        name_match = re.search(r"(?:创建|生成|做一个|build|create)\s*['\"]?(\S+)['\"]?", prompt, re.IGNORECASE)
        name = name_match.group(1) if name_match else "custom-skill"
        name = self._normalize_name(name)

        # 推断分类
        category = category_override or self._infer_category(prompt_lower)

        # 推断依赖
        deps: List[str] = []
        dep_keywords = {"requests": "requests", "api": "requests", "http": "requests",
                        "数据": "pandas", "data": "pandas", "csv": "pandas",
                        "yaml": "pyyaml", "模板": "jinja2", "template": "jinja2"}
        for kw, dep in dep_keywords.items():
            if kw in prompt_lower and dep not in deps:
                deps.append(dep)

        return SkillSpec(
            name=name,
            description=prompt[:200],
            category=category,
            dependencies=deps,
        )

    @staticmethod
    def _infer_category(text: str) -> str:
        """从文本推断技能分类。"""
        cat_keywords = {
            "tools": ["工具", "tool", "utility"],
            "content_creation": ["内容", "文章", "content", "article", "writing"],
            "data_analysis": ["数据", "分析", "data", "analysis", "statistics"],
            "automation": ["自动", "定时", "automat", "schedule"],
            "development": ["开发", "代码", "develop", "code", "generate"],
            "testing": ["测试", "test", "verify"],
            "devops": ["部署", "docker", "deploy", "ci"],
            "security": ["安全", "扫描", "security", "scan"],
        }
        for cat, kws in cat_keywords.items():
            if any(kw in text for kw in kws):
                return cat
        return "utilities"

    # ------------------------------------------------------------------ #
    #  验证
    # ------------------------------------------------------------------ #

    @staticmethod
    def _validate_spec(spec: SkillSpec) -> List[str]:
        errors: List[str] = []
        if not spec.name or not spec.name.strip():
            errors.append("技能名称不能为空")
        if not spec.description or not spec.description.strip():
            errors.append("技能描述不能为空")
        if not re.match(r"^[a-z0-9_-]+$", spec.name):
            errors.append("技能名称只能包含小写字母、数字、下划线和连字符")
        return errors

    def _validate_skill_dir(self, path: str) -> Dict[str, Any]:
        """验证已生成的技能目录。"""
        errors: List[str] = []
        warnings: List[str] = []
        p = Path(path)

        required = ["SKILL.md"]
        for f in required:
            if not (p / f).exists():
                errors.append(f"缺少必需文件: {f}")

        # 检查 Python 语法
        for py in p.rglob("*.py"):
            try:
                compile(py.read_text(encoding="utf-8"), str(py), "exec")
            except SyntaxError as e:
                errors.append(f"语法错误 {py.name}: {e}")

        # 检查 YAML 语法
        for yml in p.rglob("*.yaml"):
            try:
                import yaml
                yaml.safe_load(yml.read_text(encoding="utf-8"))
            except Exception as e:
                errors.append(f"YAML 错误 {yml.name}: {e}")

        if not (p / "scripts" / "main.py").exists():
            warnings.append("建议: 添加 scripts/main.py 入口文件")
        if not list(p.rglob("test_*.py")):
            warnings.append("建议: 添加测试文件")

        return {
            "status": "success" if not errors else "error",
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
        }

    # ------------------------------------------------------------------ #
    #  文件生成模板
    # ------------------------------------------------------------------ #

    @staticmethod
    def _gen_skill_md(spec: SkillSpec) -> str:
        return f"""---
name: {spec.name}_skill
description: {spec.description}
---

# {spec.name.replace('-', ' ').replace('_', ' ').title()}

{spec.description}

## 功能特性

{chr(10).join('- ' + f for f in spec.features) if spec.features else '- 核心功能待定义'}

## 使用方法

```python
from {spec.name}_skill import {spec.name.replace('-', '_').title().replace('_', '')}Skill

skill = {spec.name.replace('-', '_').title().replace('_', '')}Skill()
result = skill.execute(action="run")
```

## 激活条件

当用户请求与 {spec.description[:50]} 相关时自动激活。

## 版本

- **Version**: {spec.version}
- **Author**: {spec.author}
- **Category**: {spec.category}
"""

    @staticmethod
    def _gen_readme(spec: SkillSpec) -> str:
        return f"""# {spec.name.replace('-', ' ').replace('_', ' ').title()}

{spec.description}

## 安装

```bash
pip install {' '.join(spec.dependencies) if spec.dependencies else '# 无额外依赖'}
```

## 使用

```python
from {spec.name}_skill import {spec.name.replace('-', '_').title().replace('_', '')}Skill

skill = {spec.name.replace('-', '_').title().replace('_', '')}Skill()
result = skill.execute(action="run")
print(result)
```

## 配置

编辑 `config/config.yaml` 进行自定义配置。

---
*由 Leo AI Skill Code Generator 自动生成*
"""

    @staticmethod
    def _gen_init(spec: SkillSpec) -> str:
        cls = spec.name.replace("-", "_").title().replace("_", "") + "Skill"
        return f'"""\n{spec.name}_skill\n\n{spec.description}\n"""\n\nfrom .{spec.name}_skill import {cls}\n\n__all__ = ["{cls}"]\n'

    @staticmethod
    def _gen_main_skill(spec: SkillSpec) -> str:
        cls = spec.name.replace("-", "_").title().replace("_", "") + "Skill"
        snake = spec.name.replace("-", "_")
        return f'''"""
{spec.description}
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from leo_skills.core.base_executor import BaseExecutor

logger = logging.getLogger(__name__)


class {cls}(BaseExecutor):
    """{spec.description}

    支持的操作：
        - run:    执行核心功能
        - status: 查看状态
    """

    def __init__(self) -> None:
        self.name = "{snake}_skill"
        self._config: Optional[Dict[str, Any]] = None

    def execute(
        self,
        action: str = "run",
        context: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = dict(context or {{}})
        params.update(kwargs)

        if action == "run":
            return self._action_run(params)
        elif action == "status":
            return {{"status": "success", "name": self.name, "version": "{spec.version}"}}
        else:
            return {{"status": "error", "message": f"未知操作: {{action}}"}}

    def _action_run(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """核心执行逻辑。"""
        logger.info(f"{{self.name}} 开始执行")
        try:
            # TODO: 实现核心逻辑
            result = self._process(params)
            logger.info(f"{{self.name}} 执行完成")
            return {{"status": "success", "data": result}}
        except Exception as e:
            logger.error(f"{{self.name}} 执行失败: {{e}}")
            return {{"status": "error", "error": str(e)}}

    def _process(self, params: Dict[str, Any]) -> Any:
        """核心处理方法（TODO: 实现具体逻辑）。"""
        raise NotImplementedError("请实现 _process 方法")

    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件。"""
        if self._config is not None:
            return self._config
        config_path = Path(__file__).parent / "config" / "config.yaml"
        if config_path.exists():
            try:
                import yaml
                with open(config_path, "r", encoding="utf-8") as f:
                    self._config = yaml.safe_load(f) or {{}}
            except Exception:
                self._config = {{}}
        else:
            self._config = {{}}
        return self._config


__all__ = ["{cls}"]
'''

    @staticmethod
    def _gen_scripts_main(spec: SkillSpec) -> str:
        cls = spec.name.replace("-", "_").title().replace("_", "") + "Skill"
        return f'''#!/usr/bin/env python3
"""
{spec.name} - CLI 入口
"""

import argparse
import sys


def main():
    parser = argparse.ArgumentParser(description="{spec.description}")
    parser.add_argument("command", choices=["run", "status"], help="执行命令")
    args = parser.parse_args()

    from {spec.name}_skill import {cls}
    skill = {cls}()
    result = skill.execute(action=args.command)
    print(result)
    return 0 if result.get("status") == "success" else 1


if __name__ == "__main__":
    sys.exit(main())
'''

    @staticmethod
    def _gen_config_yaml(spec: SkillSpec) -> str:
        return f"""# {spec.name} 配置
enabled: true
version: "{spec.version}"

# 自定义配置项
settings:
  log_level: INFO
"""

    @staticmethod
    def _gen_test(spec: SkillSpec) -> str:
        cls = spec.name.replace("-", "_").title().replace("_", "") + "Skill"
        return f'''"""
{spec.name}_skill 单元测试
"""

import pytest


class Test{cls}:
    """测试 {cls}。"""

    def test_init(self):
        """测试初始化。"""
        from {spec.name}_skill import {cls}
        skill = {cls}()
        assert skill.name == "{spec.name.replace("-", "_")}_skill"

    def test_status(self):
        """测试状态查询。"""
        from {spec.name}_skill import {cls}
        skill = {cls}()
        result = skill.execute(action="status")
        assert result["status"] == "success"

    def test_unknown_action(self):
        """测试未知操作。"""
        from {spec.name}_skill import {cls}
        skill = {cls}()
        result = skill.execute(action="unknown_xyz")
        assert result["status"] == "error"
'''

    # ------------------------------------------------------------------ #
    #  工具方法
    # ------------------------------------------------------------------ #

    @staticmethod
    def _normalize_name(name: str) -> str:
        """规范化技能名称为 snake_case。"""
        name = re.sub(r"[^a-zA-Z0-9\u4e00-\u9fff]+", "_", name).strip("_").lower()
        name = re.sub(r"_+", "_", name)
        # 移除 -cskill / _skill 后缀
        for suffix in ("_cskill", "-cskill", "_skill", "-skill"):
            if name.endswith(suffix):
                name = name[:-len(suffix)]
        return name or "unnamed"

    @staticmethod
    def _write(path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


__all__ = ["SkillCodeGenerator"]
