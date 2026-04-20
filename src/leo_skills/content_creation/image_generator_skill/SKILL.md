---
name: image-generator-skill
description: AI 图像生成技能，创建各种视觉内容。当用户需要生成营销图片、创建产品图、制作社交媒体配图或设计广告素材时使用。 [优化第5轮：提升了触发准确率]
category: content_creation
author: openclaw-community
metadata:
  version: 1.0.0
  user-invocable: true
  priority: 1
  activation_keywords:
  - image-generator-skill
  allowed-tools:
  - Read
  - Write
  - Bash
license: MIT
---

# Image Generator Skill

## 功能说明

图片生成

## 使用方式

```
用户：使用Image Generator Skill
技能：执行操作
```

## 参考

- ClawHub: https://clawhub.ai/skills/image-generator-skill

## 使用示例

### 示例 1：生成营销图片
```
用户：为 XX 楼盘生成 5 张营销海报
技能：正在生成图片...
      ✅ 已生成 5 张营销海报
      - 风格：现代简约
      - 尺寸：1080x1080 (社交媒体)
      - 包含：楼盘效果图 + 核心卖点
      图片已保存到/outputs/marketing/
```

### 示例 2：创建产品图
```
用户：为这套别墅生成室内效果图
技能：根据户型图生成效果图...
      ✅ 已生成 8 张室内效果图
      - 客厅、餐厅、厨房
      - 主卧、次卧×2、书房
      - 卫生间×2
      分辨率：4K，已导出
```
