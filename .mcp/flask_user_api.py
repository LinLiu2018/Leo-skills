#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask API Generator - 生成用户 API
"""

import sys
import os
import json
from pathlib import Path

# 设置 UTF-8
os.environ['PYTHONIOENCODING'] = 'utf-8'
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# 添加 skill 路径
sys.path.insert(0, "../src/leo_skills/backend/flask_api_generator_skill/scripts")

from main import FlaskAPIGenerator

print('=' * 60)
print('  Flask API Generator - 生成用户 API')
print('=' * 60)

# 定义用户 API 的参数
fields = [
    {'name': 'username', 'type': 'string', 'required': True, 'unique': True, 'description': '用户名'},
    {'name': 'email', 'type': 'string', 'required': True, 'description': '邮箱'},
    {'name': 'password_hash', 'type': 'string', 'required': True, 'description': '密码哈希'},
    {'name': 'phone', 'type': 'string', 'required': False, 'description': '手机号'},
    {'name': 'status', 'type': 'string', 'required': False, 'default': 'active', 'description': '状态'},
]

# 创建输出目录
output_dir = Path("D:/桌面/leo_ai_system/output")
output_dir.mkdir(parents=True, exist_ok=True)

print("\n正在生成用户 API...")
print("-" * 60)

# 生成代码
generator = FlaskAPIGenerator(output_dir=str(output_dir))
results = generator.generate(
    resource_name='user',
    fields=fields,
    auth_required=True
)

# 保存文件
saved = generator.save_files('user', results)

print("\n" + "=" * 60)
print("  ✅ 生成完成！")
print("=" * 60)
print("\n生成的文件:")
print("-" * 60)

for name, path in saved.items():
    print(f"  ✅ {name}")
    print(f"     路径: {path}")
    print()

# 打印 Model 代码预览
print("-" * 60)
print("Model 代码预览 (user.py):")
print("-" * 60)
print(results['model'][:800])
print("\n... [更多代码省略] ...\n")
