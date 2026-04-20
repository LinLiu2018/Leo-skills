---
name: weui-miniprogram-skill
description: Weui Miniprogram Skill 技能。当用户需要相关帮助时使用。 [优化第5轮：提升了触发准确率]
license: MIT
---

# WeUI Miniprogram Skill (微信官方小程序组件库技能)

## 技能描述

基于微信官方 WeUI Miniprogram (2.4k stars) 的小程序 UI 组件生成技能。提供与微信原生视觉体验一致的组件。

## 核心能力

- **官方组件**: 微信官方设计团队出品，视觉体验与微信原生一致
- **深色模式**: 内置 DarkMode 适配支持
- **组件生成**: 快速生成符合微信设计规范的组件代码
- **最佳实践**: 内置微信官方推荐的使用方式

## 支持的组件

| 分类 | 组件 |
|------|------|
| 表单 | Form, Input, Textarea, Checkbox, Radio, Switch, Slider, Uploader |
| 基础 | Button, Cell, Badge, Loading, Progress |
| 操作反馈 | ActionSheet, Dialog, HalfScreenDialog, Msg, Toast, TopTips |
| 导航 | Navigation, Tabbar |
| 搜索 | SearchBar |
| 其他 | Gallery, Preview |

## 使用方法

```python
from weui_miniprogram_skill import WeuiMiniprogramSkill

skill = WeuiMiniprogramSkill()

# 生成按钮组件
result = skill.execute(
    action="generate_component",
    component="button",
    props={"type": "primary", "text": "确定"}
)

# 生成带深色模式的组件
result = skill.execute(
    action="generate_component",
    component="cell",
    dark_mode=True
)
```

## 安装到小程序

```bash
npm install weui-miniprogram
```

## 参考资源

- GitHub: https://github.com/wechat-miniprogram/weui-miniprogram
- 文档: https://wechat-miniprogram.github.io/weui/docs/
- Stars: 2.4k

## 进化机制

本技能支持自我进化：
- 学习用户常用的组件组合
- 优化深色模式适配
- 记录成功的设计模式
