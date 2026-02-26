# Leo AI System - 能力索引

> **自动生成** - 2026-02-26 09:30:14
>
> 本文件由 `scripts/update_capability_index.py` 自动生成
> 请勿手动编辑，运行脚本即可更新

---

## 📊 统计概览

| 类型 | 数量 | 描述 |
|------|------|------|
| 🛠️ Skills | 106 | 可执行技能 |
| 🤖 Agents | 9 | 智能代理 |
| 🔄 Workflows | 8 | 工作流定义 |

**总计**: 123 个能力单元

---

## 🛠️ Skills 索引


### automation

#### auto_logger_skill
- **描述**: auto_logger_skill 技能

- **路径**: `leo_skills\automation\auto_logger_skill`


### backend

#### api_doc_generator_skill
- **描述**: api_doc_generator_skill 技能

- **路径**: `leo_skills\backend\api_doc_generator_skill`

#### database_migration_skill
- **描述**: N/A
- **路径**: `leo_skills\backend\database_migration_skill`

#### database_model_generator_skill
- **描述**: N/A
- **路径**: `leo_skills\backend\database_model_generator_skill`

#### fastapi_endpoint_generator_skill
- **描述**: fastapi_endpoint_generator_skill 技能

- **路径**: `leo_skills\backend\fastapi_endpoint_generator_skill`

#### flask_api_generator_skill
- **描述**: N/A
- **路径**: `leo_skills\backend\flask_api_generator_skill`

#### flask_auth_generator_skill
- **描述**: flask_auth_generator_skill 技能

- **路径**: `leo_skills\backend\flask_auth_generator_skill`


### business

#### competitor_scraper_skill
- **描述**: N/A
- **路径**: `leo_skills\business\ecommerce\competitor_scraper_skill`

#### video_monitor
- **描述**: 监测视频号账号数据，包括粉丝增长、视频表现、互动数据等。
支持单账号监测和多账号对比分析。

- **路径**: `leo_skills\business\video_monitor`


### collaboration

#### brainstorming_skill
- **描述**: 【协作技能】头脑风暴。在任何创造性工作之前必须使用 - 创建功能、构建组件、添加功能或修改行为。
在实现之前探索用户意图、需求和设计。通过自然协作对话帮助将想法转化为完全形成的设计和规范。
基于 obra/superpowers 的 brainstorming 技能。

- **路径**: `leo_skills\collaboration\brainstorming_skill`

#### dispatching_parallel_agents_skill
- **描述**: 【协作技能】分发并行代理。当面对 2+ 个可以无需共享状态或顺序依赖地处理独立任务时使用。
核心理念：每个问题域分发一个代理。让它们并发工作。
基于 obra/superpowers 的 dispatching-parallel-agents 技能。

- **路径**: `leo_skills\collaboration\dispatching_parallel_agents_skill`

#### executing_plans_skill
- **描述**: 【协作技能】执行实施计划。在单独会话中有书面实施计划要执行时使用，带有审查检查点。
核心理念：批量执行，架构师审查检查点。与 writing_plans_skill 配对使用。
基于 obra/superpowers 的 executing-plans 技能。

- **路径**: `leo_skills\collaboration\executing_plans_skill`

#### receiving_code_review_skill
- **描述**: 【协作技能】接收代码审查反馈。在实现建议之前使用，特别是当反馈看起来不清楚或技术上可疑时。
核心理念：验证后再实现。询问后再假设。技术正确性高于社交舒适度。
基于 obra/superpowers 的 receiving-code-review 技能。

- **路径**: `leo_skills\collaboration\receiving_code_review_skill`

#### requesting_code_review_skill
- **描述**: 【协作技能】请求代码审查。在完成任务、实现主要功能或合并之前使用，以验证工作是否符合要求。
核心理念：早审查，常审查。
基于 obra/superpowers 的 requesting-code-review 技能。

- **路径**: `leo_skills\collaboration\requesting_code_review_skill`

#### subagent_driven_development_skill
- **描述**: 【协作技能】子代理驱动开发。在当前会话中执行具有独立任务的实施计划时使用。
核心理念：每个任务一个新子代理 + 两阶段审查（先规范符合性，再代码质量）= 高质量、快速迭代。
基于 obra/superpowers 的 subagent-driven-development 技能。

- **路径**: `leo_skills\collaboration\subagent_driven_development_skill`

#### writing_plans_skill
- **描述**: 【协作技能】编写详细的实施计划。当你有多步骤任务的规格或需求时，在接触代码之前使用。
核心理念：假设工程师对代码库零上下文，文档化他们需要知道的一切。提供小步任务粒度。
基于 obra/superpowers 的 writing-plans 技能。

- **路径**: `leo_skills\collaboration\writing_plans_skill`


### content_creation

#### content_layout_leo_skill
- **描述**: N/A
- **路径**: `leo_skills\content_creation\content_layout_leo_skill`

#### image_generator_skill
- **描述**: N/A
- **路径**: `leo_skills\content_creation\image_generator_skill`

#### project_marketing_doc_generator_skill
- **描述**: N/A
- **路径**: `leo_skills\content_creation\project_marketing_doc_generator_skill`

#### realestate_news_publisher_skill
- **描述**: N/A
- **路径**: `leo_skills\content_creation\realestate_news_publisher_skill`


### core

#### fresh-start
- **描述**: Orient to project structure and load context. Use at the start of each new session or after context reset to understand the project state.
- **路径**: `leo_skills\core\fresh_start_skill`

#### phase-checkpoint
- **描述**: Run checkpoint criteria after completing a phase. Use after /phase-start completes all tasks to verify quality gates before proceeding.
- **路径**: `leo_skills\core\phase_checkpoint_skill`

#### phase-prep
- **描述**: Check prerequisites before starting a phase. Use before /phase-start to verify dependencies are met and context is loaded.
- **路径**: `leo_skills\core\phase_prep_skill`

#### phase-start
- **描述**: Execute all tasks in a phase autonomously. Use after /phase-prep confirms prerequisites are met.
- **路径**: `leo_skills\core\phase_start_skill`

#### planning_with_files_skill
- **描述**: 【核心技能】Manus风格的持久化规划技能。通过三个Markdown文件（task_plan.md、findings.md、progress.md）
实现任务规划、发现记录和进度跟踪。适用于复杂多步骤任务、研究项目或需要>5次工具调用的任务。
核心理念：Context Window = RAM（易失、有限），Filesystem = Disk（持久、无限）
这是Leo AI System的上下文工程基础设施，让整个系统具备"外部记忆"能力。

- **路径**: `leo_skills\core\planning_with_files_skill`

#### populate-state
- **描述**: Generate `.claude/phase-state.json` from `EXECUTION_PLAN.md` and git history. Use to recover phase state after context loss or when joining an existing project.
- **路径**: `leo_skills\core\populate_state_skill`

#### progress
- **描述**: Show progress through EXECUTION_PLAN.md and feature plans. Use to check completion status and identify remaining work.
- **路径**: `leo_skills\core\progress_skill`

#### text_generator_skill
- **描述**: N/A
- **路径**: `leo_skills\core\text_generator_skill`

#### using_superpowers_skill
- **描述**: Use when starting any conversation to establish how to find and use skills, requiring skill invocation before ANY response including clarifying questions
- **路径**: `leo_skills\core\using_superpowers_skill`

#### writing_skills_skill
- **描述**: Use when creating new skills, editing existing skills, or verifying skills work before deployment
- **路径**: `leo_skills\core\writing_skills_skill`


### debugging

#### systematic_debugging_skill
- **描述**: 【调试技能】系统化四阶段根因分析方法。遇到任何bug、测试失败或意外行为时使用。
核心理念：永远先找到根因再尝试修复。避免随机修复浪费时间和制造新bug。
基于 obra/superpowers 的 systematic-debugging 技能。

- **路径**: `leo_skills\debugging\systematic_debugging_skill`


### development

#### skill_code_generator_skill
- **描述**: Automated skill generation tool for creating Leo AI skills with templates, scaffolding, code patterns, configuration files, documentation, and testing framework setup. Activates when user asks to create a new skill, generate skill code, scaffold a skill, or automate skill creation.
- **路径**: `leo_skills\development\skill_code_generator_skill`


### devops

#### configure-verification
- **描述**: Configure verification commands for this project. Use when setting up a new project or when verification-config.json is missing or incomplete.
- **路径**: `leo_skills\devops\configure_verification_skill`

#### deployment_script_generator_skill
- **描述**: deployment_script_generator_skill 技能

- **路径**: `leo_skills\devops\deployment_script_generator_skill`

#### docker_compose_generator_skill
- **描述**: docker_compose_generator_skill 技能

- **路径**: `leo_skills\devops\docker_compose_generator_skill`

#### dockerfile_generator_skill
- **描述**: N/A
- **路径**: `leo_skills\devops\dockerfile_generator_skill`

#### finishing_development_branch_skill
- **描述**: 【DevOps技能】完成开发分支。当实现完成、所有测试通过，需要决定如何集成工作时使用。
核心理念：验证测试 → 呈现选项 → 执行选择 → 清理。
基于 obra/superpowers 的 finishing-a-development-branch 技能。

- **路径**: `leo_skills\devops\finishing_development_branch_skill`

#### github_actions_generator_skill
- **描述**: N/A
- **路径**: `leo_skills\devops\github_actions_generator_skill`

#### nginx_config_generator_skill
- **描述**: N/A
- **路径**: `leo_skills\devops\nginx_config_generator_skill`

#### using_git_worktrees_skill
- **描述**: 【DevOps技能】使用 Git Worktree 创建隔离工作空间。在开始需要与当前工作区隔离的功能工作或执行实施计划之前使用。
核心理念：系统化目录选择 + 安全验证 = 可靠的隔离。
基于 obra/superpowers 的 using-git-worktrees 技能。

- **路径**: `leo_skills\devops\using_git_worktrees_skill`

#### vercel-preview
- **描述**: Resolve Vercel preview deployment URL for the current git branch. Invoked by browser-verification when deployment.enabled is true, or directly to check deployment status.
- **路径**: `leo_skills\devops\vercel_preview_skill`


### frontend

#### css_layout_generator_skill
- **描述**: css_layout_generator_skill 技能

- **路径**: `leo_skills\frontend\css_layout_generator_skill`

#### miniprogram_component_generator_skill
- **描述**: miniprogram_component_generator_skill 技能

- **路径**: `leo_skills\frontend\miniprogram_component_generator_skill`

#### miniprogram_page_generator_skill
- **描述**: N/A
- **路径**: `leo_skills\frontend\miniprogram_page_generator_skill`

#### react_component_generator_skill
- **描述**: N/A
- **路径**: `leo_skills\frontend\react_component_generator_skill`

#### vant_weapp_skill
- **描述**: N/A
- **路径**: `leo_skills\frontend\vant_weapp_skill`

#### vue_component_generator_skill
- **描述**: N/A
- **路径**: `leo_skills\frontend\vue_component_generator_skill`

#### vue_page_generator_skill
- **描述**: N/A
- **路径**: `leo_skills\frontend\vue_page_generator_skill`

#### weui_miniprogram_skill
- **描述**: N/A
- **路径**: `leo_skills\frontend\weui_miniprogram_skill`


### intelligence

#### twitter_monitor_skill
- **描述**: 监控 Twitter 上的 AI 科技博主，采集最新推文并存储到数据库
- **路径**: `leo_skills\intelligence\twitter_monitor_skill`


### prompt_engineering

#### Chain of Thought Prompter
- **描述**: 使用思维链技术引导 AI 进行结构化推理,提高复杂任务的准确性
- **路径**: `leo_skills\prompt_engineering\chain_of_thought_prompter`

#### Long Context Handler
- **描述**: 优化长文本上下文处理,确保 AI 能够有效处理和理解大量文档内容
- **路径**: `leo_skills\prompt_engineering\long_context_handler`

#### Prompt Chaining Orchestrator
- **描述**: 将复杂任务分解为多个顺序步骤,通过提示词链提高准确性和可靠性
- **路径**: `leo_skills\prompt_engineering\prompt_chaining_orchestrator`

#### Prompt Optimizer
- **描述**: 优化和改进用户的提示词,使其更加明确、具体和有效,基于 Claude 官方最佳实践
- **路径**: `leo_skills\prompt_engineering\prompt_optimizer`

#### XML Structure Builder
- **描述**: 使用 XML 标签结构化提示词,提高清晰度、准确性和可维护性
- **路径**: `leo_skills\prompt_engineering\xml_structure_builder`


### scaffold

#### bootstrap
- **描述**: Generate feature plan with codebase-aware context. Use when starting a new feature in an existing codebase to skip full spec workflow.
- **路径**: `leo_skills\scaffold\bootstrap_skill`

#### flask_api_scaffold_skill
- **描述**: flask_api_scaffold_skill 技能

- **路径**: `leo_skills\scaffold\flask_api_scaffold_skill`

#### fullstack_project_scaffold_skill
- **描述**: N/A
- **路径**: `leo_skills\scaffold\fullstack_project_scaffold_skill`

#### miniprogram_project_scaffold_skill
- **描述**: miniprogram_project_scaffold_skill 技能

- **路径**: `leo_skills\scaffold\miniprogram_project_scaffold_skill`

#### setup
- **描述**: Initialize a new project with the AI Coding Toolkit. Use when setting up toolkit skills in a new or existing project.
- **路径**: `leo_skills\scaffold\setup_skill`

#### t3_stack_scaffold_skill
- **描述**: N/A
- **路径**: `leo_skills\scaffold\t3_stack_scaffold_skill`


### security

#### oauth-login
- **描述**: Complete OAuth login flow and store tokens for verification. Use when browser verification requires authenticated sessions.
- **路径**: `leo_skills\security\oauth_login_skill`

#### security_scan_skill
- **描述**: N/A
- **路径**: `leo_skills\security\security_scan_skill`


### testing

#### api_test_generator_skill
- **描述**: api_test_generator_skill 技能

- **路径**: `leo_skills\testing\api_test_generator_skill`

#### auto-verify
- **描述**: Attempt automated verification of criteria before falling back to manual. Parses criterion text for automation hints and executes appropriate tool (curl, browser, file check). Invoked by verify-task and phase-checkpoint for MANUAL criteria.
- **路径**: `leo_skills\testing\auto_verify_skill`

#### browser-verification
- **描述**: Verify browser-based acceptance criteria using ExecuteAutomation Playwright MCP with multi-tool fallback chain. Invoked by verify-task and phase-checkpoint for BROWSER:* criteria.
- **路径**: `leo_skills\testing\browser_verification_skill`

#### code-verification
- **描述**: Multi-agent code verification workflow using a main agent and sub-agent loop. Use when verifying code against requirements, acceptance criteria, or quality standards. Triggers on requests to verify, validate, or check code against specifications, checklists, or instructions.
- **路径**: `leo_skills\testing\code_verification_skill`

#### criteria-audit
- **描述**: Validate EXECUTION_PLAN.md for verification metadata, manual reasons, and testability. Use when preparing Phase 1 or after editing EXECUTION_PLAN.md.
- **路径**: `leo_skills\testing\criteria_audit_skill`

#### e2e_test_generator_skill
- **描述**: N/A
- **路径**: `leo_skills\testing\e2e_test_generator_skill`

#### spec-verification
- **描述**: Verify generated specification documents for context preservation and quality issues. Automatically triggered after document generation. Checks that upstream requirements are preserved and identifies common specification problems.
- **路径**: `leo_skills\testing\spec_verification_skill`

#### test_driven_development_skill
- **描述**: 【测试技能】测试驱动开发（TDD）实践。实现任何功能或修复bug时，在编写实现代码之前使用。
核心理念：先写测试，观察失败，编写最少代码通过。不先看测试失败，就不知道是否测试了正确的东西。
基于 obra/superpowers 的 test-driven-development 技能。

- **路径**: `leo_skills\testing\test_driven_development_skill`

#### unit_test_generator_skill
- **描述**: N/A
- **路径**: `leo_skills\testing\unit_test_generator_skill`

#### verification_before_completion_skill
- **描述**: 【测试技能】完成前验证。在声称工作完成、修复或通过之前，在提交或创建 PR 之前使用。
核心理念：证据在断言之前，始终。
基于 obra/superpowers 的 verification-before-completion 技能。

- **路径**: `leo_skills\testing\verification_before_completion_skill`

#### verify-task
- **描述**: Run code-verification on a specific task. Use to verify a single task's acceptance criteria after implementation.
- **路径**: `leo_skills\testing\verify_task_skill`


### tools

#### add-todo
- **描述**: Add a properly formatted TODO item to TODOS.md. Use when you need to capture a new task, bug, or feature request during development.
- **路径**: `leo_skills\tools\add_todo_skill`

#### agent_skill_creator_skill
- **描述**: This enhanced skill should be used when the user asks to create an agent, automate a repetitive workflow, create a custom skill, or needs advanced agent creation capabilities. Activates with phrases like every day, daily I have to, I need to repeat, create agent for, automate workflow, create skill for, need to automate, turn process into agent. Supports single agents, multi-agent suites, transcript processing, template-based creation, and interactive configuration. Claude will use the enhanced protocol to research APIs, define analyses, structure everything, implement functional code, and create complete skills autonomously with optional user guidance.
- **路径**: `leo_skills\tools\agent_skill_creator_skill`

#### article_to_prototype_skill
- **描述**: N/A
- **路径**: `leo_skills\tools\article_to_prototype_skill`

#### audit-skills
- **描述**: Audits skills for best practice violations including length, checklists, verification steps, and progressive disclosure. Use after creating skills, during reviews, or to improve existing skills. Produces prioritized improvement suggestions.
- **路径**: `leo_skills\tools\audit_skills_skill`

#### chart_generator_skill
- **描述**: N/A
- **路径**: `leo_skills\tools\chart_generator_skill`

#### codex-review
- **描述**: Have OpenAI Codex review the current branch with documentation research. Use for second-opinion code reviews or when you want cross-AI verification.
- **路径**: `leo_skills\tools\codex_review_skill`

#### github_skills_monitor_skill
- **描述**: N/A
- **路径**: `leo_skills\tools\github_skills_monitor_skill`

#### github_skills_updater_skill
- **描述**: N/A
- **路径**: `leo_skills\tools\github_skills_updater_skill`

#### github_to_skills_skill
- **描述**: N/A
- **路径**: `leo_skills\tools\github_to_skills_skill`

#### list-todos
- **描述**: Analyze and prioritize TODO items from TODOS.md. Use when planning work or deciding what to implement next.
- **路径**: `leo_skills\tools\list_todos_skill`

#### repo_watch_skill
- **描述**: N/A
- **路径**: `leo_skills\tools\repo_watch_skill`

#### run-todos
- **描述**: Implement [ready]-tagged TODO items with commits. Use after /list-todos has clarified requirements and marked items as ready.
- **路径**: `leo_skills\tools\run_todos_skill`

#### skill_evolution_assistant_skill
- **描述**: N/A
- **路径**: `leo_skills\tools\skill_evolution_assistant_skill`

#### skill_evolution_manager_skill
- **描述**: N/A
- **路径**: `leo_skills\tools\skill_evolution_manager_skill`

#### skill_manager_skill
- **描述**: N/A
- **路径**: `leo_skills\tools\skill_manager_skill`

#### subagent_creator_skill
- **描述**: N/A
- **路径**: `leo_skills\tools\subagent_creator_skill`

#### update-docs
- **描述**: Update documentation after commits. Syncs README, AGENTS.md, CHANGELOG, and docs/ with code changes. Use after commits or to analyze working tree changes.
- **路径**: `leo_skills\tools\update_docs_skill`

#### update-target-projects
- **描述**: Discover and sync all toolkit-using projects with the latest skills. Use after modifying skills to propagate changes to target projects.
- **路径**: `leo_skills\tools\update_target_projects_skill`

#### vision-audit
- **描述**: Audit vision alignment, analyze SDLC gaps, research trends, and generate feature proposals.
- **路径**: `leo_skills\tools\vision_audit_skill`


### utilities

#### analyze-sessions
- **描述**: Analyze session logs to discover automation opportunities. Use periodically to find patterns in your Claude Code usage that could be automated.
- **路径**: `leo_skills\utilities\analyze_sessions_skill`

#### business_research_skill
- **描述**: N/A
- **路径**: `leo_skills\utilities\business_research_skill`

#### data_analyzer_skill
- **描述**: N/A
- **路径**: `leo_skills\utilities\data_analyzer_skill`

#### obsidian_sync_skill
- **描述**: N/A
- **路径**: `leo_skills\utilities\obsidian_sync_skill`

#### research_assistant_skill
- **描述**: N/A
- **路径**: `leo_skills\utilities\research_assistant_skill`

#### tech-debt-check
- **描述**: Detect technical debt patterns in code including duplication, complexity, and maintainability issues. Use at phase checkpoints or on-demand to assess code quality.
- **路径**: `leo_skills\utilities\tech_debt_check_skill`

#### tech_extractor_skill
- **描述**: N/A
- **路径**: `leo_skills\utilities\tech_extractor_skill`

#### web_search_skill
- **描述**: N/A
- **路径**: `leo_skills\utilities\web_search_skill`


### videocut_skills

#### videocut:auto_update
- **描述**: 自更新 skills。记录用户反馈，更新方法论和规则。触发词：更新规则、记录反馈、改进skill
- **路径**: `leo_skills\videocut_skills\auto_update_skill`

#### videocut:cut_speech
- **描述**: 口播视频转录和口误识别。生成审查稿和删除任务清单。触发词：剪口播、处理视频、识别口误
- **路径**: `leo_skills\videocut_skills\cut_speech_skill`

#### videocut:install
- **描述**: 环境准备。安装依赖、下载模型、验证环境。触发词：安装、环境准备、初始化
- **路径**: `leo_skills\videocut_skills\install_skill`

#### videocut:subtitle
- **描述**: 字幕生成与烧录。转录→词典纠错→审核→烧录。触发词：加字幕、生成字幕、字幕
- **路径**: `leo_skills\videocut_skills\subtitle_skill`

#### videocut:video_editing
- **描述**: 执行视频剪辑。根据确认的删除任务执行FFmpeg剪辑，循环直到零口误，生成字幕。触发词：执行剪辑、开始剪、确认剪辑
- **路径**: `leo_skills\videocut_skills\video_editing_skill`


---

## 🤖 Agents 索引


### product_manager_agent
- **类型**: planner
- **描述**: 产品经理代理，负责需求分析、PRD编写和用户故事设计
- **优先级**: 1
- **触发词**: 分析需求, 写PRD, 用户故事, 产品设计, PRD
- **技能**: research_assistant_skill, web_search_skill
- **路径**: `src\leo_subagents\agents\product_manager_agent`


### architect_agent
- **类型**: designer
- **描述**: 架构师代理，负责技术选型、系统设计和数据库设计
- **优先级**: 2
- **触发词**: 架构设计, 技术选型, 系统设计, 数据库设计, architecture
- **技能**: database_model_generator_skill, api_doc_generator_skill, research_assistant_skill
- **路径**: `src\leo_subagents\agents\architect_agent`


### research_agent
- **类型**: researcher
- **描述**: 研究代理，负责信息收集、文献调研和研究报告生成
- **优先级**: 2
- **触发词**: 研究, 调研, 收集信息, 分析报告, research
- **技能**: research_assistant_skill, web_search_skill, article_to_prototype_skill
- **路径**: `src\leo_subagents\agents\research_agent`


### analysis_agent
- **类型**: analyzer
- **描述**: 分析代理，负责数据分析、趋势洞察和决策支持
- **优先级**: 3
- **触发词**: 分析数据, 生成报告, 统计, 洞察, analyze
- **技能**: data_analyzer_skill
- **路径**: `src\leo_subagents\agents\analysis_agent`


### creative_agent
- **类型**: creator
- **描述**: 创作代理，负责内容创作、创意生成和文案撰写
- **优先级**: 4
- **触发词**: 创作内容, 生成文案, 写作, 设计, create
- **技能**: content_layout_leo_skill, article_to_prototype_skill
- **路径**: `src\leo_subagents\agents\creative_agent`


### realestate_agent
- **类型**: realestate
- **描述**: 房地产专业代理，负责房产业务自动化、客户跟进和房源管理
- **优先级**: 5
- **触发词**: 房地产, 楼盘, 项目营销, 房源, real estate
- **技能**: project_marketing_doc_generator_skill, realestate_news_publisher_skill, web_search_skill
- **路径**: `src\leo_subagents\agents\realestate_agent`


### ecommerce_agent
- **类型**: ecommerce
- **描述**: 电商代理，负责电商运营自动化、订单处理和竞品分析
- **优先级**: 6
- **触发词**: 电商, 商城, 订单, 运营, 竞品分析
- **技能**: research_assistant_skill, article_to_prototype_skill
- **路径**: `src\leo_subagents\agents\ecommerce_agent`


### ai_news_summary_agent
- **类型**: intelligence
- **描述**: 每日情报战略官 - 全球商业情报深度版，自动推送到飞书
- **优先级**: 7
- **触发词**: 今日新闻摘要, 全球商业情报, 每日情报, 新闻摘要, 定时推送
- **技能**: web_search_skill, research_assistant_skill, obsidian_sync_skill
- **路径**: `src\leo_subagents\agents\ai_news_summary_agent`


### mobile_agent
- **类型**: developer
- **描述**: 移动开发代理，负责小程序、React Native和Flutter开发
- **优先级**: 16
- **触发词**: 小程序开发, 移动开发, React Native, Flutter, mobile
- **技能**: miniprogram_page_generator_skill, miniprogram_component_generator_skill, miniprogram_project_scaffold_skill
- **路径**: `src\leo_subagents\agents\mobile_agent`


---

## 🔄 Workflows 索引


### code-review-pipeline
- **描述**: 自动化代码审查工作流 - 静态分析 + 代码质量评估 + 安全扫描
- **版本**: 1.0
- **步骤数**: 4
- **路径**: `src\leo_workflows\definitions\code_review_pipeline.yaml`


### content-pipeline
- **描述**: 从研究到发布的完整内容生产流程
- **版本**: 1.0
- **步骤数**: 7
- **路径**: `src\leo_workflows\definitions\content_pipeline.yaml`


### data-analysis-pipeline
- **描述**: 数据分析工作流 - 数据收集 + 清洗 + 分析 + 可视化
- **版本**: 1.0
- **步骤数**: 8
- **路径**: `src\leo_workflows\definitions\analysis_pipeline.yaml`


### deployment-pipeline
- **描述**: 自动化部署工作流 - Docker构建 + 测试 + 多环境部署
- **版本**: 1.0
- **步骤数**: 5
- **路径**: `src\leo_workflows\definitions\deployment_pipeline.yaml`


### fullstack-dev-pipeline
- **描述**: 从需求到部署的完整开发流程
- **版本**: 1.0
- **步骤数**: 6
- **路径**: `src\leo_workflows\definitions\fullstack_dev_pipeline.yaml`


### miniprogram-fission-pipeline
- **描述**: 裂变分销小程序开发工作流 - 需求分析 + 代码生成 + 测试 + 部署
- **版本**: 1.0
- **步骤数**: 7
- **路径**: `src\leo_workflows\definitions\miniprogram_fission_pipeline.yaml`


### research-pipeline
- **描述**: 深度研究报告生成流程
- **版本**: 1.0
- **步骤数**: 5
- **路径**: `src\leo_workflows\definitions\research_pipeline.yaml`


### test-generation-pipeline
- **描述**: 自动化测试生成工作流 - 单元测试 + 集成测试 + E2E测试
- **版本**: 1.0
- **步骤数**: 7
- **路径**: `src\leo_workflows\definitions\test_generation_pipeline.yaml`


---

## 📁 快速导航

### 按分类浏览 Skills

- **automation**: 1 个技能
- **backend**: 6 个技能
- **business**: 2 个技能
- **collaboration**: 7 个技能
- **content_creation**: 4 个技能
- **core**: 10 个技能
- **debugging**: 1 个技能
- **development**: 1 个技能
- **devops**: 9 个技能
- **frontend**: 8 个技能
- **intelligence**: 1 个技能
- **prompt_engineering**: 5 个技能
- **scaffold**: 6 个技能
- **security**: 2 个技能
- **testing**: 11 个技能
- **tools**: 19 个技能
- **utilities**: 8 个技能
- **videocut_skills**: 5 个技能

---

## 📝 使用说明

### 通过意图识别调用

系统会根据用户输入自动匹配最合适的技能或代理：

```python
from leo_orchestrator.intent_recognizer import get_intent_recognizer

recognizer = get_intent_recognizer()
match = recognizer.recognize("帮我研究量子计算")

# 返回：IntentMatch(intent_type='agent', target='research_agent', confidence=0.9)
```

### 直接通过 Registry 调用

```python
from leo_orchestrator.registry import get_registry

registry = get_registry()
skill = registry.get_skill('web_search_skill')
agent = registry.get_agent('research_agent')
```

### 执行工作流

```python
from leo_orchestrator.workflow_engine import WorkflowEngine

engine = WorkflowEngine(agents)
result = engine.execute_from_yaml('src/leo_workflows/definitions/content_pipeline.yaml')
```

---

*最后更新: 2026-02-26 09:30:14*
