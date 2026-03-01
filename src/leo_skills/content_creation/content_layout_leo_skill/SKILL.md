# Content Layout Skill

多平台内容排版技能。

## Layout

```python
from leo_skills.content_creation.content_layout_leo_skill import ContentLayoutLeo

layout = ContentLayoutLeo()
result = layout.execute("layout", content=content, template="wechat")
```

## Generate Image Prompts

```python
prompts = layout.execute("image_prompts", content=content, style="professional")
```

---
**Version:** 1.0.0
