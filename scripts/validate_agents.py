#!/usr/bin/env python3
"""
Agents 结构验证工具
验证所有代理是否符合最佳实践标准
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
AGENTS_DIR = PROJECT_ROOT / "src" / "leo_subagents" / "agents"

# 颜色输出
class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    RESET = "\033[0m"


def check_file_exists(agent_path: Path, filename: str) -> bool:
    """检查文件是否存在"""
    return (agent_path / filename).exists()


def validate_agent(agent_path: Path) -> Dict:
    """验证单个代理"""
    agent_name = agent_path.name

    results = {
        "name": agent_name,
        "path": str(agent_path.relative_to(PROJECT_ROOT)),
        "files": {},
        "score": 0,
        "max_score": 4
    }

    # 检查必需文件
    results["files"]["AGENT.md"] = check_file_exists(agent_path, "AGENT.md")
    results["files"]["__init__.py"] = check_file_exists(agent_path, "__init__.py")
    results["files"][f"{agent_name}.py"] = check_file_exists(agent_path, f"{agent_name}.py")
    results["files"]["evolution.json"] = check_file_exists(agent_path, "evolution.json")

    # 计算分数
    if results["files"]["AGENT.md"]:
        results["score"] += 2  # 必需文件，权重高
    if results["files"]["__init__.py"]:
        results["score"] += 1
    if results["files"][f"{agent_name}.py"]:
        results["score"] += 0.5
    if results["files"]["evolution.json"]:
        results["score"] += 0.5

    return results


def print_results(results: List[Dict]):
    """打印验证结果"""
    print("\n" + "=" * 80)
    print(f"{Colors.BLUE}Agents 结构验证报告{Colors.RESET}")
    print("=" * 80)

    total_score = 0
    total_max = 0

    for agent in results:
        score_pct = (agent["score"] / agent["max_score"]) * 100

        # 选择颜色
        if score_pct >= 80:
            color = Colors.GREEN
            status = "✅"
        elif score_pct >= 50:
            color = Colors.YELLOW
            status = "⚠️"
        else:
            color = Colors.RED
            status = "❌"

        print(f"\n{status} {agent['name']}")
        print(f"   路径: {agent['path']}")
        print(f"   完整度: {color}{score_pct:.1f}%{Colors.RESET} ({agent['score']}/{agent['max_score']})")

        # 显示缺失文件
        missing = [f for f, exists in agent["files"].items() if not exists]
        if missing:
            print(f"   缺失: {', '.join(missing)}")

        total_score += agent["score"]
        total_max += agent["max_score"]

    # 总体统计
    print("\n" + "=" * 80)
    overall_pct = (total_score / total_max) * 100 if total_max > 0 else 0
    print(f"{Colors.BLUE}总体完整度: {overall_pct:.1f}%{Colors.RESET}")
    print(f"总代理数: {len(results)}")

    # 分类统计
    excellent = sum(1 for r in results if r["score"] / r["max_score"] >= 0.8)
    good = sum(1 for r in results if 0.5 <= r["score"] / r["max_score"] < 0.8)
    poor = sum(1 for r in results if r["score"] / r["max_score"] < 0.5)

    print(f"\n优秀 (≥80%): {Colors.GREEN}{excellent}{Colors.RESET}")
    print(f"良好 (50-80%): {Colors.YELLOW}{good}{Colors.RESET}")
    print(f"需完善 (<50%): {Colors.RED}{poor}{Colors.RESET}")
    print("=" * 80)


def main():
    """主函数"""
    print(f"{Colors.BLUE}正在验证 Agents 结构...{Colors.RESET}")

    if not AGENTS_DIR.exists():
        print(f"{Colors.RED}错误: Agents 目录不存在: {AGENTS_DIR}{Colors.RESET}")
        sys.exit(1)

    results = []

    # 遍历所有代理目录
    for agent_dir in sorted(AGENTS_DIR.iterdir()):
        if not agent_dir.is_dir():
            continue
        if agent_dir.name.startswith(".") or agent_dir.name == "__pycache__":
            continue

        # 验证代理
        result = validate_agent(agent_dir)
        results.append(result)

    # 打印结果
    print_results(results)

    # 返回退出码
    poor_count = sum(1 for r in results if r["score"] / r["max_score"] < 0.5)
    if poor_count > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
