#!/usr/bin/env python3
"""
Skill Evolution Assistant - Main Entry Point
技能进化助手主入口
"""
import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from skill_evolution_assistant import SkillEvolutionAssistant


def main():
    """
    技能进化助手主函数

    功能：
    1. 扫描所有现有技能
    2. 识别未集成进化框架的技能
    3. 自动改造技能代码
    4. 添加必要的配置文件
    5. 验证改造结果

    使用方法：
        python main.py scan              # 扫描所有技能
        python main.py evolve [skill]    # 为指定技能添加进化能力
        python main.py evolve-all        # 为所有技能添加进化能力
    """
    print("[Skill Evolution Assistant] 启动技能进化助手...")
    print("=" * 60)

    # 创建助手实例
    assistant = SkillEvolutionAssistant()

    # 解析命令行参数
    if len(sys.argv) < 2:
        action = "scan"
    else:
        action = sys.argv[1]

    # 执行操作
    if action == "scan":
        result = assistant.execute(action="scan")
        print(f"\n扫描结果: {result}")

    elif action == "evolve-all":
        result = assistant.execute(action="evolve_all")
        print(f"\n进化结果: {result}")

    elif action == "evolve" and len(sys.argv) > 2:
        skill_name = sys.argv[2]
        result = assistant.execute(action="evolve", skill_name=skill_name)
        print(f"\n进化结果: {result}")

    else:
        print("用法:")
        print("  python main.py scan")
        print("  python main.py evolve [skill_name]")
        print("  python main.py evolve-all")


if __name__ == "__main__":
    main()
