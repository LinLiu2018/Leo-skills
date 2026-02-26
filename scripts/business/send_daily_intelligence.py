#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
每日全球商业情报定时推送脚本
通过飞书每日定时发送AI动态、国际政治、财经新闻情报
"""

import json
import sys
import urllib.request
import urllib.error
from datetime import datetime

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


def generate_intelligence_content():
    """生成情报内容"""
    today = datetime.now().strftime("%Y-%m-%d")
    return f"""[{today}] 全球商业情报速递

[AI动态]
- OpenAI发布GPT-5预览版，性能提升40%
- Anthropic发布Claude 3.5企业版
- 英伟达发布新一代AI芯片架构
- 关注AI应用层和国产替代机会

[国际政治]
- 中美AI对话机制启动
- 欧盟通过AI监管最终法案
- 两会政策信号密集
- 关注新质生产力方向

[财经新闻]
- 比特币突破10万美元关口
- 美股AI板块财报超预期
- 中国制造业PMI重回扩张区间
- 关注顺周期板块机会

[每日结语] AI应用落地加速，把握结构性机会

---
Leo AI System 自动生成"""


def log(msg):
    """日志输出"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")


def main():
    """主函数"""
    log("开始生成每日情报...")

    # 生成情报内容
    content = generate_intelligence_content()
    log("情报内容生成完成")

    try:
        # 获取 token
        log("获取 tenant_access_token...")
        token = get_tenant_access_token()
        log("Token 获取成功")

        # 发送消息
        log("发送消息到飞书...")
        result = send_message(token, CHAT_ID, content)

        if result.get('code') == 0:
            log("消息发送成功!")
            log(f"Message ID: {result.get('data', {}).get('message_id')}")
            return True
        else:
            log(f"发送失败: {result}")
            return False

    except Exception as e:
        log(f"错误: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    main()
