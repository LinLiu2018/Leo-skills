---
name: text-generator-skill
description: Text Generator Skill 技能。当用户需要相关帮助时使用。 [优化第5轮：提升了触发准确率]
license: MIT
---

# Text Generator - Claude Skill

> **Role**: Core Generation Engine
> **Type**: core

A fundamental skill for generating text content using LLM APIs.

## Capabilities
- **Generate**: Create content from prompts/templates.
- **Refine**: Improve existing text.
- **Synthesize**: Combine multiple inputs into a coherent output.

## Configuration
Requires `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` in environment variables.

## Usage
```python
from scripts.main import TextGenerator
generator = TextGenerator()
result = generator.generate(
    prompt="Write a PRD",
    context="...",
    template="..."
)
```
