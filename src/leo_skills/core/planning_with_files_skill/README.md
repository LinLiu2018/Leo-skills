# Planning with Files Skill

基于 [OthmanAdi/planning-with-files](https://github.com/OthmanAdi/planning-with-files) 的 Leo System 版本。

## 简介

这是一个 **Manus 风格的持久化规划技能**，通过文件系统作为 AI 的"外部存储"，解决了 AI 代理的上下文丢失、目标漂移等问题。

## 核心理念

```
Context Window = RAM（易失、有限）
Filesystem = Disk（持久、无限）
```

## 三文件模式

| 文件 | 用途 |
|------|------|
| `task_plan.md` | 阶段跟踪、进度、决策 |
| `findings.md` | 研究发现、技术决策 |
| `progress.md` | 会话日志、测试结果 |

## 使用方法

1. 复制 `templates/` 下的三个模板到你的项目目录
2. 根据任务填写 `task_plan.md` 的目标和阶段
3. 工作过程中持续更新三个文件
4. 遵循"2-动作规则"：每2次搜索/浏览后更新 findings.md

## 关键规则

1. **先创建计划** - 永不在没有 task_plan.md 的情况下开始
2. **2-动作规则** - 每2次操作后保存发现
3. **决策前阅读** - 重大决策前重读计划
4. **行动后更新** - 完成阶段后更新状态
5. **记录所有错误** - 建立知识防止重复
6. **永不重复失败** - 跟踪尝试，改变方法

## 与 Leo System 集成

此技能已集成到 Leo System，可与以下组件配合：

- `research_agent` - 调研时记录发现
- `content_pipeline` - 内容创作跟踪进度
- `realestate_pipeline` - 房产项目完整规划

## 致谢

- 原项目: [OthmanAdi/planning-with-files](https://github.com/OthmanAdi/planning-with-files)
- 灵感来源: Manus AI 的上下文工程方法
