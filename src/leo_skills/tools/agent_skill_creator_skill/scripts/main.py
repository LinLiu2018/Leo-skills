#!/usr/bin/env python3
"""
Agent Skill Creator - Main Entry Point
用于创建和导出 Claude Code 技能的主入口
"""
import sys
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from export_utils import main as export_main


def main():
    """
    Agent Skill Creator 主函数

    功能：
    1. 创建新的 Claude Code 技能
    2. 导出技能包（Desktop/Web/API）
    3. 验证技能结构
    4. 生成安装指南

    使用方法：
        python main.py [skill_path] [options]

    示例：
        python main.py ../my-skill --export-all
        python main.py ../my-skill --desktop
        python main.py ../my-skill --validate
    """
    print("[Agent Skill Creator] 启动技能创建工具...")
    print("=" * 60)

    # 调用 export_utils 的主函数
    export_main()


if __name__ == "__main__":
    main()
