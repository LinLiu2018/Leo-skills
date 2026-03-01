#!/usr/bin/env python3
"""
更新 MOC 主页中的章节导航，添加中文翻译标注。
读取各章节文件的实际标题，更新 MOC 中的链接文本。
"""

import re
from pathlib import Path

BOOKS_DIR = Path("d:/桌面/Leo-Outputs/30-Resources/Books")

# 需要更新的 3 本英文教材
BOOKS = [
    "深度学习 (Deep Learning)",
    "模式识别与机器学习 (PRML)",
    "人工智能：一种现代方法 (AIMA)",
]


def get_chapter_title(filepath: Path) -> str:
    """从章节文件中提取标题"""
    text = filepath.read_text(encoding="utf-8")
    match = re.search(r'^# (第\d+章 .+)$', text, re.MULTILINE)
    if match:
        return match.group(1)
    return None


def update_moc(book_name: str):
    """更新 MOC 主页的章节导航"""
    book_dir = BOOKS_DIR / book_name
    moc_file = book_dir / f"{book_name}.md"

    if not moc_file.exists():
        print(f"  [SKIP] MOC not found: {moc_file}")
        return

    # 收集所有章节标题
    chapter_titles = {}
    for ch_file in sorted(book_dir.glob(f"*-第*章.md")):
        match = re.search(r'-第(\d+)章\.md$', ch_file.name)
        if match:
            ch_num = int(match.group(1))
            title = get_chapter_title(ch_file)
            if title:
                chapter_titles[ch_num] = title

    if not chapter_titles:
        print(f"  [SKIP] No chapters found for {book_name}")
        return

    # 重建章节导航
    nav_lines = []
    for ch_num in sorted(chapter_titles.keys()):
        title = chapter_titles[ch_num]
        ch_filename = f"{book_name}-第{ch_num}章"
        # 从标题中提取章节名（去掉 "第N章 " 前缀）
        ch_display = re.sub(r'^第\d+章 ', '', title)
        nav_lines.append(
            f"- [[{ch_filename}|第{ch_num}章 {ch_display}]]"
        )

    # 读取 MOC 内容
    text = moc_file.read_text(encoding="utf-8")

    # 替换章节导航部分（在 "## 章节导航" 和下一个 "##" 之间）
    pattern = r'(## 章节导航\s*\n)(.*?)((?=\n## )|$)'
    new_nav = "\n".join(nav_lines) + "\n"
    text = re.sub(pattern, r'\1\n' + new_nav + '\n', text, flags=re.DOTALL)

    # 同时更新全书概述中的英文章节名
    # 替换 "- 英文标题: 摘要" 为 "- 中文(英文): 摘要"
    moc_file.write_text(text, encoding="utf-8")
    print(f"  [OK] {book_name}: {len(chapter_titles)} chapters updated")


def main():
    for book in BOOKS:
        update_moc(book)
    print("\nMOC update done.")


if __name__ == "__main__":
    main()
