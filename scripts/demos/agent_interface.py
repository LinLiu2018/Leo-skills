#!/usr/bin/env python3
"""
Leo AI System - Agent Interface
=================================
为外部 Agent 提供统一的系统能力调用接口

使用方法:
  python scripts/agent_interface.py --skill <skill_name> --action <action> --input <json>
  python scripts/agent_interface.py --agent <agent_name> --task <task> --input <json>
  python scripts/agent_interface.py --workflow <workflow_name> --input <json>
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def load_system():
    """加载 Leo System"""
    try:
        from leo_system import get_system
        return get_system()
    except ImportError as e:
        print(f"❌ 加载系统失败: {e}")
        print("请确保项目路径正确且已安装依赖")
        sys.exit(1)


def call_skill(system, skill_name: str, action: str = None, **kwargs) -> Dict[str, Any]:
    """调用 Skill"""
    print(f"🔧 调用 Skill: {skill_name}")
    if action:
        print(f"   Action: {action}")
    
    try:
        # 尝试调用 skill
        if action:
            result = system.call_skill(skill_name, action, **kwargs)
        else:
            result = system.call_skill(skill_name, **kwargs)
        
        print(f"✅ Skill 执行成功")
        return {"success": True, "result": result}
    except Exception as e:
        print(f"❌ Skill 执行失败: {e}")
        return {"success": False, "error": str(e)}


def dispatch_agent(system, agent_name: str, task: str, **kwargs) -> Dict[str, Any]:
    """调度 Agent"""
    print(f"🤖 调度 Agent: {agent_name}")
    print(f"   Task: {task}")
    
    try:
        # 通过 orchestrator 调度
        from leo_orchestrator.coordinator import Orchestrator
        orchestrator = Orchestrator()
        
        result = orchestrator.dispatch(
            task=task,
            agent=agent_name,
            **kwargs
        )
        
        print(f"✅ Agent 执行成功")
        return {"success": True, "result": result}
    except Exception as e:
        print(f"❌ Agent 执行失败: {e}")
        return {"success": False, "error": str(e)}


def run_workflow(system, workflow_name: str, inputs: Dict = None, **kwargs) -> Dict[str, Any]:
    """运行 Workflow"""
    print(f"🌊 运行 Workflow: {workflow_name}")
    if inputs:
        print(f"   Inputs: {json.dumps(inputs, ensure_ascii=False)}")
    
    try:
        # 动态导入 workflow
        workflow_path = PROJECT_ROOT / "src" / "leo_workflows" / "workflows" / workflow_name
        
        if workflow_name == "research_pipeline":
            from leo_workflows.workflows.research_pipeline import research_pipeline
            result = research_pipeline.run(system, inputs or kwargs)
        elif workflow_name == "content_pipeline":
            from leo_workflows.workflows.content_pipeline import content_pipeline
            result = content_pipeline.run(system, inputs or kwargs)
        elif workflow_name == "analysis_pipeline":
            from leo_workflows.workflows.analysis_pipeline import analysis_pipeline
            result = analysis_pipeline.run(system, inputs or kwargs)
        elif workflow_name == "realestate_pipeline":
            from leo_workflows.workflows.realestate_pipeline import realestate_pipeline
            result = realestate_pipeline.run(system, inputs or kwargs)
        elif workflow_name == "ecommerce_pipeline":
            from leo_workflows.workflows.ecommerce_pipeline import ecommerce_pipeline
            result = ecommerce_pipeline.run(system, inputs or kwargs)
        else:
            return {"success": False, "error": f"Unknown workflow: {workflow_name}"}
        
        print(f"✅ Workflow 执行成功")
        return {"success": True, "result": result}
    except Exception as e:
        print(f"❌ Workflow 执行失败: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}


def list_capabilities():
    """列出所有可用能力"""
    print("\n📋 Leo AI System 可用能力")
    print("=" * 60)
    
    # Skills
    print("\n🧩 Skills (104个):")
    skills_path = PROJECT_ROOT / "src" / "leo_skills"
    for category in sorted(skills_path.iterdir()):
        if category.is_dir() and not category.name.startswith("_"):
            count = len([d for d in category.iterdir() if d.is_dir() and not d.name.startswith("_")])
            print(f"   {category.name}: {count}个")
    
    # Agents
    print("\n🤖 Agents (9个):")
    agents = [
        "research_agent", "analysis_agent", "architect_agent",
        "creative_agent", "product_manager_agent", "realestate_agent",
        "mobile_agent", "ecommerce_agent", "ai_news_summary_agent"
    ]
    for agent in agents:
        print(f"   - {agent}")
    
    # Workflows
    print("\n🌊 Workflows (5个):")
    workflows = [
        "research_pipeline", "content_pipeline", "analysis_pipeline",
        "realestate_pipeline", "ecommerce_pipeline"
    ]
    for wf in workflows:
        print(f"   - {wf}")
    
    print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Leo AI System - Agent Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 调用 Skill
  python agent_interface.py --skill web_search_skill --action search --input '{"query":"AI新闻"}'
  
  # 调度 Agent
  python agent_interface.py --agent research_agent --task "调研AI最新动态"
  
  # 运行 Workflow
  python agent_interface.py --workflow research_pipeline --input '{"topic":"AI动态"}'
  
  # 列出所有能力
  python agent_interface.py --list
        """
    )
    
    # 能力选择
    parser.add_argument("--list", action="store_true", help="列出所有可用能力")
    parser.add_argument("--skill", type=str, help="技能名称")
    parser.add_argument("--agent", type=str, help="代理名称")
    parser.add_argument("--workflow", type=str, help="工作流名称")
    
    # 参数
    parser.add_argument("--action", type=str, default=None, help="技能动作")
    parser.add_argument("--task", type=str, default=None, help="任务描述")
    parser.add_argument("--input", type=str, default=None, help="JSON 格式输入参数")
    parser.add_argument("--output", type=str, default="json", choices=["json", "text"], help="输出格式")
    
    args = parser.parse_args()
    
    # 解析输入
    inputs = None
    if args.input:
        try:
            inputs = json.loads(args.input)
        except json.JSONDecodeError as e:
            print(f"❌ JSON 解析失败: {e}")
            sys.exit(1)
    
    # 列出能力
    if args.list:
        list_capabilities()
        sys.exit(0)
    
    # 加载系统
    system = load_system()
    
    # 调用对应能力
    if args.skill:
        result = call_skill(system, args.skill, args.action, **(inputs or {}))
    elif args.agent:
        result = dispatch_agent(system, args.agent, args.task or "", **(inputs or {}))
    elif args.workflow:
        result = run_workflow(system, args.workflow, inputs or {})
    else:
        parser.print_help()
        sys.exit(1)
    
    # 输出结果
    if args.output == "json":
        print("\n📤 结果:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"\n📤 结果: {result}")
    
    return 0 if result.get("success") else 1


if __name__ == "__main__":
    sys.exit(main())
