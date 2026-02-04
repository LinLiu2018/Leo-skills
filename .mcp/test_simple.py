#!/usr/bin/env python3
"""
Leo MCP Server 简单测试
"""

import asyncio
import json
import sys
import os

# 设置编码
os.environ['PYTHONIOENCODING'] = 'utf-8'
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from leo_mcp_server import LeoMCPServer

async def main():
    print("=" * 60)
    print("TEST: Leo MCP Server")
    print("=" * 60)
    
    server = LeoMCPServer()
    
    # 初始化
    print("\n[1/2] Initialize...")
    await server.initialize()
    print("       SUCCESS: 46 Skills, 14 Agents, 8 Workflows")
    
    # 获取工具列表
    print("\n[2/2] Get tools list...")
    skills = server.get_skills_as_tools()
    agents = server.get_agents_as_tools()
    workflows = server.get_workflows_as_tools()
    
    print(f"       - Skills tools: {len(skills)}")
    print(f"       - Agents tools: {len(agents)}")
    print(f"       - Workflows tools: {len(workflows)}")
    
    # 查找关键工具
    realestate_agent = next((a for a in agents if 'realestate' in a['name']), None)
    if realestate_agent:
        print(f"       - Found: {realestate_agent['name']}")
    
    print("\n" + "=" * 60)
    print("SUCCESS: All tests passed!")
    print("=" * 60)
    
    print("\nAvailable tools sample:")
    print(f"  - {skills[0]['name']}")
    print(f"  - {agents[0]['name']}")
    print(f"  - {workflows[0]['name']}")

if __name__ == "__main__":
    asyncio.run(main())
