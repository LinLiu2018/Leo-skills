#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def safe_print(text):
    """安全打印，避免编码错误"""
    try:
        print(text)
    except UnicodeEncodeError:
        safe_text = text.encode('ascii', 'ignore').decode('ascii')
        print(safe_text)

def main():
    """检查是否需要安装测试依赖"""
    
    required_packages = [
        'pytest',
        'pytest-cov', 
        'pytest-mock',
        'pytest-asyncio',
        'pytest-html'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        safe_print("Missing test dependencies:")
        for package in missing_packages:
            safe_print(f"  - {package}")
        safe_print("\nInstall with:")
        safe_print(f"pip install {' '.join(missing_packages)}")
        return False
    else:
        safe_print("[SUCCESS] All test dependencies are installed")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)