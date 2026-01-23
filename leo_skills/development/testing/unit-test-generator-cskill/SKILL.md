# 单元测试生成器 Skill

## 技能描述

自动分析源代码并生成单元测试，支持Python和JavaScript/TypeScript。

## 激活词

- "生成测试"
- "创建单元测试"
- "写测试用例"

## 输入参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| source_code | string | 是 | 源代码 |
| language | string | 否 | 语言（python/javascript） |
| test_framework | string | 否 | 测试框架（pytest/unittest/vitest/jest） |

## 支持的框架

| 语言 | 框架 |
|------|------|
| Python | pytest, unittest |
| JavaScript/TypeScript | vitest, jest |

## 输出

- `test_*.py` 或 `*.spec.ts` - 测试文件
- `conftest.py` - pytest配置（Python）

## 使用示例

```
生成测试
语言：Python
框架：pytest
源代码：[粘贴代码]
```

## 版本

- 版本: 1.0.0
- 作者: Leo Liu
- 更新: 2026-01-14
