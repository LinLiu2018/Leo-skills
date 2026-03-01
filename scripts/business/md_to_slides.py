#!/usr/bin/env python3
"""
乐橙荟营销文档 → Marp 幻灯片 + PDF/HTML 转换器

用法:
  python scripts/business/md_to_slides.py                    # 转换全部
  python scripts/business/md_to_slides.py --file 调研报告    # 转换单个（模糊匹配）
  python scripts/business/md_to_slides.py --pdf-only         # 只导出 PDF
  python scripts/business/md_to_slides.py --html-only        # 只导出 HTML
  python scripts/business/md_to_slides.py --no-export        # 只生成 .slide.md，不导出
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

# 路径配置
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SOURCE_DIR = PROJECT_ROOT / "projects" / "乐橙荟"
OUTPUT_DIR = SOURCE_DIR / "slides"
THEME_FILE = OUTPUT_DIR / "theme-lecheng.css"

# Marp frontmatter
MARP_HEADER = """---
marp: true
theme: lecheng
paginate: true
size: 16:9
---

"""

COVER_DIRECTIVE = "<!-- _class: lead -->\n"

# 表格拆分阈值（紧凑字号下可以放更多行）
MAX_TABLE_ROWS = 12
# 每页最大行数估算（用于内容过长时自动分页）
MAX_LINES_PER_SLIDE = 22


def read_md(filepath: Path) -> str:
    return filepath.read_text(encoding="utf-8")


def split_table(table_lines: list[str], header_lines: list[str]) -> list[list[str]]:
    """将超长表格拆分为多个子表格"""
    chunks = []
    for i in range(0, len(table_lines), MAX_TABLE_ROWS):
        chunk = header_lines + table_lines[i:i + MAX_TABLE_ROWS]
        chunks.append(chunk)
    return chunks


def process_tables(content: str) -> str:
    """处理超长表格"""
    lines = content.split("\n")
    result = []
    i = 0

    while i < len(lines):
        line = lines[i]
        if line.strip().startswith("|") and i + 1 < len(lines) and re.match(
            r"\s*\|[\s\-:|]+\|", lines[i + 1]
        ):
            header_lines = [lines[i], lines[i + 1]]
            i += 2
            data_lines = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                data_lines.append(lines[i])
                i += 1

            if len(data_lines) > MAX_TABLE_ROWS:
                chunks = split_table(data_lines, header_lines)
                for idx, chunk in enumerate(chunks):
                    result.extend(chunk)
                    if idx < len(chunks) - 1:
                        result.append("")
                        result.append("---")
                        result.append("")
                        result.append("*(续表)*")
                        result.append("")
            else:
                result.extend(header_lines)
                result.extend(data_lines)
        else:
            result.append(line)
            i += 1

    return "\n".join(result)


def md_to_marp(content: str, title: str) -> str:
    """将普通 MD 转为 Marp 幻灯片格式"""

    # 移除原有 frontmatter
    content = re.sub(r"^---\n.*?\n---\n", "", content, flags=re.DOTALL)

    # 处理超长表格
    content = process_tables(content)

    lines = content.split("\n")
    result_lines = []
    is_first_h1 = True
    in_code_block = False
    current_slide_lines = 0  # 当前页内容行数

    for i, line in enumerate(lines):
        stripped = line.strip()

        # 跟踪代码块
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            result_lines.append(line)
            current_slide_lines += 1
            continue

        if in_code_block:
            result_lines.append(line)
            current_slide_lines += 1
            continue

        # 跳过已有的 --- 分页符（避免重复分页产生空白页）
        if stripped == "---":
            continue

        # # 一级标题 → 封面页
        if stripped.startswith("# ") and not stripped.startswith("## "):
            if is_first_h1:
                result_lines.append(COVER_DIRECTIVE)
                result_lines.append(line)
                result_lines.append("")
                result_lines.append(f"**乐橙荟商业中心 · 投资专案**")
                result_lines.append(f"2026年2月")
                is_first_h1 = False
                current_slide_lines = 0
            else:
                result_lines.append("")
                result_lines.append("---")
                result_lines.append("")
                result_lines.append(COVER_DIRECTIVE)
                result_lines.append(line)
                current_slide_lines = 0
            continue

        # ## 二级标题 → 新页面
        if stripped.startswith("## "):
            result_lines.append("")
            result_lines.append("---")
            result_lines.append("")
            result_lines.append(line)
            current_slide_lines = 2
            continue

        # ### 三级标题 — 如果当前页已经很满，先分页
        if stripped.startswith("### ") and current_slide_lines > 14:
            result_lines.append("")
            result_lines.append("---")
            result_lines.append("")
            result_lines.append(line)
            current_slide_lines = 2
            continue

        # 空行不计入行数
        if not stripped:
            result_lines.append(line)
            continue

        # 普通内容行
        current_slide_lines += 1

        # 如果当前页内容过多，在段落间自动分页
        if current_slide_lines > MAX_LINES_PER_SLIDE:
            # 找一个合适的分页点：空行之后
            if i + 1 < len(lines) and not lines[i + 1].strip():
                result_lines.append(line)
                result_lines.append("")
                result_lines.append("---")
                result_lines.append("")
                current_slide_lines = 0
                continue

        result_lines.append(line)

    # 组装
    slide_content = MARP_HEADER + "\n".join(result_lines)

    # 清理：移除连续的 --- 之间只有空行的情况（空白页）
    slide_content = re.sub(r"\n---\n\s*\n---\n", "\n---\n", slide_content)
    # 清理多余空行
    slide_content = re.sub(r"\n{4,}", "\n\n", slide_content)

    return slide_content


def find_marp() -> str:
    """查找 marp 可执行文件路径"""
    marp = shutil.which("marp")
    if marp:
        return marp
    npm_global = Path(os.environ.get("APPDATA", "")) / "npm"
    for name in ["marp.cmd", "marp"]:
        candidate = npm_global / name
        if candidate.exists():
            return str(candidate)
    return "marp"


def export_marp(slide_file: Path, fmt: str = "pdf"):
    """调用 marp CLI 导出"""
    marp_bin = find_marp()
    cmd = [
        marp_bin,
        str(slide_file),
        f"--{fmt}",
        "--allow-local-files",
        "--theme", str(THEME_FILE),
    ]

    if fmt == "html":
        cmd.append("--bespoke.progress")

    print(f"  导出 {fmt.upper()}: {slide_file.stem}.{fmt}")
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")

    if result.returncode != 0:
        print(f"  ⚠ 导出失败: {result.stderr[:200]}")
        return False
    return True


def convert_file(md_file: Path, export_pdf=True, export_html=True):
    """转换单个文件"""
    print(f"\n📄 处理: {md_file.name}")

    content = read_md(md_file)
    title = md_file.stem
    marp_content = md_to_marp(content, title)

    slide_file = OUTPUT_DIR / f"{title}.slide.md"
    slide_file.write_text(marp_content, encoding="utf-8")
    print(f"  ✅ 生成幻灯片: {slide_file.name}")

    if export_pdf:
        export_marp(slide_file, "pdf")
    if export_html:
        export_marp(slide_file, "html")


def main():
    parser = argparse.ArgumentParser(description="乐橙荟 MD → Marp 幻灯片转换器")
    parser.add_argument("--file", help="只转换匹配的文件（模糊匹配文件名）")
    parser.add_argument("--pdf-only", action="store_true", help="只导出 PDF")
    parser.add_argument("--html-only", action="store_true", help="只导出 HTML")
    parser.add_argument("--no-export", action="store_true", help="只生成 .slide.md")
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    export_pdf = not args.html_only and not args.no_export
    export_html = not args.pdf_only and not args.no_export

    md_files = sorted(SOURCE_DIR.glob("*.md"))

    if args.file:
        md_files = [f for f in md_files if args.file in f.stem]
        if not md_files:
            print(f"❌ 未找到匹配 '{args.file}' 的文件")
            sys.exit(1)

    print(f"🚀 乐橙荟营销文档 → Marp 幻灯片转换")
    print(f"   源目录: {SOURCE_DIR}")
    print(f"   输出目录: {OUTPUT_DIR}")
    print(f"   待转换: {len(md_files)} 个文件")

    for md_file in md_files:
        convert_file(md_file, export_pdf=export_pdf, export_html=export_html)

    print(f"\n✅ 全部完成！")
    print(f"   📂 幻灯片文件: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
