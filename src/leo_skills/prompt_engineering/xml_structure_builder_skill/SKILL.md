---
name: xml-structure-builder-skill
description: 使用 XML 标签结构化提示词,提高清晰度、准确性和可维护性。当用户需要提示词工程相关帮助时使用。 [优化第5轮：提升了触发准确率]
license: MIT
---

# XML Structure Builder - XML 结构化构建器

## 功能描述

这个技能帮助你使用 XML 标签来组织和结构化提示词,使其更清晰、更易于维护,并减少 AI 误解的可能性。

## 为什么使用 XML 标签?

### 四大优势

1. **清晰度 (Clarity)**: 清楚地分离提示的不同部分,确保结构良好
2. **准确性 (Accuracy)**: 减少 Claude 误解提示部分导致的错误
3. **灵活性 (Flexibility)**: 轻松查找、添加、删除或修改部分,无需重写
4. **可解析性 (Parseability)**: 让 Claude 在输出中使用 XML 标签,便于后处理提取

## 核心原则

### 1. 保持一致性

在整个提示中使用相同的标签名称,并在引用内容时使用这些标签名。

```
使用 <contract> 标签中的合同信息...
基于 <user_profile> 中的用户资料...
```

### 2. 嵌套标签

对层次化内容使用嵌套标签:

```xml
<outer>
  <inner>
    内容
  </inner>
</outer>
```

### 3. 语义化命名

使用描述性的标签名称,让人一眼就能理解内容:

```xml
✅ 好的命名:
<user_profile>
<product_description>
<analysis_instructions>

❌ 不好的命名:
<data>
<info>
<stuff>
```

## 常用标签模式

### 1. 基础结构标签

```xml
<context>
  背景信息和上下文
</context>

<instructions>
  具体的任务指令
</instructions>

<examples>
  示例内容
</examples>

<output_format>
  期望的输出格式
</output_format>
```

### 2. 数据标签

```xml
<document>
  <source>文档来源</source>
  <content>
    文档内容
  </content>
</document>

<user_data>
  <name>用户名</name>
  <preferences>用户偏好</preferences>
  <history>历史记录</history>
</user_data>
```

### 3. 推理标签

```xml
<thinking>
  思考过程
</thinking>

<analysis>
  分析内容
</analysis>

<answer>
  最终答案
</answer>
```

## 使用模板

### 模板 1: 基础任务结构

```xml
<context>
{{BACKGROUND_INFORMATION}}
</context>

<task>
{{TASK_DESCRIPTION}}
</task>

<requirements>
- {{REQUIREMENT_1}}
- {{REQUIREMENT_2}}
- {{REQUIREMENT_3}}
</requirements>

<output_format>
{{DESIRED_FORMAT}}
</output_format>
```

### 模板 2: 多文档处理

```xml
<documents>
  <document index="1">
    <source>{{SOURCE_1}}</source>
    <document_content>
      {{CONTENT_1}}
    </document_content>
  </document>
  
  <document index="2">
    <source>{{SOURCE_2}}</source>
    <document_content>
      {{CONTENT_2}}
    </document_content>
  </document>
</documents>

<query>
{{YOUR_QUESTION}}
</query>

<instructions>
{{PROCESSING_INSTRUCTIONS}}
</instructions>
```

### 模板 3: 分析任务

```xml
<input_data>
{{DATA_TO_ANALYZE}}
</input_data>

<analysis_framework>
  <aspect name="{{ASPECT_1}}">
    {{ASPECT_1_DESCRIPTION}}
  </aspect>
  
  <aspect name="{{ASPECT_2}}">
    {{ASPECT_2_DESCRIPTION}}
  </aspect>
</analysis_framework>

<output_structure>
  <thinking>
    展示分析过程
  </thinking>
  
  <results>
    提供结构化结果
  </results>
</output_structure>
```

### 模板 4: 创意生成

```xml
<creative_brief>
  <objective>{{OBJECTIVE}}</objective>
  <target_audience>{{AUDIENCE}}</target_audience>
  <constraints>{{CONSTRAINTS}}</constraints>
</creative_brief>

<inspiration>
  <reference_1>{{REF_1}}</reference_1>
  <reference_2>{{REF_2}}</reference_2>
</inspiration>

<deliverables>
  <item>{{DELIVERABLE_1}}</item>
  <item>{{DELIVERABLE_2}}</item>
</deliverables>
```

## 实际应用示例

### 示例 1: 客户服务响应

```xml
<customer_inquiry>
  <customer_id>C12345</customer_id>
  <inquiry_type>产品退货</inquiry_type>
  <message>
    我购买的产品有质量问题,想要退货。订单号是 ORD-2024-001。
  </message>
</customer_inquiry>

<customer_history>
  <purchase_count>5</purchase_count>
  <total_spent>$500</total_spent>
  <previous_issues>无</previous_issues>
  <loyalty_tier>银卡会员</loyalty_tier>
</customer_history>

<company_policy>
  <return_window>30 天</return_window>
  <quality_issue_handling>全额退款或换货</quality_issue_handling>
  <vip_benefits>优先处理,免运费</vip_benefits>
</company_policy>

<task>
撰写一封客户服务响应邮件。

要求:
- 表达同理心和歉意
- 说明退货流程
- 提供银卡会员的额外优惠
- 语气友好专业

输出格式:
<email>
  <subject>邮件主题</subject>
  <body>邮件正文</body>
</email>
</task>
```

### 示例 2: 代码审查

```xml
<code_submission>
  <file_name>user_authentication.py</file_name>
  <code>
    {{CODE_CONTENT}}
  </code>
</code_submission>

<review_criteria>
  <criterion name="安全性">
    检查是否有安全漏洞,如 SQL 注入、XSS 等
  </criterion>
  
  <criterion name="性能">
    评估代码效率,识别性能瓶颈
  </criterion>
  
  <criterion name="可维护性">
    检查代码可读性、注释质量、命名规范
  </criterion>
  
  <criterion name="最佳实践">
    验证是否遵循 Python 最佳实践和 PEP 8
  </criterion>
</review_criteria>

<output_format>
  <summary>
    总体评价(1-2 句话)
  </summary>
  
  <detailed_review>
    <security>安全性分析</security>
    <performance>性能分析</performance>
    <maintainability>可维护性分析</maintainability>
    <best_practices>最佳实践检查</best_practices>
  </detailed_review>
  
  <recommendations>
    <critical>必须修改的问题</critical>
    <suggested>建议改进的地方</suggested>
  </recommendations>
</output_format>
```

### 示例 3: 内容改写

```xml
<original_content>
{{CONTENT_TO_REWRITE}}
</original_content>

<rewrite_parameters>
  <target_audience>
    {{AUDIENCE_DESCRIPTION}}
  </target_audience>
  
  <tone>
    {{DESIRED_TONE}}
  </tone>
  
  <length>
    {{TARGET_LENGTH}}
  </length>
  
  <key_points_to_preserve>
    <point>{{KEY_POINT_1}}</point>
    <point>{{KEY_POINT_2}}</point>
  </key_points_to_preserve>
</rewrite_parameters>

<constraints>
  <must_include>{{MUST_INCLUDE_ELEMENTS}}</must_include>
  <must_avoid>{{MUST_AVOID_ELEMENTS}}</must_avoid>
</constraints>

<output>
  <rewritten_content>
    改写后的内容
  </rewritten_content>
  
  <changes_summary>
    主要改动说明
  </changes_summary>
</output>
```

## 高级技巧

### 1. 动态标签

对于可变数量的项目,使用索引或 ID:

```xml
<items>
  <item id="1">项目 1</item>
  <item id="2">项目 2</item>
  <item id="3">项目 3</item>
</items>
```

### 2. 属性使用

使用属性添加元数据:

```xml
<document type="contract" date="2024-01-15" priority="high">
  文档内容
</document>
```

### 3. 混合内容

结合 XML 和 Markdown:

```xml
<analysis>
  ## 分析结果
  
  根据数据显示:
  - 要点 1
  - 要点 2
  
  <conclusion>
    最终结论
  </conclusion>
</analysis>
```

### 4. 引用标签内容

在指令中明确引用标签:

```
基于 <user_profile> 中的信息和 <product_catalog> 中的产品,
在 <recommendations> 标签中生成个性化推荐。
```

## 输出结构化

### 要求 AI 使用 XML 输出

```xml
<task>
分析以下数据并提供见解。

输出格式:
<analysis>
  <summary>简要总结</summary>
  <key_findings>
    <finding>发现 1</finding>
    <finding>发现 2</finding>
  </key_findings>
  <recommendations>
    <recommendation priority="high">建议 1</recommendation>
    <recommendation priority="medium">建议 2</recommendation>
  </recommendations>
</analysis>
</task>
```

### 便于后处理

使用 XML 输出便于程序化提取:

```python
import xml.etree.ElementTree as ET

# 解析 AI 的 XML 输出
root = ET.fromstring(ai_response)

# 提取特定部分
summary = root.find('summary').text
findings = [f.text for f in root.findall('.//finding')]
high_priority_recs = [r.text for r in root.findall(".//recommendation[@priority='high']")]
```

## 常见标签库

### 通用标签

- `<context>`: 背景信息
- `<instructions>`: 指令
- `<examples>`: 示例
- `<input>`: 输入数据
- `<output>`: 输出内容
- `<requirements>`: 要求
- `<constraints>`: 约束

### 文档标签

- `<document>`: 文档
- `<source>`: 来源
- `<content>`: 内容
- `<metadata>`: 元数据
- `<section>`: 章节

### 推理标签

- `<thinking>`: 思考过程
- `<analysis>`: 分析
- `<reasoning>`: 推理
- `<conclusion>`: 结论
- `<answer>`: 答案

### 数据标签

- `<user>`: 用户信息
- `<product>`: 产品信息
- `<transaction>`: 交易信息
- `<profile>`: 档案
- `<history>`: 历史记录

## 最佳实践清单

✅ **做**:

- 使用描述性的标签名称
- 保持标签命名一致
- 适当使用嵌套
- 在指令中引用标签名称
- 为复杂数据使用结构化标签

❌ **不要**:

- 过度使用标签(简单内容不需要)
- 使用模糊的标签名(如 `<data>`, `<info>`)
- 嵌套过深(一般不超过 3-4 层)
- 忘记闭合标签
- 在不需要结构化的地方强行使用

## 与 Markdown 的对比

### 何时使用 XML

- 需要严格的结构化
- 输出需要程序化处理
- 多层次嵌套数据
- 需要添加属性和元数据

### 何时使用 Markdown

- 简单的文本组织
- 人类可读性优先
- 不需要程序化处理
- 格式化文本内容

### 混合使用

```xml
<report>
  <summary>
    ## 执行摘要
    
    本报告分析了...
  </summary>
  
  <details>
    ### 详细发现
    
    1. 发现一
    2. 发现二
  </details>
</report>
```

## 注意事项

1. **不要过度工程化**: 简单任务不需要复杂的 XML 结构
2. **保持可读性**: XML 应该帮助而不是妨碍理解
3. **测试和迭代**: 验证 AI 是否正确理解你的 XML 结构
4. **文档化标签**: 对于复杂系统,维护标签使用文档

## 相关资源

- [Use XML Tags](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/use-xml-tags)
- [Prompt Engineering Overview](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview)