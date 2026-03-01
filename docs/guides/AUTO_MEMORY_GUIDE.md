# 全自动共享记忆系统 - 使用指南

> 无需配置，自动记录，跨 Agent 共享

---

## 核心特性

| 特性 | 说明 |
|------|------|
| **自动记录** | 所有交互自动捕获，无需显式调用 |
| **跨 Agent 共享** | 不同 Agent 自动获取相关历史记忆 |
| **主动注入** | 系统主动为 Agent 提供上下文 |
| **错误学习** | 自动记录失败和修正 |
| **智能压缩** | 自动归档旧记忆，保持性能 |

---

## 快速开始

### 1. 系统自动初始化

只需导入即可，无需其他配置：

```python
from leo_memory import get_auto_memory

# 记忆系统已自动启动
memory = get_auto_memory()
```

### 2. 自动记录

系统会自动记录，你也可以主动记录重要信息：

```python
from leo_memory import auto_record

# 自动记录
auto_record(
    event_type="user_decision",
    content="客户选择了方案A",
    agent="sales_agent",
    importance=4,
    tags=["decision", "preference"]
)
```

### 3. 自动获取上下文

Agent 会自动获得相关记忆：

```python
from leo_memory import get_context

# 自动获取与当前任务相关的历史
context = get_context("villa_agent", "客户需要度假别墅")
# 包含：相关记忆、用户偏好、建议行动
```

---

## Agent 集成方式

### 方式 1: 装饰器（推荐）

```python
from leo_memory import auto_memorize

@auto_memorize
class MyAgent:
    name = "my_agent"

    def execute(self, task, context=None):
        # 自动获得记忆注入
        if context and '_injected_memory' in context:
            relevant = context['_injected_memory']

        # 执行任务...
        return result
```

### 方式 2: 混入类

```python
from leo_memory import AgentMemoryMixin

class MyAgent(AgentMemoryMixin):
    def execute(self, task, context=None):
        # 主动记录
        self.remember("key", "value", importance=4)

        # 主动回忆
        related = self.recall("查询关键词")

        # 获取上下文
        ctx = self.get_memory_context(task)
```

### 方式 3: 手动调用

```python
from leo_memory import get_auto_memory

class MyAgent:
    def __init__(self):
        self.memory = get_auto_memory()

    def execute(self, task, context=None):
        # 记录开始
        call_id = self.memory.auto_record(...)

        # 获取相关记忆
        relevant = self.memory.recall(query=task)

        # 记录结果
        self.memory.auto_record(...)
```

---

## 系统级事件捕获

```python
from leo_memory import get_system_capture

capture = get_system_capture()

# 捕获用户输入
capture.capture_user_input("用户消息", source="feishu")

# 捕获工具调用
capture.capture_tool_call("web_search", {"query": "xxx"}, result)

# 捕获用户修正（用于学习）
capture.capture_correction("原内容", "修正后", "原因")

# 捕获系统决策
capture.capture_decision("选择Agent A", context, "理由")
```

---

## 记忆查询

```python
from leo_memory import get_auto_memory

memory = get_auto_memory()

# 通用查询
results = memory.recall(
    query="别墅投资",
    agent="villa_agent",
    event_type="agent_response",
    tags=["investment"],
    time_range=24,  # 最近24小时
    top_k=5
)

# 获取会话摘要
summary = memory.get_session_summary()
print(f"当前会话: {summary['memory_count']} 条记忆")

# 获取 Agent 上下文
context = memory.get_context_for_agent("agent_name", "task")
```

---

## 用户偏好学习

```python
from leo_memory import (
    record_positive_feedback,
    record_negative_feedback,
    get_preference_learner
)

# 记录正面反馈
record_positive_feedback("PDF生成", {"font_size": "17px"})

# 记录负面反馈
record_negative_feedback("排版结果", {"issue": "表格截断"})

# 获取学习报告
learner = get_preference_learner()
report = learner.export_learning_report()
```

---

## 文件存储位置

```
leo_knowledge/memory/
├── auto_storage/
│   ├── session_<id>.json      # 会话记忆
│   ├── memory_index.json       # 记忆索引
│   └── archive_202602.json     # 归档记忆
```

---

## 最佳实践

1. **让系统自动工作** - 大多数情况下无需干预
2. **重要事件标记** - 关键决策使用 importance=5
3. **合理打标签** - 便于后续检索
4. **定期查看学习报告** - 了解系统学到了什么

---

## 故障排查

| 问题 | 解决 |
|------|------|
| 记忆未记录 | 检查日志级别，确保不是 DEBUG 被过滤 |
| 记忆不共享 | 确认所有 Agent 使用同一个 get_auto_memory() |
| 性能问题 | 系统会自动压缩旧记忆，无需手动清理 |

---

*系统自动工作，你只需专注于业务逻辑。*
