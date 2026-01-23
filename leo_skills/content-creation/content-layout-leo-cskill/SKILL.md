# Content Layout Leo CSkill

**Version:** 1.0.0
**Type:** Simple Skill
**Created by:** Leo Liu

---

智能内容排版技能 by Leo - 支持微信公众号、小红书、微博、博客等多平台智能排版，具备AI图片智能匹配和10种房产类优质排版风格。

## 功能概述

### 核心能力

| 功能 | 说明 |
|------|------|
| **多平台排版** | 微信公众号、小红书、微博、博客 |
| **智能图片匹配** | AI分析内容，自动匹配合适图片 |
| **10种风格模板** | 房产类目专业排版风格 |
| **自动emoji插入** | 根据内容智能添加表情符号 |
| **金句提取** | 自动识别并高亮金句 |
| **色彩方案** | 每种风格都有专业配色 |
| **响应式排版** | 自适应不同设备 |

---

## 激活词

使用以下关键词可自动触发此技能：

- "帮我排版这篇文章"
- "生成公众号格式"
- "转为小红书格式"
- "添加配图"
- "优化文章排版"
- "智能排版"

---

## 使用方法

### 命令行使用

```bash
# 微信公众号排版
python scripts/main.py -p wechat -s data_driven -i article.md -o output.html

# 小红书排版
python scripts/main.py -p xiaohongshu -s vibrant_attention -i article.md -o output.txt

# 生成图片提示词
python scripts/main.py -p wechat -s data_driven -i article.md --images
```

### Python 代码调用

```python
from scripts.main import format_for_wechat, generate_image_prompts

# 读取文章
with open('article.md', 'r', encoding='utf-8') as f:
    content = f.read()

# 微信公众号排版
html_content = format_for_wechat(
    content=content,
    style='data_driven',
    title='2026年楼市展望'
)

# 生成图片提示词
prompts = generate_image_prompts(content, style='professional')
for prompt in prompts:
    print(f"主题: {prompt['theme']}")
    print(f"提示词: {prompt['prompt']}")
```

---

## 版本信息

- **版本:** 1.0.0
- **创建者:** Leo Liu
- **许可:** MIT License
