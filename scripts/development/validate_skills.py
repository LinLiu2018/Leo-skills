#!/usr/bin/env python3
"""
Skills 结构验证工具
验证所有技能是否符合最佳实践标准
"""

import os
import sys
import yaml
from pathlib import Path
from typing import Dict, List, Tuple

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
SKILLS_DIR = PROJECT_ROOT / "src" / "leo_skills"

# 颜色输出
class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    RESET = "\033[0m"


def check_file_exists(skill_path: Path, filename: str) -> bool:
    """检查文件是否存在"""
    return (skill_path / filename).exists()


def check_yaml_frontmatter(skill_path: Path) -> Tuple[bool, str]:
    """检查 SKILL.md 是否有有效的 YAML frontmatter"""
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return False, "SKILL.md 不存在"

    try:
        content = skill_md.read_text(encoding="utf-8")
        if not content.startswith("---"):
            return False, "缺少 YAML frontmatter"

        # 提取 YAML 部分
        parts = content.split("---", 2)
        if len(parts) < 3:
            return False, "YAML frontmatter 格式错误"

        yaml_content = parts[1].strip()
        data = yaml.safe_load(yaml_content)

        if not isinstance(data, dict):
            return False, "YAML frontmatter 不是有效的字典"

        required_fields = ["name", "description"]
        missing = [f for f in required_fields if f not in data]
        if missing:
            return False, f"缺少必需字段: {missing}"

        return True, "有效"
    except Exception as e:
        return False, f"解析错误: {e}"


def validate_skill(skill_path: Path) -> Dict:
    """验证单个技能"""
    skill_name = skill_path.name

    results = {
        "name": skill_name,
        "path": str(skill_path.relative_to(PROJECT_ROOT)),
        "files": {},
        "yaml_valid": False,
        "yaml_message": "",
        "score": 0,
        "max_score": 6
    }

    # 检查必需文件
    results["files"]["SKILL.md"] = check_file_exists(skill_path, "SKILL.md")
    results["files"]["__init__.py"] = check_file_exists(skill_path, "__init__.py")
    results["files"][f"{skill_name}.py"] = check_file_exists(skill_path, f"{skill_name}.py")
    results["files"]["config/config.yaml"] = check_file_exists(skill_path, "config/config.yaml")
    results["files"]["evolution.json"] = check_file_exists(skill_path, "evolution.json")
    results["files"]["scripts/main.py"] = check_file_exists(skill_path, "scripts/main.py")

    # 检查 YAML frontmatter
    yaml_valid, yaml_msg = check_yaml_frontmatter(skill_path)
    results["yaml_valid"] = yaml_valid
    results["yaml_message"] = yaml_msg

    # 计算分数
    if results["files"]["SKILL.md"]:
        results["score"] += 2  # 必需文件，权重高
    if yaml_valid:
        results["score"] += 1
    if results["files"]["__init__.py"]:
        results["score"] += 1
    if results["files"][f"{skill_name}.py"]:
        results["score"] += 1
    if results["files"]["config/config.yaml"]:
        results["score"] += 0.5
    if results["files"]["evolution.json"]:
        results["score"] += 0.5

    return results


def print_results(results: List[Dict]):
    """打印验证结果"""
    print("\n" + "=" * 80)
    print(f"{Colors.BLUE}Skills 结构验证报告{Colors.RESET}")
    print("=" * 80)

    # 按类别分组
    categories = {}
    for r in results:
        category = r["path"].split("/")[2]  # src/leo_skills/{category}/...
        if category not in categories:
            categories[category] = []
        categories[category].append(r)

    total_score = 0
    total_max = 0

    for category, skills in sorted(categories.items()):
        print(f"\n{Colors.BLUE}## {category}{Colors.RESET}")
        print("-" * 80)

        for skill in skills:
            score_pct = (skill["score"] / skill["max_score"]) * 100

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

            print(f"\n{status} {skill['name']}")
            print(f"   路径: {skill['path']}")
            print(f"   完整度: {color}{score_pct:.1f}%{Colors.RESET} ({skill['score']}/{skill['max_score']})")

            # 显示缺失文件
            missing = [f for f, exists in skill["files"].items() if not exists]
            if missing:
                print(f"   缺失: {', '.join(missing)}")

            # 显示 YAML 状态
            if not skill["yaml_valid"]:
                print(f"   {Colors.RED}YAML: {skill['yaml_message']}{Colors.RESET}")

            total_score += skill["score"]
            total_max += skill["max_score"]

    # 总体统计
    print("\n" + "=" * 80)
    overall_pct = (total_score / total_max) * 100 if total_max > 0 else 0
    print(f"{Colors.BLUE}总体完整度: {overall_pct:.1f}%{Colors.RESET}")
    print(f"总技能数: {len(results)}")

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
    print(f"{Colors.BLUE}正在验证 Skills 结构...{Colors.RESET}")

    if not SKILLS_DIR.exists():
        print(f"{Colors.RED}错误: Skills 目录不存在: {SKILLS_DIR}{Colors.RESET}")
        sys.exit(1)

    results = []

    # 遍历所有类别目录
    for category_dir in sorted(SKILLS_DIR.iterdir()):
        if not category_dir.is_dir():
            continue
        if category_dir.name.startswith(".") or category_dir.name == "__pycache__":
            continue

        # 遍历类别下的技能目录
        for skill_dir in sorted(category_dir.iterdir()):
            if not skill_dir.is_dir():
                continue
            if skill_dir.name.startswith(".") or skill_dir.name == "__pycache__":
                continue

            # 验证技能
            result = validate_skill(skill_dir)
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
