#!/usr/bin/env python3
"""完整提取飞书 Leo 所有配置信息"""
import json
import os
import re
from pathlib import Path
from datetime import datetime

sessions_dir = os.path.expanduser("~/.openclaw/agents/leo-assistant/sessions")
output_file = "leo_full_config_report.md"

all_content = []

# 处理所有文件（包括 deleted 和 reset）
session_files = list(Path(sessions_dir).glob("*.jsonl"))

for session_file in session_files:
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

                if role in ['user', 'assistant']:
                    for c in content_list:
                        if c.get('type') == 'text':
                            all_content.append({
                                'role': role,
                                'text': c.get('text', '')
                            })
                            break
    except Exception as e:
        pass

# 提取各类信息
cron_tasks = set()
skills = set()
personalities = []
preferences = []
memories = []
workflows = []
openclaw_configs = []

for item in all_content:
    text = item['text']
    role = item['role']

    # 定时任务
    if '[cron:' in text:
        matches = re.findall(r'\[cron:([^\]]+)\]', text)
        for m in matches:
            cron_tasks.add(m.strip())

    # 技能调用
    skill_matches = re.findall(r'skill[：:]\s*([^\s\n，。,\.]+)', text)
    for s in skill_matches:
        if ':execute' in s or '_skill' in s:
            skills.add(s.strip())

    # 技能名称（中文）
    cn_skills = re.findall(r'调用[、\s]+([^\s，。,\.]+?)(?:技能|任务)', text)
    for s in cn_skills:
        skills.add(s.strip())

    # AI人格设定
    if any(k in text for k in ['你是谁', '人格', '性格设定', '角色设定', 'system prompt', 'AI角色']):
        if len(text) < 800 and role == 'assistant':
            personalities.append(text[:500])

    # 用户偏好
    if any(k in text for k in ['我喜欢', '我不喜欢', '用户偏好', '偏好设置', '记住']):
        if len(text) < 800 and role == 'assistant':
            preferences.append(text[:400])

    # 用户记忆
    if any(k in text for k in ['记住', '存储', 'memory', '记忆']):
        if len(text) < 500:
            memories.append(text[:300])

    # OpenClaw 配置
    if any(k in text.lower() for k in ['openclaw', '配置', 'config', '设置']):
        if len(text) < 600 and 'error' not in text.lower():
            openclaw_configs.append(text[:400])

    # 工作流
    if any(k in text for k in ['工作流', 'workflow', '流程', '自动化']):
        if len(text) < 500:
            workflows.append(text[:300])

# 生成 Markdown
md = f"""# Leo AI System 完整配置报告

> 自动生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
> 来源: 飞书 Leo 助手所有对话历史 ({len(session_files)} 个会话文件)

---

## 1. 定时任务 (Cron Jobs) - {len(cron_tasks)} 个

"""

for t in sorted(cron_tasks):
    md += f"- {t}\n"

md += f"""

---

## 2. 技能 (Skills) - {len(skills)} 个

```
"""

for s in sorted(skills):
    md += f"- {s}\n"

md += """```

---

## 3. AI 人格设定

"""

for p in personalities[:3]:
    md += f"> {p}\n\n---\n\n"

md += """---

## 4. 用户偏好

"""

for p in preferences[:5]:
    md += f"> {p}\n\n---\n\n"

md += """---

## 5. 用户记忆

"""

for m in memories[:5]:
    md += f"> {m}\n\n---\n\n"

md += """---

## 6. 工作流/自动化

"""

for w in workflows[:5]:
    md += f"> {w}\n\n---\n\n"

md += f"""---

## 7. OpenClaw 配置相关

"""

for c in openclaw_configs[:5]:
    md += f"> {c}\n\n---\n\n"

md += f"""---

## 统计摘要

| 类别 | 数量 |
|------|------|
| 定时任务 | {len(cron_tasks)} |
| 技能调用 | {len(skills)} |
| AI人格设定 | {len(personalities)} |
| 用户偏好 | {len(preferences)} |
| 用户记忆 | {len(memories)} |
| 工作流 | {len(workflows)} |
| 配置相关 | {len(openclaw_configs)} |

---

*本报告由 Leo AI System 自动生成*
"""

with open(output_file, 'w', encoding='utf-8') as f:
    f.write(md)

print(f"DONE: {output_file}")
print(f"Sessions: {len(session_files)}")
