# Skill Code Generator 快速开始指南

## 5 分钟创建你的第一个技能

### 步骤 1：准备环境

```bash
# 确保已安装 Leo Skills
pip install leo-skills

# 验证安装
python -c "from leo_skills import SkillCodeGenerator; print('OK')"
```

### 步骤 2：使用 Python API 创建

```python
from skill_code_generator_skill import SkillCodeGenerator

# 创建生成器
generator = SkillCodeGenerator()

# 方法 1：从自然语言描述创建
result = generator.execute(
    action="generate_from_prompt",
    prompt="创建一个天气 API 客户端技能，可以查询实时天气和预报"
)

# 查看生成的文件
print(f"技能路径：{result['skill_path']}")
print(f"创建文件：{result['files_created']}")
```

### 步骤 3：使用模板创建（推荐新手）

```python
# 查看可用模板
templates = generator.execute(action="list_templates")
print(templates['templates'])

# 使用 api-client 模板
result = generator.execute(
    action="generate_from_template",
    template="api-client",
    name="weather-api",
    description="天气 API 客户端",
    category="tools"
)
```

### 步骤 4：验证生成的技能

```python
# 验证技能目录
result = generator.execute(
    action="validate",
    skill_path="./weather-api_skill"
)

print(f"验证结果：{result['valid']}")
if result.get('errors'):
    print(f"错误：{result['errors']}")
if result.get('warnings'):
    print(f"建议：{result['warnings']}")
```

### 步骤 5：测试生成的技能

```bash
# 进入技能目录
cd weather-api_skill

# 运行测试
python -m pytest tests/ -v

# 或手动测试
python -c "from weather_api_skill import WeatherApiSkill; s=WeatherApiSkill(); print(s.execute(action='status'))"
```

## 常见用例

### 用例 1：创建数据处理技能

```python
result = generator.execute(
    action="generate_from_template",
    template="data-processor",
    name="csv-cleaner",
    description="CSV 数据清洗工具",
    features=[
        "读取 CSV 文件",
        "处理缺失值",
        "数据格式转换",
        "导出清洗后的数据"
    ]
)
```

### 用例 2：创建内容生成技能

```python
result = generator.execute(
    action="generate_from_prompt",
    prompt="创建一个博客文章生成技能，可以根据主题生成 SEO 优化的文章"
)
```

### 用例 3：批量创建技能

```python
skills_to_create = [
    {"name": "email-sender", "template": "automation"},
    {"name": "pdf-reader", "template": "file-handler"},
    {"name": "api-tester", "template": "api-client"},
]

for skill_config in skills_to_create:
    result = generator.execute(
        action="generate_from_template",
        **skill_config
    )
    print(f"✅ 创建 {skill_config['name']}: {result['skill_path']}")
```

## 自定义模板

在 `config/templates.yaml` 中定义你自己的模板：

```yaml
templates:
  my-custom-template:
    description: "我的自定义模板"
    extra_deps:
      - requests
      - pandas
    extra_files:
      - scripts/helper.py
      - templates/output.md
```

## 故障排除

### 问题 1：生成的技能无法导入

**解决**：
```bash
# 确保在技能目录的父目录
cd ..
python -c "from my_skill_skill import MySkillSkill; print('OK')"
```

### 问题 2：依赖安装失败

**解决**：
```bash
# 手动安装依赖
pip install requests pandas jinja2 pyyaml
```

### 问题 3：测试失败

**解决**：
```bash
# 查看详细错误
python -m pytest tests/ -v -s

# 检查 Python 版本
python --version  # 需要 3.8+
```

## 下一步

- 阅读 [skill-template.md](skill-template.md) 了解完整模板结构
- 查看 [best-practices.md](best-practices.md) 学习最佳实践
- 参考生成的技能代码，实现具体业务逻辑

---
*最后更新：2026-03-13*
