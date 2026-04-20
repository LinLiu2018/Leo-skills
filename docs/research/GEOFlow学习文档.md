# GEOFlow 开源项目学习文档

> **信息来源**: GitHub yaojingang/GEOFlow
> **获取日期**: 2026-04-15
> **仓库地址**: https://github.com/yaojingang/GEOFlow
> **Star**: 540 | Fork: 109 | 语言: PHP | 许可证: Apache 2.0

---

## 📋 项目概述

**GEOFlow** 是一个面向 GEO（搜索内容优化）/ SEO 内容运营场景的**开源内容生产系统**。它把模型配置、素材管理、任务调度、草稿审核和前台发布串成一条完整链路，适合搭建自动化内容站点或内部内容运营后台。

### 核心定位
- AI 驱动的自动化内容生成与发布平台
- 批量生成 SEO 优化的文章内容
- 支持多 AI 模型接入（OpenAI 兼容接口）

### 技术栈

| 类别 | 技术 |
|------|------|
| 后端 | PHP 7.4+（原生开发，无框架） |
| 数据库 | PostgreSQL（运行时）、SQLite（旧版本） |
| 前端 | TailwindCSS + 原生 JavaScript + Lucide Icons |
| 部署 | Docker Compose |
| AI 集成 | OpenAI 兼容接口 |

---

## 🏗 系统架构

### 核心运行结构

```
后台管理页面
    ↓
任务调度器 / 队列
    ↓
Worker 执行 AI 生成
    ↓
草稿 / 审核 / 发布
    ↓
前台文章与 SEO 页面输出
```

### 层级说明

| 层级 | 说明 |
|------|------|
| **Web / Admin** | 前台文章站点与后台管理页面，负责内容浏览、素材管理、任务管理和配置入口 |
| **API / CLI** | `/api/v1` 提供机器接口，`bin/geoflow` 提供本地 CLI 能力，适合批量任务和自动化接入 |
| **Scheduler / Worker** | 调度器负责扫描任务和入队，Worker 负责实际调用模型生成内容 |
| **Domain Services** | `includes/` 中的任务、文章、队列、AI、检索等服务承载核心业务规则 |
| **Persistence** | PostgreSQL 作为运行时数据库，保存任务、文章、素材、审核状态和系统配置 |

---

## 📁 目录结构

```
GEOFlow/
├── index.php                     前台首页入口
├── article.php                   文章详情页入口
├── category.php                  分类页入口
├── archive.php                   归档页入口
├── router.php                    本地开发路由入口
├── docker-compose.yml            开发环境编排
├── docker-compose.prod.yml       生产环境编排模板
├── start.sh                      本地快速启动脚本
├── .env.example                  环境变量模板
│
├── admin/                        后台管理系统
│   ├── dashboard.php             仪表盘与统计总览
│   ├── tasks.php                 任务管理
│   ├── task-create.php           新建任务页
│   ├── articles.php              文章列表
│   ├── articles-review.php       审核中心
│   ├── materials.php             素材管理入口
│   ├── ai-models.php             AI 模型配置
│   ├── ai-prompts.php            提示词模板管理
│   └── site-settings.php         站点设置
│
├── api/v1/                       API 层
│   └── index.php                 API 单入口
│
├── assets/                       静态资源
│   ├── css/                      样式文件
│   ├── js/                       交互脚本
│   └── images/                   图片资源
│
├── bin/                          CLI 与脚本
│   ├── geoflow                   本地 CLI
│   ├── cron.php                  调度器
│   ├── worker.php                Worker 进程
│   ├── db_maintenance.php        数据库维护
│   └── migrate_sqlite_to_pg.php  迁移脚本
│
├── docker/                       容器配置
│   ├── Dockerfile                多阶段镜像定义
│   ├── entrypoint.sh             Web 容器启动入口
│   ├── scheduler.sh              调度容器启动入口
│   └── php.ini                   PHP 配置
│
├── docs/                         文档中心
│   ├── deployment/               部署文档
│   ├── project/                  研发文档
│   ├── AI_PROJECT_GUIDE.md       AI 核心模块说明
│   └── FAQ.md                    常见问题
│
├── includes/                     核心业务逻辑 ⭐
│   ├── config.php                全局配置
│   ├── db_support.php            数据库驱动
│   ├── database.php              数据访问封装
│   ├── database_admin.php        后台初始化
│   ├── functions.php              公共函数
│   ├── ai_engine.php             AI 生成引擎 ⭐核心
│   ├── ai_service.php            AI 请求封装
│   ├── job_queue_service.php      队列服务
│   ├── task_service.php           任务基础服务
│   ├── task_lifecycle_service.php 任务生命周期
│   ├── article_service.php        文章服务
│   ├── api_auth.php              API 鉴权
│   ├── api_token_service.php     Token 服务
│   └── catalog_service.php        资源字典
│
└── data/                         运行时数据目录
```

---

## 🔄 内容生成流程

```
配置模型 / 素材 / 提示词
        ↓
创建任务
        ↓
调度器入队
        ↓
Worker 调用 AI 生成正文
        ↓
可选插图 / SEO 元信息
        ↓
草稿 / 审核 / 发布
        ↓
前台展示
```

### 核心链路详解

1. **后台配置** → 配置模型、提示词和素材库
2. **创建任务** → 在"任务管理"里选择标题库、模型、提示词、图片库和发布规则
3. **调度器入队** → 调度器扫描任务并写入 job queue
4. **Worker 执行** → 调用 AI 生成正文
5. **文章流程** → 草稿 → 审核 → 发布
6. **前台输出** → 文章与 SEO 页面展示

---

## 🗄 核心数据库表

### 文章相关

```sql
articles (
    id, title, slug, excerpt, content,
    category_id, author_id, task_id,        -- task_id 关联 AI 生成任务
    keywords, meta_description,             -- SEO 字段
    status,                                 -- draft/published/private/deleted
    review_status,                          -- pending/approved/rejected
    is_featured, view_count, like_count,
    created_at, updated_at, published_at
)
```

### AI 任务相关

```sql
tasks (
    id, name,
    title_library_id,                       -- 标题库 ID
    image_library_id, image_count,          -- 图片配置
    prompt_id, ai_model_id,                 -- AI 配置
    author_id,                              -- 作者
    need_review,                            -- 是否需要审核
    publish_interval,                       -- 发布间隔（秒）
    draft_limit,                            -- 草稿数量限制
    is_loop,                                -- 是否循环生成
    status,                                 -- active/paused/completed
    batch_status,                           -- 批量执行状态
    created_count, published_count          -- 统计
)

ai_models (
    id, name, version, api_key, model_id,
    api_url,                                -- API 端点
    daily_limit, used_today, total_used,
    status
)

prompts (
    id, name, type, content,
    variables                               -- 支持的变量
)
```

### 素材库

```sql
title_libraries / titles                   -- 标题库
image_libraries / images                   -- 图片库
knowledge_bases                             -- 知识库
authors                                     -- 作者表
```

---

## 🤖 核心类说明

### Database 类 (`includes/database.php`)
- 单例模式，全局唯一数据库连接
- 核心方法：`query()`, `fetchOne()`, `fetchAll()`, `insert()`, `update()`, `delete()`, `count()`

### AIEngine 类 (`includes/ai_engine.php`) ⭐核心
```php
public function executeTask($task_id)
// 工作流程：
// 1. 获取任务配置
// 2. 检查草稿限制
// 3. 从标题库获取未使用标题
// 4. 调用 AI 生成内容
// 5. 插入图片（如果配置）
// 6. 生成关键词和描述
// 7. 保存文章为草稿
// 8. 更新统计数据
```

### TaskStatusManager 类
- 进程生命周期管理器
- 防止进程泄漏和状态不一致
- 状态：`idle` → `running` → `stopped` / `error` / `completed`

---

## 🚀 快速开始

### Docker 部署（推荐）

```bash
# 1. 克隆仓库
git clone https://github.com/yaojingang/GEOFlow.git
cd GEOFlow

# 2. 复制环境变量文件
cp .env.example .env

# 3. 编辑 .env，设置必要参数
vi .env

# 4. 启动服务
docker compose --profile scheduler up -d --build

# 访问前台: http://localhost:18080
# 访问后台: http://localhost:18080/geo_admin/
```

### 本地 PHP 服务器

```bash
# 1. 配置环境变量
export DB_DRIVER=pgsql
export DB_HOST=127.0.0.1
export DB_PORT=5432
export DB_NAME=geo_system
export DB_USER=geo_user
export DB_PASSWORD=geo_password

# 2. 启动开发服务器
php -S localhost:8080 router.php

# 访问后台: http://localhost:8080/geo_admin/
```

### 默认管理员账号
- 用户名: `admin`
- 密码: `admin888`

---

## ⚙️ 环境变量配置

```dotenv
# Web 服务端口（默认 18080）
HOST_PORT=18080

# 站点访问地址
SITE_URL=http://localhost:18080

# 应用安全密钥（建议使用 32 位以上随机字符串）
APP_SECRET_KEY=replace-with-a-long-random-secret

# Cron 调度间隔（秒，默认 60）
CRON_INTERVAL=60

# 时区
TZ=Asia/Shanghai
```

---

## 🛡 安全特性

- **SQL 注入防护**: PDO 预处理语句
- **CSRF 防护**: 表单提交验证 Token
- **XSS 防护**: HTMLSpecialChars 转义
- **密码加密**: bcrypt
- **安全响应头**: X-Frame-Options, X-Content-Type-Options 等

---

## 🔌 配套 Skill

项目配套提供公开 skill，用于通过本地 `geoflow` CLI 操作 GEOFlow 系统：

- **Skill 仓库**: yaojingang/yao-geo-skills
- **Skill 路径**: `skills/geoflow-cli-ops`

适用场景：
- 通过本地 CLI 创建和管理任务
- 上传文章草稿
- 审核和发布文章
- 检查任务与 job 状态

---

## 📚 Docker 组件

| 服务 | 说明 | 启动方式 |
|------|------|----------|
| `web` | 提供前后台 HTTP 访问 | 默认启动 |
| `postgres` | PostgreSQL 数据库 | 默认启动 |
| `scheduler` | 任务调度器 | `--profile scheduler` |
| `worker` | AI 生成进程 | `--profile scheduler` |

---

## ⚠️ 当前开源定位

- 提供可运行的公开源码版本
- 不附带生产数据库、上传文件和真实 API 密钥
- 适合作为二次开发基础，或用于自建 GEO 内容站点

---

## 🆚 与本项目（LEO）的对比参考

| 维度 | GEOFlow | LEO AI System |
|------|---------|---------------|
| 定位 | GEO/SEO 内容生产 | AI 助手系统 |
| 语言 | PHP | Python |
| 数据库 | PostgreSQL | 可配置 |
| AI 集成 | OpenAI 兼容接口 | OpenAI/MiniMax |
| 工作流 | 任务→队列→Worker→审核→发布 | 编排器→技能→执行 |
| 部署 | Docker | Docker |

---

## 📎 参考链接

- [GitHub 仓库](https://github.com/yaojingang/GEOFlow)
- [配套 Skill 仓库](https://github.com/yaojingang/yao-geo-skills)
- [多语言 README](README_en.md) / [日本語](README_ja.md) / [Español](README_es.md)
