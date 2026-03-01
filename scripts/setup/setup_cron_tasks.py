# -*- coding: utf-8 -*-
"""
定时任务配置脚本
===============

配置 Leo Wingman v2.0 的定时任务：
- 每日市场情报（8:00）
- 每日内容生成（9:00）
- 竞品监控（每4小时）
- 周报生成（周五18:00）
"""

import subprocess
import sys
from typing import List, Tuple


# 定时任务定义
# (name, cron_expr, timezone, event/message, agent)
CRON_TASKS: List[Tuple[str, str, str, str, str]] = [
    # 每日市场情报
    (
        "daily_market_intelligence",
        "0 8 * * *",
        "Asia/Shanghai",
        "生成今日市场情报简报",
        "leo-assistant"
    ),
    # 每日内容生成
    (
        "daily_content_generation",
        "0 9 * * *",
        "Asia/Shanghai",
        "生成今日社交媒体内容",
        "leo-assistant"
    ),
    # 竞品监控（每4小时）
    (
        "competitor_monitoring",
        "0 */4 * * *",
        "Asia/Shanghai",
        "执行竞品监控分析",
        "leo-assistant"
    ),
    # 周报生成（周五18:00）
    (
        "weekly_report",
        "0 18 * * 5",
        "Asia/Shanghai",
        "生成本周工作总结报告",
        "leo-assistant"
    ),
    # 每日健康检查
    (
        "daily_health_check",
        "0 7 * * *",
        "Asia/Shanghai",
        "执行系统健康检查",
        "leo-assistant"
    ),
    # 记忆清理（每周日凌晨3点）
    (
        "weekly_memory_cleanup",
        "0 3 * * 0",
        "Asia/Shanghai",
        "清理过期记忆数据",
        "leo-assistant"
    ),
]


def check_openclaw_cli() -> bool:
    """检查 openclaw CLI 是否可用"""
    try:
        result = subprocess.run(
            ["openclaw", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False
    except Exception:
        return False


def list_existing_crons():
    """列出已有的定时任务"""
    try:
        result = subprocess.run(
            ["openclaw", "cron", "list"],
            capture_output=True,
            text=True,
            timeout=10
        )
        print("现有定时任务:")
        print(result.stdout if result.returncode == 0 else "无法获取")
    except Exception as e:
        print(f"获取现有任务失败: {e}")


def add_cron_task(name: str, cron_expr: str, tz: str, message: str, agent: str) -> bool:
    """添加单个定时任务"""
    try:
        result = subprocess.run(
            [
                "openclaw", "cron", "add",
                "--name", name,
                "--cron", cron_expr,
                "--tz", tz,
                "--message", message,
                "--agent", agent
            ],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            print(f"  [OK] {name}")
            return True
        else:
            print(f"  [FAIL] {name}: {result.stderr}")
            return False

    except Exception as e:
        print(f"  [ERROR] {name}: {e}")
        return False


def remove_cron_task(name: str) -> bool:
    """移除定时任务"""
    try:
        result = subprocess.run(
            ["openclaw", "cron", "remove", "--name", name],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except Exception:
        return False


def setup_all_crons(force: bool = False):
    """配置所有定时任务"""
    print("=" * 60)
    print("Leo Wingman v2.0 - 定时任务配置")
    print("=" * 60)

    # 检查 openclaw CLI
    if not check_openclaw_cli():
        print("[ERROR] openclaw CLI 未找到，请确保 OpenClaw 已安装")
        print("安装命令: npm install -g openclaw")
        return False

    print("\n检查现有任务...")
    list_existing_crons()

    print("\n配置定时任务...")
    print("-" * 60)

    success_count = 0
    fail_count = 0

    for name, cron_expr, tz, message, agent in CRON_TASKS:
        # 如果强制模式，先移除现有任务
        if force:
            remove_cron_task(name)

        if add_cron_task(name, cron_expr, tz, message, agent):
            success_count += 1
        else:
            fail_count += 1

    print("-" * 60)
    print(f"\n配置完成: {success_count} 成功, {fail_count} 失败")

    # 显示最终任务列表
    print("\n当前定时任务列表:")
    list_existing_crons()

    return fail_count == 0


def print_manual_setup():
    """打印手动配置说明"""
    print("\n" + "=" * 60)
    print("手动配置说明")
    print("=" * 60)
    print("由于 openclaw CLI 不可用，请手动运行以下命令:")
    print()

    for name, cron_expr, tz, message, agent in CRON_TASKS:
        print(f"# {name}")
        print(f"openclaw cron add \\")
        print(f"  --name {name} \\")
        print(f"  --cron \"{cron_expr}\" \\")
        print(f"  --tz {tz} \\")
        print(f"  --message \"{message}\" \\")
        print(f"  --agent {agent}")
        print()


def main():
    """主函数"""
    force = "--force" in sys.argv

    if not check_openclaw_cli():
        print("[WARN] openclaw CLI 不可用")
        print_manual_setup()
        return

    success = setup_all_crons(force=force)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
