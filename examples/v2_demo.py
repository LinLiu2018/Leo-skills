#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Leo Wingman v2.0 快速演示
=========================
展示系统的核心能力
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))


def demo_auto_memory():
    """演示全自动记忆"""
    print("\n" + "="*50)
    print("🧠 演示 1: 全自动记忆系统")
    print("="*50)

    from leo_memory import get_auto_memory, auto_record, get_context

    # 1. 系统自动记录（无需干预）
    print("\n1️⃣ 自动记录用户查询...")
    mid1 = auto_record(
        event_type="user_query",
        content="我想找一个宁波的度假别墅，预算500万",
        agent="system",
        importance=4,
        tags=["villa", "ningbo", "investment"]
    )
    print(f"   ✓ 已记录: {mid1[:16]}...")

    # 2. Villa Agent 处理并记录
    print("\n2️⃣ Villa Agent 处理并记录结果...")
    from leo_subagents.agents.villa_agent.villa_agent import VillaAgent

    villa_agent = VillaAgent()
    result = villa_agent.execute(
        "推荐宁波度假别墅",
        context={"budget": 500, "location": "ningbo"}
    )
    print(f"   ✓ Agent 返回: {result.get('message', '成功')}")

    # 3. 另一个 Agent 自动获得相关记忆
    print("\n3️⃣ Leasing Agent 自动获取相关上下文...")
    context = get_context("leasing_agent", "客户需要投资方案")
    print(f"   ✓ 获取到 {len(context['relevant_memories'])} 条相关记忆")
    print(f"   ✓ 活跃 Agents: {context['active_agents']}")

    # 4. 查看会话摘要
    print("\n4️⃣ 会话摘要...")
    memory = get_auto_memory()
    summary = memory.get_session_summary()
    print(f"   会话ID: {summary['session_id'][:16]}...")
    print(f"   记忆总数: {summary['memory_count']}")
    print(f"   持续时间: {summary['duration_minutes']} 分钟")


def demo_agents():
    """演示多 Agent 协作"""
    print("\n" + "="*50)
    print("🤖 演示 2: 多 Agent 协作")
    print("="*50)

    # 房产 Agent
    print("\n1️⃣ Villa Agent (度假别墅)...")
    from leo_subagents.agents.villa_agent.villa_agent import VillaAgent
    villa = VillaAgent()
    result = villa.execute("推荐度假别墅", context={"budget": 500})
    print(f"   ✓ {result.get('message', '完成')}")

    # 贷款 Agent
    print("\n2️⃣ Loan Agent (贷款计算)...")
    from leo_subagents.agents.loan_agent.loan_agent import LoanAgent
    loan = LoanAgent()
    result = loan.execute(
        "计算贷款",
        context={"property_price": 500, "down_payment_percent": 30}
    )
    print(f"   ✓ 月供: {result.get('result', {}).get('monthly_payment', 0):.0f} 元")

    # 法拍 Agent
    print("\n3️⃣ Auction Agent (法拍房)...")
    from leo_subagents.agents.auction_agent.auction_agent import AuctionAgent
    auction = AuctionAgent()
    result = auction.execute("查找法拍房机会")
    print(f"   ✓ {result.get('message', '完成')}")

    # 内容 Agent
    print("\n4️⃣ Content Agent (内容创作)...")
    from leo_subagents.agents.content_agent.content_agent import ContentAgent
    content = ContentAgent()
    result = content.execute(
        "生成小红书文案",
        context={"product": "乐橙荟商铺", "platform": "xiaohongshu"}
    )
    print(f"   ✓ {result.get('message', '完成')}")


def demo_workflows():
    """演示工作流"""
    print("\n" + "="*50)
    print("📋 演示 3: 工作流")
    print("="*50)

    import yaml

    workflows = [
        ("villa_consulting_workflow", "别墅全流程咨询"),
        ("loan_calculator_workflow", "贷款计算"),
        ("weekly_sales_report", "每周销售报告"),
    ]

    for wf_file, wf_desc in workflows:
        print(f"\n📄 {wf_desc}...")
        try:
            with open(f"src/leo_workflows/definitions/{wf_file}.yaml", "r", encoding="utf-8") as f:
                wf = yaml.safe_load(f)
            print(f"   ✓ 工作流: {wf['name']}")
            print(f"   ✓ 步骤数: {len(wf.get('steps', []))}")
            print(f"   ✓ 触发器: {[t['type'] for t in wf.get('triggers', [])]}")
        except Exception as e:
            print(f"   ⚠ {e}")


def demo_user_profile():
    """演示用户画像"""
    print("\n" + "="*50)
    print("👤 演示 4: 统一用户画像")
    print("="*50)

    import json

    try:
        with open("leo_knowledge/context/user_profile.json", "r", encoding="utf-8") as f:
            profile = json.load(f)

        print(f"\n用户ID: {profile.get('user_id')}")
        print(f"业务板块: {list(profile.get('business_domains', {}).keys())}")
        print(f"学习系统: {'已启用' if profile.get('learning_system', {}).get('enabled') else '未启用'}")

        # 已学习模式
        patterns = profile.get('learning_system', {}).get('learned_patterns', {})
        if patterns:
            print(f"\n已学习模式:")
            for category, settings in patterns.items():
                print(f"  · {category}: {list(settings.keys())}")

    except Exception as e:
        print(f"⚠ 读取用户画像失败: {e}")


def show_stats():
    """显示系统统计"""
    print("\n" + "="*50)
    print("📊 Leo Wingman v2.0 系统统计")
    print("="*50)

    import os

    # 统计 Agents
    agents_dir = Path("src/leo_subagents/agents")
    agent_count = len([d for d in agents_dir.iterdir() if d.is_dir() and not d.name.startswith('_')])

    # 统计 Workflows
    workflows_dir = Path("src/leo_workflows/definitions")
    workflow_count = len(list(workflows_dir.glob("*.yaml")))

    # 统计 Skills
    skills_dir = Path("src/leo_skills")
    skill_count = sum(1 for _ in skills_dir.rglob("*Skill.md"))

    stats = {
        "Agents": agent_count,
        "Workflows": workflow_count,
        "业务板块": 7,
        "自动记忆": "✅",
        "自动进化": "✅",
    }

    for key, value in stats.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 Leo Wingman v2.0 快速演示")
    print("="*60)
    print("\n此演示展示系统的核心能力：")
    print("  1. 🧠 全自动记忆 - 自动记录、共享、学习")
    print("  2. 🤖 37个 Agent - 7大业务板块")
    print("  3. 📋 52个 Workflow - 自动化流程")
    print("  4. 👤 统一画像 - 越用越懂你")

    try:
        demo_auto_memory()
        demo_agents()
        demo_workflows()
        demo_user_profile()
        show_stats()

        print("\n" + "="*60)
        print("✅ 演示完成！")
        print("="*60)
        print("\n更多功能:")
        print("  · 查看文档: docs/guides/AUTO_MEMORY_GUIDE.md")
        print("  · 发布说明: docs/releases/RELEASE_v2.0.0.md")
        print("  · 更新日志: docs/guides/CHANGELOG.md")

    except Exception as e:
        print(f"\n❌ 演示出错: {e}")
        import traceback
        traceback.print_exc()
