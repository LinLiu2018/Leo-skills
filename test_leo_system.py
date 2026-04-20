#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Leo System 测试脚本
测试房产资讯发布技能和格式化器
"""

import sys
import os

# 设置控制台编码为 UTF-8
sys.stdout.reconfigure(encoding='utf-8')

# 添加路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("=" * 60)
print("Leo System 测试")
print("=" * 60)

# 测试 1: 导入 Leo Skills
print("\n[测试 1] 导入 Leo Skills...")
try:
    import leo_skills
    print("[OK] Leo Skills 导入成功")
except Exception as e:
    print(f"[FAIL] Leo Skills 导入失败：{e}")
    sys.exit(1)

# 测试 2: 导入房产资讯格式化器
print("\n[测试 2] 导入房产资讯格式化器...")
try:
    sys.path.insert(0, os.path.expanduser("~/.openclaw/workspace/skills"))
    from realestate_news_formatter.formatter import format_article
    print("[OK] 房产资讯格式化器导入成功")
except Exception as e:
    print(f"[FAIL] 房产资讯格式化器导入失败：{e}")

# 测试 3: 测试格式化功能
print("\n[测试 3] 测试格式化功能...")
try:
    test_content = """
    2025 年宁波楼市成交量同比下跌 10% 但这个跌幅在全国主要城市里算小的更重要的是宁波的房价相对坚挺核心区跌幅只有 2% 左右为什么宁波能扛得住我觉得有几个原因第一产业底子厚宁波制造业发达民营企业活跃人口净流入持续有人就有需求
    """
    
    formatted = format_article(
        content=test_content,
        title="2026 年宁波楼市展望",
        style="wechat"
    )
    
    print("[OK] 格式化成功")
    print(f"   格式化后长度：{len(formatted)} 字符")
    print(f"   包含章节数：{formatted.count('## ')}")
    emoji_count = formatted.count('🏠') + formatted.count('💰') + formatted.count('📊')
    print(f"   包含 Emoji: {emoji_count}")
except Exception as e:
    print(f"[FAIL] 格式化测试失败：{e}")

# 测试 4: 检查 Skills 目录
print("\n[测试 4] 检查 Skills 目录...")
skills_dir = os.path.join(os.path.dirname(__file__), 'src', 'leo_skills')
if os.path.exists(skills_dir):
    skill_count = len([d for d in os.listdir(skills_dir) if os.path.isdir(os.path.join(skills_dir, d))])
    print(f"[OK] Skills 目录存在：{skill_count} 个技能")
else:
    print(f"[FAIL] Skills 目录不存在：{skills_dir}")

# 测试 5: 检查 SubAgents 目录
print("\n[测试 5] 检查 SubAgents 目录...")
agents_dir = os.path.join(os.path.dirname(__file__), 'src', 'leo_subagents', 'agents')
if os.path.exists(agents_dir):
    agent_count = len([d for d in os.listdir(agents_dir) if os.path.isdir(os.path.join(agents_dir, d)) and not d.startswith('_')])
    print(f"[OK] SubAgents 目录存在：{agent_count} 个 Agent")
else:
    print(f"[FAIL] SubAgents 目录不存在：{agents_dir}")

# 测试 6: 检查房产资讯发布技能
print("\n[测试 6] 检查房产资讯发布技能...")
re_skill_path = os.path.join(skills_dir, 'content_creation', 'realestate_news_publisher_skill')
if os.path.exists(re_skill_path):
    files = os.listdir(re_skill_path)
    print(f"[OK] 房产资讯发布技能存在")
    print(f"   文件数：{len(files)}")
    print(f"   包含文件：{', '.join(files[:5])}...")
else:
    print(f"[FAIL] 房产资讯发布技能不存在：{re_skill_path}")

print("\n" + "=" * 60)
print("测试完成！")
print("=" * 60)

# 输出格式化示例
print("\n[示例] 格式化示例：")
print("-" * 60)
try:
    print(formatted[:500] + "..." if len(formatted) > 500 else formatted)
except:
    print("无法显示格式化示例")
print("-" * 60)
