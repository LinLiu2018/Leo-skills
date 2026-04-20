---
name: vue-page-generator-skill
description: Vue Page Generator Skill 技能。当用户需要相关帮助时使用。 [优化第5轮：提升了触发准确率]
license: MIT
---

# Vue页面生成器 Skill

## 技能描述

生成完整的Vue3页面，包含路由配置和Store模块。

## 激活词

- "生成Vue页面"
- "创建Vue页面"
- "Vue页面"

## 输入参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page_name | string | 是 | 页面名称 |
| layout_type | string | 否 | 布局类型(default/sidebar/dashboard) |
| api_endpoints | list | 否 | API端点列表 |
| features | list | 否 | 功能特性(store等) |

## 输出

- Vue页面组件(.vue)
- TypeScript类型定义
- 路由配置
- Pinia Store模块(可选)

## 版本

- 版本: 1.0.0
- 作者: Leo Liu
