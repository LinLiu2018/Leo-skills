# Obsidian Sync Skill - Claude Skill

将Claude对话、Leo System输出与Obsidian第二大脑无缝集成的同步技能。

**Version:** 1.0.0
**Created:** 2025-01-12
**Author:** Claude Code

---

## What This Skill Does

Obsidian Sync Skill 自动化Claude/Leo与Obsidian的知识管理工作流：

- **📥 快速捕获** - 将Claude对话输出保存到Obsidian Inbox
- **📝 笔记创建** - 使用模板创建结构化笔记
- **🔗 自动链接** - 智能添加双向链接和标签
- **📁 智能归档** - 按类型自动分类到对应文件夹
- **📊 MOC管理** - 自动更新内容地图索引
- **🔄 Leo集成** - 与Leo System其他Skill输出无缝对接

---

## When To Use

### 快速捕获Claude输出
```
"保存这段对话到Obsidian"
"将这个代码片段存入笔记"
"把研究结果保存到我的知识库"
```

### 创建结构化笔记
```
"创建一个关于Python最佳实践的笔记"
"用日记模板创建今日笔记"
"创建项目笔记：Leo System开发"
```

### 保存Leo输出
```
"保存排版结果到Obsidian"
"将研究报告归档到知识库"
"保存营销文档到项目文件夹"
```

### 知识管理
```
"更新编程MOC索引"
"添加链接到相关笔记"
"给这个笔记添加标签"
```

---

## When NOT To Use

- 需要直接编辑Obsidian中已有复杂笔记时
- Obsidian插件可以更好完成的任务（如Dataview查询）
- 需要图形化操作时（如调整图谱视图）

---

## How To Use

### 1. 配置Vault路径

首先配置你的Obsidian Vault路径：

```python
from scripts.main import ObsidianSync

# 初始化，指定Vault路径
sync = ObsidianSync(vault_path="D:/Obsidian/MySecondBrain")
```

或在配置文件中设置：
```yaml
# config/config.yaml
vault_path: "D:/Obsidian/MySecondBrain"
default_folder: "00-Inbox"
```

### 2. 快速捕获

```python
# 快速保存内容到Inbox
sync.quick_capture(
    content="这是Claude对话的重要内容...",
    title="Python装饰器原理"
)
```

### 3. 创建结构化笔记

```python
# 使用模板创建笔记
sync.create_note(
    title="机器学习入门",
    content="## 核心概念\n\n机器学习是...",
    template="research",  # 使用研究笔记模板
    folder="30-Resources/AI",
    tags=["机器学习", "AI", "学习笔记"],
    links=["深度学习", "神经网络"]
)
```

### 4. 保存Leo Skill输出

```python
# 保存content-layout输出
sync.save_leo_output(
    content=layout_result,
    skill_name="content-layout",
    project="房产营销",
    auto_link=True
)

# 保存research-assistant输出
sync.save_leo_output(
    content=research_result,
    skill_name="research-assistant",
    topic="AI发展趋势"
)
```

### 5. 创建日记

```python
# 创建今日日记
sync.create_daily_note(
    plan=["完成Leo System文档", "学习Obsidian插件开发"],
    notes="今天与Claude协作完成了..."
)
```

### 6. 更新MOC

```python
# 更新内容地图
sync.update_moc(
    moc_name="编程MOC",
    add_links=["Python装饰器", "异步编程"]
)
```

---

## Commands Reference

| Command | Description |
|---------|-------------|
| `quick_capture(content, title)` | 快速保存到Inbox |
| `create_note(title, content, **kwargs)` | 创建结构化笔记 |
| `create_daily_note(**kwargs)` | 创建日记 |
| `save_leo_output(content, skill_name, **kwargs)` | 保存Leo输出 |
| `update_moc(moc_name, add_links)` | 更新MOC索引 |
| `add_links(note_path, links)` | 添加链接到笔记 |
| `add_tags(note_path, tags)` | 添加标签到笔记 |
| `move_note(note_path, target_folder)` | 移动笔记 |
| `search_notes(query)` | 搜索笔记 |
| `get_recent_notes(limit)` | 获取最近笔记 |

---

## Templates

### 内置模板

| 模板名 | 用途 |
|--------|------|
| `default` | 通用笔记模板 |
| `daily` | 日记模板 |
| `research` | 研究笔记模板 |
| `claude` | Claude对话记录模板 |
| `leo-output` | Leo输出保存模板 |
| `project` | 项目笔记模板 |
| `moc` | 内容地图模板 |

### 模板变量

```markdown
{{date}}        - 当前日期 (YYYY-MM-DD)
{{time}}        - 当前时间 (HH:mm)
{{datetime}}    - 完整日期时间
{{title}}       - 笔记标题
{{tags}}        - 标签列表
{{links}}       - 链接列表
{{content}}     - 主体内容
```

---

## Folder Structure

推荐的Vault结构（自动创建）：

```
MySecondBrain/
├── 00-Inbox/              # 快速捕获
├── 01-Daily/              # 日记
├── 10-Projects/           # 项目笔记
├── 20-Areas/              # 领域笔记
├── 30-Resources/          # 资源笔记
├── 40-Archives/           # 归档
├── Leo-Outputs/           # Leo System输出
│   ├── content-layout/
│   ├── research/
│   ├── marketing/
│   └── analysis/
├── Claude-Notes/          # Claude对话笔记
└── Templates/             # 模板
```

---

## Configuration

### config/config.yaml

```yaml
# Obsidian Vault配置
vault_path: "D:/Obsidian/MySecondBrain"  # 你的Vault路径
default_folder: "00-Inbox"
template_folder: "Templates"

# 自动化设置
auto_create_folders: true
auto_add_metadata: true
auto_link_suggestions: true

# 元数据设置
default_tags:
  - claude生成
add_source_info: true
add_timestamp: true

# Leo输出设置
leo_output_folder: "Leo-Outputs"
skill_folders:
  content-layout: "content-layout"
  research-assistant: "research"
  project-marketing-doc-generator: "marketing"
  data-analyzer: "analysis"

# 日记设置
daily_folder: "01-Daily"
daily_format: "YYYY-MM-DD"

# MOC设置
moc_folder: "MOCs"
auto_update_moc: true
```

---

## Integration with Leo System

### 与其他Skill联动

```python
from leo_system import get_system

system = get_system()

# 1. 使用research-assistant搜索
research_result = system.call_skill(
    "research-assistant-cskill",
    "search_papers",
    query="transformer attention mechanism"
)

# 2. 自动保存到Obsidian
system.call_skill(
    "obsidian-sync-cskill",
    "save_leo_output",
    content=research_result,
    skill_name="research-assistant",
    topic="Transformer研究"
)
```

### 工作流集成

```python
# content-pipeline + obsidian-sync
workflow_result = system.run_workflow(
    "content-pipeline",
    topic="房地产市场分析"
)

# 保存工作流输出
system.call_skill(
    "obsidian-sync-cskill",
    "save_workflow_output",
    workflow_name="content-pipeline",
    result=workflow_result
)
```

---

## Examples

### Example 1: 保存Claude对话

```python
from scripts.main import ObsidianSync

sync = ObsidianSync()

# 保存重要的Claude对话内容
sync.quick_capture(
    content="""
## 问题
如何在Python中实现单例模式？

## Claude回答
单例模式确保一个类只有一个实例...

```python
class Singleton:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

## 我的理解
- 使用类变量存储唯一实例
- __new__方法控制实例创建
""",
    title="Python单例模式",
    tags=["Python", "设计模式", "claude笔记"]
)
```

### Example 2: 创建项目笔记

```python
sync.create_note(
    title="Leo System开发记录",
    content="""
## 项目概述
Leo是一个统一的Skills和Subagents管理系统...

## 开发进度
- [x] 基础架构
- [x] Skill注册系统
- [ ] Obsidian同步功能

## 关键决策
1. 使用YAML配置Agent
2. 支持动态Skill加载
""",
    template="project",
    folder="10-Projects/Leo-System",
    tags=["项目", "AI", "开发"],
    links=["Python最佳实践", "Agent设计模式"]
)
```

### Example 3: 自动化日记

```python
# 每日自动创建日记
sync.create_daily_note(
    plan=[
        "完成Obsidian Sync Skill",
        "测试Leo工作流",
        "整理学习笔记"
    ],
    notes="""
### Claude协作
- 完成了Obsidian同步功能开发
- 学习了知识管理最佳实践

### 收获
- 理解了PARA方法论
- 掌握了Zettelkasten笔记法
""",
    links=["Leo System开发记录"]
)
```

### Example 4: 批量保存研究结果

```python
# 批量保存多个研究主题
topics = ["大语言模型", "知识图谱", "多模态AI"]

for topic in topics:
    # 使用Leo研究
    result = system.call_skill(
        "research-assistant-cskill",
        "generate_literature_review",
        topic=topic,
        num_papers=10
    )

    # 保存到Obsidian
    sync.save_leo_output(
        content=result,
        skill_name="research-assistant",
        topic=topic,
        folder="30-Resources/AI研究"
    )
```

---

## Best Practices

### 1. 捕获原则

- **及时捕获** - 有价值的内容立即保存
- **先捕获后整理** - 不要在捕获时过度思考
- **添加上下文** - 记录为什么保存这个内容

### 2. 链接策略

- **主动链接** - 保存时思考与已有笔记的关联
- **双向链接** - 使用[[笔记名]]创建双向链接
- **MOC索引** - 定期更新内容地图

### 3. 标签使用

```yaml
# 推荐的标签体系
来源标签:
  - #claude生成
  - #leo-output
  - #手动整理

状态标签:
  - #待整理
  - #已完成
  - #需复习

类型标签:
  - #概念
  - #方法
  - #案例
  - #代码
```

### 4. 定期维护

- **每日**: 处理Inbox，创建日记
- **每周**: 整理笔记，更新MOC
- **每月**: 归档旧内容，优化结构

---

## Troubleshooting

### Vault路径错误
```
✓ 确保路径使用正斜杠或双反斜杠
✓ 检查路径是否存在
✓ 确保有写入权限
```

### 编码问题
```
✓ 所有文件使用UTF-8编码
✓ 文件名避免特殊字符
```

### 模板不生效
```
✓ 检查模板文件是否存在
✓ 确认模板变量格式正确
```

---

## Dependencies

```
pyyaml>=6.0
python-frontmatter>=1.0.0
python-dateutil>=2.8.0
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-01-12 | Initial release |

---

## License

Apache 2.0 - See LICENSE file for details
