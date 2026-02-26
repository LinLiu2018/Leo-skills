"""
Leo AI System Web UI - Backend API
FastAPI application providing REST endpoints for the React frontend.
Connects to real Leo system data.
"""

import sys
import os
import re
import yaml
import asyncio
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

# 加载环境变量
from dotenv import load_dotenv
from pathlib import Path
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# 调试: 打印环境变量
print(f"[DEBUG] Loading .env from: {env_path}")
print(f"[DEBUG] AI_PROVIDER: {os.getenv('AI_PROVIDER', 'NOT SET')}")
print(f"[DEBUG] AI_MODEL: {os.getenv('AI_MODEL', 'NOT SET')}")
print(f"[DEBUG] MINIMAX_API_KEY exists: {bool(os.getenv('MINIMAX_API_KEY'))}")

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware

# 导入数据库模型和AI客户端
sys.path.insert(0, str(Path(__file__).parent))
from models import (
    init_db, SessionLocal, get_db,
    ConversationDB, MessageDB, ExecutionLogDB,
    VideoAccountDB, VideoAccountHistoryDB
)
from ai_client import get_agent_engine, AIClient
from sqlalchemy.orm import Session

try:
    from .leo_api_adapter import get_leo_api
    from .schemas import LeoRequest, LeoResponse, ErrorCode
except ImportError:
    from leo_api_adapter import get_leo_api
    from schemas import LeoRequest, LeoResponse, ErrorCode

app = FastAPI(
    title="Leo AI System API",
    description="Backend API for Leo AI System Web UI - Connected to real system data",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== Path Configuration =====
SKILLS_DIR = project_root / "src" / "leo_skills"
WORKFLOWS_DIR = project_root / "src" / "leo_workflows" / "definitions"
KNOWLEDGE_DIR = project_root / "leo_knowledge" / "context"
MEMORY_FILE = KNOWLEDGE_DIR / "shared_memory.md"


# ===== Pydantic Models =====

class SkillInput(BaseModel):
    name: str
    type: str
    required: bool
    description: Optional[str] = None
    default: Optional[Any] = None


class SkillOutput(BaseModel):
    name: str
    type: str
    description: Optional[str] = None


class Skill(BaseModel):
    id: str
    name: str
    display_name: str
    version: str
    category: str
    description: str
    author: str
    status: str
    triggers: List[str]
    inputs: List[SkillInput]
    outputs: List[SkillOutput]
    created_at: str
    updated_at: str


class Agent(BaseModel):
    id: str
    name: str
    display_name: str
    description: str
    role: str
    capabilities: List[str]
    skills: List[str]
    status: str
    created_at: str
    updated_at: str


class WorkflowStep(BaseModel):
    name: str
    type: str
    agent: Optional[str] = None
    skill: Optional[str] = None
    retries: Optional[int] = None
    timeout: Optional[int] = None
    parallel_steps: Optional[List[Dict]] = None


class WorkflowInput(BaseModel):
    name: str
    type: str
    required: bool
    description: Optional[str] = None


class Workflow(BaseModel):
    id: str
    name: str
    display_name: str
    version: str
    description: str
    status: str
    steps: List[WorkflowStep]
    inputs: List[WorkflowInput]
    created_at: str
    updated_at: str


class MemoryEntry(BaseModel):
    id: str
    key: str
    value: str
    category: str
    importance: int
    created_at: str
    updated_at: str
    expires_at: Optional[str] = None


class MemoryStats(BaseModel):
    total_entries: int
    categories: Dict[str, int]
    by_importance: Dict[int, int]


class IntentMatch(BaseModel):
    intent_type: str
    target: str
    confidence: float
    params: Dict[str, Any]
    alternatives: List[Dict[str, Any]]


class RoutingDecision(BaseModel):
    action: str
    target: str
    params: Dict[str, Any]


class IntentTestResult(BaseModel):
    input: str
    match: IntentMatch
    routing: RoutingDecision
    execution_time_ms: int


class SystemStats(BaseModel):
    total_skills: int
    total_agents: int
    total_workflows: int
    active_tasks: int
    memory_entries: int
    uptime_hours: int


class CategoryStats(BaseModel):
    category: str
    count: int
    label: str


class ApiResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    message: Optional[str] = None


# ===== Data Loading Functions =====

def parse_skill_md(file_path: Path) -> Optional[Skill]:
    """Parse SKILL.md file and extract skill information."""
    try:
        content = file_path.read_text(encoding='utf-8')

        # Extract YAML frontmatter
        match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if not match:
            return None

        frontmatter = yaml.safe_load(match.group(1))

        # Get file stats for dates
        stat = file_path.stat()
        created_at = datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d')
        updated_at = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d')

        # Get category from directory structure
        relative_path = file_path.relative_to(SKILLS_DIR)
        category_parts = relative_path.parts[:-1]  # Exclude SKILL.md
        category = '/'.join(category_parts) if category_parts else 'uncategorized'

        # Extract inputs/outputs from frontmatter if available
        inputs = []
        outputs = []

        if 'inputs' in frontmatter:
            for inp in frontmatter['inputs']:
                inputs.append(SkillInput(
                    name=inp.get('name', 'input'),
                    type=inp.get('type', 'string'),
                    required=inp.get('required', True),
                    description=inp.get('description'),
                    default=inp.get('default')
                ))

        if 'outputs' in frontmatter:
            for out in frontmatter['outputs']:
                outputs.append(SkillOutput(
                    name=out.get('name', 'output'),
                    type=out.get('type', 'string'),
                    description=out.get('description')
                ))

        # Get triggers from activation_keywords
        triggers = frontmatter.get('activation_keywords', [])
        if isinstance(triggers, str):
            triggers = [triggers]

        skill_id = frontmatter.get('name', file_path.parent.name)

        return Skill(
            id=skill_id,
            name=skill_id,
            display_name=frontmatter.get('display_name', frontmatter.get('name', file_path.parent.name)),
            version=str(frontmatter.get('version', '1.0.0')),
            category=category,
            description=frontmatter.get('description', '').strip()[:200],
            author=frontmatter.get('author', 'Leo AI System'),
            status='active' if frontmatter.get('user-invocable', True) else 'inactive',
            triggers=triggers,
            inputs=inputs,
            outputs=outputs,
            created_at=created_at,
            updated_at=updated_at
        )
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return None


def load_all_skills() -> List[Skill]:
    """Load all skills from the skills directory."""
    skills = []
    if not SKILLS_DIR.exists():
        return skills

    for skill_md in SKILLS_DIR.rglob("SKILL.md"):
        skill = parse_skill_md(skill_md)
        if skill:
            skills.append(skill)

    return skills


def load_all_agents() -> List[Agent]:
    """Load agents from capability index or AGENT.md files."""
    agents = []

    # Try to find AGENT.md files
    agents_dir = project_root / "src" / "leo_agents"
    if agents_dir.exists():
        for agent_md in agents_dir.rglob("AGENT.md"):
            try:
                content = agent_md.read_text(encoding='utf-8')
                match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
                if match:
                    frontmatter = yaml.safe_load(match.group(1))
                    agent_name = agent_md.parent.name

                    stat = agent_md.stat()
                    created_at = datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d')
                    updated_at = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d')

                    agents.append(Agent(
                        id=agent_name,
                        name=agent_name,
                        display_name=frontmatter.get('display_name', agent_name),
                        description=frontmatter.get('description', ''),
                        role=frontmatter.get('role', 'assistant'),
                        capabilities=frontmatter.get('capabilities', []),
                        skills=frontmatter.get('skills', []),
                        status='active',
                        created_at=created_at,
                        updated_at=updated_at
                    ))
            except Exception as e:
                print(f"Error parsing agent {agent_md}: {e}")

    # If no agents found from files, use default list from capability_index
    if not agents:
        default_agents = [
            {"name": "research_agent", "display_name": "研究员", "role": "researcher", "description": "擅长深度研究和信息收集"},
            {"name": "creative_agent", "display_name": "创意设计师", "role": "creator", "description": "专注于内容创作和设计"},
            {"name": "analysis_agent", "display_name": "数据分析师", "role": "analyst", "description": "擅长数据分析和洞察提取"},
            {"name": "architect_agent", "display_name": "系统架构师", "role": "architect", "description": "负责系统设计和架构规划"},
            {"name": "product_manager_agent", "display_name": "产品经理", "role": "product", "description": "产品规划和需求分析"},
            {"name": "realestate_agent", "display_name": "房产顾问", "role": "realestate", "description": "房产市场分析和咨询"},
            {"name": "mobile_agent", "display_name": "移动端开发", "role": "mobile_dev", "description": "移动端应用开发"},
        ]

        for agent_data in default_agents:
            agents.append(Agent(
                id=agent_data["name"],
                name=agent_data["name"],
                display_name=agent_data["display_name"],
                description=agent_data["description"],
                role=agent_data["role"],
                capabilities=[],
                skills=[],
                status='active',
                created_at='2024-01-01',
                updated_at='2024-02-01'
            ))

    return agents


def load_all_workflows() -> List[Workflow]:
    """Load workflows from definitions directory."""
    workflows = []

    if not WORKFLOWS_DIR.exists():
        return workflows

    for wf_file in WORKFLOWS_DIR.glob("*.yaml"):
        try:
            content = wf_file.read_text(encoding='utf-8')
            data = yaml.safe_load(content)

            if not data:
                continue

            stat = wf_file.stat()
            created_at = datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d')
            updated_at = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d')

            # Parse steps
            steps = []
            for step_data in data.get('steps', []):
                step = WorkflowStep(
                    name=step_data.get('name', 'unnamed'),
                    type=step_data.get('type', 'sequential'),
                    agent=step_data.get('agent'),
                    skill=step_data.get('skill'),
                    retries=step_data.get('retries'),
                    timeout=step_data.get('timeout'),
                    parallel_steps=step_data.get('parallel_steps')
                )
                steps.append(step)

            # Parse inputs
            inputs = []
            for inp_name, inp_data in data.get('inputs', {}).items():
                if isinstance(inp_data, dict):
                    inputs.append(WorkflowInput(
                        name=inp_name,
                        type=inp_data.get('type', 'string'),
                        required=inp_data.get('required', False),
                        description=inp_data.get('description')
                    ))

            wf_id = data.get('name', wf_file.stem)

            workflows.append(Workflow(
                id=wf_id,
                name=wf_id,
                display_name=data.get('display_name', data.get('name', wf_file.stem)),
                version=str(data.get('version', '1.0.0')),
                description=data.get('description', ''),
                status='active',
                steps=steps,
                inputs=inputs,
                created_at=created_at,
                updated_at=updated_at
            ))
        except Exception as e:
            print(f"Error parsing workflow {wf_file}: {e}")

    return workflows


def load_memory_entries() -> List[MemoryEntry]:
    """Load memory entries from shared_memory.md."""
    entries = []

    if not MEMORY_FILE.exists():
        return entries

    try:
        content = MEMORY_FILE.read_text(encoding='utf-8')

        # Parse memory entries (simple format: key: value)
        current_category = 'general'
        for line in content.split('\n'):
            line = line.strip()

            # Check for category headers
            if line.startswith('# ') or line.startswith('## '):
                category_map = {
                    '系统': 'system',
                    '用户': 'user_profile',
                    '项目': 'project',
                    '配置': 'config'
                }
                for cn, en in category_map.items():
                    if cn in line:
                        current_category = en
                        break

            # Parse key-value entries
            if line.startswith('- ') and ':' in line:
                parts = line[2:].split(':', 1)
                if len(parts) == 2:
                    key = parts[0].strip()
                    value = parts[1].strip()

                    entries.append(MemoryEntry(
                        id=key,
                        key=key,
                        value=value,
                        category=current_category,
                        importance=3,
                        created_at='2024-01-01',
                        updated_at='2024-01-01'
                    ))
    except Exception as e:
        print(f"Error loading memory: {e}")

    return entries


# ===== Cache =====
_skills_cache: Optional[List[Skill]] = None
_agents_cache: Optional[List[Agent]] = None
_workflows_cache: Optional[List[Workflow]] = None

def refresh_cache():
    """Refresh all data caches."""
    global _skills_cache, _agents_cache, _workflows_cache
    _skills_cache = None
    _agents_cache = None
    _workflows_cache = None


# ===== API Routes =====

@app.get("/")
async def root():
    return {"message": "Leo AI System API", "version": "1.0.0", "connected": True}


@app.post("/api/system/reload")
async def reload_system():
    """Reload all data from filesystem."""
    refresh_cache()
    return ApiResponse(success=True, message="System data reloaded")


@app.post("/api/v2/execute", response_model=LeoResponse)
async def execute_unified(request: LeoRequest):
    """统一执行入口。"""
    api = get_leo_api()
    try:
        routing = api.registry.intent_recognizer.route(request.intent)
        if routing["action"] == "delegate_to_agent":
            result = api.run_agent(routing["target"], request.intent)
        elif routing["action"] == "call_skill":
            result = api.call(routing["target"], "execute", **request.params)
        else:
            result = {"message": routing.get("response", "未识别的意图")}
        return LeoResponse(
            trace_id=request.trace_id,
            status="ok",
            intent=routing.get("intent_type"),
            target=routing.get("target"),
            data=result,
            message="执行成功",
        )
    except Exception as e:
        return LeoResponse(
            trace_id=request.trace_id,
            status="error",
            error_code=ErrorCode.E_INTERNAL,
            message=str(e),
        )


# ===== Skills API =====

@app.get("/api/skills", response_model=ApiResponse)
async def get_skills(category: Optional[str] = None):
    global _skills_cache
    if _skills_cache is None:
        _skills_cache = load_all_skills()

    skills = _skills_cache
    if category:
        skills = [s for s in skills if category in s.category]

    return ApiResponse(success=True, data=[s.dict() for s in skills])


@app.get("/api/skills/{skill_id}", response_model=ApiResponse)
async def get_skill(skill_id: str):
    global _skills_cache
    if _skills_cache is None:
        _skills_cache = load_all_skills()

    skill = next((s for s in _skills_cache if s.id == skill_id), None)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return ApiResponse(success=True, data=skill.dict())


@app.post("/api/skills", response_model=ApiResponse)
async def create_skill(skill: Skill):
    """创建新技能：生成目录结构和 SKILL.md"""
    global _skills_cache
    try:
        skill_dir = SKILLS_DIR / skill.category / f"{skill.name}_skill"
        if skill_dir.exists():
            raise HTTPException(status_code=409, detail=f"Skill '{skill.name}' already exists")

        # 创建目录结构
        skill_dir.mkdir(parents=True, exist_ok=True)
        (skill_dir / "scripts").mkdir(exist_ok=True)
        (skill_dir / "config").mkdir(exist_ok=True)

        # 生成 SKILL.md
        skill_md = f"""---
name: {skill.name}
version: "{skill.version}"
description: {skill.description}
category: {skill.category}
author: {skill.author}
triggers: {skill.triggers}
---

# {skill.display_name}

{skill.description}
"""
        (skill_dir / "SKILL.md").write_text(skill_md, encoding="utf-8")
        (skill_dir / "__init__.py").write_text(f"# {skill.display_name}\n", encoding="utf-8")
        (skill_dir / "scripts" / "main.py").write_text(
            f'#!/usr/bin/env python3\n"""{skill.display_name}"""\n\ndef execute(**kwargs):\n    pass\n',
            encoding="utf-8"
        )

        _skills_cache = None  # 清除缓存
        return ApiResponse(success=True, data=skill.dict(), message=f"Skill '{skill.name}' created")
    except HTTPException:
        raise
    except Exception as e:
        return ApiResponse(success=False, error=str(e))


@app.put("/api/skills/{skill_id}", response_model=ApiResponse)
async def update_skill(skill_id: str, skill: Skill):
    """更新技能的 SKILL.md 内容"""
    global _skills_cache
    try:
        # 查找技能目录
        skill_path = find_skill_module(skill_id)
        if not skill_path:
            raise HTTPException(status_code=404, detail=f"Skill '{skill_id}' not found")

        skill_dir = skill_path.parent if skill_path.is_file() else skill_path
        skill_md_path = skill_dir / "SKILL.md"

        if skill_md_path.exists():
            skill_md = f"""---
name: {skill.name}
version: "{skill.version}"
description: {skill.description}
category: {skill.category}
author: {skill.author}
triggers: {skill.triggers}
---

# {skill.display_name}

{skill.description}
"""
            skill_md_path.write_text(skill_md, encoding="utf-8")

        _skills_cache = None
        return ApiResponse(success=True, data=skill.dict(), message=f"Skill '{skill_id}' updated")
    except HTTPException:
        raise
    except Exception as e:
        return ApiResponse(success=False, error=str(e))


@app.delete("/api/skills/{skill_id}", response_model=ApiResponse)
async def delete_skill(skill_id: str):
    """删除技能目录"""
    global _skills_cache
    try:
        skill_path = find_skill_module(skill_id)
        if not skill_path:
            raise HTTPException(status_code=404, detail=f"Skill '{skill_id}' not found")

        skill_dir = skill_path.parent if skill_path.is_file() else skill_path
        import shutil
        shutil.rmtree(skill_dir)

        _skills_cache = None
        return ApiResponse(success=True, message=f"Skill '{skill_id}' deleted")
    except HTTPException:
        raise
    except Exception as e:
        return ApiResponse(success=False, error=str(e))


class SkillExecuteRequest(BaseModel):
    method: str = "execute"
    params: Dict[str, Any] = {}


class WorkflowExecuteRequest(BaseModel):
    inputs: Dict[str, Any] = {}


def find_skill_module(skill_id: str) -> Optional[Path]:
    """Find the skill module path by skill_id."""
    # Generate possible directory names from skill_id
    # e.g., "fresh-start" -> ["fresh-start", "fresh_start", "fresh_start_skill"]
    possible_names = [
        skill_id,
        skill_id.replace("-", "_"),
        skill_id.replace("-", "_") + "_skill",
        skill_id + "_skill",
    ]

    # Search for skill directory
    for skill_dir in SKILLS_DIR.rglob("*"):
        if skill_dir.is_dir() and skill_dir.name in possible_names:
            # Look for main skill file with various naming patterns
            for name in possible_names:
                skill_file = skill_dir / f"{name}.py"
                if skill_file.exists():
                    return skill_file
            # Also try the directory name itself
            skill_file = skill_dir / f"{skill_dir.name}.py"
            if skill_file.exists():
                return skill_file
    return None


def get_skill_class(skill_path: Path):
    """Dynamically import and return the skill class."""
    import importlib.util

    spec = importlib.util.spec_from_file_location("skill_module", skill_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["skill_module"] = module
    spec.loader.exec_module(module)

    # Find the skill class (class ending with 'Skill')
    for name in dir(module):
        obj = getattr(module, name)
        if isinstance(obj, type) and name.endswith('Skill') and name != 'EvolvableSkill':
            return obj
    return None


@app.get("/api/skills/{skill_id}/methods", response_model=ApiResponse)
async def get_skill_methods(skill_id: str):
    """Get available methods for a skill."""
    try:
        skill_path = find_skill_module(skill_id)
        if not skill_path:
            raise HTTPException(status_code=404, detail=f"Skill {skill_id} not found")

        skill_class = get_skill_class(skill_path)
        if not skill_class:
            raise HTTPException(status_code=404, detail=f"Skill class not found in {skill_id}")

        # Get public methods
        methods = []
        for name in dir(skill_class):
            if not name.startswith('_') and callable(getattr(skill_class, name, None)):
                method = getattr(skill_class, name)
                if hasattr(method, '__func__'):
                    method = method.__func__

                # Get method signature
                import inspect
                try:
                    sig = inspect.signature(method)
                    params = []
                    for param_name, param in sig.parameters.items():
                        if param_name == 'self':
                            continue
                        param_info = {
                            "name": param_name,
                            "required": param.default == inspect.Parameter.empty,
                            "default": None if param.default == inspect.Parameter.empty else str(param.default),
                            "type": str(param.annotation) if param.annotation != inspect.Parameter.empty else "any"
                        }
                        params.append(param_info)

                    methods.append({
                        "name": name,
                        "doc": method.__doc__ or "",
                        "params": params
                    })
                except (ValueError, TypeError):
                    pass

        return ApiResponse(success=True, data=methods)
    except HTTPException:
        raise
    except Exception as e:
        return ApiResponse(success=False, error=str(e))


@app.post("/api/skills/{skill_id}/execute", response_model=ApiResponse)
async def execute_skill(skill_id: str, request: SkillExecuteRequest):
    """Execute a skill method with the given parameters."""
    try:
        skill_path = find_skill_module(skill_id)
        if not skill_path:
            raise HTTPException(status_code=404, detail=f"Skill {skill_id} not found")

        skill_class = get_skill_class(skill_path)
        if not skill_class:
            raise HTTPException(status_code=404, detail=f"Skill class not found in {skill_id}")

        # Instantiate skill
        skill_instance = skill_class()

        # Get method
        method_name = request.method
        if not hasattr(skill_instance, method_name):
            raise HTTPException(status_code=400, detail=f"Method {method_name} not found in skill {skill_id}")

        method = getattr(skill_instance, method_name)
        if not callable(method):
            raise HTTPException(status_code=400, detail=f"{method_name} is not callable")

        # Execute method
        import asyncio
        if asyncio.iscoroutinefunction(method):
            result = await method(**request.params)
        else:
            result = method(**request.params)

        return ApiResponse(
            success=True,
            data={"result": result, "skill_id": skill_id, "method": method_name},
            message=f"Executed {skill_id}.{method_name} successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        return ApiResponse(
            success=False,
            error=str(e),
            data={"traceback": traceback.format_exc()},
            message=f"Execution failed: {str(e)}"
        )


# ===== Agents API =====

@app.get("/api/agents", response_model=ApiResponse)
async def get_agents():
    global _agents_cache
    if _agents_cache is None:
        _agents_cache = load_all_agents()

    return ApiResponse(success=True, data=[a.dict() for a in _agents_cache])


@app.get("/api/agents/{agent_id}", response_model=ApiResponse)
async def get_agent(agent_id: str):
    global _agents_cache
    if _agents_cache is None:
        _agents_cache = load_all_agents()

    agent = next((a for a in _agents_cache if a.id == agent_id), None)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return ApiResponse(success=True, data=agent.dict())


@app.post("/api/agents", response_model=ApiResponse)
async def create_agent(agent: Agent):
    return ApiResponse(success=True, data=agent.dict(), message="Agent created (mock)")


@app.put("/api/agents/{agent_id}", response_model=ApiResponse)
async def update_agent(agent_id: str, agent: Agent):
    return ApiResponse(success=True, data=agent.dict(), message="Agent updated (mock)")


@app.delete("/api/agents/{agent_id}", response_model=ApiResponse)
async def delete_agent(agent_id: str):
    return ApiResponse(success=True, message="Agent deleted (mock)")


class AgentExecuteRequest(BaseModel):
    message: str


@app.post("/api/agents/{agent_id}/execute", response_model=ApiResponse)
async def execute_agent(agent_id: str, request: AgentExecuteRequest, db: Session = Depends(get_db)):
    """Execute an agent with the given message using real AI."""
    import time
    start_time = time.time()

    try:
        global _agents_cache
        if _agents_cache is None:
            _agents_cache = load_all_agents()

        agent = next((a for a in _agents_cache if a.id == agent_id), None)
        if not agent:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")

        # Get intent recognition for context
        from leo_orchestrator.intent_recognizer import get_intent_recognizer
        recognizer = get_intent_recognizer()
        intent_match = recognizer.recognize(request.message)

        # Use real AI to generate response
        try:
            agent_engine = get_agent_engine()
            ai_result = await agent_engine.execute(
                agent_type=agent_id,
                user_message=request.message
            )
            response_text = ai_result["response"]
            status = ai_result["status"]
        except Exception as ai_error:
            # Fallback if AI service is not available
            import traceback
            tb_str = traceback.format_exc()
            print(f"AI service error: {ai_error}")
            print(f"Traceback: {tb_str}")
            response_text = f"AI服务错误: {ai_error}\n\nTraceback:\n{tb_str}\n\n原始请求：{request.message}"
            status = "error"

        execution_time = int((time.time() - start_time) * 1000)

        result = {
            "response": response_text,
            "agent": agent_id,
            "agent_name": agent.display_name,
            "role": agent.role,
            "task": request.message,
            "intent": {
                "type": intent_match.intent_type,
                "target": intent_match.target,
                "confidence": intent_match.confidence
            },
            "execution_time_ms": execution_time,
            "capabilities_used": agent.capabilities[:3] if agent.capabilities else [],
            "status": status
        }

        # Save execution log to database
        log_entry = ExecutionLogDB(
            task_type="agent",
            task_name=agent_id,
            status=status,
            input_data={"message": request.message},
            output_data={"response": response_text[:500]},  # Truncate for storage
            execution_time_ms=execution_time
        )
        db.add(log_entry)
        db.commit()

        return ApiResponse(
            success=True,
            data=result,
            message=f"Agent {agent.display_name} 执行成功"
        )
    except HTTPException:
        raise
    except Exception as e:
        return ApiResponse(
            success=False,
            error=str(e),
            message=f"Agent execution failed: {str(e)}"
        )


# ===== Workflows API =====

@app.get("/api/workflows", response_model=ApiResponse)
async def get_workflows():
    global _workflows_cache
    if _workflows_cache is None:
        _workflows_cache = load_all_workflows()

    return ApiResponse(success=True, data=[w.dict() for w in _workflows_cache])


@app.get("/api/workflows/{workflow_id}", response_model=ApiResponse)
async def get_workflow(workflow_id: str):
    global _workflows_cache
    if _workflows_cache is None:
        _workflows_cache = load_all_workflows()

    workflow = next((w for w in _workflows_cache if w.id == workflow_id), None)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return ApiResponse(success=True, data=workflow.dict())


@app.post("/api/workflows", response_model=ApiResponse)
async def create_workflow(workflow: Workflow):
    return ApiResponse(success=True, data=workflow.dict(), message="Workflow created (mock)")


@app.put("/api/workflows/{workflow_id}", response_model=ApiResponse)
async def update_workflow(workflow_id: str, workflow: Workflow):
    return ApiResponse(success=True, data=workflow.dict(), message="Workflow updated (mock)")


@app.delete("/api/workflows/{workflow_id}", response_model=ApiResponse)
async def delete_workflow(workflow_id: str):
    return ApiResponse(success=True, message="Workflow deleted (mock)")


@app.post("/api/workflows/{workflow_id}/execute", response_model=ApiResponse)
async def execute_workflow(workflow_id: str, request: WorkflowExecuteRequest):
    """Execute a workflow with the given inputs."""
    try:
        # Try multiple file name variations
        possible_names = [
            workflow_id,
            workflow_id.replace("-", "_"),
            workflow_id.replace("_", "-"),
        ]

        workflow_file = None
        for name in possible_names:
            candidate = WORKFLOWS_DIR / f"{name}.yaml"
            if candidate.exists():
                workflow_file = candidate
                break

        if not workflow_file:
            raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")

        # Load workflow definition
        with open(workflow_file, 'r', encoding='utf-8') as f:
            workflow_def = yaml.safe_load(f)

        # For now, return a simulated execution result
        # Real execution would require instantiated agents
        steps = workflow_def.get('steps', [])
        step_results = []
        for i, step in enumerate(steps):
            step_results.append({
                "step": step.get('name', f'step_{i+1}'),
                "type": step.get('type', 'sequential'),
                "agent": step.get('agent', 'unknown'),
                "status": "simulated",
                "message": f"步骤 {step.get('name')} 模拟执行完成"
            })

        result = {
            "workflow": workflow_id,
            "inputs": request.inputs,
            "total_steps": len(steps),
            "step_results": step_results,
            "status": "simulated",
            "message": "工作流模拟执行完成（实际执行需要配置 Agent 实例）"
        }

        return ApiResponse(success=True, data=result, message="Workflow execution simulated")
    except Exception as e:
        return ApiResponse(success=False, error=str(e), message=f"Execution failed: {str(e)}")


@app.post("/api/workflows/validate", response_model=ApiResponse)
async def validate_workflow(data: Dict[str, str]):
    """Validate workflow YAML content."""
    try:
        yaml_content = data.get('yaml', '')
        yaml.safe_load(yaml_content)
        return ApiResponse(success=True, data={"valid": True})
    except yaml.YAMLError as e:
        return ApiResponse(success=True, data={"valid": False, "errors": [str(e)]})


# ===== Memory API =====

@app.get("/api/memory", response_model=ApiResponse)
async def get_memory(category: Optional[str] = None):
    entries = load_memory_entries()

    if category:
        entries = [e for e in entries if e.category == category]

    return ApiResponse(success=True, data=[e.dict() for e in entries])


@app.get("/api/memory/search", response_model=ApiResponse)
async def search_memory(q: str):
    entries = load_memory_entries()
    results = [e for e in entries if q.lower() in e.key.lower() or q.lower() in e.value.lower()]
    return ApiResponse(success=True, data=[r.dict() for r in results])


@app.get("/api/memory/stats", response_model=ApiResponse)
async def get_memory_stats():
    entries = load_memory_entries()
    categories = {}
    by_importance = {}

    for e in entries:
        categories[e.category] = categories.get(e.category, 0) + 1
        by_importance[e.importance] = by_importance.get(e.importance, 0) + 1

    stats = MemoryStats(
        total_entries=len(entries),
        categories=categories,
        by_importance=by_importance
    )
    return ApiResponse(success=True, data=stats.dict())


@app.get("/api/memory/{key}", response_model=ApiResponse)
async def get_memory_entry(key: str):
    entries = load_memory_entries()
    entry = next((e for e in entries if e.key == key), None)
    if not entry:
        raise HTTPException(status_code=404, detail="Memory entry not found")
    return ApiResponse(success=True, data=entry.dict())


@app.post("/api/memory", response_model=ApiResponse)
async def create_memory_entry(entry: MemoryEntry):
    """Create a new memory entry in shared_memory.md."""
    try:
        # Append to memory file
        with open(MEMORY_FILE, 'a', encoding='utf-8') as f:
            f.write(f"\n- {entry.key}: {entry.value}\n")
        return ApiResponse(success=True, data=entry.dict(), message="Memory entry created")
    except Exception as e:
        return ApiResponse(success=False, error=str(e))


@app.put("/api/memory/{key}", response_model=ApiResponse)
async def update_memory_entry(key: str, entry: MemoryEntry):
    return ApiResponse(success=True, data=entry.dict(), message="Memory entry updated (mock)")


@app.delete("/api/memory/{key}", response_model=ApiResponse)
async def delete_memory_entry(key: str):
    return ApiResponse(success=True, message="Memory entry deleted (mock)")


@app.post("/api/memory/cleanup", response_model=ApiResponse)
async def cleanup_memory():
    """Clean up expired memory entries."""
    return ApiResponse(success=True, data={"removed": 0}, message="Cleanup completed")


# ===== Intent API =====

@app.post("/api/intent/recognize", response_model=ApiResponse)
async def recognize_intent(data: Dict[str, str]):
    """Recognize intent using the real intent recognizer."""
    try:
        from leo_orchestrator.intent_recognizer import get_intent_recognizer

        text = data.get("text", "")
        recognizer = get_intent_recognizer()
        match = recognizer.recognize(text)

        return ApiResponse(success=True, data={
            "intent_type": match.intent_type,
            "target": match.target,
            "confidence": match.confidence,
            "params": match.params,
            "alternatives": [{"target": a.target, "confidence": a.confidence} for a in match.alternatives]
        })
    except Exception as e:
        # Fallback to simple keyword matching
        text = data.get("text", "").lower()

        # Simple keyword matching
        if "研究" in text or "调查" in text or "调研" in text:
            intent_type, target, confidence = "agent", "research_agent", 0.9
        elif "搜索" in text or "查找" in text:
            intent_type, target, confidence = "skill", "web_search_skill", 0.85
        elif "分析" in text or "数据分析" in text or "统计" in text:
            intent_type, target, confidence = "agent", "analysis_agent", 0.88
        elif "创建" in text or "生成" in text or "制作" in text:
            intent_type, target, confidence = "agent", "creative_agent", 0.82
        elif "工作流" in text or "流程" in text or "pipeline" in text:
            intent_type, target, confidence = "workflow", "content_pipeline", 0.8
        elif "视频号" in text or "账号监测" in text or "监测" in text:
            intent_type, target, confidence = "skill", "video_monitor", 0.88
        elif "开发" in text or "编程" in text or "代码" in text:
            intent_type, target, confidence = "agent", "mobile_agent", 0.85
        else:
            # 对于其他查询，默认使用 research_agent 处理
            intent_type, target, confidence = "agent", "research_agent", 0.6

        return ApiResponse(success=True, data={
            "intent_type": intent_type,
            "target": target,
            "confidence": confidence,
            "params": {"query": text},
            "alternatives": []
        })


@app.post("/api/intent/route", response_model=ApiResponse)
async def route_intent(data: Dict[str, str]):
    """Get routing decision for the input text."""
    try:
        from leo_orchestrator.intent_recognizer import get_intent_recognizer

        text = data.get("text", "")
        recognizer = get_intent_recognizer()
        routing = recognizer.route(text)

        return ApiResponse(success=True, data=routing)
    except Exception as e:
        # Fallback
        text = data.get("text", "").lower()

        if "研究" in text or "调查" in text:
            action, target = "delegate_to_agent", "research_agent"
        elif "搜索" in text or "查找" in text:
            action, target = "execute_skill", "web_search_skill"
        else:
            action, target = "chat", "default"

        return ApiResponse(success=True, data={
            "action": action,
            "target": target,
            "params": {"query": text}
        })


@app.post("/api/intent/test", response_model=ApiResponse)
async def test_intent(data: Dict[str, str]):
    """Test intent recognition with full details."""
    import time
    start = time.time()

    text = data.get("text", "")

    # Get recognition result
    recognize_result = await recognize_intent(data)
    route_result = await route_intent(data)

    execution_time = int((time.time() - start) * 1000)

    result = {
        "input": text,
        "match": recognize_result.data,
        "routing": route_result.data,
        "execution_time_ms": execution_time
    }

    return ApiResponse(success=True, data=result)


# ===== System API =====

@app.get("/api/system/stats", response_model=ApiResponse)
async def get_system_stats():
    skills = load_all_skills()
    agents = load_all_agents()
    workflows = load_all_workflows()
    memory_entries = load_memory_entries()

    stats = SystemStats(
        total_skills=len(skills),
        total_agents=len(agents),
        total_workflows=len(workflows),
        active_tasks=3,  # Placeholder
        memory_entries=len(memory_entries),
        uptime_hours=168  # Placeholder
    )
    return ApiResponse(success=True, data=stats.dict())


@app.get("/api/system/category-stats", response_model=ApiResponse)
async def get_category_stats():
    skills = load_all_skills()

    # Count by category
    category_counts = {}
    for skill in skills:
        cat = skill.category.split('/')[0] if '/' in skill.category else skill.category
        category_counts[cat] = category_counts.get(cat, 0) + 1

    # Map to labels
    category_labels = {
        'automation': '自动化',
        'backend': '后端',
        'business': '业务',
        'collaboration': '协作',
        'content_creation': '内容创作',
        'core': '核心',
        'debugging': '调试',
        'development': '开发',
        'devops': '运维',
        'frontend': '前端',
        'intelligence': '智能',
        'uncategorized': '未分类'
    }

    categories = [
        CategoryStats(category=k, count=v, label=category_labels.get(k, k))
        for k, v in sorted(category_counts.items(), key=lambda x: -x[1])
    ]

    return ApiResponse(success=True, data=[c.dict() for c in categories])


@app.get("/api/system/health", response_model=ApiResponse)
async def get_health():
    return ApiResponse(success=True, data={"status": "healthy", "uptime": 168 * 3600})


# ===== Conversation API =====

class ConversationCreate(BaseModel):
    title: Optional[str] = "新对话"


class ConversationUpdate(BaseModel):
    messages: List[Dict[str, Any]]


@app.get("/api/conversations", response_model=ApiResponse)
async def get_conversations(db: Session = Depends(get_db)):
    """获取所有对话历史"""
    conversations = db.query(ConversationDB).order_by(ConversationDB.updated_at.desc()).all()
    return ApiResponse(success=True, data=[conv.to_dict() for conv in conversations])


@app.post("/api/conversations", response_model=ApiResponse)
async def create_conversation(request: ConversationCreate, db: Session = Depends(get_db)):
    """创建新对话"""
    conversation = ConversationDB(title=request.title)
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return ApiResponse(success=True, data=conversation.to_dict(), message="对话创建成功")


@app.get("/api/conversations/{conversation_id}", response_model=ApiResponse)
async def get_conversation(conversation_id: int, db: Session = Depends(get_db)):
    """获取单个对话详情"""
    conversation = db.query(ConversationDB).filter(ConversationDB.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="对话不存在")
    return ApiResponse(success=True, data=conversation.to_dict())


@app.put("/api/conversations/{conversation_id}", response_model=ApiResponse)
async def update_conversation(conversation_id: int, request: ConversationUpdate, db: Session = Depends(get_db)):
    """更新对话消息"""
    conversation = db.query(ConversationDB).filter(ConversationDB.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="对话不存在")

    # 删除旧消息
    db.query(MessageDB).filter(MessageDB.conversation_id == conversation_id).delete()

    # 添加新消息
    for msg in request.messages:
        message = MessageDB(
            conversation_id=conversation_id,
            role=msg.get("type", "system"),
            content=msg.get("content", ""),
            metadata_json=msg.get("metadata", {})
        )
        db.add(message)

    # 更新标题
    for msg in request.messages:
        if msg.get("type") == "user":
            content = msg.get("content", "")[:20]
            conversation.title = content + ("..." if len(msg.get("content", "")) > 20 else "")
            break

    conversation.updated_at = datetime.utcnow()
    db.commit()

    return ApiResponse(success=True, data=conversation.to_dict(), message="对话更新成功")


@app.delete("/api/conversations/{conversation_id}", response_model=ApiResponse)
async def delete_conversation(conversation_id: int, db: Session = Depends(get_db)):
    """删除对话"""
    conversation = db.query(ConversationDB).filter(ConversationDB.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="对话不存在")

    db.delete(conversation)
    db.commit()

    return ApiResponse(success=True, message="对话删除成功")


# ===== Database Initialization =====

@app.on_event("startup")
async def startup_event():
    """应用启动时初始化数据库"""
    print("正在初始化数据库...")
    init_db()
    print("数据库初始化完成")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
