# Leo Skills Manifest

**Leo 的 Claude Code 技能清单** - 完整的技能索引和加载指南

---

## 技能总览

| 分类 | 技能数 | 状态 |
|------|--------|------|
| 内容创作 (content-creation) | 2 | 🟢 活跃 |
| 工具 (utilities) | 1 | 🟢 活跃 |
| 工具框架 (tools) | 3 | 🟢 活跃 |
| 数据分析 (data-analysis) | 0 | ⚪ 待开发 |
| 自动化 (automation) | 0 | ⚪ 待开发 |

**总计**: 6 个活跃技能

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
- MiniMax abab6.5s-chat
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

### 🛠️ 工具框架

#### agent-skill-creator

**路径**: `tools/agent-skill-creator/`

**描述**: 技能创建元技能 - 教会 Claude Code 如何自主创建完整的 Claude Skills

**核心功能**:
- ✅ 5阶段自主创建流程（发现→设计→架构→检测→实现）
- ✅ 多智能体套件支持
- ✅ 学习和优化能力（AgentDB 集成）
- ✅ 模板化创建
- ✅ 交互式配置

**适用场景**:
- 创建自动化工作流代理
- 将重复流程转化为技能
- 构建领域专用智能体
- 批量技能创建

**入口文件**: `SKILL.md`

**文档**: `README.md`, `SKILL.md`

---

#### article-to-prototype-cskill

**路径**: `tools/article-to-prototype-cskill/`

**描述**: 文章转代码原型技能 - 从技术文档自动提取算法并生成可执行的原型代码

**核心功能**:
- ✅ 多格式输入支持（PDF、网页、Jupyter Notebook、Markdown）
- ✅ 智能算法检测和提取
- ✅ 架构模式识别
- ✅ 自动编程语言选择
- ✅ 生成完整可运行的项目

**支持格式**:
- 学术论文（arXiv、IEEE、ACM）
- 技术博客和教程
- API文档和规范
- Jupyter Notebook

**入口文件**: `SKILL.md`

**文档**: `README.md`, `SKILL.md`

---

#### project-marketing-doc-generator-cskill

**路径**: `tools/project-marketing-doc-generator-cskill/`

**描述**: 项目营销文档生成器 - 快速生成商业项目营销文档和销售资料

**核心功能**:
- ✅ 全案营销手册生成（完整版）
- ✅ 销售速查卡生成（1页精华版）
- ✅ 投资回报测算
- ✅ 竞品分析报告
- ✅ 销售话术生成

**适用项目**:
- 菜市场、农贸市场项目
- 商业地产项目
- 招商引资项目

**入口文件**: `SKILL.md`

**文档**: `README.md`, `SKILL.md`

---

## 渐进式加载指南

### 按需加载

```bash
# 1. 加载单个技能
ln -s d:/桌面/AI_claude_skills/leo-skills/content-creation/realestate-news-publisher-cskill ~/.claude/skills/

# 2. 加载整个分类
for skill in d:/桌面/AI_claude_skills/leo-skills/content-creation/*; do
    ln -s "$skill" ~/.claude/skills/
done

# 3. 加载所有技能
for category in d:/桌面/AI_claude_skills/leo-skills/*; do
    for skill in "$category"/*; do
        ln -s "$skill" ~/.claude/skills/
    done
done
```

### Claude Code 技能路径

```
~/.claude/skills/
├── realestate-news-publisher-cskill -> d:/桌面/AI_claude_skills/leo-skills/content-creation/realestate-news-publisher-cskill
└── content-layout-leo-cskill -> d:/桌面/AI_claude_skills/leo-skills/content-creation/content-layout-leo-cskill
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

## 📚 资料文档

### 个人档案

**路径**: `docs/profile/leo-profile.md`

**描述**: Leo（佬流）完整档案 - 包含基础信息、事业板块、技术工具栈、学习目标、协作期望等

**内容概要**:
- 基础信息（36岁创业者，浙江宁波）
- 房产中介业务（度假养老别墅，10人团队）
- AI眼镜赛道（筹备中）
- 技术工具栈（Raycast + Dify + n8n + 飞书 + 企业微信）
- 学习目标（AI编程从入门到精通）
- 业务需求（飞书多维表格、账号管理系统）
- 协作期望（AI最强搭档定位）

**更新时间**: 2026年1月5日

### 技能架构分析

**路径**: `docs/analysis/skill-creator-skill-architecture.md`

**描述**: agent-skill-creator 技能架构分析 - 从"创建/训练/维护/使用"角度的优化建议

**内容概要**:
- 创建：技能发现与创建机制评估
- 训练：技能培训与成长体系设计
- 维护：技能健康度与迭代优化
- 使用：技能调度与效果评估
- 针对Leo情况的定制化建议
- 实施路线图（1-6个月）

**更新时间**: 2026年1月5日

### 思考框架

**路径**: `docs/analysis/pain-point-to-skill-framework.md`

**描述**: 从痛点到技能 - 思考框架 - 在创建技能前通过系统化思考确保解决真实痛点

**内容概要**:
- 为什么从痛点出发（而非技术出发）
- 第一阶段：痛点识别（发现真痛点、验证方法、描述模板）
- 第二阶段：痛点拆解（流程/角色/数据/动作维度、5Why分析法）
- 第三阶段：三维对标分析（平台能力、员工需求、重复动作）
- 第四阶段：评估与方案设计（评估矩阵、MVP定义、架构设计、风险评估）
- 实战案例：房源发布管理器完整思考过程
- 快速检查清单：创建技能前的10个问题

**适用场景**: Claude Code 技能创建、业务自动化需求分析、AI应用规划

**更新时间**: 2026年1月5日

---

## 更新日志

| 日期 | 项目 | 版本 | 更新内容 |
|------|------|------|----------|
| 2026-01-05 | 文档 | - | 新增思考框架到 docs/analysis/ |
| 2026-01-05 | 工具框架 | - | agent-skill-creator 移至 tools/ 子目录 |
| 2026-01-05 | 文档 | - | 新增个人档案到 docs/profile/ |
| 2026-01-05 | realestate-news-publisher | - | API切换至MiniMax |
| 2026-01-04 | realestate-news-publisher-cskill | 1.0.0 | 初始版本，支持资讯收集和发布 |
| 2026-01-04 | content-layout-leo-cskill | 1.0.0 | 初始版本，10种排版风格 |

---

## 作者信息

**Leo Liu**

- GitHub: [@LinLiu2018](https://github.com/LinLiu2018)
- 技能仓库: [leo-skills](https://github.com/LinLiu2018/leo-skills)

---

*最后更新: 2026-01-05*
