# Continuous Learning v2 实现机制深度分析

> **分析日期**: 2026-04-15
> **来源**: everything-claude-code 源码分析
> **关键文件**: observe.sh, instinct-cli.py, detect-project.sh

---

## 一、整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                    Continuous Learning v2 架构                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐   │
│  │ PreToolUse   │     │ PostToolUse │     │ SessionStart │   │
│  │    Hook      │     │    Hook     │     │    Hook     │   │
│  └──────┬───────┘     └──────┬───────┘     └──────┬───────┘   │
│         │                      │                      │            │
│         └──────────────────────┴──────────────────────┘        │
│                                    │                              │
│                                    ▼                              │
│                    ┌───────────────────────────┐               │
│                    │     observe.sh (观察器)     │               │
│                    │  - 捕获工具调用事件          │               │
│                    │  - 项目上下文检测           │               │
│                    │  - 敏感信息清理             │               │
│                    └─────────────┬─────────────┘               │
│                                  │                               │
│                                  ▼                               │
│                    ┌───────────────────────────┐               │
│                    │   observations.jsonl       │               │
│                    │   (原始观察记录)           │               │
│                    └─────────────┬─────────────┘               │
│                                  │                               │
│                                  ▼                               │
│                    ┌───────────────────────────┐               │
│                    │   Observer Agent           │               │
│                    │  (后台异步分析)            │               │
│                    │  - 模式检测                │               │
│                    │  - 本能生成                │               │
│                    └─────────────┬─────────────┘               │
│                                  │                               │
│                                  ▼                               │
│                    ┌───────────────────────────┐               │
│                    │   instincts/              │               │
│                    │   (学习到的本能)           │               │
│                    └───────────────────────────┘               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 二、核心组件

### 2.1 观察器 (observe.sh)

**职责**：在每次工具使用时自动捕获事件

**核心流程**：

```bash
# 1. 接收 Hook 参数 (pre/post)
HOOK_PHASE="${1:-post}"

# 2. 读取 Claude Code 传递的 JSON
INPUT_JSON=$(cat)

# 3. 项目检测
source "${SKILL_ROOT}/scripts/detect-project.sh"
# → PROJECT_ID, PROJECT_NAME, PROJECT_ROOT, PROJECT_DIR

# 4. 解析事件
PARSED=$(echo "$INPUT_JSON" | python3 -c '...解析工具调用...')

# 5. 清理敏感信息 (API keys, tokens, passwords)
_SECRET_RE = re.compile(r"(?i)(api[_-]?key|token|secret|password|...)")

# 6. 写入观察日志
echo "$PARSED" >> "${PROJECT_DIR}/observations.jsonl"
```

**事件格式**：

```json
{
  "timestamp": "2026-04-15T10:30:00Z",
  "event": "tool_complete",
  "tool": "Bash",
  "input": "grep -r 'pattern' src/",
  "output": "...(truncated)...",
  "session": "session-id",
  "project_id": "abc123",
  "project_name": "my-project"
}
```

**防抖机制**：

```bash
# 每 20 次观察才通知一次 Observer (避免频繁信号)
SIGNAL_EVERY_N="${ECC_OBSERVER_SIGNAL_EVERY_N:-20}"
```

### 2.2 项目检测 (detect-project.sh)

**职责**：确定当前操作属于哪个项目

**检测优先级**：

```
1. CLAUDE_PROJECT_DIR 环境变量
2. git remote URL (跨机器一致)
3. git repo root path (机器特定)
4. "global" (无项目上下文)
```

**项目隔离**：

```bash
# 每个项目有独立的目录
~/.claude/homunculus/projects/<project_id>/
├── instincts/
│   ├── personal/      # 本项目本能
│   └── inherited/      # 继承的全局本能
├── observations.jsonl  # 观察日志
├── observations.archive/
└── evolved/           # 进化后的 skills/commands/agents
```

### 2.3 本能 CLI (instinct-cli.py)

**职责**：管理本能（instincts）的生命周期

**命令**：

| 命令 | 功能 |
|------|------|
| `status` | 显示所有本能及置信度 |
| `import` | 从文件/URL 导入本能 |
| `export` | 导出本能到文件 |
| `evolve` | 将本能聚类为 skills/commands/agents |
| `promote` | 将项目本能提升为全局 |
| `projects` | 列出所有项目和本能数量 |
| `prune` | 删除超过 30 天的本能 |

**本能数据结构**：

```yaml
---
id: pattern-use-react-hooks
trigger: "使用 React 组件时"
action: "优先使用 React Hooks 而非 class 组件"
confidence: 0.8
domain: code-style
scope: project
evidence:
  - "2026-04-10: 在 components/UserCard.tsx 中观察到"
  - "2026-04-12: 在 hooks/useAuth.ts 中观察到"
created_at: 2026-04-10
expires_at: 2026-04-25
---
```

### 2.4 后台观察者 (Observer Agent)

**职责**：异步分析观察日志，生成本能

**触发条件**：
- 每 N 次观察后（默认 20）
- 或定时触发（默认 5 分钟）

**分析流程**：

```
1. 读取 observations.jsonl
2. 聚类相似模式
3. 计算置信度
4. 生成本能建议
5. 写入 instincts/personal/
```

---

## 三、项目隔离机制

### 3.1 为什么需要项目隔离？

| 问题 | 无隔离时的风险 |
|------|---------------|
| 跨项目污染 | Python 项目的 "缩进风格" 学到 JS 项目的 |
| 隐私 | A 公司的代码模式暴露给 B 项目 |
| 噪声 | 大量无关本能堆积 |

### 3.2 隔离策略

```
Project A                    Project B
├── instincts/personal/      ├── instincts/personal/
│   ├── react-hooks.yaml   │   ├── django-patterns.yaml
│   └── api-style.yaml      │   └── auth-patterns.yaml
└── evolved/                └── evolved/

Global (共享)
├── instincts/inherited/    ← 从多个项目提升的全局本能
└── instincts/personal/     ← 全局通用本能
```

### 3.3 提升机制

```
项目本能 (confidence >= 0.8)
        ↓
在 2+ 项目中出现
        ↓
提升为全局本能 → instincts/inherited/
```

---

## 四、置信度系统

### 4.1 置信度等级

| 等级 | 值 | 含义 |
|------|-----|------|
| 试探性 | 0.3 - 0.4 | 偶尔观察到，不确定 |
| 中等 | 0.5 - 0.6 | 多次观察到 |
| 高置信 | 0.7 - 0.8 | 经常观察到 |
| 确定 | 0.9 | 几乎每次都这样 |

### 4.2 置信度计算

```python
# 简化模型
confidence = base_score * frequency_weight * recency_weight

# base_score: 初始分数 (0.3)
# frequency_weight: 观察频率 (0.5 - 1.0)
# recency_weight: 最近观察权重 (衰减)
```

---

## 五、Hooks 注册机制

### 5.1 settings.json 配置

```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "${CLAUDE_PLUGIN_ROOT}/skills/continuous-learning-v2/hooks/observe.sh pre"
      }]
    }],
    "PostToolUse": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "${CLAUDE_PLUGIN_ROOT}/skills/continuous-learning-v2/hooks/observe.sh post"
      }]
    }]
  }
}
```

### 5.2 生命周期

```
SessionStart → 加载之前上下文
    ↓
工具调用 → PreToolUse Hook → 观察 → PostToolUse Hook → 观察
    ↓
观察累积 → Observer Agent 分析
    ↓
SessionEnd → 保存状态
    ↓
下次会话 → SessionStart → 加载学到的本能
```

---

## 六、对 LEO 系统的借鉴意义

### 6.1 可复制的设计

| 设计 | LEO 可用性 | 说明 |
|------|-----------|------|
| Hooks 观察机制 | ✅ 直接复制 | PreToolUse/PostToolUse |
| 项目隔离 | ✅ 参考实现 | 每个项目独立存储 |
| 置信度系统 | ✅ 参考实现 | 0.3-0.9 分级 |
| 本能进化 | ⚠️ 需要适配 | 聚类分析算法 |

### 6.2 LEO 可用的简化方案

```
LEO 长期记忆 = Hooks 观察 + 项目隔离存储 + 本能文件
```

**最小实现**：

```python
# LEO 观察 Hook (伪代码)
class LearningHook:
    def on_tool_use(self, tool, input, output):
        observation = {
            "tool": tool,
            "input": sanitize(input),  # 清理敏感
            "output": sanitize(output),
            "timestamp": now(),
            "project": detect_project()
        }
        append_to_log(observation)

    def analyze(self):
        # 简单模式检测
        patterns = cluster_similar(self.observations)
        instincts = [to_instinct(p) for p in patterns]
        save(instincts)
```

---

## 七、关键源码文件

| 文件 | 路径 | 功能 |
|------|------|------|
| observe.sh | `skills/continuous-learning-v2/hooks/` | 观察 Hook |
| detect-project.sh | `skills/continuous-learning-v2/scripts/` | 项目检测 |
| instinct-cli.py | `skills/continuous-learning-v2/scripts/` | 本能管理 CLI |
| start-observer.sh | `skills/continuous-learning-v2/agents/` | Observer 启动器 |
| config.json | `skills/continuous-learning-v2/` | 配置 |

---

## 八、总结

| 组件 | 职责 | 可复用度 |
|------|------|---------|
| observe.sh | 事件捕获 | ⭐⭐⭐⭐⭐ |
| detect-project.sh | 项目隔离 | ⭐⭐⭐⭐⭐ |
| instinct-cli.py | 生命周期管理 | ⭐⭐⭐⭐ |
| 置信度系统 | 模式评估 | ⭐⭐⭐⭐ |
| Observer Agent | 异步分析 | ⭐⭐⭐ |

**核心创新**：
1. **项目隔离**：防止跨项目污染
2. **置信度**：0.3-0.9 量化学习确定性
3. **后台分析**：不阻塞主会话
4. **隐私优先**：敏感信息自动清理

---

## 参考链接

- [everything-claude-code](https://github.com/affaan-m/everything-claude-code)
- [continuous-learning-v2 SKILL.md](https://github.com/affaan-m/everything-claude-code/blob/main/skills/continuous-learning-v2/SKILL.md)
