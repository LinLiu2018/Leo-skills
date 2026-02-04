#!/usr/bin/env python3
"""
Leo AI System - 文件自动整理脚本

根据最佳实践规则自动分类和移动文件。

使用方法:
    python scripts/organize_files.py          # 预览模式（不实际移动）
    python scripts/organize_files.py --apply  # 执行移动
    python scripts/organize_files.py --check  # 只检查问题
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Tuple

# 项目根目录
ROOT = Path(__file__).parent.parent

# 文件分类规则
RULES: Dict[str, Dict[str, List[str]]] = {
    "identity": {
        "keywords": ["identity", "soul", "user", "character"],
        "extensions": [".md"],
        "files": ["IDENTITY.md", "SOUL.md", "USER.md"],
    },
    "reference": {
        "keywords": ["agent", "tool", "skill", "capability", "manifest"],
        "extensions": [".md"],
        "files": ["AGENTS.md", "TOOLS.md", "AGENT_CAPABILITIES.md", "SKILLS_MANIFEST.md"],
    },
    "guides": {
        "keywords": ["bootstrap", "contributing", "security", "changelog", "heartbeat", "install", "deploy"],
        "extensions": [".md"],
        "files": [],
    },
    "planning": {
        "keywords": ["task_plan", "implementation", "roadmap", "plan"],
        "extensions": [".md"],
        "files": [],
    },
    "progress": {
        "keywords": ["progress", "log", "timeline"],
        "extensions": [".md"],
        "files": ["progress.md"],
    },
    "research": {
        "keywords": ["research", "finding", "report", "analysis"],
        "extensions": [".md", ".py"],
        "files": ["findings.md"],
    },
}

# 保持根目录的文件
ROOT_FILES = [
    "CLAUDE.md",
    "README.md",
    "requirements.txt",
    "pyproject.toml",
    ".env",
    ".gitignore",
]


def should_keep_in_root(filename: str) -> bool:
    """检查文件是否应该保留在根目录"""
    if filename in ROOT_FILES:
        return True
    # 配置文件
    if filename.startswith(".") and not filename.endswith(".md"):
        return True
    # 源代码目录
    if filename in ["src", "projects", "docs", "leo_knowledge", ".claude", "scripts", "tests", "logs", "archive"]:
        return True
    return False


def categorize_file(filename: str) -> str:
    """根据规则对文件进行分类"""
    name_lower = filename.lower()

    # 检查是否应该保留在根目录
    if should_keep_in_root(filename):
        return "root"

    # 检查扩展名
    ext = Path(filename).suffix.lower()

    # 临时/自动生成的文件不移动
    if filename.endswith(".pyc") or "__pycache__" in filename:
        return "skip"
    if filename.startswith(".") and filename != ".env":
        return "skip"

    # 根据规则分类
    for category, rules in RULES.items():
        # 直接匹配文件名
        if filename in rules["files"]:
            return category
        # 关键词匹配
        for keyword in rules["keywords"]:
            if keyword in name_lower:
                # 扩展名匹配
                if ext in rules["extensions"]:
                    return category

    return "unknown"


def get_target_dir(category: str) -> Path:
    """获取目标目录"""
    if category == "root":
        return ROOT
    elif category == "research":
        # 如果是报告类文件，放到 reports 子目录
        return ROOT / "docs" / "research" / "reports"
    elif category in ["identity", "reference", "guides", "planning", "progress"]:
        return ROOT / "docs" / category
    return ROOT


def organize_files(dry_run: bool = True, apply_changes: bool = False) -> Tuple[List[str], List[str], List[str]]:
    """整理文件"""
    moved = []
    errors = []
    warnings = []

    # 扫描根目录
    for filename in os.listdir(ROOT):
        filepath = ROOT / filename

        # 跳过目录
        if filepath.is_dir():
            continue

        # 跳过特殊文件
        if should_keep_in_root(filename):
            continue

        # 分类文件
        category = categorize_file(filename)

        if category == "skip":
            continue

        if category == "root":
            continue

        if category == "unknown":
            warnings.append(f"未知文件: {filename}")
            continue

        # 获取目标目录
        target_dir = get_target_dir(category)

        # 确保目标目录存在
        if not target_dir.exists():
            target_dir.mkdir(parents=True, exist_ok=True)

        target_path = target_dir / filename

        # 检查是否已经在正确位置
        if filepath == target_path:
            continue

        # 移动文件
        action = "MOVE" if not dry_run else "WOULD MOVE"
        msg = f"{action}: {filename} -> docs/{category}/"

        if apply_changes or not dry_run:
            try:
                shutil.move(str(filepath), str(target_path))
                moved.append(msg)
            except Exception as e:
                errors.append(f"错误: {filename} - {e}")
        else:
            moved.append(msg)

    return moved, errors, warnings


# Windows 编码修复
import sys
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Leo AI System 文件整理工具")
    parser.add_argument("--apply", action="store_true", help="执行移动操作（默认只预览）")
    parser.add_argument("--check", action="store_true", help="只检查问题，不移动")
    args = parser.parse_args()

    print("=" * 60)
    print("Leo AI System - 文件自动整理")
    print("=" * 60)

    if args.check:
        print("\n[检查模式]")
        moved, errors, warnings = organize_files(dry_run=True)
        if warnings:
            print("\n[!] 未知文件 (建议手动处理):")
            for w in warnings:
                print(f"  {w}")
        if not moved and not errors:
            print("\n[OK] 没有需要整理的文件")
    elif args.apply:
        print("\n[执行模式]")
        moved, errors, warnings = organize_files(dry_run=False, apply_changes=True)
        if moved:
            print("\n[OK] 已移动:")
            for m in moved:
                print(f"  {m}")
        if errors:
            print("\n[ERROR] 错误:")
            for e in errors:
                print(f"  {e}")
        if not moved and not errors:
            print("\n[OK] 没有需要整理的文件")
    else:
        print("\n[预览模式]")
        print("使用 --apply 执行移动，使用 --check 只检查\n")

        moved, errors, warnings = organize_files(dry_run=True)

        if moved:
            print("将会移动:")
            for m in moved:
                print(f"  {m}")
        else:
            print("[OK] 没有需要整理的文件")

        if warnings:
            print("\n[!] 未知文件 (建议手动处理):")
            for w in warnings:
                print(f"  {w}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
