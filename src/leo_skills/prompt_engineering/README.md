# Claude Prompt Engineering Skills

> 5 个基于 Claude 官方最佳实践的提示词工程技能

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📚 简介

这个仓库包含 5 个实用的提示词工程技能,帮助你掌握 Claude 提示词工程和上下文工程的最佳实践。所有技能都基于 [Claude 官方文档](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview)开发。

## 🎯 技能列表

| 技能名称 | 功能描述 | 适用场景 |
|---------|---------|---------|
| **[Prompt Optimizer](./prompt-optimizer/)** | 优化和改进提示词 | 提示词效果不佳,需要改进 |
| **[Long Context Handler](./long-context-handler/)** | 处理长文本和多文档 | 分析大量文档,提取关键信息 |
| **[XML Structure Builder](./xml-structure-builder/)** | 使用 XML 组织提示词 | 复杂任务需要清晰结构 |
| **[Chain of Thought Prompter](./chain-of-thought-prompter/)** | 引导结构化推理 | 需要逐步推理的复杂任务 |
| **[Prompt Chaining Orchestrator](./prompt-chaining-orchestrator/)** | 设计多步骤任务链 | 复杂任务需要分解为多个步骤 |

## 🚀 快速开始

### 安装

1. 克隆仓库:

```bash
git clone https://github.com/ponyodong2026/claude-prompt-engineering-skills.git
cd claude-prompt-engineering-skills
```

1. 将技能复制到你的 `.agent/skills/` 目录:

```bash
cp -r prompt-optimizer long-context-handler xml-structure-builder chain-of-thought-prompter prompt-chaining-orchestrator ~/.agent/skills/
```

### 使用

每个技能都包含一个 `SKILL.md` 文件,详细说明了:

- 功能描述
- 使用场景
- 核心技巧
- 使用模板
- 实际应用示例

查看技能文档:

```bash
cat prompt-optimizer/SKILL.md
```

## 📖 技能详解

### 1. Prompt Optimizer (提示词优化器)

**核心功能**: 分析并优化提示词,使其更明确、具体和有效

**核心技巧**:

- ✅ 明确性: 使用直接的动作动词
- ✅ 上下文: 解释为什么任务重要
- ✅ 具体性: 添加明确的约束和要求
- ✅ 示例: 展示期望的格式和风格
- ✅ 结构化: 使用标签组织内容

**示例**:

```
❌ 优化前: "帮我写一篇关于 AI 的文章"

✅ 优化后:
<context>
为科技博客撰写面向普通读者的文章,介绍 AI 在日常生活中的应用。
</context>

<instructions>
撰写一篇关于 AI 在日常生活中应用的科普文章。
要求:
- 字数: 800-1000 字
- 语气: 通俗易懂
- 结构: 引言 + 3-4 个应用场景 + 总结
</instructions>
```

### 2. Long Context Handler (长文本上下文处理器)

**核心功能**: 优化长文本和多文档处理,避免"上下文腐化"

**关键技巧**:

- 📍 文档置顶: 长文本放在提示词顶部,查询放在最后 (提升 30% 质量)
- 🏷️ XML 结构化: 使用 `<document>`, `<source>`, `<document_content>` 标签
- 📝 引用驱动: 要求 AI 先引用相关段落,再提供分析

### 3. XML Structure Builder (XML 结构化构建器)

**核心功能**: 使用 XML 标签组织提示词,提高清晰度和可维护性

**四大优势**:

- 🎯 清晰度: 清楚地分离提示的不同部分
- ✅ 准确性: 减少 AI 误解的可能性
- 🔧 灵活性: 轻松修改和维护
- 📊 可解析性: 便于程序化处理

### 4. Chain of Thought Prompter (思维链提示器)

**核心功能**: 引导 AI 进行逐步推理,提高复杂任务准确性

**三种实现方式**:

1. **基础思维链**: 添加"逐步思考"
2. **引导式思维链**: 提供具体推理步骤
3. **结构化思维链**: 使用 `<thinking>` 和 `<answer>` 标签分隔

### 5. Prompt Chaining Orchestrator (提示词链编排器)

**核心功能**: 将复杂任务分解为多个顺序步骤,提高准确性

**常见模式**:

- 🔄 生成-评估-改进: 创意任务、内容生成
- 🧩 分解-处理-聚合: 复杂分析、大规模处理
- 📊 提取-分析-综合: 数据分析、研究任务
- 📋 规划-执行-验证: 问题解决、项目管理

## 🔧 技能组合使用

### 组合 1: 长文档分析

```
1. XML Structure Builder → 组织多个文档
2. Long Context Handler → 优化文档结构
3. Chain of Thought → 引导分析过程
```

### 组合 2: 复杂内容创作

```
1. Prompt Chaining → 分解任务
2. XML Structure Builder → 组织输入输出
3. Prompt Optimizer → 优化每个步骤
```

### 组合 3: 数据分析报告

```
1. Prompt Chaining → 设计分析流程
2. Chain of Thought → 引导推理
3. XML Structure Builder → 结构化输出
```

## 💡 核心要点

### 提示词工程核心原则

1. ✅ **明确 > 含蓄**: 直接说明你想要什么
2. ✅ **上下文很重要**: 解释为什么,不仅仅是什么
3. ✅ **具体胜过模糊**: 提供清晰的约束和期望
4. ✅ **示例强大**: 展示而非仅仅告诉
5. ✅ **允许不确定性**: 减少幻觉

### Claude 4.x 特定要点

1. ✅ **更明确的指令**: 明确请求"超越"行为
2. ✅ **示例细节敏感**: 确保示例对齐期望行为
3. ✅ **强大的研究能力**: 使用结构化方法进行复杂研究
4. ✅ **原生子代理编排**: 自动识别何时委托
5. ✅ **思维能力**: 利用扩展思维和交错思维

## 📚 学习资源

### 官方文档

- [Prompt Engineering Best Practices](https://claude.com/blog/best-practices-for-prompt-engineering)
- [Effective Context Engineering for AI Agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Claude 4 Best Practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-4-best-practices)
- [Use XML Tags](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/use-xml-tags)
- [Long Context Tips](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/long-context-tips)

## 🎓 学习路径

### 初学者

1. 从 **Prompt Optimizer** 开始,学习基础优化技巧
2. 练习使用 **XML Structure Builder** 组织提示词
3. 尝试 **Chain of Thought** 解决简单推理问题

### 中级用户

1. 掌握 **Long Context Handler** 处理复杂文档
2. 学习 **Prompt Chaining** 设计多步骤任务
3. 组合使用多个技能解决实际问题

### 高级用户

1. 根据具体场景定制技能
2. 开发自己的提示词模板库
3. 自动化提示词链的执行

## 🤝 贡献

欢迎贡献!如果你有改进建议或新的技能想法:

1. Fork 这个仓库
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启一个 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📧 联系方式

如有问题或建议,请通过 GitHub Issues 联系我们。

## 🙏 致谢

- 感谢 [Anthropic](https://www.anthropic.com/) 提供的优秀文档和最佳实践
- 感谢所有为提示词工程做出贡献的开发者和研究者

---

**祝你在提示词工程的旅程中取得成功! 🚀**
