# -*- coding: utf-8 -*-
"""
bootstrap_skill - Bootstrap 引导技能

在现有代码库中启动新功能时使用，跳过完整规格工作流。
扫描代码库，理解现有模式，创建有针对性的功能规格和执行计划。
"""
from leo_skills.core.base_executor import BaseExecutor

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class CodebasePattern:
    """代码库模式"""
    language: str
    framework: str
    patterns: List[str] = field(default_factory=list)
    related_files: List[str] = field(default_factory=list)
    testing_approach: str = ""


@dataclass
class FeaturePlan:
    """功能计划"""
    name: str
    description: str
    feature_dir: str
    spec_content: str = ""
    plan_content: str = ""
    files_created: List[str] = field(default_factory=list)


@dataclass
class BootstrapResult:
    """引导结果"""
    status: str
    feature_name: str = ""
    feature_path: str = ""
    codebase_patterns: Optional[CodebasePattern] = None
    unfinished_plans: List[str] = field(default_factory=list)
    message: str = ""


class BootstrapSkill(BaseExecutor):
    """
    Bootstrap 引导技能

    用于在现有代码库中启动新功能，扫描代码库理解现有模式，
    创建有针对性的功能规格和执行计划。
    """

    def __init__(self):
        self.name = "bootstrap_skill"
        self.version = "1.0.0"
        self.description = "在现有代码库中生成代码感知的引导计划"
        self.category = "scaffold"

    def execute(
        self,
        user_description: str,
        project_root: str = ".",
        feature_name: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        执行引导技能

        Args:
            user_description: 用户的功能描述
            project_root: 项目根目录
            feature_name: 功能名称（可选，自动推导）

        Returns:
            引导结果
        """
        try:
            # 步骤1: 代码库扫描
            patterns = self._scan_codebase(project_root)

            # 步骤2: 检查未完成的计划
            unfinished = self._check_unfinished_plans(project_root)

            # 步骤3: 推导功能名称
            if not feature_name:
                feature_name = self._derive_feature_name(user_description)

            # 步骤4: 创建功能目录和文档
            feature_path = self._create_feature_directory(
                project_root, feature_name, user_description, patterns
            )

            result = BootstrapResult(
                status="completed",
                feature_name=feature_name,
                feature_path=feature_path,
                codebase_patterns=patterns,
                unfinished_plans=unfinished,
                message=f"功能计划已创建: {feature_path}"
            )

            return {
                "status": "success",
                "result": result,
                "next_steps": [
                    f"1. 查看功能规格: {feature_path}/FEATURE_SPEC.md",
                    f"2. 查看执行计划: {feature_path}/EXECUTION_PLAN.md",
                    "3. 运行 fresh-start 加载上下文",
                    "4. 运行 phase-start 1 开始第一阶段"
                ]
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "skill": self.name
            }

    def _scan_codebase(self, project_root: str) -> CodebasePattern:
        """扫描代码库"""
        patterns = CodebasePattern(
            language="Python",
            framework="Unknown",
            patterns=[],
            related_files=[],
            testing_approach="pytest"
        )

        # 检测技术栈
        root = Path(project_root)

        if (root / "package.json").exists():
            patterns.language = "JavaScript/TypeScript"
            patterns.framework = self._detect_js_framework(root)
        elif (root / "requirements.txt").exists() or (root / "pyproject.toml").exists():
            patterns.language = "Python"
            patterns.framework = self._detect_python_framework(root)

        # 检测测试方法
        if (root / "pytest.ini").exists() or (root / "setup.py").exists():
            patterns.testing_approach = "pytest"
        elif (root / "package.json").exists():
            patterns.testing_approach = "jest/vitest"

        return patterns

    def _detect_js_framework(self, root: Path) -> str:
        """检测JS框架"""
        pkg = root / "package.json"
        if pkg.exists():
            content = pkg.read_text()
            if "next" in content:
                return "Next.js"
            elif "react" in content:
                return "React"
            elif "vue" in content:
                return "Vue"
        return "Unknown"

    def _detect_python_framework(self, root: Path) -> str:
        """检测Python框架"""
        req = root / "requirements.txt"
        if req.exists():
            content = req.read_text()
            if "fastapi" in content:
                return "FastAPI"
            elif "flask" in content:
                return "Flask"
            elif "django" in content:
                return "Django"
        return "Unknown"

    def _check_unfinished_plans(self, project_root: str) -> List[str]:
        """检查未完成的执行计划"""
        unfinished = []
        root = Path(project_root)

        # 查找所有 EXECUTION_PLAN.md
        for plan_file in root.rglob("EXECUTION_PLAN.md"):
            # 简单检查是否有未完成的任务
            content = plan_file.read_text()
            if "- [ ]" in content:
                unfinished.append(str(plan_file.relative_to(root)))

        return unfinished[:5]  # 最多返回5个

    def _derive_feature_name(self, description: str) -> str:
        """从描述推导功能名称"""
        # 提取关键词
        words = description.lower().split()
        keywords = [w for w in words if len(w) > 3 and w not in [
            "this", "that", "with", "from", "add", "the", "for", "and"
        ]]

        if keywords:
            return "-".join(keywords[:3])
        return "new-feature"

    def _create_feature_directory(
        self,
        project_root: str,
        feature_name: str,
        description: str,
        patterns: CodebasePattern
    ) -> str:
        """创建功能目录和文档"""
        root = Path(project_root)
        features_dir = root / "features"
        features_dir.mkdir(exist_ok=True)

        feature_dir = features_dir / feature_name
        feature_dir.mkdir(exist_ok=True)

        # 创建 FEATURE_SPEC.md
        spec_content = self._generate_feature_spec(feature_name, description, patterns)
        (feature_dir / "FEATURE_SPEC.md").write_text(spec_content)

        # 创建 EXECUTION_PLAN.md
        plan_content = self._generate_execution_plan(feature_name, patterns)
        (feature_dir / "EXECUTION_PLAN.md").write_text(plan_content)

        return str(feature_dir)

    def _generate_feature_spec(
        self,
        feature_name: str,
        description: str,
        patterns: CodebasePattern
    ) -> str:
        """生成功能规格文档"""
        return f"""# {feature_name} 功能规格

## 概述

{description}

## 技术栈

- 语言: {patterns.language}
- 框架: {patterns.framework}
- 测试: {patterns.testing_approach}

## 验收标准

- [ ] 功能实现完成
- [ ] 测试覆盖
- [ ] 代码审查通过

## 注意事项

- 遵循现有代码模式
- 保持向后兼容
"""

    def _generate_execution_plan(
        self,
        feature_name: str,
        patterns: CodebasePattern
    ) -> str:
        """生成执行计划文档"""
        return f"""# {feature_name} 执行计划

## 阶段 1: 准备

- [ ] 创建必要的文件结构
- [ ] 编写失败的测试

## 阶段 2: 实现

- [ ] 实现核心功能
- [ ] 验证测试通过

## 阶段 3: 完善

- [ ] 代码重构
- [ ] 文档更新

---

基于 {patterns.language}/{patterns.framework} 技术栈生成
"""


def main():
    """入口函数"""
    return BootstrapSkill()


if __name__ == "__main__":
    skill = main()
