#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Leo Agent 命令行调用工具
直接调用 Leo 的 Agents 执行任务
"""

import sys
import os
import json
import argparse

# 添加 Leo System 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
os.environ['PYTHONIOENCODING'] = 'utf-8'

def main():
    parser = argparse.ArgumentParser(description='Leo Agent CLI')
    parser.add_argument('agent', choices=['realestate', 'research', 'creative', 'analysis'], help='Agent name')
    parser.add_argument('task', help='Task description')
    parser.add_argument('--format', default='text', choices=['text', 'json'], help='Output format')
    
    args = parser.parse_args()
    
    # 加载注册表
    from leo_orchestrator.registry import get_registry
    registry = get_registry()
    
    # 根据 agent 名称找到对应的 Agent
    agent_map = {
        'realestate': 'realestate_agent',
        'research': 'research_agent', 
        'creative': 'creative_agent',
        'analysis': 'analysis_agent'
    }
    
    agent_name = agent_map[args.agent]
    
    print("=" * 60)
    print(f"Executing: {agent_name}")
    print(f"Task: {args.task}")
    print("=" * 60)
    
    # 获取 Agent 信息
    agent = registry.get_agent(agent_name)
    if not agent:
        print(f"[ERROR] Agent not found: {agent_name}")
        print(f"Available agents: {list(registry.agents.keys())}")
        sys.exit(1)
    
    # 模拟执行（实际会调用 Agent 的处理逻辑）
    result = {
        "status": "success",
        "agent": agent_name,
        "agent_type": getattr(agent, 'type', 'unknown'),
        "priority": getattr(agent, 'priority', 0),
        "task": args.task,
        "message": f"[Leo System] {agent_name} received task: {args.task}",
        "note": "这是简化的 CLI 调用，实际执行需要完善 Agent 的调用逻辑"
    }
    
    if args.format == 'json':
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"\n[OK] Agent: {agent_name}")
        print(f"[OK] Type: {result['agent_type']}")
        print(f"[OK] Priority: {result['priority']}")
        print(f"\nTask: {args.task}")
        print(f"\nNote: {result['note']}")
        print("\n" + "=" * 60)
        print("实际执行需要完善 Agent 的调用逻辑")
        print("=" * 60)

if __name__ == "__main__":
    main()
