#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
直接通过飞书 API 发送消息
"""

import json
import urllib.request
import urllib.error

# 飞书配置
APP_ID = "cli_a9f18849edbb9cb1"
APP_SECRET = "UUNNVCiRRheoPkdnKPeVycYTTlVQ8emS"
CHAT_ID = "oc_dad825f21752952c4004b2b669568d08"

def get_tenant_access_token():
    """获取 tenant_access_token"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    data = json.dumps({
        "app_id": APP_ID,
        "app_secret": APP_SECRET
    }).encode('utf-8')

    req = urllib.request.Request(url, data=data, headers={
        'Content-Type': 'application/json'
    })

    with urllib.request.urlopen(req, timeout=30) as response:
        result = json.loads(response.read().decode('utf-8'))
        if result.get('code') == 0:
            return result.get('tenant_access_token')
        else:
            raise Exception(f"获取 token 失败: {result}")

def send_message(token, chat_id, content):
    """发送消息到飞书"""
    url = "https://open.feishu.cn/open-apis/im/v1/messages"

    data = json.dumps({
        "receive_id": chat_id,
        "msg_type": "text",
        "content": json.dumps({"text": content})
    }).encode('utf-8')

    req = urllib.request.Request(
        f"{url}?receive_id_type=chat_id",
        data=data,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }
    )

    with urllib.request.urlopen(req, timeout=30) as response:
        result = json.loads(response.read().decode('utf-8'))
        return result

def main():
    # 周报内容
    report = """[Leo AI] 核心仓库周报 (2026-02-02)

Claude Code (anthropics/claude-code)
- 最新版本: v2.1.29 (2026-01-31)
- 本周提交: 10个
- 建议: 有新版本，建议检查更新

OpenClaw (openclaw/openclaw)
- 最新版本: v2026.1.30 (2026-01-31)
- 本周提交: 10个
- 建议: 有新版本，建议检查更新

详细报告已保存至: logs/repo_watch/report_2026-02-02.md"""

    try:
        print("获取 tenant_access_token...")
        token = get_tenant_access_token()
        print(f"Token 获取成功")

        print(f"发送消息到 {CHAT_ID}...")
        result = send_message(token, CHAT_ID, report)

        if result.get('code') == 0:
            print("消息发送成功!")
            print(f"Message ID: {result.get('data', {}).get('message_id')}")
        else:
            print(f"发送失败: {result}")

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
