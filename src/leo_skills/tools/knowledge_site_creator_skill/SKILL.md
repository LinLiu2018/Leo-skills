---
name: knowledge-site-creator-skill
description: 知识学习网站创建技能。一句话生成知识学习网站，支持词根记忆、历史脉络、设计原则等主题。。当用户需要工具集成相关帮助时使用。 [优化第5轮：提升了触发准确率]
category: tools
author: joeseesun (集成：Leo Liu)
metadata:
  version: 1.0.0
  user-invocable: true
  priority: 0
  activation_keywords:
  - 知识网站
  - 学习网站
  - knowledge site
  - 词根记忆
  - 历史脉络
  allowed-tools:
  - Web Fetch
  - Web Search
  - Write
license: MIT
---

# Knowledge Site Creator Skill

## 功能

- 词根词缀英语单词记忆网站
- 历史脉络学习网站
- 设计原则学习网站
- AI 核心概念速览网站

## 演示网站

1. **词根记忆**: https://word.qiaomu.ai
2. **五代十国**: https://wudai.qiaomu.ai
3. **设计原则**: https://designrule.qiaomu.ai
4. **AI 概念**: https://llmwords.qiaomu.ai

## 使用方式

```
用户：创建一个词根记忆网站
技能：生成网站结构 → 填充内容 → 输出部署
```

## 参考

- GitHub: https://github.com/joeseesun/knowledge-site-creator
- 安装：`npx skills add joeseesun/knowledge-site-creator`