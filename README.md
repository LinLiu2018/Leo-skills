# Leo Wingman AI System v2.0

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-2.0.0-orange.svg)](docs/releases/RELEASE_v2.0.0.md)
[![Agents](https://img.shields.io/badge/Agents-37-purple.svg)](src/leo_subagents/agents/)
[![Workflows](https://img.shields.io/badge/Workflows-52-brightgreen.svg)](src/leo_workflows/definitions/)

**Leo Wingman** - 真正懂你的智能僚机系统

🧠 全自动记忆 | 🔄 自动进化 | 🤝 跨Agent共享 | 🎯 零配置

[快速开始](#-快速开始) · [架构](#-系统架构) · [开发指南](#-开发指南) · [v2.0发布说明](docs/releases/RELEASE_v2.0.0.md)

</div>

---

## ✨ 核心特性

### 🧠 全自动共享记忆（新增 v2.0）
- 自动记录所有交互，无需显式调用
- 跨 37 个 Agent 实时共享记忆
- 主动为 Agent 注入相关上下文
- 自动学习用户偏好和修正

### 🔄 自动进化架构（新增 v2.0）
- 4层进化：意图 → 感知 → 认知 → 执行
- 自动诊断问题并生成改进策略
- 自动代码修改、测试、部署

### 🤖 智能僚机系统
- **37 个 Agent** - 覆盖房产、贷款、电商、内容等7大业务板块
- **52 个工作流** - 预定义自动化流程，支持定时触发
- **零配置** - 系统自适应，越用越懂你

### 🔧 基础设施
- OpenClaw 双向集成 - 飞书/微信消息自动处理
- 统一用户画像 - 记录偏好、习惯、历史
- 多模型支持 - MiniMax、Kimi、GLM、Qwen、DeepSeek

---

## 🚀 快速开始

### 系统要求

- Python 3.9+
- pip 或 poetry

### 安装

```bash
# 克隆项目
git clone https://github.com/LinLiu2018/leo_ai_system.git
cd leo_ai_system

# 安装依赖
pip install -e .

# 安装开发依赖（可选）
pip install -e ".[dev]"
```

### 基础使用

```python
from leo_orchestrator.api import leo

# 查看系统状态
leo.stats()

# 调用Skill
result = leo.call(
    "content_layout_leo_skill",
    "layout",
    content="我的文章内容",
    style="data_driven"
)

# 运行Agent
result = leo.run_agent(
    "research-agent",
    "分析宁波房地产市场趋势"
)

# 执行工作流
result = leo.run_workflow(
    "analysis-pipeline",
    data_source="sales_data.csv"
)
```

---

## 🏗️ 系统架构 (v2.0)

```
┌─────────────────────────────────────────────────────────────┐
│                      Leo Wingman v2.0                        │
│                   自动进化 · 共享记忆 · 智能僚机               │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐   ┌─────────────────┐   ┌─────────────────┐
│  Auto Memory  │   │  Auto Evolution │   │  User Profile   │
│  全自动记忆    │   │  自动进化架构    │   │  统一用户画像    │
│  ·自动记录     │   │  ·意图解析       │   │  ·业务偏好       │
│  ·跨Agent共享 │   │  ·异常诊断       │   │  ·学习模式       │
│  ·主动注入     │   │  ·策略生成       │   │  ·交互历史       │
└───────────────┘   └─────────────────┘   └─────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Leo Orchestrator                          │
│                   (统一编排器 - 大脑)                         │
└─────────────────────────────────────────────────────────────┘
                              │
    ┌─────────────────────────┼─────────────────────────┐
    │                         │                         │
    ▼                         ▼                         ▼
┌──────────┐          ┌─────────────┐          ┌──────────┐
│  Agents  │          │  Workflows  │          │  Skills  │
│  (37个)   │          │   (52个)     │          │ (287+)   │
│ ·房产    │          │ ·房产销售    │          │ ·开发    │
│ ·贷款    │          │ ·内容创作    │          │ ·分析    │
│ ·电商    │          │ ·业务运营    │          │ ·创作    │
│ ·内容    │          │ ·数据分析    │          │ ·自动化  │
└──────────┘          └─────────────┘          └──────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     OpenClaw Gateway                         │
│              (飞书 · 微信 · 定时任务 · 多端同步)              │
└─────────────────────────────────────────────────────────────┘

### 项目结构

```
leo_ai_system/
├── src/                    # 源代码目录
│   ├── leo_orchestrator/   # 编排器 - API和协调逻辑
│   ├── leo_subagents/      # Agent层 - 任务执行者
│   ├── leo_skills/         # Skill层 - 能力模块库
│   ├── leo_workflows/      # 工作流定义
│   ├── leo_system/         # 系统核心(日志/错误/指标)
│   ├── leo_config/         # 配置管理
│   └── leo_knowledge/      # 知识库
│
├── tests/                  # 测试文件
├── scripts/                # 工具脚本
├── docs/                   # 文档
└── examples/               # 示例代码
```

### 核心组件

| 组件 | 说明 |
|------|------|
| **Skills** | 能力模块，提供具体功能实现 |
| **Subagents** | 任务执行者，调用Skills完成任务 |
| **Orchestrator** | 统一协调者，路由和编排 |
| **Workflows** | 预定义工作流，自动化流程 |

---

## 🤖 业务板块 & Agents (37个)

### 🏠 房产经纪 (5个)
| Agent | 功能 | 目标客户 |
|-------|------|----------|
| villa-agent | 度假养老别墅 | 高净值人群 |
| residential-agent | 刚需住宅 | 年轻家庭 |
| leasing-agent | 商业租赁 | 企业/商户 |
| commercial-sales-agent | 商业销售 | 投资客 |
| auction-agent | 法拍房 | 捡漏投资者 |

### 💰 贷款金融 (2个)
| Agent | 功能 |
|-------|------|
| loan-agent | 贷款计算、资质评估、方案匹配 |
| bank-product-agent | 银行产品库查询与推荐 |

### 🛒 跨境电商 (4个)
| Agent | 功能 |
|-------|------|
| ecommerce-agent | 竞品分析、文案生成、选品 |
| product-agent | 产品研究与分析 |
| operation-agent | 运营管理优化 |
| logistics-agent | 物流成本计算 |

### ✍️ 内容创意 (3个)
| Agent | 功能 |
|-------|------|
| content-agent | 社媒文案、视频脚本、分发 |
| creative-agent | 内容创作与策划 |
| distribution-agent | 多平台内容分发 |

### 🤖 基础能力 (23个)
| Agent | 类型 | 用途 |
|-------|------|------|
| task-agent | 执行者 | 通用任务执行 |
| research-agent | 研究者 | 信息采集和研究 |
| analysis-agent | 分析者 | 数据分析 |
| architect-agent | 架构师 | 系统设计 |
| mobile-agent | 移动开发 | 小程序/App开发 |
| product-manager-agent | 产品经理 | 需求分析和规划 |
| memory-agent | 记忆管理 | 共享记忆管理 |
| self-improving-agent | 自我改进 | 自动进化 |
| proactive-agent | 主动服务 | 预测用户需求 |

---

## 📋 工作流 (52个)

### 房产销售 (8个)
- **villa-consulting** - 别墅全流程咨询
- **residential-sales** - 住宅销售流程
- **auction-opportunity-scan** - 法拍房机会扫描
- **property-valuation** - 房产估值分析
- **investment-analysis** - 投资回报率分析
- **tenant-screening** - 租户资质审核
- **commercial-leasing** - 商业租赁匹配
- **site-visit-followup** - 带看自动跟进

### 业务运营 (8个)
- **weekly-sales-report** - 每周销售报告（定时）
- **market-research** - 市场研究报告
- **lead-nurturing** - 潜客培育流程
- **client-follow-up** - 客户跟进自动化
- **competitor-monitoring** - 竞品监控
- **customer-feedback** - 反馈智能分析
- **property-maintenance** - 物业维护管理
- **rent-collection** - 租金催收

### 内容创作 (5个)
- **content-pipeline** - 内容生产流水线
- **video-script-generator** - 视频脚本生成
- **social-media-generator** - 社媒内容批量生成
- **realestate-marketing** - 房产营销材料生成

### 更多工作流
查看 [工作流目录](src/leo_workflows/definitions/) 获取完整 52 个工作流列表。

---

## 🛠️ 开发指南

### 添加新Skill

1. 在 `src/leo_skills/<分类>/` 创建目录
2. 添加必需文件：
   - `SKILL.md` - Skill定义
   - `README.md` - 使用说明
   - `scripts/main.py` - 入口脚本
3. 运行发现系统：
   ```bash
   python scripts/development/manage_skills.py update
   ```

### 添加新Agent

1. 在 `src/leo_subagents/agents/` 创建目录
2. 继承 `BaseAgent` 类
3. 实现 `can_handle()` 和 `execute()` 方法
4. 在 `agents.yaml` 配置文件中注册

### 运行测试

```bash
# 运行所有测试
python -m pytest tests/ -v

# 带覆盖率
python -m pytest tests/ --cov=src --cov-report=html
```

---

## 📚 文档

### v2.0 新功能
- [v2.0 发布说明](docs/releases/RELEASE_v2.0.0.md) - 重大更新详情
- [全自动记忆指南](docs/guides/AUTO_MEMORY_GUIDE.md) - 记忆系统使用
- [更新日志](docs/guides/CHANGELOG.md) - 详细变更记录

### 开发文档
- [系统架构详解](docs/system/)
- [Skill开发指南](docs/guides/)
- [API参考](docs/reference/)

---

## 🤝 贡献

欢迎贡献代码！请查看 [贡献指南](CONTRIBUTING.md)。

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: 添加新功能'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

---

## 📄 许可证

本项目采用 [MIT 许可证](LICENSE)。

---

<div align="center">

**作者**: Leo Liu ([@LinLiu2018](https://github.com/LinLiu2018))

**版本**: 2.0.0 | **最后更新**: 2026-02-28 | [查看更新](docs/releases/RELEASE_v2.0.0.md)

</div>
