# Instincts Skill

## 简介

`instincts_skill` - AI Agent本能系统

参考 ECC 的 Instincts 设计，为Leo AI系统提供模式匹配自动触发机制。

## 功能

- 模式识别与自动触发
- 条件执行规则
- 上下文自动注入
- 行为建议生成
- 学习与适应

## 核心概念

### Instinct（本能）
一种自动触发的行为规则，包含：
- **Trigger**: 触发条件（正则/关键词/语义）
- **Action**: 执行的技能或行为
- **Evidence**: 支撑证据（为什么触发）
- **Examples**: 历史案例

### 预设本能示例

| 本能 | 触发条件 | 自动行为 |
|------|----------|----------|
| bug_finder | "bug", "报错", "错误" | 触发systematic_debugging_skill |
| security_guard | "密码", "token", "key" | 触发security_scan |
| refactor_trigger | "重构", "优化", "refactor" | 触发代码审查 |
| doc_generator | "文档", "注释", "doc" | 触发文档生成 |
| test_runner | "测试", "test", "测一下" | 运行测试套件 |

## 使用方式

```
/instincts list              # 列出所有本能
/instincts show <name>      # 查看本能详情
/instincts trigger <input>  # 测试触发
/instincts learn            # 从历史学习新本能
```

## 分类

core