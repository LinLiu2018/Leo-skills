#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
硬盘清理技能 - 主入口
Disk Cleanup Skill - Main Entry Point

Usage:
    python main.py --action analyze_space
    python main.py --action clean_temp --dry-run
    python main.py --action full_cleanup --profile standard --dry-run
"""

import argparse
import sys
import json
from pathlib import Path
import io

# 设置 UTF-8 编码输出（解决 Windows 控制台编码问题）
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from disk_cleanup_skill import DiskCleanupSkill


def print_banner():
    """打印横幅"""
    print("=" * 60)
    print("  硬盘清理技能 - Disk Cleanup Skill")
    print("  Version: 1.0.0")
    print("  安全、高效的 Windows 磁盘空间管理工具")
    print("=" * 60)
    print()


def print_result(result: dict, verbose: bool = False):
    """格式化打印结果"""
    if not result.get("success", False):
        print(f"\n❌ 操作失败: {result.get('error', 'Unknown error')}")
        return

    action = result.get("action", "unknown")
    data = result.get("data", {})

    print(f"\n✅ 操作成功: {action}")
    print("-" * 60)

    if action == "analyze_space":
        print_space_analysis(data)
    elif action == "clean_temp":
        print_clean_result(data)
    elif action == "full_cleanup":
        print_full_cleanup_result(data)
    elif action == "get_recommendations":
        print_recommendations(data)
    elif action == "get_temp_size":
        print_temp_size(data)
    else:
        if verbose:
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(f"结果: {data}")


def print_space_analysis(data: dict):
    """打印空间分析结果"""
    drives = data.get("drives", {})
    summary = data.get("summary", {})

    print("\n📊 磁盘空间分析:")
    print()

    for drive, info in drives.items():
        if "error" in info:
            print(f"  {drive} - 错误: {info['error']}")
            continue

        status_icon = {
            "critical": "🔴",
            "warning": "🟡",
            "normal": "🟢"
        }.get(info.get("status", "normal"), "⚪")

        print(f"  {status_icon} {drive}")
        print(f"     总容量: {info['total_gb']} GB")
        print(f"     已使用: {info['used_gb']} GB ({info['usage_percent']}%)")
        print(f"     剩余空间: {info['free_gb']} GB")
        print()

    print(f"总体状态: {summary.get('overall_status', 'unknown').upper()}")

    if summary.get("critical_drives"):
        print(f"⚠️  危险驱动器: {', '.join(summary['critical_drives'])}")
    if summary.get("warning_drives"):
        print(f"⚠️  警告驱动器: {', '.join(summary['warning_drives'])}")

    # 打印建议
    recommendations = data.get("recommendations", [])
    if recommendations:
        print("\n💡 清理建议:")
        for rec in recommendations:
            priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(rec.get("priority", "low"), "⚪")
            print(f"  {priority_icon} {rec.get('message', '')}")


def print_clean_result(data: dict):
    """打印清理结果"""
    print(f"\n🧹 清理结果:")
    print(f"  模式: {'Dry-run (模拟)' if data.get('dry_run') else '实际清理'}")
    print(f"  发现文件: {data.get('files_found', 0)}")
    print(f"  已删除: {data.get('files_deleted', 0)}")
    print(f"  跳过: {data.get('files_skipped', 0)}")
    print(f"  释放空间: {data.get('space_freed_gb', 0):.2f} GB ({data.get('space_freed_mb', 0):.2f} MB)")

    locations = data.get("locations", [])
    if locations:
        print(f"\n  清理位置:")
        for loc in locations:
            print(f"    - {loc['path']}")
            print(f"      文件: {loc['files_deleted']}, 空间: {loc['space_freed_mb']:.2f} MB")

    errors = data.get("errors", [])
    if errors:
        print(f"\n  ⚠️  错误 ({len(errors)} 个):")
        for error in errors[:5]:  # 只显示前5个
            print(f"    - {error}")


def print_full_cleanup_result(data: dict):
    """打印完整清理结果"""
    print(f"\n🚀 完整清理结果:")
    print(f"  配置: {data.get('profile', 'unknown')}")
    print(f"  模式: {'Dry-run (模拟)' if data.get('dry_run') else '实际清理'}")

    operations = data.get("operations", [])
    print(f"\n  执行的操作 ({len(operations)} 个):")
    for op in operations:
        op_type = op.get("type", "unknown")
        print(f"    ✓ {op_type}")

    if "space_freed" in data:
        print(f"\n  释放的空间:")
        for drive, freed_bytes in data["space_freed"].items():
            freed_gb = freed_bytes / (1024**3)
            print(f"    {drive}: {freed_gb:.2f} GB")


def print_recommendations(data: dict):
    """打印清理建议"""
    recommendations = data.get("recommendations", [])

    print(f"\n💡 清理建议 ({len(recommendations)} 条):")
    for rec in recommendations:
        priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(rec.get("priority", "low"), "⚪")
        print(f"\n  {priority_icon} {rec.get('message', '')}")
        print(f"     建议操作: {', '.join(rec.get('actions', []))}")
        print(f"     预计可回收: {rec.get('estimated_recoverable_gb', 0):.2f} GB")

    estimated = data.get("estimated_recoverable", {})
    if estimated:
        print(f"\n  总预计可回收空间: {estimated.get('total_estimated_gb', 0):.2f} GB")


def print_temp_size(data: dict):
    """打印临时文件大小"""
    print(f"\n📦 临时文件统计:")
    print(f"  总大小: {data.get('total_size_gb', 0):.2f} GB ({data.get('total_size_mb', 0):.2f} MB)")
    print(f"  文件数: {data.get('total_files', 0)}")

    locations = data.get("locations", {})
    if locations:
        print(f"\n  各位置详情:")
        for path, info in locations.items():
            print(f"    {path}")
            print(f"      大小: {info['size_gb']:.2f} GB, 文件: {info['files']}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="硬盘清理技能 - 安全、高效的 Windows 磁盘空间管理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 分析磁盘空间
  python main.py --action analyze_space

  # 清理临时文件（dry-run）
  python main.py --action clean_temp --dry-run

  # 完整清理流程（标准模式，dry-run）
  python main.py --action full_cleanup --profile standard --dry-run

  # 获取清理建议
  python main.py --action get_recommendations

  # 查看临时文件大小
  python main.py --action get_temp_size
        """
    )

    parser.add_argument(
        "--action",
        type=str,
        default="analyze_space",
        choices=[
            "analyze_space",
            "clean_temp",
            "full_cleanup",
            "get_recommendations",
            "get_temp_size",
            "scan_large_files"
        ],
        help="要执行的操作"
    )

    parser.add_argument(
        "--profile",
        type=str,
        default="standard",
        choices=["conservative", "standard", "aggressive"],
        help="清理配置（用于 full_cleanup）"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="仅模拟，不实际删除文件（默认启用）"
    )

    parser.add_argument(
        "--no-dry-run",
        action="store_true",
        help="实际执行删除操作（谨慎使用）"
    )

    parser.add_argument(
        "--drives",
        type=str,
        nargs="+",
        help="要分析的驱动器列表，如: C: D:"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="显示详细输出"
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="以 JSON 格式输出结果"
    )

    args = parser.parse_args()

    # 打印横幅
    if not args.json:
        print_banner()

    # 创建技能实例
    skill = DiskCleanupSkill()

    # 确定 dry-run 模式
    dry_run = not args.no_dry_run

    # 执行操作
    kwargs = {}

    if args.action == "analyze_space":
        if args.drives:
            kwargs["drives"] = args.drives

    elif args.action == "clean_temp":
        kwargs["dry_run"] = dry_run
        kwargs["confirm"] = not args.json  # JSON 模式不需要确认

    elif args.action == "full_cleanup":
        kwargs["profile"] = args.profile
        kwargs["dry_run"] = dry_run

    result = skill.execute(action=args.action, **kwargs)

    # 输出结果
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print_result(result, verbose=args.verbose)

    # 返回状态码
    sys.exit(0 if result.get("success", False) else 1)


if __name__ == "__main__":
    main()
