"""
Agent 技能创建工具

创建和导出 Claude Code 技能，支持验证技能结构、生成安装指南、
打包 Desktop/API 变体的 zip 包。
"""

from __future__ import annotations

import os
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from leo_skills.core.base_executor import BaseExecutor


# 导出时排除的目录和文件
_EXCLUDE_DIRS = {
    ".git", "__pycache__", "node_modules", ".claude-plugin",
    "venv", "env", ".venv", ".pytest_cache", ".mypy_cache", "dist", "build",
}
_EXCLUDE_FILES = {
    ".DS_Store", ".gitignore", "Thumbs.db", ".env",
    "credentials.json", "secrets.json", "api_keys.json",
}
_EXCLUDE_EXTS = {".pyc", ".pyo", ".log"}

# SKILL.md 校验限制
_MAX_NAME_LEN = 64
_MAX_DESC_LEN = 1024
# API 包大小限制（8 MB）
_MAX_API_SIZE = 8 * 1024 * 1024


class AgentSkillCreator(BaseExecutor):
    """Agent 技能创建工具。

    支持的操作：
        - validate: 验证技能目录结构
        - export:   导出技能包（desktop / api / both）
        - create:   创建新技能骨架
    """

    def __init__(self) -> None:
        self.name = "agent_skill_creator_skill"

    # ------------------------------------------------------------------ #
    #  BaseExecutor 接口
    # ------------------------------------------------------------------ #

    def execute(
        self,
        action: str = "validate",
        context: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = dict(context or {})
        params.update(kwargs)

        if action in ("validate", "run"):
            return self._action_validate(params)
        elif action == "export":
            return self._action_export(params)
        elif action == "create":
            return self._action_create(params)
        else:
            return {"status": "error", "message": f"未知操作: {action}"}

    # ------------------------------------------------------------------ #
    #  验证
    # ------------------------------------------------------------------ #

    def _action_validate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        skill_path = params.get("skill_path", ".")
        valid, issues = self.validate_skill(skill_path)
        return {
            "status": "success" if valid else "error",
            "valid": valid,
            "issues": issues,
            "skill_path": skill_path,
        }

    def validate_skill(self, skill_path: str) -> Tuple[bool, List[str]]:
        """验证技能目录结构和 SKILL.md 格式。"""
        issues: List[str] = []
        path = Path(skill_path)

        if not path.exists():
            return False, [f"路径不存在: {skill_path}"]
        if not path.is_dir():
            return False, [f"不是目录: {skill_path}"]

        # 检查 SKILL.md
        skill_md = path / "SKILL.md"
        if not skill_md.exists():
            return False, ["缺少 SKILL.md 文件（必须）"]

        # 解析 frontmatter
        try:
            content = skill_md.read_text(encoding="utf-8")
            if not content.startswith("---"):
                issues.append("SKILL.md 缺少 frontmatter（必须以 --- 开头）")
            else:
                end = content.find("---", 3)
                if end == -1:
                    issues.append("SKILL.md frontmatter 未关闭（缺少第二个 ---）")
                else:
                    fm = content[3:end]
                    has_name = has_desc = False
                    for line in fm.split("\n"):
                        line = line.strip()
                        if line.startswith("name:"):
                            has_name = True
                            name_val = line.split(":", 1)[1].strip()
                            if len(name_val) > _MAX_NAME_LEN:
                                issues.append(f"name 过长: {len(name_val)} 字符（最大 {_MAX_NAME_LEN}）")
                        elif line.startswith("description:"):
                            has_desc = True
                            desc_val = line.split(":", 1)[1].strip()
                            if len(desc_val) > _MAX_DESC_LEN:
                                issues.append(f"description 过长: {len(desc_val)} 字符（最大 {_MAX_DESC_LEN}）")
                    if not has_name:
                        issues.append("SKILL.md frontmatter 缺少 'name:' 字段")
                    if not has_desc:
                        issues.append("SKILL.md frontmatter 缺少 'description:' 字段")
        except Exception as e:
            issues.append(f"读取 SKILL.md 出错: {e}")

        return len(issues) == 0, issues

    # ------------------------------------------------------------------ #
    #  导出
    # ------------------------------------------------------------------ #

    def _action_export(self, params: Dict[str, Any]) -> Dict[str, Any]:
        skill_path = params.get("skill_path", ".")
        variants = params.get("variants", ["desktop", "api"])
        version = params.get("version")
        output_dir = params.get("output_dir")

        return self.export_skill(skill_path, variants, version, output_dir)

    def export_skill(
        self,
        skill_path: str,
        variants: Optional[List[str]] = None,
        version_override: Optional[str] = None,
        output_dir: Optional[str] = None,
    ) -> Dict[str, Any]:
        """导出技能包。"""
        variants = variants or ["desktop", "api"]
        skill_path = os.path.abspath(skill_path)
        skill_name = os.path.basename(skill_path)

        # 验证
        valid, issues = self.validate_skill(skill_path)
        if not valid:
            return {"status": "error", "message": "技能验证失败", "issues": issues}

        # 确定版本
        version = self._detect_version(skill_path, version_override)

        # 输出目录
        if output_dir is None:
            output_dir = os.path.join(os.path.dirname(skill_path), "exports")
        os.makedirs(output_dir, exist_ok=True)

        results: Dict[str, Any] = {"status": "success", "version": version, "packages": {}}

        for variant in variants:
            pkg = self._create_package(skill_path, output_dir, variant, version, skill_name)
            results["packages"][variant] = pkg
            if not pkg["success"]:
                results["status"] = "warning"

        # 生成安装指南
        if any(p["success"] for p in results["packages"].values()):
            guide = self._generate_guide(skill_name, version, results["packages"], output_dir)
            results["guide_path"] = guide

        return results

    def _detect_version(self, skill_path: str, override: Optional[str] = None) -> str:
        """检测技能版本。"""
        if override:
            return override if override.startswith("v") else f"v{override}"

        # 从 SKILL.md frontmatter 读取
        skill_md = os.path.join(skill_path, "SKILL.md")
        if os.path.exists(skill_md):
            try:
                with open(skill_md, "r", encoding="utf-8") as f:
                    content = f.read()
                if content.startswith("---"):
                    end = content.find("---", 3)
                    if end > 0:
                        for line in content[3:end].split("\n"):
                            if line.strip().startswith("version:"):
                                v = line.split(":", 1)[1].strip()
                                return v if v.startswith("v") else f"v{v}"
            except Exception:
                pass
        return "v1.0.0"

    @staticmethod
    def _should_include(file_path: str, filename: str, variant: str) -> bool:
        """判断文件是否应该包含在导出包中。"""
        if filename in _EXCLUDE_FILES:
            return False
        _, ext = os.path.splitext(filename)
        if ext in _EXCLUDE_EXTS:
            return False
        if variant == "api":
            if ext == ".md" and filename not in ("SKILL.md", "README.md"):
                return False
            if "examples" in file_path.lower():
                return False
        return True

    def _create_package(
        self, skill_path: str, output_dir: str, variant: str, version: str, skill_name: str
    ) -> Dict[str, Any]:
        """创建 zip 包。"""
        zip_name = f"{skill_name}-{variant}-{version}.zip"
        zip_path = os.path.join(output_dir, zip_name)
        included: List[str] = []

        try:
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
                for root, dirs, files in os.walk(skill_path):
                    dirs[:] = [d for d in dirs if d not in _EXCLUDE_DIRS]
                    if variant == "api" and ".claude-plugin" in dirs:
                        dirs.remove(".claude-plugin")

                    for fname in files:
                        fpath = os.path.join(root, fname)
                        if not self._should_include(fpath, fname, variant):
                            continue
                        arcname = os.path.relpath(fpath, skill_path)
                        zf.write(fpath, arcname)
                        included.append(arcname)

            size = os.path.getsize(zip_path)
            size_mb = size / (1024 * 1024)

            if variant == "api" and size > _MAX_API_SIZE:
                return {
                    "success": False, "zip_path": zip_path, "size_mb": round(size_mb, 2),
                    "files_included": included,
                    "message": f"API 包过大: {size_mb:.2f} MB（最大 8 MB）",
                }

            return {
                "success": True, "zip_path": zip_path, "size_mb": round(size_mb, 2),
                "files_included": included,
                "message": f"打包成功: {len(included)} 个文件, {size_mb:.2f} MB",
            }
        except Exception as e:
            return {"success": False, "message": f"打包失败: {e}"}

    @staticmethod
    def _generate_guide(
        skill_name: str, version: str, packages: Dict, output_dir: str
    ) -> str:
        """生成安装指南。"""
        guide_path = os.path.join(output_dir, f"{skill_name}-{version}_INSTALL.md")
        lines = [
            f"# {skill_name} - 安装指南",
            f"\n**版本:** {version}",
            f"**生成时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "\n---\n",
        ]

        for variant, pkg in packages.items():
            if pkg.get("success"):
                lines.append(f"## {variant.capitalize()} 包")
                lines.append(f"- 文件: `{os.path.basename(pkg['zip_path'])}`")
                lines.append(f"- 大小: {pkg['size_mb']:.2f} MB")
                lines.append(f"- 文件数: {len(pkg['files_included'])}\n")

        lines.append("## 安装方法\n")
        lines.append("### Claude Desktop\n1. 打开 Claude Desktop\n2. 设置 → 技能 → 上传技能\n3. 选择 desktop 包\n")
        lines.append("### Claude API\n1. 使用 Anthropic SDK 上传 api 包\n2. 在请求中指定 skill_id\n")

        with open(guide_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return guide_path

    # ------------------------------------------------------------------ #
    #  创建新技能
    # ------------------------------------------------------------------ #

    def _action_create(self, params: Dict[str, Any]) -> Dict[str, Any]:
        name = params.get("name", "my-skill")
        description = params.get("description", "A new skill")
        output_dir = params.get("output_dir", ".")
        return self.create_skill(name, description, output_dir)

    def create_skill(self, name: str, description: str, output_dir: str = ".") -> Dict[str, Any]:
        """创建新的技能目录骨架。"""
        skill_dir = Path(output_dir) / f"{name}-cskill"
        skill_dir.mkdir(parents=True, exist_ok=True)

        # SKILL.md
        (skill_dir / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: {description}\n---\n\n# {name}\n\n{description}\n",
            encoding="utf-8",
        )

        # README.md
        (skill_dir / "README.md").write_text(
            f"# {name}\n\n{description}\n\n## 使用方法\n\nTODO\n",
            encoding="utf-8",
        )

        # scripts/main.py
        scripts_dir = skill_dir / "scripts"
        scripts_dir.mkdir(exist_ok=True)
        (scripts_dir / "__init__.py").write_text("", encoding="utf-8")
        (scripts_dir / "main.py").write_text(
            f'"""\n{name} - 主入口\n"""\n\n\ndef main():\n    print("{name} 启动")\n\n\nif __name__ == "__main__":\n    main()\n',
            encoding="utf-8",
        )

        # config
        config_dir = skill_dir / "config"
        config_dir.mkdir(exist_ok=True)
        (config_dir / "config.yaml").write_text(
            f"# {name} 配置\nenabled: true\n", encoding="utf-8"
        )

        return {
            "status": "success",
            "action": "create",
            "skill_name": name,
            "skill_path": str(skill_dir),
            "files_created": 5,
        }


__all__ = ["AgentSkillCreator"]
