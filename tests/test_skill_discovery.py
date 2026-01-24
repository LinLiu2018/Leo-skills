#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""测试技能发现系统"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from leo_subagents.skills_bridge.skill_discovery_simple import SkillDiscoverySystem

def test_skill_discovery():
    """测试技能发现系统"""
    discovery = SkillDiscoverySystem(project_root)
    
    # 更新注册表
    print("=== Testing Skill Discovery ===")
    result = discovery.update_registry()
    
    # 搜索测试
    print("\n=== Testing Search ===")
    results = discovery.search_skills("realestate")
    print(f"Found {len(results)} skills matching 'realestate':")
    for skill in results:
        print(f"  - {skill['name']} ({skill['category']})")
    
    # 状态报告
    print("\n=== Status Report ===")
    status = discovery.get_status_report()
    print(f"Total skills: {status['total_skills']}")
    print(f"Valid skills: {status['valid_skills']}")
    print(f"Invalid skills: {status['invalid_skills']}")
    
    # 生成Claude目录测试
    print("\n=== Claude Directory Generation ===")
    success = discovery.generate_claude_skills_directory()
    print(f"Generation: {'SUCCESS' if success else 'FAILED'}")
    
    print("\n[SUCCESS] All tests completed!")

if __name__ == "__main__":
    test_skill_discovery()