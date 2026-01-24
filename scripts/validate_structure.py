#!/usr/bin/env python3
"""
项目结构验证脚本
功能：验证项目结构的一致性，防止命名和路径问题
"""
from pathlib import Path
import sys


class ProjectValidator:
    """项目结构验证器"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.errors = []
        self.warnings = []

    def validate_all(self):
        """执行所有验证"""
        print("=" * 60)
        print("项目结构验证")
        print("=" * 60)

        self.validate_naming_convention()
        self.validate_required_files()
        self.validate_skill_structure()
        self.validate_no_legacy_names()
        self.print_report()

        return len(self.errors) == 0

    def validate_naming_convention(self):
        """验证命名规范：所有目录应使用下划线而非连字符"""
        print("\n[检查] 目录命名规范...")

        # 检查顶层目录
        for item in self.project_root.iterdir():
            if not item.is_dir():
                continue

            # 跳过特殊目录
            skip_patterns = [
                ".",  # 隐藏目录
                "archive", "docs", "tests", "scripts", "examples",  # 标准目录
                "__pycache__",  # Python 缓存
                "node_modules",  # Node.js
                ".egg-info",  # Python 包信息（后缀匹配）
                "demo-",  # demo 目录可以使用连字符
            ]

            should_skip = False
            for pattern in skip_patterns:
                if item.name.startswith(pattern) or item.name.endswith(pattern):
                    should_skip = True
                    break

            if should_skip:
                continue

            # 检查 leo_ 开头的目录
            if item.name.startswith("leo"):
                if "-" in item.name:
                    self.errors.append(
                        f"目录使用连字符: {item.name} (应使用下划线，如 leo_xxx)"
                    )
                elif not item.name.startswith("leo_"):
                    self.warnings.append(
                        f"目录命名不规范: {item.name} (建议使用 leo_xxx 格式)"
                    )

    def validate_required_files(self):
        """验证必需文件存在"""
        print("[检查] 必需文件...")

        required_files = [
            "README.md",
            "CLAUDE.md",
            ".gitignore",
            "requirements.txt",
            "leo_system.py",  # 注意：使用下划线
        ]

        for file_name in required_files:
            file_path = self.project_root / file_name
            if not file_path.exists():
                self.errors.append(f"缺少必需文件: {file_name}")

    def validate_skill_structure(self):
        """验证技能结构"""
        print("[检查] 技能结构...")

        skills_dir = self.project_root / "leo_skills"
        if not skills_dir.exists():
            self.errors.append("leo_skills 目录不存在")
            return

        # 遍历所有技能
        for category_dir in skills_dir.iterdir():
            if not category_dir.is_dir() or category_dir.name.startswith("."):
                continue

            for skill_dir in category_dir.iterdir():
                if not skill_dir.is_dir() or skill_dir.name.startswith("."):
                    continue

                # 跳过特殊目录
                if skill_dir.name in ["__pycache__", "node_modules", ".pytest_cache"]:
                    continue

                # 检查技能必需文件
                skill_md = skill_dir / "SKILL.md"
                main_py = skill_dir / "scripts" / "main.py"

                if not skill_md.exists():
                    self.warnings.append(
                        f"技能缺少 SKILL.md: {skill_dir.name}"
                    )

                if not main_py.exists():
                    self.warnings.append(
                        f"技能缺少 scripts/main.py: {skill_dir.name}"
                    )

    def validate_no_legacy_names(self):
        """验证没有遗留的旧命名"""
        print("[检查] 遗留命名...")

        # 检查是否存在使用连字符的旧文件
        legacy_patterns = [
            "leo-system.py",
            "leo-skills",
            "leo-subagents",
            "leo-workflows",
        ]

        for pattern in legacy_patterns:
            path = self.project_root / pattern
            if path.exists():
                self.errors.append(
                    f"发现遗留文件/目录: {pattern} (应使用下划线命名)"
                )

    def print_report(self):
        """打印验证报告"""
        print("\n" + "=" * 60)
        print("验证报告")
        print("=" * 60)

        if self.errors:
            print(f"\n[错误] 发现 {len(self.errors)} 个错误:")
            for error in self.errors:
                print(f"  - {error}")

        if self.warnings:
            print(f"\n[警告] 发现 {len(self.warnings)} 个警告:")
            for warning in self.warnings:
                print(f"  - {warning}")

        if not self.errors and not self.warnings:
            print("\n[成功] 所有检查通过！")
        elif not self.errors:
            print(f"\n[成功] 无错误，但有 {len(self.warnings)} 个警告")
        else:
            print(f"\n[失败] 发现 {len(self.errors)} 个错误")

        print("=" * 60)


def main():
    """主函数"""
    validator = ProjectValidator()
    success = validator.validate_all()

    if not success:
        print("\n建议：运行 'python scripts/fix_structure.py' 自动修复问题")
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
