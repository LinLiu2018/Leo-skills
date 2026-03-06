#!/usr/bin/env python3
"""详细提取飞书 Leo 助手的配置信息"""
import json
import os
import re
from pathlib import Path
from collections import defaultdict

sessions_dir = os.path.expanduser("~/.openclaw/agents/leo-assistant/sessions")
output_file = "leo_system_config_summary.md"

# 存储提取的信息
info = {
    'cron_tasks': [],
    'agents': [],
    'skills': [],
    'ai_personalities': [],
    'user_preferences': [],
    'openclaw_settings': [],
    'user_memories': []
}

session_files = sorted(Path(sessions_dir).glob("*.jsonl"))

for session_file in session_files:
    # 包含所有文件，包括 deleted 和 reset
    pass  # 处理所有文件

    try:
        with open(session_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for line in lines:
            try:
                data = json.loads(line.strip())
            except:
                continue

            if data.get('type') == 'message':
                msg = data.get('message', {})
                role = msg.get('role')
                content_list = msg.get('content', [])

                if role == 'user':
                    text = ''
                    for c in content_list:
                        if c.get('type') == 'text':
                            text = c.get('text', '')
                            break

                    # 提取 cron 任务
                    if '[cron:' in text or 'cron:' in text.lower():
                        cron_match = re.search(r'\[?cron:([^\]]+)\]?', text)
                        if cron_match:
                            task_name = cron_match.group(1).strip()
                            if task_name not in [t['name'] for t in info['cron_tasks']]:
                                info['cron_tasks'].append({'name': task_name, 'session': session_file.name[:8]})

                    # 提取技能名称
                    skill_patterns = [
                        r'技能[：:]\s*([^\n，。,\.]+)',
                        r'skill[：:]\s*([^\n，。,\.]+)',
                        r'调用\s*([^\s]+)\s*技能',
                        r'执行\s*([^\s]+)\s*任务'
                    ]
                    for pattern in skill_patterns:
                        matches = re.findall(pattern, text, re.IGNORECASE)
                        for m in matches:
                            if m.strip() and len(m.strip()) < 50:
                                if m.strip() not in info['skills']:
                                    info['skills'].append(m.strip())

                elif role == 'assistant':
                    text = ''
                    for c in content_list:
                        if c.get('type') == 'text':
                            text = c.get('text', '')
                            break

                    # 提取 AI 人格设定
                    if any(k in text for k in ['人格', '性格', '角色设定', 'prompt', 'system prompt', '你是谁']):
                        if len(text) < 500:
                            info['ai_personalities'].append(text[:300])

                    # 提取用户偏好
                    if any(k in text for k in ['偏好', '喜欢', '不喜欢', '用户要求', '用户设定']):
                        if len(text) < 500:
                            info['user_preferences'].append(text[:300])

                    # 提取 OpenClaw 设置
                    if any(k in text for k in ['openclaw', '配置', 'config', 'setting']):
                        if len(text) < 500:
                            info['openclaw_settings'].append(text[:300])

    except Exception as e:
        print(f"Error: {e}")

# 去重
info['skills'] = list(set(info['skills']))[:30]  # 限制30个

# 生成 Markdown
md = """# Leo AI System 配置总览

> 从飞书对话历史中自动提取

---

## 1. 定时任务 (Cron Jobs)

| 任务名称 | 来源会话 |
|---------|---------|
"""

for t in info['cron_tasks']:
    md += f"| {t['name']} | {t['session']} |\n"

md += """
---

## 2. 技能 (Skills)

```
"""

for s in info['skills']:
    md += f"- {s}\n"

md += """```

---

## 3. AI 人格设定

"""

for p in info['ai_personalities'][:5]:
    md += f"> {p}\n\n"

md += """
---

## 4. 用户偏好

"""

for p in info['user_preferences'][:5]:
    md += f"> {p}\n\n"

md += """
---

## 5. OpenClaw 配置

"""

for s in info['openclaw_settings'][:5]:
    md += f"> {s}\n\n"

md += f"""
---

## 统计信息

- 定时任务: {len(info['cron_tasks'])} 个
- 技能: {len(info['skills'])} 个
- AI人格设定: {len(info['ai_personalities'])} 条
- 用户偏好: {len(info['user_preferences'])} 条
- OpenClaw配置: {len(info['openclaw_settings'])} 条
"""

with open(output_file, 'w', encoding='utf-8') as f:
    f.write(md)

print(f"DONE: {output_file}")
