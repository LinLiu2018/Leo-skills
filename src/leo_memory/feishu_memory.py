#!/usr/bin/env python3
"""
飞书对话记忆系统
================
从 OpenClaw 会话历史中提取关键信息，作为 Leo System 的动态记忆

功能：
1. 读取 OpenClaw 会话历史
2. 提取关键信息（任务、决策、偏好等）
3. 更新到 Leo System 知识库
4. 支持实时同步和增量更新
"""

import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# OpenClaw 会话目录
OPENCLAW_SESSIONS_DIR = Path.home() / ".openclaw" / "agents" / "leo-assistant" / "sessions"
# Leo System 记忆文件
LEO_MEMORY_FILE = Path(__file__).parent.parent.parent / "leo_knowledge" / "context" / "shared_memory.md"
# 记忆缓存文件
MEMORY_CACHE_FILE = Path(__file__).parent / "memory_cache.json"


class FeishuMemory:
    """飞书对话记忆管理器"""

    def __init__(self):
        self.sessions_dir = OPENCLAW_SESSIONS_DIR
        self.memory_file = LEO_MEMORY_FILE
        self.cache_file = MEMORY_CACHE_FILE
        self.memories: Dict[str, List[dict]] = {
            "tasks": [],           # 任务记录
            "decisions": [],       # 决策记录
            "preferences": [],     # 用户偏好
            "key_info": [],        # 关键信息
            "recent_topics": [],   # 最近话题
            "conversations": []    # 原始对话
        }
        self._load_cache()

    def _load_cache(self):
        """加载缓存"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cached = json.load(f)
                    self.memories.update(cached.get("memories", {}))
            except:
                pass

    def _save_cache(self):
        """保存缓存"""
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump({
                "memories": self.memories,
                "updated_at": datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)

    def load_sessions(self, hours_back: int = 24) -> List[dict]:
        """加载最近的会话历史"""
        messages = []
        cutoff_time = datetime.now() - timedelta(hours=hours_back)

        # 读取 sessions.json 获取会话文件列表
        sessions_index = self.sessions_dir / "sessions.json"
        if not sessions_index.exists():
            return messages

        with open(sessions_index, 'r', encoding='utf-8') as f:
            sessions = json.load(f)

        # 读取每个会话的 JSONL 文件
        for session_key, session_info in sessions.items():
            session_file = session_info.get("sessionFile")
            if session_file and os.path.exists(session_file):
                messages.extend(self._parse_session_file(session_file, cutoff_time))

        return messages

    def _parse_session_file(self, file_path: str, cutoff_time: datetime = None) -> List[dict]:
        """解析会话 JSONL 文件"""
        messages = []

        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    if entry.get("type") == "message":
                        msg = entry.get("message", {})
                        timestamp_str = entry.get("timestamp", "")

                        # 检查时间过滤
                        if cutoff_time and timestamp_str:
                            try:
                                msg_time = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                                if msg_time.replace(tzinfo=None) < cutoff_time:
                                    continue
                            except:
                                pass

                        content = msg.get("content", [])
                        text = ""
                        for item in content:
                            if item.get("type") == "text":
                                text += item.get("text", "")

                        if text:
                            # 提取飞书消息内容
                            feishu_match = re.search(r'Feishu DM from [^:]+: (.+?)(?:\n|$)', text)
                            clean_text = feishu_match.group(1) if feishu_match else text

                            messages.append({
                                "role": msg.get("role", "unknown"),
                                "content": clean_text,
                                "raw_content": text,
                                "timestamp": timestamp_str
                            })
                except json.JSONDecodeError:
                    continue

        return messages

    def extract_key_info(self, messages: List[dict]) -> None:
        """从消息中提取关键信息"""

        for msg in messages:
            content = msg.get("content", "")
            role = msg.get("role", "")
            timestamp = msg.get("timestamp", "")

            # 保存原始对话
            self.memories["conversations"].append({
                "role": role,
                "content": content[:200],
                "timestamp": timestamp
            })

            # 提取任务（用户请求）
            if role == "user":
                task_patterns = [
                    (r"帮我(.+)", "帮我"),
                    (r"请(.+)", "请"),
                    (r"生成(.+)", "生成"),
                    (r"创建(.+)", "创建"),
                    (r"写(.+)", "写"),
                    (r"分析(.+)", "分析"),
                    (r"研究(.+)", "研究"),
                    (r"检查(.+)", "检查"),
                    (r"验证(.+)", "验证"),
                    (r"测试(.+)", "测试")
                ]
                for pattern, prefix in task_patterns:
                    match = re.search(pattern, content)
                    if match:
                        task_text = match.group(0)
                        # 避免重复
                        if not any(t["task"] == task_text for t in self.memories["tasks"]):
                            self.memories["tasks"].append({
                                "task": task_text,
                                "timestamp": timestamp,
                                "status": "completed"
                            })
                        break

                # 提取关键信息
                key_patterns = [
                    r"(MCP|OpenClaw|飞书|Leo|Gateway)",
                    r"(最佳实践|架构|集成|同步)",
                    r"(房产|楼盘|市场)"
                ]
                for pattern in key_patterns:
                    if re.search(pattern, content):
                        self.memories["key_info"].append({
                            "info": content[:100],
                            "timestamp": timestamp
                        })
                        break

            # 提取决策（AI 回复中的关键决策）
            if role == "assistant":
                decision_patterns = [
                    r"我建议(.+)",
                    r"推荐(.+)",
                    r"选择(.+)",
                    r"使用(.+)方案",
                    r"已完成(.+)",
                    r"已修复(.+)"
                ]
                for pattern in decision_patterns:
                    match = re.search(pattern, content)
                    if match:
                        decision_text = match.group(0)
                        if not any(d["decision"] == decision_text for d in self.memories["decisions"]):
                            self.memories["decisions"].append({
                                "decision": decision_text,
                                "timestamp": timestamp
                            })
                        break

        # 只保留最近的记录
        for key in self.memories:
            self.memories[key] = self.memories[key][-50:]  # 保留最近50条

    def update_memory_file(self) -> None:
        """更新记忆文件"""

        content = f"""# Leo System 动态记忆

> 自动从飞书对话中提取，最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 最近任务 (最近24小时)

| 任务 | 时间 | 状态 |
|------|------|------|
"""
        for task in self.memories["tasks"][-15:]:
            task_text = task['task'][:60].replace('|', '/')
            time_str = task['timestamp'][:10] if task['timestamp'] else '-'
            content += f"| {task_text} | {time_str} | {task['status']} |\n"

        content += """
## 最近对话摘要

"""
        # 只显示用户消息
        user_msgs = [c for c in self.memories["conversations"] if c["role"] == "user"]
        for conv in user_msgs[-10:]:
            conv_text = conv['content'][:80].replace('\n', ' ')
            content += f"- [{conv['timestamp'][:16]}] {conv_text}\n"

        content += """
## 关键决策

"""
        for decision in self.memories["decisions"][-10:]:
            content += f"- {decision['decision'][:100]}\n"

        content += """
## 关键信息

"""
        for info in self.memories["key_info"][-10:]:
            content += f"- {info['info'][:80]}\n"

        content += """
## 用户偏好

- 语言: 中文
- 领域: 房地产、AI、内容创作、系统集成
- 工具: 飞书、OpenClaw、Claude Code、Leo System
- 关注点: 最佳实践、架构设计、能力同步

---
*此文件由 feishu_memory.py 自动生成，支持实时同步*
"""

        # 确保目录存在
        self.memory_file.parent.mkdir(parents=True, exist_ok=True)

        with open(self.memory_file, 'w', encoding='utf-8') as f:
            f.write(content)

    def sync(self, hours_back: int = 24) -> dict:
        """同步记忆"""
        messages = self.load_sessions(hours_back)
        self.extract_key_info(messages)
        self.update_memory_file()
        self._save_cache()

        return {
            "status": "success",
            "messages_processed": len(messages),
            "tasks_extracted": len(self.memories["tasks"]),
            "decisions_extracted": len(self.memories["decisions"]),
            "conversations_stored": len(self.memories["conversations"]),
            "memory_file": str(self.memory_file)
        }

    def get_recent_context(self, limit: int = 10) -> str:
        """获取最近的对话上下文（供 AI 使用）"""
        context = "## 最近飞书对话上下文\n\n"
        user_msgs = [c for c in self.memories["conversations"] if c["role"] == "user"]
        for conv in user_msgs[-limit:]:
            context += f"- {conv['content'][:100]}\n"
        return context


def sync_feishu_memory(hours_back: int = 24) -> dict:
    """同步飞书记忆（供外部调用）"""
    memory = FeishuMemory()
    return memory.sync(hours_back)


def get_feishu_context(limit: int = 10) -> str:
    """获取飞书对话上下文（供外部调用）"""
    memory = FeishuMemory()
    memory.load_sessions(24)
    return memory.get_recent_context(limit)


if __name__ == "__main__":
    result = sync_feishu_memory(48)  # 同步最近48小时
    print(json.dumps(result, indent=2, ensure_ascii=False))
