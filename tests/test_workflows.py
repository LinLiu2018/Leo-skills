"""
Workflow测试脚本
================
测试3个预定义工作流的执行
"""

import sys
from pathlib import Path

# 添加路径
current_path = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_path))

# 使用importlib直接加载模块
import importlib.util

def load_module_from_file(module_name: str, file_path: str):
    """从文件直接加载模块"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

# 加载leo-system模块
leo_system_module = load_module_from_file("leo_system", str(current_path / "leo-system.py"))
LeoSystem = leo_system_module.LeoSystem


def test_workflow(system: LeoSystem, workflow_name: str, **kwargs):
    """
    测试单个工作流

    Args:
        system: Leo系统实例
        workflow_name: 工作流名称
        **kwargs: 工作流参数
    """
    print("\n" + "="*80)
    print(f"🧪 测试工作流: {workflow_name}")
    print("="*80)

    try:
        result = system.run_workflow(workflow_name, **kwargs)

        if result and result.get('success'):
            print(f"\n✅ 工作流测试成功")
            print(f"   成功步骤: {result['successful_steps']}/{result['total_steps']}")
        else:
            print(f"\n⚠️  工作流测试完成（有失败步骤）")
            if result:
                print(f"   成功步骤: {result['successful_steps']}/{result['total_steps']}")
                print(f"   失败步骤: {result['failed_steps']}")

        return result

    except Exception as e:
        print(f"\n❌ 工作流测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """主测试函数"""
    print("\n" + "="*80)
    print("🚀 Leo AI Agent System - Workflow测试")
    print("="*80)

    # 初始化系统
    print("\n📦 初始化系统...")
    system = LeoSystem()

    print("\n✅ 系统初始化完成")
    print(f"   Agents: {len(system.agents)} 个")
    print(f"   Skills: {len(system.skill_loader.skills)} 个")

    # 测试1: content-pipeline (内容生产线)
    print("\n" + "="*80)
    print("测试 1/3: content-pipeline (内容生产线)")
    print("="*80)

    result1 = test_workflow(
        system,
        "content-pipeline",
        task="生成2026年宁波房地产市场趋势分析文章",
        topic="宁波房地产市场",
        year=2026
    )

    # 测试2: research-pipeline (研究线)
    print("\n" + "="*80)
    print("测试 2/3: research-pipeline (研究线)")
    print("="*80)

    result2 = test_workflow(
        system,
        "research-pipeline",
        task="调研智慧农贸市场竞品分析",
        topic="智慧农贸市场",
        focus="竞品分析"
    )

    # 测试3: analysis-pipeline (分析线)
    print("\n" + "="*80)
    print("测试 3/3: analysis-pipeline (分析线)")
    print("="*80)

    result3 = test_workflow(
        system,
        "analysis-pipeline",
        task="分析月度销售数据",
        data=[100, 120, 110, 130, 150, 140],
        title="2026年1月销售分析报告"
    )

    # 汇总测试结果
    print("\n" + "="*80)
    print("📊 测试结果汇总")
    print("="*80)

    results = [
        ("content-pipeline", result1),
        ("research-pipeline", result2),
        ("analysis-pipeline", result3)
    ]

    total_tests = len(results)
    successful_tests = sum(1 for _, r in results if r and r.get('success'))

    print(f"\n总测试数: {total_tests}")
    print(f"成功: {successful_tests}")
    print(f"失败: {total_tests - successful_tests}")

    print("\n详细结果:")
    for workflow_name, result in results:
        if result and result.get('success'):
            status = "✅ 成功"
        elif result:
            status = "⚠️  部分成功"
        else:
            status = "❌ 失败"

        print(f"  {status} - {workflow_name}")

    # 最终状态
    print("\n" + "="*80)
    if successful_tests == total_tests:
        print("🎉 所有工作流测试通过！")
    else:
        print(f"⚠️  {total_tests - successful_tests} 个工作流测试失败")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
