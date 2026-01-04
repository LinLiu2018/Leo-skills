# Leo Skills Manifest

**Leo 的 Claude Code 技能清单** - 完整的技能索引和加载指南

---

## 技能总览

| 分类 | 技能数 | 状态 |
|------|--------|------|
| 内容创作 (content-creation) | 2 | 🟢 活跃 |
| 数据分析 (data-analysis) | 0 | ⚪ 待开发 |
| 自动化 (automation) | 0 | ⚪ 待开发 |
| 工具 (utilities) | 0 | ⚪ 待开发 |

**总计**: 2 个活跃技能

---

## 详细清单

### 📝 内容创作类

#### 1. realestate-news-publisher-cskill

**路径**: `content-creation/realestate-news-publisher-cskill/`

**描述**: 房产政策资讯自动化发布代理 - 收集全网房产资讯，AI分析生成专业文章并发布到公众号

**核心功能**:
- ✅ 多源数据收集（政府、新闻、行业、社交媒体）
- ✅ AI智能分析和内容生成
- ✅ 微信公众号自动发布
- ✅ 关键词监控和去重
- ✅ 支持宁波本地市场分析

**技术栈**:
- Python 3.9+
- ZhipuAI GLM-4
- BeautifulSoup4
- YAML配置

**激活词**:
- "发布房产资讯"
- "生成楼市分析"
- "收集房产政策"

**入口文件**: `scripts/main.py`

**配置文件**:
- `config/config.yaml` - 主配置
- `config/sources.yaml` - 数据源
- `config/keywords.yaml` - 关键词

---

#### 2. content-layout-leo-cskill

**路径**: `content-creation/content-layout-leo-cskill/`

**描述**: 智能内容排版技能 - 支持微信公众号、小红书、微博、博客等多平台智能排版

**核心功能**:
- ✅ 10种房产类优质排版风格
- ✅ 智能图片匹配（AI生成提示词）
- ✅ 多平台格式转换
- ✅ 自动emoji插入
- ✅ 金句提取高亮
- ✅ 色彩方案配置

**10种风格**:
1. data_driven - 数据驱动型（真叫卢俊风格）
2. story_telling - 故事叙述型（米宅风格）
3. minimalist_professional - 极简专业型（层楼风格）
4. vibrant_attention - 活力吸睛型（大V风格）
5. emotional_resonance - 情感共鸣型（暖心风格）
6. listicle_practical - 清单列表型（实用风格）
7. comparison_analysis - 对比分析型（分析风格）
8. case_study_deep - 案例解读型（深度风格）
9. qa_interactive - 问答互动型（社群风格）
10. magazine_premium - 杂志排版型（高端风格）

**支持平台**:
- 微信公众号（HTML）
- 小红书（emoji文本）
- 微博（Markdown）
- 博客（Markdown）

**激活词**:
- "帮我排版"
- "生成公众号格式"
- "转为小红书格式"
- "添加配图"
- "优化文章排版"

**入口文件**: `scripts/main.py`

**配置文件**:
- `config/style_profiles.yaml` - 风格配置

---

### 📊 数据分析类

*暂无技能*

---

### 🤖 自动化类

*暂无技能*

---

### 🔧 工具类

*暂无技能*

---

## 渐进式加载指南

### 按需加载

```bash
# 1. 加载单个技能
ln -s ~/ai-agents-workspace/leo-skills/content-creation/realestate-news-publisher-cskill ~/.claude/skills/

# 2. 加载整个分类
for skill in ~/ai-agents-workspace/leo-skills/content-creation/*; do
    ln -s "$skill" ~/.claude/skills/
done

# 3. 加载所有技能
for category in ~/ai-agents-workspace/leo-skills/*; do
    for skill in "$category"/*; do
        ln -s "$skill" ~/.claude/skills/
    done
done
```

### Claude Code 技能路径

```
~/.claude/skills/
├── realestate-news-publisher-cskill -> ~/ai-agents-workspace/leo-skills/content-creation/realestate-news-publisher-cskill
└── content-layout-leo-cskill -> ~/ai-agents-workspace/leo-skills/content-creation/content-layout-leo-cskill
```

---

## 技能开发路线图

### 短期计划 (Q1 2026)

- [ ] 增加数据分析类技能
  - [ ] 数据可视化技能
  - [ ] Excel自动化处理

### 中期计划 (Q2 2026)

- [ ] 增加自动化类技能
  - [ ] 网页自动化测试
  - [ ] 定时任务调度

### 长期计划 (Q3-Q4 2026)

- [ ] 增加工具类技能
  - [ ] 代码重构助手
  - [ ] 文档生成器

---

## 更新日志

| 日期 | 技能 | 版本 | 更新内容 |
|------|------|------|----------|
| 2026-01-04 | realestate-news-publisher-cskill | 1.0.0 | 初始版本，支持资讯收集和发布 |
| 2026-01-04 | content-layout-leo-cskill | 1.0.0 | 初始版本，10种排版风格 |

---

## 作者信息

**Leo Liu**

- GitHub: [@LinLiu2018](https://github.com/LinLiu2018)
- 技能仓库: [leo-skills](https://github.com/LinLiu2018/leo-skills)

---

*最后更新: 2026-01-04*
