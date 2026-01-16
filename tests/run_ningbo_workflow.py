import sys
import importlib.util
from pathlib import Path

# 加载leo-system模块
leo_system_path = Path(__file__).parent / 'leo-system.py'
spec = importlib.util.spec_from_file_location('leo_system', leo_system_path)
leo_system = importlib.util.module_from_spec(spec)
spec.loader.exec_module(leo_system)

system = leo_system.get_system()
result = system.run_workflow(
    'content-pipeline',
    task='生成宁波房地产市场分析文章',
    topic='宁波房地产市场'
)

print('\n' + '='*60)
print('📄 生成的内容详情')
print('='*60)

if result and result.get('success'):
    # 打印各步骤的详细结果
    for step in result.get('results', []):
        print(f"\n【{step['step']}】- {step['agent']}")
        if 'result' in step:
            step_result = step['result']
            # 使用serialize_result处理
            serialized = leo_system.serialize_result(step_result)
            import json
            print(json.dumps(serialized, indent=2, ensure_ascii=False))

    # 打印最终上下文
    print('\n' + '='*60)
    print('📊 最终输出')
    print('='*60)
    context = result.get('context', {})
    serialized_context = leo_system.serialize_result(context)
    import json
    print(json.dumps(serialized_context, indent=2, ensure_ascii=False))

print('\n执行完成！')
