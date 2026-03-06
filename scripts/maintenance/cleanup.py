#!/usr/bin/env python3
"""
自动清理脚本 - 按最佳实践规范清理无用文件

运行方式:
    python scripts/maintenance/cleanup.py

建议添加到 crontab 或 pre-commit hook:
    */30 * * * * cd /path/to/leo_ai_system && python scripts/maintenance/cleanup.py
"""

import os
import shutil
from pathlib import Path

# 项目根目录
ROOT = Path(__file__).parent.parent

# 需要清理的目录模式
DIR_PATTERNS = [
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".tox",
    "node_modules/.cache",
    ".next",
    ".nuxt",
    "dist",
    "build",
]

# 需要清理的文件模式
FILE_PATTERNS = [
    "*.pyc",
    "*.pyo",
    "*.log",
    "*.tmp",
    ".DS_Store",
    "Thumbs.db",
]

# 大于此大小的日志文件需要清理 (MB)
LOG_SIZE_LIMIT = 10


def should_clean(path: Path) -> bool:
    """判断路径是否应该被清理"""
    # 保留 node_modules
    if "node_modules" in path.parts and path.suffix != ".cache":
        return False
    return True


def clean_directories():
    """清理缓存目录"""
    cleaned = []
    for root, dirs, files in os.walk(ROOT):
        # 逆序遍历，避免修改列表时出错
        for d in reversed(dirs):
            if any(pattern in d for pattern in DIR_PATTERNS):
                path = Path(root) / d
                if should_clean(path):
                    try:
                        shutil.rmtree(path)
                        cleaned.append(str(path))
                    except Exception as e:
                        print(f"Failed to remove {path}: {e}")
    return cleaned


def clean_files():
    """清理缓存文件"""
    cleaned = []
    for root, dirs, files in os.walk(ROOT):
        for f in files:
            if any(f.endswith(p.replace("*", "")) or any(p in f for p in FILE_PATTERNS):
                path = Path(root) / f
                if should_clean(path):
                    # 检查日志文件大小
                    if f.endswith(".log"):
                        try:
                            size_mb = path.stat().st_size / 1024 / 1024
                            if size_mb > LOG_SIZE_LIMIT:
                                path.unlink()
                                cleaned.append(f"{path} ({size_mb:.1f}MB)")
                        except Exception:
                            pass
                    else:
                        try:
                            path.unlink()
                            cleaned.append(str(path))
                        except Exception:
                            pass
    return cleaned


def clean_large_logs():
    """清理大日志文件"""
    cleaned = []
    logs_dir = ROOT / "logs"
    if logs_dir.exists():
        for f in logs_dir.glob("*.log"):
            try:
                size_mb = f.stat().st_size / 1024 / 1024
                if size_mb > LOG_SIZE_LIMIT:
                    f.unlink()
                    cleaned.append(f"{f} ({size_mb:.1f}MB)")
            except Exception:
                pass
    return cleaned


def main():
    print("=" * 50)
    print("Leo AI System 自动清理脚本")
    print("=" * 50)

    # 清理目录
    print("\n[1/3] 清理缓存目录...")
    dirs_cleaned = clean_directories()
    print(f"  已清理 {len(dirs_cleaned)} 个目录")

    # 清理文件
    print("\n[2/3] 清理缓存文件...")
    files_cleaned = clean_files()
    print(f"  已清理 {len(files_cleaned)} 个文件")

    # 清理大日志
    print("\n[3/3] 清理大日志文件...")
    logs_cleaned = clean_large_logs()
    print(f"  已清理 {len(logs_cleaned)} 个大日志")

    # 统计
    total = len(dirs_cleaned) + len(files_cleaned) + len(logs_cleaned)
    print("\n" + "=" * 50)
    print(f"总计清理: {total} 项")
    print("=" * 50)

    if total > 0:
        print("\n已清理的项目:")
        for p in dirs_cleaned[:10]:
            print(f"  - {p}")
        for p in files_cleaned[:10]:
            print(f"  - {p}")


if __name__ == "__main__":
    main()
