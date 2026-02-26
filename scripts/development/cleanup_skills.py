#!/usr/bin/env python3
"""
技能库清理脚本
功能：分析和清理leo_skills目录中的无效技能
"""
import shutil
from pathlib import Path
import argparse


class SkillCleaner:
    """技能清理器"""

    def __init__(self, skills_dir: str, dry_run: bool = True):
        self.skills_dir = Path(skills_dir)
        self.dry_run = dry_run
        self.archive_dir = Path("archive/skills")
        self.report = {
            "total_skills": 0,
            "valid_skills": [],
            "invalid_skills": [],
            "backup_dirs": [],
            "large_files": [],
            "total_size_before": 0,
            "total_size_after": 0,
        }

    def analyze(self):
        """分析技能库"""
        print("[分析] 开始分析技能库...")
        print(f"[目录] {self.skills_dir}")
        print("-" * 60)

        # 计算总大小
        self.report["total_size_before"] = self._get_dir_size(self.skills_dir)
        print(f"[大小] 当前大小: {self._format_size(self.report['total_size_before'])}")

        # 遍历所有技能目录
        for category_dir in self.skills_dir.iterdir():
            if not category_dir.is_dir() or category_dir.name.startswith("."):
                continue

            for skill_dir in category_dir.iterdir():
                if not skill_dir.is_dir():
                    continue

                self.report["total_skills"] += 1
                self._analyze_skill(skill_dir)

        self._print_report()

    def _analyze_skill(self, skill_dir: Path):
        """分析单个技能"""
        skill_name = skill_dir.name

        # 检查是否是备份目录
        if ".backup" in skill_name or skill_name.startswith("."):
            self.report["backup_dirs"].append(str(skill_dir))
            return

        # 检查必需文件
        has_skill_md = (skill_dir / "SKILL.md").exists()
        has_main_py = (skill_dir / "scripts" / "main.py").exists()
        has_readme = (skill_dir / "README.md").exists()

        # 计算目录大小
        size = self._get_dir_size(skill_dir)

        # 判断是否有效
        is_valid = has_skill_md and has_main_py

        skill_info = {
            "name": skill_name,
            "path": str(skill_dir),
            "has_skill_md": has_skill_md,
            "has_main_py": has_main_py,
            "has_readme": has_readme,
            "size": size,
            "size_formatted": self._format_size(size),
        }

        if is_valid:
            self.report["valid_skills"].append(skill_info)
        else:
            self.report["invalid_skills"].append(skill_info)

        # 检查大文件
        if size > 50 * 1024 * 1024:  # 超过50MB
            self.report["large_files"].append(skill_info)

    def _get_dir_size(self, path: Path) -> int:
        """计算目录大小"""
        total = 0
        try:
            for item in path.rglob("*"):
                if item.is_file():
                    total += item.stat().st_size
        except Exception:
            pass
        return total

    def _format_size(self, size: int) -> str:
        """格式化文件大小"""
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} TB"

    def _print_report(self):
        """打印分析报告"""
        print("\n" + "=" * 60)
        print("[报告] 分析报告")
        print("=" * 60)

        print(f"\n[有效] 有效技能: {len(self.report['valid_skills'])}")
        for skill in self.report["valid_skills"]:
            print(f"  - {skill['name']} ({skill['size_formatted']})")

        print(f"\n[无效] 无效技能: {len(self.report['invalid_skills'])}")
        for skill in self.report["invalid_skills"]:
            missing = []
            if not skill["has_skill_md"]:
                missing.append("SKILL.md")
            if not skill["has_main_py"]:
                missing.append("main.py")
            print(f"  - {skill['name']} (缺少: {', '.join(missing)})")

        print(f"\n[备份] 备份目录: {len(self.report['backup_dirs'])}")
        for backup in self.report["backup_dirs"]:
            print(f"  - {backup}")

        print(f"\n[大文件] 大文件技能 (>50MB): {len(self.report['large_files'])}")
        for skill in self.report["large_files"]:
            print(f"  - {skill['name']} ({skill['size_formatted']})")

        print(f"\n[总大小] 总大小: {self._format_size(self.report['total_size_before'])}")

        # 计算预期清理后的大小
        cleanup_size = sum(
            skill["size"] for skill in self.report["invalid_skills"]
        )
        for backup in self.report["backup_dirs"]:
            cleanup_size += self._get_dir_size(Path(backup))

        expected_size = self.report["total_size_before"] - cleanup_size
        print(f"[预期] 清理后: {self._format_size(expected_size)}")
        print(f"[节省] 节省空间: {self._format_size(cleanup_size)} ({cleanup_size / self.report['total_size_before'] * 100:.1f}%)")

    def cleanup(self):
        """执行清理"""
        if self.dry_run:
            print("\n[警告] DRY RUN 模式 - 不会实际删除文件")
            return

        print("\n[清理] 开始清理...")

        # 创建归档目录
        self.archive_dir.mkdir(parents=True, exist_ok=True)

        # 清理无效技能
        for skill in self.report["invalid_skills"]:
            skill_path = Path(skill["path"])
            archive_path = self.archive_dir / skill_path.name

            print(f"[归档] {skill['name']}")
            shutil.move(str(skill_path), str(archive_path))

        # 删除备份目录
        for backup in self.report["backup_dirs"]:
            backup_path = Path(backup)
            print(f"[删除] {backup_path}")
            shutil.rmtree(backup_path)

        print("\n[完成] 清理完成！")


def main():
    parser = argparse.ArgumentParser(description="技能库清理工具")
    parser.add_argument(
        "--skills-dir",
        default="leo_skills",
        help="技能目录路径 (默认: leo_skills)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="预览模式，不实际删除文件",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="执行清理",
    )

    args = parser.parse_args()

    cleaner = SkillCleaner(args.skills_dir, dry_run=not args.execute)
    cleaner.analyze()

    if args.execute:
        confirm = input("\n[警告] 确认执行清理？(yes/no): ")
        if confirm.lower() == "yes":
            cleaner.cleanup()
        else:
            print("[取消] 取消清理")


if __name__ == "__main__":
    main()
