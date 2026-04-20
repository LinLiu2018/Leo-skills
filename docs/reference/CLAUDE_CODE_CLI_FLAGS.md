# Claude Code CLI Flags 完整清单

> 最后更新: 2026-04-15

## 使用方式

```bash
# 单个 flag
claude --flag

# 多个 flags
claude --flag1 --flag2

# 在 settings.json 中配置
{
  "launchFlags": ["--flag1", "--flag2"]
}
```

---

## 完整 Flags 列表

### 核心选项

| Flag | 说明 | 使用场景 |
|------|------|----------|
| `--version`, `-v` | 输出版本号 | 查版本 |
| `--help`, `-h` | 显示帮助 | 忘记命令时 |
| `--debug` | 启用调试模式 | 排查问题时 |
| `--debug-file <path>` | 写入调试日志 | 详细日志分析 |

### 会话管理

| Flag | 说明 | 使用场景 |
|------|------|----------|
| `--continue`, `-c` | 继续最新会话 | 继续之前工作 |
| `--continue -p <query>` | 通过 SDK 继续 | 自动化脚本 |
| `--resume <session>` | 恢复指定会话 | 按 ID 恢复 |
| `--session-id <id>` | 使用特定会话 | 多会话管理 |
| `--fork-session` | 创建新会话 ID | 分支工作 |
| `--no-session-persistence` | 禁用会话持久化 | 临时会话 |
| `--new` | 清除并新建会话 | 全新开始 |

### 模型选择

| Flag | 说明 | 使用场景 |
|------|------|----------|
| `--model <model>` | 设置默认模型 | 切换模型 |
| `--fallback-model <model>` | 备用模型 | 主模型失败时 |
| `--effort <level>` | 努力级别 | 控制深度 |

### 权限和安全

| Flag | 说明 | 使用场景 |
|------|------|----------|
| `--permission-mode <mode>` | 权限模式 | 自动化场景 |
| `--allow-dangerously-skip-permissions` | 跳过权限 | CI/CD |
| `--dangerously-skip-permissions` | 跳过所有检查 | 完全自动化 |
| `--sandbox` | 启用沙箱 | 安全隔离 |

### MCP 和扩展

| Flag | 说明 | 使用场景 |
|------|------|----------|
| `--mcp-config <path>` | MCP 配置路径 | 指定 MCP 服务器 |
| `--strict-mcp-config` | 仅用指定配置 | 隔离环境 |
| `--plugin-dir <path>` | 插件目录 | 加载自定义插件 |
| `--agents` | 动态定义代理 | 自定义代理 |

### 项目和目录

| Flag | 说明 | 使用场景 |
|------|------|----------|
| `--add-dir <path>` | 添加工作目录 | 多项目管理 |
| `--worktree <name>` | Git worktree | 隔离分支 |
| `--bare` | 跳过自动发现 | 最小化加载 |

### 输出和显示

| Flag | 说明 | 使用场景 |
|------|------|----------|
| `--output-format <format>` | 输出格式 | 程序化处理 |
| `--print`, `-p` | 打印模式 | 非交互查询 |
| `--verbose` | 详细输出 | 调试 |
| `--include-partial-messages` | 包含部分消息 | 流式处理 |

### IDE 集成

| Flag | 说明 | 使用场景 |
|------|------|----------|
| `--ide <name>` | 指定 IDE | VSCode/JetBrains |
| `--no-chrome` | 禁用 Chrome | 不需要浏览器 |
| `--chrome` | 启用 Chrome | 浏览器自动化 |

### 高级选项

| Flag | 说明 | 使用场景 |
|------|------|----------|
| `--betas <header>` | Beta 头信息 | 测试新功能 |
| `--max-budget-usd <amount>` | 最大消费 | 成本控制 |
| `--max-turns <n>` | 最大轮次 | 防止无限循环 |
| `--input-format <format>` | 输入格式 | 处理管道 |
| `--json-schema <schema>` | JSON Schema | 结构化输出 |
| `--system-prompt <text>` | 替换系统提示 | 自定义行为 |
| `--append-system-prompt <text>` | 追加系统提示 | 额外上下文 |
| `--append-system-prompt-file <path>` | 从文件加载 |  |

### 远程和协作

| Flag | 说明 | 使用场景 |
|------|------|----------|
| `--remote` | 创建 Web 会话 | 远程协作 |
| `--remote-control`, `--rc` | 远程控制 | 远程操作 |
| `--teleport` | 拉取 Web 会话 | 迁移会话 |
| `--from-pr <pr>` | 从 PR 恢复 | 代码审查 |

### 初始化

| Flag | 说明 | 使用场景 |
|------|------|----------|
| `--init` | 运行初始化钩子 | 首次启动 |
| `--init-only` | 仅运行初始化 | 配置检查 |
| `--exclude-dynamic-system-prompt-sections` | 排除动态部分 | 最小化 |

### 其他

| Flag | 说明 | 使用场景 |
|------|------|----------|
| `--disable-slash-commands` | 禁用斜杠命令 | 防止误触 |
| `--replay-user-messages` | 重放用户消息 | 测试 |
| `--setting-sources` | 显示设置源 | 调试配置 |
| `--tmux` | 创建 tmux 会话 | tmux 集成 |
| `--channels` | MCP 通道 | 通知 |

---

## 在 settings.json 中配置默认 Flags

```json
{
  "launchFlags": [
    "--verbose",
    "--debug-file .claude/debug.log",
    "--max-turns 50"
  ]
}
```

---

## 权限模式

| 模式 | 说明 |
|------|------|
| `default` | 每次操作前询问 |
| `acceptEdits` | 自动批准编辑 |
| `plan` | 分析后再编辑 |
| `auto` | 自动模式（需订阅） |
| `dontAsk` | 仅使用预批准工具 |
| `bypassPermissions` | 跳过所有检查 |

---

## 环境变量

| 变量 | 说明 |
|------|------|
| `ANTHROPIC_API_KEY` | API 密钥 |
| `ANTHROPIC_BASE_URL` | API 基础 URL |
| `CLAUDE_CODE_SIMPLE` | 最小模式 |
| `CLAUDE_CODE_DEBUG_LOGS_DIR` | 调试日志目录 |
| `CLAUDE_REMOTE_CONTROL_SESSION_NAME_PREFIX` | 远程会话前缀 |
