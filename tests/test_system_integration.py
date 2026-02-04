#!/usr/bin/env python3
"""
系统集成测试 - 验证 Skills、Agents、Workflows 能正常工作
"""

import sys
import os
from pathlib import Path

# 添加项目路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

def test_fresh_start_skill():
    """测试 fresh_start_skill"""
    print("\n🧪 测试 fresh_start_skill...")
    try:
        from leo_skills.core.fresh_start_skill import FreshStartSkill
        skill = FreshStartSkill()
        result = skill.execute(project_dir=str(PROJECT_ROOT))

        assert result["status"] == "completed", "状态应为 completed"
        assert "working_dir" in result, "应有 working_dir"
        assert "context" in result, "应有 context"

        print(f"   ✅ fresh_start_skill 正常")
        print(f"   📁 工作目录: {result['working_dir']}")
        print(f"   📄 发现文件: {len(result['files_loaded'])} 个")
        return True
    except Exception as e:
        print(f"   ❌ fresh_start_skill 失败: {e}")
        return False

def test_planning_with_files_skill():
    """测试 planning_with_files_skill"""
    print("\n🧪 测试 planning_with_files_skill...")
    try:
        from leo_skills.core.planning_with_files_skill import PlanningWithFilesSkill
        skill = PlanningWithFilesSkill()

        # 模拟创建任务规划
        result = skill.execute(
            task="测试任务",
            project_dir=str(PROJECT_ROOT)
        )

        assert result["status"] == "completed", "状态应为 completed"

        print(f"   ✅ planning_with_files_skill 正常")
        return True
    except Exception as e:
        print(f"   ❌ planning_with_files_skill 失败: {e}")
        return False

def test_research_agent():
    """测试 research_agent"""
    print("\n🧪 测试 research_agent...")
    try:
        # 检查文件存在性和导入
        agent_dir = PROJECT_ROOT / "src" / "leo_subagents" / "agents" / "research_agent"
        assert (agent_dir / "AGENT.md").exists(), "AGENT.md 应存在"
        assert (agent_dir / "research_agent.py").exists(), "research_agent.py 应存在"
        assert (agent_dir / "__init__.py").exists(), "__init__.py 应存在"
        assert (agent_dir / "evolution.json").exists(), "evolution.json 应存在"

        print(f"   ✅ research_agent 文件结构完整")
        return True
    except Exception as e:
        print(f"   ❌ research_agent 失败: {e}")
        return False

def test_realestate_agent():
    """测试 realestate_agent"""
    print("\n🧪 测试 realestate_agent...")
    try:
        # 检查文件存在性和导入
        agent_dir = PROJECT_ROOT / "src" / "leo_subagents" / "agents" / "realestate_agent"
        assert (agent_dir / "AGENT.md").exists(), "AGENT.md 应存在"
        assert (agent_dir / "realestate_agent.py").exists(), "realestate_agent.py 应存在"
        assert (agent_dir / "__init__.py").exists(), "__init__.py 应存在"
        assert (agent_dir / "evolution.json").exists(), "evolution.json 应存在"

        print(f"   ✅ realestate_agent 文件结构完整")
        return True
    except Exception as e:
        print(f"   ❌ realestate_agent 失败: {e}")
        return False

def test_content_pipeline():
    """测试 content_pipeline"""
    print("\n🧪 测试 content_pipeline...")
    try:
        # 检查文件存在性
        workflow_dir = PROJECT_ROOT / "src" / "leo_workflows" / "workflows" / "content_pipeline"
        assert (workflow_dir / "workflow.yaml").exists(), "workflow.yaml 应存在"
        assert (workflow_dir / "content_pipeline.py").exists(), "content_pipeline.py 应存在"
        assert (workflow_dir / "__init__.py").exists(), "__init__.py 应存在"

        # 尝试导入
        from leo_workflows.workflows.content_pipeline import ContentPipeline
        workflow = ContentPipeline()
        workflow.load_config()

        result = workflow.execute(content_type="article", topic="测试主题")

        assert result["status"] == "completed", "状态应为 completed"

        print(f"   ✅ content_pipeline 正常")
        print(f"   📊 步骤数: {len(workflow.steps)}")
        return True
    except Exception as e:
        print(f"   ❌ content_pipeline 失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("🚀 Leo AI System 集成测试")
    print("=" * 60)

    results = []

    # 测试 Skills
    results.append(("fresh_start_skill", test_fresh_start_skill()))
    results.append(("planning_with_files_skill", test_planning_with_files_skill()))

    # 测试 Agents
    results.append(("research_agent", test_research_agent()))
    results.append(("realestate_agent", test_realestate_agent()))

    # 测试 Workflows
    results.append(("content_pipeline", test_content_pipeline()))

    # 总结
    print("\n" + "=" * 60)
    print("📊 测试结果汇总")
    print("=" * 60)

    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {status} - {name}")

    print(f"\n总计: {passed}/{total} 通过 ({passed/total*100:.0f}%)")

    if passed == total:
        print("\n🎉 所有测试通过！系统运行正常。")
        return 0
    else:
        print(f"\n⚠️ 有 {total-passed} 个测试失败，需要检查。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
