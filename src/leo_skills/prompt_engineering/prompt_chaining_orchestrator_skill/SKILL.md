---
name: prompt-chaining-orchestrator-skill
description: 将复杂任务分解为多个顺序步骤,通过提示词链提高准确性和可靠性。当用户需要提示词工程相关帮助时使用。 [优化第5轮：提升了触发准确率]
license: MIT
---

# Prompt Chaining Orchestrator - 提示词链编排器

## 功能描述

这个技能帮助你将复杂任务分解为多个顺序步骤,每个步骤使用单独的提示词。通过链式处理,可以显著提高复杂任务的准确性和可靠性。

## 什么是提示词链?

提示词链 (Prompt Chaining) 是将一个复杂任务分解为多个较小的顺序步骤,每个步骤的输出作为下一个步骤的输入。这种方法通过使每个单独任务更简单来提高整体准确性。

## 核心优势

✅ **提高准确性**: 每个步骤专注于单一任务,减少错误
✅ **增强可控性**: 可以在每个步骤验证和调整
✅ **便于调试**: 容易识别和修复问题环节
✅ **支持迭代**: 可以基于中间结果进行改进
✅ **模块化**: 步骤可以重用和组合

## 权衡考虑

⚠️ **增加延迟**: 多次 API 调用需要更多时间
⚠️ **成本更高**: 更多的 token 使用
⚠️ **需要编排**: 需要管理步骤之间的数据流

**何时值得使用**: 当准确性和可靠性比速度更重要时

## 何时使用提示词链?

✅ **适合的场景**:

- 复杂的多阶段任务
- 需要迭代改进的任务
- 多步骤分析和推理
- 中间验证能增加价值
- 单个提示产生不一致结果

❌ **不适合的场景**:

- 简单的单步任务
- 对延迟非常敏感的应用
- 预算有限的场景
- 步骤之间没有明确边界的任务

## 基本模式

### 模式 1: 线性链 (Linear Chain)

最简单的模式,步骤按顺序执行:

```
步骤 1: 初始处理
   ↓
步骤 2: 中间处理
   ↓
步骤 3: 最终输出
```

### 模式 2: 分支链 (Branching Chain)

根据中间结果选择不同路径:

```
步骤 1: 分析输入
   ↓
步骤 2: 分类
   ├─→ 路径 A → 步骤 3A
   └─→ 路径 B → 步骤 3B
```

### 模式 3: 迭代链 (Iterative Chain)

包含反馈循环的链:

```
步骤 1: 生成初稿
   ↓
步骤 2: 评估质量
   ↓
步骤 3: 改进 → 返回步骤 2(如果需要)
```

### 模式 4: 并行聚合链 (Parallel Aggregation Chain)

并行处理后聚合结果:

```
步骤 1: 分发任务
   ├─→ 子任务 A
   ├─→ 子任务 B
   └─→ 子任务 C
        ↓
步骤 2: 聚合结果
```

## 实际应用示例

### 示例 1: 研究摘要链

**任务**: 创建高质量的研究论文摘要

```
步骤 1: 初始摘要
提示词:
"总结这篇研究论文,涵盖方法、发现和临床意义。

论文: {{PAPER_CONTENT}}

要求:
- 200-300 字
- 包含关键发现
- 使用专业术语"

步骤 2: 质量评估
提示词:
"审查以下摘要的准确性、清晰度和完整性。

原始论文: {{PAPER_CONTENT}}
摘要: {{STEP_1_OUTPUT}}

提供分级反馈:
- 准确性 (1-10)
- 清晰度 (1-10)
- 完整性 (1-10)
- 具体改进建议"

步骤 3: 改进摘要
提示词:
"基于以下反馈改进摘要。

原始摘要: {{STEP_1_OUTPUT}}
反馈: {{STEP_2_OUTPUT}}

生成改进后的摘要,确保:
- 解决所有反馈点
- 保持字数限制
- 提高整体质量"
```

### 示例 2: 内容创作链

**任务**: 创建营销文案

```
步骤 1: 头脑风暴
提示词:
"为以下产品生成 10 个营销角度。

产品: {{PRODUCT_INFO}}
目标受众: {{TARGET_AUDIENCE}}

对每个角度提供:
- 核心信息
- 情感诉求
- 独特卖点"

步骤 2: 选择最佳角度
提示词:
"评估以下营销角度,选择最有潜力的 3 个。

角度列表: {{STEP_1_OUTPUT}}
产品: {{PRODUCT_INFO}}
目标受众: {{TARGET_AUDIENCE}}

评估标准:
- 相关性
- 独特性
- 情感共鸣
- 可行性

输出: 排名前 3 的角度及理由"

步骤 3: 撰写文案
提示词:
"基于选定的营销角度撰写完整文案。

选定角度: {{STEP_2_OUTPUT}}
产品: {{PRODUCT_INFO}}

要求:
- 标题(吸引眼球)
- 正文(200-300 字)
- 行动号召
- 语气: 友好、专业"

步骤 4: 优化和润色
提示词:
"优化以下营销文案。

文案: {{STEP_3_OUTPUT}}

优化重点:
- 增强情感吸引力
- 简化语言
- 强化行动号召
- 确保语法完美"
```

### 示例 3: 数据分析链

**任务**: 分析销售数据并提供建议

```
步骤 1: 数据清洗和验证
提示词:
"检查以下销售数据的质量。

数据: {{RAW_DATA}}

任务:
1. 识别缺失值
2. 发现异常值
3. 验证数据一致性
4. 提供清洗后的数据

输出格式: JSON"

步骤 2: 描述性统计
提示词:
"对清洗后的数据进行描述性统计分析。

数据: {{STEP_1_OUTPUT}}

计算:
- 基本统计量(均值、中位数、标准差)
- 时间趋势
- 产品类别分布
- 地区分布

输出格式: 结构化报告"

步骤 3: 洞察提取
提示词:
"基于统计分析提取关键洞察。

统计报告: {{STEP_2_OUTPUT}}

识别:
- 最重要的趋势
- 异常模式
- 机会领域
- 风险因素

每个洞察提供:
- 描述
- 支持数据
- 业务影响"

步骤 4: 行动建议
提示词:
"基于分析洞察提供可执行建议。

洞察: {{STEP_3_OUTPUT}}
原始数据: {{STEP_1_OUTPUT}}

生成:
- 3-5 个优先级建议
- 每个建议包含:
  * 具体行动
  * 预期影响
  * 实施难度
  * 所需资源

输出格式: 优先级排序的行动计划"
```

### 示例 4: 代码审查链

**任务**: 全面的代码审查

```
步骤 1: 语法和风格检查
提示词:
"审查代码的语法和风格。

代码: {{CODE}}
语言: {{LANGUAGE}}

检查:
- 语法错误
- 命名规范
- 代码格式
- 注释质量

输出: 问题列表和建议"

步骤 2: 逻辑和算法审查
提示词:
"审查代码的逻辑和算法。

代码: {{CODE}}
步骤 1 反馈: {{STEP_1_OUTPUT}}

检查:
- 逻辑错误
- 算法效率
- 边界情况处理
- 错误处理

输出: 逻辑问题和优化建议"

步骤 3: 安全性审查
提示词:
"审查代码的安全性。

代码: {{CODE}}

检查:
- SQL 注入风险
- XSS 漏洞
- 认证/授权问题
- 敏感数据处理

输出: 安全问题和修复建议"

步骤 4: 综合报告
提示词:
"生成综合代码审查报告。

语法审查: {{STEP_1_OUTPUT}}
逻辑审查: {{STEP_2_OUTPUT}}
安全审查: {{STEP_3_OUTPUT}}

生成:
- 执行摘要
- 按严重性分类的问题
- 优先级修复建议
- 整体代码质量评分

输出格式: Markdown 报告"
```

## 实现策略

### 策略 1: 手动链接

在对话中手动执行每个步骤:

```
用户: [执行步骤 1]
AI: [步骤 1 输出]
用户: [使用步骤 1 输出执行步骤 2]
AI: [步骤 2 输出]
...
```

**优点**: 灵活,可以根据中间结果调整
**缺点**: 手动操作,效率较低

### 策略 2: 工作流自动化

使用工作流工具自动化链式执行:

```python
# 伪代码示例
def research_summary_chain(paper_content):
    # 步骤 1: 初始摘要
    summary = call_ai(prompt_1, paper_content)
    
    # 步骤 2: 质量评估
    feedback = call_ai(prompt_2, paper_content, summary)
    
    # 步骤 3: 改进摘要
    improved_summary = call_ai(prompt_3, summary, feedback)
    
    return improved_summary
```

**优点**: 可重复,高效
**缺点**: 需要编程,灵活性较低

### 策略 3: 条件分支

根据中间结果选择路径:

```python
def content_moderation_chain(content):
    # 步骤 1: 初步分类
    category = call_ai(classify_prompt, content)
    
    # 步骤 2: 根据分类选择路径
    if category == "safe":
        return approve_content(content)
    elif category == "suspicious":
        detailed_review = call_ai(detailed_review_prompt, content)
        return make_decision(detailed_review)
    else:  # category == "unsafe"
        return reject_content(content)
```

### 策略 4: 迭代改进

包含质量检查和重试逻辑:

```python
def iterative_generation_chain(requirements, max_iterations=3):
    output = call_ai(generate_prompt, requirements)
    
    for i in range(max_iterations):
        quality_score = call_ai(evaluate_prompt, output, requirements)
        
        if quality_score >= 8:  # 质量足够好
            break
            
        # 生成改进建议
        feedback = call_ai(feedback_prompt, output, quality_score)
        
        # 基于反馈改进
        output = call_ai(improve_prompt, output, feedback)
    
    return output
```

## 设计提示词链的最佳实践

### 1. 明确定义步骤边界

每个步骤应该有清晰的:

- **输入**: 需要什么信息
- **任务**: 要完成什么
- **输出**: 产生什么结果

### 2. 保持步骤独立性

每个步骤应该:

- 专注于单一任务
- 不依赖隐含的上下文
- 可以独立测试和优化

### 3. 设计清晰的数据流

```
步骤 1 输出 → 步骤 2 输入
步骤 2 输出 → 步骤 3 输入
```

明确每个步骤需要前面哪些步骤的输出

### 4. 包含验证步骤

在关键点添加验证:

```
生成 → 验证 → 改进 → 最终输出
```

### 5. 优化提示词

每个步骤的提示词应该:

- 明确说明任务
- 提供必要的上下文
- 指定输出格式
- 包含质量标准

## 常见链式模式

### 模式 1: 生成-评估-改进

```
1. 生成初始输出
2. 评估质量
3. 基于评估改进
```

**适用**: 创意任务、内容生成

### 模式 2: 分解-处理-聚合

```
1. 将大任务分解为子任务
2. 分别处理每个子任务
3. 聚合结果
```

**适用**: 复杂分析、大规模处理

### 模式 3: 提取-分析-综合

```
1. 从原始数据提取信息
2. 分析提取的信息
3. 综合形成结论
```

**适用**: 数据分析、研究任务

### 模式 4: 规划-执行-验证

```
1. 制定行动计划
2. 执行计划
3. 验证结果
```

**适用**: 问题解决、项目管理

## 性能优化

### 1. 并行化独立步骤

如果某些步骤不相互依赖,可以并行执行:

```python
# 并行执行独立分析
results = parallel_execute([
    (analyze_sales, sales_data),
    (analyze_marketing, marketing_data),
    (analyze_customer, customer_data)
])

# 聚合结果
final_report = synthesize(results)
```

### 2. 缓存中间结果

避免重复计算:

```python
cache = {}

def cached_step(step_id, prompt, input_data):
    cache_key = f"{step_id}:{hash(input_data)}"
    
    if cache_key in cache:
        return cache[cache_key]
    
    result = call_ai(prompt, input_data)
    cache[cache_key] = result
    return result
```

### 3. 早期终止

在满足条件时提前结束链:

```python
def quality_controlled_chain(input_data):
    output = generate(input_data)
    
    if quality_check(output) >= threshold:
        return output  # 质量已足够好,无需继续
    
    # 否则继续改进步骤
    feedback = evaluate(output)
    improved = refine(output, feedback)
    return improved
```

## 监控和调试

### 1. 记录每个步骤

```python
def logged_chain(input_data):
    log = []
    
    step1_output = step1(input_data)
    log.append({"step": 1, "output": step1_output})
    
    step2_output = step2(step1_output)
    log.append({"step": 2, "output": step2_output})
    
    # ...
    
    return final_output, log
```

### 2. 质量检查点

在关键步骤添加质量检查:

```python
def quality_checked_chain(input_data):
    step1_output = step1(input_data)
    
    if not validate_step1(step1_output):
        raise ValueError("Step 1 output failed validation")
    
    step2_output = step2(step1_output)
    # ...
```

### 3. A/B 测试

测试不同的链式设计:

```python
# 版本 A: 3 步链
chain_a = [step1, step2, step3]

# 版本 B: 4 步链(包含额外验证)
chain_b = [step1, validate, step2, step3]

# 比较结果质量
```

## 注意事项

1. **不要过度分解**: 太多步骤会增加复杂性和成本
2. **保持上下文**: 确保每个步骤有足够的上下文信息
3. **处理错误**: 设计错误处理和恢复机制
4. **成本意识**: 监控 token 使用和 API 调用次数
5. **测试整个链**: 不仅测试单个步骤,也要测试整个流程

## 相关资源

- [Prompt Chaining](https://claude.com/blog/best-practices-for-prompt-engineering)
- [Building Effective Agents](https://www.anthropic.com/research/building-effective-agents)