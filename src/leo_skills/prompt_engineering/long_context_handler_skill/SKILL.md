---
name: long-context-handler-skill
description: 优化长文本上下文处理,确保 AI 能够有效处理和理解大量文档内容。当用户需要提示词工程相关帮助时使用。 [优化第5轮：提升了触发准确率]
license: MIT
---

# Long Context Handler - 长文本上下文处理器

## 功能描述

这个技能帮助你优化长文本和多文档的处理方式,确保 AI 能够准确理解和提取关键信息,避免"上下文腐化"问题。

## 核心原理

### 上下文腐化 (Context Rot)

- 随着上下文长度增加,模型准确召回信息的能力会下降
- 每个新 token 都会消耗"注意力预算"
- 需要策略性地组织和呈现长文本内容

## 使用场景

- 处理多个长文档(每个 20K+ tokens)
- 从大量文本中提取特定信息
- 分析和总结长篇报告
- 比较多个文档的内容

## 最佳实践

### 1. 文档结构优化

#### 将长文本放在顶部

```
<documents>
[所有长文档内容放在这里]
</documents>

<query>
[你的问题和指令放在最后]
</query>
```

**效果**: 查询放在末尾可以将响应质量提高多达 30%

#### 使用 XML 标签结构化多文档

```xml
<documents>
  <document index="1">
    <source>文档来源/标题</source>
    <document_content>
      [文档 1 的完整内容]
    </document_content>
  </document>
  
  <document index="2">
    <source>文档来源/标题</source>
    <document_content>
      [文档 2 的完整内容]
    </document_content>
  </document>
</documents>

<instructions>
[你的分析指令]
</instructions>
```

### 2. 引用驱动的响应

对于长文档任务,要求 AI 先引用相关部分,再执行任务:

```
<instructions>
分析以下文档并回答问题。

步骤:
1. 首先,从文档中引用与问题相关的关键段落
2. 然后,基于这些引用提供你的分析

问题: [具体问题]
</instructions>
```

**好处**: 帮助 AI 穿透文档其余内容的"噪音",聚焦关键信息

### 3. 渐进式信息披露

对于超长文档,使用分步处理:

```
第一步: 提供文档概览和目录
第二步: 根据用户兴趣,深入特定章节
第三步: 提取和综合关键信息
```

## 使用模板

### 模板 1: 多文档分析

```
<documents>
  <document index="1">
    <source>{{DOCUMENT_1_SOURCE}}</source>
    <document_content>
      {{DOCUMENT_1_CONTENT}}
    </document_content>
  </document>
  
  <document index="2">
    <source>{{DOCUMENT_2_SOURCE}}</source>
    <document_content>
      {{DOCUMENT_2_CONTENT}}
    </document_content>
  </document>
</documents>

<task>
分析上述文档并完成以下任务:

1. 识别每个文档的主要观点
2. 比较文档之间的异同
3. 综合形成整体见解

输出格式:
- 每个文档的摘要(2-3 句话)
- 关键差异点列表
- 综合分析(1 段)

注意: 在分析时,请引用具体的文档段落来支持你的观点。
</task>
```

### 模板 2: 信息提取

```
<document>
  <source>{{SOURCE}}</source>
  <document_content>
    {{LONG_DOCUMENT_CONTENT}}
  </document_content>
</document>

<extraction_task>
从上述文档中提取以下信息:

目标信息:
- {{INFO_TYPE_1}}
- {{INFO_TYPE_2}}
- {{INFO_TYPE_3}}

处理步骤:
1. 首先,引用文档中包含相关信息的段落
2. 然后,以结构化格式提取信息
3. 如果某些信息在文档中未找到,明确说明

输出格式: JSON
</extraction_task>
```

### 模板 3: 文档问答

```
<context>
{{LONG_DOCUMENT_CONTENT}}
</context>

<instructions>
基于上述文档回答以下问题。

问题: {{QUESTION}}

回答要求:
1. 先引用文档中相关的原文段落(使用引号)
2. 基于引用的内容提供答案
3. 如果文档中没有足够信息回答问题,请明确说明

答案结构:
- 相关引用: [引用原文]
- 分析: [你的分析]
- 结论: [最终答案]
</instructions>
```

## 高级技巧

### 1. 分块处理策略

对于超长文档(100K+ tokens),考虑分块处理:

```python
# 伪代码示例
chunks = split_document(long_doc, chunk_size=20000)
summaries = []

for chunk in chunks:
    summary = process_chunk(chunk)
    summaries.append(summary)

final_result = synthesize_summaries(summaries)
```

### 2. 层次化摘要

```
第一层: 每个章节的摘要
第二层: 章节摘要的综合
第三层: 最终整体摘要
```

### 3. 关键词引导

在处理长文档前,先提取关键词:

```
步骤 1: 快速扫描文档,提取 10-15 个关键词
步骤 2: 使用这些关键词引导深入分析
步骤 3: 基于关键词定位相关段落
```

## 实际应用示例

### 示例 1: 合同分析

```xml
<contracts>
  <contract id="A">
    <source>供应商 A 合同</source>
    <document_content>
      [合同 A 全文]
    </document_content>
  </contract>
  
  <contract id="B">
    <source>供应商 B 合同</source>
    <document_content>
      [合同 B 全文]
    </document_content>
  </contract>
</contracts>

<analysis_task>
比较这两份合同,重点关注:
1. 价格条款
2. 交付时间
3. 违约责任
4. 付款条件

对于每个方面:
- 引用合同中的具体条款
- 比较两份合同的差异
- 提供建议

输出格式: 使用表格对比
</analysis_task>
```

### 示例 2: 研究论文综述

```xml
<papers>
  <paper index="1">
    <source>论文标题 1 (作者, 年份)</source>
    <document_content>[论文 1 全文]</document_content>
  </paper>
  
  <paper index="2">
    <source>论文标题 2 (作者, 年份)</source>
    <document_content>[论文 2 全文]</document_content>
  </paper>
  
  <paper index="3">
    <source>论文标题 3 (作者, 年份)</source>
    <document_content>[论文 3 全文]</document_content>
  </paper>
</papers>

<synthesis_task>
创建这些论文的综述,包括:

1. 每篇论文的核心贡献(引用关键段落)
2. 研究方法的比较
3. 主要发现的综合
4. 研究局限性
5. 未来研究方向

要求:
- 使用引用支持每个观点
- 识别论文之间的联系和矛盾
- 保持客观和学术性
</synthesis_task>
```

## 性能优化建议

### 1. 减少冗余

- 移除重复内容
- 只包含任务相关的部分
- 使用摘要代替完整文本(如果可能)

### 2. 结构化元数据

- 添加文档索引
- 包含来源信息
- 标注文档类型和日期

### 3. 明确优先级

```
<priority_sections>
重点关注以下部分:
1. [高优先级部分]
2. [中优先级部分]
3. [低优先级部分]
</priority_sections>
```

## 注意事项

1. **不要超载上下文**: 即使 Claude 支持 200K tokens,也要尽量精简
2. **测试和迭代**: 对于关键任务,先用较短文档测试提示词
3. **监控质量**: 注意 AI 是否准确引用和理解文档内容
4. **考虑替代方案**: 对于超长文档,考虑使用 RAG 或分块处理

## 相关资源

- [Long Context Tips](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/long-context-tips)
- [Effective Context Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)