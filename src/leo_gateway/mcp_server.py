#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Leo MCP Server - Model Context Protocol 服务器

提供 Claude Code 与 OpenClaw/Leo System 的双向调用能力。

功能:
1. 工具 (Tools): 供 Claude Code 调用的 Leo System 能力
2. 资源 (Resources): 暴露 Skills、Agents、Memory 等数据
3. 提示词 (Prompts): 预定义的提示词模板

用法:
    python src/leo_gateway/mcp_server.py
    # 或通过 Claude Code MCP 配置调用
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel,
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger("leo-mcp-server")


class LeoMCPServer:
    """Leo MCP 服务器实现"""

    def __init__(self):
        self.server = Server("leo-system")
        self.project_root = Path(__file__).parent.parent.parent
        self._setup_handlers()

    def _setup_handlers(self):
        """设置 MCP 处理程序"""

        @self.server.list_resources()
        async def list_resources() -> List[Resource]:
            """列出可用资源"""
            resources = [
                Resource(
                    uri="leo://skills/registry",
                    name="Skill Registry",
                    description="所有已注册的 Leo Skills",
                    mimeType="application/json",
                ),
                Resource(
                    uri="leo://agents/list",
                    name="Agent List",
                    description="所有可用的 Agents",
                    mimeType="application/json",
                ),
                Resource(
                    uri="leo://memory/shared",
                    name="Shared Memory",
                    description="共享记忆存储",
                    mimeType="application/json",
                ),
                Resource(
                    uri="leo://gateway/status",
                    name="Gateway Status",
                    description="Leo Gateway 运行状态",
                    mimeType="application/json",
                ),
                Resource(
                    uri="leo://user/profile",
                    name="User Profile",
                    description="当前用户画像",
                    mimeType="application/json",
                ),
            ]
            return resources

        @self.server.read_resource()
        async def read_resource(uri: str) -> str:
            """读取资源内容"""
            logger.info(f"Reading resource: {uri}")

            if uri == "leo://skills/registry":
                return self._get_skills_registry()

            elif uri == "leo://agents/list":
                return self._get_agents_list()

            elif uri == "leo://memory/shared":
                return self._get_shared_memory()

            elif uri == "leo://gateway/status":
                return self._get_gateway_status()

            elif uri == "leo://user/profile":
                return self._get_user_profile()

            else:
                raise ValueError(f"Unknown resource: {uri}")

        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """列出可用工具"""
            tools = [
                Tool(
                    name="execute_skill",
                    description="执行指定的 Leo Skill",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "skill_name": {
                                "type": "string",
                                "description": "要执行的 skill 名称",
                            },
                            "parameters": {
                                "type": "object",
                                "description": "执行参数",
                                "default": {},
                            },
                        },
                        "required": ["skill_name"],
                    },
                ),
                Tool(
                    name="delegate_to_agent",
                    description="委托任务给指定的 Agent",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "agent_name": {
                                "type": "string",
                                "description": "Agent 名称",
                            },
                            "task": {
                                "type": "string",
                                "description": "任务描述",
                            },
                            "context": {
                                "type": "object",
                                "description": "上下文信息",
                                "default": {},
                            },
                        },
                        "required": ["agent_name", "task"],
                    },
                ),
                Tool(
                    name="search_skills",
                    description="搜索匹配的 Skills",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "搜索关键词",
                            },
                            "category": {
                                "type": "string",
                                "description": "分类过滤（可选）",
                            },
                        },
                        "required": ["query"],
                    },
                ),
                Tool(
                    name="remember",
                    description="保存信息到共享记忆",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "key": {
                                "type": "string",
                                "description": "记忆键",
                            },
                            "value": {
                                "type": "string",
                                "description": "记忆值",
                            },
                            "category": {
                                "type": "string",
                                "description": "分类",
                                "default": "general",
                            },
                            "importance": {
                                "type": "integer",
                                "description": "重要性 1-5",
                                "default": 3,
                            },
                        },
                        "required": ["key", "value"],
                    },
                ),
                Tool(
                    name="recall",
                    description="从共享记忆检索信息",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "key": {
                                "type": "string",
                                "description": "记忆键",
                            },
                            "query": {
                                "type": "string",
                                "description": "搜索关键词（可选，用于模糊搜索）",
                            },
                        },
                        "required": [],
                    },
                ),
                Tool(
                    name="send_to_feishu",
                    description="发送消息到飞书",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "description": "消息内容",
                            },
                            "channel_id": {
                                "type": "string",
                                "description": "频道ID",
                                "default": "default",
                            },
                        },
                        "required": ["message"],
                    },
                ),
                Tool(
                    name="get_openclaw_status",
                    description="获取 OpenClaw Gateway 状态",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                    },
                ),
                Tool(
                    name="get_task_status",
                    description="查询 Agent 任务执行状态",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "string",
                                "description": "任务ID (由 delegate_to_agent 返回)",
                            },
                        },
                        "required": ["task_id"],
                    },
                ),
            ]
            return tools

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
            """调用工具"""
            logger.info(f"Calling tool: {name} with args: {arguments}")

            try:
                if name == "execute_skill":
                    result = await self._execute_skill(
                        arguments["skill_name"],
                        arguments.get("parameters", {})
                    )
                    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

                elif name == "delegate_to_agent":
                    result = await self._delegate_to_agent(
                        arguments["agent_name"],
                        arguments["task"],
                        arguments.get("context", {})
                    )
                    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

                elif name == "search_skills":
                    result = self._search_skills(
                        arguments["query"],
                        arguments.get("category")
                    )
                    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

                elif name == "remember":
                    result = self._remember(
                        arguments["key"],
                        arguments["value"],
                        arguments.get("category", "general"),
                        arguments.get("importance", 3)
                    )
                    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

                elif name == "recall":
                    result = self._recall(
                        arguments.get("key"),
                        arguments.get("query")
                    )
                    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

                elif name == "send_to_feishu":
                    result = await self._send_to_feishu(
                        arguments["message"],
                        arguments.get("channel_id", "default")
                    )
                    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

                elif name == "get_openclaw_status":
                    result = await self._get_openclaw_status()
                    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

                elif name == "get_task_status":
                    result = await self._get_task_status(arguments["task_id"])
                    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

                else:
                    raise ValueError(f"Unknown tool: {name}")

            except Exception as e:
                logger.error(f"Tool execution error: {e}")
                return [TextContent(type="text", text=json.dumps({"error": str(e)}, ensure_ascii=False))]

    # ========== 资源实现 ==========

    def _get_skills_registry(self) -> str:
        """获取技能注册表"""
        registry_file = self.project_root / ".claude" / "skill_registry.json"
        if registry_file.exists():
            with open(registry_file, "r", encoding="utf-8") as f:
                return f.read()
        return json.dumps({"error": "Registry not found"}, ensure_ascii=False)

    def _get_agents_list(self) -> str:
        """获取 Agent 列表"""
        try:
            from leo_orchestrator.registry import get_registry
            registry = get_registry()
            agents = [
                {
                    "name": name,
                    "type": agent.type,
                    "priority": agent.priority,
                    "skills": agent.skills,
                    "enabled": agent.enabled,
                }
                for name, agent in (registry.agents or {}).items()
            ]
            return json.dumps({"agents": agents}, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    def _get_shared_memory(self) -> str:
        """获取共享记忆"""
        try:
            from leo_memory.shared_memory import get_shared_memory
            memory = get_shared_memory()
            stats = memory.get_stats()
            return json.dumps(stats, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    def _get_gateway_status(self) -> str:
        """获取 Gateway 状态"""
        try:
            from leo_gateway.gateway import get_gateway
            gateway = get_gateway()
            status = gateway.get_status()
            return json.dumps(status, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    def _get_user_profile(self) -> str:
        """获取用户画像"""
        try:
            user_profile_path = self.project_root / "leo_knowledge" / "context" / "user_profile.md"
            if user_profile_path.exists():
                content = user_profile_path.read_text(encoding="utf-8")
                return json.dumps({
                    "profile_available": True,
                    "content_preview": content[:500] + "..." if len(content) > 500 else content
                }, ensure_ascii=False, indent=2)
            else:
                return json.dumps({"profile_available": False}, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    # ========== 工具实现 ==========

    async def _execute_skill(self, skill_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """执行 Skill"""
        try:
            # 尝试动态导入 skill
            skill_path = f"src.leo_skills.{skill_name}"
            module = __import__(skill_path, fromlist=["main"])

            if hasattr(module, "main"):
                result = await module.main(**parameters) if asyncio.iscoroutinefunction(module.main) else module.main(**parameters)
                return {"success": True, "skill": skill_name, "result": result}
            else:
                return {"success": False, "error": f"Skill {skill_name} has no main() function"}

        except Exception as e:
            return {"success": False, "skill": skill_name, "error": str(e)}

    async def _delegate_to_agent(self, agent_name: str, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        委托给 Agent - 使用异步任务队列实现真正执行

        Args:
            agent_name: Agent 名称
            task: 任务描述
            context: 上下文信息

        Returns:
            包含 task_id 的响应，可用于后续查询任务状态
        """
        try:
            from leo_orchestrator.registry import get_registry
            from leo_gateway.task_queue import get_task_queue

            registry = get_registry()
            agent = registry.get_agent(agent_name)

            if not agent:
                return {"success": False, "error": f"Agent {agent_name} not found"}

            # 获取或启动任务队列
            task_queue = get_task_queue()
            if not task_queue._running:
                await task_queue.start()

            # 提交异步任务
            task_id = await task_queue.submit(
                agent_name=agent_name,
                task_description=task,
                context=context
            )

            return {
                "success": True,
                "task_id": task_id,
                "agent": agent_name,
                "task": task,
                "status": "queued",
                "estimated_wait": "5-10s",
                "check_status": f"使用 get_task_status 工具查询任务 {task_id}"
            }

        except Exception as e:
            logger.error(f"Agent delegation failed: {e}")
            return {"success": False, "error": str(e)}

    def _search_skills(self, query: str, category: Optional[str] = None) -> Dict[str, Any]:
        """搜索 Skills"""
        try:
            registry_file = self.project_root / ".claude" / "skill_registry.json"
            with open(registry_file, "r", encoding="utf-8") as f:
                registry = json.load(f)

            results = []
            query_lower = query.lower()

            for name, skill in registry.get("skills", {}).items():
                # 分类过滤
                if category and skill.get("category") != category:
                    continue

                # 匹配搜索
                match_score = 0
                if query_lower in name.lower():
                    match_score += 10
                if query_lower in skill.get("description", "").lower():
                    match_score += 5
                for trigger in skill.get("triggers", []):
                    if query_lower in trigger.lower():
                        match_score += 8

                if match_score > 0:
                    results.append({
                        "name": name,
                        "match_score": match_score,
                        **skill
                    })

            # 按匹配度排序
            results.sort(key=lambda x: x["match_score"], reverse=True)

            return {
                "query": query,
                "category_filter": category,
                "total_matches": len(results),
                "results": results[:10]  # 返回前10个
            }

        except Exception as e:
            return {"error": str(e)}

    def _remember(self, key: str, value: str, category: str, importance: int) -> Dict[str, Any]:
        """保存记忆"""
        try:
            from leo_memory.shared_memory import get_shared_memory
            memory = get_shared_memory()
            entry = memory.remember(
                key=key,
                value=value,
                category=category,
                importance=importance
            )
            return {
                "success": True,
                "key": key,
                "category": category,
                "created_at": entry.created_at
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _recall(self, key: Optional[str], query: Optional[str]) -> Dict[str, Any]:
        """检索记忆"""
        try:
            from leo_memory.shared_memory import get_shared_memory
            memory = get_shared_memory()

            if key:
                entry = memory.recall(key)
                if entry:
                    return {
                        "found": True,
                        "key": entry.key,
                        "value": entry.value,
                        "category": entry.category,
                        "created_at": entry.created_at
                    }
                else:
                    return {"found": False, "key": key}

            elif query:
                entries = memory.search(query)
                return {
                    "found": len(entries) > 0,
                    "query": query,
                    "matches": [
                        {
                            "key": e.key,
                            "value": e.value,
                            "category": e.category,
                            "importance": e.importance
                        }
                        for e in entries[:10]
                    ]
                }

            else:
                # 返回所有活跃记忆
                entries = memory.get_all()
                return {
                    "total": len(entries),
                    "entries": [
                        {
                            "key": e.key,
                            "value": e.value[:100] + "..." if len(e.value) > 100 else e.value,
                            "category": e.category
                        }
                        for e in entries[:20]
                    ]
                }

        except Exception as e:
            return {"error": str(e)}

    async def _send_to_feishu(self, message: str, channel_id: str) -> Dict[str, Any]:
        """发送到飞书"""
        try:
            from leo_interface.openclaw_bridge import OpenClawBridge
            bridge = OpenClawBridge()
            result = bridge.send_to_feishu(message, channel_id)
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _get_openclaw_status(self) -> Dict[str, Any]:
        """获取 OpenClaw 状态"""
        try:
            from leo_interface.openclaw_bridge import OpenClawBridge
            bridge = OpenClawBridge()
            health = bridge.healthcheck()
            return {
                "gateway_url": bridge.gateway_url,
                "healthcheck": health,
                "timestamp": str(__import__('datetime').datetime.now())
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _get_task_status(self, task_id: str) -> Dict[str, Any]:
        """查询 Agent 任务状态"""
        try:
            from leo_gateway.task_queue import get_task_queue

            task_queue = get_task_queue()
            status = task_queue.get_task_status(task_id)

            if not status:
                return {"success": False, "error": f"Task {task_id} not found"}

            return {"success": True, "task": status}

        except Exception as e:
            return {"success": False, "error": str(e)}

    # ========== 服务器运行 ==========

    async def run(self):
        """运行 MCP 服务器"""
        logger.info("Starting Leo MCP Server...")

        async with stdio_server(server=self.server) as (read_stream, write_stream):
            logger.info("MCP Server connected via stdio")
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options(),
            )


def main():
    server = LeoMCPServer()
    asyncio.run(server.run())


if __name__ == "__main__":
    main()
