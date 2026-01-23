# Content Layout Leo CSkill

**智能内容排版技能 by Leo** - 支持微信公众号、小红书、微博、博客等多平台智能排版

## 功能特性

✅ **10种房产类优质排版风格**
- 数据驱动型（真叫卢俊风格）
- 故事叙述型（米宅风格）
- 极简专业型（层楼风格）
- 活力吸睛型（大V风格）
- 情感共鸣型（暖心风格）
- 清单列表型（实用风格）
- 对比分析型（分析风格）
- 案例解读型（深度风格）
- 问答互动型（社群风格）
- 杂志排版型（高端风格）

✅ **智能图片匹配**
- AI分析内容自动匹配合适图片
- 生成AI图片提示词
- 支持多种图片类型

✅ **多平台支持**
- 微信公众号（HTML格式）
- 小红书（emoji丰富文本）
- 微博、博客（Markdown格式）

✅ **智能优化**
- 自动emoji插入
- 金句提取高亮
- 色彩方案配置
- 字体大小优化

## 快速开始

```bash
# 基础使用
python scripts/main.py -p wechat -s data_driven -i input.md -o output.html

# 小红书格式
python scripts/main.py -p xiaohongshu -i input.md -o output.txt

# 生成图片提示词
python scripts/main.py -p wechat -i input.md --images
```

## 10种风格速览

| 风格 | 特点 | 适用场景 |
|------|------|----------|
| data_driven | 数据驱动、图表丰富 | 市场分析、政策解读 |
| story_telling | 故事化、情感共鸣 | 市场观察、购房故事 |
| minimalist_professional | 极简专业、高端大气 | 高端项目、豪宅推广 |
| vibrant_attention | 色彩鲜明、视觉冲击 | 爆款文章、热点话题 |
| emotional_resonance | 温暖亲切、情感化 | 购房者故事、家园情怀 |
| listicle_practical | 清单式、条理清晰 | 购房攻略、干货分享 |
| comparison_analysis | 对比鲜明、优缺点清晰 | 项目对比、区域分析 |
| case_study_deep | 深度剖析、图文并茂 | 项目深度解读 |
| qa_interactive | 问答形式、互动性强 | 知识科普、购房咨询 |
| magazine_premium | 杂志质感、精美排版 | 高端项目、品牌形象 |

## 作为 Claude Code 技能使用

配置到技能路径后，使用激活词：
- "帮我排版这篇文章"
- "生成公众号格式"
- "转为小红书格式"
- "添加配图"
- "优化文章排版"

## 项目信息

- **版本**: 1.0.0
- **类型**: Simple Skill
- **创建者**: Leo Liu

---

**Created with Agent-Skill-Creator v2.1**
