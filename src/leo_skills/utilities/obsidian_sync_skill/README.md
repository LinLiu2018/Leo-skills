# Obsidian Sync Skill

将Claude对话、Leo System输出与Obsidian第二大脑无缝集成的同步技能。

## 快速开始

### 1. 配置Vault路径

编辑 `config/config.yaml`：

```yaml
vault_path: "D:/Obsidian/MySecondBrain"  # 改为你的Vault路径
```

### 2. 基本使用

```python
from scripts.main import ObsidianSync

# 初始化
sync = ObsidianSync()

# 快速捕获内容
sync.quick_capture("重要内容...", title="学习笔记")

# 创建日记
sync.create_daily_note(plan=["任务1", "任务2"])

# 保存Claude对话
sync.save_claude_note(
    content="Claude的回答...",
    title="Python技巧",
    question="如何优化Python代码？"
)

# 保存Leo输出
sync.save_leo_output(
    content=leo_result,
    skill_name="research-assistant",
    topic="AI发展趋势"
)
```

## 功能特性

- 📥 **快速捕获** - 一键保存到Inbox
- 📝 **模板系统** - 7种内置模板
- 🔗 **自动链接** - 智能添加双向链接
- 📁 **智能归档** - 按类型自动分类
- 📊 **MOC管理** - 自动更新内容地图
- 🔄 **Leo集成** - 与其他Skill无缝对接

## 目录结构

```
obsidian_sync_skill/
├── SKILL.md           # 详细使用文档
├── README.md          # 快速入门
├── scripts/
│   └── main.py        # 核心代码
├── config/
│   └── config.yaml    # 配置文件
└── templates/         # 笔记模板
    ├── default.md
    ├── daily.md
    ├── research.md
    ├── claude.md
    ├── leo-output.md
    ├── project.md
    └── moc.md
```

## 详细文档

查看 [SKILL.md](SKILL.md) 获取完整使用指南。

## 依赖

```
pyyaml>=6.0
```

## License

Apache 2.0
