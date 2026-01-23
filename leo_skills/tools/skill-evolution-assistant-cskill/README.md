# 技能进化助手 (Skill Evolution Assistant)

## 概述

技能进化助手是一个**元技能**，可以自动为所有现有技能添加进化能力，无需手动配置。

## 功能特性

### 🔍 自动扫描
- 扫描所有技能目录
- 识别技能结构
- 检测是否已集成进化框架

### 🤖 自动改造
- 自动修改技能代码
- 继承EvolvableSkill基类
- 添加进化配置文件
- 创建备份以便回滚

### ✅ 自动验证
- 验证代码改造是否成功
- 检查必要组件是否完整
- 提供详细的验证报告

## 使用方法

### 1. 扫描所有技能

```bash
cd leo-skills/tools/skill-evolution-assistant-cskill
python skill_evolution_assistant.py scan
```

输出示例：
```json
{
  "success": true,
  "total_skills": 8,
  "skills": [
    {
      "name": "web-search-cskill",
      "category": "utilities",
      "has_evolution": false
    },
    ...
  ]
}
```

### 2. 分析哪些技能需要改造

```bash
python skill_evolution_assistant.py analyze
```

输出示例：
```json
{
  "success": true,
  "total_skills": 8,
  "needs_evolution": 6,
  "has_evolution": 2,
  "needs_evolution_list": [
    "web-search-cskill",
    "data-analyzer-cskill",
    ...
  ]
}
```

### 3. 改造单个技能

```bash
python skill_evolution_assistant.py transform web-search-cskill
```

### 4. 改造所有技能（一键完成）

```bash
python skill_evolution_assistant.py transform_all
```

这将自动改造所有未集成进化框架的技能！

## 改造过程

### 自动执行的步骤：

1. **备份原文件** → `.backup/` 目录
2. **修改代码**：
   - 添加 `from core.evolution import EvolvableSkill`
   - 修改类继承：`class MySkill(EvolvableSkill)`
   - 添加 `super().__init__()` 调用
   - 重命名主方法为 `_execute_core()`
3. **添加配置** → `config/evolution_config.yaml`
4. **验证改造** → 检查所有必要组件

### 改造前后对比：

**改造前：**
```python
class WebSearchSkill:
    def __init__(self, config=None):
        self.config = config or {}

    def search(self, query, **kwargs):
        # 搜索逻辑
        return results
```

**改造后：**
```python
from core.evolution import EvolvableSkill

class WebSearchSkill(EvolvableSkill):
    def __init__(self, config=None):
        super().__init__(
            skill_name="web-search-cskill",
            config_path=str(Path(__file__).parent.parent / "config" / "config.yaml")
        )
        self.config = config or {}

    def _execute_core(self, action="search", **kwargs):
        if action == "search":
            return self.search(**kwargs)

    def search(self, query, **kwargs):
        # 搜索逻辑（保持不变）
        return {
            'success': True,
            'results': results,
            'quality_score': 0.85  # 用于进化学习
        }
```

## 安全机制

### 备份与回滚
- 每次改造前自动创建备份
- 改造失败自动回滚
- 备份保存在 `.backup/` 目录

### 验证检查
- 检查import是否正确
- 检查类继承是否正确
- 检查_execute_core方法是否存在
- 检查evolution_config.yaml是否存在

## 配置选项

编辑 `config/config.yaml` 可以自定义：

```yaml
scan:
  categories:  # 扫描的分类
    - content-creation
    - utilities
  exclude:     # 排除的技能
    - skill-evolution-assistant-cskill

transform:
  create_backup: true   # 是否创建备份
  auto_test: false      # 是否自动测试
  keep_original: true   # 是否保留原方法
```

## 作为技能使用

也可以在代码中使用：

```python
from skill_evolution_assistant import SkillEvolutionAssistant

assistant = SkillEvolutionAssistant()

# 扫描
result = assistant.execute(action="scan")

# 分析
result = assistant.execute(action="analyze")

# 改造单个
result = assistant.execute(action="transform", skill_name="web-search-cskill")

# 改造所有
result = assistant.execute(action="transform_all")
```

## 注意事项

1. **首次使用前建议**：
   - 先运行 `scan` 和 `analyze` 了解情况
   - 先用 `transform` 改造一个简单技能测试
   - 确认无误后再运行 `transform_all`

2. **改造后需要**：
   - 测试技能功能是否正常
   - 检查进化配置是否合适
   - 运行技能10+次以触发学习

3. **如果改造失败**：
   - 检查 `.backup/` 目录中的备份
   - 手动恢复或重新运行
   - 查看错误信息调整代码

## 版本信息

- 版本：1.0.0
- 创建日期：2026-01-11
- 作者：Leo AI Agent System
- 类型：元技能（Meta-Skill）

## 相关文档

- [进化框架文档](../../core/evolution/README.md)
- [进化框架实施报告](../../../SKILL_EVOLUTION_IMPLEMENTATION_REPORT.md)
- [快速开始指南](../../../QUICK_START_EVOLUTION.md)
