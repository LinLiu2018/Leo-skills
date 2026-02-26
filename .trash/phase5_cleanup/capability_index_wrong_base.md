# Leo AI System - 能力索引

> **自动生成** - 2026-02-26 09:29:59
>
> 本文件由 `scripts/update_capability_index.py` 自动生成
> 请勿手动编辑，运行脚本即可更新

---

## 📊 统计概览

| 类型 | 数量 | 描述 |
|------|------|------|
| 🛠️ Skills | 0 | 可执行技能 |
| 🤖 Agents | 0 | 智能代理 |
| 🔄 Workflows | 0 | 工作流定义 |

**总计**: 0 个能力单元

---

## 🛠️ Skills 索引

暂无 Skills

---

## 🤖 Agents 索引

暂无 Agents

---

## 🔄 Workflows 索引

暂无 Workflows

---

## 📁 快速导航

### 按分类浏览 Skills

暂无分类

---

## 📝 使用说明

### 通过意图识别调用

系统会根据用户输入自动匹配最合适的技能或代理：

```python
from leo_orchestrator.intent_recognizer import get_intent_recognizer

recognizer = get_intent_recognizer()
match = recognizer.recognize("帮我研究量子计算")

# 返回：IntentMatch(intent_type='agent', target='research_agent', confidence=0.9)
```

### 直接通过 Registry 调用

```python
from leo_orchestrator.registry import get_registry

registry = get_registry()
skill = registry.get_skill('web_search_skill')
agent = registry.get_agent('research_agent')
```

### 执行工作流

```python
from leo_orchestrator.workflow_engine import WorkflowEngine

engine = WorkflowEngine(agents)
result = engine.execute_from_yaml('src/leo_workflows/definitions/content_pipeline.yaml')
```

---

*最后更新: 2026-02-26 09:29:59*
