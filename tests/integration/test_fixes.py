#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动化测试脚本 - 验证所有修复是否生效
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))


def test_config_manager():
    """测试配置中心"""
    print("\n" + "=" * 60)
    print("测试 1: 配置中心 (ConfigManager)")
    print("=" * 60)

    try:
        from src.leo_config.config_manager import config

        port = config.get("gateway.port")
        print(f"✓ 配置加载成功")
        print(f"  - gateway.port: {port}")

        session_timeout = config.get("session.timeout")
        print(f"  - session.timeout: {session_timeout}")

        # 测试默认值
        nonexistent = config.get("nonexistent.key", "default_value")
        assert nonexistent == "default_value", "默认值未生效"
        print(f"  - 默认值测试: 通过")

        return True
    except Exception as e:
        print(f"✗ 配置中心测试失败: {e}")
        return False


def test_session_persistence():
    """测试 Session 持久化"""
    print("\n" + "=" * 60)
    print("测试 2: Session 持久化")
    print("=" * 60)

    try:
        from src.leo_gateway.session import Session

        # 创建会话并添加消息
        session = Session(id="test_session", user_id="user_001", channel="feishu")
        session.add_message({"role": "user", "content": "测试消息1"})
        session.add_message({"role": "assistant", "content": "测试回复1"})

        # 转换为字典
        data = session.to_dict()

        # 验证 messages 字段存在
        assert "messages" in data, "to_dict() 缺少 messages 字段"
        assert len(data["messages"]) == 2, f"消息数量不正确: {len(data['messages'])}"
        print(f"✓ Session.to_dict() 包含 messages 字段")
        print(f"  - 消息数量: {len(data['messages'])}")

        # 验证从字典恢复
        restored = Session.from_dict(data)
        assert len(restored.messages) == 2, "恢复后的消息数量不正确"
        print(f"✓ Session.from_dict() 正确恢复消息")

        return True
    except Exception as e:
        print(f"✗ Session 持久化测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_session_message_limit():
    """测试 Session 消息数量限制"""
    print("\n" + "=" * 60)
    print("测试 3: Session 消息数量限制")
    print("=" * 60)

    try:
        from src.leo_gateway.session import Session

        session = Session(id="test_limit", user_id="user_002", channel="test")

        # 添加超过限制的消息 (MAX_MESSAGES = 1000)
        for i in range(1200):
            session.add_message({"role": "user", "content": f"消息{i}"})

        # 验证消息被限制
        assert len(session.messages) <= session.MAX_MESSAGES, \
            f"消息数量未限制: {len(session.messages)}"
        print(f"✓ 消息数量限制生效")
        print(f"  - 添加消息: 1200")
        print(f"  - 实际保留: {len(session.messages)} (限制: {session.MAX_MESSAGES})")

        return True
    except Exception as e:
        print(f"✗ 消息限制测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_self_improvement_exports():
    """测试自优化模块导出"""
    print("\n" + "=" * 60)
    print("测试 4: 自优化模块导出")
    print("=" * 60)

    try:
        from src.leo_skills.core.self_improvement import (
            ConversationAnalyzer,
            SkillRecommender,
            PerformanceTracker,
            SelfOptimizationEngine,
            run_self_optimization,
            AutoSkillGenerator,
            auto_generate_skill,
            CrossUserLearning,
            contribute_user_patterns,
            get_global_insights,
        )

        print(f"✓ 所有组件导入成功")
        print(f"  - ConversationAnalyzer")
        print(f"  - SkillRecommender")
        print(f"  - PerformanceTracker")
        print(f"  - SelfOptimizationEngine")
        print(f"  - AutoSkillGenerator")
        print(f"  - CrossUserLearning")

        # 验证类可以实例化
        analyzer = ConversationAnalyzer()
        print(f"✓ ConversationAnalyzer 可以实例化")

        return True
    except Exception as e:
        print(f"✗ 模块导出测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_registry_triggers():
    """测试 Registry triggers 字段"""
    print("\n" + "=" * 60)
    print("测试 5: Registry triggers 字段")
    print("=" * 60)

    try:
        from src.leo_orchestrator.registry import (
            SkillRegistration,
            AgentRegistration,
            UnifiedRegistry,
        )

        # 测试 SkillRegistration
        skill = SkillRegistration(
            name="test_skill",
            path="test/path",
            category="test",
            triggers=["trigger1", "trigger2"],
        )
        assert hasattr(skill, "triggers"), "SkillRegistration 缺少 triggers 字段"
        assert skill.triggers == ["trigger1", "trigger2"], "triggers 值不正确"
        print(f"✓ SkillRegistration 包含 triggers 字段")

        # 测试 get_all_triggers
        all_triggers = skill.get_all_triggers()
        assert "trigger1" in all_triggers, "get_all_triggers 返回不正确"
        print(f"✓ get_all_triggers() 方法工作正常")

        # 测试 AgentRegistration
        agent = AgentRegistration(
            name="test_agent",
            type="executor",
            priority=1,
            triggers=["agent_trigger"],
        )
        assert hasattr(agent, "triggers"), "AgentRegistration 缺少 triggers 字段"
        print(f"✓ AgentRegistration 包含 triggers 字段")

        # 测试变更通知机制
        registry = UnifiedRegistry()
        assert hasattr(registry, "register_change_listener"), "缺少 register_change_listener"
        assert hasattr(registry, "_notify_change"), "缺少 _notify_change"
        print(f"✓ UnifiedRegistry 包含变更通知机制")

        return True
    except Exception as e:
        print(f"✗ Registry triggers 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_task_queue():
    """测试异步任务队列"""
    print("\n" + "=" * 60)
    print("测试 6: 异步任务队列")
    print("=" * 60)

    try:
        from src.leo_gateway.task_queue import TaskQueue, get_task_queue

        # 测试任务队列创建
        queue = TaskQueue(max_workers=2)
        print(f"✓ TaskQueue 可以创建")

        # 启动队列
        await queue.start()
        assert queue._running, "任务队列未启动"
        print(f"✓ TaskQueue 可以启动")

        # 提交测试任务
        task_id = await queue.submit(
            agent_name="test_agent",
            task_description="这是一个测试任务",
            context={"param": "value"},
        )
        print(f"✓ 任务提交成功: {task_id[:8]}...")

        # 查询任务状态
        await asyncio.sleep(0.5)  # 等待任务处理
        status = queue.get_task_status(task_id)
        assert status is not None, "任务状态查询失败"
        print(f"✓ 任务状态查询成功: {status['status']}")

        # 停止队列
        await queue.stop()
        print(f"✓ TaskQueue 可以停止")

        return True
    except Exception as e:
        print(f"✗ 任务队列测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_smart_router_listeners():
    """测试 SmartRouter 变更监听"""
    print("\n" + "=" * 60)
    print("测试 7: SmartRouter 变更监听")
    print("=" * 60)

    try:
        from src.leo_gateway.router import SmartRouter
        from src.leo_orchestrator.registry import UnifiedRegistry

        registry = UnifiedRegistry()

        # 检查 SmartRouter 是否有监听方法
        router = SmartRouter(registry=registry, auto_sync=False)

        assert hasattr(router, "_on_registry_change"), "缺少 _on_registry_change 方法"
        assert hasattr(router, "_sync_single_skill"), "缺少 _sync_single_skill 方法"
        assert hasattr(router, "_sync_single_agent"), "缺少 _sync_single_agent 方法"
        assert hasattr(router, "_remove_item_routes"), "缺少 _remove_item_routes 方法"

        print(f"✓ SmartRouter 包含变更监听方法")

        # 测试增量同步
        registry.register_skill(
            "test_incremental_skill",
            "test/path",
            "test",
            triggers=["test_trigger"],
        )

        # 检查路由表是否更新
        assert "test_trigger" in router._keyword_rules, "增量同步未生效"
        print(f"✓ 增量同步生效: test_trigger 已添加到路由表")

        # 测试移除
        router._remove_item_routes("test_incremental_skill")
        assert "test_trigger" not in router._keyword_rules, "路由移除未生效"
        print(f"✓ 路由移除生效")

        return True
    except Exception as e:
        print(f"✗ SmartRouter 监听测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("开始自动化测试")
    print("=" * 60)

    results = []

    # 同步测试
    results.append(("配置中心", test_config_manager()))
    results.append(("Session 持久化", test_session_persistence()))
    results.append(("消息数量限制", test_session_message_limit()))
    results.append(("模块导出", test_self_improvement_exports()))
    results.append(("Registry triggers", test_registry_triggers()))
    results.append(("SmartRouter 监听", test_smart_router_listeners()))

    # 异步测试
    results.append(("任务队列", await test_task_queue()))

    # 打印汇总
    print("\n" + "=" * 60)
    print("测试汇总")
    print("=" * 60)

    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{status}: {name}")

    print("\n" + "=" * 60)
    print(f"总计: {passed}/{total} 通过 ({passed/total*100:.0f}%)")
    print("=" * 60)

    return passed == total


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
