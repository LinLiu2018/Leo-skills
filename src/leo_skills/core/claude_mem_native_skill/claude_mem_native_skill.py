# -*- coding: utf-8 -*-
"""
Claude Mem Native Skill
======================

集成 Claude-Mem 原生命令行工具
npm: claude-mem v12.1.2

Author: Leo AI System
"""

import json
import subprocess
import re
from pathlib import Path
from typing import Dict, List, Optional, Any

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from base import BaseSkill, SkillResult


def run_claude_mem(args: List[str], timeout: int = 30) -> Dict[str, Any]:
    """
    运行 claude-mem 命令

    Args:
        args: 命令参数列表
        timeout: 超时秒数

    Returns:
        {"success": bool, "output": str, "error": str}
    """
    try:
        cmd = ["npx", "claude-mem"] + args
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=False
        )

        if result.returncode == 0:
            return {"success": True, "output": result.stdout, "error": ""}
        else:
            return {"success": False, "output": result.stdout, "error": result.stderr}

    except subprocess.TimeoutExpired:
        return {"success": False, "output": "", "error": "Command timeout"}
    except FileNotFoundError:
        return {"success": False, "output": "", "error": "claude-mem not found. Install with: npx claude-mem install"}
    except Exception as e:
        return {"success": False, "output": "", "error": str(e)}


class ClaudeMemNativeSkill(BaseSkill):
    """
    Claude-Mem Native Skill

    提供与原生 Claude-Mem 的集成
    """

    @property
    def name(self) -> str:
        return "claude_mem_native"

    @property
    def description(self) -> str:
        return "Claude-Mem原生集成 - 跨会话记忆系统"

    def execute(self, action: str = "default", **kwargs) -> SkillResult:
        """
        执行 Claude-Mem 操作

        Actions:
            status: 查看状态
            search: 搜索记忆
            recent: 最近记忆
            stats: 统计信息
            install: 安装
        """
        if action == "status":
            return self._status()
        elif action == "search":
            return self._search(kwargs.get("query", ""))
        elif action == "recent":
            return self._recent(kwargs.get("limit", 10))
        elif action == "stats":
            return self._stats()
        elif action == "install":
            return self._install()
        elif action == "openclaw":
            return self._openclaw_install()
        else:
            return self._status()

    def _status(self) -> SkillResult:
        """查看状态"""
        result = run_claude_mem(["--version"])

        if result["success"]:
            return SkillResult.ok(
                data={"version": result["output"].strip(), "installed": True},
                message=f"Claude-Mem {result['output'].strip()} 已安装"
            )
        else:
            return SkillResult.ok(
                data={"installed": False, "error": result["error"]},
                message="Claude-Mem 未安装"
            )

    def _search(self, query: str) -> SkillResult:
        """搜索记忆"""
        if not query:
            return SkillResult.fail("请提供搜索关键词")

        result = run_claude_mem(["search", query])

        if result["success"]:
            return SkillResult.ok(
                data={"query": query, "output": result["output"]},
                message=f"搜索 '{query}' 完成"
            )
        else:
            return SkillResult.fail(f"搜索失败: {result['error']}")

    def _recent(self, limit: int = 10) -> SkillResult:
        """最近记忆"""
        result = run_claude_mem(["recent", "--limit", str(limit)])

        if result["success"]:
            return SkillResult.ok(
                data={"recent": result["output"]},
                message=f"获取最近 {limit} 条记忆"
            )
        else:
            return SkillResult.fail(f"获取失败: {result['error']}")

    def _stats(self) -> SkillResult:
        """统计信息"""
        result = run_claude_mem(["stats"])

        if result["success"]:
            return SkillResult.ok(
                data={"stats": result["output"]},
                message="统计信息"
            )
        else:
            return SkillResult.fail(f"获取失败: {result['error']}")

    def _install(self) -> SkillResult:
        """安装 Claude-Mem"""
        return SkillResult.ok(
            data={"command": "npx claude-mem install"},
            message="运行 'npx claude-mem install' 安装"
        )

    def _openclaw_install(self) -> SkillResult:
        """OpenClaw集成安装"""
        return SkillResult.ok(
            data={"command": "curl -fsSL https://install.cmem.ai/openclaw.sh | bash"},
            message="运行 'curl -fsSL https://install.cmem.ai/openclaw.sh | bash' 集成到OpenClaw"
        )

    def get_actions(self) -> List[str]:
        return ["default", "status", "search", "recent", "stats", "install", "openclaw"]


# 快捷函数
def mem_search(query: str) -> str:
    """快速搜索"""
    skill = ClaudeMemNativeSkill()
    result = skill.execute(action="search", query=query)
    return result.data.get("output", "") if result.success else result.error


def mem_stats() -> str:
    """快速获取统计"""
    skill = ClaudeMemNativeSkill()
    result = skill.execute(action="stats")
    return result.data.get("stats", "") if result.success else result.error


if __name__ == "__main__":
    skill = ClaudeMemNativeSkill()
    print(skill.execute("status"))
