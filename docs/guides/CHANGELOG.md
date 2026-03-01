# 更新日志

本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/) 规范。

## [2.0.0] - 2026-02-28

### 🚀 重大更新：Leo Wingman 自动进化系统

此次更新实现了完整的自动进化架构，系统具备"越用越懂你"的能力。

#### 新增

- **全自动共享记忆系统**
  - `auto_memory.py` - 自动记录所有交互，无需显式调用
  - `memory_hooks.py` - 自动拦截 Agent 调用并注入上下文
  - `auto_init.py` - 系统启动时自动加载记忆能力
  - 跨 37 个 Agent 实时共享记忆
  - 主动为 Agent 提供相关历史上下文

- **用户偏好学习系统**
  - `preference_learning.py` - 自动学习用户偏好
  - 记录正面/负面反馈和修正
  - 生成个性化建议
  - 自适应参数调整

- **自动进化架构（4层）**
  - `intent_parser.py` - 意图解析层
  - `monitor.py` - 性能监控层
  - `strategy_engine.py` - 策略生成层
  - `auto_pipeline.py` - 自动执行流水线

- **房产业务 Agent（5个）**
  - Villa Agent - 度假养老别墅顾问
  - Residential Agent - 刚需住宅顾问
  - Leasing Agent - 商业租赁顾问
  - Commercial Sales Agent - 商业销售顾问
  - Auction Agent - 法拍房投资顾问

- **业务板块 Agent（3个）**
  - Loan Agent - 贷款金融顾问（完整功能）
  - Ecommerce Agent - 跨境电商顾问（已存在，功能扩展）
  - Content Agent - 内容创意顾问（新增）

- **Workflows（新增 21 个，总计 52 个）**
  - 贷款金融：loan_calculator, bank_product_matching
  - 跨境电商：listing_optimizer, logistics_calculator
  - 内容创意：social_media_generator, video_script_generator
  - 房产管理：property_valuation, investment_analysis, tenant_screening
  - 业务运营：market_research, weekly_sales_report, lead_nurturing
  - 销售支持：contract_review, site_visit_followup, competitor_monitoring
  - 物业管理：property_maintenance, rent_collection
  - 数据分析：feedback_analysis, price_optimization, inventory_management, financial_reporting

- **基础设施**
  - `openclaw_bridge.py` - OpenClaw 双向桥接
  - `openclaw.sh/bat` - 统一入口脚本
  - `user_profile.json` - 统一用户画像
  - `leo_wingman/` 目录骨架

#### 变更

- Workflow 定义文件从 31 个扩展到 52 个
- Agent 数量从 25 个扩展到 37 个
- 用户画像增加 `learning_system` 和 `interaction_history`
- 所有 Agent 可通过装饰器自动获得记忆能力

#### 修复

- 修复 `leo_skills.core.evolution.base` 导入路径问题
- 修复 OpenClaw 配置 `ownerDisplay` 问题
- 统一 OpenClaw 入口（解决 npm CLI 和本地 runtime 不一致）

---

## [1.0.0] - 2026-01-23

### 新增

- **Agents**
  - ArchitectAgent - 架构设计代理
  - MobileAgent - 移动开发代理
  - ProductManagerAgent - 产品经理代理
  - ResearchAgent - 研究代理
  - CreativeAgent - 创作代理
  - AnalysisAgent - 分析代理
  - RealestateAgent - 房产代理
  - TaskAgent - 任务执行代理

- **Workflows**
  - analysis-pipeline - 数据分析工作流
  - content-pipeline - 内容创作工作流
  - research-pipeline - 研究调研工作流

- **基础设施**
  - `.pre-commit-config.yaml` - 代码质量钩子
  - `.github/workflows/ci.yml` - CI/CD 流程
  - 扩展单元测试覆盖

### 变更

- 统一目录命名为 snake_case
- 全局语言设置为简体中文 (zh-CN)
