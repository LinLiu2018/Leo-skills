# OpenClaw 运维日志

## 2026-02-26 Agent Exec 死循环导致飞书卡顿（第二次）

### 故障现象
- 飞书发送消息后一直卡着不动，无响应
- 网关进程在运行，端口 18789 正常监听
- 守护进程日志显示反复重启网关，每次启动两个实例

### 根因分析

#### 直接原因
Agent（Leo）在飞书直聊会话中陷入 exec 工具死循环：
1. Agent 尝试执行 `openclaw cron run <job-id>` 来手动触发定时任务
2. 该命令连接网关 WebSocket，超时后返回 `gateway timeout after 30000ms`
3. Agent 接着执行 `openclaw gateway status`，发现 `gateway token mismatch`
4. Agent 尝试 `taskkill` 杀死网关进程并重启
5. 重启后 token 不匹配问题持续，Agent 陷入无限循环
6. 整个飞书会话被阻塞，用户消息无法得到响应

#### 会话日志关键片段
```
02:47:13 → exec: openclaw cron run 1c77af71... → "Command still running"
02:47:48 → process poll → "gateway timeout after 30000ms"
02:47:56 → exec: openclaw gateway status → "token mismatch"
02:48:49 → exec: taskkill /F /PID 11664
02:59:20 → exec: Start-Process node gateway → "port already in use"
03:11:42 → exec: openclaw cron run ... → 又超时
03:12:19 → exec: openclaw gateway status → 又 token mismatch
03:15:44 → exec: openclaw gateway status → 继续循环...
03:37:03 → exec: Stop-Process → 杀进程 → 重启 → 继续循环
```

#### 为什么之前的安全规则没生效
- 2026-02-25 已在 AGENTS.md 添加了 exec 安全规则
- 但规则采用"黑名单"模式，只禁止了 `openclaw cron add/remove/update`
- Agent 绕过限制执行了 `openclaw cron run`（不在黑名单中）
- `openclaw gateway status` 也不在黑名单中
- 结论：黑名单模式无法覆盖所有危险命令

#### 守护进程问题
- guardian_loop.ps1 每次检测到网关无响应时启动两个实例（日志显示同一时间两个 PID）
- 多个网关实例竞争同一端口，导致 token mismatch

### 修复方案

#### 1. 清除卡死会话
```bash
# 备份并删除卡死的飞书直聊会话
cp sessions/0529a4d5-*.jsonl sessions/0529a4d5-BACKUP.jsonl
rm sessions/0529a4d5-*.jsonl

# 从 sessions.json 移除引用
# 删除 agent:leo-assistant:feishu:direct:ou_099438b3924bd34e5f9445bc8220a460
# 删除 agent:leo-assistant:main (session 075cb0cf)
```

#### 2. 强化 AGENTS.md 安全规则（黑名单 → 白名单）
将 exec 安全规则从"禁止特定命令"改为"只允许特定命令"：

**禁止所有 `openclaw` 命令**（无一例外）：
- `openclaw cron *` — 全部禁止
- `openclaw gateway *` — 全部禁止
- `openclaw config/agent/onboard/doctor/tui/status/dashboard` — 全部禁止
- 任何以 `openclaw` 或 `node openclaw.mjs` 开头的命令

**同时禁止**：
- `taskkill` — 不杀进程
- `Start-Process` — 不启动后台进程
- 任何可能超过 10 秒的命令

**白名单（仅允许）**：
- `ls`, `cat`, `head`, `tail` — 文件查看
- `date`, `whoami`, `hostname` — 系统信息
- `curl --max-time 10` — 短网络请求
- `python -c "..."` — 短脚本
- `git status/log/diff` — Git 只读

**替代方案**：用 read/write 工具直接编辑配置文件，不通过 exec。

#### 3. 干净重启网关
```bash
taskkill /F /IM node.exe
cd D:\openclaw && node openclaw.mjs gateway --port 18789
```

### 影响范围
- 飞书消息响应中断约 1 小时
- 守护进程产生多个僵尸网关进程
- 无数据丢失

### 经验教训

1. **exec 安全规则必须用白名单模式**：黑名单永远无法穷举所有危险命令
2. **`openclaw` CLI 的所有子命令都可能连接网关 WebSocket**：包括看似只读的 `status`、`cron list` 等
3. **会话卡死后必须删除会话文件**：仅重启网关不够，agent 会从断点继续执行卡死的命令
4. **守护进程需要防重入锁**：避免同时启动多个网关实例

### 待改进项
- [ ] guardian_loop.ps1 添加防重入锁，避免同时启动多个网关
- [ ] 考虑给 OpenClaw 提 issue 请求 exec 工具超时配置
- [ ] 监控 agent 会话大小，超过阈值自动清理
