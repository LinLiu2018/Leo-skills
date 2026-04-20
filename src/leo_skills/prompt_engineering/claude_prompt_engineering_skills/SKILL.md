---
name: claude-prompt-engineering-skills
description: Claude提示工程技能集合，提供少样本学习、思维链、角色设定等最佳提示技术。
license: MIT
---

# Claude Prompt Engineering Skills - Claude提示工程技能

## 功能描述

提供Claude最佳提示工程技术，帮助用户更有效地与AI交互。

## 支持的提示技术

### 1. 少样本学习 (Few-Shot)

通过提供示例来引导AI理解任务模式。

```
任务描述：[你的任务]
示例：
输入: [示例1输入] → 输出: [示例1输出]
输入: [示例2输入] → 输出: [示例2输出]
现在请处理：[新输入]
```

### 2. 思维链 (Chain of Thought)

要求AI展示推理过程，提高复杂任务的准确性。

```
[任务描述]
在回答之前,请逐步思考。
```

### 3. 角色设定 (Role Playing)

为AI分配特定角色以获得更专业的回答。

```
你是一位[角色]，具有[专业背景]。
请以专家身份回答以下问题。
```

### 4. 自我纠正 (Self-Correction)

让AI在回答后进行自我审查和改进。

```
回答问题后，请检查：
1. 回答是否准确？
2. 是否有遗漏的重要点？
3. 如何改进回答质量？
```

### 5. 上下文优化 (Context Optimization)

有效管理对话上下文，避免信息丢失。

### 6. 输出格式化 (Output Formatting)

指定输出的结构和格式要求。

## 核心类

- `ClaudePromptEngineeringSkills`: 主类，提供所有提示工程技术
- `PromptTechnique`: 提示技术枚举
- `PromptTemplate`: 提示模板
- `PromptExample`: 提示示例

## 使用示例

```python
from leo_skills.prompt_engineering.claude_prompt_engineering_skills import ClaudePromptEngineeringSkills

skills = ClaudePromptEngineeringSkills()
template = skills.create_template(
    name="问题解决",
    technique=PromptTechnique.CHAIN_OF_THOUGHT,
    description="使用思维链解决复杂问题"
)
```

## 相关资源

- [Claude 提示工程最佳实践](https://docs.anthropic.com/)
- [提示工程指南](https://www.promptingguide.ai/)
