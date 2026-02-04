#!/usr/bin/env python3
"""
Leo System Quick Executor
==========================
快速执行系统能力的脚本

使用方法:
  cd D:/桌面/leo_ai_system/src
  py -3 ../scripts/quick_run.py list
  py -3 ../scripts/quick_run.py skill <skill_name> [json_params]
  py -3 ../scripts/quick_run.py agent <agent_name> <task>
  py -3 ../scripts/quick_run.py workflow <workflow_name> [json_params]
"""

import json
import sys
from pathlib import Path

# 确保从 src 目录运行
SRC_ROOT = Path(__file__).parent.parent / "src"
PROJECT_ROOT = Path(__file__).parent.parent

# 添加 src 到路径
sys.path.insert(0, str(SRC_ROOT))
sys.path.insert(0, str(PROJECT_ROOT))


def run_skill(skill_name, params_json=None):
    """执行 Skill"""
    from leo_system import get_system
    
    params = json.loads(params_json or "{}")
    print(f"[EXEC] Skill: {skill_name}")
    print(f"[INPUT] {params}")
    
    try:
        system = get_system(PROJECT_ROOT)
        result = system.call_skill(skill_name, "generate", **params)
        print("[OK] Success!")
        return result
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return None


def run_agent(agent_name, task):
    """执行 Agent"""
    from leo_orchestrator.coordinator import Orchestrator
    
    print(f"[EXEC] Agent: {agent_name}")
    print(f"[TASK] {task}")
    
    try:
        orchestrator = Orchestrator()
        result = orchestrator.dispatch(task=task, agent=agent_name)
        print("[OK] Success!")
        return result
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return None


def run_workflow(workflow_name, params_json=None):
    """执行 Workflow"""
    from leo_workflows.workflows.research_pipeline import research_pipeline
    from leo_workflows.workflows.content_pipeline import content_pipeline
    from leo_workflows.workflows.analysis_pipeline import analysis_pipeline
    from leo_workflows.workflows.realestate_pipeline import realestate_pipeline
    from leo_workflows.workflows.ecommerce_pipeline import ecommerce_pipeline
    
    params = json.loads(params_json or "{}")
    print(f"[EXEC] Workflow: {workflow_name}")
    print(f"[INPUT] {params}")
    
    workflows = {
        "research_pipeline": research_pipeline,
        "content_pipeline": content_pipeline,
        "analysis_pipeline": analysis_pipeline,
        "realestate_pipeline": realestate_pipeline,
        "ecommerce_pipeline": ecommerce_pipeline,
    }
    
    if workflow_name not in workflows:
        print(f"[ERROR] Unknown workflow: {workflow_name}")
        return None
    
    try:
        from leo_system import get_system
        system = get_system(PROJECT_ROOT)
        result = workflows[workflow_name].run(system, params)
        print("[OK] Success!")
        return result
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return None


def list_all():
    """列出所有能力"""
    print("\n[CAPABILITIES] Leo AI System")
    print("=" * 50)
    
    skills_path = SRC_ROOT / "leo_skills"
    skills_count = len(list(skills_path.glob('*/*/')))
    print(f"\n[SKILLS] {skills_count} skills")
    
    print("\n[AGENTS] (9 agents)")
    print("  - research_agent")
    print("  - analysis_agent")
    print("  - architect_agent")
    print("  - creative_agent")
    print("  - product_manager_agent")
    print("  - realestate_agent")
    print("  - mobile_agent")
    print("  - ecommerce_agent")
    print("  - ai_news_summary_agent")
    
    print("\n[WORKFLOWS] (5 workflows)")
    print("  - research_pipeline")
    print("  - content_pipeline")
    print("  - analysis_pipeline")
    print("  - realestate_pipeline")
    print("  - ecommerce_pipeline")
    
    print("\n" + "=" * 50)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "list":
        list_all()
    elif command == "skill":
        if len(sys.argv) < 3:
            print("Usage: quick_run.py skill <skill_name> [json_params]")
            sys.exit(1)
        params = sys.argv[3] if len(sys.argv) > 3 else "{}"
        run_skill(sys.argv[2], params)
    elif command == "agent":
        if len(sys.argv) < 4:
            print("Usage: quick_run.py agent <agent_name> <task>")
            sys.exit(1)
        run_agent(sys.argv[2], sys.argv[3])
    elif command == "workflow":
        if len(sys.argv) < 3:
            print("Usage: quick_run.py workflow <workflow_name> [json_params]")
            sys.exit(1)
        params = sys.argv[3] if len(sys.argv) > 3 else "{}"
        run_workflow(sys.argv[2], params)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
