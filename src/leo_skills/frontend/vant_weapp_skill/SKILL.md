# Vant Weapp Skill (小程序UI组件库技能)

## 技能描述

基于有赞 Vant Weapp (18.3k stars) 的小程序 UI 组件生成技能。支持快速生成符合微信设计规范的小程序页面和组件。

## 核心能力

- **组件生成**: 快速生成 80+ 种 UI 组件代码
- **页面模板**: 提供常用页面模板（首页、列表页、详情页、个人中心等）
- **主题定制**: 支持自定义主题色和样式变量
- **最佳实践**: 内置组件使用最佳实践和示例

## 支持的组件分类

| 分类 | 组件 |
|------|------|
| 基础组件 | Button, Cell, Icon, Image, Layout, Popup, Toast |
| 表单组件 | Checkbox, DatetimePicker, Field, Picker, Radio, Rate, Search, Slider, Stepper, Switch, Uploader |
| 反馈组件 | ActionSheet, Dialog, DropdownMenu, Loading, Notify, Overlay, ShareSheet, SwipeCell |
| 展示组件 | Badge, Card, Collapse, CountDown, Divider, Empty, NoticeBar, Panel, Progress, Skeleton, Steps, Sticky, Tag |
| 导航组件 | Grid, IndexBar, NavBar, Sidebar, Tab, Tabbar, TreeSelect |
| 业务组件 | Area, Calendar, Card, GoodsAction, SubmitBar |

## 使用方法

```python
from vant_weapp_skill import VantWeappSkill

skill = VantWeappSkill()

# 生成按钮组件
result = skill.execute(
    action="generate_component",
    component="button",
    props={"type": "primary", "text": "立即领取"}
)

# 生成完整页面
result = skill.execute(
    action="generate_page",
    template="gift-list",
    theme_color="#FF6B35"
)

# 获取组件使用示例
result = skill.execute(
    action="get_example",
    component="card"
)
```

## 安装到小程序

```bash
# 在小程序项目中安装
npm i @vant/weapp -S --production
```

## 参考资源

- GitHub: https://github.com/vant-ui/vant-weapp
- 文档: https://vant-contrib.gitee.io/vant-weapp/
- Stars: 18.3k

## 进化机制

本技能支持自我进化：
- 学习用户常用的组件组合
- 优化页面模板生成质量
- 记录成功的设计模式
