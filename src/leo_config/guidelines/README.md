# 去AI化内容处理指南 (双模式版本)

## 📖 概述

这个模块提供了一套完整的去AI化内容处理方案，支持**创意模式**和**严谨模式**两种不同的处理方式。

### 🔄 双模式说明

**创意模式 (creative_mode)**

- 适用场景：营销文案、短视频脚本、直播话术、社交媒体内容
- 特点：口语化、接地气、真人口吻、有创意
- 目标：让内容像真人创作，有亲和力和感染力

**严谨模式 (formal_mode)**

- 适用场景：技术文档、数据分析、正式报告、商业计划书
- 特点：客观、准确、拒绝夸大、避免AI幻想
- 目标：提供可信可靠的信息，不虚构不误导

## 🎯 核心功能

### 创意模式功能

- 替换营销黑话为口语化表达
- 避免过度绝对化表达
- 添加个人感受和不确定性表达
- 调整句式让表达更自然

### 严谨模式功能

- 替换夸大表达为准确表述
- 为数据添加不确定性标注
- 自动添加风险提示
- 确保内容客观可信

### 质量检查

- 根据模式检测不同类型的问题
- 提供针对性的改进建议
- 给出质量评分

## 🚀 快速使用

### Python代码中使用

```python
from leo_config.guidelines import deaiify, check_text_quality, DeAIifier

# 原AI化文本
ai_text = """
该项目采用智慧农贸系统，打造全方位数字化生活服务。
依托14万人口红利，构建核心商业护城河。
投资回报率高达20%，保证6个月回本！
"""

# 创意模式处理（用于营销文案）
creative_text = deaiify(ai_text, mode="creative")
print(creative_text)
# 输出: 这个市场挺正规的，买菜付款都方便。
# 周边14万人左右，这生意应该差不了。
# 差不多半年能回本，一年赚个20%左右应该没问题。

# 严谨模式处理（用于正式报告）
formal_text = deaiify(ai_text, mode="formal")
print(formal_text)
# 输出: 项目配备标准化管理系统，提供便民服务。
# 辐射区域人口约14万人左右。
# 预计投资回报率约20%左右，回收期约6个月。
# **风险提示**: 以上数据为估算值，实际结果可能因市场环境、经营能力等因素而异。

# 质量检查
quality = check_text_quality(ai_text, mode="creative")
print(f"分数: {quality['score']}, 通过: {quality['passed']}")
```

### 在Skills中使用

```python
from leo_config.guidelines import DeAIifier

class MarketingSkill:
    """营销文案生成技能 - 使用创意模式"""
    def __init__(self):
        # 创意模式：用于营销文案
        self.deaiifier = DeAIifier(mode="creative")

    def generate_content(self, topic):
        # 1. 正常生成内容
        content = self._generate(topic)

        # 2. 去AI化处理（创意模式）
        content = self.deaiifier.process(content)

        # 3. 质量检查
        quality = self.deaiifier.check_quality(content)

        if not quality['passed']:
            # 根据建议改进
            suggestions = self.deaiifier.suggest_improvements(content)
            print(f"改进建议: {suggestions}")

        return content

class ReportSkill:
    """报告生成技能 - 使用严谨模式"""
    def __init__(self):
        # 严谨模式：用于正式报告
        self.deaiifier = DeAIifier(mode="formal")

    def generate_report(self, data):
        # 1. 正常生成报告
        report = self._generate(data)

        # 2. 去AI化处理（严谨模式）
        report = self.deaiifier.process(report)

        return report
```

## 📋 配置文件

配置位于：`leo_config/guidelines/deaiification_guide.yaml`

### 主要配置项

#### 创意模式配置

```yaml
creative_mode:
  # 营销黑话替换
  marketing_jargon_replacements:
    "核心卖点": "这几个地方我觉得不错"
    "投资回报": "能赚多少钱"
    "竞争优势": "比别人强的地方"

  # 避免绝对化
  avoid_absolutes:
    "完美": "还不错"
    "保证": "应该没问题"
    "必须": "最好"

  # 口语化表达
  colloquial_style:
    opening: ["我跟你说", "说实话"]
    personal_touch: ["我觉得", "我算了算"]
    uncertainty: ["差不多", "应该", "可能"]
```

#### 严谨模式配置

```yaml
formal_mode:
  # 避免夸大
  avoid_exaggeration:
    "保证": "预计/根据数据分析"
    "必定": "可能/有较大概率"
    "稳赚": "存在投资风险"

  # 数据表述规范
  data_language:
    - 使用"约/左右/大约"表示估算
    - 使用"根据XX数据显示"标注来源

  # 风险提示
  risk_disclaimers:
    - "以上数据为估算值，实际结果可能因市场环境、经营能力等因素而异"
```

#### 技能默认模式

```yaml
skill_default_modes:
  # 创意类技能
  "project-marketing-doc-generator-cskill": "creative"
  # 严谨类技能
  "data-analysis-cskill": "formal"
```

## 📝 去AI化原则

### 创意模式原则

1. **真实性**：加入个人经历和感受，承认不确定性
2. **接地气**：用大白话解释，用具体数字和案例
3. **情感共鸣**：分享真实困惑，展示决策犹豫
4. **不完美**：承认局限，展示学习过程

### 严谨模式原则

1. **事实优先**：只陈述可验证的事实
2. **拒绝夸大**：使用保守估计，避免过度乐观
3. **风险提示**：明确说明可能的负面影响
4. **数据溯源**：标注数据来源或估算性质

## 🔄 在Leo系统中的应用

### 自动应用

不同技能会根据类型自动应用对应的去AI化模式：

**创意类技能（自动使用创意模式）**

- `project-marketing-doc-generator-cskill` - 营销文档生成
- `content-layout-leo-cskill` - 内容排版
- `realestate-news-publisher` - 房产资讯发布

**严谨类技能（自动使用严谨模式）**

- `data-analysis-cskill` - 数据分析
- `technical-writer-cskill` - 技术文档写作
- `business-analyzer-cskill` - 商业分析

### 手动应用

```python
# 在代码中手动调用
from leo_config.guidelines import DeAIifier

# 创意模式
deaiifier = DeAIifier(mode="creative")
text = deaiifier.process("原文")

# 严谨模式
deaiifier = DeAIifier(mode="formal")
text = deaiifier.process("原文")
```

## 📊 质量评分标准

### 创意模式评分标准

| 分数 | 等级 | 说明 |
|------|------|------|
| 90-100 | 优秀 | 非常自然，像真人在说话 |
| 70-89 | 良好 | 基本自然，有少量营销黑话 |
| 50-69 | 一般 | 有明显AI痕迹，过于正式 |
| 0-49 | 差 | AI痕迹严重，大量营销黑话 |

### 严谨模式评分标准

| 分数 | 等级 | 说明 |
|------|------|------|
| 90-100 | 优秀 | 客观准确，风险提示完善 |
| 70-89 | 良好 | 基本准确，有少量夸大 |
| 50-69 | 一般 | 存在夸大表达，数据标注不足 |
| 0-49 | 差 | 严重夸大，缺少风险提示 |

## 🛠️ 开发指南

### 扩展配置

编辑 `deaiification_guide.yaml` 添加新的规则：

```yaml
# 创意模式
creative_mode:
  marketing_jargon_replacements:
    "新词": "口语化表达"
  avoid_absolutes:
    "绝对化词": "相对化表达"

# 严谨模式
formal_mode:
  avoid_exaggeration:
    "夸大词": "准确表达"
  risk_disclaimers:
    - "新的风险提示模板"
```

### 自定义处理器

```python
from leo_config.guidelines import DeAIifier

class CustomDeAIifier(DeAIifier):
    def _custom_rule(self, text: str) -> str:
        # 你的自定义规则
        return text

    def process(self, text: str, mode: str = None) -> str:
        text = super().process(text, mode)
        return self._custom_rule(text)
```

## 📚 相关资源

- [去AI化指南完整配置](leo_config/guidelines/deaiification_guide.yaml)
- [去AI化处理器源码](leo_config/guidelines/deaiifier.py)
- [营销文档生成器Skill](leo_skills/tools/project-marketing-doc-generator-cskill/)

## 🤝 贡献

如果你发现新的AI化表达模式，欢迎更新配置文件并提交PR！

## 📞 支持

有问题或建议？请联系Leo团队或提Issue。

---

**最后更新**: 2026-01-08
**版本**: 2.0.0 (双模式版本)
