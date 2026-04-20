"""Leo Web v2 API (clean implementation)."""

from __future__ import annotations

import os
import re
import sys
import uuid
import logging
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from collections import defaultdict, deque

import yaml
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException, Request, Response, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

try:
    from .leo_api_adapter import get_leo_api
    from .schemas import ErrorCode, LeoRequest, LeoResponse
except ImportError:
    from leo_api_adapter import get_leo_api
    from schemas import ErrorCode, LeoRequest, LeoResponse

load_dotenv()

project_root = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

logger = logging.getLogger('leo_web_api')

app = FastAPI(
    title='Leo AI System API',
    description='Backend API for Leo Web v2',
    version='2.0.0',
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5173', 'http://127.0.0.1:5173'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.middleware('http')
async def request_context_middleware(request: Request, call_next):
    request_id = request.headers.get('x-request-id') or str(uuid.uuid4())[:8]
    request.state.request_id = request_id
    started = time.time()
    response: Response = await call_next(request)
    response.headers['X-Request-ID'] = request_id
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Referrer-Policy'] = 'same-origin'
    response.headers['X-Response-Time-Ms'] = str(int((time.time() - started) * 1000))
    return response


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception('Unhandled error: %s', request.url.path)
    request_id = getattr(request.state, 'request_id', str(uuid.uuid4())[:8])
    return JSONResponse(
        status_code=500,
        content=ApiResponse(success=False, error='Internal server error', data={'request_id': request_id}).model_dump(),
    )

SKILLS_DIR = project_root / 'src' / 'leo_skills'
WORKFLOWS_DIR = project_root / 'src' / 'leo_workflows' / 'definitions'
SUBAGENTS_DIR = project_root / 'src' / 'leo_subagents' / 'agents'
MEMORY_FILE = project_root / 'leo_knowledge' / 'context' / 'shared_memory.md'

WRITE_TOKEN_ENV = 'LEO_WEB_API_TOKEN'
SAFE_SEGMENT_PATTERN = re.compile(r'^[a-z0-9_]+$')
AUDIT_LOG_FILE = project_root / 'logs' / 'web_api_audit.jsonl'
STARTED_AT = time.time()
RATE_LIMIT_WRITE_PER_MIN = int(os.getenv('LEO_WEB_RATE_LIMIT_WRITE_PER_MIN', '60'))
RATE_LIMIT_EXECUTE_PER_MIN = int(os.getenv('LEO_WEB_RATE_LIMIT_EXECUTE_PER_MIN', '120'))
READ_TOKEN_REQUIRED = os.getenv('LEO_WEB_API_REQUIRE_READ_TOKEN', 'false').lower() in ('1', 'true', 'yes')
ROLE_SCOPES: Dict[str, set[str]] = {
    'admin': {'read', 'write', 'execute', 'admin'},
    'operator': {'read', 'write', 'execute'},
    'executor': {'read', 'execute'},
    'viewer': {'read'},
}
RATE_BUCKETS: Dict[str, deque[float]] = defaultdict(deque)


class SkillInput(BaseModel):
    name: str
    type: str = 'string'
    required: bool = False
    description: Optional[str] = None
    default: Optional[Any] = None


class SkillOutput(BaseModel):
    name: str
    type: str = 'string'
    description: Optional[str] = None


class Skill(BaseModel):
    id: str
    name: str
    display_name: str
    version: str
    category: str
    description: str
    author: str
    status: str = 'active'
    triggers: List[str] = Field(default_factory=list)
    inputs: List[SkillInput] = Field(default_factory=list)
    outputs: List[SkillOutput] = Field(default_factory=list)
    created_at: str
    updated_at: str


class Agent(BaseModel):
    id: str
    name: str
    display_name: str
    description: str
    role: str = 'assistant'
    capabilities: List[str] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    status: str = 'active'
    created_at: str
    updated_at: str


class Workflow(BaseModel):
    id: str
    name: str
    display_name: str
    version: str
    description: str
    status: str = 'active'
    steps: List[Dict[str, Any]] = Field(default_factory=list)
    inputs: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: str
    updated_at: str


class MemoryEntry(BaseModel):
    id: str
    key: str
    value: str
    category: str
    importance: int = 3
    created_at: str
    updated_at: str
    expires_at: Optional[str] = None


class MemoryStats(BaseModel):
    total_entries: int
    categories: Dict[str, int]
    by_importance: Dict[int, int]


class ApiResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    message: Optional[str] = None


class AuthContext(BaseModel):
    principal: str
    role: str
    scopes: List[str]


class SkillExecuteRequest(BaseModel):
    method: str = 'execute'
    params: Dict[str, Any] = Field(default_factory=dict)


class AgentExecuteRequest(BaseModel):
    message: str


class WorkflowExecuteRequest(BaseModel):
    inputs: Dict[str, Any] = Field(default_factory=dict)


class ConversationCreate(BaseModel):
    title: str = '新对话'


class ConversationUpdate(BaseModel):
    messages: List[Dict[str, Any]]


CONVERSATIONS: Dict[int, Dict[str, Any]] = {}
CONVERSATION_SEQ = 0


# -------- security --------
def _load_token_registry() -> Dict[str, Dict[str, str]]:
    raw = os.getenv('LEO_WEB_API_TOKENS', '').strip()
    registry: Dict[str, Dict[str, str]] = {}
    if raw:
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, dict):
                for token, role in parsed.items():
                    if isinstance(token, str) and isinstance(role, str):
                        registry[token] = {'role': role, 'principal': role}
            elif isinstance(parsed, list):
                for item in parsed:
                    if isinstance(item, dict) and isinstance(item.get('token'), str):
                        registry[item['token']] = {
                            'role': str(item.get('role', 'viewer')),
                            'principal': str(item.get('principal', item.get('role', 'viewer'))),
                        }
        except Exception:
            logger.exception('Invalid LEO_WEB_API_TOKENS JSON')

    fallback = os.getenv(WRITE_TOKEN_ENV, '').strip()
    if fallback and fallback not in registry:
        registry[fallback] = {'role': 'admin', 'principal': 'legacy-admin-token'}
    return registry


def _extract_token(authorization: Optional[str], x_api_key: Optional[str]) -> Optional[str]:
    if x_api_key:
        return x_api_key.strip()
    if authorization and authorization.lower().startswith('bearer '):
        return authorization[7:].strip()
    return None


def _auth_context(
    authorization: Optional[str] = Header(default=None),
    x_api_key: Optional[str] = Header(default=None),
) -> AuthContext:
    registry = _load_token_registry()
    if not registry:
        return AuthContext(principal='local-dev', role='admin', scopes=sorted(ROLE_SCOPES['admin']))

    incoming = _extract_token(authorization, x_api_key)
    if not incoming or incoming not in registry:
        raise HTTPException(status_code=401, detail='Unauthorized')
    role = registry[incoming].get('role', 'viewer')
    principal = registry[incoming].get('principal', role)
    scopes = ROLE_SCOPES.get(role, ROLE_SCOPES['viewer'])
    return AuthContext(principal=principal, role=role, scopes=sorted(scopes))


def _check_rate_limit(principal: str, scope: str) -> None:
    limit = RATE_LIMIT_WRITE_PER_MIN if scope == 'write' else RATE_LIMIT_EXECUTE_PER_MIN
    key = f'{principal}:{scope}'
    now = time.time()
    window_start = now - 60
    bucket = RATE_BUCKETS[key]
    while bucket and bucket[0] < window_start:
        bucket.popleft()
    if len(bucket) >= limit:
        raise HTTPException(status_code=429, detail='Too many requests')
    bucket.append(now)


def _require_scope(scope: str, auth: AuthContext) -> AuthContext:
    if scope not in auth.scopes and 'admin' not in auth.scopes:
        raise HTTPException(status_code=403, detail='Forbidden')
    if scope in ('write', 'execute'):
        _check_rate_limit(auth.principal, scope)
    return auth


def require_read_access(auth: AuthContext = Depends(_auth_context)) -> AuthContext:
    if READ_TOKEN_REQUIRED:
        return _require_scope('read', auth)
    return auth


def require_write_access(auth: AuthContext = Depends(_auth_context)) -> AuthContext:
    return _require_scope('write', auth)


def require_execute_access(auth: AuthContext = Depends(_auth_context)) -> AuthContext:
    return _require_scope('execute', auth)


def _audit(event: str, request_id: str, status: str, principal: str, extra: Optional[Dict[str, Any]] = None) -> None:
    try:
        AUDIT_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        payload: Dict[str, Any] = {
            'ts': datetime.utcnow().isoformat(),
            'event': event,
            'request_id': request_id,
            'status': status,
            'principal': principal,
        }
        if extra:
            payload.update(extra)
        with AUDIT_LOG_FILE.open('a', encoding='utf-8') as fh:
            fh.write(json.dumps(payload, ensure_ascii=True) + '\n')
    except Exception:
        logger.exception('Audit write failed')


def _infer_route(intent_text: str) -> Dict[str, str]:
    text = (intent_text or '').lower()
    if any(word in text for word in ['workflow', '流程', 'pipeline']):
        return {'mode': 'workflow', 'target': 'content_pipeline'}
    if any(word in text for word in ['skill', '工具', '执行']):
        return {'mode': 'skill', 'target': 'web_search_skill'}
    return {'mode': 'agent', 'target': 'research_agent'}


# -------- loaders --------
def _read_stat_dates(path: Path) -> tuple[str, str]:
    stat = path.stat()
    created_at = datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d')
    updated_at = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d')
    return created_at, updated_at


def _parse_skill(skill_md: Path) -> Optional[Skill]:
    content = skill_md.read_text(encoding='utf-8', errors='ignore')
    match = re.search(r'^---\s*\n(.*?)\n---\s*\n', content, flags=re.DOTALL | re.MULTILINE)
    if not match:
        return None
    front = yaml.safe_load(match.group(1)) or {}
    if not isinstance(front, dict):
        return None

    created_at, updated_at = _read_stat_dates(skill_md)
    relative = skill_md.relative_to(SKILLS_DIR)
    parts = relative.parts[:-1]
    category = '/'.join(parts) if parts else 'uncategorized'
    name = str(front.get('name') or skill_md.parent.name)

    inputs = [SkillInput(**item) for item in front.get('inputs', []) if isinstance(item, dict)]
    outputs = [SkillOutput(**item) for item in front.get('outputs', []) if isinstance(item, dict)]

    triggers = front.get('activation_keywords') or front.get('triggers') or []
    if isinstance(triggers, str):
        triggers = [triggers]

    return Skill(
        id=name,
        name=name,
        display_name=str(front.get('display_name') or name),
        version=str(front.get('version') or '1.0.0'),
        category=category,
        description=str(front.get('description') or '').strip()[:200],
        author=str(front.get('author') or 'Leo AI System'),
        status='active' if front.get('user-invocable', True) else 'inactive',
        triggers=triggers,
        inputs=inputs,
        outputs=outputs,
        created_at=created_at,
        updated_at=updated_at,
    )


def load_all_skills() -> List[Skill]:
    if not SKILLS_DIR.exists():
        return []
    skills: List[Skill] = []
    for md in SKILLS_DIR.rglob('SKILL.md'):
        try:
            skill = _parse_skill(md)
            if skill:
                skills.append(skill)
        except Exception:
            logger.exception('Failed to parse skill file: %s', md)
    return skills


def load_all_agents() -> List[Agent]:
    agents: List[Agent] = []
    if SUBAGENTS_DIR.exists():
        for agent_dir in SUBAGENTS_DIR.iterdir():
            if not agent_dir.is_dir() or agent_dir.name.startswith('_'):
                continue
            created_at, updated_at = _read_stat_dates(agent_dir)
            aid = agent_dir.name
            agents.append(
                Agent(
                    id=aid,
                    name=aid,
                    display_name=aid,
                    description=f'Agent {aid}',
                    role='assistant',
                    created_at=created_at,
                    updated_at=updated_at,
                )
            )
    return agents


def load_all_workflows() -> List[Workflow]:
    workflows: List[Workflow] = []
    if not WORKFLOWS_DIR.exists():
        return workflows

    for wf in WORKFLOWS_DIR.glob('*.yaml'):
        data = yaml.safe_load(wf.read_text(encoding='utf-8', errors='ignore')) or {}
        created_at, updated_at = _read_stat_dates(wf)
        wf_id = str(data.get('name') or wf.stem)
        inputs: List[Dict[str, Any]] = []
        if isinstance(data.get('inputs'), dict):
            for key, val in data['inputs'].items():
                if isinstance(val, dict):
                    inputs.append({'name': key, **val})

        workflows.append(
            Workflow(
                id=wf_id,
                name=wf_id,
                display_name=str(data.get('display_name') or wf_id),
                version=str(data.get('version') or '1.0.0'),
                description=str(data.get('description') or ''),
                steps=data.get('steps', []) if isinstance(data.get('steps', []), list) else [],
                inputs=inputs,
                created_at=created_at,
                updated_at=updated_at,
            )
        )
    return workflows


def load_memory_entries() -> List[MemoryEntry]:
    if not MEMORY_FILE.exists():
        return []

    entries: List[MemoryEntry] = []
    category = 'general'
    for line in MEMORY_FILE.read_text(encoding='utf-8', errors='ignore').splitlines():
        raw = line.strip()
        if raw.startswith('#'):
            category = raw.strip('#').strip() or 'general'
            continue
        if not raw.startswith('- ') or ':' not in raw:
            continue
        key, value = raw[2:].split(':', 1)
        key = key.strip()
        value = value.strip()
        entries.append(
            MemoryEntry(
                id=key,
                key=key,
                value=value,
                category=category,
                created_at='2024-01-01',
                updated_at='2024-01-01',
            )
        )
    return entries


# -------- routes --------
@app.get('/')
async def root() -> Dict[str, Any]:
    return {'message': 'Leo AI System API', 'version': '2.0.0', 'connected': True}


@app.post('/api/system/reload', dependencies=[Depends(require_write_access)], response_model=ApiResponse)
async def reload_system() -> ApiResponse:
    return ApiResponse(success=True, message='Reload acknowledged')


@app.post('/api/v2/execute', response_model=LeoResponse)
async def execute_unified(request: LeoRequest, http_request: Request, auth: AuthContext = Depends(require_execute_access)) -> LeoResponse:
    api = get_leo_api()
    request_id = getattr(http_request.state, 'request_id', request.trace_id)
    try:
        mode = request.mode
        target = request.target

        if mode == 'skill' and target:
            method_name = request.method or 'execute'
            try:
                result = api.call(target, method_name, **request.params)
            except Exception:
                logger.exception('Skill call failed, fallback to simulated response: %s', target)
                result = {
                    'mode': 'skill',
                    'target': target,
                    'method': method_name,
                    'status': 'fallback',
                    'message': f'Skill {target}.{method_name} fallback executed',
                    'params': request.params,
                }
            resolved_intent = mode
            resolved_target = target
        elif mode == 'agent' and target:
            try:
                result = api.run_agent(target, request.intent)
            except Exception:
                logger.exception('Agent run failed, fallback to simulated response: %s', target)
                result = {
                    'mode': 'agent',
                    'target': target,
                    'status': 'fallback',
                    'response': f'Agent {target} fallback response for: {request.intent}',
                }
            resolved_intent = mode
            resolved_target = target
        elif mode == 'workflow' and target:
            result = {'status': 'simulated', 'target': target, 'inputs': request.params}
            resolved_intent = mode
            resolved_target = target
        else:
            route = _infer_route(request.intent)
            resolved_intent = route['mode']
            resolved_target = route['target']
            if resolved_intent == 'agent':
                try:
                    result = api.run_agent(resolved_target, request.intent)
                except Exception:
                    logger.exception('Auto agent run failed, fallback: %s', resolved_target)
                    result = {
                        'mode': 'agent',
                        'target': resolved_target,
                        'status': 'fallback',
                        'response': f'Agent {resolved_target} fallback response for: {request.intent}',
                    }
            elif resolved_intent == 'skill':
                try:
                    result = api.call(resolved_target, 'execute', **request.params)
                except Exception:
                    logger.exception('Auto skill call failed, fallback: %s', resolved_target)
                    result = {
                        'mode': 'skill',
                        'target': resolved_target,
                        'method': 'execute',
                        'status': 'fallback',
                        'message': f'Skill {resolved_target}.execute fallback executed',
                        'params': request.params,
                    }
            else:
                result = {'status': 'simulated', 'target': resolved_target, 'inputs': request.params}

        if result is None:
            result = {
                'status': 'ok',
                'target': resolved_target,
                'message': f'{resolved_intent} execution completed with no payload.',
            }

        resp = LeoResponse(
            trace_id=request.trace_id,
            status='ok',
            intent=resolved_intent,
            target=resolved_target,
            data=result,
            message='Execution completed',
        )
        _audit(
            event='execute',
            request_id=request_id,
            status='ok',
            principal=auth.principal,
            extra={'intent': resp.intent, 'target': resp.target, 'mode': request.mode},
        )
        return resp
    except Exception:
        logger.exception('execute_unified failed')
        _audit(
            event='execute',
            request_id=request_id,
            status='error',
            principal=auth.principal,
            extra={'mode': request.mode, 'target': request.target},
        )
        return LeoResponse(
            trace_id=request.trace_id,
            status='error',
            error_code=ErrorCode.E_INTERNAL,
            message='Execution failed',
        )


@app.get('/api/skills', response_model=ApiResponse, dependencies=[Depends(require_read_access)])
async def get_skills(category: Optional[str] = None) -> ApiResponse:
    skills = load_all_skills()
    if category:
        skills = [s for s in skills if category in s.category]
    return ApiResponse(success=True, data=[s.model_dump() for s in skills])


@app.get('/api/skills/{skill_id}', response_model=ApiResponse, dependencies=[Depends(require_read_access)])
async def get_skill(skill_id: str) -> ApiResponse:
    skill = next((s for s in load_all_skills() if s.id == skill_id), None)
    if not skill:
        raise HTTPException(status_code=404, detail='Skill not found')
    return ApiResponse(success=True, data=skill.model_dump())


@app.post('/api/skills/{skill_id}/execute', response_model=ApiResponse, dependencies=[Depends(require_execute_access)])
async def execute_skill(skill_id: str, request: SkillExecuteRequest) -> ApiResponse:
    response = await execute_unified(
        LeoRequest(
            intent=request.params.get('query', f'execute {skill_id}'),
            mode='skill',
            target=skill_id,
            method=request.method,
            params=request.params,
            trace_id=str(uuid.uuid4())[:8],
        )
    )
    return ApiResponse(success=response.status == 'ok', data=response.data, error=response.message if response.status != 'ok' else None)


@app.get('/api/skills/{skill_id}/methods', response_model=ApiResponse, dependencies=[Depends(require_read_access)])
async def get_skill_methods(skill_id: str) -> ApiResponse:
    return ApiResponse(success=True, data=[{'name': 'execute', 'doc': 'default execute method', 'params': []}])


@app.get('/api/agents', response_model=ApiResponse, dependencies=[Depends(require_read_access)])
async def get_agents() -> ApiResponse:
    return ApiResponse(success=True, data=[a.model_dump() for a in load_all_agents()])


@app.get('/api/agents/{agent_id}', response_model=ApiResponse, dependencies=[Depends(require_read_access)])
async def get_agent(agent_id: str) -> ApiResponse:
    agent = next((a for a in load_all_agents() if a.id == agent_id), None)
    if not agent:
        raise HTTPException(status_code=404, detail='Agent not found')
    return ApiResponse(success=True, data=agent.model_dump())


@app.post('/api/agents/{agent_id}/execute', response_model=ApiResponse, dependencies=[Depends(require_execute_access)])
async def execute_agent(agent_id: str, request: AgentExecuteRequest) -> ApiResponse:
    response = await execute_unified(
        LeoRequest(intent=request.message, mode='agent', target=agent_id, trace_id=str(uuid.uuid4())[:8])
    )
    return ApiResponse(success=response.status == 'ok', data=response.data, error=response.message if response.status != 'ok' else None)


@app.get('/api/workflows', response_model=ApiResponse, dependencies=[Depends(require_read_access)])
async def get_workflows() -> ApiResponse:
    return ApiResponse(success=True, data=[w.model_dump() for w in load_all_workflows()])


@app.get('/api/workflows/{workflow_id}', response_model=ApiResponse, dependencies=[Depends(require_read_access)])
async def get_workflow(workflow_id: str) -> ApiResponse:
    workflow = next((w for w in load_all_workflows() if w.id == workflow_id), None)
    if not workflow:
        raise HTTPException(status_code=404, detail='Workflow not found')
    return ApiResponse(success=True, data=workflow.model_dump())


@app.post('/api/workflows/{workflow_id}/execute', response_model=ApiResponse, dependencies=[Depends(require_execute_access)])
async def execute_workflow(workflow_id: str, request: WorkflowExecuteRequest) -> ApiResponse:
    response = await execute_unified(
        LeoRequest(intent=f'run {workflow_id}', mode='workflow', target=workflow_id, params=request.inputs, trace_id=str(uuid.uuid4())[:8])
    )
    return ApiResponse(success=response.status == 'ok', data=response.data, error=response.message if response.status != 'ok' else None)


@app.post('/api/workflows/validate', response_model=ApiResponse, dependencies=[Depends(require_write_access)])
async def validate_workflow(data: Dict[str, str]) -> ApiResponse:
    try:
        yaml.safe_load(data.get('yaml', ''))
        return ApiResponse(success=True, data={'valid': True})
    except yaml.YAMLError as exc:
        return ApiResponse(success=True, data={'valid': False, 'errors': [str(exc)]})


@app.get('/api/memory', response_model=ApiResponse, dependencies=[Depends(require_read_access)])
async def get_memory(category: Optional[str] = None) -> ApiResponse:
    entries = load_memory_entries()
    if category:
        entries = [e for e in entries if e.category == category]
    return ApiResponse(success=True, data=[e.model_dump() for e in entries])


@app.get('/api/memory/search', response_model=ApiResponse, dependencies=[Depends(require_read_access)])
async def search_memory(q: str) -> ApiResponse:
    ql = q.lower()
    results = [e for e in load_memory_entries() if ql in e.key.lower() or ql in e.value.lower()]
    return ApiResponse(success=True, data=[e.model_dump() for e in results])


@app.get('/api/memory/stats', response_model=ApiResponse, dependencies=[Depends(require_read_access)])
async def get_memory_stats() -> ApiResponse:
    entries = load_memory_entries()
    categories: Dict[str, int] = {}
    by_importance: Dict[int, int] = {}
    for entry in entries:
        categories[entry.category] = categories.get(entry.category, 0) + 1
        by_importance[entry.importance] = by_importance.get(entry.importance, 0) + 1
    return ApiResponse(success=True, data=MemoryStats(total_entries=len(entries), categories=categories, by_importance=by_importance).model_dump())


@app.post('/api/memory', response_model=ApiResponse, dependencies=[Depends(require_write_access)])
async def create_memory_entry(entry: MemoryEntry) -> ApiResponse:
    MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with MEMORY_FILE.open('a', encoding='utf-8') as fh:
        fh.write(f'\n- {entry.key}: {entry.value}\n')
    return ApiResponse(success=True, data=entry.model_dump(), message='Memory entry created')


@app.post('/api/intent/recognize', response_model=ApiResponse, dependencies=[Depends(require_read_access)])
async def recognize_intent(data: Dict[str, str]) -> ApiResponse:
    text = data.get('text', '').strip()
    if not text:
        return ApiResponse(success=True, data={'intent_type': 'query', 'target': 'research_agent', 'confidence': 0.2, 'params': {}, 'alternatives': []})

    lower = text.lower()
    if any(word in lower for word in ['workflow', '流程', 'pipeline']):
        intent_type, target, confidence = 'workflow', 'content_pipeline', 0.82
    elif any(word in lower for word in ['skill', '工具', '执行']):
        intent_type, target, confidence = 'skill', 'web_search_skill', 0.8
    else:
        intent_type, target, confidence = 'agent', 'research_agent', 0.76

    return ApiResponse(success=True, data={
        'intent_type': intent_type,
        'target': target,
        'confidence': confidence,
        'params': {'query': text},
        'alternatives': [],
    })


@app.post('/api/intent/route', response_model=ApiResponse, dependencies=[Depends(require_read_access)])
async def route_intent(data: Dict[str, str]) -> ApiResponse:
    recognized = await recognize_intent(data)
    match = recognized.data or {}
    action = 'delegate_to_agent'
    if match.get('intent_type') == 'skill':
        action = 'execute_skill'
    elif match.get('intent_type') == 'workflow':
        action = 'execute_workflow'
    return ApiResponse(success=True, data={'action': action, 'target': match.get('target'), 'params': match.get('params', {})})


@app.post('/api/intent/test', response_model=ApiResponse, dependencies=[Depends(require_read_access)])
async def test_intent(data: Dict[str, str]) -> ApiResponse:
    start = datetime.utcnow()
    match_resp = await recognize_intent(data)
    route_resp = await route_intent(data)
    elapsed = int((datetime.utcnow() - start).total_seconds() * 1000)
    return ApiResponse(success=True, data={
        'input': data.get('text', ''),
        'match': match_resp.data,
        'routing': route_resp.data,
        'execution_time_ms': elapsed,
    })


@app.get('/api/system/stats', response_model=ApiResponse, dependencies=[Depends(require_read_access)])
async def get_system_stats() -> ApiResponse:
    return ApiResponse(success=True, data={
        'total_skills': len(load_all_skills()),
        'total_agents': len(load_all_agents()),
        'total_workflows': len(load_all_workflows()),
        'active_tasks': 0,
        'memory_entries': len(load_memory_entries()),
        'uptime_hours': 0,
    })


@app.get('/api/system/category-stats', response_model=ApiResponse, dependencies=[Depends(require_read_access)])
async def get_category_stats() -> ApiResponse:
    counts: Dict[str, int] = {}
    for skill in load_all_skills():
        root = skill.category.split('/')[0]
        counts[root] = counts.get(root, 0) + 1
    return ApiResponse(success=True, data=[{'category': k, 'count': v, 'label': k} for k, v in sorted(counts.items())])


@app.get('/api/system/health', response_model=ApiResponse, dependencies=[Depends(require_read_access)])
async def get_health() -> ApiResponse:
    uptime = int(time.time() - STARTED_AT)
    return ApiResponse(success=True, data={'status': 'healthy', 'uptime': uptime, 'version': '2.1.0'})


@app.get('/api/conversations', response_model=ApiResponse, dependencies=[Depends(require_read_access)])
async def get_conversations() -> ApiResponse:
    items = sorted(CONVERSATIONS.values(), key=lambda x: x['updated_at'], reverse=True)
    return ApiResponse(success=True, data=items)


@app.post('/api/conversations', response_model=ApiResponse, dependencies=[Depends(require_write_access)])
async def create_conversation(request: ConversationCreate) -> ApiResponse:
    global CONVERSATION_SEQ
    CONVERSATION_SEQ += 1
    now = datetime.utcnow().isoformat()
    data = {'id': CONVERSATION_SEQ, 'title': request.title, 'messages': [], 'created_at': now, 'updated_at': now}
    CONVERSATIONS[CONVERSATION_SEQ] = data
    return ApiResponse(success=True, data=data)


@app.get('/api/conversations/{conversation_id}', response_model=ApiResponse, dependencies=[Depends(require_read_access)])
async def get_conversation(conversation_id: int) -> ApiResponse:
    item = CONVERSATIONS.get(conversation_id)
    if not item:
        raise HTTPException(status_code=404, detail='Conversation not found')
    return ApiResponse(success=True, data=item)


@app.put('/api/conversations/{conversation_id}', response_model=ApiResponse, dependencies=[Depends(require_write_access)])
async def update_conversation(conversation_id: int, request: ConversationUpdate) -> ApiResponse:
    item = CONVERSATIONS.get(conversation_id)
    if not item:
        raise HTTPException(status_code=404, detail='Conversation not found')
    item['messages'] = request.messages
    item['updated_at'] = datetime.utcnow().isoformat()
    return ApiResponse(success=True, data=item)


@app.delete('/api/conversations/{conversation_id}', response_model=ApiResponse, dependencies=[Depends(require_write_access)])
async def delete_conversation(conversation_id: int) -> ApiResponse:
    if conversation_id not in CONVERSATIONS:
        raise HTTPException(status_code=404, detail='Conversation not found')
    del CONVERSATIONS[conversation_id]
    return ApiResponse(success=True, message='Conversation deleted')


# ==================== WebSocket 支持 ====================

class ConnectionManager:
    """WebSocket 连接管理器"""

    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"WebSocket client connected: {client_id}")

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"WebSocket client disconnected: {client_id}")

    async def send_message(self, client_id: str, message: dict):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json(message)

    async def broadcast(self, message: dict):
        for connection in self.active_connections.values():
            await connection.send_json(message)


manager = ConnectionManager()


@app.websocket('/ws/{client_id}')
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket 实时通信端点"""
    await manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get('type', 'unknown')

            if msg_type == 'ping':
                await manager.send_message(client_id, {'type': 'pong'})
            elif msg_type == 'execute':
                # 异步执行任务
                result = await execute_skill_async(data.get('skill'), data.get('params', {}))
                await manager.send_message(client_id, {'type': 'result', 'data': result})
            elif msg_type == 'subscribe':
                # 订阅事件
                logger.info(f"Client {client_id} subscribed to {data.get('event')}")

    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(client_id)


async def execute_skill_async(skill_name: str, params: dict) -> dict:
    """异步执行 Skill"""
    try:
        from leo_orchestrator.api import get_leo_api
        api = get_leo_api()
        result = api.call(skill_name, params.get('action', 'execute'), **params)
        return {'success': True, 'result': result}
    except Exception as e:
        return {'success': False, 'error': str(e)}


# ==================== 限流中间件 ====================

from collections import defaultdict
from time import time
from typing import Callable

class RateLimiter:
    """简单的内存限流器"""

    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests: defaultdict[str, list] = defaultdict(list)

    def is_allowed(self, key: str) -> bool:
        """检查请求是否允许"""
        now = time()
        minute_ago = now - 60

        # 清理旧请求
        self.requests[key] = [t for t in self.requests[key] if t > minute_ago]

        if len(self.requests[key]) >= self.requests_per_minute:
            return False

        self.requests[key].append(now)
        return True


# 全局限流器
execute_limiter = RateLimiter(120)
write_limiter = RateLimiter(60)


@app.middleware('http')
async def rate_limit_middleware(request: Request, call_next: Callable):
    """请求限流中间件"""
    # 跳过 WebSocket 和健康检查
    if request.url.path.startswith('/ws') or request.url.path == '/api/system/health':
        return await call_next(request)

    # 获取客户端标识
    client_id = request.client.host if request.client else 'unknown'

    # 根据路径选择限流器
    if request.url.path.startswith('/api/'):
        if request.method in ['POST', 'PUT', 'DELETE']:
            limiter = write_limiter
        else:
            limiter = execute_limiter

        if not limiter.is_allowed(client_id):
            return JSONResponse(
                status_code=429,
                content={'success': False, 'error': 'Rate limit exceeded'}
            )

    return await call_next(request)


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='0.0.0.0', port=8000)
