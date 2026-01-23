#!/usr/bin/env python3
"""
简单示例技能 - 演示如何使用进化框架

这是一个简单的文本处理技能，用于演示进化框架的使用方法。
"""

import sys
from pathlib import Path

# 添加父目录到路径以便导入
sys.path.insert(0, str(Path(__file__).parent.parent))

from performer import EvolvableSkill


class SimpleTextProcessor(EvolvableSkill):
    """简单文本处理器 - 演示技能"""

    def __init__(self):
        # 初始化父类，传入技能名称和配置路径
        super().__init__(
            skill_name="simple-text-processor",
            config_path=str(Path(__file__).parent / "config.yaml")
        )

    def _execute_core(self, text: str = "", mode: str = "upper", **kwargs):
        """
        核心执行逻辑

        Args:
            text: 输入文本
            mode: 处理模式 (upper/lower/title)

        Returns:
            包含success, quality_score等字段的字典
        """
        if not text:
            return {
                'success': False,
                'error': '输入文本为空',
                'quality_score': 0.0
            }

        # 执行文本处理
        if mode == "upper":
            result = text.upper()
        elif mode == "lower":
            result = text.lower()
        elif mode == "title":
            result = text.title()
        else:
            return {
                'success': False,
                'error': f'未知模式: {mode}',
                'quality_score': 0.0
            }

        # 计算质量评分（示例：基于输出长度）
        quality_score = min(len(result) / 100, 1.0)  # 长度越接近100，分数越高

        return {
            'success': True,
            'result': result,
            'quality_score': quality_score,
            'output_metrics': {
                'input_length': len(text),
                'output_length': len(result),
                'mode': mode
            }
        }


def demo():
    """演示进化框架的使用"""
    print("=" * 60)
    print("技能进化框架 - 简单示例")
    print("=" * 60)

    # 创建技能实例
    skill = SimpleTextProcessor()

    # 模拟多次执行（收集数据）
    test_cases = [
        ("hello world", "upper"),
        ("HELLO WORLD", "lower"),
        ("hello world", "title"),
        ("this is a test", "upper"),
        ("ANOTHER TEST", "lower"),
        ("test case", "title"),
        ("", "upper"),  # 失败案例
        ("short", "upper"),
        ("this is a longer text for better quality score", "upper"),
        ("final test", "title"),
    ]

    print("\n执行测试案例...")
    for i, (text, mode) in enumerate(test_cases, 1):
        print(f"\n[{i}/{len(test_cases)}] 处理: '{text[:30]}...' (mode={mode})")
        result = skill.execute(text=text, mode=mode)

        if result.success:
            print(f"  ✓ 成功: {result.data.get('result', '')[:50]}")
            print(f"  质量评分: {result.data.get('quality_score', 0):.2f}")
        else:
            print(f"  ✗ 失败: {result.error}")

    # 查看进化状态
    print("\n" + "=" * 60)
    print("进化状态")
    print("=" * 60)
    status = skill.get_evolution_status()
    print(f"进化能力: {'已启用' if status['enabled'] else '已禁用'}")
    print(f"总执行次数: {status['total_executions']}")
    print(f"最佳实践数: {status['best_practices_count']}")
    print(f"优化规则数: {status['optimization_rules_count']}")
    print(f"配置快照数: {status['snapshots_count']}")

    # 手动触发学习
    if status['total_executions'] >= 5:
        print("\n" + "=" * 60)
        print("手动触发学习流程")
        print("=" * 60)
        learn_result = skill.trigger_manual_learning()
        if learn_result['success']:
            print(f"✓ 学习完成，分析了 {learn_result['analyzed_count']} 条记录")
        else:
            print(f"✗ 学习失败: {learn_result.get('reason')}")

    print("\n" + "=" * 60)
    print("演示完成！")
    print("=" * 60)
    print("\n数据已保存到: leo-skills/.evolution_data/simple-text-processor/")
    print("  - execution_history.jsonl  # 执行历史")
    print("  - best_practices.json      # 最佳实践")
    print("  - optimization_rules.json  # 优化规则")


if __name__ == "__main__":
    demo()
