#!/usr/bin/env python3
"""
Workflows 结构验证工具
验证所有工作流是否符合最佳实践标准
"""

import os
import sys
import yaml
from pathlib import Path
from typing import Dict, List, Tuple

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
WORKFLOWS_DIR = PROJECT_ROOT / "src" / "leo_workflows" / "workflows"

# 颜色输出
class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    RESET = "\033[0m"


def check_file_exists(workflow_path: Path, filename: str) -> bool:
    """检查文件是否存在"""
    return (workflow_path / filename).exists()


def check_yaml_valid(workflow_path: Path) -> Tuple[bool, str]:
    """检查 workflow.yaml 是否有效"""
    workflow_yaml = workflow_path / "workflow.yaml"
    if not workflow_yaml.exists():
        return False, "workflow.yaml 不存在"

    try:
        content = workflow_yaml.read_text(encoding="utf-8")
        data = yaml.safe_load(content)

        if not isinstance(data, dict):
            return False, "workflow.yaml 不是有效的字典"

        # 检查必需字段
        if "name" not in data:
            return False, "缺少 name 字段"
        if "steps" not in data:
            return False, "缺少 steps 字段"

        return True, "有效"
    except Exception as e:
        return False, f"解析错误: {e}"


def validate_workflow(workflow_path: Path) -> Dict:
    """验证单个工作流"""
    workflow_name = workflow_path.name

    results = {
        "name": workflow_name,
        "path": str(workflow_path.relative_to(PROJECT_ROOT)),
        "files": {},
        "yaml_valid": False,
        "yaml_message": "",
        "score": 0,
        "max_score": 5
    }

    # 检查必需文件
    results["files"]["workflow.yaml"] = check_file_exists(workflow_path, "workflow.yaml")
    results["files"]["__init__.py"] = check_file_exists(workflow_path, "__init__.py")

    # 检查 Python 文件 (命名可能不同)
    py_files = list(workflow_path.glob("*.py"))
    results["files"]["pipeline.py"] = len(py_files) > 0

    results["files"]["README.md"] = check_file_exists(workflow_path, "README.md")

    # 检查 YAML 有效性
    yaml_valid, yaml_msg = check_yaml_valid(workflow_path)
    results["yaml_valid"] = yaml_valid
    results["yaml_message"] = yaml_msg

    # 计算分数
    if results["files"]["workflow.yaml"]:
        results["score"] += 2  # 必需文件，权重高
    if yaml_valid:
        results["score"] += 1
    if results["files"]["__init__.py"]:
        results["score"] += 1
    if results["files"]["pipeline.py"]:
        results["score"] += 0.5
    if results["files"]["README.md"]:
        results["score"] += 0.5

    return results


def print_results(results: List[Dict]):
    """打印验证结果"""
    print("\n" + "=" * 80)
    print(f"{Colors.BLUE}Workflows 结构验证报告{Colors.RESET}")
    print("=" * 80)

    total_score = 0
    total_max = 0

    for workflow in results:
        score_pct = (workflow["score"] / workflow["max_score"]) * 100

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

        print(f"\n{status} {workflow['name']}")
        print(f"   路径: {workflow['path']}")
        print(f"   完整度: {color}{score_pct:.1f}%{Colors.RESET} ({workflow['score']}/{workflow['max_score']})")

        # 显示缺失文件
        missing = [f for f, exists in workflow["files"].items() if not exists]
        if missing:
            print(f"   缺失: {', '.join(missing)}")

        # 显示 YAML 状态
        if not workflow["yaml_valid"]:
            print(f"   {Colors.RED}YAML: {workflow['yaml_message']}{Colors.RESET}")

        total_score += workflow["score"]
        total_max += workflow["max_score"]

    # 总体统计
    print("\n" + "=" * 80)
    overall_pct = (total_score / total_max) * 100 if total_max > 0 else 0
    print(f"{Colors.BLUE}总体完整度: {overall_pct:.1f}%{Colors.RESET}")
    print(f"总工作流数: {len(results)}")

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
    print(f"{Colors.BLUE}正在验证 Workflows 结构...{Colors.RESET}")

    if not WORKFLOWS_DIR.exists():
        print(f"{Colors.RED}错误: Workflows 目录不存在: {WORKFLOWS_DIR}{Colors.RESET}")
        sys.exit(1)

    results = []

    # 遍历所有工作流目录
    for workflow_dir in sorted(WORKFLOWS_DIR.iterdir()):
        if not workflow_dir.is_dir():
            continue
        if workflow_dir.name.startswith(".") or workflow_dir.name == "__pycache__":
            continue

        # 验证工作流
        result = validate_workflow(workflow_dir)
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
