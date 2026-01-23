# CLAUDE.md - Leo AI Agent System 项目记忆

> 此文件由 Claude Code 自动读取，用于保持对话一致性和项目上下文。

---

## 用户背景 (Leo / 佬流)

**基础信息**: 36岁，宁波，8年创业经验，自由创业者

**事业板块**:
- 房产中介（主营）：10人团队，度假养老别墅，总价100-300万
- 商业地产：不良资产业务、菜场摊位销售
- AI眼镜：电商代理销售（筹备中）

**2026核心目标**:
1. 房产团队AI赋能（全媒体营销、客户转化、广告投放）
2. 商业地产业务拓展
3. AI工具从入门到精通

**技术工具栈**:
- 编程：Cursor、VS Code、Claude Code
- 自动化：Dify + n8n + 飞书多维表格 + 企业微信
- 其他：NotebookLM、Monica、Manus

**核心理念**:
- ✅ 拒绝AI幻想：不迷信AI万能，只做能落地的改进
- ✅ 小步快跑：先跑通MVP，再迭代优化
- ✅ 数据说话：用结果验证假设
- ✅ 务实优先：能用 > 完美

**协作要求**:
- **语言规则**: 必须全程使用**简体中文**交流
- **解释规则**: 遇到专业技术术语，必须用**大白话**（通俗易懂的语言）解释，禁止堆砌术语
- 拒绝AI谄媚，客观务实
- 可落地执行，小白友好
- 主动发现问题并提出建议

---

## 项目概述

**Leo AI Agent System** - Skills + Subagents 协同工作的 AI 智能体系统

- **创建者**: Leo Liu (@LinLiu2018)
- **主要语言**: Python 3.13+
- **核心理念**: Skills(能力库) + Subagents(执行者) + Orchestrator(编排器)

---

## 核心目录结构

```
AI_claude_skills/
├── leo_skills/           # Skills 能力库
│   ├── content-creation/ # 内容创作（排版、资讯发布）
│   ├── tools/            # 工具框架（技能创建、原型生成）
│   ├── utilities/        # 工具类（研究助手、网页搜索、Obsidian同步）
│   ├── data-analysis/    # 数据分析
│   ├── development/      # 开发工具
│   ├── video-editing/    # 视频编辑（videocut-skills）
│   ├── prompt-engineering/ # 提示词工程（claude-prompt-engineering-skills）
│   └── core/             # 核心技能
├── leo-subagents/        # Subagents 代理库
│   ├── agents/           # Agent 实现
│   │   ├── task-agent/       # 通用任务
│   │   ├── research-agent/   # 研究调研
│   │   ├── creative-agent/   # 内容创作
│   │   ├── analysis-agent/   # 数据分析
│   │   ├── architect-agent/  # 架构设计
│   │   ├── product-manager-agent/ # 产品管理
│   │   ├── mobile-agent/     # 移动端
│   │   └── realestate-agent/ # 房产专业
│   ├── skills-bridge/    # Skills 桥接层
│   └── config/           # Agent 配置
├── leo_orchestrator/     # 统一编排器
├── leo_workflows/        # 工作流定义
├── leo_config/           # 全局配置
│   ├── settings/         # 配置文件
│   └── guidelines/       # 指南（含去AI化指南）
└── projects/             # 项目文件
```

---

## 核心文件

| 文件 | 用途 |
|------|------|
| `leo-system.py` | 系统主入口 |
| `leo_orchestrator/api.py` | 统一 API |
| `leo_orchestrator/registry.py` | Skills/Agents 注册表 |
| `leo_orchestrator/workflow_engine.py` | 工作流引擎 |
| `leo_config/settings/config.yaml` | 全局配置 |
| `leo_config/guidelines/deaiification_guide.yaml` | 去AI化指南 |
| `leo-subagents/config/agents.yaml` | Agent 配置 |

---

## 常用命令

### 系统运行
```bash
# 运行主系统
python leo-system.py

# 测试技能
python leo_skills/test_dev_skills.py

# 测试进化功能
python leo_skills/test_evolution.py
```

### 依赖管理
```bash
# 安装依赖
pip install -r requirements.txt

# 核心依赖: pyyaml, requests
```

### Git 操作
```bash
# 提交格式
git commit -m "feat: 添加新功能"
git commit -m "fix: 修复问题"
git commit -m "docs: 更新文档"
git commit -m "refactor: 重构代码"
```

---

## 代码风格指南

### Python 规范
- 使用 Python 3.13+ 特性
- 类名: PascalCase (如 `TaskAgent`)
- 函数/变量: snake_case (如 `run_workflow`)
- 常量: UPPER_SNAKE_CASE (如 `MAX_RETRIES`)
- 私有成员: 前缀下划线 (如 `_internal_method`)

### Skill 命名规范
- 目录格式: `{功能}-{类型}-cskill`
- 示例: `content-layout-leo-cskill`, `research-assistant-cskill`

### 文件组织
```
skill-name-cskill/
├── SKILL.md              # 技能文档（必需）
├── README.md             # 说明文档
├── scripts/
│   └── main.py           # 入口文件
├── config/               # 配置文件
└── requirements.txt      # 依赖
```

### 注释规范
- 中文注释优先
- 复杂逻辑必须注释
- 函数使用 docstring

---

## 仓库礼仪

### 提交规范
- feat: 新功能
- fix: 修复 bug
- docs: 文档更新
- refactor: 重构
- chore: 杂项（清理、配置等）

### 分支策略
- `master`: 主分支，保持稳定
- `feature/*`: 功能开发分支
- `fix/*`: 修复分支

### PR 要求
- 描述清楚改动内容
- 确保测试通过
- 不引入新的 lint 错误

---

## 架构概览

```
┌─────────────────────────────────────────────────┐
│                  Leo Orchestrator               │
│              (统一编排器 - 大脑)                  │
└────────────┬────────────────────────────────────┘
             │
      ┌──────┴──────┐
      │             │
      ▼             ▼
┌──────────┐  ┌─────────────┐
│ Subagents│  │   Skills    │
│ (执行者)  │  │  (能力库)    │
└──────────┘  └─────────────┘
```

### 核心组件

1. **Skills** - 能力提供者
   - content-layout-leo-cskill: 智能排版
   - realestate-news-publisher-cskill: 房产资讯发布
   - research-assistant-cskill: 研究助手
   - web-search-cskill: 网页搜索
   - obsidian-sync-cskill: Obsidian 同步
   - project-marketing-doc-generator-cskill: 营销文档生成
   - article-to-prototype-cskill: 文章转原型
   - **videocut-skills**: 视频剪辑（口播剪辑、字幕生成）
     - `/videocut:安装` - 环境配置
     - `/videocut:剪口播` - 口误/静音检测
     - `/videocut:剪辑` - 执行剪辑
     - `/videocut:字幕` - 字幕生成
     - `/videocut:自更新` - 自我进化
   - **claude-prompt-engineering-skills**: 提示词工程技能库
     - prompt-optimizer: 提示词优化器
     - long-context-handler: 长文本处理器
     - xml-structure-builder: XML结构构建器
     - chain-of-thought-prompter: 思维链提示器
     - prompt-chaining-orchestrator: 提示词链编排器

2. **Subagents** - 任务执行者
   - task-agent: 通用任务执行
   - research-agent: 研究调研
   - creative-agent: 内容创作
   - analysis-agent: 数据分析
   - architect-agent: 架构设计
   - product-manager-agent: 产品管理
   - mobile-agent: 移动端开发
   - realestate-agent: 房产专业

3. **Orchestrator** - 统一协调
   - 自动发现和注册 Skills
   - 协调 Agent 执行任务
   - 管理工作流

---

## 去AI化指南

项目使用双模式去AI化策略（`leo_config/guidelines/deaiification_guide.yaml`）：

| 模式 | 适用场景 | 特点 |
|------|----------|------|
| 创意模式 | 营销文案、短视频、直播脚本 | 口语化、接地气、真人口吻 |
| 严谨模式 | 技术文档、数据分析、正式报告 | 客观准确、实事求是、标注来源 |

**创意模式关键词**: "我跟你说"、"说实话"、"差不多"、"应该"
**严谨模式原则**: 不虚构数据、不夸大收益、不绝对承诺、不隐瞒风险

---

## API 快速参考

```python
from leo_orchestrator.api import leo

# 查看状态
leo.stats()

# 列出 Skills
leo.list("skills")

# 调用 Skill
leo.call("content-layout-leo-cskill", "layout", content="...", style="data_driven")

# 运行 Agent
leo.run_agent("task-agent", "生成营销文档", project_info={...})

# 运行工作流
leo.run_workflow("content-pipeline", topic="...")
```

---

## 开发注意事项

1. **新增 Skill**: 在 `leo_skills/` 对应分类下创建，系统自动发现
2. **新增 Agent**: 在 `leo-subagents/agents/` 下创建，需在 config 中注册
3. **配置修改**: 优先修改 `leo_config/settings/config.yaml`
4. **测试**: 修改后运行相关测试脚本验证

---

## 当前工作重点

### 已完成 ✅
- [x] 去 AI 化内容处理功能（双模式）
- [x] 目录重命名和标准化（2026-01-23 完成）
- [x] 工作流引擎开发（已完善）

### 进行中 🚧
- [ ] 实现 3 个新 Agent：
  - [ ] Architect Agent（架构设计代理）
  - [ ] Mobile Agent（移动开发代理）
  - [ ] Product Manager Agent（产品管理代理）
- [ ] 实现 3 个工作流：
  - [ ] Analysis Pipeline（数据分析工作流）
  - [ ] Content Pipeline（内容创作工作流）
  - [ ] Research Pipeline（研究调研工作流）

### 待优化 📋
- [ ] Skills 桥接层完善
- [ ] Agent 调用逻辑优化

---

## 已知问题

- ✅ ~~部分 Agent 状态为 🟡（analysis-agent 待完善）~~ - 已修复，已集成 data-analyzer-cskill
- ✅ ~~工作流引擎 `workflow_engine.py` 开发中~~ - 已完善，支持条件分支、并行执行、重试机制、超时控制
- ✅ ~~重复目录和临时文件~~ - 已清理（2026-01-23）
- ✅ ~~目录命名不一致~~ - 已统一使用下划线命名（2026-01-23）
- 部分 Agent 类型未实现（architect, mobile, product-manager）- 待实现
- 3 个工作流待实现（analysis-pipeline, content-pipeline, research-pipeline）

---

## 最近更新

### 2026-01-23: 目录重命名和标准化（完成）
**第一阶段：项目清理**
- ✅ 删除临时目录 `~/`
- ✅ 删除重复的 `t3-stack-scaffold-cskill` 目录
- ✅ 清理废弃的空目录（fission-project, docs/reports 等）
- ✅ 为规划中的目录添加 README.md 说明文档

**第二阶段：目录重命名**
- ✅ 创建 git 分支 `refactor/standardize-structure`
- ✅ 合并 `leo-orchestrator/` 和 `leo_orchestrator/`
- ✅ 重命名 `leo-workflows/` → `leo_workflows/`
- ✅ 重命名 `leo-config/` → `leo_config/`
- ✅ 重命名 `leo-skills/` → `leo_skills/`
- ✅ 批量替换所有文件中的路径引用（46个文件，243处修改）
- ✅ 验证系统运行正常
- ✅ 提交更改（2次提交，545个文件被修改）

**成果**:
- 所有目录已统一使用下划线命名，符合 Python PEP 8 规范
- 系统运行正常，所有 Skills 和 Agents 成功注册
- 代码库更规范、更易维护

**下一步**:
- 实现 3 个新 Agent（architect, mobile, product-manager）
- 实现 3 个工作流（analysis-pipeline, content-pipeline, research-pipeline）

---

*最后更新: 2026-01-23*
