# Leo AI Agent System

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![CI/CD](https://img.shields.io/badge/CI-GitHub_Actions-2088FF.svg)](.github/workflows/ci-cd.yml)

**Leo的AI智能体系统** - Skills + Subagents 协同工作架构

[快速开始](#-快速开始) · [架构](#-系统架构) · [开发指南](#-开发指南) · [贡献](CONTRIBUTING.md)

</div>

---

## ✨ 特性

- 🧠 **智能编排** - Orchestrator统一协调Skills和Agents
- 🔧 **模块化Skills** - 287+个可复用技能模块
- 🤖 **多Agent支持** - 支持Research、Analysis、Creative等多种Agent类型
- 📋 **工作流引擎** - 支持并行、条件分支的复杂工作流
- 🔌 **易扩展** - 简单的API添加新Skill和Agent

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

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────┐
│                  Leo Orchestrator               │
│              (统一编排器 - 大脑)                  │
└────────────┬────────────────────────────────────┘
             │
      ┌──────┴──────┐
      │             │
      ▼             ▼
┌──────────┐  ┌─────────────┐
│ Subagents│  │   Skills    │
│ (执行者)  │  │  (能力库)    │
└──────────┘  └─────────────┘
```

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

## 🤖 可用Agents

| Agent | 类型 | 用途 |
|-------|------|------|
| task-agent | 执行者 | 通用任务执行 |
| research-agent | 研究者 | 信息采集和研究 |
| analysis-agent | 分析者 | 数据分析 |
| creative-agent | 创作者 | 内容创作 |
| architect-agent | 架构师 | 系统设计 |
| mobile-agent | 移动开发 | 小程序/App开发 |
| product-manager-agent | 产品经理 | 需求分析和规划 |

---

## 📋 预置工作流

| 工作流 | 说明 |
|--------|------|
| analysis-pipeline | 数据分析：采集→清洗→分析→报告 |
| content-pipeline | 内容创作：策划→创作→排版→发布 |
| research-pipeline | 研究调研：搜集→整理→分析→报告 |

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

- [系统架构详解](docs/system/)
- [Skill开发指南](docs/guides/)
- [API参考](docs/reference/)
- [更新日志](CHANGELOG.md)

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

**版本**: 1.0.0 | **最后更新**: 2026-01-24

</div>
