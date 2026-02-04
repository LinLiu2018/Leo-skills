#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
技能进化助手 - 自动为所有技能添加进化能力的元技能

功能：
1. 自动扫描所有现有技能
2. 识别未集成进化框架的技能
3. 自动改造技能代码
4. 添加必要的配置文件
5. 验证改造结果
"""

import sys
import os
import re
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

# 添加leo-skills到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.evolution import EvolvableSkill


@dataclass
class SkillInfo:
    """技能信息"""
    name: str
    path: Path
    category: str
    has_evolution: bool
    main_file: Optional[Path] = None
    config_file: Optional[Path] = None


class SkillEvolutionAssistant(EvolvableSkill):
    """技能进化助手 - 自动为技能添加进化能力"""

    def __init__(self):
        super().__init__(
            skill_name="skill-evolution-assistant",
            config_path=str(Path(__file__).parent / "config" / "config.yaml")
        )
        self.skills_root = Path(__file__).parent.parent.parent
        self.categories = ["content-creation", "data-analysis", "utilities", "tools", "automation"]

    def _execute_core(self, action: str = "scan", **kwargs) -> Dict[str, Any]:
        """
        核心执行逻辑

        Actions:
        - scan: 扫描所有技能
        - analyze: 分析哪些技能需要改造
        - transform: 自动改造技能
        - transform_all: 改造所有未集成的技能
        """
        if action == "scan":
            return self.scan_skills()
        elif action == "analyze":
            return self.analyze_skills()
        elif action == "transform":
            skill_name = kwargs.get("skill_name")
            if not skill_name:
                return {"success": False, "error": "skill_name is required"}
            return self.transform_skill(skill_name)
        elif action == "transform_all":
            return self.transform_all_skills()
        else:
            return {"success": False, "error": f"Unknown action: {action}"}

    def scan_skills(self) -> Dict[str, Any]:
        """扫描所有技能"""
        skills = []

        for category in self.categories:
            category_path = self.skills_root / category
            if not category_path.exists():
                continue

            for skill_dir in category_path.iterdir():
                if not skill_dir.is_dir() or not skill_dir.name.endswith("-cskill"):
                    continue

                skill_info = self._analyze_skill(skill_dir, category)
                skills.append(skill_info)

        return {
            "success": True,
            "total_skills": len(skills),
            "skills": [self._skill_to_dict(s) for s in skills],
            "quality_score": 1.0
        }

    def analyze_skills(self) -> Dict[str, Any]:
        """分析哪些技能需要改造"""
        scan_result = self.scan_skills()
        skills = [self._dict_to_skill_info(s) for s in scan_result["skills"]]

        needs_evolution = [s for s in skills if not s.has_evolution]
        has_evolution = [s for s in skills if s.has_evolution]

        return {
            "success": True,
            "total_skills": len(skills),
            "needs_evolution": len(needs_evolution),
            "has_evolution": len(has_evolution),
            "needs_evolution_list": [s.name for s in needs_evolution],
            "has_evolution_list": [s.name for s in has_evolution],
            "quality_score": len(has_evolution) / len(skills) if skills else 0
        }

    def transform_skill(self, skill_name: str) -> Dict[str, Any]:
        """自动改造单个技能"""
        # 查找技能
        skill_info = self._find_skill(skill_name)
        if not skill_info:
            return {"success": False, "error": f"Skill not found: {skill_name}"}

        if skill_info.has_evolution:
            return {"success": False, "error": f"Skill already has evolution: {skill_name}"}

        # 执行改造
        try:
            # 1. 备份原文件
            self._backup_skill(skill_info)

            # 2. 改造主文件
            if skill_info.main_file:
                self._transform_main_file(skill_info)

            # 3. 添加进化配置
            self._add_evolution_config(skill_info)

            # 4. 验证改造
            validation = self._validate_transformation(skill_info)

            return {
                "success": True,
                "skill_name": skill_name,
                "transformed": True,
                "validation": validation,
                "quality_score": 0.9 if validation["valid"] else 0.5
            }

        except Exception as e:
            # 回滚
            self._rollback_skill(skill_info)
            return {
                "success": False,
                "error": str(e),
                "quality_score": 0.0
            }

    def transform_all_skills(self) -> Dict[str, Any]:
        """自动改造所有未集成的技能"""
        analyze_result = self.analyze_skills()
        needs_evolution = analyze_result["needs_evolution_list"]

        results = []
        for skill_name in needs_evolution:
            result = self.transform_skill(skill_name)
            results.append({
                "skill": skill_name,
                "success": result["success"],
                "error": result.get("error")
            })

        success_count = sum(1 for r in results if r["success"])

        return {
            "success": True,
            "total_transformed": len(results),
            "successful": success_count,
            "failed": len(results) - success_count,
            "results": results,
            "quality_score": success_count / len(results) if results else 0
        }

    def _analyze_skill(self, skill_dir: Path, category: str) -> SkillInfo:
        """分析单个技能"""
        # 查找主文件
        main_file = None
        scripts_dir = skill_dir / "scripts"
        if scripts_dir.exists():
            main_py = scripts_dir / "main.py"
            if main_py.exists():
                main_file = main_py
        else:
            # 查找根目录的.py文件
            py_files = list(skill_dir.glob("*.py"))
            if py_files:
                main_file = py_files[0]

        # 检查是否已集成进化框架
        has_evolution = False
        if main_file and main_file.exists():
            content = main_file.read_text(encoding="utf-8")
            has_evolution = "EvolvableSkill" in content or "BaseSkill" in content

        # 查找配置文件
        config_file = None
        config_dir = skill_dir / "config"
        if config_dir.exists():
            config_yaml = config_dir / "config.yaml"
            if config_yaml.exists():
                config_file = config_yaml

        return SkillInfo(
            name=skill_dir.name,
            path=skill_dir,
            category=category,
            has_evolution=has_evolution,
            main_file=main_file,
            config_file=config_file
        )

    def _find_skill(self, skill_name: str) -> Optional[SkillInfo]:
        """查找技能"""
        scan_result = self.scan_skills()
        for skill_dict in scan_result["skills"]:
            if skill_dict["name"] == skill_name:
                skill_info = self._dict_to_skill_info(skill_dict)
                # 重新分析以获取完整信息
                return self._analyze_skill(skill_info.path, skill_info.category)
        return None

    def _backup_skill(self, skill_info: SkillInfo):
        """备份技能文件"""
        backup_dir = skill_info.path / ".backup"
        backup_dir.mkdir(exist_ok=True)

        if skill_info.main_file:
            shutil.copy2(skill_info.main_file, backup_dir / skill_info.main_file.name)

    def _rollback_skill(self, skill_info: SkillInfo):
        """回滚技能文件"""
        backup_dir = skill_info.path / ".backup"
        if not backup_dir.exists():
            return

        if skill_info.main_file:
            backup_file = backup_dir / skill_info.main_file.name
            if backup_file.exists():
                shutil.copy2(backup_file, skill_info.main_file)

    def _transform_main_file(self, skill_info: SkillInfo):
        """改造主文件"""
        if not skill_info.main_file:
            return

        content = skill_info.main_file.read_text(encoding="utf-8")

        # 1. 添加import
        if "from core.evolution import EvolvableSkill" not in content:
            # 在文件开头添加import
            import_line = "\nfrom core.evolution import EvolvableSkill\n"
            # 找到第一个class定义的位置
            class_match = re.search(r"^class\s+\w+", content, re.MULTILINE)
            if class_match:
                insert_pos = class_match.start()
                content = content[:insert_pos] + import_line + content[insert_pos:]

        # 2. 修改类继承
        # 查找类定义
        class_pattern = r"class\s+(\w+)(\([^)]*\))?"
        match = re.search(class_pattern, content)
        if match:
            class_name = match.group(1)
            old_inheritance = match.group(2) or "()"

            # 替换为继承EvolvableSkill
            new_inheritance = "(EvolvableSkill)"
            content = content.replace(
                f"class {class_name}{old_inheritance}",
                f"class {class_name}{new_inheritance}"
            )

        # 3. 修改__init__方法
        # 添加super().__init__调用
        init_pattern = r"def __init__\(self[^)]*\):"
        if re.search(init_pattern, content):
            # 在__init__开头添加super调用
            init_super = f"""
        super().__init__(
            skill_name="{skill_info.name}",
            config_path=str(Path(__file__).parent.parent / "config" / "config.yaml")
        )
"""
            content = re.sub(
                r"(def __init__\(self[^)]*\):)\s*\n",
                r"\1\n" + init_super,
                content,
                count=1
            )

        # 4. 重命名主方法为_execute_core
        # 查找主要的执行方法（如run, execute, process等）
        for method_name in ["run", "execute", "process", "main"]:
            pattern = f"def {method_name}\\(self"
            if re.search(pattern, content):
                content = re.sub(
                    f"def {method_name}\\(self",
                    "def _execute_core(self",
                    content,
                    count=1
                )
                break

        # 保存修改后的文件
        skill_info.main_file.write_text(content, encoding="utf-8")

    def _add_evolution_config(self, skill_info: SkillInfo):
        """添加进化配置文件"""
        config_dir = skill_info.path / "config"
        config_dir.mkdir(exist_ok=True)

        evolution_config_path = config_dir / "evolution_config.yaml"
        if evolution_config_path.exists():
            return

        # 复制模板
        template_path = self.skills_root / "core" / "evolution" / "config" / "evolution_config_template.yaml"
        if template_path.exists():
            shutil.copy2(template_path, evolution_config_path)

    def _validate_transformation(self, skill_info: SkillInfo) -> Dict[str, Any]:
        """验证改造结果"""
        if not skill_info.main_file:
            return {"valid": False, "error": "No main file"}

        content = skill_info.main_file.read_text(encoding="utf-8")

        checks = {
            "has_import": "EvolvableSkill" in content,
            "has_inheritance": re.search(r"class\s+\w+\(EvolvableSkill\)", content) is not None,
            "has_execute_core": "_execute_core" in content,
            "has_evolution_config": (skill_info.path / "config" / "evolution_config.yaml").exists()
        }

        return {
            "valid": all(checks.values()),
            "checks": checks
        }

    def _skill_to_dict(self, skill_info: SkillInfo) -> Dict[str, Any]:
        """将SkillInfo转换为字典"""
        return {
            "name": skill_info.name,
            "path": str(skill_info.path),
            "category": skill_info.category,
            "has_evolution": skill_info.has_evolution,
            "main_file": str(skill_info.main_file) if skill_info.main_file else None,
            "config_file": str(skill_info.config_file) if skill_info.config_file else None
        }

    def _dict_to_skill_info(self, skill_dict: Dict[str, Any]) -> SkillInfo:
        """从字典重建SkillInfo，将字符串路径转换回Path对象"""
        return SkillInfo(
            name=skill_dict["name"],
            path=Path(skill_dict["path"]),
            category=skill_dict["category"],
            has_evolution=skill_dict["has_evolution"],
            main_file=Path(skill_dict["main_file"]) if skill_dict.get("main_file") else None,
            config_file=Path(skill_dict["config_file"]) if skill_dict.get("config_file") else None
        )


def main():
    """主函数"""
    import sys

    assistant = SkillEvolutionAssistant()

    if len(sys.argv) < 2:
        print("用法: python skill_evolution_assistant.py <action> [skill_name]")
        print("Actions:")
        print("  scan          - 扫描所有技能")
        print("  analyze       - 分析哪些技能需要改造")
        print("  transform <skill_name> - 改造指定技能")
        print("  transform_all - 改造所有未集成的技能")
        return

    action = sys.argv[1]
    kwargs = {}

    if action == "transform" and len(sys.argv) > 2:
        kwargs["skill_name"] = sys.argv[2]

    result = assistant.execute(action=action, **kwargs)

    import json
    print(json.dumps(result.data, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
