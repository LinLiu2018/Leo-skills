# Leo AI System - 完整组件清单

**项目路径：** `E:\桌面\leo_ai_system`
**更新时间：** 2026-03-10
**Python 版本：** 3.11.9
**状态：** ✅ 已配置完成

---

## 📊 系统概览

| 组件类型 | 数量 | 说明 |
|---------|------|------|
| **Skills (技能)** | 200+ | 按功能分类的独立技能模块 |
| **SubAgents (子代理)** | 32 | 专业化 AI 代理，可独立执行任务 |
| **Workflows (工作流)** | 10+ | 多步骤自动化流程 |
| **技能分类** | 18 | 按功能领域分组 |

---

## 🗂️ 一、Skills 技能库（按分类）

### 1. automation/ - 自动化技能
| 技能名 | 中文注释 | 用途 |
|--------|---------|------|
| `auto_logger_skill` | 自动日志技能 | 自动记录系统运行日志 |
| `email_automation_skill` | 邮件自动化技能 | 自动发送邮件、处理邮件 |
| `zapier_webhook_skill` | Zapier  webhook 技能 | 与 Zapier 集成的 webhook |
| `auto_update_skill` | 自动更新技能 | 自动更新系统/依赖 |
| `install_skill` | 安装技能 | 自动化安装流程 |

### 2. backend/ - 后端开发技能
| 技能名 | 中文注释 | 用途 |
|--------|---------|------|
| `api_doc_generator_skill` | API 文档生成器 | 自动生成 API 文档 |
| `database_migration_skill` | 数据库迁移技能 | 数据库版本迁移 |
| `database_model_generator_skill` | 数据库模型生成器 | 生成数据库模型代码 |
| `fastapi_endpoint_generator_skill` | FastAPI 端点生成器 | 生成 FastAPI 路由 |
| `flask_api_generator_skill` | Flask API 生成器 | 生成 Flask API 项目 |
| `flask_auth_generator_skill` | Flask 认证生成器 | 生成用户认证系统 |
| `oauth_login_skill` | OAuth 登录技能 | 第三方登录集成 |

### 3. business/ - 业务技能 ⭐ **房产业务核心**
| 技能名 | 中文注释 | 用途 |
|--------|---------|------|
| `ads_manager_skill` | 广告管理技能 | 管理广告投放 |
| `aliexpress_skill` | 速卖通技能 | 速卖通平台操作 |
| `amazon_skill` | 亚马逊技能 | 亚马逊平台操作 |
| `competitor_content_crawler_skill` | 竞品内容爬取技能 | 爬取竞品内容 |
| `competitor_monitor_skill` | 竞品监控技能 | 监控竞品动态 |
| `compliance_check_skill` | 合规检查技能 | 业务合规性检查 |
| `credit_check_skill` | 信用检查技能 | 客户信用评估 |
| `customer_portrait_skill` | 客户画像技能 | 生成客户画像 |
| `ebay_skill` | eBay 技能 | eBay 平台操作 |
| `facebook_ads_skill` | Facebook 广告技能 | Facebook 广告投放 |
| `financial_analysis_skill` | 财务分析技能 | 财务数据分析 |
| `fission_miniprogram` | 裂变小程序技能 | 小程序裂变营销 |
| `google_ads_skill` | Google 广告技能 | Google 广告投放 |
| `inventory_skill` | 库存管理技能 | 库存管理 |
| `leasing_management_skill` | 租赁管理技能 | 租赁业务管理 |
| `market_analysis_skill` | 市场分析技能 | 市场趋势分析 |
| `pocket_crm_skill` | 口袋 CRM 技能 | 客户关系管理 |
| `price_analysis_skill` | 价格分析技能 | 价格趋势分析 |
| `price_monitor_skill` | 价格监控技能 | 监控价格变化 |
| `property_valuation_skill` | 房产估值技能 | 房产价值评估 |
| `realestate` | 房产技能 | 房产交易管理 |
| `realestate_listing_skill` | 房产上架技能 | 房源信息发布 |
| `risk_assessment_skill` | 风险评估技能 | 业务风险评估 |
| `sales_sop_skill` | 销售 SOP 技能 | 销售流程标准化 |
| `shopify_skill` | Shopify 技能 | Shopify 店铺管理 |
| `tenant_screening_skill` | 租户筛选技能 | 租户背景调查 |
| `video_monitor_skill` | 视频监控技能 | 视频内容监控 |
| `warehouse_skill` | 仓库管理技能 | 仓库管理 |

### 4. content_creation/ - 内容创作技能 ⭐ **内容运营核心**
| 技能名 | 中文注释 | 用途 |
|--------|---------|------|
| `article_generator_skill` | 文章生成器 | 自动生成文章 |
| `blog_generator_skill` | 博客生成器 | 生成博客文章 |
| `content_generator_skill` | 内容生成器 | 通用内容生成 |
| `content_layout_leo_skill` | 内容排版技能 | 内容格式优化 |
| `copywriting_skill` | 文案写作技能 | 营销文案创作 |
| `image_generator_skill` | 图片生成器 | AI 图片生成 |
| `keyword_research_skill` | 关键词研究技能 | SEO 关键词挖掘 |
| `meta_generator_skill` | Meta 标签生成器 | 生成 SEO meta 标签 |
| `project_marketing_doc_generator_skill` | 项目营销文档生成器 | 生成营销文档 |
| `realestate_news_publisher_skill` | 房产资讯发布技能 ⭐ | 房产资讯自动发布 |
| `seo_skill` | SEO 优化技能 | 搜索引擎优化 |
| `social_auto_publish_skill` | 社交自动发布技能 | 自动发布到社交平台 |
| `social_media_skill` | 社交媒体技能 | 社交媒体管理 |
| `thumbnail_skill` | 缩略图技能 | 生成视频缩略图 |
| `video_skill` | 视频技能 | 视频处理/生成 |

### 5. core/ - 核心技能
| 技能名 | 中文注释 | 用途 |
|--------|---------|------|
| `brainstorming_skill` | 头脑风暴技能 | 创意生成 |
| `dispatching_parallel_agents_skill` | 并行代理调度技能 | 多代理并行执行 |
| `executing_plans_skill` | 计划执行技能 | 执行任务计划 |
| `finishing_development_branch_skill` | 开发分支完成技能 | Git 分支管理 |
| `receiving_code_review_skill` | 接收代码审查技能 | 代码审查接收 |
| `requesting_code_review_skill` | 请求代码审查技能 | 请求代码审查 |
| `subagent_driven_development_skill` | 子代理驱动开发技能 | 子代理协作开发 |
| `writing_plans_skill` | 计划编写技能 | 编写任务计划 |

### 6. debugging/ - 调试技能
| 技能名 | 中文注释 | 用途 |
|--------|---------|------|
| `systematic_debugging_skill` | 系统调试技能 | 系统性调试方法 |

### 7. development/ - 开发技能
| 技能名 | 中文注释 | 用途 |
|--------|---------|------|
| `skill_code_generator_skill` | 技能代码生成器 | 生成技能代码 |

### 8. devops/ - DevOps 技能
| 技能名 | 中文注释 | 用途 |
|--------|---------|------|
| `configure_verification_skill` | 配置验证技能 | 验证配置正确性 |
| `deployment_script_generator_skill` | 部署脚本生成器 | 生成部署脚本 |
| `dockerfile_generator_skill` | Dockerfile 生成器 | 生成 Docker 配置 |
| `docker_compose_generator_skill` | Docker Compose 生成器 | 生成 Docker Compose |
| `github_actions_generator_skill` | GitHub Actions 生成器 | 生成 CI/CD 流程 |
| `nginx_config_generator_skill` | Nginx 配置生成器 | 生成 Nginx 配置 |
| `using_git_worktrees_skill` | Git Worktrees 使用技能 | Git 多工作区管理 |
| `vercel_preview_skill` | Vercel 预览技能 | Vercel 部署预览 |

### 9. evolution/ - 进化技能
| 技能名 | 中文注释 | 用途 |
|--------|---------|------|
| `auto_dispatcher_skill` | 自动调度器 | 任务自动分配 |
| `fresh_start_skill` | 全新开始技能 | 重置/初始化 |
| `memory_enhanced_skill` | 记忆增强技能 | 增强记忆能力 |
| `phase_checkpoint_skill` | 阶段检查点技能 | 任务阶段检查 |
| `phase_prep_skill` | 阶段准备技能 | 任务阶段准备 |
| `phase_start_skill` | 阶段开始技能 | 启动任务阶段 |
| `planning_with_files_skill` | 文件规划技能 | 基于文件的规划 |
| `populate_state_skill` | 状态填充技能 | 填充任务状态 |
| `progress_skill` | 进度技能 | 跟踪任务进度 |
| `text_generator_skill` | 文本生成器 | 通用文本生成 |
| `using_superpowers_skill` | 超能力使用技能 | 调用特殊能力 |
| `writing_skills_skill` | 编写技能技能 | 创建新技能 |

### 10. frontend/ - 前端开发技能
| 技能名 | 中文注释 | 用途 |
|--------|---------|------|
| `css_layout_generator_skill` | CSS 布局生成器 | 生成 CSS 布局 |
| `miniprogram_component_generator_skill` | 小程序组件生成器 | 生成小程序组件 |
| `miniprogram_page_generator_skill` | 小程序页面生成器 | 生成小程序页面 |
| `react_component_generator_skill` | React 组件生成器 | 生成 React 组件 |
| `vant_weapp_skill` | Vant Weapp 技能 | Vant 小程序 UI 库 |
| `vue_component_generator_skill` | Vue 组件生成器 | 生成 Vue 组件 |
| `vue_page_generator_skill` | Vue 页面生成器 | 生成 Vue 页面 |
| `weui_miniprogram_skill` | WeUI 小程序技能 | 微信 UI 组件库 |

### 11. intelligence/ - 智能分析技能
| 技能名 | 中文注释 | 用途 |
|--------|---------|------|
| `analytics_skill` | 分析技能 | 数据分析 |
| `analyze_sessions_skill` | 会话分析技能 | 分析对话记录 |
| `bing_search_skill` | 必应搜索技能 | 必应搜索引擎 |
| `book_learning_skill` | 书籍学习技能 | 书籍内容学习 |
| `business_research_skill` | 商业研究技能 | 商业市场调研 |
| `content_analytics_skill` | 内容分析技能 | 内容数据分析 |
| `data_analyzer_skill` | 数据分析器 | 通用数据分析 |
| `excel_skill` | Excel 技能 | Excel 文件处理 |
| `file_manager_skill` | 文件管理器 | 文件操作管理 |
| `google_search_skill` | 谷歌搜索技能 | 谷歌搜索引擎 |
| `interest_calculator_skill` | 利息计算器 | 贷款利息计算 |
| `loan_calculator_skill` | 贷款计算器 | 贷款计算 |
| `mortgage_calculator_skill` | 房贷计算器 | 房贷计算 |
| `obsidian_sync_skill` | Obsidian 同步技能 | Obsidian 笔记同步 |
| `pdf_analyzer_skill` | PDF 分析器 | PDF 文档分析 |
| `pdf_generator_skill` | PDF 生成器 | 生成 PDF 文档 |
| `powerpoint_skill` | PPT 技能 | PowerPoint 制作 |
| `repayment_calculator_skill` | 还款计算器 | 还款计划计算 |
| `research_assistant_skill` | 研究助理技能 | 研究辅助 |
| `review_analyzer_skill` | 评论分析器 | 用户评论分析 |
| `roi_calculator_skill` | ROI 计算器 | 投资回报率计算 |
| `scheduler_skill` | 调度器技能 | 任务调度 |
| `sentiment_analysis_skill` | 情感分析技能 | 文本情感分析 |
| `summarize_skill` | 总结技能 | 内容摘要总结 |
| `tech_debt_check_skill` | 技术债务检查技能 | 检查技术债务 |
| `tech_extractor_skill` | 技术提取技能 | 提取技术信息 |
| `timezone_skill` | 时区技能 | 时区转换 |
| `translate_skill` | 翻译技能 | 多语言翻译 |
| `weather_skill` | 天气技能 | 天气查询 |
| `web_search_enhanced_skill` | 增强网络搜索技能 | 增强版搜索 |
| `web_search_skill` | 网络搜索技能 | 基础网络搜索 |
| `word_skill` | Word 技能 | Word 文档处理 |
| `youtube_summarizer_skill` | YouTube 总结器 | YouTube 视频总结 |

### 12. prompt_engineering/ - 提示词工程技能
| 技能名 | 中文注释 | 用途 |
|--------|---------|------|
| `chain_of_thought_prompter_skill` | 思维链提示词技能 | CoT 提示词 |
| `long_context_handler_skill` | 长上下文处理技能 | 处理长文本 |
| `prompt_chaining_orchestrator_skill` | 提示词链编排技能 | 多提示词协作 |
| `prompt_optimizer_skill` | 提示词优化技能 | 优化提示词 |
| `prompt_vault_skill` | 提示词库技能 | 提示词管理 |
| `xml_structure_builder_skill` | XML 结构构建技能 | 构建 XML 结构 |

### 13. scaffold/ - 项目脚手架技能
| 技能名 | 中文注释 | 用途 |
|--------|---------|------|
| `bootstrap_skill` | 引导技能 | 项目初始化 |
| `flask_api_scaffold_skill` | Flask API 脚手架 | Flask 项目脚手架 |
| `fullstack_project_scaffold_skill` | 全栈项目脚手架 | 全栈项目模板 |
| `miniprogram_project_scaffold_skill` | 小程序项目脚手架 | 小程序项目模板 |
| `setup_skill` | 设置技能 | 环境配置 |
| `t3_stack_scaffold_skill` | T3 Stack 脚手架 | T3 技术栈模板 |

### 14. security/ - 安全技能
| 技能名 | 中文注释 | 用途 |
|--------|---------|------|
| `security_scan_skill` | 安全扫描技能 | 安全漏洞扫描 |

### 15. testing/ - 测试技能
| 技能名 | 中文注释 | 用途 |
|--------|---------|------|
| `api_test_generator_skill` | API 测试生成器 | 生成 API 测试 |
| `auto_verify_skill` | 自动验证技能 | 自动化验证 |
| `browser_verification_skill` | 浏览器验证技能 | 浏览器测试 |
| `code_verification_skill` | 代码验证技能 | 代码验证 |
| `criteria_audit_skill` | 标准审计技能 | 标准符合性检查 |
| `e2e_test_generator_skill` | E2E 测试生成器 | 端到端测试 |
| `spec_verification_skill` | 规格验证技能 | 规格验证 |
| `test_driven_development_skill` | TDD 技能 | 测试驱动开发 |
| `unit_test_generator_skill` | 单元测试生成器 | 生成单元测试 |
| `verification_before_completion_skill` | 完成前验证技能 | 任务完成前检查 |
| `verify_task_skill` | 任务验证技能 | 任务验证 |

### 16. tools/ - 工具技能
| 技能名 | 中文注释 | 用途 |
|--------|---------|------|
| `add_todo_skill` | 添加待办技能 | 添加待办事项 |
| `agent_skill_creator_skill` | 代理技能创建器 | 创建代理技能 |
| `stock-analyzer-cskill` | 股票分析技能 | 股票数据分析 |

### 17. utilities/ - 实用工具技能
| 技能名 | 中文注释 | 用途 |
|--------|---------|------|
| `airtable_connector_skill` | Airtable 连接器 | Airtable 集成 |
| `alerting_skill` | 告警技能 | 系统告警 |
| `alipay_skill` | 支付宝技能 | 支付宝集成 |
| `api_doc_skill` | API 文档技能 | API 文档管理 |
| `article_to_prototype_skill` | 文章转原型技能 | 从文章生成原型 |
| `asana_skill` | Asana 技能 | Asana 项目管理 |
| `audit_skills_skill` | 技能审计技能 | 技能审查 |
| `aws_skill` | AWS 技能 | AWS 云服务 |
| `azure_skill` | Azure 技能 | Azure 云服务 |
| `bank_connector_skill` | 银行连接器 | 银行 API 集成 |
| `bitbucket_skill` | Bitbucket 技能 | Bitbucket 集成 |
| `browser_skill` | 浏览器技能 | 浏览器自动化 |
| `calendar_skill` | 日历技能 | 日历管理 |
| `cal_com_integration_skill` | Cal.com 集成技能 | Cal.com 日程 |
| `cal_com_skill` | Cal.com 技能 | Cal.com 调度 |
| `chart_generator_skill` | 图表生成器 | 生成数据图表 |
| `cloud_storage_skill` | 云存储技能 | 云存储服务 |
| `codex_review_skill` | Codex 审查技能 | Codex 代码审查 |
| `code_review_skill` | 代码审查技能 | 代码审查 |
| `content_to_action_skill` | 内容转行动技能 | 内容转化为行动 |
| `contract_generator_skill` | 合同生成器 | 生成合同文档 |
| `coverage_skill` | 覆盖率技能 | 代码覆盖率 |
| `crm_connector_skill` | CRM 连接器 | CRM 系统集成 |
| `customs_skill` | 海关技能 | 海关数据 |
| `deploy_skill` | 部署技能 | 应用部署 |
| `discord_skill` | Discord 技能 | Discord 集成 |
| `docker_skill` | Docker 技能 | Docker 容器 |
| `doc_generator_skill` | 文档生成器 | 生成文档 |
| `doc_sign_skill` | 文档签名技能 | 电子签名 |
| `douyin_skill` | 抖音技能 | 抖音平台集成 |
| `facebook_skill` | Facebook 技能 | Facebook 集成 |
| `find_skills_skill` | 查找技能技能 | 查找可用技能 |
| `gcp_skill` | GCP 技能 | Google 云服务 |
| `github_auto_register_skill` | GitHub 自动注册技能 | GitHub 自动注册 |
| `github_integration_skill` | GitHub 集成技能 | GitHub 集成 |
| `github_skills_monitor_skill` | GitHub 技能监控技能 | 监控 GitHub 技能 |
| `github_skills_updater_skill` | GitHub 技能更新技能 | 更新 GitHub 技能 |
| `github_skill` | GitHub 技能 | GitHub 操作 |
| `github_to_skills_skill` | GitHub 转技能技能 | 从 GitHub 导入技能 |
| `gitlab_skill` | GitLab 技能 | GitLab 集成 |
| `git_skill` | Git 技能 | Git 版本控制 |
| `gmail_skill` | Gmail 技能 | Gmail 邮件 |
| `gog_skill` | GOG 技能 | GOG 游戏平台 |
| `google_calendar_skill` | Google 日历技能 | Google 日历 |
| `google_maps_skill` | Google 地图技能 | Google 地图 |
| `hubspot_skill` | HubSpot 技能 | HubSpot CRM |
| `instagram_skill` | Instagram 技能 | Instagram 集成 |
| `jira_skill` | Jira 技能 | Jira 项目管理 |
| `knowledge_site_creator_skill` | 知识站点创建器 | 创建知识库 |
| `kubernetes_skill` | Kubernetes 技能 | K8s 容器编排 |
| `linkedin_skill` | LinkedIn 技能 | LinkedIn 集成 |
| `lint_skill` | Lint 技能 | 代码检查 |
| `list_todos_skill` | 列出待办技能 | 查看待办事项 |
| `location_skill` | 位置技能 | 地理位置服务 |
| `logging_skill` | 日志技能 | 日志记录 |
| `monitoring_skill` | 监控技能 | 系统监控 |
| `notification_skill` | 通知技能 | 系统通知 |
| `notion_connector_skill` | Notion 连接器 | Notion 集成 |
| `obsidian_connector_skill` | Obsidian 连接器 | Obsidian 集成 |
| `outlook_skill` | Outlook 技能 | Outlook 邮件 |
| `paypal_skill` | PayPal 技能 | PayPal 支付 |
| `pocket_assistant_skill` | 口袋助理技能 | 口袋助理集成 |
| `repo_watch_skill` | 仓库监控技能 | 监控代码仓库 |
| `run_todos_skill` | 运行待办技能 | 执行待办事项 |
| `salesforce_skill` | Salesforce 技能 | Salesforce CRM |
| `shipping_skill` | 物流技能 | 物流配送 |
| `skill_deduplication_skill` | 技能去重技能 | 技能去重 |
| `skill_evolution_assistant_skill` | 技能进化助手 | 技能进化辅助 |
| `skill_evolution_manager_skill` | 技能进化管理器 | 技能进化管理 |
| `skill_manager_skill` | 技能管理器 | 技能管理 |
| `skill_vetter_skill` | 技能审核技能 | 技能审核 |
| `slack_skill` | Slack 技能 | Slack 集成 |
| `sms_skill` | 短信技能 | 短信服务 |
| `social_media_monitor_skill` | 社交媒体监控技能 | 监控社交媒体 |
| `stripe_skill` | Stripe 技能 | Stripe 支付 |
| `subagent_creator_skill` | 子代理创建器 | 创建子代理 |
| `tavily_search_skill` | Tavily 搜索技能 | Tavily 搜索 API |
| `telegram_skill` | Telegram 技能 | Telegram 集成 |
| `test_generator_skill` | 测试生成器 | 生成测试用例 |
| `tracking_skill` | 追踪技能 | 数据追踪 |
| `trello_skill` | Trello 技能 | Trello 看板 |
| `twitter_monitor_skill` | Twitter 监控技能 | 监控 Twitter |
| `twitter_skill` | Twitter 技能 | Twitter 集成 |
| `update_docs_skill` | 更新文档技能 | 更新文档 |
| `update_target_projects_skill` | 更新目标项目技能 | 更新项目 |
| `usage_tracking_skill` | 使用追踪技能 | 使用量追踪 |
| `vapi_integration_skill` | VAPI 集成技能 | VAPI 语音集成 |
| `vision_audit_skill` | 视觉审计技能 | 视觉内容检查 |
| `wechat_skill` | 微信技能 | 微信集成 |
| `weibo_skill` | 微博技能 | 微博集成 |
| `whatsapp_skill` | WhatsApp 技能 | WhatsApp 集成 |
| `xiaohongshu_skill` | 小红书技能 | 小红书集成 |

### 18. videocut_skills/ - 视频剪辑技能
| 技能名 | 中文注释 | 用途 |
|--------|---------|------|
| `cut_speech_skill` | 演讲剪辑技能 | 演讲视频剪辑 |
| `subtitle_skill` | 字幕技能 | 添加字幕 |
| `video_editing_skill` | 视频剪辑技能 | 视频编辑 |

---

## 🤖 二、SubAgents 子代理（32 个）

### 房产业务代理 ⭐
| 代理名 | 中文注释 | 用途 |
|--------|---------|------|
| `realestate_agent` | 房产代理 | 房产交易咨询 |
| `villa_agent` | 别墅代理 | 别墅业务专家 |
| `commercial_agent` | 商业地产代理 | 商业地产交易 |
| `commercial_lease_agent` | 商业租赁代理 | 商铺写字楼租赁 |
| `commercial_sales_agent` | 商业销售代理 | 商业销售 |
| `investment_agent` | 投资代理 | 投资分析 |
| `leasing_agent` | 租赁代理 | 租赁管理 |
| `residential_agent` | 住宅代理 | 住宅销售 |
| `auction_agent` | 法拍代理 | 法拍房业务 |

### 营销与内容代理
| 代理名 | 中文注释 | 用途 |
|--------|---------|------|
| `marketing_agent` | 营销代理 | 营销策划 |
| `content_agent` | 内容代理 | 内容创作 |
| `creative_agent` | 创意代理 | 创意设计 |
| `distribution_agent` | 分发代理 | 内容分发 |

### 业务运营代理
| 代理名 | 中文注释 | 用途 |
|--------|---------|------|
| `sales_agent` | 销售代理 | 销售管理 |
| `operation_agent` | 运营代理 | 业务运营 |
| `product_agent` | 产品代理 | 产品管理 |
| `product_manager_agent` | 产品经理代理 | 产品规划 |
| `service_agent` | 客服代理 | 客户服务 |
| `support_agent` | 支持代理 | 技术支持 |

### 金融与电商代理
| 代理名 | 中文注释 | 用途 |
|--------|---------|------|
| `bank_product_agent` | 银行产品代理 | 银行贷款产品 |
| `loan_agent` | 贷款代理 | 贷款业务 |
| `ecommerce_agent` | 电商代理 | 电商运营 |
| `logistics_agent` | 物流代理 | 物流管理 |

### 研究与分析代理
| 代理名 | 中文注释 | 用途 |
|--------|---------|------|
| `research_agent` | 研究代理 | 市场研究 |
| `analysis_agent` | 分析代理 | 数据分析 |

### 技术与开发代理
| 代理名 | 中文注释 | 用途 |
|--------|---------|------|
| `architect_agent` | 架构师代理 | 系统架构设计 |
| `mobile_agent` | 移动端代理 | 移动开发 |

### 系统与工具代理
| 代理名 | 中文注释 | 用途 |
|--------|---------|------|
| `memory_agent` | 记忆代理 | 记忆管理 |
| `proactive_agent` | 主动代理 | 主动任务执行 |
| `self_improving_agent` | 自我进化代理 | 自我学习优化 |
| `ai_news_summary_agent` | AI 新闻摘要代理 | AI 新闻总结 |
| `x_monitor_agent` | X 监控代理 | 推特/X 监控 |

---

## ⚙️ 三、Workflows 工作流（10+ 个）

### 核心工作流
| 工作流 | 中文注释 | 用途 |
|--------|---------|------|
| `villa_consulting_workflow.py` | 别墅咨询工作流 | 别墅业务咨询流程 |
| `workflow_runner.py` | 工作流运行器 | 执行工作流 |
| `pipeline_base.py` | 流水线基类 | 工作流基础类 |

### 分析流水线
| 工作流 | 中文注释 | 用途 |
|--------|---------|------|
| `analysis_pipeline/analysis_pipeline.py` | 分析流水线 | 数据分析流程 |

### 内容流水线
| 工作流 | 中文注释 | 用途 |
|--------|---------|------|
| `content_pipeline/content_pipeline.py` | 内容流水线 | 内容生产流程 |

### 电商流水线
| 工作流 | 中文注释 | 用途 |
|--------|---------|------|
| `ecommerce_pipeline/ecommerce_pipeline.py` | 电商流水线 | 电商运营流程 |

### 知识管理流水线
| 工作流 | 中文注释 | 用途 |
|--------|---------|------|
| `practice_to_knowledge_pipeline/practice_to_knowledge_pipeline.py` | 实践到知识流水线 | 经验转化为知识 |

### 房产营销流水线 ⭐
| 工作流 | 中文注释 | 用途 |
|--------|---------|------|
| `realestate_marketing_pipeline/realestate_marketing_pipeline.py` | 房产营销流水线 | 房产营销自动化 |
| `realestate_pipeline/realestate_pipeline.py` | 房产流水线 | 房产交易流程 |

### 研究流水线
| 工作流 | 中文注释 | 用途 |
|--------|---------|------|
| `research_pipeline/research_pipeline.py` | 研究流水线 | 市场研究流程 |

### 集成模块
| 模块 | 中文注释 | 用途 |
|------|---------|------|
| `integrations/opencode_bridge.py` | OpenCode 桥接 | 与 OpenCode 集成 |

---

## 🎯 四、房产业务核心组件推荐

### 别墅业务
```
Skills:
  - business/property_valuation_skill (房产估值)
  - business/realestate (房产交易)
  - content_creation/realestate_news_publisher_skill (资讯发布)

Agents:
  - villa_agent (别墅专家)
  - realestate_agent (房产专家)

Workflows:
  - villa_consulting_workflow.py (别墅咨询)
  - realestate_marketing_pipeline (营销自动化)
```

### 商业地产业务
```
Skills:
  - business/leasing_management_skill (租赁管理)
  - business/commercial_agent (商业地产)

Agents:
  - commercial_agent (商业地产代理)
  - commercial_lease_agent (商业租赁代理)
```

### 法拍业务
```
Skills:
  - business/auction_agent (法拍)
  - business/risk_assessment_skill (风险评估)

Agents:
  - auction_agent (法拍代理)
```

### 贷款金融业务
```
Skills:
  - business/financial_analysis_skill (财务分析)
  - business/credit_check_skill (信用检查)
  - intelligence/loan_calculator_skill (贷款计算)

Agents:
  - loan_agent (贷款代理)
  - bank_product_agent (银行产品代理)
```

### 内容运营
```
Skills:
  - content_creation/realestate_news_publisher_skill (资讯发布)
  - content_creation/copywriting_skill (文案写作)
  - content_creation/social_auto_publish_skill (自动发布)

Agents:
  - content_agent (内容代理)
  - marketing_agent (营销代理)
```

---

## 📞 使用指南

### 调用技能
```python
from leo_skills.business import realestate_listing_skill
from leo_skills.content_creation import realestate_news_publisher_skill
```

### 调用子代理
```python
from leo_subagents import villa_agent, realestate_agent

# 执行任务
result = await villa_agent.execute("分析宁波别墅市场")
```

### 调用工作流
```python
from leo_workflows import villa_consulting_workflow

# 执行工作流
result = await villa_consulting_workflow.run(params)
```

---

## 📊 统计汇总

| 类别 | 数量 |
|------|------|
| **技能分类** | 18 个 |
| **Skills** | 200+ 个 |
| **SubAgents** | 32 个 |
| **Workflows** | 10+ 个 |
| **房产业务相关** | 30+ 个 |
| **内容运营相关** | 20+ 个 |
| **电商相关** | 15+ 个 |

---

**文档生成时间：** 2026-03-10
**项目位置：** `E:\桌面\leo_ai_system`
**状态：** ✅ 全部可用
