# Leo AI System 技能索引

> 基于 [awesome-claude-skills](docs/reference/awesome-claude-skills/README.md) 和 [ai_coding_project_base](docs/reference/ai_coding_project_base/) 构建

## 目录

- [核心技能 (Core)](#核心技能-core)
- [测试技能 (Testing)](#测试技能-testing)
- [开发技能 (Development)](#开发技能-development)
- [脚手架技能 (Scaffold)](#脚手架技能-scaffold)
- [工具技能 (Tools)](#工具技能-tools)
- [DevOps 技能](#devops-技能)
- [安全技能](#安全技能)
- [外部推荐技能](#外部推荐技能)

---

## 核心技能 (Core)

| 技能 | 路径 | 来源 | 描述 |
|------|------|------|------|
| **planning_with_files_skill** | `src/leo_skills/core/planning_with_files_skill/` | OthmanAdi/planning-with-files | 持久化规划技能，使用任务计划、研究发现和进度追踪三文件模式 |
| **fresh_start_skill** | `src/leo_skills/core/fresh_start_skill/` | ai_coding_project_base | 项目上下文加载，在每个新会话开始时理解项目状态 |
| **phase_prep_skill** | `src/leo_skills/core/phase_prep_skill/` | ai_coding_project_base | 阶段准备，检查先决条件并预览人工审核项 |
| **phase_start_skill** | `src/leo_skills/core/phase_start_skill/` | ai_coding_project_base | 阶段执行，自主执行阶段中的所有任务 |
| **phase_checkpoint_skill** | `src/leo_skills/core/phase_checkpoint_skill/` | ai_coding_project_base | 阶段检查点，运行测试、安全扫描并验证完成情况 |
| **progress_skill** | `src/leo_skills/core/progress_skill/` | ai_coding_project_base | 进度查看，显示执行计划中的进度 |
| **populate_state_skill** | `src/leo_skills/core/populate_state_skill/` | ai_coding_project_base | 状态初始化，初始化阶段状态文件 |

---

## 测试技能 (Testing)

| 技能 | 路径 | 来源 | 描述 |
|------|------|------|------|
| **code_verification_skill** | `src/leo_skills/testing/code_verification_skill/` | ai_coding_project_base | 多代理代码验收标准验证 |
| **auto_verify_skill** | `src/leo_skills/testing/auto_verify_skill/` | ai_coding_project_base | 自动化验证，在人工审核前自动检查 |
| **browser_verification_skill** | `src/leo_skills/testing/browser_verification_skill/` | ai_coding_project_base | 浏览器验证，使用 Playwright 验证 Web 应用 |
| **verify_task_skill** | `src/leo_skills/testing/verify_task_skill/` | ai_coding_project_base | 任务验证，验证单个任务是否符合验收标准 |
| **spec_verification_skill** | `src/leo_skills/testing/spec_verification_skill/` | ai_coding_project_base | 规格验证，验证规范文档质量 |
| **criteria_audit_skill** | `src/leo_skills/testing/criteria_audit_skill/` | ai_coding_project_base | 验收标准审计，验证任务验收标准元数据 |
| **unit_test_generator_skill** | `src/leo_skills/testing/unit_test_generator_skill/` | Leo System | 单元测试生成器 |
| **e2e_test_generator_skill** | `src/leo_skills/testing/e2e_test_generator_skill/` | Leo System | E2E 测试生成器 |
| **api_test_generator_skill** | `src/leo_skills/testing/api_test_generator_skill/` | Leo System | API 测试生成器 |

---

## 开发技能 (Development)

| 技能 | 路径 | 来源 | 描述 |
|------|------|------|------|
| **skill_code_generator_skill** | `src/leo_skills/development/skill_code_generator_skill/` | Leo System | 技能代码生成器 |

---

## 脚手架技能 (Scaffold)

| 技能 | 路径 | 来源 | 描述 |
|------|------|------|------|
| **bootstrap_skill** | `src/leo_skills/scaffold/bootstrap_skill/` | ai_coding_project_base | 快速启动，从现有上下文生成计划 |
| **setup_skill** | `src/leo_skills/scaffold/setup_skill/` | ai_coding_project_base | 项目初始化，初始化项目目录结构 |
| **fullstack_project_scaffold_skill** | `src/leo_skills/scaffold/fullstack_project_scaffold_skill/` | Leo System | 全栈项目脚手架 |
| **t3_stack_scaffold_skill** | `src/leo_skills/scaffold/t3_stack_scaffold_skill/` | Leo System | T3 Stack 脚手架 |

---

## 工具技能 (Tools)

| 技能 | 路径 | 来源 | 描述 |
|------|------|------|------|
| **add_todo_skill** | `src/leo_skills/tools/add_todo_skill/` | ai_coding_project_base | 添加 TODO 项 |
| **list_todos_skill** | `src/leo_skills/tools/list_todos_skill/` | ai_coding_project_base | 列出并分析 TODO 项 |
| **run_todos_skill** | `src/leo_skills/tools/run_todos_skill/` | ai_coding_project_base | 执行标记为 ready 的 TODO 项 |
| **audit_skills_skill** | `src/leo_skills/tools/audit_skills_skill/` | ai_coding_project_base | 审计技能质量和合规性 |
| **codex_review_skill** | `src/leo_skills/tools/codex_review_skill/` | ai_coding_project_base | Codex CLI 交叉审查 |
| **update_docs_skill** | `src/leo_skills/tools/update_docs_skill/` | ai_coding_project_base | 文档更新，将代码变更同步到文档 |
| **update_target_projects_skill** | `src/leo_skills/tools/update_target_projects_skill/` | ai_coding_project_base | 同步目标项目，更新工具包项目 |
| **vision_audit_skill** | `src/leo_skills/tools/vision_audit_skill/` | ai_coding_project_base | 愿景审计，审计愿景一致性 |
| **skill_manager_skill** | `src/leo_skills/tools/skill_manager_skill/` | Leo System | 技能管理器 |
| **skill_evolution_manager_skill** | `src/leo_skills/tools/skill_evolution_manager_skill/` | Leo System | 技能演进管理器 |
| **skill_evolution_assistant_skill** | `src/leo_skills/tools/skill_evolution_assistant_skill/` | Leo System | 技能演进助手 |
| **agent_skill_creator_skill** | `src/leo_skills/tools/agent_skill_creator_skill/` | Leo System | 代理技能创建器 |
| **subagent_creator_skill** | `src/leo_skills/tools/subagent_creator_skill/` | Leo System | 子代理创建器 |
| **github_to_skills_skill** | `src/leo_skills/tools/github_to_skills_skill/` | Leo System | GitHub 技能转换器 |
| **github_skills_monitor_skill** | `src/leo_skills/tools/github_skills_monitor_skill/` | Leo System | GitHub 技能监控器，实时检测并自动加载 |
| **github_skills_updater_skill** | `src/leo_skills/tools/github_skills_updater_skill/` | Leo System | GitHub 技能自动更新器，检测已注册技能的远程更新 |

---

## DevOps 技能

| 技能 | 路径 | 来源 | 描述 |
|------|------|------|------|
| **configure_verification_skill** | `src/leo_skills/devops/configure_verification_skill/` | ai_coding_project_base | 配置验证，设置测试、lint、构建命令 |
| **vercel_preview_skill** | `src/leo_skills/devops/vercel_preview_skill/` | ai_coding_project_base | Vercel 预览，解析预览部署 URL |
| **dockerfile_generator_skill** | `src/leo_skills/devops/dockerfile_generator_skill/` | Leo System | Dockerfile 生成器 |
| **nginx_config_generator_skill** | `src/leo_skills/devops/nginx_config_generator_skill/` | Leo System | Nginx 配置生成器 |
| **github_actions_generator_skill** | `src/leo_skills/devops/github_actions_generator_skill/` | Leo System | GitHub Actions 生成器 |

---

## 安全技能

| 技能 | 路径 | 来源 | 描述 |
|------|------|------|------|
| **security_scan_skill** | `src/leo_skills/security/security_scan_skill/` | ai_coding_project_base | 安全扫描，运行依赖审计、密钥检测和静态分析 |
| **oauth_login_skill** | `src/leo_skills/security/oauth_login_skill/` | ai_coding_project_base | OAuth 登录，完成浏览器验证的 OAuth 流程 |

---

## 实用工具技能 (Utilities)

| 技能 | 路径 | 来源 | 描述 |
|------|------|------|------|
| **analyze_sessions_skill** | `src/leo_skills/utilities/analyze_sessions_skill/` | ai_coding_project_base | 分析会话日志 |
| **tech_debt_check_skill** | `src/leo_skills/utilities/tech_debt_check_skill/` | ai_coding_project_base | 技术债务检查 |
| **data_analyzer_skill** | `src/leo_skills/utilities/data_analyzer_skill/` | Leo System | 数据分析器 |
| **obsidian_sync_skill** | `src/leo_skills/utilities/obsidian_sync_skill/` | Leo System | Obsidian 同步 |
| **research_assistant_skill** | `src/leo_skills/utilities/research_assistant_skill/` | Leo System | 研究助手 |
| **tech_extractor_skill** | `src/leo_skills/utilities/tech_extractor_skill/` | Leo System | 技术提取器 |
| **web_search_skill** | `src/leo_skills/utilities/web_search_skill/` | Leo System | 网络搜索 |
| **business_research_skill** | `src/leo_skills/utilities/business_research_skill/` | Leo System | 商业研究 |

---

## 外部推荐技能

以下技能来自社区推荐，可选择性集成：

### 优先推荐

| 技能 | 来源 | 用途 |
|------|------|------|
| **obra/superpowers** | GitHub | 20+ 核心技能库（TDD、调试、协作模式） |
| **playwright-skill** | GitHub | 通用浏览器自动化 |
| **skill-creator** | Anthropic官方 | 交互式技能创建向导 |

### 文档技能

| 技能 | 来源 | 用途 |
|------|------|------|
| **docx** | Anthropic官方 | Word 文档处理 |
| **pdf** | Anthropic官方 | PDF 操作工具包 |
| **pptx** | Anthropic官方 | PowerPoint 演示文稿 |
| **xlsx** | Anthropic官方 | Excel 电子表格 |

### 设计与创意

| 技能 | 来源 | 用途 |
|------|------|------|
| **algorithmic-art** | Anthropic官方 | 使用 p5.js 创建生成艺术 |
| **canvas-design** | Anthropic官方 | 设计视觉艺术 |
| **slack-gif-creator** | Anthropic官方 | 创建动画 GIF |

### 开发技能

| 技能 | 来源 | 用途 |
|------|------|------|
| **frontend-design** | Anthropic官方 | 前端设计，避免"AI slop" |
| **artifacts-builder** | Anthropic官方 | 构建 Claude.ai HTML 组件 |
| **mcp-builder** | Anthropic官方 | MCP 服务器创建指南 |
| **webapp-testing** | Anthropic官方 | 本地 Web 应用测试 |

### 安全技能

| 技能 | 来源 | 用途 |
|------|------|------|
| **Trail of Bits Security** | GitHub | CodeQL/Semgrep 静态分析 |

---

## 技能索引

- 查看完整技能列表: [SKILLS_CATALOG.md](../SKILLS_CATALOG.md)
- 查看能力索引: [capability_index.md](../../leo_knowledge/context/capability_index.md)

## 更新日志

### 2026-02-01
- 新增 **github_skills_monitor_skill** - GitHub技能实时监控器
- 新增 **github_skills_updater_skill** - GitHub技能自动更新器
- 完善工作逻辑：检测GitHub技能 → 分类 → 自动加载 → 自动更新

### 2026-01-29
- 从 ai_coding_project_base 集成了 25 个新技能
- 创建了统一的技能索引文档
- 核心技能：fresh-start, phase-*, progress, populate-state
- 测试技能：code-verification, auto-verify, browser-verification, verify-task, spec-verification, criteria-audit
