# Leo AI System - 完整能力清单

> **生成时间**: 2026-03-04
> **版本**: v3.0
> **技能注册表**: [.claude/skill_registry.json](.claude/skill_registry.json)

---

## 📊 能力概览

| 类别 | 数量 | 说明 |
|------|------|------|
| **技能 (Skills)** | 249 | 18个分类，覆盖房产、电商、内容、开发等 |
| **代理 (Agents)** | 37 | 4个Claude Code代理 + 33个Leo业务代理 |
| **插件 (Plugins)** | 1 | Leo Core 核心插件 |
| **MCP 工具** | 7 | Leo System MCP 服务器工具 |
| **Hooks** | 3 | SessionStart, ToolStart, ToolEnd |
| **工作流** | 14 | Superpowers 协作工作流 |
| **脚本工具** | 99 | 维护、业务、开发、测试等脚本 |

---

## 🏗️ 1. 核心架构模块

### 1.1 Leo Gateway (网关层)
**路径**: [src/leo_gateway/](src/leo_gateway/)

| 组件 | 功能 |
|------|------|
| **gateway.py** | 核心网关服务 |
| **mcp_server.py** | MCP 服务器实现 |
| **router.py** | 请求路由 |
| **protocol.py** | 协议定义 |
| **session.py** | 会话管理 |
| **task_queue.py** | 任务队列 |
| **channel/** | 多渠道适配器 |

### 1.2 Leo Orchestrator (编排层)
**路径**: [src/leo_orchestrator/](src/leo_orchestrator/)

| 组件 | 功能 |
|------|------|
| **workflow_engine.py** | 工作流引擎 |
| **intent_recognizer.py** | 意图识别 |
| **registry.py** | 技能注册表 |
| **wingman_pipeline.py** | Wingman 管道 |
| **api.py** | API 接口 |

### 1.3 Leo Memory (记忆层)
**路径**: [src/leo_memory/](src/leo_memory/)

- 向量记忆存储
- 会话上下文管理
- 用户画像管理

### 1.4 Leo Config (配置层)
**路径**: [src/leo_config/](src/leo_config/)

| 组件 | 功能 |
|------|------|
| **config_manager.py** | 配置管理器 |
| **settings.yaml** | 系统配置 |

### 1.5 Leo Interface (接口层)
**路径**: [src/leo_interface/](src/leo_interface/)

| 组件 | 功能 |
|------|------|
| **openclaw_bridge.py** | OpenClaw 桥接 |

### 1.6 Leo Workflows (工作流层)
**路径**: [src/leo_workflows/](src/leo_workflows/)

| 组件 | 功能 |
|------|------|
| **workflow_runner.py** | 工作流运行器 |
| **pipeline_base.py** | 管道基类 |
| **villa_consulting_workflow.py** | 别墅咨询工作流 |

---

## 🎯 2. 技能系统 (249个技能)

### 1.1 房产业务 (Business - 26个)

#### 核心房产技能
- **property_valuation_skill** - 房产估值
- **realestate_listing_skill** - 房源管理
- **tenant_screening_skill** - 租户筛选
- **leasing_management_skill** - 招商管理
- **sales-sop** - 房地产销售SOP数字化

#### 金融计算
- **mortgage_calculator_skill** - 房贷计算
- **loan_calculator_skill** - 贷款计算
- **interest_calculator_skill** - 利息计算
- **repayment_calculator_skill** - 还款计算
- **roi_calculator_skill** - 投资回报计算
- **credit_check_skill** - 信用查询

#### 客户管理
- **pocket-crm** - 口袋助理CRM集成
- **customer-portrait** - 客户画像AI分析
- **competitor_monitor_skill** - 竞品监控
- **competitor-content-crawler** - 竞品内容采集

#### 市场分析
- **market_analysis_skill** - 市场分析
- **price_analysis_skill** - 价格分析
- **price_monitor_skill** - 价格监控
- **financial_analysis_skill** - 财务分析
- **risk_assessment_skill** - 风险评估

#### 电商运营
- **amazon_skill** - 亚马逊运营
- **shopify_skill** - Shopify 独立站
- **aliexpress_skill** - 速卖通运营
- **ebay_skill** - eBay 运营

#### 广告投放
- **ads_manager_skill** - 广告投放管理
- **facebook_ads_skill** - Facebook 广告
- **google_ads_skill** - Google 广告

#### 其他业务
- **compliance_check_skill** - 合规检查
- **inventory_skill** - 库存管理
- **warehouse_skill** - 仓库管理
- **video_monitor_skill** - 视频号账号监控

---

### 2.2 内容创作 (Content Creation - 15个)

- **article_generator_skill** - 文章生成
- **blog_generator_skill** - 博客生成
- **content_generator_skill** - 内容自动生成
- **copywriting_skill** - 文案生成
- **image_generator_skill** - 图片生成
- **video_skill** - 视频处理
- **thumbnail_skill** - 缩略图生成
- **keyword_research_skill** - 关键词研究
- **seo_skill** - SEO 优化
- **meta_generator_skill** - Meta 标签生成
- **social-auto-publish** - 多平台内容自动发布
- **social_media_skill** - 社交媒体管理
- **content_layout_leo_skill** - 多平台内容排版
- **project_marketing_doc_generator_skill** - 项目营销文档生成
- **realestate_news_publisher_skill** - 房产新闻发布

---

### 2.3 开发工具 (Development - 96个)

#### 后端开发 (Backend - 6个)
- **api_doc_generator_skill** - API 文档生成
- **fastapi_endpoint_generator_skill** - FastAPI 端点生成
- **flask_api_generator_skill** - Flask API 生成
- **flask_auth_generator_skill** - Flask 认证生成
- **database_model_generator_skill** - 数据库模型生成
- **database_migration_skill** - 数据库迁移脚本

#### 前端开发 (Frontend - 8个)
- **react_component_generator_skill** - React 组件生成
- **vue_component_generator_skill** - Vue3 组件生成
- **vue_page_generator_skill** - Vue3 页面生成
- **css_layout_generator_skill** - CSS 布局生成
- **miniprogram_component_generator_skill** - 小程序组件生成
- **miniprogram_page_generator_skill** - 小程序页面生成
- **vant_weapp_skill** - Vant Weapp UI 组件
- **weui_miniprogram_skill** - WeUI 小程序组件

#### 项目脚手架 (Scaffold - 6个)
- **fullstack_project_scaffold_skill** - 全栈项目脚手架
- **t3_stack_scaffold_skill** - T3 Stack 脚手架
- **flask_api_scaffold_skill** - Flask API 脚手架
- **miniprogram_project_scaffold_skill** - 小程序项目脚手架
- **bootstrap** - 功能计划生成
- **setup** - AI Coding Toolkit 初始化

#### DevOps (9个)
- **dockerfile_generator_skill** - Dockerfile 生成
- **docker_compose_generator_skill** - Docker Compose 生成
- **github_actions_generator_skill** - GitHub Actions 生成
- **nginx_config_generator_skill** - Nginx 配置生成
- **deployment_script_generator_skill** - 部署脚本生成
- **configure-verification** - 验证命令配置
- **using_git_worktrees_skill** - Git Worktree 工作流
- **finishing_development_branch_skill** - 完成开发分支
- **vercel-preview** - Vercel 预览部署

#### 测试 (Testing - 11个)
- **unit_test_generator_skill** - 单元测试生成
- **e2e_test_generator_skill** - E2E 测试生成
- **api_test_generator_skill** - API 测试生成
- **test_driven_development_skill** - TDD 实践
- **verification_before_completion_skill** - 完成前验证
- **code-verification** - 代码验证工作流
- **browser-verification** - 浏览器验证
- **auto-verify** - 自动验证
- **verify-task** - 任务验证
- **criteria-audit** - 验证标准审计
- **spec-verification** - 规格验证

#### 代码质量 (56个工具类技能)
- **code_review_skill** - 代码审查
- **lint_skill** - 代码检查
- **coverage_skill** - 测试覆盖率
- **security_scan_skill** - 安全扫描
- **skill_vetter_skill** - 技能安全扫描
- **tech-debt-check** - 技术债务检测
- **systematic_debugging_skill** - 系统化调试
- **git_skill** - Git 版本控制
- **github_integration_skill** - GitHub 集成
- **gitlab_skill** - GitLab 集成
- **bitbucket_skill** - Bitbucket 集成
- **docker_skill** - Docker 容器
- **kubernetes_skill** - K8s 编排
- **monitoring_skill** - 系统监控
- **logging_skill** - 日志管理
- **alerting_skill** - 告警管理
- **deploy_skill** - 自动部署

---

### 2.4 协作工作流 (Collaboration - 8个)

基于 **Superpowers v4.3.1** 的协作技能：

- **brainstorming_skill** - 头脑风暴（创造性工作前必用）
- **writing_plans_skill** - 编写详细实施计划
- **executing_plans_skill** - 执行实施计划
- **subagent_driven_development_skill** - 子代理驱动开发
- **dispatching_parallel_agents_skill** - 分发并行代理
- **requesting_code_review_skill** - 请求代码审查
- **receiving_code_review_skill** - 接收代码审查反馈
- **finishing_development_branch_skill** - 完成开发分支

---

### 2.5 核心系统 (Core - 11个)

- **planning_with_files_skill** - 持久化规划（Manus风格）
- **memory_enhanced_skill** - 增强记忆
- **using_superpowers_skill** - Superpowers 入口
- **writing_skills_skill** - 技能编写
- **fresh-start** - 项目上下文加载
- **phase-prep** - 阶段准备
- **phase-start** - 阶段执行
- **phase-checkpoint** - 阶段检查点
- **populate-state** - 状态恢复
- **progress** - 进度查看
- **text_generator_skill** - 文本生成引擎

---

### 2.6 提示词工程 (Prompt Engineering - 6个)

- **prompt_optimizer_skill** - 提示词优化
- **prompt_vault_skill** - 提示词库管理
- **chain_of_thought_prompter_skill** - 思维链提示
- **prompt_chaining_orchestrator_skill** - 提示词链编排
- **long_context_handler_skill** - 长上下文处理
- **xml_structure_builder_skill** - XML 结构化提示

---

### 2.7 自动化 (Automation - 3个)

- **auto_logger_skill** - 自动日志
- **email_automation_skill** - 邮件自动化
- **zapier_webhook_skill** - Zapier Webhook 集成

---

### 2.8 实用工具 (Utilities - 34个)

#### 数据分析
- **analytics_skill** - 数据分析
- **data_analyzer_skill** - 数据分析器
- **content_analytics_skill** - 内容效果分析
- **sentiment_analysis_skill** - 情感分析
- **review_analyzer_skill** - 评论分析

#### 文档处理
- **pdf_analyzer_skill** - PDF 分析
- **pdf_generator_skill** - PDF 生成
- **excel_skill** - Excel 处理
- **word_skill** - Word 处理
- **powerpoint_skill** - PPT 生成
- **doc_generator_skill** - 文档生成

#### 搜索工具
- **google_search_skill** - Google 搜索
- **bing_search_skill** - Bing 搜索
- **tavily_search_skill** - Tavily API 搜索
- **web_search_enhanced_skill** - 增强版网络搜索
- **web_search_skill** - 网络搜索 v2.0

#### 内容总结
- **summarize_skill** - 内容总结
- **youtube_summarizer_skill** - YouTube 视频总结
- **book_learning_skill** - 书籍知识提取
- **content_to_action_skill** - 内容转化为行动计划

#### 其他工具
- **translate_skill** - 多语言翻译
- **timezone_skill** - 时区转换
- **weather_skill_skill** - 天气查询
- **location_skill** - 位置服务
- **file_manager_skill** - 文件管理
- **scheduler_skill** - 任务调度
- **notification_skill** - 通知推送
- **usage_tracking_skill** - 使用追踪
- **obsidian_sync_skill** - Obsidian 同步
- **research_assistant_skill** - 研究助手
- **business_research_skill** - 商业项目调研
- **tech_extractor_skill** - 技术关键词提取
- **chart_generator_skill** - 图表生成

---

### 2.9 集成连接器 (Tools - 96个)

#### 项目管理
- **jira_skill** - Jira
- **asana_skill** - Asana
- **trello_skill** - Trello

#### CRM系统
- **salesforce_skill** - Salesforce
- **hubspot_skill** - HubSpot
- **pocket_assistant_skill** - 口袋助理
- **crm_connector_skill** - CRM 连接器

#### 通讯工具
- **slack_skill_skill** - Slack
- **discord_skill_skill** - Discord
- **telegram_skill_skill** - Telegram
- **whatsapp_skill_skill** - WhatsApp
- **wechat_skill** - 微信
- **sms_skill** - 短信

#### 邮件服务
- **gmail_skill** - Gmail
- **outlook_skill** - Outlook

#### 日历服务
- **calendar_skill_skill** - 日历管理
- **google_calendar_skill** - Google 日历
- **cal_com_skill** - Cal.com 预约
- **cal_com_integration_skill** - Cal.com 集成

#### 社交媒体
- **douyin_skill** - 抖音
- **xiaohongshu_skill** - 小红书
- **twitter_skill** - Twitter
- **twitter_monitor_skill** - Twitter 监控
- **facebook_skill** - Facebook
- **instagram_skill** - Instagram
- **weibo_skill** - 微博
- **linkedin_skill** - LinkedIn
- **social_media_monitor_skill** - 多平台监控

#### 云服务
- **aws_skill** - AWS
- **azure_skill** - Azure
- **gcp_skill** - GCP
- **cloud_storage_skill** - 云存储

#### 数据库/知识库
- **airtable_connector_skill** - Airtable
- **notion_connector_skill** - Notion
- **obsidian_connector_skill** - Obsidian

#### 支付服务
- **alipay_skill** - 支付宝
- **stripe_skill** - Stripe
- **paypal_skill** - PayPal

#### Google Workspace
- **gog_skill** - Google Workspace 全家桶
- **google_maps_skill** - Google 地图

#### 其他集成
- **browser_skill** - 浏览器控制
- **vapi_integration_skill** - Vapi 语音 AI
- **bank_connector_skill** - 银行接口
- **doc_sign_skill** - 电子签名
- **shipping_skill** - 物流管理
- **tracking_skill** - 物流追踪
- **customs_skill** - 海关申报

#### GitHub 生态
- **github_skill_skill** - GitHub 集成
- **github_auto_register_skill** - GitHub 技能自动注册
- **github_to_skills_skill** - GitHub 仓库转技能
- **github_skills_monitor_skill** - GitHub 技能监控
- **github_skills_updater_skill** - GitHub 技能更新
- **repo_watch_skill** - 仓库监控

#### 技能管理
- **skill_code_generator_skill** - 技能代码生成
- **skill_manager_skill** - 技能生命周期管理
- **skill_evolution_manager_skill** - 技能进化管理
- **skill_evolution_assistant_skill** - 技能进化助手
- **skill_deduplication_skill** - 技能去重检查
- **find_skills_skill** - 技能发现
- **agent_skill_creator_skill** - Agent 技能创建器
- **subagent_creator_skill** - Subagent 创建器
- **auto_update_skill** - 自动更新

#### 文档工具
- **add-todo** - 添加 TODO
- **list-todos** - 列出 TODO
- **run-todos** - 执行 TODO
- **update-docs** - 更新文档
- **update-target-projects** - 更新目标项目
- **analyze-sessions** - 会话分析
- **audit-skills** - 技能审计
- **codex-review** - Codex 代码审查
- **vision-audit** - 愿景审计
- **oauth-login** - OAuth 登录
- **knowledge_site_creator_skill** - 知识网站创建
- **article_to_prototype_skill** - 文章转原型
- **contract_generator_skill** - 合同生成

---

### 2.10 视频剪辑 (VideoCut - 5个)

- **videocut:install** - 环境准备
- **videocut:cut_speech** - 口播视频转录和口误识别
- **videocut:subtitle** - 字幕生成与烧录
- **videocut:video_editing** - 执行视频剪辑
- **videocut:auto_update** - 自更新规则

---

### 2.11 智能监控 (Intelligence - 1个)

- **twitter_monitor_skill** - Twitter AI 科技博主监控

---

### 2.12 调试 (Debugging - 1个)

- **systematic_debugging_skill** - 系统化四阶段根因分析

---

### 2.13 安全 (Security - 2个)

- **oauth-login** - OAuth 登录流程
- **security_scan_skill** - 代码安全扫描

---

## 🤖 3. 代理系统 (37个代理)

### 3.1 Claude Code 子代理 (4个)

#### 3.1.1 代码审查专家 (code-reviewer)
- **模型**: Sonnet
- **工具**: Read, Grep, Glob, Bash
- **职责**: 代码质量、安全性、性能、最佳实践审查
- **触发**: 代码变更后自动触发
- **配置**: [.claude/agents/code-reviewer.md](.claude/agents/code-reviewer.md)

#### 3.1.2 研究探索专家 (researcher)
- **代理类型**: Explore
- **工具**: 所有工具
- **职责**: 深入分析代码库，理解架构和依赖关系
- **输出**: 研究报告、架构图、文件索引
- **配置**: [.claude/agents/researcher.md](.claude/agents/researcher.md)

#### 3.1.3 文档生成专家 (documenter)
- **工具**: Read, Glob, Grep, Write, Edit
- **职责**: 自动生成或更新项目文档
- **配置**: [.claude/agents/documenter.md](.claude/agents/documenter.md)

#### 3.1.4 项目重构专家 (project-refactor-agent)
- **工具**: Read, Glob, Grep, Bash, Edit, Write
- **职责**: 分析和重构项目目录结构
- **功能**:
  - 分析项目结构
  - 生成重构方案
  - 执行重构（分阶段）
  - 验证重构结果
- **配置**: [.claude/agents/project-refactor-agent.md](.claude/agents/project-refactor-agent.md)

---

### 3.2 Leo 业务代理 (33个)

**配置文件**: [src/leo_subagents/config/agents.yaml](src/leo_subagents/config/agents.yaml)
**代理目录**: [src/leo_subagents/agents/](src/leo_subagents/agents/)

#### 房产业务代理 (6个)

| 代理 | 描述 | 优先级 |
|------|------|--------|
| **realestate_agent** | 房地产市场分析、项目营销、政策追踪 | 5 |
| **villa_agent** | 别墅项目专家 | - |
| **residential_agent** | 住宅项目专家 | - |
| **commercial_agent** | 商业地产专家 | - |
| **commercial_sales_agent** | 商业销售专家 | - |
| **auction_agent** | 法拍房专家 | - |

#### 租赁业务代理 (2个)

| 代理 | 描述 | 优先级 |
|------|------|--------|
| **leasing_agent** | 租赁管理专家 | - |
| **commercial_lease_agent** | 商业租赁专家 | - |

#### 金融业务代理 (3个)

| 代理 | 描述 | 优先级 |
|------|------|--------|
| **loan_agent** | 贷款产品专家 | - |
| **bank_product_agent** | 银行产品专家 | - |
| **investment_agent** | 投资分析专家 | - |

#### 电商业务代理 (4个)

| 代理 | 描述 | 优先级 |
|------|------|--------|
| **ecommerce_agent** | AI眼镜电商、竞品分析和爆款文案 | 6 |
| **product_agent** | 产品管理专家 | - |
| **operation_agent** | 运营管理专家 | - |
| **logistics_agent** | 物流管理专家 | - |

#### 营销与内容代理 (5个)

| 代理 | 描述 | 优先级 |
|------|------|--------|
| **marketing_agent** | 营销策划专家 | - |
| **sales_agent** | 销售管理专家 | - |
| **content_agent** | 内容创作专家 | - |
| **creative_agent** | 创意输出、文案生成 | 4 |
| **distribution_agent** | 分发渠道管理 | - |

#### 客户服务代理 (2个)

| 代理 | 描述 | 优先级 |
|------|------|--------|
| **support_agent** | 客户支持专家 | - |
| **service_agent** | 服务管理专家 | - |

#### 技术开发代理 (3个)

| 代理 | 描述 | 优先级 |
|------|------|--------|
| **architect_agent** | 技术选型、系统设计和数据库设计 | 2 |
| **mobile_agent** | 小程序、React Native和Flutter开发 | 16 |
| **product_manager_agent** | 需求分析、PRD编写和用户故事设计 | 1 |

#### 研究与分析代理 (3个)

| 代理 | 描述 | 优先级 |
|------|------|--------|
| **research_agent** | 信息收集、文献调研、知识整理 | 2 |
| **analysis_agent** | 数据分析、趋势分析、报告生成、市场研究 | 3 |
| **ai_news_summary_agent** | AI新闻摘要代理，自动收集和生成AI相关新闻摘要 | 10 |

#### 智能监控代理 (1个)

| 代理 | 描述 | 优先级 |
|------|------|--------|
| **x_monitor_agent** | X平台监控专家 | - |

#### 系统核心代理 (4个)

| 代理 | 描述 | 优先级 |
|------|------|--------|
| **task_agent** | 执行具体任务，调用相关Skills | 1 |
| **memory_agent** | 记忆管理专家 | - |
| **proactive_agent** | 主动服务专家 | - |
| **self_improving_agent** | 自我改进专家 | - |

---

## 🔌 4. 插件系统 (1个插件)

### 4.1 Leo Core Plugin
- **名称**: leo-core
- **版本**: 1.0.0
- **描述**: Leo AI System 核心插件
- **包含**:
  - 核心技能 (./skills/)
  - 子代理 (./agents/)
  - 自定义命令 (./commands/)
  - Hooks (./hooks/hooks.json)
  - MCP 服务器 (./mcp/servers.json)
- **配置**: [.claude/plugins/leo-core/plugin.json](.claude/plugins/leo-core/plugin.json)

---

## 🛠️ 5. MCP 工具 (7个工具)

### 5.1 Leo System MCP 服务器
- **配置**: [mcp.json](mcp.json)
- **服务器**: `src/leo_gateway/mcp_server.py`
- **端口**: 通过 OpenClaw Gateway (18789)

### 5.2 可用工具

| 工具 | 功能 |
|------|------|
| **execute_skill** | 执行指定的 Leo Skill |
| **delegate_to_agent** | 委托任务给指定的 Agent |
| **search_skills** | 搜索匹配的 Skills |
| **remember** | 保存信息到共享记忆 |
| **recall** | 从共享记忆检索信息 |
| **send_to_feishu** | 发送消息到飞书 |
| **get_openclaw_status** | 获取 OpenClaw Gateway 状态 |

### 5.3 可用资源

| 资源 | 内容 |
|------|------|
| **leo://skills/registry** | 所有已注册的 Leo Skills |
| **leo://agents/list** | 所有可用的 Agents |
| **leo://memory/shared** | 共享记忆存储 |
| **leo://gateway/status** | Leo Gateway 运行状态 |
| **leo://user/profile** | 当前用户画像 |

---

## 🪝 6. Hooks 系统 (3个 Hooks)

### 6.1 SessionStart Hook
- **触发时机**: 每次会话开始
- **功能**: 自动注入 Superpowers 技能上下文
- **配置**: [.claude/hooks.json](.claude/hooks.json)

### 6.2 ToolStart Hook
- **触发时机**: 工具调用前
- **功能**: 记录工具调用开始

### 6.3 ToolEnd Hook
- **触发时机**: 工具调用后
- **功能**: 记录工具调用结果

---

## 🔄 7. 工作流系统 (14个工作流)

基于 **Superpowers v4.3.1** 的协作工作流：

### 7.1 规划阶段
1. **brainstorming** - 头脑风暴
2. **writing_plans** - 编写实施计划
3. **bootstrap** - 生成功能计划

### 7.2 开发阶段
4. **using_git_worktrees** - 创建隔离工作空间
5. **test_driven_development** - TDD 实践
6. **subagent_driven_development** - 子代理驱动开发
7. **dispatching_parallel_agents** - 分发并行代理
8. **executing_plans** - 执行实施计划

### 7.3 审查阶段
9. **requesting_code_review** - 请求代码审查
10. **receiving_code_review** - 接收代码审查反馈
11. **verification_before_completion** - 完成前验证

### 7.4 调试阶段
12. **systematic_debugging** - 系统化调试

### 7.5 完成阶段
13. **finishing_development_branch** - 完成开发分支
14. **fresh-start** - 项目上下文加载

---

## 📦 10. MVP 项目

### 10.1 Angel Worm AI System
- **路径**: [projects/angel-worm-ai/](projects/angel-worm-ai/)
- **描述**: 天使虫 AI 系统
- **状态**: 开发中

---

## 🛠️ 8. 本地工具脚本 (99个脚本)

**脚本目录**: [scripts/](scripts/)

### 8.1 维护脚本 (19个)
**路径**: [scripts/maintenance/](scripts/maintenance/)

| 脚本 | 功能 |
|------|------|
| **self_maintenance.py** | 系统自维护 |
| **health_monitor.py** | 健康监控 |
| **doctor_check.py** | 系统诊断 |
| **monitor_openclaw_ui.py** | OpenClaw UI 监控 |
| **daily_memory_sync.py** | 每日记忆同步 |
| **sync_documentation.py** | 文档同步 |
| **sync_leo_to_obsidian.py** | Leo → Obsidian 同步 |
| **update_capability_index.py** | 更新能力索引 |
| **update_manifests.py** | 更新清单文件 |
| **review_all_capabilities.py** | 审查所有能力 |
| **scan_all_skills_security.py** | 技能安全扫描 |
| **auto_analyze_sessions.py** | 自动分析会话 |
| **repo_watch_weekly.py** | 每周仓库监控 |
| **validate_paths.py** | 路径验证 |
| **optimize_cron_schedule.py** | 优化定时任务 |
| **optimize_cron_schedule_v2.py** | 优化定时任务 v2 |
| **align_cron_to_8am.py** | 对齐定时任务到8点 |
| **add_ecommerce_cron.py** | 添加电商定时任务 |
| **设置每日情报定时任务.ps1** | 设置每日情报定时任务 |

### 8.2 业务脚本 (10个)
**路径**: [scripts/business/](scripts/business/)

| 脚本 | 功能 |
|------|------|
| **send_daily_intelligence.py** | 发送每日情报 |
| **send_feishu_report.py** | 发送飞书报告 |
| **deep_research_ningbo.py** | 宁波深度研究 |
| **deep_research_shaoxing_huafa.py** | 绍兴华发深度研究 |
| **research_ningbo_commercial.py** | 宁波商业地产研究 |
| **research_wechat_article.py** | 微信文章研究 |
| **generate_marketing_manual.py** | 生成营销手册 |
| **generate_marketing_manual_real.py** | 生成营销手册（真实版） |
| **md_to_slides.py** | Markdown 转 PPT |
| **run_opencode_pilot.py** | 运行 OpenCode Pilot |

### 8.3 OpenClaw 脚本 (9个)
**路径**: [scripts/openclaw/](scripts/openclaw/)

| 脚本 | 功能 |
|------|------|
| **openclaw_guardian.ps1** | OpenClaw 守护进程 |
| **openclaw_auto_healer.ps1** | OpenClaw 自动修复 |
| **guardian_loop.ps1** | 守护循环 |
| **session_maintenance.ps1** | 会话维护 |
| **validate_openclaw_config.py** | 验证 OpenClaw 配置 |
| **fix_openclaw_config_v2.py** | 修复 OpenClaw 配置 v2 |
| **create_shortcut.ps1** | 创建快捷方式 |
| **update_shortcut.ps1** | 更新快捷方式 |

### 8.4 开发工具 (16个)
**路径**: [scripts/development/](scripts/development/)

| 脚本 | 功能 |
|------|------|
| **create_skill.py** | 创建新技能 |
| **create_agent.py** | 创建新代理 |
| **create_workflow.py** | 创建新工作流 |
| **manage_skills.py** | 技能管理 |
| **cleanup_skills.py** | 清理技能 |
| **check_duplicates.py** | 检查重复 |

### 8.5 定时任务 (5个)
**路径**: [scripts/cron/](scripts/cron/)

| 脚本 | 功能 |
|------|------|
| **update_cron_jobs.py** | 更新定时任务 |
| **add_health_check_cron.py** | 添加健康检查定时任务 |
| **add_sleep_reminder.py** | 添加睡眠提醒 |
| **social_media_monitor.py** | 社交媒体监控 |
| **search_with_keywords.py** | 关键词搜索 |

### 8.6 演示脚本 (8个)
**路径**: [scripts/demos/](scripts/demos/)

| 脚本 | 功能 |
|------|------|
| **quick_run.py** | 快速运行 |
| **direct_executor.py** | 直接执行器 |
| **agent_interface.py** | 代理接口 |
| **agent_evaluation.py** | 代理评估 |
| **demo_skill_evolution.py** | 技能进化演示 |
| **demo_business_empowerment.py** | 业务赋能演示 |
| **run_prd_task.py** | 运行 PRD 任务 |
| **implement_web_ui.py** | 实现 Web UI |

### 8.7 测试脚本 (6个)
**路径**: [scripts/testing/](scripts/testing/)

### 8.8 实用工具 (12个)
**路径**: [scripts/utilities/](scripts/utilities/)

### 8.9 同步工具 (2个)
**路径**: [scripts/sync/](scripts/sync/)

| 脚本 | 功能 |
|------|------|
| **sync_superpowers.py** | 同步 Superpowers 技能 |

### 8.10 设置脚本 (8个)
**路径**: [scripts/setup/](scripts/setup/)

---

## 🔗 9. 集成系统

### 9.1 OpenClaw (飞书 AI 助手)
- **版本**: 2026.03.03
- **本地目录**: `D:\openclaw`
- **网关端口**: 18789
- **启动命令**: `cd D:\openclaw && node openclaw.mjs gateway --port 18789`
- **运维手册**: [docs/reference/OPENCLAW_OPS.md](docs/reference/OPENCLAW_OPS.md)

### 9.2 Superpowers
- **版本**: v4.3.1
- **原始存储**: `~/.claude/skills/superpowers/`
- **Leo 对应**: `src/leo_skills/` 下 14 个技能
- **同步脚本**: `scripts/sync/sync_superpowers.py`

### 9.3 Claude Code
- **版本**: 2.1.63
- **能力指南**: [docs/reference/CLAUDE_CODE_CAPABILITIES.md](docs/reference/CLAUDE_CODE_CAPABILITIES.md)

---

## 📂 10. 技能分类目录

Leo System 技能按以下 18 个分类组织：

| 分类 | 技能数 | 路径 |
|------|--------|------|
| automation | 3 | src/leo_skills/automation/ |
| backend | 6 | src/leo_skills/backend/ |
| business | 26 | src/leo_skills/business/ |
| collaboration | 8 | src/leo_skills/collaboration/ |
| content_creation | 15 | src/leo_skills/content_creation/ |
| core | 11 | src/leo_skills/core/ |
| debugging | 1 | src/leo_skills/debugging/ |
| development | 1 | src/leo_skills/development/ |
| devops | 9 | src/leo_skills/devops/ |
| frontend | 8 | src/leo_skills/frontend/ |
| intelligence | 1 | src/leo_skills/intelligence/ |
| prompt_engineering | 6 | src/leo_skills/prompt_engineering/ |
| scaffold | 6 | src/leo_skills/scaffold/ |
| security | 2 | src/leo_skills/security/ |
| testing | 11 | src/leo_skills/testing/ |
| tools | 96 | src/leo_skills/tools/ |
| utilities | 34 | src/leo_skills/utilities/ |
| videocut_skills | 5 | src/leo_skills/videocut_skills/ |

---

## 🎯 11. 快速查找索引

### 11.1 按业务场景

#### 房产业务
```
realestate, villa, auction, leasing, property_valuation,
tenant_screening, sales-sop, mortgage_calculator, pocket-crm
```

#### 贷款金融
```
loan, mortgage, credit, interest_calculator, repayment_calculator,
roi_calculator, financial_analysis
```

#### 电商运营
```
amazon, shopify, aliexpress, ebay, inventory, warehouse,
shipping, tracking, customs
```

#### 内容营销
```
content, article, blog, copywriting, seo, keyword_research,
social-auto-publish, douyin, xiaohongshu, video_monitor
```

#### 开发工具
```
code, api, database, test, docker, kubernetes, github,
react, vue, miniprogram, fastapi, flask
```

---

## 📊 12. 技能成熟度

详见 [leo_knowledge/context/skill_levels.md](leo_knowledge/context/skill_levels.md)

- **A级 (生产就绪)**: 核心技能、协作工作流
- **B级 (功能完整)**: 大部分业务技能
- **C级 (基础可用)**: 部分集成连接器
- **D级 (实验性)**: 新增技能

---

## 🔍 13. 使用方式

### 13.1 调用技能
```bash
# 通过 Claude Code
/skill_name

# 通过 Leo Gateway MCP
execute_skill(skill_name="xxx", params={...})

# 通过 OpenClaw 飞书
@Leo /skill_name
```

### 13.2 调用代理
```bash
# 通过 Agent 工具
Agent(subagent_type="code-reviewer", prompt="审查代码")

# 通过 MCP
delegate_to_agent(agent_name="researcher", task="分析架构")
```

### 13.3 查看技能详情
```bash
# 查看技能注册表
cat .claude/skill_registry.json

# 查看技能摘要
cat .claude/SKILLS_SUMMARY.md

# 搜索技能
grep -r "关键词" src/leo_skills/
```

---

## 📝 14. 相关文档

- **技能注册表**: [.claude/skill_registry.json](.claude/skill_registry.json)
- **技能摘要**: [.claude/SKILLS_SUMMARY.md](.claude/SKILLS_SUMMARY.md)
- **能力索引**: [leo_knowledge/context/capability_index.md](leo_knowledge/context/capability_index.md)
- **技能成熟度**: [leo_knowledge/context/skill_levels.md](leo_knowledge/context/skill_levels.md)
- **系统架构**: [docs/reference/LEO_SYSTEM_ARCHITECTURE_REPORT.md](docs/reference/LEO_SYSTEM_ARCHITECTURE_REPORT.md)
- **Claude Code 能力**: [docs/reference/CLAUDE_CODE_CAPABILITIES.md](docs/reference/CLAUDE_CODE_CAPABILITIES.md)
- **OpenClaw 运维**: [docs/reference/OPENCLAW_OPS.md](docs/reference/OPENCLAW_OPS.md)

---

## 🎉 总结

Leo AI System 是一个**全栈 AI 能力平台**，整合了：

- ✅ **249 个技能** - 覆盖房产、电商、内容、开发全业务链
- ✅ **37 个代理** - 4个Claude Code专家 + 33个Leo业务代理
- ✅ **14 个协作工作流** - 基于 Superpowers 的最佳实践
- ✅ **7 个 MCP 工具** - 统一的技能和代理调用接口
- ✅ **99 个脚本工具** - 维护、业务、开发、测试自动化
- ✅ **3 大集成系统** - OpenClaw、Superpowers、Claude Code

**核心优势**:
1. **业务导向** - 专为房产、电商、内容营销设计
2. **开发友好** - 完整的前后端、测试、DevOps 工具链
3. **协作增强** - Superpowers 工作流提升团队效率
4. **持续进化** - 技能自动更新、进化管理、安全扫描
5. **自动化运维** - 99个脚本工具实现系统自维护

---

**最后更新**: 2026-03-04
**维护者**: Leo AI System
**版本**: v3.0
