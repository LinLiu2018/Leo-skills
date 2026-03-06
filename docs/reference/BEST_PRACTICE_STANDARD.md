# Leo AI System 最佳实践规范

> 本规范定义了 Leo AI System 项目的文件命名、目录结构、代码风格等最佳实践。

---

## 1. 目录结构规范

### 1.1 项目根目录

```
leo_ai_system/
├── .claude/          # Claude Code 配置
├── src/               # 源代码
│   └── leo_*/       # 功能模块
├── projects/          # 项目文件
│   ├── active/       # 活跃项目
│   └── archive/      # 归档项目
├── docs/             # 文档
│   ├── guides/       # 操作指南
│   ├── planning/     # 规划文档
│   ├── reference/    # 参考文档
│   └── research/     # 研究发现
├── scripts/           # 脚本
├── tests/             # 测试
├── config/            # 配置
├── data/             # 数据
└── leo_knowledge/   # 知识库
```

### 1.2 技能目录结构 (src/leo_skills/)

```
src/leo_skills/
├── {category}/
│   ├── {skill_name}/
│   │   ├── SKILL.md          # 技能定义 (必须)
│   │   ├── {skill_name}.py   # 技能实现
│   │   ├── __init__.py
│   │   ├── config/           # 配置
│   │   ├── scripts/         # 脚本
│   │   ├── templates/        # 模板
│   │   └── tests/           # 测试
│   └── ...
├── ...
```

---

## 2. 文件命名规范

### 2.1 目录命名

| 类型 | 规范 | 示例 |
|------|------|------|
| 技能目录 | `{skill_name}_skill/` | `agent_skill_creator_skill/` |
| 类别目录 | snake_case | `content_creation/` |
| 模块目录 | snake_case | `leo_skills/` |

### 2.2 文件命名

| 类型 | 规范 | 示例 |
|------|------|------|
| 技能入口 | `{skill_name}.py` | `agent_skill_creator_skill.py` |
| 技能定义 | `SKILL.md` | `SKILL.md` |
| 初始化 | `__init__.py` | `__init__.py` |
| 配置 | `config.yaml` | `config.yaml` |
| 测试 | `test_{name}.py` | `test_agent.py` |
| 模板 | `{name}.j2` | `dockerfile.j2` |

### 2.3 禁止的命名

- ❌ 中文文件名
- ❌ 空格
- ❌ 大写字母（除常量）
- ❌ 特殊字符（`_` `-` 除外）

---

## 3. SKILL.md 规范

### 3.1 必须的 Frontmatter

```yaml
---
name: skill_name
description: 技能简短描述
---
```

### 3.2 技能结构模板

```markdown
# Skill Name

技能详细描述。

## When to Use This Skill

触发条件说明。

## Features

- 特性1
- 特性2

## Usage

```bash
# 使用示例
```

## Configuration

配置说明。

## Dependencies

- 依赖1
- 依赖2
```

---

## 4. Python 代码规范

### 4.1 导入顺序

```python
# 1. 标准库
import os
import sys
from typing import Optional

# 2. 第三方库
import requests
from loguru import logger

# 3. 本地模块
from src.leo_skills.base import BaseSkill
```

### 4.2 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 函数 | snake_case | `def get_user_info():` |
| 类 | PascalCase | `class UserService:` |
| 常量 | UPPER_SNAKE | `MAX_RETRIES = 3` |
| 私有变量 | `_private_var` | `_cache = {}` |

### 4.3 类型注解

```python
def process_user(user_id: int, name: str) -> dict[str, Any]:
    """处理用户信息"""
    return {"id": user_id, "name": name}
```

---

## 5. 配置文件规范

### 5.1 config/ 目录

```
config/
├── keywords/          # 关键词配置
├── models/            # 模型配置
├── security/          # 安全配置
└── settings.yaml     # 主配置
```

### 5.2 YAML 格式

```yaml
skill:
  name: "example"
  version: "1.0.0"
  enabled: true

settings:
  timeout: 30
  retries: 3
```

---

## 6. 文档规范

### 6.1 README.md

```markdown
# Skill Name

简短描述。

## 功能特性

- 特性1
- 特性2

## 快速开始

```bash
# 安装
pip install xxx

# 使用
xxx --help
```

## 配置

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| xxx | str | - | xxx |

## 依赖

- package1
- package2
```

### 6.2 CHANGELOG.md

```markdown
# Changelog

## [版本] - 日期

### 新增
- xxx

### 修改
- xxx

### 修复
- xxx
```

---

## 7. Git 规范

### 7.1 提交信息

```
feat: 添加新功能
fix: 修复问题
docs: 文档更新
refactor: 重构
test: 测试
chore: 其他
```

### 7.2 分支命名

```
feature/功能名
fix/问题描述
refactor/模块名
docs/文档类型
```

---

## 8. 自动清理规则

### 8.1 定期清理

| 类型 | 位置 | 清理条件 |
|------|------|---------|
| __pycache__ | 所有目录 | 每次构建前 |
| .pyc | 所有目录 | 每次构建前 |
| node_modules | 项目目录 | 删除后重建 |
| .pytest_cache | tests/ | 每次测试后 |
| *.log | logs/ | 大于 10MB |

### 8.2 构建时清理

```bash
# 清理 Python 缓存
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# 清理测试缓存
rm -rf .pytest_cache
rm -rf htmlcov/
rm -rf .coverage
```

### 8.3 禁止提交

```
*.log
*.pyc
__pycache__/
node_modules/
.env
.DS_Store
*.swp
*.swo
*~
```

---

## 9. 测试规范

### 9.1 测试文件位置

```
src/leo_skills/{skill}/
├── tests/
│   ├── __init__.py
│   ├── test_skill.py      # 单元测试
│   └── test_integration.py # 集成测试
```

### 9.2 测试命名

```python
def test_skill_initialization():
    """测试技能初始化"""

def test_skill_execution():
    """测试技能执行"""
```

---

## 10. 最佳实践清单

### 10.1 新建技能检查

- [ ] 遵循目录结构
- [ ] 使用正确的命名规范
- [ ] 创建 SKILL.md
- [ ] 添加类型注解
- [ ] 编写测试用例
- [ ] 更新 CHANGELOG.md
- [ ] 添加到 skill_registry.json

### 10.2 代码审查检查

- [ ] 无硬编码密码
- [ ] 有适当的错误处理
- [ ] 有日志记录
- [ ] 有类型注解
- [ ] 单元测试通过

### 10.3 提交前检查

- [ ] 清理临时文件
- [ ] 无 __pycache__
- [ ] 无 .pyc 文件
- [ ] 无大日志文件
- [ ] git status 检查

---

> 最后更新: 2026-03-05
