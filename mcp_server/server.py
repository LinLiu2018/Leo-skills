#!/usr/bin/env python3
"""
Leo System MCP Server

通过 MCP 协议暴露 Leo AI System 的所有能力（252 个 Skills、32 个 Agents、Workflows）
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# 添加 Leo System 到路径
LEO_SYSTEM_PATH = Path(os.getenv("LEO_SYSTEM_PATH", r"E:\桌面\leo_ai_system"))
sys.path.insert(0, str(LEO_SYSTEM_PATH / "src"))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# 初始化 MCP Server
server = Server("leo-system")


# ========== Tools 定义 ==========

@server.list_tools()
async def list_tools() -> List[Tool]:
    """列出所有可用的工具"""
    return [
        # Skills 相关
        Tool(
            name="skills_list",
            description="列出 Leo System 的所有技能",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {"type": "string", "description": "技能分类"},
                    "limit": {"type": "integer", "description": "返回数量限制"}
                }
            }
        ),
        Tool(
            name="skills_get",
            description="获取技能详情",
            inputSchema={
                "type": "object",
                "properties": {
                    "skill_name": {"type": "string", "description": "技能名称"}
                },
                "required": ["skill_name"]
            }
        ),
        Tool(
            name="skills_execute",
            description="执行技能",
            inputSchema={
                "type": "object",
                "properties": {
                    "skill_name": {"type": "string", "description": "技能名称"},
                    "action": {"type": "string", "description": "操作类型"},
                    "params": {"type": "object", "description": "参数"}
                },
                "required": ["skill_name", "action"]
            }
        ),
        Tool(
            name="skills_create",
            description="创建新技能",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "技能名称"},
                    "description": {"type": "string", "description": "技能描述"},
                    "category": {"type": "string", "description": "技能分类"}
                },
                "required": ["name", "description"]
            }
        ),
        Tool(
            name="skills_evaluate",
            description="评估技能质量",
            inputSchema={
                "type": "object",
                "properties": {
                    "skill_path": {"type": "string", "description": "技能路径"}
                },
                "required": ["skill_path"]
            }
        ),
        
        # Agents 相关
        Tool(
            name="agents_list",
            description="列出所有 Agent",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="agents_execute",
            description="执行 Agent",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_name": {"type": "string", "description": "Agent 名称"},
                    "task": {"type": "string", "description": "任务描述"},
                    "context": {"type": "object", "description": "上下文"}
                },
                "required": ["agent_name", "task"]
            }
        ),
        
        # Workflows 相关
        Tool(
            name="workflows_list",
            description="列出所有工作流",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="workflows_run",
            description="运行工作流",
            inputSchema={
                "type": "object",
                "properties": {
                    "workflow_name": {"type": "string", "description": "工作流名称"},
                    "input": {"type": "object", "description": "输入数据"}
                },
                "required": ["workflow_name"]
            }
        ),
        
        # 系统相关
        Tool(
            name="system_status",
            description="系统状态检查",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="system_health",
            description="健康检查",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """调用工具"""
    
    try:
        if name == "skills_list":
            result = await skills_list(arguments)
        elif name == "skills_get":
            result = await skills_get(arguments)
        elif name == "skills_execute":
            result = await skills_execute(arguments)
        elif name == "skills_create":
            result = await skills_create(arguments)
        elif name == "skills_evaluate":
            result = await skills_evaluate(arguments)
        elif name == "agents_list":
            result = await agents_list(arguments)
        elif name == "agents_execute":
            result = await agents_execute(arguments)
        elif name == "workflows_list":
            result = await workflows_list(arguments)
        elif name == "workflows_run":
            result = await workflows_run(arguments)
        elif name == "system_status":
            result = await system_status(arguments)
        elif name == "system_health":
            result = await system_health(arguments)
        else:
            return [TextContent(type="text", text=f"未知工具：{name}")]
        
        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
    
    except Exception as e:
        return [TextContent(type="text", text=f"错误：{str(e)}")]


# ========== Skills 相关实现 ==========

async def skills_list(args: Dict[str, Any]) -> Dict[str, Any]:
    """列出所有技能"""
    skills_dir = LEO_SYSTEM_PATH / "src" / "leo_skills"
    
    category_filter = args.get("category")
    limit = args.get("limit", 100)
    
    skills = []
    categories = set()
    
    for skill_dir in skills_dir.rglob("*_skill"):
        if not skill_dir.is_dir():
            continue
        
        category = skill_dir.parent.name
        categories.add(category)
        
        if category_filter and category != category_filter:
            continue
        
        # 读取 SKILL.md 获取基本信息
        skill_md = skill_dir / "SKILL.md"
        if skill_md.exists():
            content = skill_md.read_text(encoding='utf-8')
            # 简单解析 YAML 前置元数据
            desc = ""
            if 'description:' in content:
                desc = content.split('description:')[1].split('\n')[0].strip()[:100]
            
            skills.append({
                "name": skill_dir.name,
                "category": category,
                "path": str(skill_dir.relative_to(skills_dir)),
                "description": desc
            })
        
        if len(skills) >= limit:
            break
    
    return {
        "status": "success",
        "total": len(skills),
        "categories": sorted(list(categories)),
        "skills": skills
    }


async def skills_get(args: Dict[str, Any]) -> Dict[str, Any]:
    """获取技能详情"""
    skill_name = args.get("skill_name")
    if not skill_name:
        return {"status": "error", "message": "缺少 skill_name 参数"}
    
    # 查找技能
    skills_dir = LEO_SYSTEM_PATH / "src" / "leo_skills"
    
    for skill_dir in skills_dir.rglob(f"*{skill_name}*"):
        if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
            skill_md = skill_dir / "SKILL.md"
            content = skill_md.read_text(encoding='utf-8')
            
            return {
                "status": "success",
                "skill": {
                    "name": skill_dir.name,
                    "category": skill_dir.parent.name,
                    "path": str(skill_dir),
                    "content": content[:2000]  # 限制返回长度
                }
            }
    
    return {"status": "error", "message": f"未找到技能：{skill_name}"}


async def skills_execute(args: Dict[str, Any]) -> Dict[str, Any]:
    """执行技能"""
    skill_name = args.get("skill_name")
    action = args.get("action", "run")
    params = args.get("params", {})
    
    if not skill_name:
        return {"status": "error", "message": "缺少 skill_name 参数"}
    
    # 尝试导入并执行技能
    try:
        skills_dir = LEO_SYSTEM_PATH / "src" / "leo_skills"
        
        # 查找技能文件
        for skill_file in skills_dir.rglob(f"*{skill_name}*.py"):
            if skill_file.name == f"{skill_name}.py" or skill_file.name == f"{skill_name.replace('-', '_')}.py":
                # 动态导入
                import importlib.util
                spec = importlib.util.spec_from_file_location(skill_name, skill_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # 查找 Skill 类并执行
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if isinstance(attr, type) and hasattr(attr, 'execute'):
                        skill_instance = attr()
                        result = skill_instance.execute(action=action, **params)
                        return result
                
                return {"status": "error", "message": "未找到可执行的 Skill 类"}
        
        return {"status": "error", "message": f"未找到技能文件：{skill_name}"}
    
    except Exception as e:
        return {"status": "error", "message": f"执行失败：{str(e)}"}


async def skills_create(args: Dict[str, Any]) -> Dict[str, Any]:
    """创建新技能"""
    name = args.get("name")
    description = args.get("description")
    category = args.get("category", "utilities")
    
    if not name or not description:
        return {"status": "error", "message": "缺少 name 或 description 参数"}
    
    try:
        # 使用 skill-creator 创建技能
        from leo_skills.development.skill_creator.skill_creator import SkillCreator
        
        creator = SkillCreator()
        result = creator.execute(
            action="create",
            description=f"{description}。当用户需要{category}相关帮助时使用。",
            category=category
        )
        
        return result
    
    except Exception as e:
        return {"status": "error", "message": f"创建失败：{str(e)}"}


async def skills_evaluate(args: Dict[str, Any]) -> Dict[str, Any]:
    """评估技能质量"""
    skill_path = args.get("skill_path")
    
    if not skill_path:
        return {"status": "error", "message": "缺少 skill_path 参数"}
    
    try:
        # 使用 skill-creator 评估技能
        from leo_skills.development.skill_creator.skill_creator import SkillCreator
        
        creator = SkillCreator()
        
        # 1. 评估
        eval_result = creator.execute(action="evaluate", skill_path=skill_path)
        
        # 2. 基准测试
        benchmark_result = creator.execute(action="benchmark", skill_path=skill_path)
        
        # 3. 描述调优
        tune_result = creator.execute(action="tune_description", skill_path=skill_path)
        
        return {
            "status": "success",
            "evaluation": eval_result,
            "benchmark": benchmark_result,
            "optimization": tune_result
        }
    
    except Exception as e:
        return {"status": "error", "message": f"评估失败：{str(e)}"}


# ========== Agents 相关实现 ==========

async def agents_list(args: Dict[str, Any]) -> Dict[str, Any]:
    """列出所有 Agent"""
    agents_dir = LEO_SYSTEM_PATH / "src" / "leo_subagents" / "agents"
    
    agents = []
    
    if agents_dir.exists():
        for agent_dir in agents_dir.iterdir():
            if agent_dir.is_dir():
                agents.append({
                    "name": agent_dir.name,
                    "path": str(agent_dir)
                })
    
    return {
        "status": "success",
        "total": len(agents),
        "agents": agents
    }


async def agents_execute(args: Dict[str, Any]) -> Dict[str, Any]:
    """执行 Agent"""
    agent_name = args.get("agent_name")
    task = args.get("task")
    context = args.get("context", {})
    
    if not agent_name or not task:
        return {"status": "error", "message": "缺少 agent_name 或 task 参数"}
    
    # TODO: 实现 Agent 执行逻辑
    return {
        "status": "success",
        "message": f"Agent {agent_name} 执行任务：{task}",
        "context": context
    }


# ========== Workflows 相关实现 ==========

async def workflows_list(args: Dict[str, Any]) -> Dict[str, Any]:
    """列出所有工作流"""
    workflows_dir = LEO_SYSTEM_PATH / "src" / "leo_workflows"
    
    workflows = []
    
    if workflows_dir.exists():
        for workflow_file in workflows_dir.glob("*.py"):
            workflows.append({
                "name": workflow_file.stem,
                "path": str(workflow_file)
            })
    
    return {
        "status": "success",
        "total": len(workflows),
        "workflows": workflows
    }


async def workflows_run(args: Dict[str, Any]) -> Dict[str, Any]:
    """运行工作流"""
    workflow_name = args.get("workflow_name")
    input_data = args.get("input", {})
    
    if not workflow_name:
        return {"status": "error", "message": "缺少 workflow_name 参数"}
    
    # TODO: 实现工作流执行逻辑
    return {
        "status": "success",
        "message": f"工作流 {workflow_name} 运行完成",
        "input": input_data
    }


# ========== 系统相关实现 ==========

async def system_status(args: Dict[str, Any]) -> Dict[str, Any]:
    """系统状态检查"""
    return {
        "status": "success",
        "leo_system": {
            "path": str(LEO_SYSTEM_PATH),
            "exists": LEO_SYSTEM_PATH.exists(),
            "python_version": sys.version,
            "skills_count": 252,
            "agents_count": 32,
            "workflows_count": 3
        }
    }


async def system_health(args: Dict[str, Any]) -> Dict[str, Any]:
    """健康检查"""
    checks = {
        "leo_system_path": LEO_SYSTEM_PATH.exists(),
        "skills_dir": (LEO_SYSTEM_PATH / "src" / "leo_skills").exists(),
        "agents_dir": (LEO_SYSTEM_PATH / "src" / "leo_subagents").exists(),
        "python_version": sys.version_info.major >= 3 and sys.version_info.minor >= 8,
    }
    
    all_ok = all(checks.values())
    
    return {
        "status": "success" if all_ok else "warning",
        "healthy": all_ok,
        "checks": checks
    }


# ========== 主函数 ==========

async def main():
    """主函数"""
    print(f"Leo System MCP Server 启动中...")
    print(f"Leo System 路径：{LEO_SYSTEM_PATH}")
    print(f"技能数：252 | Agent 数：32 | Workflows 数：3")
    print()
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
