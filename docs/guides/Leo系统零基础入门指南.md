# Leo AI系统 - 零基础入门指南

**复制粘贴即用 | 不需要懂代码 | 中文激活**

> 最后更新：2026-02-01

---

## 🎯 三大系统关系（核心必读）

在使用系统前，先搞懂这三个系统的关系：

```
┌─────────────────────────────────────────────────────────────┐
│              Leo AI System (你的核心大脑)                    │
│  📁 位置: d:\桌面\leo_ai_system                              │
│  💾 职责: 技能(Skills)、代理(Agents)、工作流(Workflows)      │
│  ⚙️ 存储: 本地 src/ 目录                                     │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              OpenClaw (大龙虾/小龙虾)                        │
│  📁 位置: D:\moltbot                                        │
│  💾 职责: 消息网关、多渠道分发、飞书集成                      │
│  ☁️ 部署: 云端 Linux (Vultr/腾讯云)                         │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                      飞书 (Feishu)                           │
│  📱 职责: 用户交互界面、消息输入/输出                         │
│  🤖 机器人: cli_a9f18849edbb9cb1 (本地)                     │
│  🤖 机器人: cli_a9f7c17a65b89cd2 (云端)                     │
└─────────────────────────────────────────────────────────────┘
```

**通俗理解**：
- **Leo AI System** = 你办公室里的**电脑主机**（负责思考和干活）
- **OpenClaw (大龙虾)** = 电脑的**网卡和路由器**（负责接收和发送消息）
- **飞书** = 电脑的**显示器和键盘**（你看的和操作的界面）

**数据流向**：
```
你说的话 (飞书)
    ↓
大龙虾 Gateway (接收消息)
    ↓
Leo AI System (思考+执行)
    ↓
大龙虾 Gateway (发送结果)
    ↓
飞书 (你看到回答)
```

**文件位置速查**：

| 系统 | 位置 | 用途 |
|------|------|------|
| Leo AI System | `d:\桌面\leo_ai_system\src\` | 所有代码、技能、代理 |
| OpenClaw (原moltbot) | `D:\moltbot\` | 飞书机器人网关（GitHub已改名） |
| 飞书配置 | `C:\Users\刘方林\.openclaw\` | 机器人配置 |

---

## 🆕 飞书机器人入口（推荐）

现在你可以通过**飞书**直接与 Leo AI System 交互！

### 使用方式

| 方式 | 操作 | 说明 |
|------|------|------|
| **群聊** | @机器人 + 消息 | 在群里 @机器人 发送消息 |
| **私聊** | 直接发消息 | 找到机器人直接对话 |

### 可用模型

| 模型 | 切换命令 | 说明 |
|------|----------|------|
| MiniMax-M2.1 | `/model minimax/MiniMax-M2.1` | 默认模型，中文能力强 |
| 智谱 GLM-4 Plus | `/model GLM4` | 智谱大模型 |

### 示例对话

```
你：@Leo助手 查看项目的 CLAUDE.md 文件
机器人：[显示文件内容]

你：@Leo助手 项目结构是什么？
机器人：[显示项目目录结构]

你：@Leo助手 帮我排版这篇文章
机器人：[调用 content_layout_leo_skill 排版]
```

### 机器人能做什么？

- 📁 **查看/编辑项目文件** - 读取代码、文档、配置
- 🔍 **搜索信息** - 网页搜索、项目内搜索
- 💻 **执行命令** - 运行脚本、Git 操作
- 📝 **内容创作** - 写文章、排版、发布
- 🤖 **调用技能** - 使用 Leo System 的所有技能
- 🎬 **视频剪辑** - 剪口播、生成字幕（FFmpeg 8.0.1 已部署）

---

## 🔧 系统运维指南

### 智能守护系统（自动运维）

系统已部署**自动守护进程**，无需手动维护：

| 功能 | 说明 |
|------|------|
| **自动监控** | 每30秒检测 Gateway 状态 |
| **智能修复** | 自动修复配置文件、清理僵尸进程 |
| **自动重启** | 掉线后自动重启，最多3次重试 |
| **故障记录** | 完整日志记录到 `.openclaw/logs/` |

**常用命令**:
```bash
# 一键启动智能守护
d:\桌面\leo_ai_system\scripts\一键启动智能守护.bat

# 检查系统状态
d:\桌面\leo_ai_system\scripts\check_gateway_status.bat

# 安装开机自动启动（管理员）
d:\桌面\leo_ai_system\scripts\install_auto_healer.bat
```

**日志位置**:
- 守护日志: `%USERPROFILE%\.openclaw\logs\auto_healer_*.log`
- Gateway日志: `%USERPROFILE%\.openclaw\gateway.log`

---

## 先搞懂三个概念

把Leo系统想象成一家公司：

| 概念 | 通俗解释 | 类比 |
|------|---------|------|
| **Skills（技能）** | 具体干活的工具 | 公司里的各种软件工具（Excel、PS等） |
| **Agents（代理）** | 会用工具的员工 | 不同部门的专业员工（会自己选工具） |
| **Workflows（工作流）** | 多人协作的流程 | 跨部门协作的SOP（自动流水线） |

**关系图**：
```
工作流（流水线）
    ↓ 调度
代理（员工）
    ↓ 使用
技能（工具）
    ↓
完成任务
```

---

## 一、Skills（技能）- 你的工具箱

### 核心技能（推荐优先使用）

| 技能 | 大白话说明 | 激活命令 | 成熟度 |
|------|-----------|---------|--------|
| **content_layout_leo_skill** | 把文章变漂亮，适配微信/小红书 | `帮我排版这篇文章` | ⭐⭐⭐⭐⭐ |
| **research_assistant_skill** | 帮你查资料、整理文献 | `帮我研究这个主题` | ⭐⭐⭐⭐⭐ |
| **web_search_skill** | 上网搜信息 | `搜索xxx` | ⭐⭐⭐⭐ |
| **realestate_news_publisher_skill** | 发布房产资讯到公众号 | `帮我发布房产资讯` | ⭐⭐⭐⭐ |
| **image_generator_skill** | AI生成图片/效果图 | `生成一张xxx图片` | ⭐⭐⭐⭐ |

### 项目执行类（新增）🆕

| 技能 | 大白话说明 | 激活命令 | 成熟度 |
|------|-----------|---------|--------|
| **planning_with_files_skill** | 持久化规划，用3个文件管理复杂任务 | `开始复杂任务` | ⭐⭐⭐⭐⭐ |
| **fresh_start_skill** | 加载项目上下文 | `/fresh-start` | ⭐⭐⭐⭐ |
| **phase_prep_skill** | 检查阶段先决条件 | `/phase-prep 1` | ⭐⭐⭐⭐ |
| **phase_start_skill** | 执行项目阶段任务 | `/phase-start 1` | ⭐⭐⭐⭐ |
| **phase_checkpoint_skill** | 验证阶段完成 | `/phase-checkpoint 1` | ⭐⭐⭐⭐ |

### 专业开发类（obra/superpowers）🆕

| 技能 | 大白话说明 | 激活命令 | 成熟度 |
|------|-----------|---------|--------|
| **brainstorming_skill** | 头脑风暴，探索需求和设计 | `头脑风暴这个功能` | ⭐⭐⭐ |
| **writing_plans_skill** | 编写详细实施计划 | `写实施计划` | ⭐⭐⭐⭐⭐ |
| **executing_plans_skill** | 批量执行计划带检查点 | `执行计划` | ⭐⭐⭐⭐ |
| **subagent_driven_development_skill** | 子代理驱动开发，两阶段审查 | `子代理开发模式` | ⭐⭐⭐⭐ |
| **systematic_debugging_skill** | 四阶段根因分析系统化调试 | `系统调试这个问题` | ⭐⭐⭐⭐⭐ |
| **test_driven_development_skill** | TDD 红-绿-重构循环 | `TDD模式开发` | ⭐⭐⭐⭐⭐ |
| **verification_before_completion_skill** | 完成前验证，证据优先 | `验证工作完成` | ⭐⭐⭐⭐ |
| **using_git_worktrees_skill** | Git 并行分支管理 | `创建隔离工作区` | ⭐⭐⭐⭐ |
| **finishing_development_branch_skill** | 完成开发分支，处理合并/PR | `完成这个分支` | ⭐⭐⭐⭐ |
| **dispatching_parallel_agents_skill** | 并行分发多个代理 | `并行调查这些问题` | ⭐⭐⭐⭐ |
| **requesting_code_review_skill** | 请求代码审查 | `请求代码审查` | ⭐⭐⭐⭐ |
| **receiving_code_review_skill** | 接收审查反馈，处理建议 | `处理审查反馈` | ⭐⭐⭐⭐ |

### 开发工具类（给技术人员用）

| 技能 | 大白话说明 | 激活命令 | 成熟度 |
|------|-----------|---------|--------|
| agent_skill_creator_skill | 帮你造新技能 | `帮我创建一个新技能` | ⭐⭐⭐⭐ |
| github_to_skills_skill | 把GitHub项目转成技能 | `把这个GitHub仓库转成技能` | ⭐⭐⭐⭐ |
| article_to_prototype_skill | 把文章变成代码原型 | `把这篇文章转成代码` | ⭐⭐⭐ |
| skill_code_generator_skill | 自动生成技能代码 | `生成技能代码` | ⭐⭐⭐ |

### 后端开发类

| 技能 | 大白话说明 | 成熟度 |
|------|-----------|--------|
| api_doc_generator_skill | 自动生成API文档 | ⭐⭐⭐ |
| database_model_generator_skill | 生成数据库模型 | ⭐⭐⭐ |
| fastapi_endpoint_generator_skill | 生成FastAPI接口 | ⭐⭐⭐ |
| flask_api_generator_skill | 生成Flask接口 | ⭐⭐⭐ |

### 前端开发类

| 技能 | 大白话说明 | 成熟度 |
|------|-----------|--------|
| vue_component_generator_skill | 生成Vue组件 | ⭐⭐⭐ |
| react_component_generator_skill | 生成React组件 | ⭐⭐⭐ |
| miniprogram_page_generator_skill | 生成小程序页面 | ⭐⭐⭐ |

### DevOps类

| 技能 | 大白话说明 | 成熟度 |
|------|-----------|--------|
| dockerfile_generator_skill | 生成Docker配置 | ⭐⭐⭐ |
| nginx_config_generator_skill | 生成Nginx配置 | ⭐⭐⭐ |
| github_actions_generator_skill | 生成CI/CD流程 | ⭐⭐⭐ |

### 视频编辑类（已部署FFmpeg 8.0.1）

| 技能 | 大白话说明 | 激活命令 | 成熟度 |
|------|-----------|---------|--------|
| **cut_speech_skill** | 剪口播视频，自动识别口误和静音 | `帮我剪口播` | ⭐⭐⭐⭐ |
| **video_editing_skill** | 执行视频剪辑，生成字幕 | `执行剪辑` | ⭐⭐⭐⭐ |
| **subtitle_skill** | 生成视频字幕（SRT格式） | `生成字幕` | ⭐⭐⭐⭐ |

**使用方式**：在飞书发送视频文件，然后说"帮我剪口播"

### 其他工具

| 技能 | 大白话说明 | 成熟度 |
|------|-----------|--------|
| obsidian_sync_skill | 同步到Obsidian笔记 | ⭐⭐⭐ |
| data_analyzer_skill | 分析数据 | ⭐⭐⭐ |
| twitter_monitor_skill | 监控Twitter动态 | ⭐⭐ |
| security_scan_skill | 安全扫描 | ⭐⭐ |

---

## 二、Agents（代理）- 你的AI员工

### 核心代理（10个）

| Agent | 大白话说明 | 激活示例 | 成熟度 |
|-------|-----------|---------|--------|
| **realestate_agent** | 房产专家，懂营销懂市场 | `生成楼盘营销方案` | ⭐⭐⭐⭐⭐ |
| **research_agent** | 调研专家，会搜资料整理 | `帮我调研智慧农贸市场` | ⭐⭐⭐⭐ |
| **creative_agent** | 文案专家，会写会改 | `帮我写一篇营销文案` | ⭐⭐⭐⭐ |
| **task_agent** | 执行专家，干具体活 | `帮我排版并发布这篇文章` | ⭐⭐⭐⭐ |
| **analysis_agent** | 分析专家，看数据出报告 | `分析这组销售数据的趋势` | ⭐⭐⭐ |
| **ecommerce_agent** | 电商专家，懂选品懂文案 | `分析AI眼镜竞品` | ⭐⭐⭐ |
| **product_manager_agent** | 产品经理，写PRD做需求 | `帮我写PRD` | ⭐⭐⭐ |
| **architect_agent** | 架构师，做技术设计 | `设计系统架构` | ⭐⭐⭐ |
| **mobile_agent** | 移动开发，做小程序 | `生成小程序页面` | ⭐⭐⭐ |
| **ai_news_summary_agent** | 每日新闻摘要（AI+财经+政治） | `今日新闻摘要`、`财经要闻`、`政治新闻汇总` | ⭐⭐⭐ |

### 怎么用Agent？

**方式1：让系统自动选**（推荐新手）
```
分析宁波房地产市场
```
系统会自动选择 realestate-agent。

**方式2：指定Agent**（推荐老手）
```
用research-agent帮我调研AI眼镜市场
```

### Agent vs Skill 区别

| 对比 | Skill（技能） | Agent（代理） |
|------|--------------|--------------|
| 类比 | 一把锤子 | 一个木匠 |
| 能力 | 只会一件事 | 会组合多个技能 |
| 智能 | 不会思考 | 会分析任务选工具 |
| 例子 | 排版 | 搜索+写作+排版+发布 |

**例子**：
- 用Skill：`帮我排版` → 只做排版这一件事
- 用Agent：`帮我写一篇房产分析文章并排版发布` → 自动调用4个技能完成

---

## 三、Workflows（工作流）- 自动流水线

### 8条流水线

| 工作流 | 大白话说明 | 步骤 | 成熟度 |
|--------|-----------|------|--------|
| **content_pipeline** | 内容生产线 | 策划→素材收集→创作→排版→去AI化→质检→发布 | ⭐⭐⭐⭐ |
| **research_pipeline** | 调研流水线 | 多源搜集→去重→分类→质量评估→深度分析→报告→同步知识库 | ⭐⭐⭐⭐ |
| **analysis_pipeline** | 分析流水线 | 数据采集→验证→清洗→并行分析→汇总→报告 | ⭐⭐⭐ |
| **realestate_pipeline** | 房产营销线 | 市场调研→竞品分析→项目定位→营销策略→内容创作→发布 | ⭐⭐⭐⭐ |
| **ecommerce_pipeline** | 电商分析线 | 市场趋势→竞品收集→深度分析→选品建议→文案创作→营销策略 | ⭐⭐⭐ |
| **fullstack_dev_pipeline** | 全栈开发线 | 需求分析→后端开发→前端开发→部署上线 | ⭐⭐⭐ |
| **miniprogram_dev_pipeline** | 小程序开发线 | 产品设计→页面开发→接口开发→发布上线 | ⭐⭐⭐ |
| **api_pipeline** | API开发线 | 需求分析→架构设计→API开发→测试→部署 | ⭐⭐⭐ |

### 工作流详解

#### 内容生产线（content_pipeline）
```
你说：运行content_pipeline，主题是"2026年宁波楼市分析"

系统自动执行：
1. 策划大纲（research-agent）
2. 并行收集素材（research-agent + analysis-agent）
3. 写文章（creative-agent）
4. 排版美化（task-agent + content_layout_leo_skill）
5. 去AI化处理（creative-agent）
6. 质量检查（analysis-agent）
7. 发布（task-agent + realestate_news_publisher_skill）
```

#### 调研流水线（research_pipeline）
```
你说：运行research_pipeline，主题是"AI眼镜竞品分析"

系统自动执行：
1. 并行搜索（网页+数据库+文档）
2. 信息去重
3. 资料分类（核心概念/案例/数据/观点/动态）
4. 质量评估（不够就补充搜索）
5. 深度分析
6. 交叉验证
7. 生成报告
8. 同步到Obsidian知识库
```

#### 房产营销线（realestate_pipeline）【新增】
```
你说：运行realestate_pipeline，项目是"淮安建华官园"，位置是"淮安"

系统自动执行：
1. 市场调研（research-agent）
2. 并行竞品分析（竞品搜索+价格分析+政策研究）
3. 项目定位分析（realestate-agent）
4. 营销策略制定（realestate-agent）
5. 并行内容创作（微信文章+小红书笔记+短文案）
6. 内容排版优化（content_layout_leo_skill）
7. 去AI化处理（creative-agent）
8. 质量检查（analysis-agent）
9. 生成营销报告
```

#### 电商分析线（ecommerce_pipeline）【新增】
```
你说：运行ecommerce_pipeline，类目是"AI眼镜"

系统自动执行：
1. 市场趋势调研（research-agent）
2. 并行竞品收集（淘宝+京东+抖音）
3. 竞品深度分析（analysis-agent）
4. 选品建议生成（ecommerce-agent）
5. 并行文案创作（标题+详情+抖音脚本+小红书笔记）
6. 营销策略制定（ecommerce-agent）
7. 生成分析报告
```

---

## 四、快速对照表

| 我想... | 说什么 | 用到什么 |
|--------|-------|---------|
| 排版文章 | `帮我排版这篇文章` | content_layout_leo_skill |
| 发布房产资讯 | `帮我发布房产资讯` | realestate_news_publisher_skill |
| 生成营销手册 | `生成项目营销手册` | realestate-agent |
| 搜索信息 | `搜索xxx` | web_search_skill |
| 生成效果图 | `生成一张小程序首页效果图` | image_generator_skill |
| 分析数据 | `分析这组数据` | analysis-agent |
| 做完整调研 | `运行research_pipeline，主题是xxx` | 调研工作流 |
| 写文章并发布 | `运行content_pipeline，主题是xxx` | 内容工作流 |
| 房产项目营销 | `运行realestate_pipeline，项目是xxx` | 房产工作流 |
| 电商竞品分析 | `运行ecommerce_pipeline，类目是xxx` | 电商工作流 |
| 创建新技能 | `帮我创建一个新技能` | agent_skill_creator_skill |
| GitHub转技能 | `把这个GitHub仓库转成技能` | github_to_skills_skill |
| 写PRD | `帮我写PRD` | product-manager-agent |
| 分析竞品 | `分析xxx竞品` | ecommerce-agent |

---

## 五、协同机制（进阶理解）

### 三层架构

```
┌─────────────────────────────────────────┐
│     Workflows（工作流）- 流水线         │
│     编排多步骤，管理数据流转             │
└────────────────┬────────────────────────┘
                 │ 调度
┌────────────────▼────────────────────────┐
│     Agents（代理）- 智能员工            │
│     理解任务，选择并组合Skills           │
└────────────────┬────────────────────────┘
                 │ 调用
┌────────────────▼────────────────────────┐
│     Skills（技能）- 工具箱              │
│     原子化功能，可复用                   │
└─────────────────────────────────────────┘
```

### 协同模式

| 模式 | 说明 | 例子 |
|------|------|------|
| **串行** | 一步一步来 | 收集→分析→生成→发布 |
| **并行** | 同时干多件事 | 同时搜索网页+数据库+文档 |
| **条件分支** | 根据结果决定下一步 | 质量<80分→修订→发布 |
| **自动选择** | 系统自动选Agent | 说"房产"自动选realestate-agent |

---

## 六、使用技巧

### 技巧1：说清楚需求

| 不好 | 好 |
|-----|-----|
| 帮我做个东西 | 生成项目营销手册 |
| 帮我排版 | 帮我排版，用数据驱动型风格 |
| 帮我分析 | 分析宁波2025年房价走势 |

### 技巧2：复杂任务用工作流

| 简单任务 | 复杂任务 |
|---------|---------|
| 直接说需求 | 运行xxx工作流 |
| 帮我排版 | 运行内容生产线 |
| 搜索信息 | 运行调研流水线 |

### 技巧3：不确定用什么？

直接说你要做什么，系统会自动选择：
```
我要写一篇关于宁波楼市的分析文章
```

### 技巧4：指定Agent更精准

如果自动选择不准，可以指定：
```
用realestate-agent帮我分析楼盘
```

---

## 七、系统评估与优化建议

### 当前系统成熟度

| 组件类型 | 数量 | 成熟度 | 建议 |
|---------|------|--------|------|
| Skills | 89 | ⭐⭐⭐⭐ | 核心技能成熟，集成 obra/superpowers 专业开发技能 |
| Agents | 14 | ⭐⭐⭐⭐ | 房产/研究/创作最成熟 |
| Workflows | 8 | ⭐⭐⭐⭐ | 设计完善，待实战验证 |

### 优先使用推荐

**Leo的业务场景推荐**：

1. **房产营销** → `realestate-agent` + `content_pipeline`
2. **市场调研** → `research-agent` + `research_pipeline`
3. **内容创作** → `creative-agent` + `content_layout_leo_skill`
4. **电商分析** → `ecommerce-agent` + `web_search_skill`
5. **复杂项目开发** → `fresh_start_skill` + `phase_*` 三阶段工作流

### 新增能力：系统化项目执行 🆕

基于 ai_coding_projectbase 的三阶段工作流：

```
/fresh-start        → 加载项目上下文
/phase-prep 1       → 检查准备阶段
/phase-start 1      → 执行阶段任务
/phase-checkpoint 1 → 验证阶段完成
```

### 待优化项

1. **Skills**：全部核心技能已集成，可选集成剩余协作技能
2. **Agents**：analysis_agent 需要更多数据分析场景测试
3. **Workflows**：开发类工作流（全栈/小程序/API）待实战验证

---

## 八、系统文件位置

```
leo_ai_system/src/
├── leo_skills/              # 所有技能（89个）
│   ├── core/                 # 核心技能（planning, phase_*, fresh_start）
│   ├── testing/              # 测试技能（TDD, verification）
│   ├── debugging/            # 调试技能（systematic_debugging）
│   ├── collaboration/        # 协作技能（superpowers 系列）
│   ├── content_creation/     # 内容创作类
│   ├── utilities/            # 工具类
│   ├── backend/              # 后端开发类
│   ├── frontend/             # 前端开发类
│   ├── devops/               # 运维类
│   ├── security/             # 安全类
│   └── ...
├── leo_subagents/           # 所有代理（14个）
│   ├── agents/               # 代理实现
│   ├── config/agents.yaml    # 代理配置
│   └── skills_bridge/        # 技能桥接层
├── leo_workflows/           # 所有工作流（8条）
│   └── workflows/
│       ├── content_pipeline/
│       ├── research_pipeline/
│       ├── analysis_pipeline/
│       ├── realestate_pipeline/
│       ├── ecommerce_pipeline/
│       ├── fullstack_dev_pipeline/
│       ├── miniprogram_dev_pipeline/
│       └── api_pipeline/
├── leo_system/              # 系统核心
└── leo_knowledge/           # 知识库
```

---

## 八、Obsidian同步使用手册

> **Obsidian Sync Skill** - 将AI输出无缝同步到你的第二大脑

### 什么是Obsidian同步？

把 Claude/Leo 的输出自动保存到你的 Obsidian 知识库，自动添加标签、链接、分类，让你的知识形成网络。

---

### 核心功能

| 功能 | 中文指令 | 说明 |
|------|---------|------|
| **快速捕获** | `保存到Obsidian` / `保存这段对话` | 一键保存到 Inbox |
| **创建笔记** | `在Obsidian创建笔记` / `创建笔记` | 用模板创建结构化笔记 |
| **保存Leo输出** | `保存到Obsidian知识库` / `归档到Obsidian` | 保存技能输出到指定文件夹 |
| **创建日记** | `创建今日日记` / `写日记` | 自动化每日记录 |
| **更新索引** | `更新MOC` / `更新内容地图` | 维护知识索引 |

---

### 常用场景

#### 场景1：保存重要对话

```
你说：把这段对话保存到Obsidian
AI：已保存到 Inbox，标题："Python单例模式"
```

#### 场景2：保存研究结果

```
你说：用research-assistant研究AI趋势，然后保存到Obsidian
AI：完成研究，已保存到 "30-Resources/AI研究/AI趋势.md"
```

#### 场景3：自动化日记

```
你说：创建今日日记，计划是[完成文档、测试系统]
AI：已创建今日笔记，包含计划任务和Claude协作记录
```

#### 场景4：更新知识索引

```
你说：更新编程MOC，添加新链接"Python异步编程"
AI：已更新 MOC/Python.md，添加双向链接
```

---

### 中文指令速查表

| 场景 | 激活指令 |
|------|---------|
| 快速保存对话 | `保存这段话到Obsidian` |
| 保存代码片段 | `把这段代码存到笔记` |
| 保存研究结果 | `保存研究结果到知识库` |
| 创建结构化笔记 | `创建关于xxx的笔记` |
| 创建今日日记 | `创建今日日记` / `写日记` |
| 保存Leo输出 | `保存排版结果到Obsidian` |
| 更新MOC索引 | `更新编程MOC` / `更新内容地图` |
| 添加链接 | `给这个笔记添加链接` |
| 添加标签 | `给这个笔记添加标签xxx` |
| 搜索笔记 | `搜索Obsidian笔记xxx` |

---

### 推荐使用方式

| 工作流 | 指令组合 |
|-------|---------|
| **研究→保存** | `运行research_pipeline` → `保存到Obsidian` |
| **创作→归档** | `运行content_pipeline` → `保存到知识库` |
| **对话→笔记** | `保存这段对话` → `添加标签claude生成` |
| **每日记录** | `创建今日日记` → 自动记录计划和协作 |

---

### 文件夹结构

Obsidian Vault 会自动创建以下结构：

```
MySecondBrain/
├── 00-Inbox/              # 快速捕获
├── 01-Daily/              # 日记
├── 10-Projects/           # 项目笔记
├── 20-Areas/              # 领域笔记
├── 30-Resources/          # 资源笔记
├── 40-Archives/           # 归档
├── Leo-Outputs/           # Leo输出（自动分类）
│   ├── content-layout/    # 排版输出
│   ├── research/          # 研究输出
│   ├── marketing/         # 营销输出
│   └── analysis/          # 分析输出
└── Templates/             # 模板
```

---

### 标签使用建议

| 标签类型 | 推荐标签 |
|---------|---------|
| 来源 | `#claude生成` `#leo-output` `#手动整理` |
| 状态 | `#待整理` `#已完成` `#需复习` |
| 类型 | `#概念` `#方法` `#案例` `#代码` |

---

### 与其他技能联动

```
# 研究 + 保存
research-assistant → 研究主题 → save_leo_output → Obsidian

# 排版 + 保存
content-layout-leo-skill → 排版文章 → save_leo_output → Obsidian

# 工作流 + 保存
content_pipeline → 完成 → save_workflow_output → Obsidian
```

---

### 注意事项

**适合场景**：
- 快速捕获AI生成内容
- 自动分类和归档
- 建立知识双链
- 维护MOC索引

**不适合场景**：
- 需要图形化操作时
- 编辑已有复杂笔记
- 调整图谱视图

---

## 九、常见问题

**Q: 技能和代理有什么区别？**
A: 技能是单一工具（如锤子），代理是会用工具的人（如木匠）。代理会根据任务自动选择和组合多个技能。

**Q: 什么时候用工作流？**
A: 当任务需要多个步骤、多人协作时用工作流。比如"写一篇文章并发布"就适合用content_pipeline。

**Q: 系统怎么知道选哪个Agent？**
A: 系统会根据你说的关键词匹配。比如说"房产"会自动选realestate-agent，说"调研"会选research-agent。

**Q: 可以自己创建新技能吗？**
A: 可以！用 `agent_skill_creator_skill` 或 `skill_code_generator_skill`。

---

**记住**：用中文说出你的需求就行，不需要记英文命令！

---

## 十、小龙虾（飞书机器人）配置参考

> **小龙虾** 是 Leo 对 OpenClaw/Moltbot 飞书网关的昵称

### 系统架构

```
飞书客户端 ←→ 飞书开放平台 ←→ 小龙虾 Gateway ←→ Leo AI System
                WebSocket          本地运行         项目文件
```

### 版本信息

| 项目 | 值 |
|------|-----|
| 当前版本 | v2026.1.30 |
| 项目名称 | OpenClaw |
| 仓库位置 | D:\moltbot |
| 远程仓库 | github.com/openclaw/openclaw |

### 关键配置文件

| 文件 | 用途 |
|------|------|
| `C:\Users\刘方林\.openclaw\openclaw.json` | 主配置（模型、渠道、网关）|
| `C:\Users\刘方林\.openclaw\agents\main\agent\models.json` | 模型 API 配置（MiniMax、智谱）|
| `C:\Users\刘方林\.openclaw\agents\main\agent\auth-profiles.json` | API Key 认证配置 |
| `D:\moltbot\` | OpenClaw 安装目录 |

### 模型配置说明

**MiniMax (默认)**
```json
{
  "provider": "minimax",
  "api": "anthropic-messages",
  "baseUrl": "https://api.minimax.io/anthropic",
  "modelId": "MiniMax-M2.1"
}
```

**智谱 GLM-4**
```json
{
  "provider": "zhipu",
  "api": "openai-completions",
  "baseUrl": "https://open.bigmodel.cn/api/paas/v4",
  "modelId": "glm-4-plus"
}
```

### 管理脚本

| 脚本 | 用途 | 位置 |
|------|------|------|
| `start_gateway.bat` | 启动小龙虾 | scripts/ |
| `stop_gateway.bat` | 停止小龙虾 | scripts/ |
| `update_xiaolongxia.bat` | 更新小龙虾到最新版 | scripts/ |
| `check_xiaolongxia_update.bat` | 检查是否有新版本 | scripts/ |

### 启动方式

**方式1：双击脚本（推荐）**
```
双击 scripts/start_gateway.bat
```

**方式2：命令行**
```bash
cd D:\moltbot && node openclaw.mjs gateway
```

### 状态检查

```bash
cd D:\moltbot && node openclaw.mjs channels status
```

### 更新小龙虾

```bash
# 方式1：使用脚本
双击 scripts/update_xiaolongxia.bat

# 方式2：手动更新
cd D:\moltbot
git pull origin main
npx pnpm install
npx pnpm build
```

### 常见问题

**Q: Gateway 启动后飞书收不到消息？**
A: 检查 `.openclaw/openclaw.json` 中的 channels.feishu 配置是否正确。

**Q: 飞书报错 "No API key found for provider 'minimax'"？**
A: 这是配置目录问题。运行 `scripts/start_gateway.bat` 重启 Gateway，系统会自动修复目录联结。

**Q: 如何切换模型？**
A: 在飞书中发送 `/model minimax/MiniMax-M2.1` 或 `/model GLM4`。

**Q: 小龙虾断线了怎么办？**
A: 运行 `scripts/start_gateway.bat` 重新启动。

**Q: 如何检查模型配置是否正确？**
A: 运行以下命令：
```bash
cd D:\moltbot && node openclaw.mjs agents list
```

---

## 附录一：命名规范与去重机制

> **重要**: 所有 Skills、Agents、Workflows 必须符合以下标准

### 命名规范（强制）

| 类型 | 格式 | 示例 |
|-----|------|------|
| 技能目录 | `{功能}_{类型}_skill` | `web_search_skill` |
| 代理目录 | `{领域}_agent` | `research_agent` |
| 工作流目录 | `{业务}_pipeline` | `content_pipeline` |
| Python类 | `PascalCase` | `ResearchAgent` |
| Python函数/变量 | `snake_case` | `execute_task` |

**禁止使用**:
- `-` 连字符
- 空格
- 大写字母开头的目录/文件名
- 中文目录名

### 去重机制（强制）

**新增前检查**:
- [ ] 功能重复检查（搜索 skill_index）
- [ ] 命名冲突检查
- [ ] 能力重叠评估

**重复处理**:
- 功能完全相同 → 合并为最优实现
- 功能部分重叠 → 整合能力
- 功能相似但不同 → 保留并明确区分

### 目录规范化状态

| 状态 | 原名称 | 新名称 |
|---------|------|---------|
| ✅ 已完成 | `剪口播` | `cut_speech_skill` |
| ✅ 已完成 | `剪辑` | `video_editing_skill` |
| ✅ 已完成 | `字幕` | `subtitle_skill` |
| ✅ 已完成 | `安装` | `install_skill` |
| ✅ 已完成 | `自更新` | `auto_update_skill` |

---

## 附录二：系统记忆体系（给AI看的）

> 以下内容主要给 Claude Code 等AI助手参考，人类用户无需记忆。

### 核心文件优先级（AI必读）

| 优先级 | 文件 | 说明 |
|--------|------|------|
| 🔴 最高 | `src/leo_knowledge/context/user_profile.md` | 核心！Leo的业务、目标、价值观 |
| 🟠 高 | `CLAUDE.md` | 项目级指令 |
| 🟡 中 | `src/leo_knowledge/context/development_guide.md` | 开发规范、命名规则 |
| 🟢 参考 | `src/leo_knowledge/context/system_architecture.md` | 完整架构文档 |

### 记忆体系5层架构

```
Layer 5: 全局配置 (C:\Users\刘方林\.claude\settings.json)
Layer 4: 项目配置 (.claude/settings.local.json)
Layer 3: 静态上下文 (src/leo_knowledge/context/)
    ├── user_profile.md      ← AI首先读取
    ├── development_guide.md ← 开发规范
    └── system_architecture.md ← 架构参考
Layer 2: 动态索引 (src/leo_knowledge/context/)
    ├── capability_index.md
    └── docs/reference/skill_index.md
Layer 1: 动态状态 (项目根目录)
    ├── task_plan.md
    ├── findings.md
    └── progress.md
```

### 三大系统文件位置

| 系统 | 根目录 | 关键子目录 |
|------|--------|-----------|
| Leo AI System | `d:\桌面\leo_ai_system` | `src/leo_skills/`, `src/leo_subagents/`, `src/leo_workflows/` |
| OpenClaw | `D:\moltbot` | `.openclaw/agents/`, `scripts/` |
| 飞书配置 | `C:\Users\刘方林` | `.openclaw/openclaw.json` |

---

*本文档最后更新：2026-02-01 | 说"更新入门指南"可刷新*
