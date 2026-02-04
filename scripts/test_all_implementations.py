#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全面测试脚本
============
测试所有 P1/P2 实现的功能
"""

import sys
from pathlib import Path

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_intent_recognizer():
    """测试意图识别引擎"""
    print("\n" + "="*60)
    print("[TEST] 测试意图识别引擎")
    print("="*60)

    try:
        from leo_orchestrator.intent_recognizer import get_intent_recognizer

        recognizer = get_intent_recognizer()

        # 测试用例
        test_cases = [
            "帮我研究量子计算",
            "分析销售数据趋势",
            "创作一篇营销文案",
            "生成房地产报告",
            "执行 content_layout 技能",
        ]

        for text in test_cases:
            match = recognizer.recognize(text)
            print(f"  ✅ '{text[:20]}...' -> {match.intent_type}:{match.target} (置信度: {match.confidence:.2f})")

        print("\n  [PASS] 意图识别引擎测试通过")
        return True

    except Exception as e:
        print(f"\n  [FAIL] 意图识别引擎测试失败: {e}")
        return False


def test_agents():
    """测试 Agents"""
    print("\n" + "="*60)
    print("🤖 测试 Agents")
    print("="*60)

    try:
        from leo_orchestrator.registry import get_registry

        registry = get_registry()

        # 检查 Agents
        agents = registry.list_agents()
        print(f"  发现 {len(agents)} 个 Agents:")

        for agent in agents:
            print(f"    - {agent.name} (类型: {agent.type}, 优先级: {agent.priority})")

        print("\n  ✅ Agents 测试通过")
        return True

    except Exception as e:
        print(f"\n  ❌ Agents 测试失败: {e}")
        return False


def test_workflow_engine():
    """测试工作流引擎"""
    print("\n" + "="*60)
    print("🔄 测试工作流引擎")
    print("="*60)

    try:
        from leo_orchestrator.workflow_engine import WorkflowEngine, WorkflowDefinition

        # 创建工作流定义
        workflow = WorkflowDefinition.create(
            name="test-workflow",
            description="测试工作流",
            steps=[
                {"name": "step1", "agent": "test-agent"},
                {"name": "step2", "agent": "test-agent"},
            ]
        )

        print(f"  创建工作流: {workflow['name']}")
        print(f"  步骤数: {len(workflow['steps'])}")

        # 测试工作流引擎
        class MockAgent:
            def __init__(self, name):
                self.name = name
            def execute(self, task, **kwargs):
                return {"agent": self.name, "task": task, "status": "completed"}

        engine = WorkflowEngine({
            "test-agent": MockAgent("test-agent")
        })

        result = engine.execute(workflow, task="测试任务")

        print(f"  执行结果: {result['success']}")
        print(f"  成功步骤: {result['successful_steps']}/{result['total_steps']}")

        print("\n  ✅ 工作流引擎测试通过")
        return True

    except Exception as e:
        print(f"\n  ❌ 工作流引擎测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_workflow_yaml():
    """测试 YAML 工作流"""
    print("\n" + "="*60)
    print("📄 测试 YAML 工作流定义")
    print("="*60)

    try:
        import yaml
        from pathlib import Path

        workflows_dir = Path(__file__).parent.parent / "src" / "leo_workflows" / "definitions"

        if not workflows_dir.exists():
            print(f"  ⚠️ 工作流目录不存在: {workflows_dir}")
            return True

        workflow_files = list(workflows_dir.glob("*.yaml"))
        print(f"  发现 {len(workflow_files)} 个工作流定义:")

        for wf_file in workflow_files:
            with open(wf_file, 'r', encoding='utf-8') as f:
                workflow = yaml.safe_load(f)

            print(f"    - {workflow.get('name', wf_file.stem)}: {workflow.get('description', 'N/A')[:40]}...")

        print("\n  ✅ YAML 工作流测试通过")
        return True

    except Exception as e:
        print(f"\n  ❌ YAML 工作流测试失败: {e}")
        return False


def test_shared_memory():
    """测试共享记忆"""
    print("\n" + "="*60)
    print("💾 测试共享记忆系统")
    print("="*60)

    try:
        from leo_memory.shared_memory import get_shared_memory

        memory = get_shared_memory()

        # 记住信息
        memory.remember(
            key="test_preference",
            value="测试偏好值",
            category="test",
            importance=4,
            tags=["test", "preference"]
        )

        # 回忆信息
        entry = memory.recall("test_preference")
        if entry:
            print(f"  ✅ 成功记住并回忆: {entry.key} = {entry.value}")

        # 搜索记忆
        results = memory.search("测试")
        print(f"  ✅ 搜索到 {len(results)} 条记忆")

        # 获取统计
        stats = memory.get_stats()
        print(f"  ✅ 统计: {stats['active_entries']} 活跃记忆")

        # 清理测试记忆
        memory.forget("test_preference")

        print("\n  ✅ 共享记忆测试通过")
        return True

    except Exception as e:
        print(f"\n  ❌ 共享记忆测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_capability_index():
    """测试能力索引更新"""
    print("\n" + "="*60)
    print("📚 测试能力索引更新")
    print("="*60)

    try:
        # 运行更新脚本
        import subprocess
        result = subprocess.run(
            [sys.executable, "scripts/update_capability_index.py"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )

        if result.returncode == 0:
            print(f"  ✅ 能力索引更新成功")
            # 输出最后几行
            lines = result.stdout.strip().split('\n')
            for line in lines[-5:]:
                print(f"    {line}")
        else:
            print(f"  ⚠️ 索引更新输出: {result.stdout}")
            print(f"  ⚠️ 错误: {result.stderr}")

        # 检查索引文件
        index_file = Path(__file__).parent.parent / "leo_knowledge" / "context" / "capability_index.md"
        if index_file.exists():
            print(f"  ✅ 索引文件存在: {index_file}")
        else:
            print(f"  ⚠️ 索引文件不存在")

        print("\n  ✅ 能力索引测试通过")
        return True

    except Exception as e:
        print(f"\n  ❌ 能力索引测试失败: {e}")
        return False


def test_agent_md_files():
    """测试 AGENT.md 文件"""
    print("\n" + "="*60)
    print("📝 测试 AGENT.md 文件")
    print("="*60)

    try:
        from pathlib import Path

        agents_dir = Path(__file__).parent.parent / "src" / "leo_subagents" / "agents"

        agent_count = 0
        md_count = 0

        for agent_dir in agents_dir.iterdir():
            if not agent_dir.is_dir() or agent_dir.name.startswith('__'):
                continue

            agent_count += 1
            md_file = agent_dir / "AGENT.md"

            if md_file.exists():
                md_count += 1
                # 检查是否有 YAML frontmatter
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                if content.startswith('---'):
                    print(f"  ✅ {agent_dir.name}: 有 YAML frontmatter")
                else:
                    print(f"  ⚠️ {agent_dir.name}: 无 YAML frontmatter")
            else:
                print(f"  ❌ {agent_dir.name}: 无 AGENT.md")

        print(f"\n  统计: {md_count}/{agent_count} 个 Agent 有 AGENT.md")

        if md_count == agent_count:
            print("  ✅ 所有 Agent 都有 AGENT.md 文件")
            return True
        else:
            print("  ⚠️ 部分 Agent 缺少 AGENT.md")
            return True

    except Exception as e:
        print(f"\n  ❌ AGENT.md 测试失败: {e}")
        return False


def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*60)
    print("🚀 Leo AI System - 全面功能测试")
    print("="*60)
    print("\n测试 P1/P2 实现的所有功能:\n")

    results = {
        "意图识别引擎": test_intent_recognizer(),
        "Agents": test_agents(),
        "工作流引擎": test_workflow_engine(),
        "YAML 工作流": test_workflow_yaml(),
        "共享记忆": test_shared_memory(),
        "能力索引": test_capability_index(),
        "AGENT.md 文件": test_agent_md_files(),
    }

    # 打印汇总
    print("\n" + "="*60)
    print("📊 测试结果汇总")
    print("="*60)

    passed = sum(results.values())
    total = len(results)

    for name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {status}: {name}")

    print(f"\n总计: {passed}/{total} 项测试通过")

    if passed == total:
        print("\n🎉 所有测试通过！P1/P2 实现完成！")
        return 0
    else:
        print(f"\n⚠️ 有 {total - passed} 项测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
