# Leo Skills Collection

**Leo 的 Claude Code 技能合集** - 按功能分类整理的 AI 技能库

---

## 简介

这是我的个人 Claude Code 技能仓库，按照功能模块分类管理，方便高效渐进式加载和使用。

---

## 技能分类

### 📝 内容创作类 (content-creation)

| 技能 | 描述 | 激活词 |
|------|------|--------|
| [realestate-news-publisher-cskill](content-creation/realestate-news-publisher-cskill/) | 房产资讯自动化发布 - 收集政策、市场资讯，AI生成并发布到公众号 | "发布房产资讯"、"生成楼市分析" |
| [content-layout-leo-cskill](content-creation/content-layout-leo-cskill/) | 智能内容排版 - 多平台排版，10种风格，AI图片匹配 | "帮我排版"、"生成公众号格式" |

### 📊 数据分析类 (data-analysis)

*待补充*

### 🤖 自动化类 (automation)

*待补充*

### 🔧 工具类 (utilities)

| 技能 | 描述 | 激活词 |
|------|------|--------|
| [research-assistant-cskill](utilities/research-assistant-cskill/) | 智能研究助手 - 文献调研、信息整合、知识管理 | "帮我研究"、"文献调研"、"信息整理" |
| [obsidian-sync-cskill](utilities/obsidian-sync-cskill/) | Obsidian同步技能 - Claude/Leo输出同步到Obsidian第二大脑 | "保存到Obsidian"、"同步笔记"、"创建日记" |
| [web-search-cskill](utilities/web-search-cskill/) | 网络搜索技能 - 网络搜索和信息收集 | "搜索"、"查找资料" |

---

## 🛠️ 工具框架 (tools)

| 技能 | 描述 | 激活词 |
|------|------|--------|
| [agent-skill-creator](tools/agent-skill-creator/) | 技能创建元技能 - 自动化创建完整Claude技能 | "创建agent"、"自动化工作流"、"创建技能" |
| [article-to-prototype-cskill](tools/article-to-prototype-cskill/) | 文章转代码原型 - 从技术文档生成可执行代码 | "从论文生成代码"、"实现这个算法" |
| [project-marketing-doc-generator-cskill](tools/project-marketing-doc-generator-cskill/) | 营销文档生成器 - 快速生成商业项目营销资料 | "生成营销文档"、"创建销售手册"、"项目资料" |

---

## 快速使用

### 方式一：注册单个技能

```bash
# 符号链接到 Claude Code 技能目录
ln -s ~/ai-agents-workspace/leo-skills/content-creation/realestate-news-publisher-cskill ~/.claude/skills/
```

### 方式二：批量注册所有技能

```bash
# 批量创建符号链接
for skill in ~/ai-agents-workspace/leo-skills/*/*-cskill; do
    ln -s "$skill" ~/.claude/skills/
done
```

### 方式三：渐进式加载

根据需要，按分类加载：

```bash
# 只加载内容创作类技能
for skill in ~/ai-agents-workspace/leo-skills/content-creation/*-cskill; do
    ln -s "$skill" ~/.claude/skills/"
done
```

---

## 技能开发规范

### 目录结构

```
category-name/
└── skill-name-cskill/
    ├── .claude-plugin/
    │   └── marketplace.json    # 技能元数据
    ├── SKILL.md                # 技能文档
    ├── README.md               # 说明文档
    ├── config/                 # 配置文件
    ├── scripts/                # 核心代码
    │   ├── main.py            # 入口文件
    │   ├── collectors/        # 数据收集
    │   ├── analyzers/         # 数据分析
    │   ├── generators/        # 内容生成
    │   └── publishers/        # 内容发布
    └── requirements.txt        # Python依赖
```

### 命名规范

- 技能目录：`{功能}-{类型}-cskill`
- 分类目录：英文小写，用连字符分隔

### 元数据规范

每个技能的 `.claude-plugin/marketplace.json` 必须包含：

```json
{
  "name": "skill-name-cskill",
  "version": "1.0.0",
  "description": "简短描述",
  "author": "Leo Liu",
  "keywords": ["关键词"],
  "activation": {
    "keywords": ["激活词1", "激活词2"]
  }
}
```

---

## 版本信息

- **创建者**: Leo Liu
- **创建时间**: 2026-01-04
- **最后更新**: 2026-01-08
- **技能数量**: 8个
- **分类数量**: 5个 (内容创作2、工具3、工具框架3、数据分析0、自动化0)

---

## 技能清单

详细清单请查看 [SKILLS_MANIFEST.md](SKILLS_MANIFEST.md)
