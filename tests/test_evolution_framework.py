#!/usr/bin/env python3
"""
简单测试脚本 - 验证进化框架基本功能
"""

import sys
import os
from pathlib import Path

# 设置Python路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# 设置工作目录
os.chdir(project_root)

print("=" * 60)
print("Leo Skills 进化框架 - 基础测试")
print("=" * 60)

# 测试导入
print("\n[1/5] 测试模块导入...")
try:
    from leo_skills.core.evolution import (
        EvolvableSkill,
        ExecutionMetrics,
        SkillLearner,
        SkillEvolver,
        SkillAdapter
    )
    print("✓ 所有模块导入成功")
except Exception as e:
    print(f"✗ 导入失败: {e}")
    sys.exit(1)

# 测试数据结构
print("\n[2/5] 测试数据结构...")
try:
    from datetime import datetime
    metrics = ExecutionMetrics(
        skill_name="test",
        timestamp=datetime.now(),
        success=True,
        duration=1.5,
        quality_score=0.8
    )
    print(f"✓ ExecutionMetrics 创建成功: {metrics.skill_name}")
except Exception as e:
    print(f"✗ 数据结构测试失败: {e}")
    sys.exit(1)

# 测试学习器
print("\n[3/5] 测试学习器...")
try:
    learner = SkillLearner("test-skill")
    print(f"✓ SkillLearner 创建成功")
    print(f"  数据目录: {learner.data_dir}")
except Exception as e:
    print(f"✗ 学习器测试失败: {e}")
    sys.exit(1)

# 测试进化器
print("\n[4/5] 测试进化器...")
try:
    evolver = SkillEvolver("test-skill")
    print(f"✓ SkillEvolver 创建成功")
except Exception as e:
    print(f"✗ 进化器测试失败: {e}")
    sys.exit(1)

# 测试适配器
print("\n[5/5] 测试适配器...")
try:
    # 创建临时配置文件
    test_config_path = project_root / "leo-skills" / ".evolution_data" / "test_config.yaml"
    test_config_path.parent.mkdir(parents=True, exist_ok=True)

    with open(test_config_path, 'w') as f:
        f.write("test: true\n")

    adapter = SkillAdapter("test-skill", str(test_config_path))
    print(f"✓ SkillAdapter 创建成功")

    # 清理
    test_config_path.unlink()
except Exception as e:
    print(f"✗ 适配器测试失败: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✓ 所有基础测试通过！")
print("=" * 60)
print("\n进化框架已就绪，可以开始使用。")
print("\n下一步:")
print("1. 查看文档: leo-skills/core/evolution/README.md")
print("2. 参考配置模板: leo-skills/core/evolution/config/evolution_config_template.yaml")
print("3. 改造你的技能以支持进化能力")
