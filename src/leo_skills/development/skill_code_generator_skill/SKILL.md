---
name: skill_code_generator_skill
description: Automated skill generation tool for creating Leo AI skills with templates, scaffolding, code patterns, configuration files, documentation, and testing framework setup. Activates when user asks to create a new skill, generate skill code, scaffold a skill, or automate skill creation.
---

# Skill Code Generator

自动化技能生成工具，用于快速创建符合 Leo AI 标准的技能。

## 功能特性

### 1. 模板化生成
- 基于预定义模板快速生成技能结构
- 支持多种技能类型（数据分析、内容创建、工具类等）
- 自动生成标准目录结构

### 2. 代码脚手架
- 自动创建 `SKILL.md`、`README.md`、`scripts/main.py`
- 生成配置文件（`config.yaml`）
- 创建测试文件框架

### 3. 代码模式实现
- 实现常见的代码模式（API调用、数据处理、文件操作等）
- 自动添加错误处理和日志记录
- 集成最佳实践

### 4. 文档生成
- 自动生成技能文档
- 创建使用示例
- 生成 API 文档

### 5. 测试框架
- 创建单元测试模板
- 生成测试数据
- 配置测试环境

## 使用方法

### 基本用法

```bash
# 创建新技能
python scripts/main.py create --name my-skill --category tools

# 使用模板创建
python scripts/main.py create --name my-skill --template api-client

# 交互式创建
python scripts/main.py create --interactive
```

### 命令选项

- `--name`: 技能名称
- `--category`: 技能分类（tools/utilities/content-creation等）
- `--template`: 使用的模板名称
- `--description`: 技能描述
- `--interactive`: 交互式模式

## 激活条件

当用户说以下内容时自动激活：
- "创建一个新技能"
- "生成技能代码"
- "搭建技能脚手架"
- "自动化创建技能"
- "Create a new skill"
- "Generate skill code"
- "Scaffold a skill"

## 技能结构

生成的技能包含以下标准结构：

```
my-skill-cskill/
├── SKILL.md              # 技能定义
├── README.md             # 使用文档
├── config/
│   └── config.yaml       # 配置文件
├── scripts/
│   ├── main.py          # 主入口
│   └── utils/           # 工具函数
├── tests/
│   └── test_main.py     # 测试文件
└── examples/
    └── example.py       # 使用示例
```

## 支持的模板

1. **api-client**: API 客户端技能
2. **data-processor**: 数据处理技能
3. **content-generator**: 内容生成技能
4. **file-handler**: 文件处理技能
5. **automation**: 自动化任务技能

## 配置

在 `config/templates.yaml` 中可以自定义模板：

```yaml
templates:
  api-client:
    description: "API client skill template"
    files:
      - SKILL.md
      - README.md
      - scripts/main.py
      - scripts/api_client.py
      - config/config.yaml
```

## 最佳实践

1. **命名规范**: 使用 `{function}-{type}-cskill` 格式
2. **文档完整**: 确保 SKILL.md 和 README.md 完整
3. **测试覆盖**: 为关键功能编写测试
4. **配置分离**: 将配置与代码分离
5. **错误处理**: 添加完善的错误处理

## 示例

### 创建 API 客户端技能

```bash
python scripts/main.py create \
  --name weather-api-cskill \
  --category tools \
  --template api-client \
  --description "Weather API client for fetching weather data"
```

### 创建数据处理技能

```bash
python scripts/main.py create \
  --name data-cleaner-cskill \
  --category utilities \
  --template data-processor \
  --description "Data cleaning and preprocessing tool"
```

## 依赖

- Python 3.8+
- jinja2 (模板引擎)
- pyyaml (配置文件)

## 版本

- **Version**: 1.0.0
- **Author**: Claude Code
- **Last Updated**: 2026-01-24

## 相关技能

- [agent_skill_creator_skill](../tools/agent_skill_creator_skill) - 高级代理创建工具
- [skill-evolution-assistant](../tools/skill_evolution_assistant_skill) - 技能进化助手
