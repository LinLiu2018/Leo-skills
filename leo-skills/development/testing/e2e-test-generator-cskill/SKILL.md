# E2E测试生成器 Skill

## 技能描述

生成端到端测试代码，支持Playwright和Cypress。

## 激活词

- "生成E2E测试"
- "创建端到端测试"
- "自动化测试"

## 输入参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| test_name | string | 是 | 测试名称 |
| user_flows | list | 是 | 用户流程列表 |
| base_url | string | 否 | 基础URL |
| framework | string | 否 | 测试框架（playwright/cypress） |

## 支持的操作

| 操作 | 说明 |
|------|------|
| goto | 访问页面 |
| click | 点击元素 |
| fill | 填写输入框 |
| select | 选择下拉选项 |
| wait | 等待元素 |
| assert_text | 断言文本 |
| assert_visible | 断言可见 |

## 版本

- 版本: 1.0.0
- 作者: Leo Liu
