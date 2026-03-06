#!/usr/bin/env python3
"""
每日交互日志总结脚本
====================
每天定时汇总过去24小时的交互日志，生成统计报告

功能：
1. 汇总技能调用统计
2. 统计代理使用排行
3. 记录任务完成情况
4. 输出交互摘要

使用方法：
    python scripts/maintenance/daily_interaction_summary.py
    python scripts/maintenance/daily_interaction_summary.py --hours 24
"""

import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path

# 项目根目录 (scripts/maintenance 的父目录的父目录)
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

# 日志目录
INTERACTION_LOGS_DIR = PROJECT_ROOT / "src" / "logs" / "interactions"
GROWTH_LOG_DIR = PROJECT_ROOT / "docs" / "growth_logs"


def load_interaction_logs(hours: int = 24) -> list:
    """加载过去N小时的交互日志"""
    cutoff_time = datetime.now() - timedelta(hours=hours)
    all_logs = []

    if not INTERACTION_LOGS_DIR.exists():
        print(f"  - 日志目录不存在: {INTERACTION_LOGS_DIR}")
        return all_logs

    # 读取所有JSON日志文件
    for log_file in INTERACTION_LOGS_DIR.glob("*.json"):
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logs = data.get('logs', [])

                # 过滤时间范围内的日志
                for log in logs:
                    log_time = datetime.fromisoformat(log['timestamp'])
                    if log_time >= cutoff_time:
                        all_logs.append(log)
        except (json.JSONDecodeError, KeyError) as e:
            print(f"  - 警告: 读取日志文件失败 {log_file.name}: {e}")

    # 按时间排序
    all_logs.sort(key=lambda x: x['timestamp'])
    return all_logs


def analyze_skill_calls(logs: list) -> dict:
    """分析技能调用统计"""
    skill_calls = [l for l in logs if l['log_type'] == 'skill_call']

    skill_counter = Counter()
    skill_success = defaultdict(lambda: {'success': 0, 'failed': 0})
    skill_times = defaultdict(list)

    for log in skill_calls:
        skill_name = log['content'].get('skill_name', 'unknown')
        skill_counter[skill_name] += 1

        if log['content'].get('success'):
            skill_success[skill_name]['success'] += 1
        else:
            skill_success[skill_name]['failed'] += 1

        exec_time = log['content'].get('execution_time', 0)
        if exec_time > 0:
            skill_times[skill_name].append(exec_time)

    # 计算平均执行时间
    avg_times = {}
    for skill, times in skill_times.items():
        avg_times[skill] = sum(times) / len(times) if times else 0

    return {
        'total_calls': len(skill_calls),
        'top_skills': skill_counter.most_common(10),
        'success_rate': skill_success,
        'avg_execution_time': avg_times,
    }


def analyze_agent_usage(logs: list) -> dict:
    """分析代理使用情况"""
    agent_selects = [l for l in logs if l['log_type'] == 'agent_select']
    agent_executes = [l for l in logs if l['log_type'] == 'agent_execute']

    # 代理选择统计
    agent_counter = Counter()
    for log in agent_selects:
        agent = log['content'].get('selected_agent', 'unknown')
        agent_counter[agent] += 1

    # 代理执行统计
    exec_counter = Counter()
    exec_success = defaultdict(lambda: {'success': 0, 'failed': 0})
    for log in agent_executes:
        agent = log['content'].get('agent_name', 'unknown')
        exec_counter[agent] += 1

        if log['content'].get('success'):
            exec_success[agent]['success'] += 1
        else:
            exec_success[agent]['failed'] += 1

    return {
        'total_selects': len(agent_selects),
        'total_executes': len(agent_executes),
        'top_agents': agent_counter.most_common(10),
        'execution_stats': dict(exec_success),
    }


def analyze_workflows(logs: list) -> dict:
    """分析工作流执行情况"""
    workflow_starts = [l for l in logs if l['log_type'] == 'workflow_start']
    workflow_ends = [l for l in logs if l['log_type'] == 'workflow_end']

    workflows = {}
    for log in workflow_starts:
        wf_id = log['content'].get('workflow_id')
        workflows[wf_id] = {
            'name': log['content'].get('workflow_name', 'unknown'),
            'start_time': log['timestamp'],
            'steps': log['content'].get('total_steps', 0),
            'completed': 0,
            'success': None,
        }

    for log in workflow_ends:
        wf_id = log['content'].get('workflow_id')
        if wf_id in workflows:
            workflows[wf_id]['completed'] = log['content'].get('completed_steps', 0)
            workflows[wf_id]['success'] = log['content'].get('success', False)
            workflows[wf_id]['total_time'] = log['content'].get('total_time', 0)
            workflows[wf_id]['end_time'] = log['timestamp']

    success_count = sum(1 for w in workflows.values() if w.get('success') is True)
    failed_count = sum(1 for w in workflows.values() if w.get('success') is False)

    return {
        'total_workflows': len(workflow_starts),
        'completed': success_count,
        'failed': failed_count,
        'workflow_details': list(workflows.values())[:10],
    }


def analyze_user_interactions(logs: list) -> dict:
    """分析用户交互情况"""
    user_inputs = [l for l in logs if l['log_type'] == 'user_input']
    system_responses = [l for l in logs if l['log_type'] == 'system_response']
    errors = [l for l in logs if l['log_type'] == 'error']

    # 统计会话
    sessions = set()
    for log in logs:
        if log.get('session_id'):
            sessions.add(log['session_id'])

    # 统计输入长度
    input_lengths = [l['content'].get('input_length', 0) for l in user_inputs]
    avg_input_length = sum(input_lengths) / len(input_lengths) if input_lengths else 0

    return {
        'total_sessions': len(sessions),
        'user_inputs': len(user_inputs),
        'system_responses': len(system_responses),
        'errors': len(errors),
        'avg_input_length': round(avg_input_length, 1),
    }


def generate_summary_markdown(
    hours: int,
    skill_stats: dict,
    agent_stats: dict,
    workflow_stats: dict,
    user_stats: dict,
) -> str:
    """生成Markdown格式的总结报告"""
    today = datetime.now().strftime('%Y-%m-%d')

    content = f"""# 每日交互日志总结 - {today}

> 自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
> 统计周期: 过去 {hours} 小时

---

## 整体概览

| 指标 | 数值 |
|------|------|
| 会话数 | {user_stats['total_sessions']} |
| 用户输入 | {user_stats['user_inputs']} 次 |
| 系统响应 | {user_stats['system_responses']} 次 |
| 错误数 | {user_stats['errors']} |
| 平均输入长度 | {user_stats['avg_input_length']} 字符 |

---

## 技能调用统计

**总调用次数**: {skill_stats['total_calls']}

| 技能名称 | 调用次数 | 成功率 | 平均耗时 |
|----------|----------|--------|----------|
"""

    for skill, count in skill_stats['top_skills']:
        success_data = skill_stats['success_rate'].get(skill, {'success': 0, 'failed': 0})
        total = success_data['success'] + success_data['failed']
        success_rate = (success_data['success'] / total * 100) if total > 0 else 0
        avg_time = skill_stats['avg_execution_time'].get(skill, 0)
        content += f"| {skill} | {count} | {success_rate:.1f}% | {avg_time:.2f}s |\n"

    content += f"""
---

## 代理使用排行

**总选择次数**: {agent_stats['total_selects']} | **总执行次数**: {agent_stats['total_executes']}

| 代理名称 | 选择次数 | 执行次数 |
|----------|----------|----------|
"""

    for agent, count in agent_stats['top_agents']:
        exec_count = agent_stats['execution_stats'].get(agent, {}).get('success', 0) + \
                     agent_stats['execution_stats'].get(agent, {}).get('failed', 0)
        content += f"| {agent} | {count} | {exec_count} |\n"

    content += f"""
---

## 工作流执行情况

**总工作流数**: {workflow_stats['total_workflows']} | **成功**: {workflow_stats['completed']} | **失败**: {workflow_stats['failed']}

| 工作流名称 | 步骤数 | 完成步骤 | 状态 | 耗时 |
|------------|--------|----------|------|------|
"""

    for wf in workflow_stats['workflow_details']:
        status = "✅ 成功" if wf.get('success') else "❌ 失败" if wf.get('success') is False else "进行中"
        total_time = wf.get('total_time', 0)
        content += f"| {wf['name']} | {wf['steps']} | {wf['completed']} | {status} | {total_time:.2f}s |\n"

    if not workflow_stats['workflow_details']:
        content += "| (本周期无工作流执行) | - | - | - | - |\n"

    content += f"""
---

## 错误统计

"""

    error_logs = [l for l in [] if l.get('log_type') == 'error']  # 这里需要从原始logs获取
    if error_logs:
        for err in error_logs[:10]:
            err_type = err['content'].get('error_type', 'unknown')
            err_msg = err['content'].get('error_message', '')[:60]
            content += f"- **{err_type}**: {err_msg}\n"
    else:
        content += "- (本周期无错误记录)\n"

    content += f"""
---

*此报告由 daily_interaction_summary.py 自动生成*
"""

    return content


def save_summary(content: str, hours: int) -> str:
    """保存总结报告"""
    GROWTH_LOG_DIR.mkdir(parents=True, exist_ok=True)

    today = datetime.now().strftime('%Y-%m-%d')
    summary_file = GROWTH_LOG_DIR / f"interaction_summary_{today}.md"

    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(content)

    return str(summary_file)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='每日交互日志总结')
    parser.add_argument('--hours', type=int, default=24, help='统计过去N小时 (默认24)')
    args = parser.parse_args()

    print(f"[{datetime.now()}] 开始生成每日交互日志总结...")

    # 1. 加载日志
    print(f"  - 加载过去 {args.hours} 小时的交互日志...")
    logs = load_interaction_logs(args.hours)
    print(f"  - 共加载 {len(logs)} 条日志记录")

    # 2. 统计分析
    print("  - 分析技能调用...")
    skill_stats = analyze_skill_calls(logs)

    print("  - 分析代理使用...")
    agent_stats = analyze_agent_usage(logs)

    print("  - 分析工作流执行...")
    workflow_stats = analyze_workflows(logs)

    print("  - 分析用户交互...")
    user_stats = analyze_user_interactions(logs)

    # 3. 生成报告
    print("  - 生成总结报告...")
    summary_md = generate_summary_markdown(
        args.hours,
        skill_stats,
        agent_stats,
        workflow_stats,
        user_stats,
    )

    # 4. 保存报告
    summary_file = save_summary(summary_md, args.hours)
    print(f"  - 报告已保存: {summary_file}")

    # 5. 输出关键指标
    print(f"\n[{datetime.now()}] 总结完成!")
    print(f"  - 技能调用: {skill_stats['total_calls']} 次")
    print(f"  - 代理执行: {agent_stats['total_executes']} 次")
    print(f"  - 工作流: {workflow_stats['completed']}/{workflow_stats['total_workflows']} 成功")
    print(f"  - 用户输入: {user_stats['user_inputs']} 次")

    return {
        'logs_analyzed': len(logs),
        'skill_calls': skill_stats['total_calls'],
        'agent_executes': agent_stats['total_executes'],
        'workflows': workflow_stats['total_workflows'],
        'summary_file': summary_file,
    }


if __name__ == "__main__":
    main()
