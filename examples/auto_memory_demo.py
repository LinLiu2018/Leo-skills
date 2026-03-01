# -*- coding: utf-8 -*-
"""
全自动记忆系统演示
==================
展示如何使用自动记忆功能
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from leo_memory import (
    get_auto_memory,
    auto_record,
    get_context,
    auto_memorize,
    get_system_capture
)


# 示例 1: 基础自动记录
print("=" * 50)
print("示例 1: 自动记录记忆")
print("=" * 50)

# 自动记录用户输入（系统会自动捕获）
mem_id = auto_record(
    event_type="user_input",
    content="我想找一个宁波的度假别墅，预算500万左右",
    agent="system",
    importance=4,
    tags=["user_query", "villa", "ningbo"]
)
print(f"✓ 已记录用户查询: {mem_id}")

# 自动记录 Agent 处理
auto_record(
    event_type="agent_response",
    content="已推荐3个符合预算的度假别墅项目",
    agent="villa_agent",
    importance=4,
    tags=["villa", "recommendation"]
)
print("✓ 已记录 Agent 响应")


# 示例 2: 自动获取上下文
print("\n" + "=" * 50)
print("示例 2: 自动获取相关上下文")
print("=" * 50)

# 另一个 Agent 处理相关任务时，自动获取上下文
context = get_context("leasing_agent", "客户需要商铺投资方案")
print(f"✓ 获取到 {len(context['relevant_memories'])} 条相关记忆")
print(f"✓ 活跃 Agent: {context['active_agents']}")
print(f"✓ 用户偏好: {list(context['user_preferences'].keys())}")


# 示例 3: Agent 自动记忆装饰器
print("\n" + "=" * 50)
print("示例 3: Agent 自动获得记忆能力")
print("=" * 50)


class DemoAgent:
    """演示 Agent"""
    name = "demo_agent"

    def execute(self, task, context=None):
        """执行任务"""
        # 自动注入的记忆上下文
        if context and '_injected_memory' in context:
            print(f"✓ 自动获取记忆上下文: {len(context['_injected_memory']['relevant_memories'])} 条")

        return {"status": "success", "task": task}


# 使用装饰器让 Agent 自动获得记忆
DemoAgent = auto_memorize(DemoAgent)

# 创建实例并执行
agent = DemoAgent()
result = agent.execute("测试任务", context={"test": True})
print(f"✓ Agent 执行完成，结果包含记忆引用: {'_memory_reference' in result}")


# 示例 4: 系统级捕获
print("\n" + "=" * 50)
print("示例 4: 系统级事件捕获")
print("=" * 50)

capture = get_system_capture()

# 捕获工具调用
capture.capture_tool_call(
    tool_name="web_search",
    params={"query": "宁波别墅价格"},
    result={"count": 10}
)
print("✓ 已捕获工具调用")

# 捕获用户修正
capture.capture_correction(
    original="字体22px",
    corrected="字体17px",
    reason="表格内容太拥挤"
)
print("✓ 已捕获用户修正（用于学习）")


# 示例 5: 会话摘要
print("\n" + "=" * 50)
print("示例 5: 会话摘要")
print("=" * 50)

memory = get_auto_memory()
summary = memory.get_session_summary()

print(f"会话ID: {summary['session_id'][:8]}...")
print(f"持续时间: {summary['duration_minutes']} 分钟")
print(f"记忆总数: {summary['memory_count']}")
print(f"活跃Agent: {summary['active_agents']}")
print(f"涉及主题: {summary['topics']}")


# 示例 6: 主动回忆
print("\n" + "=" * 50)
print("示例 6: 主动回忆相关记忆")
print("=" * 50)

# 自动召回与"别墅"相关的记忆
relevant = memory.recall(query="别墅投资", top_k=3)
print(f"✓ 找到 {len(relevant)} 条相关记忆:")
for mem in relevant:
    print(f"  - [{mem['event_type']}] {mem['content'][:50]}...")


print("\n" + "=" * 50)
print("演示完成！")
print("=" * 50)
print("\n关键特性:")
print("1. ✓ 自动记录 - 无需显式调用")
print("2. ✓ 跨 Agent 共享 - 自动获取相关记忆")
print("3. ✓ 主动注入 - 自动为 Agent 提供上下文")
print("4. ✓ 错误捕获 - 自动记录异常")
print("5. ✓ 用户修正 - 自动学习用户反馈")
