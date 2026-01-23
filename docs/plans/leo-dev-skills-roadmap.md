# Leo产品开发技能链路方案

**规划日期**: 2026-01-12
**目标**: 为Leo系统集成完整的产品开发能力，覆盖从需求到上线的全流程

---

## 一、调研结果总结

### 1.1 你已拥有的参考资源

你的项目中已有丰富的Claude Code subagents参考：

**官方示例 (claude-agent-sdk-demos)**:
- email-agent: 邮件处理Agent示例
- excel-demo: Excel处理示例
- research-agent: 多Agent研究系统
- resume-generator: 简历生成器

**社区资源 (claude-code-subagents)**:
```
├── architecture/      # 架构设计
│   ├── backend-architect.md
│   ├── cloud-architect.md
│   └── graphql-architect.md
├── development/       # 开发
│   ├── frontend-developer.md
│   ├── python-developer.md
│   ├── mobile-developer.md
│   └── go-developer.md
├── operations/        # 运维部署
│   ├── deployment-engineer.md
│   ├── devops-troubleshooter.md
│   └── performance-engineer.md
├── quality-assurance/ # 质量保证
│   ├── code-reviewer.md
│   ├── test-automator.md
│   └── debugger.md
└── security/          # 安全
    ├── security-auditor.md
    └── security-scanner.md
```

### 1.2 GitHub上值得参考的开源项目

| 项目 | GitHub Stars | 用途 | 集成建议 |
|------|-------------|------|----------|
| **gpt-engineer** | 52k+ | 需求→代码生成 | 参考其Prompt结构 |
| **aider** | 25k+ | AI结对编程 | 参考其代码编辑策略 |
| **crewAI** | 22k+ | 多Agent协作框架 | 参考其Agent编排模式 |
| **AutoGPT** | 168k+ | 自主Agent | 参考其任务分解逻辑 |
| **MetaGPT** | 45k+ | 软件公司模拟 | 参考其角色定义 |
| **OpenDevin** | 35k+ | 代码Agent | 参考其工具调用 |
| **Cookiecutter** | 22k+ | 项目脚手架 | 直接集成 |
| **Yeoman** | 9k+ | 脚手架生成器 | 参考模式 |

---

## 二、Leo产品开发技能体系架构

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                    Leo Product Dev System                    │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────┐   │
│  │                    Orchestrator                       │   │
│  │         (leo_orchestrator - 已有)                     │   │
│  └──────────────────────────────────────────────────────┘   │
│                            ↓                                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Dev Subagents Layer (新增)               │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐    │   │
│  │  │ Product │ │  Arch   │ │Frontend │ │ Backend │    │   │
│  │  │ Manager │ │Architect│ │   Dev   │ │   Dev   │    │   │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘    │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐    │   │
│  │  │ Mobile  │ │  Test   │ │ DevOps  │ │Security │    │   │
│  │  │   Dev   │ │Engineer │ │Engineer │ │ Auditor │    │   │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘    │   │
│  └──────────────────────────────────────────────────────┘   │
│                            ↓                                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                Dev Skills Layer (新增)                │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │  前端Skills    后端Skills    脚手架Skills   部署Skills │   │
│  │  ├─vue-gen    ├─flask-api   ├─project-    ├─docker   │   │
│  │  ├─react-gen  ├─fastapi     │ scaffold    ├─nginx    │   │
│  │  ├─miniprogram├─database    ├─miniprogram-├─ci-cd    │   │
│  │  └─css-gen    └─auth        │ template    └─deploy   │   │
│  └──────────────────────────────────────────────────────┘   │
│                            ↓                                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Dev Workflows (新增)                     │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │  • fullstack-pipeline: 需求→设计→开发→测试→部署       │   │
│  │  • miniprogram-pipeline: 小程序专用开发流程           │   │
│  │  • api-pipeline: API开发专用流程                      │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 开发角色定义

| 角色 | 职责 | 对应Subagent |
|------|------|-------------|
| 产品经理 | 需求分析、PRD编写、用户故事 | product-manager-agent |
| 架构师 | 技术选型、系统设计、数据库设计 | architect-agent |
| 前端开发 | Vue/React组件、小程序、H5页面 | frontend-agent |
| 后端开发 | Flask/FastAPI、数据库、API | backend-agent |
| 移动开发 | 小程序、React Native、Flutter | mobile-agent |
| 测试工程师 | 单元测试、集成测试、E2E测试 | test-agent |
| 运维工程师 | Docker、CI/CD、部署上线 | devops-agent |
| 安全审计 | 代码安全检查、漏洞扫描 | security-agent |

---

## 三、技能清单设计

### 3.1 前端Skills

```yaml
frontend-skills:
  # Vue生态
  - name: vue-component-generator-cskill
    description: "生成Vue3组件（Composition API + TypeScript）"
    inputs: [component_name, props_definition, functionality]
    outputs: [vue_component, types, unit_test]

  - name: vue-page-generator-cskill
    description: "生成完整的Vue页面（含路由配置）"
    inputs: [page_name, layout_type, api_endpoints]
    outputs: [vue_page, router_config, store_module]

  # React生态
  - name: react-component-generator-cskill
    description: "生成React组件（Hooks + TypeScript）"
    inputs: [component_name, props_interface, features]
    outputs: [react_component, types, test_file]

  # 微信小程序
  - name: miniprogram-page-generator-cskill
    description: "生成微信小程序页面"
    inputs: [page_name, page_config, data_bindings]
    outputs: [wxml, wxss, js, json]

  - name: miniprogram-component-generator-cskill
    description: "生成微信小程序组件"
    inputs: [component_name, properties, methods]
    outputs: [component_files]

  # 通用
  - name: css-layout-generator-cskill
    description: "生成响应式CSS布局"
    inputs: [layout_type, breakpoints, design_spec]
    outputs: [css_code, tailwind_classes]
```

### 3.2 后端Skills

```yaml
backend-skills:
  # Flask生态
  - name: flask-api-generator-cskill
    description: "生成Flask RESTful API"
    inputs: [resource_name, endpoints, database_model]
    outputs: [blueprint, models, schemas]

  - name: flask-auth-generator-cskill
    description: "生成Flask认证模块（JWT/Session）"
    inputs: [auth_type, user_model]
    outputs: [auth_blueprint, middleware, utils]

  # FastAPI生态
  - name: fastapi-endpoint-generator-cskill
    description: "生成FastAPI端点"
    inputs: [endpoint_spec, pydantic_models]
    outputs: [router, schemas, crud]

  # 数据库
  - name: database-model-generator-cskill
    description: "生成SQLAlchemy/Peewee模型"
    inputs: [entity_name, fields, relationships]
    outputs: [model_file, migration]

  - name: database-migration-cskill
    description: "生成数据库迁移脚本"
    inputs: [changes_description]
    outputs: [migration_script]

  # API文档
  - name: api-doc-generator-cskill
    description: "生成API文档（OpenAPI/Swagger）"
    inputs: [api_routes]
    outputs: [openapi_spec, markdown_doc]
```

### 3.3 脚手架Skills

```yaml
scaffold-skills:
  # 全栈项目
  - name: fullstack-project-scaffold-cskill
    description: "生成全栈项目结构"
    inputs: [project_name, frontend_framework, backend_framework]
    outputs: [project_structure, configs, docker_compose]
    template: |
      {{project_name}}/
      ├── frontend/           # 前端代码
      │   ├── src/
      │   ├── public/
      │   └── package.json
      ├── backend/            # 后端代码
      │   ├── app/
      │   ├── tests/
      │   └── requirements.txt
      ├── docker/             # Docker配置
      ├── docs/               # 文档
      └── docker-compose.yml

  # 微信小程序项目
  - name: miniprogram-project-scaffold-cskill
    description: "生成微信小程序项目结构"
    inputs: [project_name, features]
    outputs: [miniprogram_structure]
    template: |
      {{project_name}}/
      ├── miniprogram/
      │   ├── pages/
      │   ├── components/
      │   ├── utils/
      │   ├── services/
      │   └── app.json
      ├── cloudfunctions/    # 云函数
      └── project.config.json

  # Flask API项目
  - name: flask-api-scaffold-cskill
    description: "生成Flask API项目结构"
    inputs: [project_name, database_type]
    outputs: [flask_structure]
    template: |
      {{project_name}}/
      ├── app/
      │   ├── __init__.py
      │   ├── models/
      │   ├── api/
      │   ├── services/
      │   └── utils/
      ├── migrations/
      ├── tests/
      ├── config.py
      └── requirements.txt
```

### 3.4 部署Skills

```yaml
deployment-skills:
  # Docker
  - name: dockerfile-generator-cskill
    description: "生成优化的Dockerfile"
    inputs: [app_type, runtime, requirements]
    outputs: [dockerfile, dockerignore]

  - name: docker-compose-generator-cskill
    description: "生成docker-compose配置"
    inputs: [services, networks, volumes]
    outputs: [docker_compose_yaml]

  # Nginx
  - name: nginx-config-generator-cskill
    description: "生成Nginx配置"
    inputs: [domain, upstream, ssl_enabled]
    outputs: [nginx_conf]

  # CI/CD
  - name: github-actions-generator-cskill
    description: "生成GitHub Actions工作流"
    inputs: [workflow_type, triggers, steps]
    outputs: [workflow_yaml]

  # 一键部署
  - name: deployment-script-generator-cskill
    description: "生成部署脚本"
    inputs: [server_info, deploy_type]
    outputs: [deploy_script, rollback_script]
```

### 3.5 测试Skills

```yaml
test-skills:
  - name: unit-test-generator-cskill
    description: "生成单元测试"
    inputs: [source_code, test_framework]
    outputs: [test_file]

  - name: api-test-generator-cskill
    description: "生成API测试用例"
    inputs: [api_spec]
    outputs: [test_cases, postman_collection]

  - name: e2e-test-generator-cskill
    description: "生成端到端测试"
    inputs: [user_flows]
    outputs: [cypress_tests, playwright_tests]
```

---

## 四、开发工作流设计

### 4.1 全栈开发Pipeline

```yaml
fullstack-dev-pipeline:
  name: "全栈开发流水线"
  description: "从需求到部署的完整开发流程"

  stages:
    - name: "需求分析"
      agent: product-manager-agent
      skills:
        - research-assistant-cskill  # 已有
      outputs:
        - prd_document
        - user_stories

    - name: "架构设计"
      agent: architect-agent
      skills:
        - database-model-generator-cskill
        - api-doc-generator-cskill
      outputs:
        - system_design
        - database_schema
        - api_spec

    - name: "项目初始化"
      agent: devops-agent
      skills:
        - fullstack-project-scaffold-cskill
        - docker-compose-generator-cskill
      outputs:
        - project_structure
        - dev_environment

    - name: "后端开发"
      agent: backend-agent
      skills:
        - flask-api-generator-cskill
        - database-model-generator-cskill
        - flask-auth-generator-cskill
      outputs:
        - api_code
        - models
        - auth_module

    - name: "前端开发"
      agent: frontend-agent
      skills:
        - vue-page-generator-cskill
        - vue-component-generator-cskill
        - css-layout-generator-cskill
      outputs:
        - frontend_code
        - components

    - name: "测试"
      agent: test-agent
      skills:
        - unit-test-generator-cskill
        - api-test-generator-cskill
      outputs:
        - test_reports

    - name: "部署"
      agent: devops-agent
      skills:
        - dockerfile-generator-cskill
        - nginx-config-generator-cskill
        - deployment-script-generator-cskill
      outputs:
        - deployed_app
```

### 4.2 微信小程序Pipeline

```yaml
miniprogram-dev-pipeline:
  name: "微信小程序开发流水线"
  description: "专门针对微信小程序的开发流程"

  stages:
    - name: "需求设计"
      agent: product-manager-agent
      outputs: [prd, wireframes]

    - name: "项目初始化"
      skills:
        - miniprogram-project-scaffold-cskill
      outputs: [project_structure]

    - name: "页面开发"
      agent: frontend-agent
      skills:
        - miniprogram-page-generator-cskill
        - miniprogram-component-generator-cskill
      outputs: [pages, components]

    - name: "云函数开发"
      agent: backend-agent
      skills:
        - cloud-function-generator-cskill
      outputs: [cloud_functions]

    - name: "测试发布"
      outputs: [体验版, 正式版]
```

---

## 五、集成实施方案

### 5.1 目录结构规划

```
leo_skills/
├── content-creation/     # 已有
├── data-analysis/        # 已有
├── utilities/            # 已有
├── tools/                # 已有
│
├── development/          # 🆕 新增：开发类Skills
│   ├── frontend/
│   │   ├── vue-component-generator-cskill/
│   │   ├── react-component-generator-cskill/
│   │   ├── miniprogram-page-generator-cskill/
│   │   └── css-layout-generator-cskill/
│   ├── backend/
│   │   ├── flask-api-generator-cskill/
│   │   ├── fastapi-endpoint-generator-cskill/
│   │   ├── database-model-generator-cskill/
│   │   └── api-doc-generator-cskill/
│   ├── scaffold/
│   │   ├── fullstack-project-scaffold-cskill/
│   │   ├── miniprogram-project-scaffold-cskill/
│   │   └── flask-api-scaffold-cskill/
│   ├── deployment/
│   │   ├── dockerfile-generator-cskill/
│   │   ├── nginx-config-generator-cskill/
│   │   ├── github-actions-generator-cskill/
│   │   └── deployment-script-generator-cskill/
│   └── testing/
│       ├── unit-test-generator-cskill/
│       └── api-test-generator-cskill/

leo-subagents/
├── agents/               # 已有
│   ├── task-agent/
│   ├── research-agent/
│   ├── analysis-agent/
│   ├── creative-agent/
│   ├── realestate-agent/
│   │
│   ├── product-manager-agent/   # 🆕 新增
│   ├── architect-agent/         # 🆕 新增
│   ├── frontend-agent/          # 🆕 新增
│   ├── backend-agent/           # 🆕 新增
│   ├── mobile-agent/            # 🆕 新增
│   ├── test-agent/              # 🆕 新增
│   ├── devops-agent/            # 🆕 新增
│   └── security-agent/          # 🆕 新增
```

### 5.2 实施优先级

**第一阶段：核心开发能力（1-2周）**
```
高优先级（与裂变小程序直接相关）：
1. flask-api-generator-cskill      # 生成Flask API
2. miniprogram-page-generator-cskill # 生成小程序页面
3. database-model-generator-cskill  # 生成数据库模型
4. dockerfile-generator-cskill      # 生成Docker配置
```

**第二阶段：完善开发链路（2-3周）**
```
中优先级：
5. vue-component-generator-cskill
6. fullstack-project-scaffold-cskill
7. unit-test-generator-cskill
8. nginx-config-generator-cskill
```

**第三阶段：高级能力（持续迭代）**
```
低优先级：
9. react-component-generator-cskill
10. github-actions-generator-cskill
11. e2e-test-generator-cskill
12. security-scan-cskill
```

### 5.3 Subagent配置模板

```yaml
# leo-subagents/config/agents.yaml 新增内容

agents:
  # ... 已有的agents ...

  # 🆕 前端开发代理
  frontend-agent:
    name: "Frontend Agent"
    description: "前端开发代理，负责Vue/React/小程序开发"
    type: "developer"
    priority: 10

    skills:
      - name: "vue-component-generator-cskill"
        path: "../leo_skills/development/frontend/vue-component-generator-cskill"
        enabled: true
      - name: "miniprogram-page-generator-cskill"
        path: "../leo_skills/development/frontend/miniprogram-page-generator-cskill"
        enabled: true

    config:
      preferred_framework: "vue3"
      typescript_enabled: true

    activation_keywords:
      - "创建组件"
      - "生成页面"
      - "前端开发"
      - "小程序页面"

  # 🆕 后端开发代理
  backend-agent:
    name: "Backend Agent"
    description: "后端开发代理，负责Flask/FastAPI开发"
    type: "developer"
    priority: 11

    skills:
      - name: "flask-api-generator-cskill"
        path: "../leo_skills/development/backend/flask-api-generator-cskill"
        enabled: true
      - name: "database-model-generator-cskill"
        path: "../leo_skills/development/backend/database-model-generator-cskill"
        enabled: true

    config:
      preferred_framework: "flask"
      database: "mysql"

    activation_keywords:
      - "创建API"
      - "生成接口"
      - "后端开发"
      - "数据库模型"

  # 🆕 运维部署代理
  devops-agent:
    name: "DevOps Agent"
    description: "运维部署代理，负责Docker/CI-CD/部署"
    type: "operator"
    priority: 12

    skills:
      - name: "dockerfile-generator-cskill"
        path: "../leo_skills/development/deployment/dockerfile-generator-cskill"
        enabled: true
      - name: "nginx-config-generator-cskill"
        path: "../leo_skills/development/deployment/nginx-config-generator-cskill"
        enabled: true
      - name: "deployment-script-generator-cskill"
        path: "../leo_skills/development/deployment/deployment-script-generator-cskill"
        enabled: true

    activation_keywords:
      - "部署"
      - "Docker"
      - "上线"
      - "服务器配置"
```

### 5.4 开发Workflow配置

```yaml
# leo_config/settings/config.yaml 新增workflows

workflows:
  # ... 已有的workflows ...

  # 🆕 全栈开发流水线
  fullstack-dev-pipeline:
    name: "全栈开发流水线"
    description: "从需求到部署的完整开发流程"
    enabled: true
    steps:
      - name: "analyze"
        agent: "research-agent"
        description: "需求分析"
      - name: "design"
        agent: "architect-agent"
        description: "架构设计"
      - name: "backend"
        agent: "backend-agent"
        description: "后端开发"
      - name: "frontend"
        agent: "frontend-agent"
        description: "前端开发"
      - name: "test"
        agent: "test-agent"
        description: "测试"
      - name: "deploy"
        agent: "devops-agent"
        description: "部署上线"

  # 🆕 小程序开发流水线
  miniprogram-dev-pipeline:
    name: "小程序开发流水线"
    description: "微信小程序专用开发流程"
    enabled: true
    steps:
      - name: "design"
        agent: "product-manager-agent"
        description: "产品设计"
      - name: "pages"
        agent: "frontend-agent"
        description: "页面开发"
      - name: "api"
        agent: "backend-agent"
        description: "接口开发"
      - name: "deploy"
        agent: "devops-agent"
        description: "发布上线"
```

---

## 六、与裂变小程序项目的对接

你的裂变小程序项目可以这样使用新的开发技能：

### 6.1 一键生成项目结构

```python
# 使用脚手架Skill
from leo_system import LeoSystem

system = LeoSystem()
result = system.execute_task(
    "创建裂变小程序项目",
    skill_name="miniprogram-project-scaffold-cskill",
    project_name="fission-miniprogram",
    features=["裂变分享", "用户信息收集", "邀请统计"]
)
```

### 6.2 生成API接口

```python
# 使用Flask API Skill
result = system.execute_task(
    "生成线索收集API",
    skill_name="flask-api-generator-cskill",
    resource_name="leads",
    endpoints=[
        {"method": "POST", "path": "/leads", "description": "创建线索"},
        {"method": "GET", "path": "/leads/<id>", "description": "获取线索"},
        {"method": "GET", "path": "/leads/<id>/referrals", "description": "获取邀请列表"}
    ]
)
```

### 6.3 生成部署配置

```python
# 使用部署Skill
result = system.execute_task(
    "生成部署配置",
    skill_name="dockerfile-generator-cskill",
    app_type="flask",
    runtime="python:3.9",
    requirements="requirements.txt"
)
```

---

## 七、下一步行动

### 立即可以做的事情

1. **复用已有的subagent定义**
   - 直接从 `docs/reference/claude-code-subagents/community/` 复制相关agent到 `leo-subagents/agents/`
   - 重命名并调整为符合Leo规范

2. **创建第一个开发Skill**
   - 建议从 `flask-api-generator-cskill` 开始
   - 因为你的裂变小程序后端就是Flask

3. **测试开发流程**
   - 用新的Skills重新实现裂变小程序的某个模块
   - 验证开发效率提升

### 建议的开始命令

```bash
# 1. 创建开发Skills目录结构
mkdir -p leo_skills/development/{frontend,backend,scaffold,deployment,testing}

# 2. 复制参考的subagents
cp docs/reference/claude-code-subagents/community/claude-code-subagents/subagents/development/*.md leo-subagents/agents/

# 3. 创建第一个Skill
mkdir -p leo_skills/development/backend/flask-api-generator-cskill
```

---

**方案完成时间**: 2026-01-12
**规划者**: Leo AI Agent System + Claude
**版本**: 1.0.0
