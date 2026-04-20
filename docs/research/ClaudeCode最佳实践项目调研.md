# Claude Code 最佳实践项目调研报告

> **调研日期**: 2026-04-15
> **来源**: GitHub 搜索

---

## 一、项目概览

| 项目 | Stars | 定位 | 记忆能力 |
|------|-------|------|----------|
| **[everything-claude-code](https://github.com/affaan-m/everything-claude-code)** | ⭐ 156k | AI Agent 性能优化系统 | ✅ 完整长期记忆 |
| **[claude-code-best-practice](https://github.com/shanraisshan/claude-code-best-practice)** | ⭐ 44k | 最佳实践综合指南 | ⚠️ 参考指南 |

---

## 二、everything-claude-code（156k Stars）⭐强烈推荐

### 2.1 项目概述

| 维度 | 信息 |
|------|------|
| **名称** | Everything Claude Code (ECC) |
| **作者** | affaan-m |
| **Stars** | 156k |
| **Forks** | 24.3k |
| **贡献者** | 170+ |
| **定位** | AI Agent 性能优化系统 |
| **荣誉** | Anthropic Hackathon Winner |

### 2.2 核心功能

| 功能 | 说明 |
|------|------|
| **Token 优化** | 模型选择、系统提示精简、后台进程管理 |
| **内存持久化** | 跨会话自动保存/加载上下文 |
| **持续学习** | 从会话中自动提取模式为可复用技能 |
| **验证循环** | 检查点 vs 连续评估、分级器类型、pass@k 指标 |
| **并行化** | Git worktrees、级联方法、实例扩展 |
| **子代理编排** | 上下文问题、迭代检索模式 |
| **安全扫描** | AgentShield 集成 |

### 2.3 目录结构

```
everything-claude-code/
├── .claude/              # Claude Code 配置
├── agents/               # 36 个专业子代理
├── skills/               # 183 个技能
│   ├── continuous-learning-v2/   # ⭐ 持续学习 v2
│   ├── iterative-retrieval/      # 迭代检索
│   ├── context-budget/           # 上下文预算
│   └── ... (183 个 skills)
├── hooks/                # 生命周期钩子
│   ├── SessionStart/     # ⭐ 会话开始时加载
│   ├── SessionEnd/       # ⭐ 会话结束时保存
│   └── Pre-compact/      # 压缩前保存
├── rules/                # 多语言规则
├── docs/                 # 文档
└── 安装脚本
```

### 2.4 长期记忆能力（核心亮点）

#### 2.4.1 持续学习 v2（Continuous Learning v2）

**特点**：
- 基于"本能"(Instinct)的学习系统
- 置信度评分（0.3-0.9）
- 项目隔离，防止跨项目污染
- 自动从会话中提取模式

**本能模型**：
```json
{
  "trigger": "触发条件",
  "action": "执行动作",
  "confidence": 0.7,
  "domain": "code-style|testing|git|debugging|workflow",
  "scope": "project|global",
  "evidence": "观察记录"
}
```

**工作流程**：
```
会话活动 → Hooks 捕获(100%可靠) → 模式检测
    ↓
本能存储 → 进化为 skills/commands/agents
```

**可用命令**：

| 命令 | 说明 |
|------|------|
| `/instinct-status` | 查看所有本能及置信度 |
| `/evolve` | 将本能聚类为 skills/commands |
| `/instinct-export` | 导出本能到文件 |
| `/instinct-import <file>` | 导入本能 |
| `/promote [id]` | 将项目本能提升为全局 |
| `/projects` | 列出项目和本能数量 |

#### 2.4.2 记忆持久化（Memory Persistence）

**机制**：
- SessionStart Hooks → 会话开始时加载上下文
- SessionEnd Hooks → 会话关闭时自动保存
- Pre-compact Hooks → 压缩前保留状态

**生命周期**：
```
SessionStart → 加载之前的上下文
    ↓
会话进行中
    ↓
Pre-compact → 压缩前保存状态
    ↓
SessionEnd → 持久化会话状态
```

### 2.5 安装方式

#### 方式1：插件安装（推荐）
```bash
/plugin marketplace add https://github.com/affaan-m/everything-claude-code
/plugin install everything-claude-code@everything-claude-code
```

#### 方式2：手动安装
```bash
git clone https://github.com/affaan-m/everything-claude-code.git
cd everything-claude-code
./install.sh --profile full
```

#### 方式3：PowerShell（Windows）
```powershell
.\install.ps1 --profile full
```

---

## 三、claude-code-best-practice（44k Stars）

### 3.1 项目概述

| 维度 | 信息 |
|------|------|
| **名称** | claude-code-best-practice |
| **作者** | shanraisshan |
| **Stars** | 44.2k |
| **定位** | 从 vibe coding 到 agentic engineering |

### 3.2 目录结构

```
├── .claude/              # Claude Code 配置
├── agent-teams/          # 多代理协作
├── best-practice/        # 最佳实践文档
├── changelog/            # 版本历史
├── implementation/       # 实际实现
├── orchestration-workflow/ # 命令→代理→技能 模式
└── tutorial/day0/       # 入门教程
```

---

## 四、ECC vs 其他方案对比

| 维度 | everything-claude-code | 内置记忆 | OpenCLI |
|------|------------------------|----------|----------|
| **Stars** | 156k | N/A | N/A |
| **记忆持久化** | ✅ 完整 | ⚠️ 有限 | ❌ 无 |
| **持续学习** | ✅ 本能系统 | ❌ 无 | ❌ 无 |
| **Token 优化** | ✅ 完整 | ⚠️ 有限 | N/A |
| **安装复杂度** | 中等 | N/A | N/A |
| **与 LEO 兼容** | ✅ | ✅ | ✅ |

---

## 五、对 LEO 系统的建议

### 5.1 立即可集成的能力

| 能力 | 来源 | 集成价值 |
|------|------|----------|
| **持续学习 v2** | everything-claude-code | ⭐⭐⭐⭐⭐ |
| **记忆持久化 Hooks** | everything-claude-code | ⭐⭐⭐⭐⭐ |
| **Token 优化** | everything-claude-code | ⭐⭐⭐⭐ |
| **专业 Skills** | everything-claude-code | ⭐⭐⭐ |

### 5.2 建议的集成路径

```
1. 评估 everything-claude-code
   ├─ 阅读 README 和文档
   ├─ 理解 continuous-learning-v2 机制
   └─ 评估与 LEO 的兼容性

2. 如果集成：
   ├─ 安装为插件或独立复制 skills/hooks
   ├─ 配置 SessionStart/SessionEnd Hooks
   └─ 启用持续学习系统

3. 替代方案：
   └─ 参考其设计理念，在 LEO 中实现类似能力
```

### 5.3 关键参考文件

| 文件 | 说明 |
|------|------|
| `skills/continuous-learning-v2/SKILL.md` | 持续学习 v2 完整文档 |
| `hooks/SessionStart/*` | 会话开始 Hook |
| `hooks/SessionEnd/*` | 会话结束 Hook |
| `hooks/Pre-compact/*` | 压缩前 Hook |

---

## 六、总结

| 推荐度 | 项目 | 理由 |
|--------|------|------|
| ⭐⭐⭐⭐⭐ | **everything-claude-code** | 156k stars验证、完整长期记忆、持续学习、Token优化 |
| ⭐⭐⭐ | claude-code-best-practice | 44k stars、最佳实践指南、无记忆能力 |

**最终建议**：深入研究 [everything-claude-code](https://github.com/affaan-m/everything-claude-code) 的 `continuous-learning-v2` 和记忆持久化机制，可作为 LEO 系统长期记忆模块的参考或直接集成。

---

## 参考链接

- [everything-claude-code](https://github.com/affaan-m/everything-claude-code)
- [continuous-learning-v2 SKILL.md](https://github.com/affaan-m/everything-claude-code/blob/main/skills/continuous-learning-v2/SKILL.md)
- [claude-code-best-practice](https://github.com/shanraisshan/claude-code-best-practice)
