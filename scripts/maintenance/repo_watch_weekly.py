#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
仓库监控周报生成脚本
每周一早上9点执行，生成报告并发送到飞书
"""

import sys
import os
import json
from datetime import datetime

# 添加项目路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(project_root, 'src'))

def main():
    """主函数"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始生成仓库周报...")

    try:
        from leo_skills.tools.repo_watch_skill import RepoWatchSkill

        # 创建技能实例
        skill = RepoWatchSkill()

        # 生成报告
        result = skill.execute('generate_report')

        if result.get('status') == 'error':
            print(f"[ERROR] 报告生成失败: {result.get('message')}")
            return 1

        report_file = result.get('report_file')
        print(f"[OK] 报告已生成: {report_file}")

        # 读取报告内容
        if report_file and os.path.exists(report_file):
            with open(report_file, 'r', encoding='utf-8') as f:
                report_content = f.read()

            # 发送到飞书
            send_to_feishu(report_content)

        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 周报任务完成")
        return 0

    except Exception as e:
        print(f"[ERROR] 执行失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


def send_to_feishu(content):
    """发送报告到飞书"""
    import urllib.request
    import urllib.error

    # 飞书 Webhook URL (从配置读取)
    config_path = os.path.join(project_root, 'src', 'leo_config', 'settings', 'config.yaml')
    webhook_url = None

    try:
        import yaml
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            webhook_url = config.get('feishu', {}).get('webhook_url')
    except Exception as e:
        print(f"[WARN] 无法读取飞书配置: {e}")

    if not webhook_url:
        # 尝试从环境变量获取
        webhook_url = os.environ.get('FEISHU_WEBHOOK_URL')

    if not webhook_url:
        print("[WARN] 未配置飞书 Webhook，跳过发送")
        print("=" * 50)
        print(content)
        print("=" * 50)
        return

    # 构建飞书消息
    message = {
        "msg_type": "text",
        "content": {
            "text": f"[Leo AI] 核心仓库周报\n\n{content}"
        }
    }

    try:
        data = json.dumps(message).encode('utf-8')
        req = urllib.request.Request(
            webhook_url,
            data=data,
            headers={'Content-Type': 'application/json'}
        )

        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            if result.get('code') == 0:
                print("[OK] 报告已发送到飞书")
            else:
                print(f"[WARN] 飞书发送返回: {result}")

    except urllib.error.URLError as e:
        print(f"[ERROR] 飞书发送失败: {e}")
    except Exception as e:
        print(f"[ERROR] 飞书发送异常: {e}")


if __name__ == '__main__':
    sys.exit(main())
