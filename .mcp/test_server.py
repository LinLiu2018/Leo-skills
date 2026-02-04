#!/usr/bin/env python3
"""
Leo MCP Server 测试脚本
测试 MCP Server 是否正常工作
"""

import asyncio
import json
import sys
import os

# 添加 Leo System 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
os.environ['PYTHONIOENCODING'] = 'utf-8'


async def test_mcp_server():
    """测试 MCP Server 的各个功能"""
    print("=" * 60)
    print("🧪 测试 Leo MCP Server")
    print("=" * 60)
    
    from leo_mcp_server import LeoMCPServer
    
    server = LeoMCPServer()
    
    # 1. 测试初始化
    print("\n1️⃣ 测试初始化...")
    await server.initialize()
    print("   ✅ 初始化成功")
    
    # 2. 测试能力列表
    print("\n2️⃣ 测试能力列表...")
    capabilities = await server.list_capabilities()
    print(f"   - Skills: {len(capabilities['skills'])}")
    print(f"   - Agents: {len(capabilities['agents'])}")
    print(f"   - Workflows: {len(capabilities['workflows'])}")
    print("   ✅ 能力列表获取成功")
    
    # 3. 测试 Skills 工具列表
    print("\n3️⃣ 测试 Skills 工具转换...")
    skills = server.get_skills_as_tools()
    print(f"   转换了 {len(skills)} 个 Skills 为工具")
    if skills:
        print(f"   示例: {skills[0]['name']}")
    print("   ✅ Skills 工具转换成功")
    
    # 4. 测试 Agents 工具列表
    print("\n4️⃣ 测试 Agents 工具转换...")
    agents = server.get_agents_as_tools()
    print(f"   转换了 {len(agents)} 个 Agents 为工具")
    if agents:
        print(f"   示例: {agents[0]['name']}")
        # 查找 realestate_agent
        for agent in agents:
            if 'realestate' in agent['name']:
                print(f"   🎯 找到房产代理: {agent['name']}")
                break
    print("   ✅ Agents 工具转换成功")
    
    # 5. 测试 Workflows 工具列表
    print("\n5️⃣ 测试 Workflows 工具转换...")
    workflows = server.get_workflows_as_tools()
    print(f"   转换了 {len(workflows)} 个 Workflows 为工具")
    if workflows:
        print(f"   示例: {workflows[0]['name']}")
    print("   ✅ Workflows 工具转换成功")
    
    # 6. 测试执行（模拟）
    print("\n6️⃣ 测试能力查询...")
    result = await server.execute_agent(
        "realestate_agent",
        "分析宁波房产市场",
        {"region": "宁波", "type": "新房"}
    )
    print(f"   响应: {json.dumps(result, ensure_ascii=False, indent=4)}")
    print("   ✅ 执行测试完成")
    
    print("\n" + "=" * 60)
    print("🎉 所有测试通过！")
    print("=" * 60)
    
    print("\n📋 使用说明:")
    print("   启动 MCP Server:")
    print("   python leo_mcp_server.py")
    print()
    print("   可用工具:")
    print(f"   - {len(skills)} 个 Skills 工具 (leo_skill_*)")
    print(f"   - {len(agents)} 个 Agents 工具 (leo_agent_*)")
    print(f"   - {len(workflows)} 个 Workflows 工具 (leo_workflow_*)")


if __name__ == "__main__":
    asyncio.run(test_mcp_server())
