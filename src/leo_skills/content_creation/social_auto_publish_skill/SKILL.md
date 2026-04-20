---
name: social-auto-publish
description: 多平台内容自动发布技能，支持抖音、视频号、小红书、闲鱼等平台。当用户需要内容创作生成相关帮助时使用。 [优化第5轮：提升了触发准确率]
compatibility: '>=1.0.0'
license: MIT
metadata:
  version: 1.0.0
  category: content_creation
  author: Leo AI System
  platforms:
  - douyin
  - shipinhao
  - xiaohongshu
  - xianyu
  - kuaishou
  - bilibili
  upstream: https://github.com/dreammis/social-auto-upload
---

# Social Auto Publish Skill - 多平台自动发布技能

## 概述

基于 [social-auto-upload](https://github.com/dreammis/social-auto-upload) 集成的多平台内容自动发布技能。
使用 Playwright 浏览器自动化，无需官方 API，直接模拟用户操作完成内容发布。

## 支持平台

| 平台 | 类型 | 状态 |
|------|------|------|
| 抖音 | 短视频 | ✅ 已集成 |
| 视频号 | 短视频 | ✅ 已集成 |
| 小红书 | 图文/视频 | ✅ 已集成 |
| 快手 | 短视频 | ✅ 已集成 |
| B站 | 视频 | ✅ 已集成 |
| 闲鱼 | 商品/图文 | 🔧 待开发 |

## 核心功能

1. **一键多平台发布**: 一份内容自动适配并发布到多个平台
2. **内容适配引擎**: 根据平台特性自动调整标题、文案、标签
3. **定时发布**: 支持 cron 定时任务，自动在最佳时间发布
4. **Cookie 管理**: 自动管理各平台登录状态
5. **发布日志**: 记录每次发布结果，支持失败重试

## 工作流程

```
素材准备 → 内容适配 → 平台登录检查 → 自动上传 → 结果记录
   ↑                                              ↓
   └──────────── 失败重试 ←─────────────────────────┘
```

## 平台内容适配规则

| 平台 | 标题限制 | 文案风格 | 标签策略 |
|------|---------|---------|---------|
| 抖音 | 30字内 | 钩子开头+悬念 | #话题 3-5个 |
| 视频号 | 20字内 | 信任感+深度 | #话题 2-3个 |
| 小红书 | 20字内 | 种草+emoji | #标签 5-10个 |
| 闲鱼 | 30字内 | 直给+价格 | 关键词堆叠 |

## 使用方式

```python
from social_auto_publish_skill import SocialAutoPublisher

publisher = SocialAutoPublisher(config_path="config/config.yaml")

# 发布视频到所有平台
publisher.publish_video(
    video_path="videos/villa_tour.mp4",
    title="宁波度假别墅实拍",
    description="牟山湖畔，推窗见山...",
    tags=["宁波别墅", "度假养老", "牟山"],
    platforms=["douyin", "shipinhao", "xiaohongshu"]
)

# 发布图文到小红书
publisher.publish_note(
    images=["img1.jpg", "img2.jpg"],
    title="宁波周边别墅推荐",
    content="周末去看了几个盘...",
    platform="xiaohongshu"
)
```

## 依赖

- playwright >= 1.40.0
- social-auto-upload (参考实现: docs/reference/social-auto-upload/)

## 配置

见 `config/config.yaml`