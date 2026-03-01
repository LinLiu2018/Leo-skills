# -*- coding: utf-8 -*-
"""
部署 AI 学习网站到 Vercel
"""

import os
import sys
import subprocess
from pathlib import Path

# 网站目录
SITE_DIR = Path("D:/桌面/leo_ai_system/output/ai_learning_site")

print("=" * 60)
print("AI 学习网站 - Vercel 部署脚本")
print("=" * 60)
print()

# 检查 Node.js
print("[1/5] 检查 Node.js...")
try:
    result = subprocess.run(["node", "--version"], capture_output=True, text=True, timeout=10)
    print(f"  [OK] Node.js 已安装：{result.stdout.strip()}")
except Exception as e:
    print(f"  [ERROR] Node.js 未安装")
    print()
    print("  请先安装 Node.js:")
    print("  1. 访问 https://nodejs.org/")
    print("  2. 下载并安装 LTS 版本")
    print("  3. 重新运行此脚本")
    sys.exit(1)

# 检查 Vercel CLI
print("[2/5] 检查 Vercel CLI...")
try:
    result = subprocess.run(["vercel", "--version"], capture_output=True, text=True, timeout=10)
    print(f"  [OK] Vercel CLI 已安装：{result.stdout.strip()}")
except Exception as e:
    print(f"  [INFO] Vercel CLI 未安装，正在安装...")
    subprocess.run(["npm", "install", "-g", "vercel"], check=True)
    print(f"  [OK] Vercel CLI 安装完成")

# 检查网站文件
print("[3/5] 检查网站文件...")
if not SITE_DIR.exists():
    print(f"  [ERROR] 网站目录不存在：{SITE_DIR}")
    sys.exit(1)

files = list(SITE_DIR.glob("*.html"))
print(f"  [OK] 找到 {len(files)} 个 HTML 文件")

# 登录 Vercel
print("[4/5] 登录 Vercel...")
print()
print("  请选择登录方式:")
print("  1. GitHub (推荐)")
print("  2. GitLab")
print("  3. Bitbucket")
print("  4. Email")
print()

# 执行部署
print("[5/5] 部署到 Vercel...")
print()
print("  正在部署...")
print()

os.chdir(SITE_DIR)

try:
    # 首次部署
    result = subprocess.run(["vercel", "--prod"], capture_output=True, text=True, timeout=300)
    
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    
    if result.returncode == 0:
        print()
        print("=" * 60)
        print("🎉 部署成功!")
        print("=" * 60)
        print()
        print("访问你的网站:")
        print("  https://your-project.vercel.app")
        print()
        print("查看部署详情:")
        print("  https://vercel.com/dashboard")
        print()
    else:
        print()
        print("=" * 60)
        print("部署失败，请检查错误信息")
        print("=" * 60)
        
except subprocess.TimeoutExpired:
    print()
    print("=" * 60)
    print("部署超时，请重试")
    print("=" * 60)
except Exception as e:
    print()
    print("=" * 60)
    print(f"部署出错：{e}")
    print("=" * 60)

print()
