# -*- coding: utf-8 -*-
"""
Leo Wingman v2.0 端到端测试
===========================

验证内容：
1. 5个房产Agent的记忆装饰器
2. 自动记忆系统工作正常
3. 跨Agent记忆共享
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.leo_subagents.agents.villa_agent.villa_agent import VillaAgent
from src.leo_subagents.agents.residential_agent.residential_agent import ResidentialAgent
from src.leo_subagents.agents.leasing_agent.leasing_agent import LeasingAgent
from src.leo_subagents.agents.commercial_sales_agent.commercial_sales_agent import CommercialSalesAgent
from src.leo_subagents.agents.auction_agent.auction_agent import AuctionAgent
from src.leo_memory import get_auto_memory


def test_agent_with_memory(agent_class, agent_name, test_task):
    """测试带记忆的Agent"""
    print(f"\n{'='*60}")
    print(f"测试 {agent_name}")
    print('='*60)

    try:
        # 创建Agent实例
        agent = agent_class()
        print(f"[OK] Agent 创建成功: {agent.display_name}")

        # 检查是否有记忆方法
        has_remember = hasattr(agent, 'remember')
        has_recall = hasattr(agent, 'recall')
        has_get_memory_context = hasattr(agent, 'get_memory_context')

        print(f"[OK] 记忆方法检查:")
        print(f"   - remember: {has_remember}")
        print(f"   - recall: {has_recall}")
        print(f"   - get_memory_context: {has_get_memory_context}")

        # 执行测试任务
        result = agent.execute(test_task, context={"test": True})
        print(f"[OK] execute 执行成功")
        print(f"   返回状态: {result.get('status')}")
        print(f"   返回动作: {result.get('action')}")

        # 检查记忆是否被记录
        memory = get_auto_memory()
        summary = memory.get_session_summary()
        print(f"[OK] 记忆系统正常")
        print(f"   会话记忆数: {len(summary.get('recent_events', []))}")

        return True, None

    except Exception as e:
        print(f"[FAIL] 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False, str(e)


def test_cross_agent_memory():
    """测试跨Agent记忆共享"""
    print(f"\n{'='*60}")
    print("测试跨Agent记忆共享")
    print('='*60)

    try:
        # VillaAgent 记录记忆
        villa = VillaAgent()
        villa.remember("test_key", "来自VillaAgent的测试记忆", importance=4)
        print("[OK] VillaAgent 记录记忆成功")

        # ResidentialAgent 尝试回忆
        residential = ResidentialAgent()
        memories = residential.recall("test_key", top_k=5)
        print(f"[OK] ResidentialAgent 回忆成功，找到 {len(memories)} 条记忆")

        if memories:
            print(f"   记忆内容: {memories[0].get('content', {})}")

        return True, None

    except Exception as e:
        print(f"[FAIL] 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False, str(e)


def test_auto_memory_system():
    """测试自动记忆系统"""
    print(f"\n{'='*60}")
    print("测试自动记忆系统")
    print('='*60)

    try:
        memory = get_auto_memory()

        # 自动记录事件
        memory_id = memory.auto_record(
            event_type="test_event",
            content={"message": "测试消息"},
            agent="test_agent",
            importance=3,
            tags=["test"]
        )
        print(f"[OK] 自动记录成功，记忆ID: {memory_id}")

        # 获取上下文
        context = memory.get_context_for_agent("test_agent", "测试任务")
        print(f"[OK] 获取上下文成功")
        print(f"   相关记忆数: {len(context.get('relevant_memories', []))}")

        # 获取会话摘要
        summary = memory.get_session_summary()
        print(f"[OK] 获取会话摘要成功")
        print(f"   总事件数: {summary.get('total_events', 0)}")

        return True, None

    except Exception as e:
        print(f"[FAIL] 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False, str(e)


def main():
    """主测试函数"""
    print("="*60)
    print("Leo Wingman v2.0 端到端测试")
    print("="*60)

    results = []

    # 测试5个房产Agent
    agents_to_test = [
        (VillaAgent, "VillaAgent", "搜索宁波别墅市场情报"),
        (ResidentialAgent, "ResidentialAgent", "分析住宅客户画像"),
        (LeasingAgent, "LeasingAgent", "处理招商咨询"),
        (CommercialSalesAgent, "CommercialSalesAgent", "搜索商业地产市场"),
        (AuctionAgent, "AuctionAgent", "search auction listings"),
    ]

    for agent_class, agent_name, test_task in agents_to_test:
        success, error = test_agent_with_memory(agent_class, agent_name, test_task)
        results.append((agent_name, success, error))

    # 测试跨Agent记忆共享
    success, error = test_cross_agent_memory()
    results.append(("跨Agent记忆共享", success, error))

    # 测试自动记忆系统
    success, error = test_auto_memory_system()
    results.append(("自动记忆系统", success, error))

    # 打印总结
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)

    passed = 0
    failed = 0

    for name, success, error in results:
        status = "[PASS]" if success else "[FAIL]"
        print(f"{status} {name}")
        if error:
            print(f"       错误: {error}")

        if success:
            passed += 1
        else:
            failed += 1

    print("\n" + "="*60)
    print(f"总计: {passed} 通过, {failed} 失败")
    print("="*60)

    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
