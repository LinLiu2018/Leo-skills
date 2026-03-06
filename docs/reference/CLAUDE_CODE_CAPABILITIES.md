# Claude Code 能力完全指南

> Claude Code CLI v2.1.63 完整能力索引
> 基于官方文档: https://code.claude.com/docs/

---

## 目录

1. [核心命令](#1-核心命令)
2. [CLI 参数](#2-cli-参数)
3. [内置技能 (Bundled Skills)](#3-内置技能-bundled-skills)
4. [自定义技能 (Skills)](#4-自定义技能-skills)
5. [子代理 (Subagents)](#5-子代理-subagents)
6.钩子](#6-hook [Hook -钩子)
7. [MCP 服务器](#7-mcp-服务器)
8. [权限系统](#8-权限系统)
9. [记忆系统](#9-记忆系统)
10. [插件系统](#10-插件系统)

---

## 1. 核心命令

### 基础会话命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `claude` | 启动交互式会话 | `claude` |
| `claude "query"` | 带初始提示启动会话 | `claude "explain this project"` |
| `claude -p "query"` | SDK模式查询后退出 | `claude -p "explain this function"` |
| `claude -c` | 继续当前目录最近会话 | `claude -c` |
| `claude -r "<session>" "query"` | 恢复指定会话 | `claude -r "auth-refactor" "Finish this PR"` |

### 认证命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `claude auth login` | 登录 Anthropic 账户 | `claude auth login --email user@example.com --sso` |
| `claude auth logout` | 登出账户 | `claude auth logout` |
| `claude auth status` | 查看认证状态 | `claude auth status` |

### 管理命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `claude update` | 更新到最新版本 | `claude update` |
| `claude agents` | 列出所有子代理 | `claude agents` |
| `claude mcp` | 配置MCP服务器 | 见MCP文档 |
| `claude remote-control` | 启动远程控制会话 | `claude remote-control` |

---

## 2. CLI 参数

### 会话控制

| 参数 | 说明 | 示例 |
|------|------|------|
| `--continue`, `-c` | 加载最近会话 | `claude --continue` |
| `--resume`, `-r` | 恢复指定会话 | `claude -r session-id` |
| `--fork-session` | 恢复时创建新会话ID | `claude --resume abc --fork-session` |
| `--session-id` | 使用指定会话ID | `claude --session-id 550e8400-...` |
| `--no-session-persistence` | 禁用会话持久化 | `claude -p --no-session-persistence "query"` |

### 输入输出模式

| 参数 | 说明 | 示例 |
|------|------|------|
| `--print`, `-p` | 非交互式打印模式 | `claude -p "query"` |
| `--output-format` | 输出格式 (text/json/stream-json) | `claude -p --output-format json "query"` |
| `--input-format` | 输入格式 | `claude -p --input-format stream-json` |

### 模型控制

| 参数 | 说明 | 示例 |
|------|------|------|
| `--model` | 指定模型 | `claude --model claude-sonnet-4-6` |
| `--fallback-model` | 备用模型 | `claude -p --fallback-model sonnet "query"` |
| `--betas` | Beta特性头 | `claude --betas interleaved-thinking` |

### 系统提示词

| 参数 | 说明 | 示例 |
|------|------|------|
| `--system-prompt` | 替换整个系统提示 | `claude --system-prompt "You are a Python expert"` |
| `--system-prompt-file` | 从文件加载系统提示 | `claude -p --system-prompt-file ./prompt.txt "query"` |
| `--append-system-prompt` | 追加系统提示 | `claude --append-system-prompt "Always use TypeScript"` |
| `--append-system-prompt-file` | 从文件追加提示 | `claude -p --append-system-prompt-file ./rules.txt "query"` |

### 工具权限

| 参数 | 说明 | 示例 |
|------|------|------|
| `--allowedTools` | 允许的工具 | `--allowedTools "Bash(git *)" "Read" "Edit"` |
| `--disallowedTools` | 禁止的工具 | `--disallowedTools "Bash rm *" "Write"` |
| `--tools` | 限制可用工具 | `--tools "Bash,Edit,Read"` |
| `--dangerously-skip-permissions` | 跳过所有权限提示 | `claude --dangerously-skip-permissions` |
| `--permission-mode` | 权限模式 | `--permission-mode plan` |

### 工作目录

| 参数 | 说明 | 示例 |
|------|------|------|
| `--add-dir` | 添加额外工作目录 | `claude --add-dir ../apps ../lib` |
| `--worktree`, `-w` | 在git worktree中启动 | `claude -w feature-auth` |

### 其他常用参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `--max-turns` | 最大交互次数 | `claude -p --max-turns 3 "query"` |
| `--max-budget-usd` | 最大API花费 | `claude -p --max-budget-usd 5.00 "query"` |
| `--debug` | 调试模式 | `claude --debug "api,mcp"` |
| `--verbose` | 详细日志 | `claude --verbose` |
| `--version`, `-v` | 版本号 | `claude -v` |
| `--init` | 运行初始化hook | `claude --init` |
| `--init-only` | 仅运行hook后退出 | `claude --init-only` |

---

## 3. 内置技能 (Bundled Skills)

Claude Code 内置了以下技能，直接使用 `/技能名` 调用：

### `/simplify`
- **用途**: 审查最近修改的文件，检查代码复用、质量和效率问题，然后修复
- **用法**: 在实现功能或修复bug后运行
- **特性**: 并行启动3个审查代理（代码复用、代码质量、效率），汇总发现并应用修复

### `/batch`
- **用途**: 跨代码库编排大规模变更
- **用法**: `/batch migrate src/ from Solid to React`
- **特性**: 研究代码库，将工作分解为5-30个独立单元，在隔离的git worktree中并行执行

### `/debug`
- **用途**: 排查当前Claude Code会话问题
- **用法**: `/debug` 或 `/debug [描述问题]`
- **特性**: 读取会话调试日志，可选聚焦分析

---

## 4. 自定义技能 (Skills)

### 技能文件结构

```
my-skill/
├── SKILL.md           # 主指令（必需）
├── reference.md       # 参考文档
├── examples/          # 示例
└── scripts/           # 脚本
```

### SKILL.md 格式

```yaml
---
name: my-skill                    # 技能名称（成为 /my-skill 命令）
description: 技能描述              # 帮助Claude决定何时使用
disable-model-invocable: true     # 禁止自动调用
allowed-tools: Read, Grep         # 允许的工具
user-invocable: false            # 隐藏自/菜单
context: fork                     # 在子代理中运行
---

# 技能指令...
```

### Frontmatter 字段

| 字段 | 说明 |
|------|------|
| `name` | 技能名称 |
| `description` | 描述（推荐填写） |
| `argument-hint` | 参数提示 |
| `disable-model-invocation` | 禁止自动调用 |
| `user-invocable` | 是否可从菜单调用 |
| `allowed-tools` | 可用工具列表 |
| `model` | 使用的模型 |
| `context` | `fork`表示在子代理运行 |
| `hooks` | 技能生命周期钩子 |

### 字符串替换

| 变量 | 说明 |
|------|------|
| `$ARGUMENTS` | 调用时传递的所有参数 |
| `$ARGUMENTS[N]` | 按索引访问参数 |
| `$N` | `$ARGUMENTS[N]`的简写 |
| `${CLAUDE_SESSION_ID}` | 当前会话ID |

### 动态上下文注入

使用 ```!<command>``` 语法在技能执行前运行命令：

```yaml
---
name: pr-summary
context: fork
agent: Explore
allowed-tools: Bash(gh *)
---

## PR Context
- Diff: !`gh pr diff`
- Comments: !`gh pr view --comments`
```

---

## 5. 子代理 (Subagents)

### 内置子代理类型

| 类型 | 用途 |
|------|------|
| `Explore` | 探索代码库（只读工具） |
| `Plan` | 规划实现方案 |
| `general-purpose` | 通用任务 |

### 定义子代理

```bash
claude --agents '{
  "reviewer": {
    "description": "代码审查专家",
    "prompt": "你是一位高级代码审查员...",
    "tools": ["Read", "Grep", "Glob", "Bash"],
    "model": "sonnet"
  }
}'
```

### 子代理字段

| 字段 | 说明 |
|------|------|
| `description` | 何时调用 |
| `prompt` | 系统提示 |
| `tools` | 可用工具 |
| `disallowedTools` | 禁止工具 |
| `model` | 模型选择 |
| `skills` | 预加载技能 |
| `mcpServers` | MCP服务器 |
| `maxTurns` | 最大轮次 |

---

## 6. Hook 钩子

### Hook 类型

| 事件 | 说明 |
|------|------|
| `SessionStart` | 会话开始时 |
| `MessageStart` | 消息开始时 |
| `ToolStart` | 工具执行前 |
| `ToolEnd` | 工具执行后 |
| `Notification` | 通知时 |

### hooks.json 格式

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|resume",
        "hooks": [
          {
            "type": "command",
            "command": "bash ./scripts/session-start.sh",
            "async": false
          }
        ]
      }
    ]
  }
}
```

---

## 7. MCP 服务器

### 配置方式

```bash
# 从文件加载
claude --mcp-config ./mcp.json

# 严格模式（仅用指定配置）
claude --strict-mcp-config --mcp-config ./mcp.json
```

### mcp.json 格式

```json
{
  "mcpServers": {
    "server-name": {
      "command": "npx",
      "args": ["-y", "@example/mcp-server"],
      "env": {}
    }
  }
}
```

---

## 8. 权限系统

### 权限模式

| 模式 | 说明 |
|------|------|
| `accept` | 自动接受所有操作 |
| `plan` | 计划模式，列出操作但不执行 |
| `review` | 每次操作需要确认 |
| `browse` | 浏览模式 |

### 权限规则语法

```
# 允许特定工具
Allow: Bash(git *)

# 拒绝特定工具
Deny: Bash(rm *)

# 拒绝所有
Deny: *

# 允许特定技能
Allow: Skill(commit)
```

---

## 9. 记忆系统

### CLAUDE.md

项目根目录的 `CLAUDE.md` 文件会在每次会话开始时加载。

### 自动记忆

Claude Code 自动保存学习到的信息：
- 构建命令
- 调试技巧
- 项目特定知识

### 字符串替换

| 变量 | 说明 |
|------|------|
| `$CLAUDE_ROOT` | 项目根目录 |
| `$CLAUDE_SESSION_ID` | 会话ID |

---

## 10. 插件系统

### 插件结构

```
my-plugin/
├── plugin.json        # 插件清单
├── skills/           # 技能
├── agents/           # 子代理
├── commands/         # 命令
├── hooks/            # 钩子
└── mcp/             # MCP服务器
```

### plugin.json 格式

```json
{
  "name": "my-plugin",
  "displayName": "My Plugin",
  "version": "1.0.0",
  "skills": "./skills/",
  "agents": "./agents/",
  "commands": "./commands/",
  "hooks": "./hooks/hooks.json"
}
```

### 加载插件

```bash
claude --plugin-dir ./my-plugins
```

---

## 快速参考

### 常用命令组合

```bash
# 交互式审查代码
claude

# 非交互式查询
claude -p --output-format json "解释这个函数" | jq

# 继续会话
claude -c

# 在worktree中工作
claude -w feature-branch

# 限制工具权限
claude --tools "Read,Grep,Bash"

# 追加自定义规则
claude --append-system-prompt "始终使用TypeScript"
```

---

## 相关资源

- 官方文档: https://code.claude.com/docs/
- GitHub: https://github.com/anthropics/claude-code
- Agent SDK: https://platform.claude.com/docs/en/agent-sdk/overview
