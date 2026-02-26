#!/usr/bin/env python3
"""
Leo System Direct Executor - 绕过复杂的依赖问题，直接调用系统能力
=====================================================================
"""

import sys
import json
from pathlib import Path

# 添加路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))


def list_skills():
    """列出所有注册的 Skills"""
    from leo_orchestrator.registry import get_registry
    registry = get_registry()
    skills = registry.list_skills()
    
    print("\n[REGISTERED SKILLS]")
    print("=" * 50)
    for skill in skills:
        print(f"  - {skill.name} ({skill.category})")
    print("=" * 50)
    print(f"Total: {len(skills)} skills\n")


def list_agents():
    """列出所有注册的 Agents"""
    from leo_orchestrator.registry import get_registry
    registry = get_registry()
    agents = registry.list_agents()
    
    print("\n[REGISTERED AGENTS]")
    print("=" * 50)
    for agent in agents:
        print(f"  - {agent.name} ({agent.type}) - Priority: {agent.priority}")
    print("=" * 50)
    print(f"Total: {len(agents)} agents\n")


def list_workflows():
    """列出所有注册的 Workflows"""
    from leo_orchestrator.registry import get_registry
    registry = get_registry()
    workflows = registry.list_workflows()
    
    print("\n[REGISTERED WORKFLOWS]")
    print("=" * 50)
    for wf in workflows:
        print(f"  - {wf}")
    print("=" * 50)
    print(f"Total: {len(workflows)} workflows\n")


def call_api_skill(skill_name, action=None, **kwargs):
    """通过 LeoAPI 调用 Skill"""
    from leo_orchestrator.api import LeoAPI
    
    api = LeoAPI()
    print(f"\n[CALLING SKILL] {skill_name}")
    
    if action:
        result = api.call(skill_name, action, **kwargs)
    else:
        # 尝试默认 action
        result = api.call(skill_name, "execute", **kwargs)
    
    return result


def run_agent(agent_name, task):
    """通过 LeoAPI 运行 Agent"""
    from leo_orchestrator.api import LeoAPI
    
    api = LeoAPI()
    print(f"\n[RUNNING AGENT] {agent_name}")
    print(f"[TASK] {task}")
    
    result = api.run_agent(agent_name, task)
    return result


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("\n[USAGE]")
        print("  python direct_executor.py list")
        print("  python direct_executor.py list_skills")
        print("  python direct_executor.py list_agents")
        print("  python direct_executor.py list_workflows")
        print("  python direct_executor.py api_skill <skill_name> [action] [json_params]")
        print("  python direct_executor.py run_agent <agent_name> <task>")
        sys.exit(0)
    
    command = sys.argv[1]
    
    if command == "list":
        list_skills()
        list_agents()
        list_workflows()
    elif command == "list_skills":
        list_skills()
    elif command == "list_agents":
        list_agents()
    elif command == "list_workflows":
        list_workflows()
    elif command == "api_skill":
        skill_name = sys.argv[2] if len(sys.argv) > 2 else None
        action = sys.argv[3] if len(sys.argv) > 3 else None
        params = {}
        if len(sys.argv) > 4:
            try:
                params = json.loads(sys.argv[4])
            except:
                pass
        
        if not skill_name:
            print("[ERROR] Please specify skill name")
            sys.exit(1)
        
        result = call_api_skill(skill_name, action, **params)
        print(f"\n[RESULT] {result}")
    elif command == "run_agent":
        agent_name = sys.argv[2] if len(sys.argv) > 2 else None
        task = sys.argv[3] if len(sys.argv) > 3 else ""
        
        if not agent_name:
            print("[ERROR] Please specify agent name")
            sys.exit(1)
        
        result = run_agent(agent_name, task)
        print(f"\n[RESULT] {result}")
    else:
        print(f"[ERROR] Unknown command: {command}")


if __name__ == "__main__":
    main()
