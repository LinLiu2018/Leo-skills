# Skill 开发模板

## 标准结构

```
your-skill/
├── SKILL.md              # 技能定义（必需）
├── __init__.py           # 模块初始化
├── your_skill.py         # 主逻辑
├── scripts/
│   └── main.py          # 可执行脚本
├── references/
│   ├── api-guide.md     # API 文档
│   └── best-practices.md # 最佳实践
└── tests/
    └── test_skill.py    # 测试文件
```

## SKILL.md 模板

```yaml
---
name: your-skill-name
description: [做什么] + [何时使用] + [触发条件]
license: MIT
metadata:
  version: "1.0.0"
  category: [category]
  author: [author]
---

# Skill 名称

## 概述

简要描述技能功能。

## 使用方式

```python
from your_skill import YourSkill

skill = YourSkill()
result = skill.execute(param="value")
```

## 示例

### 示例 1：基本使用
[使用示例]

## 故障排除

[常见问题和解决方案]
```

## 开发检查清单

- [ ] SKILL.md 符合 Anthropic 标准
- [ ] name 使用 kebab-case
- [ ] description 包含触发条件
- [ ] 添加了 license
- [ ] 提供了使用示例
- [ ] 创建了 references/文档
- [ ] 编写了测试用例
