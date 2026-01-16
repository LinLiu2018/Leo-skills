# 微信小程序页面生成器 Skill

## 技能描述

自动生成微信小程序页面代码，包括WXML、WXSS、JS和JSON配置文件。

## 激活词

- "生成小程序页面"
- "创建小程序页面"
- "miniprogram page"
- "小程序页面"

## 输入参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page_name | string | 是 | 页面名称（如：index, form, result） |
| page_type | string | 否 | 页面类型（form/list/detail/share） |
| data_bindings | list | 否 | 数据绑定字段 |
| api_endpoints | list | 否 | 需要调用的API |
| features | list | 否 | 特性（分享/下拉刷新等） |

## 输出

- `pages/{page_name}/{page_name}.wxml` - 页面结构
- `pages/{page_name}/{page_name}.wxss` - 页面样式
- `pages/{page_name}/{page_name}.js` - 页面逻辑
- `pages/{page_name}/{page_name}.json` - 页面配置

## 使用示例

### 示例1：生成表单页面

```
生成小程序页面，页面名称：form
类型：form
字段：
- name: 姓名，输入框
- phone: 手机号，输入框
- demand: 需求，下拉选择
提交API：/api/leads
```

### 示例2：生成分享结果页

```
生成小程序页面，页面名称：result
类型：share
特性：分享到好友、生成海报
数据：优惠券信息、邀请链接
```

## 支持的页面类型

| 类型 | 说明 | 包含组件 |
|------|------|----------|
| form | 表单页 | 输入框、选择器、提交按钮 |
| list | 列表页 | 列表、下拉刷新、加载更多 |
| detail | 详情页 | 数据展示、操作按钮 |
| share | 分享页 | 分享按钮、海报生成 |

## 版本

- 版本: 1.0.0
- 作者: Leo Liu
- 更新: 2026-01-12
