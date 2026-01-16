#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一键进化所有技能 - 快速脚本

使用方法：
    python quick_evolve_all.py
"""

import sys
import io
from pathlib import Path

# 设置UTF-8输出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加路径
sys.path.insert(0, str(Path(__file__).parent))

from skill_evolution_assistant import SkillEvolutionAssistant


def main():
    print("=" * 60)
    print("技能进化助手 - 一键进化所有技能")
    print("=" * 60)

    assistant = SkillEvolutionAssistant()

    # 1. 分析现状
    print("\n[1/3] 分析现状...")
    analyze_result = assistant.execute(action="analyze")

    if not analyze_result.success:
        print(f"✗ 分析失败: {analyze_result.error}")
        return

    print(f"✓ 分析完成")
    print(f"  总技能数: {analyze_result.data['total_skills']}")
    print(f"  需要进化: {analyze_result.data['needs_evolution']}")
    print(f"  已有进化: {analyze_result.data['has_evolution']}")

    if analyze_result.data['needs_evolution'] == 0:
        print("\n所有技能已经具备进化能力！")
        return

    print(f"\n需要进化的技能:")
    for skill in analyze_result.data['needs_evolution_list']:
        print(f"  - {skill}")

    # 2. 确认
    print("\n[2/3] 确认操作...")
    response = input("是否继续改造所有技能？(y/n): ")
    if response.lower() != 'y':
        print("已取消")
        return

    # 3. 执行改造
    print("\n[3/3] 执行改造...")
    transform_result = assistant.execute(action="transform_all")

    if not transform_result.success:
        print(f"✗ 改造失败: {transform_result.error}")
        return

    print(f"\n✓ 改造完成")
    print(f"  总共改造: {transform_result.data['total_transformed']}")
    print(f"  成功: {transform_result.data['successful']}")
    print(f"  失败: {transform_result.data['failed']}")

    # 显示详细结果
    print("\n详细结果:")
    for result in transform_result.data['results']:
        status = "✓" if result['success'] else "✗"
        print(f"  {status} {result['skill']}")
        if not result['success']:
            print(f"    错误: {result.get('error', 'Unknown')}")

    # 4. 再次分析
    print("\n[验证] 再次分析...")
    final_result = assistant.execute(action="analyze")
    print(f"✓ 验证完成")
    print(f"  进化能力覆盖率: {final_result.data['quality_score']:.1%}")

    print("\n" + "=" * 60)
    print("所有技能已具备自我进化能力！")
    print("=" * 60)
    print("\n下一步:")
    print("1. 测试每个技能的功能是否正常")
    print("2. 运行技能10+次以触发学习")
    print("3. 查看进化数据: leo-skills/.evolution_data/")


if __name__ == "__main__":
    main()
