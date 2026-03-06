#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Superpowers 官方仓库同步脚本

功能：
1. 拉取官方 Superpowers 最新版本
2. 对比差异
3. 生成同步报告

使用方法：
    python scripts/sync/sync_superpowers.py [--check-only] [--pull]
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from datetime import datetime


# 配置
SUPERPOWERS_REPO = "https://github.com/obra/superpowers.git"
SUPERPOWERS_LOCAL = Path.home() / ".claude" / "skills" / "superpowers"
LEO_SKILLS_DIR = Path(__file__).parent.parent.parent / "src" / "leo_skills"
OFFICIAL_SKILLS_DIR = SUPERPOWERS_LOCAL / "skills"


def run_command(cmd, cwd=None):
    """执行命令并返回输出"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, "", str(e)


def check_superpowers_exists():
    """检查本地是否存在 Superpowers 仓库"""
    return SUPERPOWERS_LOCAL.exists() and (SUPERPOWERS_LOCAL / ".git").exists()


def clone_or_pull():
    """克隆或更新 Superpowers 仓库"""
    print(f"\n{'='*60}")
    print("同步 Superpowers 官方仓库")
    print(f"{'='*60}\n")

    if not check_superpowers_exists():
        print(f"正在克隆 {SUPERPOWERS_REPO}...")
        print(f"目标目录: {SUPERPOWERS_LOCAL}")
        code, stdout, stderr = run_command(
            f"git clone {SUPERPOWERS_REPO} {SUPERPOWERS_LOCAL}"
        )
        if code != 0:
            print(f"克隆失败: {stderr}")
            return False
        print("克隆成功!")
    else:
        print(f"更新现有仓库: {SUPERPOWERS_LOCAL}")
        code, stdout, stderr = run_command(
            "git fetch origin && git pull",
            cwd=SUPERPOWERS_LOCAL
        )
        if code != 0:
            print(f"更新失败: {stderr}")
            return False
        print("更新成功!")

    return True


def get_current_version():
    """获取当前版本号"""
    code, stdout, stderr = run_command(
        "git describe --tags --abbrev=0",
        cwd=SUPERPOWERS_LOCAL
    )
    if code == 0:
        return stdout.strip()
    return "未知"


def list_official_skills():
    """列出官方所有技能"""
    if not OFFICIAL_SKILLS_DIR.exists():
        return []

    skills = []
    for item in OFFICIAL_SKILLS_DIR.iterdir():
        if item.is_dir() and (item / "SKILL.md").exists():
            skills.append(item.name)
    return sorted(skills)


def list_leo_skills():
    """列出 Leo 系统所有技能"""
    skills = []
    # 直接扫描 collaboration, testing, devops 等关键目录
    key_dirs = ['collaboration', 'testing', 'devops', 'core', 'debugging']
    for key_dir in key_dirs:
        dir_path = LEO_SKILLS_DIR / key_dir
        if dir_path.exists():
            for item in dir_path.iterdir():
                if item.is_dir() and (item / "SKILL.md").exists():
                    skills.append(item.name)
    return sorted(skills)


def compare_skills():
    """对比官方和 Leo 技能"""
    official = list_official_skills()
    leo = list_leo_skills()

    official_set = set(official)
    leo_set = set(leo)

    # 转换技能名称格式: finishing-a-development-branch -> finishing_development_branch_skill
    def to_leo_format(name):
        return name.replace('-', '_') + '_skill'

    leo_from_official = {to_leo_format(s) for s in official}

    missing = leo_from_official - leo_set  # Leo缺少的官方技能
    extra = leo_set - official_set - leo_from_official  # Leo独有的技能
    matched = leo_set & leo_from_official  # 已匹配的技能

    return {
        "official": official,
        "leo": leo,
        "missing": missing,
        "extra": extra,
        "matched": matched
    }


def generate_report(compare_result, current_version):
    """生成同步报告"""
    print(f"\n{'='*60}")
    print(f"Superpowers 同步报告")
    print(f"官方版本: {current_version}")
    print(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    print("📊 技能统计:")
    print(f"  官方技能数: {len(compare_result['official'])}")
    print(f"  Leo技能数: {len(compare_result['leo'])}")
    print(f"  已匹配: {len(compare_result['matched'])}")

    print("\n✅ 已实现的官方技能:")
    for skill in sorted(compare_result['matched']):
        print(f"  - {skill}")

    print("\n❌ 缺失的官方技能:")
    if compare_result['missing']:
        for skill in sorted(compare_result['missing']):
            print(f"  - {skill}")
    else:
        print("  (无)")

    print("\n🔧 Leo独有的技能:")
    if compare_result['extra']:
        for skill in sorted(compare_result['extra']):
            print(f"  - {skill}")
    else:
        print("  (无)")

    print("\n📋 官方所有技能列表:")
    for skill in compare_result['official']:
        status = "✅" if skill.replace('-', '_') + '_skill' in compare_result['matched'] else "❌"
        print(f"  {status} {skill}")


def main():
    parser = argparse.ArgumentParser(description="Superpowers 官方仓库同步工具")
    parser.add_argument("--check-only", action="store_true", help="仅检查不拉取")
    parser.add_argument("--pull", action="store_true", help="拉取最新代码")
    args = parser.parse_args()

    # 检查本地仓库
    if not check_superpowers_exists():
        print("❌ 本地未找到 Superpowers 仓库")
        if args.check_only:
            print("使用 --pull 参数克隆仓库")
            return 1

        if not clone_or_pull():
            return 1

    # 获取版本
    current_version = get_current_version()

    # 拉取更新
    if args.pull:
        clone_or_pull()
        current_version = get_current_version()

    # 对比技能
    compare_result = compare_skills()

    # 生成报告
    generate_report(compare_result, current_version)

    # 检查更新
    code, stdout, stderr = run_command(
        "git log --oneline -5",
        cwd=SUPERPOWERS_LOCAL
    )
    print("\n📝 最近提交:")
    for line in stdout.strip().split('\n'):
        print(f"  {line}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
