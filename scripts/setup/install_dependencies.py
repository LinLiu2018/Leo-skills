#!/usr/bin/env python3
"""
Leo System Dependency Installer
=================================
自动化安装系统依赖

使用方法:
  py -3 install_dependencies.py
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """运行命令并返回结果"""
    print(f"\n[INSTALL] {description}...")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"[OK] {description} 成功")
            return True
        else:
            print(f"[WARN] {description} 失败: {result.stderr[:200]}")
            return False
    except Exception as e:
        print(f"[ERROR] {description} 异常: {e}")
        return False


def install_yaml():
    """安装 pyyaml"""
    methods = [
        ("py -3 -m pip install pyyaml", "通过 pip 安装 pyyaml"),
        ("py -3 -m ensurepip", "先安装 pip"),
    ]
    
    for cmd, desc in methods:
        if run_command(cmd, desc):
            return True
    
    return False


def check_python():
    """检查 Python 版本"""
    print("\n[CHECK] Python 环境...")
    try:
        result = subprocess.run(
            "py -3 --version",
            shell=True,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"[OK] {result.stdout.strip()}")
            return True
    except Exception as e:
        print(f"[ERROR] {e}")
    return False


def main():
    print("=" * 60)
    print("[LEO SYSTEM] 依赖安装工具")
    print("=" * 60)
    
    # 检查 Python
    if not check_python():
        print("\n[ERROR] Python 3 未安装，请先安装 Python 3.10+")
        sys.exit(1)
    
    # 安装 pyyaml
    print("\n[NEED] 正在安装核心依赖...")
    if install_yaml():
        print("\n" + "=" * 60)
        print("[SUCCESS] 依赖安装完成!")
        print("=" * 60)
        print("\n[USAGE] 现在可以运行:")
        project_root = Path(__file__).parent.parent.resolve()
        print(f"  cd {project_root / 'src'}")
        print("  py -3 ../scripts/quick_run.py list")
        print("  py -3 ../scripts/quick_run.py skill web_search_skill '{}'")
    else:
        print("\n" + "=" * 60)
        print("[FAIL] 依赖安装失败")
        print("=" * 60)
        print("\n[MANUAL] 请手动安装:")
        print("  1. 下载 get-pip.py:")
        print("     curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py")
        print("  2. 安装 pip:")
        print("     py -3 get-pip.py")
        print("  3. 安装 pyyaml:")
        print("     py -3 -m pip install pyyaml")


if __name__ == "__main__":
    main()
