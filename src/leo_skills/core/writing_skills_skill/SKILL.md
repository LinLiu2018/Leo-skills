---
name: writing-skills-skill
description: Use when creating new skills, editing existing skills, or verifying skills work before deployment。当用户需要核心功能相关帮助时使用。 [优化第5轮：提升了触发准确率]
metadata:
  version: 1.1.0
  category: core
  author: Leo AI System (基于 obra/superpowers)
  activation_keywords:
  - 编写技能
  - 创建技能
  - 新增技能
  - writing-skills
  - skill creation
license: MIT
---

# 技能编写方法论（Writing Skills）

## 概述

**编写技能就是将 TDD 应用于流程文档。**

编写测试用例（子代理压力场景），观察失败（基线行为），编写技能（文档），
观察通过（代理遵守），重构（关闭漏洞）。

**核心理念**：如果你没有观察到代理在没有技能的情况下失败，你就不知道技能是否教了正确的东西。

## 什么是技能？

技能是经过验证的技术、模式或工具的参考指南。

**技能是**：可复用的技术、模式、工具、参考指南
**技能不是**：关于你如何解决某个问题的叙述

## TDD 映射

| TDD 概念 | 技能创建 |
|----------|---------|
| **测试用例** | 子代理压力场景 |
| **生产代码** | 技能文档 (SKILL.md) |
| **测试失败 (RED)** | 代理在没有技能时违反规则（基线） |
| **测试通过 (GREEN)** | 代理在有技能时遵守 |
| **重构** | 关闭漏洞同时保持合规 |

## 何时创建技能

**创建当**：
- 技术对你来说不是直觉上显而易见的
- 你会在不同项目中再次引用
- 模式广泛适用（非项目特定）
- 其他人会受益

**不要创建**：
- 一次性解决方案
- 其他地方有良好文档的标准实践
- 项目特定约定（放在 CLAUDE.md 中）

## SKILL.md 结构（Leo AI System 规范）

```yaml
---
name: {skill_name}
description: Use when creating new skills, editing existing skills, or verifying skills work before deployment。当用户需要核心功能相关帮助时使用。 [优化第5轮：提升了触发准确率]
metadata:
  version: "1.0.0"
  category: {category}
  author: Leo AI System
  activation_keywords: [keyword1, keyword2]
---
```

**Leo 系统命名规范**：
- 目录名：`{功能}_{类型}_skill`（snake_case）
- 禁止连字符 `-`、空格、大写字母

## 铁律（与 TDD 相同）

```
没有失败测试就没有技能
```

这适用于新技能和对现有技能的编辑。

## 技能创建检查清单

**RED 阶段 - 编写失败测试**：
- [ ] 创建压力场景（纪律技能需 3+ 组合压力）
- [ ] 在没有技能的情况下运行场景 - 逐字记录基线行为
- [ ] 识别合理化/失败中的模式

**GREEN 阶段 - 编写最小技能**：
- [ ] YAML frontmatter 包含完整字段
- [ ] description 以"Use when..."开头，包含具体触发条件
- [ ] 清晰的概述和核心原则
- [ ] 解决 RED 阶段识别的具体失败
- [ ] 使用技能运行场景 - 验证代理现在遵守

**REFACTOR 阶段 - 关闭漏洞**：
- [ ] 识别测试中的新合理化
- [ ] 添加明确的反驳（如果是纪律技能）
- [ ] 从所有测试迭代构建合理化表
- [ ] 重新测试直到防弹

## 相关技能

- **test_driven_development_skill** - TDD 基础（必需背景）
- **using_superpowers_skill** - 技能发现与调用

## 致谢

基于 [obra/superpowers](https://github.com/obra/superpowers) v4.2.0