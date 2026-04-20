# Leo AI System 整体优化方案

> 版本: 1.0 | 日期: 2026-03-10 | 基于系统评估报告

---

## 一、架构优化

### 1.1 模块化重构

**问题**: 当前模块耦合度较高，`src/` 目录下模块边界不够清晰

**优化方案**:
```
当前结构:
src/
├── leo_orchestrator/  # 编排器
├── leo_subagents/     # Agent层
├── leo_skills/       # Skill层
├── leo_workflows/    # 工作流
├── leo_memory/       # 记忆系统
├── leo_interface/   # 接口层
└── leo_gateway/      # 网关

优化后结构:
src/
├── leo_core/                    # 核心模块
│   ├── orchestrator/           # 编排协调
│   ├── registry/              # 注册中心
│   ├── intent/                 # 意图识别
│   └── workflow/               # 工作流引擎
├── leo_agents/                 # Agent模块
│   ├── base/                   # Agent基类
│   ├── realestate/            # 房产Agent
│   ├── ecommerce/             # 电商Agent
│   └── financial/             # 金融Agent
├── leo_skills/                 # Skill模块
│   ├── base/                   # Skill基类
│   ├── business/              # 业务Skill
│   ├── dev/                   # 开发Skill
│   └── content/               # 内容Skill
├── leo_services/               # 服务模块
│   ├── memory/                # 记忆服务
│   ├── llm/                   # LLM集成
│   └── storage/               # 存储服务
└── leo_interface/             # 接口模块
```

### 1.2 接口标准化

**问题**: Agent/Skill 接口不统一，扩展困难

**优化方案**: 定义标准接口协议

```python
# src/leo_core/base.py

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

class AgentRequest(BaseModel):
    """Agent请求标准模型"""
    input: str
    context: Optional[Dict[str, Any]] = None
    parameters: Optional[Dict[str, Any]] = None

class AgentResponse(BaseModel):
    """Agent响应标准模型"""
    output: str
    status: str  # success, error, partial
    metadata: Optional[Dict[str, Any]] = None
    artifacts: Optional[List[Dict[str, Any]]] = None

class BaseAgent(ABC):
    """Agent基类 - 统一接口"""

    @abstractmethod
    async def execute(self, request: AgentRequest) -> AgentResponse:
        """执行Agent逻辑"""
        pass

    @abstractmethod
    def get_capabilities(self) -> Dict[str, Any]:
        """获取Agent能力描述"""
        pass

    @abstractmethod
    async def validate_input(self, request: AgentRequest) -> bool:
        """验证输入合法性"""
        pass


class BaseSkill(ABC):
    """Skill基类 - 统一接口"""

    @abstractmethod
    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行Skill逻辑"""
        pass

    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """获取Skill输入输出Schema"""
        pass
```

### 1.3 事件驱动架构

**问题**: 当前模块间调用耦合紧密

**优化方案**: 引入事件总线

```python
# src/leo_core/events/__init__.py

from typing import Callable, Dict, List
from dataclasses import dataclass
from datetime import datetime
import asyncio

@dataclass
class Event:
    """事件模型"""
    type: str
    payload: Dict
    source: str
    timestamp: datetime = None

    def __post_init__(self):
        self.timestamp = self.timestamp or datetime.now()

class EventBus:
    """事件总线"""

    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, handler: Callable):
        """订阅事件"""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)

    async def publish(self, event: Event):
        """发布事件"""
        handlers = self._subscribers.get(event.type, [])
        for handler in handlers:
            await handler(event)

# 事件类型定义
class Events:
    AGENT_STARTED = "agent.started"
    AGENT_COMPLETED = "agent.completed"
    AGENT_FAILED = "agent.failed"
    SKILL_INVOKED = "skill.invoked"
    WORKFLOW_TRIGGERED = "workflow.triggered"
    MEMORY_UPDATED = "memory.updated"
```

---

## 二、依赖管理优化

### 2.1 统一依赖管理

**问题**: 多个 requirements.txt 分散在不同目录

**优化方案**: 使用 Poetry 统一管理

```toml
# pyproject.toml (扩展)

[tool.poetry]
name = "leo-ai-system"
version = "2.0.0"
description = "Leo AI Agent System"

[tool.poetry.dependencies]
python = "^3.9"
# 核心
pyyaml = "^6.0"
requests = "^2.31"
sqlalchemy = "^2.0"
aiohttp = "^3.9"

# AI
anthropic = "^0.18"
openai = "^1.12"

# 数据
pydantic = "^2.0"
python-dotenv = "^1.0"

# Web
streamlit = "^1.28"
fastapi = "^0.109"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4"
pytest-asyncio = "^0.21"
pytest-cov = "^4.0"
black = "^23.0"
ruff = "^0.1"

[tool.poetry.group.optional]
name = "web"
dependencies = [
    "streamlit>=1.28",
    "gradio>=4.0",
]
```

### 2.2 依赖版本锁定

**问题**: 依赖版本不稳定可能导致问题

**优化方案**:
```bash
# 生成锁文件
poetry lock

# 更新依赖
poetry update

# 导出requirements.txt (兼容旧系统)
poetry export -f requirements.txt --output requirements.lock.txt
```

### 2.3 依赖分析与优化

```bash
# 安装依赖分析工具
pip install pip-audit safety

# 检查漏洞
pip-audit

# 检查兼容性问题
pip check
```

---

## 三、代码质量优化

### 3.1 类型注解增强

**当前问题**: 大部分代码缺少类型注解

**优化方案**:

```python
# 优化前
def process_request(data):
    return data.get('result')

# 优化后
from typing import TypedDict, Optional, List

class RequestData(TypedDict):
    input: str
    context: Optional[dict]
    options: Optional[dict]

class ProcessResult(TypedDict):
    success: bool
    data: Optional[dict]
    error: Optional[str]

def process_request(data: RequestData) -> ProcessResult:
    """处理请求并返回结果"""
    try:
        result = data.get('result', {})
        return ProcessResult(success=True, data=result, error=None)
    except Exception as e:
        return ProcessResult(success=False, data=None, error=str(e))
```

### 3.2 错误处理标准化

```python
# src/leo_core/exceptions.py

from typing import Optional
from enum import Enum

class ErrorCode(Enum):
    """错误码定义"""
    INVALID_INPUT = "E001"
    AGENT_NOT_FOUND = "E002"
    SKILL_EXECUTION_FAILED = "E003"
    WORKFLOW_NOT_FOUND = "E004"
    LLM_API_ERROR = "E005"
    MEMORY_ERROR = "E006"

class LeoException(Exception):
    """基础异常类"""

    def __init__(
        self,
        message: str,
        code: ErrorCode,
        details: Optional[dict] = None
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}

    def to_dict(self) -> dict:
        return {
            "error": self.message,
            "code": self.code.value,
            "details": self.details
        }

class AgentNotFoundException(LeoException):
    def __init__(self, agent_name: str):
        super().__init__(
            f"Agent '{agent_name}' not found",
            ErrorCode.AGENT_NOT_FOUND,
            {"agent_name": agent_name}
        )

class SkillExecutionException(LeoException):
    def __init__(self, skill_name: str, reason: str):
        super().__init__(
            f"Skill '{skill_name}' execution failed: {reason}",
            ErrorCode.SKILL_EXECUTION_FAILED,
            {"skill_name": skill_name, "reason": reason}
        )
```

### 3.3 日志标准化

```python
# src/leo_core/logging.py

import logging
import sys
from typing import Optional
from logging.handlers import RotatingFileHandler

def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    format_json: bool = False
):
    """标准化日志配置"""

    # 日志格式
    if format_json:
        # JSON格式 (用于日志收集)
        format_str = '{"time":"%(asctime)s","level":"%(levelname)s","name":"%(name)s","message":"%(message)s"}'
    else:
        # 人类可读格式
        format_str = '%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s'

    formatter = logging.Formatter(format_str)

    # 根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))

    # 控制台处理器
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)
    root_logger.addHandler(console)

    # 文件处理器 (可选)
    if log_file:
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    return root_logger

# 使用示例
logger = logging.getLogger(__name__)

async def execute_agent(agent_name: str, input_data: dict):
    logger.info(f"Starting agent: {agent_name}", extra={"input": input_data})
    try:
        result = await agent.execute(input_data)
        logger.info(f"Agent completed: {agent_name}", extra={"result": result})
        return result
    except Exception as e:
        logger.error(f"Agent failed: {agent_name}", exc_info=True, extra={"error": str(e)})
        raise
```

---

## 四、测试优化

### 4.1 测试结构重组

```
tests/
├── unit/                    # 单元测试
│   ├── test_agents/
│   ├── test_skills/
│   └── test_core/
├── integration/             # 集成测试
│   ├── test_workflows/
│   └── test_agents_skills/
├── e2e/                    # 端到端测试
│   └── test_full_pipeline/
├── fixtures/               # 测试数据
│   ├── agents/
│   ├── skills/
│   └── workflows/
├── mocks/                 # Mock对象
│   ├── llm_mock.py
│   └── storage_mock.py
├── conftest.py            # pytest配置
└── README.md              # 测试说明
```

### 4.2 测试基类和Fixtures

```python
# tests/conftest.py

import pytest
import asyncio
from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock

from leo_core.agents import BaseAgent
from leo_core.skills import BaseSkill

@pytest.fixture
def mock_llm_response():
    """Mock LLM响应"""
    return {
        "choices": [{
            "message": {
                "content": "Test response"
            }
        }]
    }

@pytest.fixture
def sample_agent_context():
    """标准Agent上下文"""
    return {
        "user_id": "test_user",
        "session_id": "test_session",
        "conversation_history": []
    }

@pytest.fixture
async def mock_agent() -> AsyncGenerator[BaseAgent, None]:
    """Mock Agent"""
    agent = AsyncMock(spec=BaseAgent)
    agent.execute.return_value = AgentResponse(
        output="Mock response",
        status="success"
    )
    agent.get_capabilities.return_value = {
        "name": "test_agent",
        "description": "Test agent"
    }
    yield agent
    await agent.aclose()

@pytest.fixture
def event_loop():
    """事件循环fixture"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

# 标记
pytest_plugins = ['pytest_asyncio']

# 自动使用fixtures
@pytest.fixture(autouse=True)
async def reset_context():
    """每个测试后重置上下文"""
    yield
    # 清理逻辑
```

### 4.3 测试覆盖目标

| 模块 | 目标覆盖率 | 关键测试 |
|------|-----------|---------|
| leo_core | 90% | 注册、编排、事件 |
| leo_agents | 85% | 各Agent执行逻辑 |
| leo_skills | 80% | Skill执行、错误处理 |
| leo_workflows | 85% | 工作流执行 |
| leo_memory | 90% | 存储、检索 |

---

## 五、文档优化

### 5.1 API文档自动化

```python
# docs/api/openapi.yaml

openapi: 3.1.0
info:
  title: Leo AI System API
  version: 2.0.0
  description: Leo AI Agent System REST API

paths:
  /api/v1/agents/{agent_name}/execute:
    post:
      summary: Execute an agent
      parameters:
        - name: agent_name
          in: path
          required: true
          schema:
            type: string
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/AgentRequest'
      responses:
        '200':
          description: Successful execution
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/AgentResponse'

components:
  schemas:
    AgentRequest:
      type: object
      properties:
        input:
          type: string
        context:
          type: object
        parameters:
          type: object

    AgentResponse:
      type: object
      properties:
        output:
          type: string
        status:
          type: string
          enum: [success, error, partial]
```

### 5.2 代码文档规范

```python
"""
模块名称
==========

模块功能详细描述

Classes:
    - ClassName: 类功能描述

Functions:
    - function_name: 函数功能描述

Example:
    >>> from leo_core import Example
    >>> example = Example()
    >>> example.execute()
"""

class Example:
    """
    示例类

    类的详细功能描述

    Attributes:
        name: 属性描述
        value: 属性描述

    Example:
        >>> example = Example(name="test")
        >>> example.process()
    """

    def __init__(self, name: str) -> None:
        """
        初始化方法

        Args:
            name: 参数说明
        """
        self.name = name

    def process(self) -> dict:
        """
        处理方法

        Returns:
            处理结果字典

        Raises:
            ValueError: 异常说明
        """
        return {"status": "success", "name": self.name}
```

---

## 六、性能优化

### 6.1 缓存策略

```python
# src/leo_core/cache.py

import asyncio
import hashlib
import json
from functools import wraps
from typing import Any, Callable, Optional
from datetime import timedelta

class CacheManager:
    """缓存管理器"""

    def __init__(self):
        self._cache: dict = {}
        self._ttl: dict = {}

    def _make_key(self, *args, **kwargs) -> str:
        """生成缓存键"""
        key_data = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True)
        return hashlib.md5(key_data.encode()).hexdigest()

    def set(self, key: str, value: Any, ttl: Optional[int] = 3600):
        """设置缓存"""
        self._cache[key] = value
        if ttl:
            self._ttl[key] = asyncio.get_event_loop().time() + ttl

    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        if key in self._cache:
            if key in self._ttl:
                if asyncio.get_event_loop().time() > self._ttl[key]:
                    del self._cache[key]
                    del self._ttl[key]
                    return None
            return self._cache[key]
        return None

    def delete(self, key: str):
        """删除缓存"""
        self._cache.pop(key, None)
        self._ttl.pop(key, None)

# 缓存装饰器
def cached(ttl: int = 3600):
    """缓存装饰器"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache = CacheManager()
            key = cache._make_key(func.__name__, *args, **kwargs)

            cached_value = cache.get(key)
            if cached_value is not None:
                return cached_value

            result = await func(*args, **kwargs)
            cache.set(key, result, ttl)
            return result
        return wrapper
    return decorator


# 使用示例
@cached(ttl=1800)  # 30分钟缓存
async def get_agent_capabilities(agent_name: str) -> dict:
    """获取Agent能力描述 (带缓存)"""
    # 实际获取逻辑
    return {"name": agent_name, "capabilities": []}
```

### 6.2 连接池与资源管理

```python
# src/leo_core/resources.py

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

class ConnectionPool:
    """连接池"""

    def __init__(self, factory, max_size: int = 10):
        self.factory = factory
        self.max_size = max_size
        self._pool: asyncio.Queue = asyncio.Queue(maxsize=max_size)
        self._semaphore = asyncio.Semaphore(max_size)

    async def initialize(self):
        """初始化连接池"""
        for _ in range(self.max_size):
            conn = await self.factory.create()
            await self._pool.put(conn)

    @asynccontextmanager
    async def acquire(self):
        """获取连接"""
        async with self._semaphore:
            conn = await self._pool.get()
            try:
                yield conn
            finally:
                await self._pool.put(conn)

    async def close(self):
        """关闭连接池"""
        while not self._pool.empty():
            conn = await self._pool.get()
            await self.factory.close(conn)
```

### 6.3 异步优化

```python
# 批量处理优化
async def batch_process(items: list, batch_size: int = 10):
    """批量处理项目"""
    results = []
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        batch_results = await asyncio.gather(
            *[process_item(item) for item in batch],
            return_exceptions=True
        )
        results.extend(batch_results)
    return results


# 并发限制
from asyncio import Semaphore

async def limited_concurrent(tasks: list, limit: int = 5):
    """限制并发数"""
    semaphore = Semaphore(limit)

    async def bounded_task(task):
        async with semaphore:
            return await task

    return await asyncio.gather(*[bounded_task(t) for t in tasks])
```

---

## 七、安全优化

### 7.1 输入验证

```python
# src/leo_core/validation.py

from pydantic import BaseModel, Field, validator
from typing import Optional, List

class AgentRequestModel(BaseModel):
    """Agent请求验证模型"""

    input: str = Field(..., min_length=1, max_length=10000)
    context: Optional[dict] = Field(default_factory=dict)
    parameters: Optional[dict] = Field(default_factory=dict)

    @validator('input')
    def validate_input(cls, v):
        # 移除潜在恶意内容
        dangerous_patterns = ['<script', 'eval(', 'exec(']
        for pattern in dangerous_patterns:
            if pattern in v.lower():
                raise ValueError(f'Invalid input pattern: {pattern}')
        return v

    class Config:
        schema_extra = {
            "example": {
                "input": "分析宁波房产市场",
                "context": {"user_id": "123"},
                "parameters": {"depth": "detailed"}
            }
        }
```

### 7.2 敏感信息处理

```python
# src/leo_core/security.py

import os
import re
from typing import Any, Dict

class SensitiveDataFilter:
    """敏感数据过滤器"""

    PATTERNS = {
        'api_key': r'(?i)(api[_-]?key|apikey|secret[_-]?key)\s*[:=]\s*[\'"]?([a-zA-Z0-9_\-]{20,})',
        'password': r'(?i)(password|passwd|pwd)\s*[:=]\s*[\'"]?([^\s\'"]{6,})',
        'token': r'(?i)(bearer\s+|token\s*[:=]\s*)[\'"]?([a-zA-Z0-9_\-\.]{20,})',
    }

    @classmethod
    def filter(cls, data: Any) -> Any:
        """过滤敏感信息"""
        if isinstance(data, dict):
            return {k: cls.filter(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [cls.filter(item) for item in data]
        elif isinstance(data, str):
            return cls._filter_string(data)
        return data

    @classmethod
    def _filter_string(cls, text: str) -> str:
        """过滤字符串中的敏感信息"""
        result = text
        for pattern in cls.PATTERNS.values():
            result = re.sub(pattern, r'\1: [REDACTED]', result)
        return result


# 环境变量安全加载
def safe_get_env(key: str, default: Optional[str] = None) -> str:
    """安全获取环境变量"""
    value = os.getenv(key, default)
    if value is None:
        raise ValueError(f"Required environment variable {key} is not set")
    return value
```

### 7.3 速率限制

```python
# src/leo_core/rate_limit.py

import time
from collections import defaultdict
from asyncio import Lock
from typing import Dict

class RateLimiter:
    """速率限制器"""

    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: Dict[str, list] = defaultdict(list)
        self._locks: Dict[str, Lock] = defaultdict(Lock)

    async def check(self, client_id: str) -> bool:
        """检查是否允许请求"""
        async with self._locks[client_id]:
            now = time.time()
            # 清理过期请求
            self._requests[client_id] = [
                t for t in self._requests[client_id]
                if now - t < self.window_seconds
            ]

            if len(self._requests[client_id]) >= self.max_requests:
                return False

            self._requests[client_id].append(now)
            return True

    async def get_remaining(self, client_id: str) -> int:
        """获取剩余请求数"""
        now = time.time()
        active_requests = [
            t for t in self._requests[client_id]
            if now - t < self.window_seconds
        ]
        return max(0, self.max_requests - len(active_requests))
```

---

## 八、CI/CD 优化

### 8.1 GitHub Actions 工作流

```yaml
# .github/workflows/ci.yml

name: CI Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Cache dependencies
        uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Lint
        run: |
          ruff check src/
          black --check src/

      - name: Type check
        run: |
          mypy src/

      - name: Test
        run: |
          pytest tests/ -v --cov=src --cov-report=xml

      - name: Security audit
        run: |
          pip-audit || true

  build:
    needs: test
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Build package
        run: |
          pip install build
          python -m build

      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: dist
          path: dist/
```

### 8.2 Docker优化

```dockerfile
# Dockerfile

FROM python:3.11-slim as builder

WORKDIR /app

# 安装构建依赖
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# 运行依赖
FROM python:3.11-slim

WORKDIR /app

# 创建非root用户
RUN useradd --create-home appuser
USER appuser

# 复制依赖
COPY --from=builder /root/.local /home/appuser/.local

# 复制应用
COPY --chown=appuser:appuser . .

# 环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

CMD ["python", "-m", "leo_system.cli"]
```

---

## 九、监控与可观测性

### 9.1 结构化日志

```python
# 使用结构化日志便于监控
import logging
import json

class StructuredLogger:
    """结构化日志"""

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)

    def log(self, level: str, message: str, **kwargs):
        """记录结构化日志"""
        log_data = {
            "message": message,
            "level": level,
            **kwargs
        }
        self.logger.log(getattr(logging, level), json.dumps(log_data))

    def info(self, message: str, **kwargs):
        self.log("INFO", message, **kwargs)

    def error(self, message: str, **kwargs):
        self.log("ERROR", message, **kwargs)
```

### 9.2 指标收集

```python
# src/leo_core/metrics.py

from prometheus_client import Counter, Histogram, Gauge
import time

# 请求计数器
REQUEST_COUNT = Counter(
    'leo_requests_total',
    'Total requests',
    ['agent', 'status']
)

# 执行时间直方图
EXECUTION_TIME = Histogram(
    'leo_execution_seconds',
    'Execution time',
    ['agent', 'operation']
)

# 活跃会话 gauge
ACTIVE_SESSIONS = Gauge(
    'leo_active_sessions',
    'Number of active sessions'
)

# 使用示例
def track_execution(agent_name: str):
    def decorator(func):
        def wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = func(*args, **kwargs)
                REQUEST_COUNT.labels(agent=agent_name, status='success').inc()
                return result
            except Exception as e:
                REQUEST_COUNT.labels(agent=agent_name, status='error').inc()
                raise
            finally:
                duration = time.time() - start
                EXECUTION_TIME.labels(agent=agent_name, operation=func.__name__).observe(duration)
        return wrapper
    return decorator
```

---

## 十一、MCP 集成优化 (针对 OpenClaw)

### 11.1 当前架构分析

**MCP 集成现状**:
- MCP Server: `src/leo_gateway/mcp_server.py`
- 配置位置: `.mcp.json` / `mcp.json`
- 暴露工具: 7+ 个
- 暴露资源: 5+ 个

**问题点**:
1. MCP Server 启动依赖本地 Python 环境
2. Tools 和 Resources 定义分散在不同文件
3. 缺乏 MCP 协议的版本管理
4. 错误处理不够友好

### 11.2 MCP 服务标准化

```python
# src/leo_gateway/mcp/__init__.py

from .server import LeoMCPServer
from .tools import TOOL_REGISTRY
from .resources import RESOURCE_REGISTRY
from .prompts import PROMPT_REGISTRY

__all__ = [
    'LeoMCPServer',
    'TOOL_REGISTRY',
    'RESOURCE_REGISTRY',
    'PROMPT_REGISTRY',
]

# src/leo_gateway/mcp/tools.py

from typing import Dict, Callable, Any
from dataclasses import dataclass
from enum import Enum

class ToolCategory(Enum):
    """工具分类"""
    AGENT = "agent"        # Agent 相关
    SKILL = "skill"       # Skill 执行
    MEMORY = "memory"     # 记忆系统
    INTEGRATION = "integration"  # 第三方集成
    SYSTEM = "system"     # 系统操作

@dataclass
class ToolDefinition:
    """工具定义"""
    name: str
    description: str
    category: ToolCategory
    handler: Callable
    input_schema: Dict[str, Any]
    examples: list = None

# 工具注册表
TOOL_REGISTRY: Dict[str, ToolDefinition] = {}

def register_tool(
    name: str,
    description: str,
    category: ToolCategory,
    input_schema: Dict[str, Any],
    examples: list = None
):
    """工具注册装饰器"""
    def decorator(func: Callable):
        tool_def = ToolDefinition(
            name=name,
            description=description,
            category=category,
            handler=func,
            input_schema=input_schema,
            examples=examples
        )
        TOOL_REGISTRY[name] = tool_def
        return func
    return decorator


# 使用示例
@register_tool(
    name="execute_skill",
    description="执行指定的 Leo Skill",
    category=ToolCategory.SKILL,
    input_schema={
        "type": "object",
        "properties": {
            "skill_name": {
                "type": "string",
                "description": "Skill 名称"
            },
            "parameters": {
                "type": "object",
                "description": "Skill 参数"
            }
        },
        "required": ["skill_name"]
    },
    examples=[
        {
            "input": {"skill_name": "realestate_news_publisher", "parameters": {"topic": "宁波房产"}},
            "output": "执行结果"
        }
    ]
)
async def execute_skill(skill_name: str, parameters: dict = None):
    """执行 Skill 的实现"""
    pass
```

### 11.3 MCP 性能优化

```python
# src/leo_gateway/mcp/cache.py

import hashlib
import json
from functools import lru_cache
from typing import Optional, Any
import asyncio

class MCPCache:
    """MCP 专用缓存"""

    def __init__(self, default_ttl: int = 300):
        self.default_ttl = default_ttl
        self._cache: dict = {}
        self._lock = asyncio.Lock()

    def _generate_key(self, *args, **kwargs) -> str:
        """生成缓存键"""
        data = {"args": args, "kwargs": kwargs}
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()

    async def get_or_set(
        self,
        key: str,
        factory,
        ttl: Optional[int] = None
    ) -> Any:
        """获取或设置缓存"""
        async with self._lock:
            if key in self._cache:
                return self._cache[key]

            # 异步获取数据
            if asyncio.iscoroutinefunction(factory):
                value = await factory()
            else:
                value = factory()

            self._cache[key] = value
            return value


# Resource 缓存优化
class ResourceCache:
    """资源缓存管理器"""

    # 缓存策略配置
    CACHE_STRATEGY = {
        "leo://skills/registry": {"ttl": 3600, "cache": True},      # Skills 不常变化
        "leo://agents/list": {"ttl": 3600, "cache": True},         # Agents 不常变化
        "leo://memory/shared": {"ttl": 60, "cache": False},        # Memory 频繁变化
        "leo://gateway/status": {"ttl": 10, "cache": True},         # 状态实时性要求高
        "leo://user/profile": {"ttl": 300, "cache": True},         # 用户信息中等变化
    }

    @classmethod
    def should_cache(cls, uri: str) -> bool:
        """判断资源是否应该缓存"""
        strategy = cls.CACHE_STRATEGY.get(uri, {})
        return strategy.get("cache", True)

    @classmethod
    def get_ttl(cls, uri: str) -> int:
        """获取资源缓存时间"""
        strategy = cls.CACHE_STRATEGY.get(uri, {})
        return strategy.get("ttl", 300)
```

### 11.4 MCP 错误处理优化

```python
# src/leo_gateway/mcp/errors.py

from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel

class MCPErrorCode(Enum):
    """MCP 错误码"""
    TOOL_NOT_FOUND = "TOOL_NOT_FOUND"
    TOOL_EXECUTION_ERROR = "TOOL_EXECUTION_ERROR"
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    RESOURCE_READ_ERROR = "RESOURCE_READ_ERROR"
    INVALID_INPUT = "INVALID_INPUT"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"

class MCPError(Exception):
    """MCP 基础异常"""

    def __init__(
        self,
        code: MCPErrorCode,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "error": {
                "code": self.code.value,
                "message": self.message,
                "details": self.details
            }
        }

# 错误响应格式化
def format_error_response(error: Exception) -> Dict[str, Any]:
    """格式化错误响应"""
    if isinstance(error, MCPError):
        return error.to_dict()

    # 未知错误
    return {
        "error": {
            "code": MCPErrorCode.INTERNAL_ERROR.value,
            "message": str(error),
            "details": {"type": type(error).__name__}
        }
    }
```

### 11.5 MCP 监控与日志

```python
# src/leo_gateway/mcp/monitoring.py

import time
from typing import Dict, Any
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class MCPRequest:
    """MCP 请求记录"""
    request_id: str
    tool_name: str
    start_time: float
    end_time: float = 0
    status: str = "pending"  # pending, success, error
    error: str = ""
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Any = None

class MCPMonitor:
    """MCP 监控"""

    def __init__(self, max_records: int = 1000):
        self.max_records = max_records
        self._requests: list = []

    def record(self, request: MCPRequest):
        """记录请求"""
        self._requests.append(request)
        # 保持最大记录数
        if len(self._requests) > self.max_records:
            self._requests = self._requests[-self.max_records:]

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        if not self._requests:
            return {"total": 0}

        total = len(self._requests)
        success = len([r for r in self._requests if r.status == "success"])
        errors = len([r for r in self._requests if r.status == "error"])

        # 计算平均响应时间
        completed = [r for r in self._requests if r.end_time > 0]
        avg_time = sum(r.end_time - r.start_time for r in completed) / len(completed) if completed else 0

        return {
            "total": total,
            "success": success,
            "error": errors,
            "success_rate": success / total if total > 0 else 0,
            "avg_response_time": avg_time,
        }

# 全局监控实例
mcp_monitor = MCPMonitor()
```

### 11.6 MCP 配置文件优化

```json
// .mcp.json (优化版)

{
  "mcpServers": {
    "leo-system": {
      "command": "python",
      "args": ["src/leo_gateway/mcp_server.py"],
      "env": {
        "LEO_WORKSPACE": "D:/桌面/leo_ai_system",
        "OPENCLAW_GATEWAY": "http://127.0.0.1:18789",
        "PYTHONUTF8": "1",
        "LOG_LEVEL": "INFO",
        "MCP_CACHE_TTL": "300",
        "MCP_RATE_LIMIT": "100"  // 每分钟最大请求数
      },
      "cwd": "D:/桌面/leo_ai_system",
      "metadata": {
        "version": "2.0.0",
        "description": "Leo AI System MCP Server",
        "author": "Leo Team",
        "repository": "https://github.com/..."
      }
    }
  },

  "_tools": {
    "execute_skill": {
      "version": "2.0",
      "deprecated": false,
      "category": "skill"
    },
    "delegate_to_agent": {
      "version": "2.0",
      "deprecated": false,
      "category": "agent"
    }
  },

  "_resources": {
    "cache_strategy": {
      "leo://skills/registry": {"ttl": 3600},
      "leo://agents/list": {"ttl": 3600},
      "leo://memory/shared": {"ttl": 60}
    }
  }
}
```

---

## 十二、实施路线图

### 阶段一：基础设施优化 (1-2周)
- [ ] 统一依赖管理 (Poetry)
- [ ] 完善类型注解
- [ ] 标准化日志系统

### 阶段二：代码质量提升 (2-3周)
- [ ] 统一Agent/Skill接口
- [ ] 完善错误处理
- [ ] 增加单元测试覆盖

### 阶段三：MCP 集成优化 (2周)
- [ ] MCP 工具/资源标准化注册
- [ ] MCP 缓存策略实现
- [ ] MCP 监控与日志完善

### 阶段四：性能优化 (2周)
- [ ] 实现缓存策略
- [ ] 优化数据库连接
- [ ] 添加性能监控

### 阶段五：安全加固 (1-2周)
- [ ] 输入验证增强
- [ ] 敏感数据过滤
- [ ] 速率限制实现

### 阶段六：DevOps完善 (2周)
- [ ] CI/CD流程优化
- [ ] Docker镜像优化
- [ ] 监控告警搭建

---

## 十三、总结

本优化方案涵盖:

| 类别 | 关键改进 |
|------|---------|
| **架构** | 模块化重构、接口标准化、事件驱动 |
| **MCP集成** | 工具注册标准化、缓存策略、监控完善 |
| **质量** | 类型注解、错误处理、日志标准化 |
| **测试** | 测试结构、Fixtures、覆盖率目标 |
| **性能** | 缓存策略、连接池、异步优化 |
| **安全** | 输入验证、敏感数据、速率限制 |
| **运维** | CI/CD、Docker、监控可观测性 |

**MCP 集成优化要点**:
1. **标准化**: 统一工具/资源注册机制
2. **性能**: 分级缓存策略，减少重复调用
3. **监控**: 请求追踪、错误统计、性能指标
4. **容错**: 友好的错误提示、降级处理

建议按阶段实施，优先完成基础设施和MCP集成优化部分，再逐步推进性能和运维优化。
