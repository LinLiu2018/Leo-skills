# -*- coding: utf-8 -*-
"""
validate_paths.py - 路径完整性验证脚本

由 analyze_sessions_skill 驱动生成。
检查项目中引用的文件路径是否实际存在，防止重构后路径断裂。
"""

import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
EXCLUDE_DIRS = {"node_modules", ".git", "__pycache__", ".venv", "venv", ".claude"}


def _should_skip(path: Path) -> bool:
    return any(part in EXCLUDE_DIRS for part in path.parts)


def check_markdown_links(md_file: Path) -> list[dict]:
    """检查 Markdown 文件中的相对路径链接"""
    issues = []
    if not md_file.exists():
        return issues
    text = md_file.read_text(encoding="utf-8", errors="replace")
    # 匹配 [text](relative/path) 但排除 http/https
    for m in re.finditer(r"\[([^\]]*)\]\(([^)]+)\)", text):
        link = m.group(2)
        if link.startswith(("http://", "https://", "#", "mailto:")):
            continue
        target = (md_file.parent / link.split("#")[0]).resolve()
        if not target.exists():
            issues.append({
                "file": str(md_file.relative_to(PROJECT_ROOT)),
                "link": link,
                "target": str(target),
                "type": "broken_link",
            })
    return issues


def check_python_imports(py_file: Path) -> list[dict]:
    """检查 Python 文件中的相对导入路径"""
    issues = []
    if not py_file.exists():
        return issues
    text = py_file.read_text(encoding="utf-8", errors="replace")
    for m in re.finditer(r"from\s+(\.+)([\w.]*)\s+import", text):
        dots = m.group(1)  # 点的数量决定回退层级
        module_part = m.group(2)  # 模块路径部分
        if not module_part:
            continue
        # 计算基准目录：每个点回退一级
        base = py_file.parent
        for _ in range(len(dots)):
            base = base.parent
        module_path = module_part.replace(".", "/")
        candidate_file = base / f"{module_path}.py"
        candidate_pkg = base / module_path / "__init__.py"
        if not candidate_file.exists() and not candidate_pkg.exists():
            issues.append({
                "file": str(py_file.relative_to(PROJECT_ROOT)),
                "import": m.group(0),
                "type": "broken_import",
            })
    return issues


def scan_project() -> list[dict]:
    """扫描整个项目，返回所有路径问题"""
    all_issues = []
    src = PROJECT_ROOT / "src"
    docs = PROJECT_ROOT / "docs"

    for py in src.rglob("*.py"):
        if _should_skip(py):
            continue
        all_issues.extend(check_python_imports(py))

    for md_dir in [src, docs, PROJECT_ROOT]:
        pattern = "*.md" if md_dir == PROJECT_ROOT else "**/*.md"
        for md in md_dir.glob(pattern):
            if _should_skip(md):
                continue
            all_issues.extend(check_markdown_links(md))

    return all_issues


def main():
    issues = scan_project()
    if not issues:
        print("✅ 路径验证通过，未发现断裂引用")
        return 0

    print(f"⚠️  发现 {len(issues)} 个路径问题:\n")
    for i, issue in enumerate(issues, 1):
        if issue["type"] == "broken_link":
            print(f"  {i}. [{issue['file']}] 断裂链接: {issue['link']}")
        else:
            print(f"  {i}. [{issue['file']}] 断裂导入: {issue['import']}")

    report_path = PROJECT_ROOT / ".claude" / "logs" / "path_validation.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"# 路径验证报告\n\n共 {len(issues)} 个问题\n"]
    for issue in issues:
        if issue["type"] == "broken_link":
            lines.append(f"- `{issue['file']}`: 链接 `{issue['link']}` 目标不存在")
        else:
            lines.append(f"- `{issue['file']}`: 导入 `{issue['import']}` 模块不存在")
    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n报告已写入: {report_path}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
