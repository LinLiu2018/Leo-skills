---
name: skill-code-generator-skill
description: 技能代码生成工具，自动化创建 Leo AI 技能。当用户需要创建新技能、生成技能代码、搭建技能脚手架、从模板生成技能或批量创建技能时使用。 [优化第5轮：提升了触发准确率]
license: MIT
metadata:
  version: "2.0.0"
  category: development
  author: Leo AI System
  templates: 5
  actions: 6
---

# Skill Code Generator - 技能代码生成器

自动化技能生成工具，用于快速创建符合 Leo AI 和 Anthropic 标准的技能。

## 核心功能

### 1. 模板化生成
- 基于 5 个预定义模板快速生成技能结构
- 支持多种技能类型（API 客户端、数据处理、内容生成等）
- 自动生成标准目录结构

### 2. 代码脚手架
- 自动创建 `SKILL.md`、`README.md`、`scripts/main.py`
- 生成配置文件（`config.yaml`）
- 创建测试文件框架

### 3. 代码模式实现
- 实现常见的代码模式（API 调用、数据处理、文件操作等）
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

```python
from skill_code_generator_skill import SkillCodeGenerator

generator = SkillCodeGenerator()

# 从规格生成
result = generator.execute(
    action="generate",
    name="my-skill",
    description="我的技能描述",
    category="tools"
)

# 从自然语言生成
result = generator.execute(
    action="generate_from_prompt",
    prompt="创建一个天气 API 客户端技能"
)

# 从模板生成
result = generator.execute(
    action="generate_from_template",
    template="api-client",
    name="weather-api"
)

# 列出可用模板
result = generator.execute(action="list_templates")
```

### CLI 用法

```bash
# 创建新技能
python scripts/main.py create --name my-skill --category tools

# 使用模板创建
python scripts/main.py create --name my-skill --template api-client

# 交互式创建
python scripts/main.py create --interactive
```

## 使用示例

### 示例 1：创建 API 客户端技能

```
用户：帮我创建一个天气 API 客户端技能
技能：正在生成技能代码...
      ✅ 技能已生成：weather-api-client-skill
      📁 目录结构：
      - SKILL.md
      - weather_api_client_skill.py
      - scripts/main.py
      - config/config.yaml
      - tests/test_weather_api.py
      📦 依赖：requests
      位置：./weather-api-client-skill/
```

### 示例 2：从模板生成

```
用户：用 api-client 模板创建一个技能
技能：正在使用 api-client 模板...
      ✅ 技能已生成：my-api-client-skill
      🔧 预置功能：
      - API 认证处理
      - 请求/响应封装
      - 错误处理
      - 速率限制
      位置：./my-api-client-skill/
```

### 示例 3：批量创建技能

```
用户：帮我创建 3 个技能：数据分析、内容生成、自动化
技能：正在批量生成...
      ✅ 数据分析技能 - data-analysis-skill
      ✅ 内容生成技能 - content-generator-skill
      ✅ 自动化技能 - automation-scheduler-skill
      共创建 21 个文件
      所有技能已就绪，可以开始开发
```

### 示例 4：验证技能

```
用户：验证这个技能目录是否规范
技能：正在检查...
      ✅ 验证通过
      - SKILL.md: 符合 Anthropic 标准
      - Python 语法：无错误
      - YAML 配置：格式正确
      - 测试文件：已包含
      建议：可以添加更多使用示例
```

### 示例 5：列出可用模板

```
用户：有哪些技能模板可以用？
技能：可用模板：
      1. api-client - API 客户端技能（依赖：requests）
      2. data-processor - 数据处理技能（依赖：pandas）
      3. content-generator - 内容生成技能（依赖：jinja2）
      4. file-handler - 文件处理技能
      5. automation - 自动化任务技能（依赖：schedule）
      使用 generate_from_template 选择模板创建
```

## 支持的模板

| 模板名 | 用途 | 依赖 |
|--------|------|------|
| `api-client` | API 客户端技能 | requests |
| `data-processor` | 数据处理技能 | pandas |
| `content-generator` | 内容生成技能 | jinja2 |
| `file-handler` | 文件处理技能 | - |
| `automation` | 自动化任务技能 | schedule |

## 生成的技能结构

```
my-skill_skill/
├── SKILL.md              # 技能定义（符合 Anthropic 标准）
├── README.md             # 使用文档
├── __init__.py           # 模块初始化
├── {name}_skill.py       # 主实现（继承 BaseExecutor）
├── scripts/
│   ├── __init__.py
│   └── main.py          # CLI 入口
├── config/
│   └── config.yaml      # 配置文件
└── tests/
    ├── __init__.py
    └── test_{name}_skill.py  # 单元测试
```

## 激活条件

当用户说以下内容时自动激活：
- "创建一个新技能"
- "生成技能代码"
- "搭建技能脚手架"
- "用模板创建技能"
- "批量创建技能"
- "Create a new skill"
- "Generate skill code"
- "Scaffold a skill"

## 配置

在 `config/config.yaml` 中可以自定义：

```yaml
# 技能代码生成器配置
enabled: true
version: "2.0.0"

# 默认设置
defaults:
  category: utilities
  author: "Leo AI System"
  license: "MIT"

# 模板配置
templates:
  api-client:
    enabled: true
    extra_files:
      - scripts/api_client.py
```

## 最佳实践

1. **命名规范**: 使用 `{function}-{type}-skill` 格式
2. **文档完整**: 确保 SKILL.md 和 README.md 完整
3. **测试覆盖**: 为关键功能编写测试
4. **配置分离**: 将配置与代码分离
5. **错误处理**: 添加完善的错误处理

## 依赖

- Python 3.8+
- Leo Skills Core
- jinja2 (模板引擎)
- pyyaml (配置文件)

## 版本历史

| 版本 | 日期 | 更新内容 |
|------|------|----------|
| 2.0.0 | 2026-03-13 | 符合 Anthropic 标准，添加使用示例 |
| 1.0.0 | 2026-01-24 | 初始版本 |

## 相关技能

- [agent_skill_creator_skill](../tools/agent_skill_creator_skill) - 高级代理创建工具
- [skill-evolution-assistant](../tools/skill_evolution_assistant_skill) - 技能进化助手

---
*最后更新：2026-03-13*
