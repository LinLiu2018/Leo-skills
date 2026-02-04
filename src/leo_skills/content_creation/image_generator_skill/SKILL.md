# Image Generator Skill (AI图片生成技能)

## 技能描述

基于 OpenAI DALL-E 3/GPT-Image-1 API 的 AI 图片生成技能。支持文本生成图片、图片编辑、风格变换等功能。

## 核心能力

- **文本生成图片**: 根据文字描述生成高质量图片
- **图片编辑**: 对现有图片进行 AI 编辑修改
- **风格变换**: 生成图片的不同风格变体
- **批量生成**: 支持批量生成多张图片
- **尺寸支持**: 1024x1024, 1792x1024, 1024x1792

## 使用方法

```python
from image_generator_skill import ImageGeneratorSkill

skill = ImageGeneratorSkill()

# 生成图片
result = skill.execute(
    action="generate",
    prompt="一个现代简约风格的小程序首页界面，橙色主题",
    size="1024x1024",
    quality="hd"
)

# 批量生成
result = skill.execute(
    action="batch_generate",
    prompts=["首页效果图", "分享页效果图", "个人中心效果图"],
    style="miniprogram-ui"
)
```

## 配置要求

需要在环境变量或配置文件中设置 OpenAI API Key:
```yaml
openai:
  api_key: "your-api-key"
```

## 支持的模型

- `dall-e-3` (默认): 最新的 DALL-E 3 模型
- `gpt-image-1`: OpenAI 最新图片生成模型

## 进化机制

本技能支持自我进化：
- 学习用户偏好的图片风格
- 优化 prompt 生成质量
- 记录成功的生成案例
