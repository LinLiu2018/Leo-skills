#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Leo Direct - 直接调用 Leo 系统能力
无需 MCP，直接通过 Python 执行
"""

import sys
import os
import json
from datetime import datetime

# 添加 Leo 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
os.environ['PYTHONIOENCODING'] = 'utf-8'

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def get_leo_capabilities():
    """获取 Leo 系统能力"""
    try:
        from leo_orchestrator.registry import get_registry
        registry = get_registry()
        
        skills = list(registry.skills.keys()) if hasattr(registry.skills, 'keys') else registry.skills
        agents = list(registry.agents.keys()) if hasattr(registry.agents, 'keys') else registry.agents
        workflows = registry.workflows or []
        
        return {
            "skills": skills,
            "agents": agents, 
            "workflows": workflows
        }
    except Exception as e:
        return {"error": str(e)}


def execute_research(query: str):
    """执行研究任务"""
    caps = get_leo_capabilities()
    
    result = {
        "task": "research",
        "query": query,
        "timestamp": datetime.now().isoformat(),
        "capabilities": caps,
        "note": "由于缺少 API Key，无法访问网络数据",
        "data_sources": [
            "宁波市统计局 tjj.ningbo.gov.cn",
            "宁波住建局 nbjs.ningbo.gov.cn",
            "透明售房网 www.nbfcjs.com"
        ],
        "recommendation": "请从上述官方数据源获取最新数据后，我可以帮你分析"
    }
    
    return result


def generate_report(topic: str, data: str = None):
    """生成报告"""
    result = {
        "task": "report_generation",
        "topic": topic,
        "timestamp": datetime.now().isoformat(),
        "content": f"# {topic}\n\n## 报告生成时间\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n## 概述\n\n{data or '等待数据输入...'}\n\n## 数据来源\n\n请从官方数据源获取最新数据。",
        "note": "使用 --data 参数提供数据可以生成更详细的报告"
    }
    
    return result


def main():
    if len(sys.argv) < 2:
        print("Leo Direct - 直接调用 Leo 系统")
        print()
        print("Usage:")
        print("  python leo_direct.py capabilities    # 查看所有能力")
        print("  python leo_direct.py research <query>  # 执行研究")
        print("  python leo_direct.py report <topic>    # 生成报告")
        print()
        print("Examples:")
        print("  python leo_direct.py research 宁波房产市场")
        print("  python leo_direct.py report 宁波商业租赁分析")
        sys.exit(0)
    
    command = sys.argv[1]
    
    if command == "capabilities":
        caps = get_leo_capabilities()
        print("\n[Leo System Capabilities]")
        print("=" * 60)
        print(f"Skills: {len(caps.get('skills', []))}")
        print(f"Agents: {len(caps.get('agents', []))}")
        print(f"Workflows: {len(caps.get('workflows', []))}")
        print()
        print("Available Skills:")
        for s in caps.get('skills', [])[:10]:
            print(f"  - {s}")
        print()
        print("Available Agents:")
        for a in caps.get('agents', []):
            print(f"  - {a}")
    
    elif command == "research":
        query = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "请提供研究主题"
        result = execute_research(query)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif command == "report":
        topic = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "未指定主题"
        result = generate_report(topic)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    else:
        print(f"Unknown command: {command}")
        print("Use: capabilities, research, report")
        sys.exit(1)


if __name__ == "__main__":
    main()
