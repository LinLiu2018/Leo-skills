# -*- coding: utf-8 -*-
"""
跨系统记忆同步
===============
实现 Claude Code ↔ OpenClaw ↔ SharedMemory 的三向同步
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


class CrossSystemMemorySync:
    """跨系统记忆同步器"""

    def __init__(self):
        self.claude_memory_path = self._find_claude_memory()
        self.shared_memory_path = Path("leo_knowledge/context/shared_memory.md")

    def _find_claude_memory(self) -> Optional[Path]:
        """查找 Claude Code auto memory 路径"""
        # 标准路径
        possible_paths = [
            Path.home() / ".claude" / "projects" / "leo-ai-system" / "memory" / "MEMORY.md",
            Path("C:/Users/刘方林/.claude/projects/leo-ai-system/memory/MEMORY.md"),
        ]
        for path in possible_paths:
            if path.exists():
                return path
        return None

    def sync_to_claude(self, key: str, value: str, category: str = "leo_system"):
        """同步到 Claude Code memory"""
        if not self.claude_memory_path:
            return False

        try:
            with open(self.claude_memory_path, "a", encoding="utf-8") as f:
                f.write(f"\n## {category}\n")
                f.write(f"- **{key}**: {value} (同步于 {datetime.now().isoformat()})\n")
            return True
        except Exception as e:
            print(f"[ERROR] 同步到 Claude 失败: {e}")
            return False

    def sync_from_openclaw(self, messages: list) -> int:
        """从 OpenClaw/飞书同步消息"""
        count = 0
        try:
            from leo_memory.shared_memory import get_shared_memory
            memory = get_shared_memory()

            for msg in messages:
                if "项目" in msg.get("content", ""):
                    memory.remember(
                        key=f"feishu_{msg.get('id', 'unknown')}",
                        value=msg["content"],
                        category="openclaw_sync"
                    )
                    count += 1
            return count
        except Exception as e:
            print(f"[ERROR] 从 OpenClaw 同步失败: {e}")
            return 0


def sync_memory(direction: str, **data) -> bool:
    """便捷函数：同步记忆"""
    sync = CrossSystemMemorySync()
    if direction == "to_claude":
        return sync.sync_to_claude(data.get("key"), data.get("value"))
    elif direction == "from_openclaw":
        return sync.sync_from_openclaw(data.get("messages", [])) > 0
    return False
