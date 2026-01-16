#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
进化框架基础测试 - 在leo-skills目录下运行
"""

import sys
import io
from pathlib import Path

# 设置UTF-8输出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 60)
print("Leo Skills 进化框架 - 基础测试")
print("=" * 60)

# 测试导入
print("\n[1/5] 测试模块导入...")
try:
    from core.evolution import (
        EvolvableSkill,
        ExecutionMetrics,
        SkillLearner,
        SkillEvolver,
        SkillAdapter
    )
    print("✓ 所有模块导入成功")
except Exception as e:
    print(f"✗ 导入失败: {e}")
    import traceback
    traceback.print_exc()
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
    test_config_path = Path(__file__).parent / ".evolution_data" / "test_config.yaml"
    test_config_path.parent.mkdir(parents=True, exist_ok=True)

    with open(test_config_path, 'w', encoding='utf-8') as f:
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
print("1. 查看文档: core/evolution/README.md")
print("2. 参考配置模板: core/evolution/config/evolution_config_template.yaml")
print("3. 改造你的技能以支持进化能力")
print("\n框架文件:")
print("  - core/evolution/metrics.py      # 数据结构定义")
print("  - core/evolution/learner.py      # 学习器")
print("  - core/evolution/evolver.py      # 进化器")
print("  - core/evolution/adapter.py      # 适配器")
print("  - core/evolution/performer.py    # 可进化技能基类")
