# AI Agent 架构实现指南

> 本文档说明如何在 Leo AI System 中实现 Claude Code Agent SDK、MCP 协议、Hook 系统

---

## 架构概览

```
┌─────────────────────────────────────────────────────────────────┐
│                         用户交互层                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │ 飞书     │  │ 命令行   │  │ Claude   │  │ 其他渠道 │        │
│  │ (OpenClaw)│  │ (CLI)    │  │ Code     │  │         │        │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘        │
│       └─────────────┴─────────────┴─────────────┘               │
│                         │                                       │
└─────────────────────────┼───────────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Leo Gateway (网关层)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Router       │  │ Session      │  │ Protocol     │          │
│  │ (消息路由)    │  │ (会话管理)    │  │ (协议转换)    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ MCP Server (Model Context Protocol)                       │  │
│  │ ├─ Tools: execute_skill, delegate_to_agent, remember...   │  │
│  │ └─ Resources: skills, agents, memory, gateway_status      │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Agent Orchestrator (编排层)                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │ code-    │  │ documen- │  │ research │  │ project- │        │
│  │ reviewer │  │ ter      │  │ er       │  │ refactor │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Task Queue (异步任务队列)                                 │   │
│  │ - 并行执行多个 Agent                                      │   │
│  │ - 任务状态追踪                                            │   │
│  │ - 结果汇总                                                │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Skill Layer (技能层)                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │ file_ops │  │ web_fetch│  │ data_proc│  │ feishu   │        │
│  │ (文件操作)│  │ (网页获取)│  │ (数据处理)│  │ (飞书)   │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 第一步：激活 MCP Server

### 1.1 当前状态

✅ **已完成**:
- `mcp_server.py` - MCP 服务器实现 (650 行)
- `mcp.json` - 配置文件
- 8 个 Tools 定义
- 5 个 Resources 定义

⏳ **待激活**:
- 启动 MCP Server
- 让 Claude Code 连接

### 1.2 启动步骤

```bash
# 1. 安装 MCP 依赖
pip install mcp

# 2. 使用启动脚本
bash scripts/mcp/start_mcp_server.sh

# 3. 或在 Claude Code 中启动
claude --mcp-config ./mcp.json
```

### 1.3 验证连接

启动后，Claude Code 可以调用以下能力：

```
Tools (工具):
- execute_skill: 执行 Leo Skill
- delegate_to_agent: 委托给 Agent
- search_skills: 搜索 Skills
- remember/recall: 记忆存储/检索
- send_to_feishu: 发送到飞书

Resources (资源):
- leo://skills/registry: 技能注册表
- leo://agents/list: Agent 列表
- leo://memory/shared: 共享记忆
- leo://gateway/status: 网关状态
- leo://user/profile: 用户画像
```

---

## 第二步：完善 Agent 系统

### 2.1 Agent 定义 (已有)

| Agent | 文件 | 用途 | 触发方式 |
|-------|------|------|----------|
| code-reviewer | `.claude/agents/code-reviewer.md` | 代码审查 | 手动/MCP调用 |
| researcher | `.claude/agents/researcher.md` | 代码库研究 | 手动/MCP调用 |
| documenter | `.claude/agents/documenter.md` | 文档生成 | 手动/MCP调用 |
| project-refactor | `.claude/agents/project-refactor-agent.md` | 架构重构 | 手动/MCP调用 |

### 2.2 Agent 调用方式

**方式 1: 通过 MCP Tool (推荐)**

```python
# Claude Code 内部调用
result = await tool("delegate_to_agent", {
    "agent_name": "code-reviewer",
    "task": "审查 src/leo_gateway/gateway.py",
    "context": {"focus": "security"}
})
```

**方式 2: 通过 Skill 调用**

```python
# 创建 Skill 包装器
# src/leo_skills/agent_caller.py

async def call_agent(agent_name: str, task: str, **kwargs):
    """调用指定 Agent"""
    from leo_orchestrator.registry import get_registry
    registry = get_registry()
    agent = registry.get_agent(agent_name)
    return await agent.execute(task, **kwargs)
```

**方式 3: 直接 Agent SDK (Claude Code 原生)**

```python
# 使用 Claude Code 的 Agent SDK
from claude_code import Agent

agent = Agent(
    name="code-reviewer",
    description="代码审查专家",
    tools=["Read", "Grep", "Bash"]
)

result = await agent.run("审查 gateway.py")
```

### 2.3 并行 Agent 执行

```python
# 同时运行多个 Agent
import asyncio

async def parallel_agents():
    tasks = [
        delegate_to_agent("code-reviewer", "审查核心模块"),
        delegate_to_agent("documenter", "更新 API 文档"),
        delegate_to_agent("researcher", "分析依赖关系")
    ]
    results = await asyncio.gather(*tasks)
    return results
```

---

## 第三步：完善 Hook 系统

### 3.1 Hook 配置 (已有)

`.claude/hooks.json`:
```json
{
  "hooks": {
    "SessionStart": [...],
    "ToolStart": [...],
    "ToolEnd": [...]
  }
}
```

### 3.2 创建 Hook 脚本

**SessionStart Hook** - 初始化环境:

```bash
#!/bin/bash
# .claude/hooks/session-start.sh

echo "🚀 Leo AI System 启动..."

# 1. 加载用户画像
if [ -f "leo_knowledge/context/user_profile.md" ]; then
    echo "✅ 用户画像已加载"
fi

# 2. 检查 OpenClaw 连接
if curl -s http://127.0.0.1:18789/health > /dev/null; then
    echo "✅ OpenClaw Gateway 连接正常"
else
    echo "⚠️  OpenClaw Gateway 未启动"
fi

# 3. 加载今日任务
if [ -f "docs/progress/progress.md" ]; then
    echo "📋 今日任务:"
    head -20 docs/progress/progress.md
fi

# 4. 注入上下文到 Claude Code
# 通过标准输出让 Claude Code 读取
cat leo_knowledge/context/QUICK_CONTEXT.md
```

**ToolStart Hook** - 记录工具调用:

```bash
#!/bin/bash
# .claude/hooks/tool-start.sh

# 记录所有 Bash 命令
if [ "$1" = "Bash" ]; then
    echo "$(date): Bash command started" >> .claude/logs/tool_usage.log
fi
```

**ToolEnd Hook** - 处理结果:

```bash
#!/bin/bash
# .claude/hooks/tool-end.sh

# 可以在这里做结果后处理
# 例如：自动保存重要结果到记忆
```

---

## 第四步：OpenClaw 集成

### 4.1 OpenClaw Gateway 启动

```bash
# 在 D:\openclaw 目录
cd D:/openclaw
node openclaw.mjs gateway --port 18789
```

### 4.2 Leo Gateway 对接

`src/leo_gateway/channel/openclaw.py`:

```python
class OpenClawChannel:
    """OpenClaw 通道实现"""

    def __init__(self, endpoint="http://127.0.0.1:18789"):
        self.endpoint = endpoint
        self.session = requests.Session()

    async def send_message(self, message: str, user_id: str):
        """发送消息到飞书"""
        response = await self.session.post(
            f"{self.endpoint}/api/message",
            json={
                "content": message,
                "user_id": user_id,
                "source": "leo_gateway"
            }
        )
        return response.json()

    async def receive_message(self) -> Message:
        """接收来自飞书的消息"""
        # 通过 Webhook 或轮询
        pass
```

### 4.3 消息路由

```python
# src/leo_gateway/router.py

class MessageRouter:
    """智能消息路由"""

    async def route(self, message: Message) -> str:
        """决定消息去向"""

        # 1. 检查是否为 Skill 触发
        skill = self.match_skill(message.content)
        if skill:
            return await self.execute_skill(skill, message)

        # 2. 检查是否需要 Agent 处理
        if self.is_complex_task(message.content):
            agent = self.select_agent(message)
            return await self.delegate_to_agent(agent, message)

        # 3. 直接回复
        return await self.generate_reply(message)
```

---

## 第五步：实际使用场景

### 场景 1: 代码变更自动审查

```
用户提交代码变更
    ↓
Hook 触发 (post-commit)
    ↓
调用 code-reviewer Agent
    ↓
生成审查报告
    ↓
通过 MCP send_to_feishu 发送到飞书
```

### 场景 2: 复杂任务并行处理

```
用户: "帮我重构项目并更新文档"
    ↓
Claude Code 分析任务
    ↓
并行启动:
    - project-refactor Agent → 重构代码
    - documenter Agent → 更新文档
    - code-reviewer Agent → 审查变更
    ↓
结果汇总 → 返回给用户
```

### 场景 3: 记忆持久化

```
Claude Code 会话中
    ↓
用户: "记住我是做房地产的"
    ↓
调用 remember Tool
    ↓
保存到 leo://memory/shared
    ↓
下次会话通过 SessionStart Hook 加载
```

---

## 快速启动检查清单

- [ ] 安装 MCP: `pip install mcp`
- [ ] 启动 MCP Server: `bash scripts/mcp/start_mcp_server.sh`
- [ ] 配置 Claude Code: `claude --mcp-config ./mcp.json`
- [ ] 检查 Agent 定义: `ls .claude/agents/`
- [ ] 验证 Hook 配置: 检查 `.claude/hooks.json`
- [ ] 启动 OpenClaw: `cd D:/openclaw && node openclaw.mjs gateway --port 18789`
- [ ] 测试飞书连接: `curl http://127.0.0.1:18789/health`

---

## 故障排查

### MCP Server 无法启动

```bash
# 检查依赖
pip install mcp

# 检查端口占用
netstat -ano | findstr :8080

# 查看日志
tail -f .claude/logs/mcp_server.log
```

### Agent 调用失败

```bash
# 检查 Agent 定义文件
ls -la .claude/agents/

# 检查注册表
python -c "from leo_orchestrator.registry import get_registry; print(get_registry().list_agents())"
```

### OpenClaw 连接失败

```bash
# 检查网关状态
curl http://127.0.0.1:18789/health

# 重启网关
cd D:/openclaw && node openclaw.mjs gateway --port 18789
```

---

## 下一步扩展

1. **更多 Agent**: 创建 test-runner、security-auditor 等
2. **Skill 市场**: 标准化 Skill 开发流程
3. **可视化界面**: Gateway Dashboard
4. **多租户支持**: 区分不同用户/团队的资源
