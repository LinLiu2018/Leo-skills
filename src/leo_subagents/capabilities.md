# Agent Capabilities Registry - Leo AI System 能力注册中心

> 本文件由 Agent 自动生成，用于注册 Leo AI System 的所有能力
> 
> **上次更新:** 2026-02-01
> **状态:** 完整注册完成 ✅ (已规范化文件架构)

---

## 📋 能力总览

| 类别 | 数量 | 可调用状态 |
|------|------|-----------|
| **Subagents (代理)** | 9个 | ✅ 已注册 |
| **Workflows (工作流)** | 5个 | ✅ 已注册 |
| **Skills (技能)** | **103个** | ✅ 完整注册 (100% 符合标准) |

---

## 🤖 Subagents (代理层)

### 9大代理清单

| 代理名称 | 文件路径 | 激活关键词 | 核心能力 |
|----------|----------|-----------|----------|
| **research_agent** | `src/leo_subagents/agents/research_agent/` | 研究、调研、分析、报告、收集、查找、搜索 | 信息收集、文献调研、知识整理、研究报告生成 |
| **analysis_agent** | `src/leo_subagents/agents/analysis_agent/` | 分析、数据、统计、洞察 | 数据分析、趋势洞察、决策支持 |
| **architect_agent** | `src/leo_subagents/agents/architect_agent/` | 架构、技术、设计、系统 | 技术架构决策、系统设计、技术选型 |
| **creative_agent** | `src/leo_subagents/agents/creative_agent/` | 创意、内容、写作、设计 | 内容创作、创意生成、文案撰写 |
| **product_manager_agent** | `src/leo_subagents/agents/product_manager_agent/` | 产品、需求、功能、规划 | 需求定义、产品规划、功能设计 |
| **realestate_agent** | `src/leo_subagents/agents/realestate_agent/` | 房产、地产、房源、客户 | 房产业务自动化、客户跟进、房源管理 |
| **mobile_agent** | `src/leo_subagents/agents/mobile_agent/` | 移动端、小程序、APP、手机 | 移动端开发、小程序开发 |
| **ecommerce_agent** | `src/leo_subagents/agents/ecommerce_agent/` | 电商、商城、订单、运营 | 电商运营自动化、订单处理 |
| **ai_news_summary_agent** | `src/leo_subagents/agents/ai_news_summary_agent/` | AI新闻、摘要、每日快报 | AI新闻收集与摘要生成 |

---

## 🌊 Workflows (工作流层)

### 5大工作流清单

| 工作流名称 | 文件路径 | 输入参数 | 用途 |
|------------|----------|---------|------|
| **research_pipeline** | `src/leo_workflows/workflows/research_pipeline/` | `topic`, `depth`, `format` | 自动化研究调研流程 |
| **content_pipeline** | `src/leo_workflows/workflows/content_pipeline/` | `content_type`, `topic` | 内容生产自动化 |
| **analysis_pipeline** | `src/leo_workflows/workflows/analysis_pipeline/` | `data`, `analysis_type` | 数据分析自动化 |
| **realestate_pipeline** | `src/leo_workflows/workflows/realestate_pipeline/` | `task_type`, `params` | 房产业务自动化 |
| **ecommerce_pipeline** | `src/leo_workflows/workflows/ecommerce_pipeline/` | `operation`, `params` | 电商运营自动化 |

---

## 🧩 Skills (技能层) - 完整列表 (104个)

### 1. Backend (后端开发) - 6个
| 技能名称 | 路径 |
|----------|------|
| api_doc_generator_skill | `src/leo_skills/backend/api_doc_generator_skill/` |
| database_migration_skill | `src/leo_skills/backend/database_migration_skill/` |
| database_model_generator_skill | `src/leo_skills/backend/database_model_generator_skill/` |
| fastapi_endpoint_generator_skill | `src/leo_skills/backend/fastapi_endpoint_generator_skill/` |
| flask_api_generator_skill | `src/leo_skills/backend/flask_api_generator_skill/` |
| flask_auth_generator_skill | `src/leo_skills/backend/flask_auth_generator_skill/` |

### 2. Business (业务) - 3个
| 技能名称 | 路径 |
|----------|------|
| ecommerce | `src/leo_skills/business/ecommerce/` |
| fission_miniprogram | `src/leo_skills/business/fission_miniprogram/` |
| realestate | `src/leo_skills/business/realestate/` |

### 3. Collaboration (协作) - 7个
| 技能名称 | 路径 |
|----------|------|
| brainstorming_skill | `src/leo_skills/collaboration/brainstorming_skill/` |
| dispatching_parallel_agents_skill | `src/leo_skills/collaboration/dispatching_parallel_agents_skill/` |
| executing_plans_skill | `src/leo_skills/collaboration/executing_plans_skill/` |
| receiving_code_review_skill | `src/leo_skills/collaboration/receiving_code_review_skill/` |
| requesting_code_review_skill | `src/leo_skills/collaboration/requesting_code_review_skill/` |
| subagent_driven_development_skill | `src/leo_skills/collaboration/subagent_driven_development_skill/` |
| writing_plans_skill | `src/leo_skills/collaboration/writing_plans_skill/` |

### 4. Content Creation (内容创作) - 4个
| 技能名称 | 路径 |
|----------|------|
| content_layout_leo_skill | `src/leo_skills/content_creation/content_layout_leo_skill/` |
| image_generator_skill | `src/leo_skills/content_creation/image_generator_skill/` |
| project_marketing_doc_generator_skill | `src/leo_skills/content_creation/project_marketing_doc_generator_skill/` |
| realestate_news_publisher_skill | `src/leo_skills/content_creation/realestate_news_publisher_skill/` |

### 5. Core (核心) - 8个
| 技能名称 | 路径 |
|----------|------|
| evolution | `src/leo_skills/core/evolution/` |
| fresh_start_skill | `src/leo_skills/core/fresh_start_skill/` |
| phase_checkpoint_skill | `src/leo_skills/core/phase_checkpoint_skill/` |
| phase_prep_skill | `src/leo_skills/core/phase_prep_skill/` |
| phase_start_skill | `src/leo_skills/core/phase_start_skill/` |
| planning_with_files_skill | `src/leo_skills/core/planning_with_files_skill/` |
| populate_state_skill | `src/leo_skills/core/populate_state_skill/` |
| progress_skill | `src/leo_skills/core/progress_skill/` |
| text_generator_skill | `src/leo_skills/core/text_generator_skill/` |

### 6. Debugging (调试) - 1个
| 技能名称 | 路径 |
|----------|------|
| systematic_debugging_skill | `src/leo_skills/debugging/systematic_debugging_skill/` |

### 7. Development (开发) - 1个
| 技能名称 | 路径 |
|----------|------|
| skill_code_generator_skill | `src/leo_skills/development/skill_code_generator_skill/` |

### 8. DevOps (运维) - 8个
| 技能名称 | 路径 |
|----------|------|
| configure_verification_skill | `src/leo_skills/devops/configure_verification_skill/` |
| deployment_script_generator_skill | `src/leo_skills/devops/deployment_script_generator_skill/` |
| dockerfile_generator_skill | `src/leo_skills/devops/dockerfile_generator_skill/` |
| docker_compose_generator_skill | `src/leo_skills/devops/docker_compose_generator_skill/` |
| finishing_development_branch_skill | `src/leo_skills/devops/finishing_development_branch_skill/` |
| github_actions_generator_skill | `src/leo_skills/devops/github_actions_generator_skill/` |
| nginx_config_generator_skill | `src/leo_skills/devops/nginx_config_generator_skill/` |
| using_git_worktrees_skill | `src/leo_skills/devops/using_git_worktrees_skill/` |
| vercel_preview_skill | `src/leo_skills/devops/vercel_preview_skill/` |

### 9. Frontend (前端) - 8个
| 技能名称 | 路径 |
|----------|------|
| css_layout_generator_skill | `src/leo_skills/frontend/css_layout_generator_skill/` |
| miniprogram_component_generator_skill | `src/leo_skills/frontend/miniprogram_component_generator_skill/` |
| miniprogram_page_generator_skill | `src/leo_skills/frontend/miniprogram_page_generator_skill/` |
| react_component_generator_skill | `src/leo_skills/frontend/react_component_generator_skill/` |
| vant_weapp_skill | `src/leo_skills/frontend/vant_weapp_skill/` |
| vue_component_generator_skill | `src/leo_skills/frontend/vue_component_generator_skill/` |
| vue_page_generator_skill | `src/leo_skills/frontend/vue_page_generator_skill/` |
| weui_miniprogram_skill | `src/leo_skills/frontend/weui_miniprogram_skill/` |

### 10. Intelligence (情报) - 1个
| 技能名称 | 路径 |
|----------|------|
| twitter_monitor_skill | `src/leo_skills/intelligence/twitter_monitor_skill/` |

### 11. Prompt Engineering (提示工程) - 6个
| 技能名称 | 路径 |
|----------|------|
| chain_of_thought_prompter | `src/leo_skills/prompt_engineering/chain_of_thought_prompter/` |
| claude_prompt_engineering_skills | `src/leo_skills/prompt_engineering/claude_prompt_engineering_skills/` |
| long_context_handler | `src/leo_skills/prompt_engineering/long_context_handler/` |
| prompt_chaining_orchestrator | `src/leo_skills/prompt_engineering/prompt_chaining_orchestrator/` |
| prompt_optimizer | `src/leo_skills/prompt_engineering/prompt_optimizer/` |
| xml_structure_builder | `src/leo_skills/prompt_engineering/xml_structure_builder/` |

### 12. Scaffold (脚手架) - 6个
| 技能名称 | 路径 |
|----------|------|
| bootstrap_skill | `src/leo_skills/scaffold/bootstrap_skill/` |
| flask_api_scaffold_skill | `src/leo_skills/scaffold/flask_api_scaffold_skill/` |
| fullstack_project_scaffold_skill | `src/leo_skills/scaffold/fullstack_project_scaffold_skill/` |
| miniprogram_project_scaffold_skill | `src/leo_skills/scaffold/miniprogram_project_scaffold_skill/` |
| setup_skill | `src/leo_skills/scaffold/setup_skill/` |
| t3_stack_scaffold_skill | `src/leo_skills/scaffold/t3_stack_scaffold_skill/` |

### 13. Security (安全) - 2个
| 技能名称 | 路径 |
|----------|------|
| oauth_login_skill | `src/leo_skills/security/oauth_login_skill/` |
| security_scan_skill | `src/leo_skills/security/security_scan_skill/` |

### 14. Testing (测试) - 10个
| 技能名称 | 路径 |
|----------|------|
| api_test_generator_skill | `src/leo_skills/testing/api_test_generator_skill/` |
| auto_verify_skill | `src/leo_skills/testing/auto_verify_skill/` |
| browser_verification_skill | `src/leo_skills/testing/browser_verification_skill/` |
| code_verification_skill | `src/leo_skills/testing/code_verification_skill/` |
| criteria_audit_skill | `src/leo_skills/testing/criteria_audit_skill/` |
| e2e_test_generator_skill | `src/leo_skills/testing/e2e_test_generator_skill/` |
| spec_verification_skill | `src/leo_skills/testing/spec_verification_skill/` |
| test_driven_development_skill | `src/leo_skills/testing/test_driven_development_skill/` |
| unit_test_generator_skill | `src/leo_skills/testing/unit_test_generator_skill/` |
| verification_before_completion_skill | `src/leo_skills/testing/verification_before_completion_skill/` |
| verify_task_skill | `src/leo_skills/testing/verify_task_skill/` |

### 15. Tools (工具) - 15个
| 技能名称 | 路径 |
|----------|------|
| add_todo_skill | `src/leo_skills/tools/add_todo_skill/` |
| agent_skill_creator_skill | `src/leo_skills/tools/agent_skill_creator_skill/` |
| article_to_prototype_skill | `src/leo_skills/tools/article_to_prototype_skill/` |
| audit_skills_skill | `src/leo_skills/tools/audit_skills_skill/` |
| codex_review_skill | `src/leo_skills/tools/codex_review_skill/` |
| github_to_skills_skill | `src/leo_skills/tools/github_to_skills_skill/` |
| list_todos_skill | `src/leo_skills/tools/list_todos_skill/` |
| run_todos_skill | `src/leo_skills/tools/run_todos_skill/` |
| skill_evolution_assistant_skill | `src/leo_skills/tools/skill_evolution_assistant_skill/` |
| skill_evolution_manager_skill | `src/leo_skills/tools/skill_evolution_manager_skill/` |
| skill_manager_skill | `src/leo_skills/tools/skill_manager_skill/` |
| subagent_creator_skill | `src/leo_skills/tools/subagent_creator_skill/` |
| update_docs_skill | `src/leo_skills/tools/update_docs_skill/` |
| update_target_projects_skill | `src/leo_skills/tools/update_target_projects_skill/` |
| chart_generator_skill | `src/leo_skills/tools/chart_generator_skill/` | 图表生成、商业可视化 |
| vision_audit_skill | `src/leo_skills/tools/vision_audit_skill/` |

### 16. Utilities (实用工具) - 8个
| 技能名称 | 路径 |
|----------|------|
| analyze_sessions_skill | `src/leo_skills/utilities/analyze_sessions_skill/` |
| business_research_skill | `src/leo_skills/utilities/business_research_skill/` |
| data_analyzer_skill | `src/leo_skills/utilities/data_analyzer_skill/` |
| obsidian_sync_skill | `src/leo_skills/utilities/obsidian_sync_skill/` |
| research_assistant_skill | `src/leo_skills/utilities/research_assistant_skill/` |
| tech_debt_check_skill | `src/leo_skills/utilities/tech_debt_check_skill/` |
| tech_extractor_skill | `src/leo_skills/utilities/tech_extractor_skill/` |
| web_search_skill | `src/leo_skills/utilities/web_search_skill/` |

### 17. Video Editing (视频剪辑) - 5个
| 技能名称 | 路径 |
|----------|------|
| cut_speech_skill | `src/leo_skills/videocut_skills/cut_speech_skill/` |
| video_editing_skill | `src/leo_skills/videocut_skills/video_editing_skill/` |
| subtitle_skill | `src/leo_skills/videocut_skills/subtitle_skill/` |
| install_skill | `src/leo_skills/videocut_skills/install_skill/` |
| auto_update_skill | `src/leo_skills/videocut_skills/auto_update_skill/` |

---

## 📊 完整统计

| 类别 | 数量 | 文件完整度 |
|------|------|-----------|
| **Subagents** | 9 | 100% (AGENT.md + agent.py + __init__.py + evolution.json) |
| **Workflows** | 5 | 100% (workflow.yaml + pipeline.py + __init__.py + README.md) |
| **Skills** | **103** | 100% (SKILL.md + __init__.py + evolution.json + config.yaml) |
| **总计** | **117** | - |

---

## 🔄 能力更新日志

### 2026-02-01
- ✅ 完成所有 103 个 Skills 文件架构规范化 (SKILL.md + __init__.py + skill.py + evolution.json + config.yaml)
- ✅ 完成所有 9 个 Agents 文件架构规范化 (AGENT.md + agent.py + __init__.py + evolution.json)
- ✅ 更新 videocut_skills 目录命名 (中文 → snake_case)
- ✅ 创建验证脚本 (validate_skills.py, validate_agents.py, validate_workflows.py)
- ✅ 创建模板生成器 (create_skill.py, create_agent.py, create_workflow.py)

### 2026-01-31
- ✅ 完成所有 Subagents 注册 (9个)
- ✅ 完成所有 Workflows 注册 (5个)
- ✅ 完成 Skills **完整注册 (104个)**
- ✅ 创建快速调用指南

---

**下次检查:** 2026-02-07
