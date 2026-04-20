---
name: skill-vetter-skill
description: 技能安全扫描器。扫描技能代码中的危险操作，检查网络请求、文件访问、系统命令，生成安全评分报告。。当用户需要工具集成相关帮助时使用。 [优化第5轮：提升了触发准确率]
category: tools
author: Leo Liu
metadata:
  version: 1.0.0
  user-invocable: true
  priority: 0
  activation_keywords:
  - 技能扫描
  - 安全检查
  - vet skill
  - 扫描技能
  - 安全评估
  allowed-tools:
  - Read
  - Bash
license: MIT
---

# Skill Vetter Skill - 技能安全扫描器

## 功能说明

在安装或运行任何技能之前，先使用此技能进行安全扫描。

## 扫描内容

1. **危险函数检测**: eval(), exec(), system(), subprocess 等
2. **网络请求检测**: requests, urllib, http 客户端
3. **文件访问检测**: 读写敏感目录
4. **系统命令检测**: os.system, subprocess.call 等
5. **权限评估**: 需要的系统权限级别

## 安全评分

| 等级 | 分数 | 说明 |
|------|------|------|
| 🟢 安全 | 90-100 | 无危险操作，可放心使用 |
| 🟡 注意 | 60-89 | 有中等风险操作，需审查 |
| 🔴 危险 | 0-59 | 有高危操作，禁止使用 |

## 使用方式

```
用户：扫描这个技能是否安全
技能：分析代码 → 检测危险操作 → 生成评分 → 给出建议
```