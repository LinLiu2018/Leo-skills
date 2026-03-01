# Leo AI System 技能分级索引

> 更新于 2026-03-01（全部 C/D 级技能已升级为 A 级）
> 供 Claude Code / OpenClaw 在每次任务前快速了解可用能力

## 分级说明

| 等级 | 含义 | Python 代码特征 |
|------|------|----------------|
| **A 生产级** | 有完整业务逻辑，可直接使用 | 200+ 行独立实现 |
| **B 可用级** | 有一定实现，可能需要完善 | 60-200 行，有自己的逻辑 |

> **2026-03-01 升级**: 原 22 个 C 级（71行wrapper）和 5 个 D 级（空壳）技能已全部重写为 A 级生产实现。
> C/D 级分类已清空。

---

## A 级 - 生产级（44 个）

> 有完整业务逻辑，可直接使用

### 业务技能 (business/)
| 技能 | 行数 | 说明 |
|------|------|------|
| realestate_skill | 615 | 房产数据分析、价格评估、市场分析 |
| ecommerce_skill | 569 | 电商运营、竞品分析 |
| fission_miniprogram_skill | 550 | 裂变小程序完整实现 |
| sales_sop_skill | 385 | 销售 SOP 流程管理 |
| auto_logger_skill | 414 | 自动日志记录 |
| competitor_content_crawler_skill | 289 | 竞品内容爬取 |
| customer_portrait_skill | 289 | 客户画像分析 |
| video_monitor_skill | 206 | 视频监控技能 |

### 核心技能 (core/)
| 技能 | 行数 | 说明 |
|------|------|------|
| planning_with_files_skill | 630 | 上下文工程核心，文件规划 |
| phase_checkpoint_skill | 590 | 阶段检查点管理 |
| populate_state_skill | 568 | 状态填充 |
| phase_prep_skill | 547 | 阶段准备 |
| evolution_skill | 544 | 技能进化引擎 |
| phase_start_skill | 511 | 阶段启动 |
| progress_skill | 467 | 进度追踪 |
| text_generator_skill | 402 | 文本生成 |

### 协作技能 (collaboration/)
| 技能 | 行数 | 说明 |
|------|------|------|
| dispatching_parallel_agents_skill | 534 | 并行代理调度 |
| brainstorming_skill | 509 | 头脑风暴引导 |
| executing_plans_skill | 427 | 计划执行 |
| writing_plans_skill | 395 | 计划编写 |
| subagent_driven_development_skill | 289 | 子代理驱动开发 |
| receiving_code_review_skill | 278 | 接收代码审查 |
| requesting_code_review_skill | 231 | 请求代码审查 |

### 提示词工程 (prompt_engineering/)
| 技能 | 行数 | 说明 |
|------|------|------|
| prompt_vault_skill | 884 | 提示词库管理（最大技能） |
| prompt_optimizer_skill | 572 | 提示词优化 |
| chain_of_thought_prompter_skill | 509 | 思维链提示 |

### DevOps 技能 (devops/)
| 技能 | 行数 | 说明 |
|------|------|------|
| finishing_development_branch_skill | 455 | 分支收尾流程 |
| using_git_worktrees_skill | 389 | Git worktree 使用 |
| configure_verification_skill | 368 | 配置验证 |
| vercel_preview_skill | 367 | Vercel 预览部署 |

### 工具技能 (tools/)
| 技能 | 行数 | 说明 |
|------|------|------|
| subagent_creator_skill | 569 | 子代理创建 |
| update_docs_skill | 473 | 文档自动更新 |
| github_skills_updater_skill | 383 | GitHub 技能更新 |
| list_todos_skill | 365 | TODO 管理 |
| run_todos_skill | 358 | TODO 执行 |
| skill_evolution_manager_skill | 378 | 技能进化管理 |
| skill_manager_skill | 332 | 技能管理 |
| add_todo_skill | 331 | 添加 TODO |
| github_skills_monitor_skill | 321 | GitHub 技能监控 |
| repo_watch_skill | 318 | 仓库监控 |
| github_to_skills_skill | 294 | GitHub 转技能 |
| chart_generator_skill | 271 | 图表生成 |

### 其他 A 级
| 技能 | 行数 | 分类 |
|------|------|------|
| content_creation/image_generator_skill | 281 | DALL-E 图片生成 |
| content_creation/social_auto_publish_skill | 425 | 社交平台自动发布 |
| content_creation/project_marketing_doc_generator_skill | 403 | 营销文档生成 |
| utilities/business_research_skill | 508 | 商业调研 |
| utilities/analyze_sessions_skill | 433 | 会话分析 |
| utilities/web_search_skill | 382 | 网页搜索 |
| utilities/data_analyzer_skill | 304 | 数据分析 |
| scaffold/bootstrap_skill | 294 | 项目引导 |
| security/oauth_login_skill | 276 | OAuth 登录 |
| debugging/systematic_debugging_skill | 268 | 系统化调试 |
| frontend/vant_weapp_skill | 301 | Vant 小程序组件 |
| frontend/weui_miniprogram_skill | 251 | WeUI 小程序 |
| scaffold/setup_skill | 236 | 项目初始化 |
| tools/skill_orchestrator_skill | 231 | 技能编排 |
| tools/skill_vetter_skill | 220 | 技能审核 |
| tools/audit_skills_skill | 207 | 技能审计 |

---

## B 级 - 可用级（25 个）

> 有一定实现，功能可用但不够完整

| 技能 | 行数 | 分类 |
|------|------|------|
| pocket_crm_skill | 179 | business/ |
| prompt_chaining_orchestrator_skill | 189 | prompt_engineering/ |
| long_context_handler_skill | 173 | prompt_engineering/ |
| xml_structure_builder_skill | 153 | prompt_engineering/ |
| tech_debt_check_skill | 148 | utilities/ |
| twitter_monitor_skill | 137 | intelligence/ |
| codex_review_skill | 131 | tools/ |
| gog_skill | 126 | tools/ |
| memory_enhanced_skill | 118 | core/ |
| fresh_start_skill | 112 | core/ |
| skill_deduplication_skill | 111 | tools/ |
| browser_skill | 110 | tools/ |
| find_skills_skill | 108 | tools/ |
| web_search_enhanced_skill | 99 | utilities/ |
| usage_tracking_skill | 96 | tools/ |
| knowledge_site_creator_skill | 93 | tools/ |
| content_to_action_skill | 92 | tools/ |
| book_learning_skill | 91 | utilities/ |
| github_integration_skill | 139 | tools/ |
| github_auto_register_skill | 162 | tools/ |
| summarize_skill | 76 | utilities/ |
| auto_update_skill | 66 | tools/ |
| videocut/auto_update_skill | 34 | videocut/ |
| videocut/cut_speech_skill | 34 | videocut/ |
| videocut/install_skill | 34 | videocut/ |
| videocut/subtitle_skill | 34 | videocut/ |
| videocut/video_editing_skill | 34 | videocut/ |

---

## C 级 - 已全部升级为 A 级 (2026-03-01)

> 以下 22 个技能已从 71 行 wrapper 重写为 230-762 行的生产级实现

| 技能 | 原行数 | 新行数 | 分类 |
|------|--------|--------|------|
| api_doc_generator_skill | 71 | 230 | backend/ |
| database_migration_skill | 71 | 353 | backend/ |
| database_model_generator_skill | 71 | 486 | backend/ |
| fastapi_endpoint_generator_skill | 71 | 290 | backend/ |
| flask_api_generator_skill | 71 | 491 | backend/ |
| flask_auth_generator_skill | 71 | 310 | backend/ |
| content_layout_leo_skill | 71 | 428 | content_creation/ |
| realestate_news_publisher_skill | 71 | 432 | content_creation/ |
| deployment_script_generator_skill | 71 | 340 | devops/ |
| docker_compose_generator_skill | 71 | 419 | devops/ |
| dockerfile_generator_skill | 71 | 570 | devops/ |
| github_actions_generator_skill | 71 | 396 | devops/ |
| nginx_config_generator_skill | 71 | 377 | devops/ |
| css_layout_generator_skill | 71 | 308 | frontend/ |
| miniprogram_component_generator_skill | 71 | 255 | frontend/ |
| miniprogram_page_generator_skill | 71 | 762 | frontend/ |
| react_component_generator_skill | 71 | 390 | frontend/ |
| vue_component_generator_skill | 71 | 476 | frontend/ |
| vue_page_generator_skill | 71 | 268 | frontend/ |
| flask_api_scaffold_skill | 71 | 358 | scaffold/ |
| fullstack_project_scaffold_skill | 71 | 507 | scaffold/ |
| miniprogram_project_scaffold_skill | 71 | 294 | scaffold/ |
| t3_stack_scaffold_skill | 71 | 469 | scaffold/ |
| agent_skill_creator_skill | 71 | 343 | tools/ |
| article_to_prototype_skill | 71 | 365 | tools/ |

---

## D 级 - 已全部升级为 A 级 (2026-03-01)

> 以下 5 个技能已从 9 行空壳重写为完整实现

| 技能 | 原行数 | 新行数 | 分类 |
|------|--------|--------|------|
| skill_code_generator_skill | 9 | 614 | development/ |
| security_scan_skill | 9 | 392 | security/ |
| obsidian_sync_skill | 9 | 481 | utilities/ |
| research_assistant_skill | 9 | 347 | utilities/ |
| tech_extractor_skill | 9 | 274 | utilities/ |

---

## 统计总览

| 等级 | 数量 | 占比 | 说明 |
|------|------|------|------|
| A 生产级 | **71** | **74%** | 可直接使用（含 27 个新升级） |
| B 可用级 | 25 | 26% | 基本可用，可完善 |
| C 包装级 | **0** | 0% | 已全部升级 |
| D 空壳级 | **0** | 0% | 已全部升级 |
| **总计** | **96** | 100% | |

> 2026-03-01 升级成果：C/D 级从 27 个降至 0 个，A 级从 44 个增至 71 个。
