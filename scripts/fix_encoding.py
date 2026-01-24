#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import sys
from pathlib import Path

def safe_print(text):
    """安全打印，避免编码错误"""
    try:
        print(text)
    except UnicodeEncodeError:
        # 如果编码失败，移除特殊字符后重试
        safe_text = text.encode('ascii', 'ignore').decode('ascii')
        print(safe_text)

def fix_emoji_in_file(file_path):
    """修复文件中的emoji字符"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 替换常见的emoji字符为文本
        emoji_replacements = {
            '[SUCCESS]': '[SUCCESS]',
            '[ERROR]': '[ERROR]', 
            '[WARNING]': '[WARNING]',
            '[HOT]': '[HOT]',
            '[LAUNCH]': '[LAUNCH]',
            '[DATA]': '[DATA]',
            '[TARGET]': '[TARGET]',
            '[TOOLS]': '[TOOLS]',
            '[BUILD]': '[BUILD]',
            '[SPARKLE]': '[SPARKLE]',
            '[IDEA]': '[IDEA]',
            '[NOTE]': '[NOTE]',
            '[SEARCH]': '[SEARCH]',
            '[STAR]': '[STAR]',
            '[IMPORTANT]': '[IMPORTANT]'
        }
        
        for emoji, replacement in emoji_replacements.items():
            content = content.replace(emoji, replacement)
        
        # 如果内容有变化，写回文件
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
            
    except Exception as e:
        safe_print(f"Error processing {file_path}: {e}")
        return False

def fix_all_python_files(root_path):
    """修复所有Python文件中的emoji字符"""
    root = Path(root_path)
    fixed_count = 0
    total_count = 0
    
    # 遍历所有Python文件
    for py_file in root.rglob("*.py"):
        if any(skip_part in str(py_file) for skip_part in ['.git', '__pycache__', '.venv', 'node_modules']):
            continue
            
        total_count += 1
        if fix_emoji_in_file(py_file):
            fixed_count += 1
            safe_print(f"Fixed: {py_file}")
    
    safe_print(f"\nSummary: Fixed {fixed_count} out of {total_count} Python files")
    return fixed_count, total_count

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target_path = sys.argv[1]
    else:
        target_path = "."
    
    safe_print("Starting emoji encoding fix for Python files...")
    fix_all_python_files(target_path)