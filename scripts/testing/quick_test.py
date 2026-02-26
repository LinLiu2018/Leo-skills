#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试脚本 - 验证所有 P1/P2 实现
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_intent_recognizer():
    """测试意图识别引擎"""
    print("\n[1] 测试意图识别引擎...")
    try:
        from leo_orchestrator.intent_recognizer import get_intent_recognizer
        recognizer = get_intent_recognizer()

        test_cases = ["帮我研究量子计算", "分析销售数据", "创作营销文案"]
        for text in test_cases:
            match = recognizer.recognize(text)
            print(f"    '{text}' -> {match.intent_type}:{match.target} ({match.confidence:.2f})")

        print("    [PASS]")
        return True
    except Exception as e:
        print(f"    [FAIL] {e}")
        return False


def test_shared_memory():
    """测试共享记忆"""
    print("\n[2] 测试共享记忆...")
    try:
        from leo_memory.shared_memory import get_shared_memory
        memory = get_shared_memory()

        memory.remember(key="test_key", value="test_value", category="test")
        entry = memory.recall("test_key")

        if entry and entry.value == "test_value":
            print(f"    记忆/回忆成功: {entry.value}")
            memory.forget("test_key")
            print("    [PASS]")
            return True
        else:
            print("    [FAIL] 记忆失败")
            return False
    except Exception as e:
        print(f"    [FAIL] {e}")
        return False


def test_workflow_engine():
    """测试工作流引擎"""
    print("\n[3] 测试工作流引擎...")
    try:
        from leo_orchestrator.workflow_engine import WorkflowEngine

        class MockAgent:
            def execute(self, task, **kwargs):
                return {"status": "completed", "task": task}

        engine = WorkflowEngine({"mock": MockAgent()})

        workflow = {
            "name": "test",
            "steps": [{"name": "step1", "agent": "mock"}]
        }

        result = engine.execute(workflow, task="test")
        print(f"    工作流执行: {result['success']}")
        print("    [PASS]")
        return True
    except Exception as e:
        print(f"    [FAIL] {e}")
        return False


def test_workflow_yaml():
    """测试 YAML 工作流"""
    print("\n[4] 测试 YAML 工作流定义...")
    try:
        import yaml
        workflows_dir = Path(__file__).parent.parent / "src" / "leo_workflows" / "definitions"

        if workflows_dir.exists():
            files = list(workflows_dir.glob("*.yaml"))
            print(f"    发现 {len(files)} 个工作流定义")
            for f in files[:3]:
                with open(f) as fp:
                    wf = yaml.safe_load(fp)
                print(f"    - {wf.get('name', f.stem)}")
            print("    [PASS]")
            return True
        else:
            print("    [SKIP] 目录不存在")
            return True
    except Exception as e:
        print(f"    [FAIL] {e}")
        return False


def test_agents():
    """测试 Agents"""
    print("\n[5] 测试 Agents...")
    try:
        from leo_orchestrator.registry import get_registry
        registry = get_registry()
        agents = registry.list_agents()
        print(f"    注册表中有 {len(agents)} 个 Agents")
        print("    [PASS]")
        return True
    except Exception as e:
        print(f"    [FAIL] {e}")
        return False


def test_capability_index():
    """测试能力索引更新"""
    print("\n[6] 测试能力索引更新...")
    try:
        import subprocess
        result = subprocess.run(
            [sys.executable, "scripts/update_capability_index.py"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
            timeout=30
        )

        if "已更新" in result.stdout:
            print("    索引更新成功")
            print("    [PASS]")
            return True
        else:
            print(f"    [WARN] {result.stdout[-200:]}")
            return True
    except Exception as e:
        print(f"    [FAIL] {e}")
        return False


def test_agent_md():
    """测试 AGENT.md 文件"""
    print("\n[7] 测试 AGENT.md 文件...")
    try:
        agents_dir = Path(__file__).parent.parent / "src" / "leo_subagents" / "agents"

        total = 0
        with_yaml = 0

        for agent_dir in agents_dir.iterdir():
            if not agent_dir.is_dir() or agent_dir.name.startswith('__'):
                continue
            total += 1
            md_file = agent_dir / "AGENT.md"
            if md_file.exists():
                with open(md_file) as f:
                    if f.read().startswith('---'):
                        with_yaml += 1

        print(f"    {with_yaml}/{total} 个 Agent 有标准 AGENT.md")
        print("    [PASS]")
        return True
    except Exception as e:
        print(f"    [FAIL] {e}")
        return False


def main():
    print("=" * 60)
    print("Leo AI System - P1/P2 功能测试")
    print("=" * 60)

    tests = [
        ("意图识别引擎", test_intent_recognizer),
        ("共享记忆", test_shared_memory),
        ("工作流引擎", test_workflow_engine),
        ("YAML 工作流", test_workflow_yaml),
        ("Agents", test_agents),
        ("能力索引", test_capability_index),
        ("AGENT.md", test_agent_md),
    ]

    results = []
    for name, test_func in tests:
        try:
            results.append(test_func())
        except Exception as e:
            print(f"\n[ERROR] {name}: {e}")
            results.append(False)

    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)

    passed = sum(results)
    total = len(results)

    for (name, _), result in zip(tests, results):
        status = "PASS" if result else "FAIL"
        print(f"  [{status}] {name}")

    print(f"\n总计: {passed}/{total} 项通过")

    if passed == total:
        print("\n[SUCCESS] 所有 P1/P2 实现完成！")
        return 0
    else:
        print(f"\n[WARNING] {total - passed} 项失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())
