---
description:
alwaysApply: true
---

# Leo AI System - Context Registry

> **Attention Strategy**: 按需读取，不要一次性加载所有引用文件。

## 0. 上下文工程 (Context Engineering)

> **"Context Window = RAM, Filesystem = Disk"**

复杂任务（3+步骤）使用 planning_with_files_skill：

| 文件 | 用途 |
|------|------|
| `docs/planning/task_plan.md` | 阶段、进度、决策 |
| `docs/research/findings.md` | 研究发现 |
| `docs/progress/progress.md` | 会话日志 |

**规则**: 复杂任务先建计划 → 每2次搜索后更新发现 → 决策前重读计划 → 记录错误不重复

---

## 1. Context Map (静态上下文)

| Module | Path |
| :--- | :--- |
| **User Profile** | `leo_knowledge/context/user_profile.md` |
| **Dev Guide** | `leo_knowledge/context/development_guide.md` |
| **Architecture** | `leo_knowledge/context/system_architecture.md` |
| **Project Tree** | `leo_knowledge/context/project_structure.md` |
| **All Capabilities** | `leo_knowledge/context/capability_index.md` |
| **Skill Levels** | `leo_knowledge/context/skill_levels.md` |

## 2. Active Work (动态状态)

- **Current Task**: `docs/planning/task_plan.md` (优先检查)
- **Findings**: `docs/research/findings.md`
- **Progress**: `docs/progress/progress.md`

## 3. 文件路径规则

```
根目录 (只放入口和配置):
├── CLAUDE.md, README.md, AGENTS.md
├── src/                   # 源代码
├── scripts/               # 脚本 (按功能分子目录)
├── tests/                 # 测试
├── projects/              # 项目文件
├── leo_knowledge/         # 知识库
└── docs/                  # 所有文档
    ├── identity/          # 身份
    ├── reference/         # 索引、清单、运维手册
    ├── guides/            # 操作指南
    ├── planning/          # 任务规划
    ├── progress/          # 进度日志
    ├── research/          # 研究发现
    └── assets/            # 静态资源
```

**新建文件**: 先判断类型 → 放到 `docs/` 对应目录 → 禁止放根目录

---

## 4. Quick Actions

1. 检查 `docs/planning/task_plan.md` 获取当前任务状态
2. 新项目先读 `leo_knowledge/context/user_profile.md`
3. 写代码前查 `leo_knowledge/context/capability_index.md` 避免重复
4. 查看 `leo_knowledge/context/skill_levels.md` 了解技能成熟度（A/B/C/D 四级）
5. 复杂任务用 planning_with_files_skill

---

## 5. 集成系统

### OpenClaw (飞书 AI 助手)

| 项目 | 信息 |
|------|------|
| **本地目录** | `D:\openclaw` |
| **版本** | 2026.2.23 |
| **运维手册** | `docs/reference/OPENCLAW_OPS.md` (故障排查、配置规则) |
| **启动命令** | `cd D:\openclaw && node openclaw.mjs gateway --port 18789` |

**核心规则**: feishu 是 Channel 不是 Plugin；`doctor --fix` 后必须人工检查配置

**故障案例库**:

| 日期 | 症状 | 根因 | 修复方案 |
|------|------|------|----------|
| 2026-03-01 | `Message ordering conflict` 反复出现 | 会话历史 1000+ 条，compaction 超时失败，状态损坏 | 1. 删除 `~/.openclaw/agents/leo-assistant/sessions/*`<br>2. 重启网关<br>3. 部署定时清理脚本 `scripts/openclaw/session_maintenance.ps1` |
| 2026-03-01 | MiniMax API 401 | 配置使用旧 API Key (`sk-api-`)，Coding Plan 需用 `sk-cp-` Key | 更新 `openclaw.json` 中的 apiKey 和 baseUrl |

**预防性维护**:
- 定期在飞书发送 `/reset` 或 `/new` 重置会话
- 每周运行一次 `session_maintenance.ps1` 清理大文件
- 监控 `~/.openclaw/agents/leo-assistant/sessions/` 目录大小

### Superpowers (v4.2.0)

| 项目 | 说明 |
|------|------|
| **原始存储** | `~/.claude/skills/superpowers/` |
| **Leo 对应** | `src/leo_skills/` 下 14 个 snake_case 技能 |
| **Hook** | `.claude/hooks.json` SessionStart 自动注入 |

---

## 6. 会话驱动规则

1. **先读后写**: 修改文件前必须先 Read，批量操作每个文件都要读
2. **路径验证**: 重构后执行 `PYTHONUTF8=1 python scripts/maintenance/validate_paths.py`
3. **统一 Bash**: 禁止 PowerShell，脚本用 `.sh` 或 `.py`

---

## 7. 简体中文规则（强制）

- AI 回复全部使用简体中文
- 代码注释用中文，文件名/变量名保持英文
- 技术术语保留英文原词，括号附中文解释
- Git 提交信息使用中文
- 用大白话解释，给可直接执行的命令，步骤数字编号

---

## 8. 双引擎协作（Claude Code + Codex）

> 详细规范见 `AGENTS.md`

**简单记忆**: Claude 想 → Claude 拆 → Codex 干 → Claude 查 → Claude 收

| Claude Code (大脑) | Codex (双手) |
|---|---|
| 架构设计、代码审查、重构、规划 | 脚手架搭建、模板生成、批量修改 |

**冲突避免**: 不同时编辑同一文件；Codex 不改 CLAUDE.md；Claude 不做批量创建
