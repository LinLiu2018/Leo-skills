#!/usr/bin/env python3
"""Extract Feishu Leo conversations to Markdown"""
import json
import os
from pathlib import Path

sessions_dir = os.path.expanduser("~/.openclaw/agents/leo-assistant/sessions")
output_file = "leo_feishu_conversations.md"

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
                            if text.startswith('System:'):
                                lines2 = text.split('\n')
                                text = '\n'.join([l for l in lines2 if not l.startswith('System:')])
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
        print(f"Error: {e}")

# Generate Markdown
md = """# 飞书 Leo 助手对话历史

> 自动整理自 Leo AI System - """ + str(len(conversations)) + """ 个会话

---

"""

for conv in conversations:
    md += f"## 会话 {conv['file']} - {conv['date']}\n\n"

    for role, content in conv['messages']:
        if role == 'user':
            if len(content) > 300:
                content = content[:300] + "..."
            md += f"### User\n\n{content}\n\n"
        else:
            if len(content) > 500:
                content = content[:500] + "..."
            md += f"### Leo\n\n{content}\n\n"

    md += "---\n\n"

with open(output_file, 'w', encoding='utf-8') as f:
    f.write(md)

print(f"DONE: {output_file}")
print(f"Total: {len(md)} chars")
