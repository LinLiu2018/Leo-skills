#!/usr/bin/env python3
"""
优化 Skill Code Generator Skill
1. 更新 Description 符合 Anthropic 标准
2. 规范化版本管理
3. 添加使用示例
4. 启用进化能力配置
"""

import os
import yaml
from pathlib import Path
from datetime import datetime

SKILL_PATH = Path(r"E:\桌面\leo_ai_system\src\leo_skills\development\skill_code_generator_skill")

def optimize_skill():
    """优化技能文件"""
    
    print("="*60)
    print("优化 Skill Code Generator Skill")
    print("="*60)
    
    # ========== 1. 更新 SKILL.md ==========
    print("\n[1/4] 更新 SKILL.md...")
    
    skill_md_content = '''---
name: skill-code-generator-skill
description: 技能代码生成工具，自动化创建 Leo AI 技能。当用户需要创建新技能、生成技能代码、搭建技能脚手架、从模板生成技能或批量创建技能时使用。
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
'''
    
    skill_md_path = SKILL_PATH / "SKILL.md"
    skill_md_path.write_text(skill_md_content, encoding='utf-8')
    print(f"[OK] 已更新 SKILL.md")
    
    # ========== 2. 更新 Python 文件版本 ==========
    print("\n[2/4] 更新 Python 文件版本...")
    
    main_py_path = SKILL_PATH / "skill_code_generator_skill.py"
    content = main_py_path.read_text(encoding='utf-8')
    
    # 更新类文档字符串中的版本
    if 'version: "1.0.0"' in content:
        content = content.replace('version: "1.0.0"', 'version: "2.0.0"')
        main_py_path.write_text(content, encoding='utf-8')
        print(f"[OK] 已更新版本号：1.0.0 → 2.0.0")
    else:
        print(f"[WARN] 版本号格式可能已变更")
    
    # ========== 3. 创建进化能力配置 ==========
    print("\n[3/4] 创建进化能力配置...")
    
    evolution_config = {
        "evolution": {
            "enabled": True,
            "learning": {
                "min_executions_for_learning": 10,
                "analysis_window": 100
            },
            "optimization": {
                "auto_optimize": False,
                "require_approval": True
            }
        },
        "version": "2.0.0",
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    evolution_path = SKILL_PATH / "config" / "evolution_config.yaml"
    evolution_path.parent.mkdir(parents=True, exist_ok=True)
    
    import yaml
    with open(evolution_path, 'w', encoding='utf-8') as f:
        yaml.dump(evolution_config, f, allow_unicode=True, default_flow_style=False)
    
    print(f"[OK] 已创建进化能力配置：config/evolution_config.yaml")
    
    # 更新 evolution.json
    evolution_json_path = SKILL_PATH / "evolution.json"
    if evolution_json_path.exists():
        import json
        with open(evolution_json_path, 'r', encoding='utf-8') as f:
            evol_data = json.load(f)
        
        evol_data['enabled'] = True
        evol_data['version'] = '2.0.0'
        
        with open(evolution_json_path, 'w', encoding='utf-8') as f:
            json.dump(evol_data, f, ensure_ascii=False, indent=2)
        
        print(f"[OK] 已更新 evolution.json")
    
    # ========== 4. 创建快速开始指南 ==========
    print("\n[4/4] 创建快速开始指南...")
    
    quickstart_content = '''# Skill Code Generator 快速开始指南

## 5 分钟创建你的第一个技能

### 步骤 1：准备环境

```bash
# 确保已安装 Leo Skills
pip install leo-skills

# 验证安装
python -c "from leo_skills import SkillCodeGenerator; print('OK')"
```

### 步骤 2：使用 Python API 创建

```python
from skill_code_generator_skill import SkillCodeGenerator

# 创建生成器
generator = SkillCodeGenerator()

# 方法 1：从自然语言描述创建
result = generator.execute(
    action="generate_from_prompt",
    prompt="创建一个天气 API 客户端技能，可以查询实时天气和预报"
)

# 查看生成的文件
print(f"技能路径：{result['skill_path']}")
print(f"创建文件：{result['files_created']}")
```

### 步骤 3：使用模板创建（推荐新手）

```python
# 查看可用模板
templates = generator.execute(action="list_templates")
print(templates['templates'])

# 使用 api-client 模板
result = generator.execute(
    action="generate_from_template",
    template="api-client",
    name="weather-api",
    description="天气 API 客户端",
    category="tools"
)
```

### 步骤 4：验证生成的技能

```python
# 验证技能目录
result = generator.execute(
    action="validate",
    skill_path="./weather-api_skill"
)

print(f"验证结果：{result['valid']}")
if result.get('errors'):
    print(f"错误：{result['errors']}")
if result.get('warnings'):
    print(f"建议：{result['warnings']}")
```

### 步骤 5：测试生成的技能

```bash
# 进入技能目录
cd weather-api_skill

# 运行测试
python -m pytest tests/ -v

# 或手动测试
python -c "from weather_api_skill import WeatherApiSkill; s=WeatherApiSkill(); print(s.execute(action='status'))"
```

## 常见用例

### 用例 1：创建数据处理技能

```python
result = generator.execute(
    action="generate_from_template",
    template="data-processor",
    name="csv-cleaner",
    description="CSV 数据清洗工具",
    features=[
        "读取 CSV 文件",
        "处理缺失值",
        "数据格式转换",
        "导出清洗后的数据"
    ]
)
```

### 用例 2：创建内容生成技能

```python
result = generator.execute(
    action="generate_from_prompt",
    prompt="创建一个博客文章生成技能，可以根据主题生成 SEO 优化的文章"
)
```

### 用例 3：批量创建技能

```python
skills_to_create = [
    {"name": "email-sender", "template": "automation"},
    {"name": "pdf-reader", "template": "file-handler"},
    {"name": "api-tester", "template": "api-client"},
]

for skill_config in skills_to_create:
    result = generator.execute(
        action="generate_from_template",
        **skill_config
    )
    print(f"✅ 创建 {skill_config['name']}: {result['skill_path']}")
```

## 自定义模板

在 `config/templates.yaml` 中定义你自己的模板：

```yaml
templates:
  my-custom-template:
    description: "我的自定义模板"
    extra_deps:
      - requests
      - pandas
    extra_files:
      - scripts/helper.py
      - templates/output.md
```

## 故障排除

### 问题 1：生成的技能无法导入

**解决**：
```bash
# 确保在技能目录的父目录
cd ..
python -c "from my_skill_skill import MySkillSkill; print('OK')"
```

### 问题 2：依赖安装失败

**解决**：
```bash
# 手动安装依赖
pip install requests pandas jinja2 pyyaml
```

### 问题 3：测试失败

**解决**：
```bash
# 查看详细错误
python -m pytest tests/ -v -s

# 检查 Python 版本
python --version  # 需要 3.8+
```

## 下一步

- 阅读 [skill-template.md](skill-template.md) 了解完整模板结构
- 查看 [best-practices.md](best-practices.md) 学习最佳实践
- 参考生成的技能代码，实现具体业务逻辑

---
*最后更新：2026-03-13*
'''
    
    quickstart_path = SKILL_PATH / "references" / "quickstart-guide.md"
    quickstart_path.parent.mkdir(parents=True, exist_ok=True)
    quickstart_path.write_text(quickstart_content, encoding='utf-8')
    print(f"[OK] 已创建快速开始指南：references/quickstart-guide.md")
    
    # ========== 总结 ==========
    print("\n" + "="*60)
    print("优化完成！")
    print("="*60)
    print("[OK] SKILL.md - 符合 Anthropic 标准，添加使用示例")
    print("[OK] 版本号 - 1.0.0 → 2.0.0")
    print("[OK] 进化能力 - 已配置并启用")
    print("[OK] 快速开始指南 - references/quickstart-guide.md")
    print("\n下一步：测试技能生成功能")
    print("="*60)


if __name__ == '__main__':
    optimize_skill()
