#!/usr/bin/env python3
"""
批量替换目录引用脚本
用于将所有文件中的旧目录名替换为新目录名
"""
from pathlib import Path
from typing import Tuple

# 替换规则（旧名 -> 新名）
REPLACEMENTS = {
    "leo_config": "leo_config",
    "leo_workflows": "leo_workflows",
    "leo_orchestrator": "leo_orchestrator",
    "leo_skills": "leo_skills",  # 现在可以替换了
}

# 需要处理的文件类型
FILE_PATTERNS = ["*.py", "*.yaml", "*.yml", "*.md", "*.sh", "*.json"]

# 排除的目录
EXCLUDE_DIRS = {
    ".git",
    "__pycache__",
    "node_modules",
    ".pytest_cache",
    "leo_ai_system.egg-info",
    ".evolution_data",
    ".playwright-mcp",
    "leo_skills",  # 暂时排除，避免处理大量文件
}


def should_process_file(file_path: Path) -> bool:
    """判断是否应该处理该文件"""
    # 检查是否在排除目录中
    for part in file_path.parts:
        if part in EXCLUDE_DIRS:
            return False

    # 检查文件扩展名
    for pattern in FILE_PATTERNS:
        if file_path.match(pattern):
            return True

    return False


def replace_in_file(file_path: Path, dry_run: bool = False) -> Tuple[bool, int]:
    """
    替换单个文件中的内容

    Args:
        file_path: 文件路径
        dry_run: 是否为试运行模式

    Returns:
        (是否有修改, 修改次数)
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except UnicodeDecodeError:
        # 尝试其他编码
        try:
            with open(file_path, "r", encoding="gbk") as f:
                content = f.read()
        except:
            print(f"[警告] 无法读取: {file_path}")
            return False, 0
    except Exception as e:
        print(f"[警告] 读取错误 {file_path}: {e}")
        return False, 0

    original_content = content
    replace_count = 0

    # 执行替换
    for old, new in REPLACEMENTS.items():
        # 统计替换次数
        count = content.count(old)
        if count > 0:
            replace_count += count
            content = content.replace(old, new)

    # 如果内容有变化
    if content != original_content:
        if not dry_run:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"[OK] 已更新: {file_path} ({replace_count} 处)")
            except Exception as e:
                print(f"[错误] 写入错误 {file_path}: {e}")
                return False, 0
        else:
            print(f"[试运行] 将更新: {file_path} ({replace_count} 处)")

        return True, replace_count

    return False, 0


def main(dry_run: bool = False):
    """
    主函数

    Args:
        dry_run: 是否为试运行模式（不实际修改文件）
    """
    base_dir = Path(__file__).parent
    updated_count = 0
    total_replacements = 0
    processed_files = []

    print("=" * 70)
    print("批量替换目录引用脚本")
    print("=" * 70)
    print(f"基础目录: {base_dir}")
    print(f"替换规则: {REPLACEMENTS}")
    print(f"模式: {'试运行' if dry_run else '实际执行'}")
    print("-" * 70)

    # 遍历所有文件
    for pattern in FILE_PATTERNS:
        for file_path in base_dir.rglob(pattern):
            if should_process_file(file_path):
                modified, count = replace_in_file(file_path, dry_run)
                if modified:
                    updated_count += 1
                    total_replacements += count
                    processed_files.append((file_path, count))

    print("-" * 70)
    print(f"完成! 共{'将' if dry_run else '已'}更新 {updated_count} 个文件")
    print(f"总替换次数: {total_replacements}")

    if processed_files and dry_run:
        print("\n将要修改的文件列表:")
        for file_path, count in processed_files[:20]:  # 只显示前20个
            print(f"  - {file_path.relative_to(base_dir)} ({count} 处)")
        if len(processed_files) > 20:
            print(f"  ... 还有 {len(processed_files) - 20} 个文件")

    print("=" * 70)


if __name__ == "__main__":
    import sys

    # 检查命令行参数
    dry_run = "--dry-run" in sys.argv or "-n" in sys.argv

    if dry_run:
        print("\n[试运行模式] 不会实际修改文件\n")
        main(dry_run=True)
        print("\n如果确认无误，请运行: python batch_rename_paths.py")
    else:
        print("\n[警告] 即将修改文件，请确保已备份重要数据！")
        response = input("是否继续？(yes/no): ")
        if response.lower() in ["yes", "y"]:
            main(dry_run=False)
        else:
            print("已取消操作")
