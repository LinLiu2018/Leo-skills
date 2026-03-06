#!/usr/bin/env python3
"""
整理飞书 Leo 助手的对话历史为 Markdown 文档
"""
import json
import os
from datetime import datetime
from pathlib import Path

def extract_conversations(sessions_dir):
    """从所有会话文件中提取对话"""
    conversations = []

    session_files = sorted(Path(sessions_dir).glob("*.jsonl"))

    for session_file in session_files:
        if ".deleted." in session_file.name or ".reset." in session_file.name:
            continue

        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            session_time = None
            messages = []

            for line in lines:
                try:
                    data = json.loads(line.strip())
                except:
                    continue

                if data.get('type') == 'session':
                    session_time = data.get('timestamp', '')[:10]
                elif data.get('type') == 'message':
                    msg = data.get('message', {})
                    role = msg.get('role')
                    content_list = msg.get('content', [])

                    if role == 'user':
                        text = ''
                        for c in content_list:
                            if c.get('type') == 'text':
                                text = c.get('text', '')
                                # 去除 System: 前缀
                                if text.startswith('System:'):
                                    lines = text.split('\n')
                                    text = '\n'.join([l for l in lines if not l.startswith('System:')])
                                break
                        if text:
                            messages.append(('user', text))
                    elif role == 'assistant':
                        text = ''
                        for c in content_list:
                            if c.get('type') == 'text':
                                text = c.get('text', '')
                                break
                        if text:
                            messages.append(('assistant', text))

            if messages:
                conversations.append({
                    'file': session_file.name[:8],
                    'date': session_time,
                    'messages': messages
                })
        except Exception as e:
            print(f"Error processing {session_file.name}: {e}")

    return conversations

def generate_markdown(conversations):
    """生成 Markdown 文档"""
    md = """# 飞书 Leo 助手对话历史

> 自动整理自 Leo AI System

---

"""

    for conv in conversations:
        md += f"## 对话 {conv['file']} - {conv['date']}\n\n"

        for role, content in conv['messages']:
            if role == 'user':
                # 用户消息
                md += f"### 👤 用户\n\n{content}\n\n"
            else:
                # AI 回复，截取前500字符避免太长
                if len(content) > 500:
                    content = content[:500] + "..."
                md += f"### 🤖 Leo\n\n{content}\n\n"

        md += "---\n\n"

    return md

def main():
    sessions_dir = os.path.expanduser("~/.openclaw/agents/leo-assistant/sessions")
    output_file = "leo_feishu_conversations.md"

    print("正在提取对话...")
    conversations = extract_conversations(sessions_dir)
    print(f"找到 {len(conversations)} 个有效对话")

    print("正在生成 Markdown...")
    md = generate_markdown(conversations)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(md)

    print(f"DONE: {output_file}")
    print(f"Total chars: {len(md)}")

if __name__ == "__main__":
    main()
