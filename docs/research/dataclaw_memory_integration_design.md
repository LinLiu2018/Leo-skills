# DataClaw 与 Leo 共享记忆系统联动设计方案

> **文档类型**: 技术设计方案
> **设计目标**: 实现 DataClaw 导出数据与 Leo 共享记忆系统的深度联动
> **版本**: 1.0.0
> **日期**: 2026-02-28

---

## 1. 设计概述

### 1.1 设计目标

基于 DataClaw 项目研究，设计一套完整的技术方案，实现：

1. **数据联动**: DataClaw 导出的会话数据 → Leo 共享记忆系统
2. **价值集成**: 将导出数据转化为可复用的知识资产
3. **自动化流程**: 最小人工干预的自动知识提取与存储

### 1.2 核心问题

| 问题 | 说明 |
|------|------|
| **数据格式差异** | DataClaw 输出 JSONL，记忆系统使用 Markdown + 结构化条目 |
| **语义提取** | 如何从对话中自动提取有价值的知识 |
| **知识分类** | 提取的知识应该归属到哪个记忆分类 |
| **增量更新** | 如何处理新导出数据与已有记忆的关系 |
| **隐私边界** | 哪些数据可以进入记忆系统，哪些需要额外保护 |

---

## 2. 系统架构设计

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          DataClaw Memory Integration                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐       │
│  │   DataClaw      │     │   Knowledge     │     │  Shared Memory  │       │
│  │   Exporter      │ --> │   Extractor     │ --> │   System        │       │
│  │                 │     │                 │     │                 │       │
│  │ • 导出会话      │     │ • 语义分析      │     │ • 结构化存储    │       │
│  │ • 隐私处理      │     │ • 知识分类      │     │ • 增量更新      │       │
│  │ • 格式转换      │     │ • 重要性评估    │     │ • 检索服务      │       │
│  └─────────────────┘     └─────────────────┘     └─────────────────┘       │
│          │                      │                      │                    │
│          ▼                      ▼                      ▼                    │
│  ┌─────────────────────────────────────────────────────────────────┐       │
│  │                     Workflow Engine                              │       │
│  │  • 自动化流水线    • 定时任务    • 触发器机制                     │       │
│  └─────────────────────────────────────────────────────────────────┘       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 组件详细设计

#### 组件 1: DataClaw Exporter (数据导出层)

```python
class DataClawExporter:
    """
    DataClaw 导出器封装

    职责:
    - 调用 DataClaw CLI 导出会话数据
    - 处理导出配置（源、隐私级别、过滤条件）
    - 返回标准化的会话数据
    """

    def export_sessions(
        self,
        source: str = "all",  # claude|codex|gemini|opencode|openclaw|all
        output_format: str = "jsonl",
        privacy_level: str = "strict",
        date_range: Optional[Tuple[datetime, datetime]] = None,
        project_filter: Optional[List[str]] = None
    ) -> ExportResult:
        """导出会话数据"""
        pass
```

#### 组件 2: Knowledge Extractor (知识提取层)

```python
class KnowledgeExtractor:
    """
    知识提取器

    职责:
    - 解析 DataClaw 导出的会话数据
    - 提取有价值的知识点
    - 分类并评估重要性
    """

    # 知识类型定义
    KNOWLEDGE_TYPES = {
        "user_preference": {
            "patterns": ["我喜欢", "我偏好", "我希望", "我不喜欢"],
            "category": "user_profile",
            "importance": 4
        },
        "project_decision": {
            "patterns": ["决定", "选择", "采用", "方案是", "架构是"],
            "category": "project_knowledge",
            "importance": 5
        },
        "technical_solution": {
            "patterns": ["解决方案", "修复了", "解决了", " workaround", "最佳实践"],
            "category": "technical_knowledge",
            "importance": 4
        },
        "skill_usage": {
            "patterns": ["技能", "skill", "agent", "工作流", "workflow"],
            "category": "system_knowledge",
            "importance": 3
        },
        "error_learning": {
            "patterns": ["错误", "失败", "exception", "bug", "问题"],
            "category": "learned_errors",
            "importance": 4
        }
    }

    def extract_from_session(self, session_data: Dict) -> List[KnowledgeItem]:
        """从单个会话中提取知识"""
        pass

    def classify_knowledge(self, content: str) -> KnowledgeClassification:
        """对知识进行分类和重要性评估"""
        pass
```

#### 组件 3: Memory Integrator (记忆整合层)

```python
class MemoryIntegrator:
    """
    记忆整合器

    职责:
    - 将提取的知识写入共享记忆系统
    - 处理重复和冲突
    - 维护知识关联
    """

    def integrate(
        self,
        knowledge_items: List[KnowledgeItem],
        merge_strategy: str = "smart"  # overwrite|skip|smart
    ) -> IntegrationResult:
        """整合知识到记忆系统"""
        pass

    def detect_duplicates(self, new_item: KnowledgeItem) -> Optional[MemoryEntry]:
        """检测重复知识"""
        pass

    def merge_knowledge(
        self,
        existing: MemoryEntry,
        new: KnowledgeItem
    ) -> MemoryEntry:
        """合并新旧知识"""
        pass
```

---

## 3. 数据映射设计

### 3.1 DataClaw → 共享记忆 映射表

| DataClaw 字段 | 共享记忆字段 | 转换规则 |
|---------------|--------------|----------|
| `session_id` | `context.session_id` | 原样保留，用于追溯 |
| `project` | `context.project` | 映射为项目上下文 |
| `model` | `context.model` | 记录使用的 AI 模型 |
| `messages[].content` | `value` | 提取有价值的内容 |
| `messages[].role` | `context.role` | 区分用户/助手内容 |
| `stats.tool_uses` | `context.tools` | 记录使用的工具 |
| `start_time` | `created_at` | 时间戳格式转换 |
| 语义分析结果 | `category` | 根据内容自动分类 |
| 重要性评估 | `importance` | 1-5 评分 |

### 3.2 知识分类体系

```
shared_memory.md 结构扩展:

## user_profile          ← 用户偏好、习惯、沟通风格
## project_knowledge     ← 项目决策、架构选择、技术方案
## technical_knowledge   ← 技术解决方案、最佳实践、技巧
## system_knowledge      ← 技能使用模式、工作流优化
## learned_errors        ← 错误记录、避坑指南
## session_context       ← 会话元数据（新分类）
```

### 3.3 数据流转换图

```
DataClaw JSONL
├── session_id ────────┐
├── project ───────────┼──► MemoryEntry.context
├── model ─────────────┤
├── messages ──────────┤
│   ├── user content ──┼──► KnowledgeExtractor
│   │                      ├── 用户偏好 ──► user_profile
│   │                      ├── 项目决策 ──► project_knowledge
│   │                      ├── 技术方案 ──► technical_knowledge
│   │                      └── 错误经验 ──► learned_errors
│   └── assistant content ─► (辅助理解上下文)
├── stats ─────────────┼──► MemoryEntry.context.stats
└── timestamps ────────┴──► MemoryEntry.created_at
```

---

## 4. 核心算法设计

### 4.1 知识提取算法

```python
def extract_knowledge_from_message(message: Dict, context: Dict) -> List[KnowledgeItem]:
    """
    从消息中提取知识

    算法步骤:
    1. 过滤无价值内容（问候、确认等）
    2. 识别知识模式
    3. 提取关键语句
    4. 去重和合并
    """
    items = []
    content = message.get("content", "")

    # 步骤 1: 过滤
    if is_trivial_content(content):
        return items

    # 步骤 2: 模式匹配
    for knowledge_type, config in KNOWLEDGE_TYPES.items():
        if matches_pattern(content, config["patterns"]):
            # 步骤 3: 提取关键语句
            extracted = extract_key_sentence(content, config["patterns"])

            item = KnowledgeItem(
                type=knowledge_type,
                content=extracted,
                category=config["category"],
                importance=config["importance"],
                context={
                    "session_id": context.get("session_id"),
                    "project": context.get("project"),
                    "message_role": message.get("role")
                }
            )
            items.append(item)

    # 步骤 4: 去重
    return deduplicate_items(items)
```

### 4.2 重复检测算法

```python
def detect_duplicate(new_item: KnowledgeItem, existing_entries: List[MemoryEntry]) -> Optional[MemoryEntry]:
    """
    检测知识是否已存在

    使用多种相似度算法:
    1. 精确匹配
    2. 关键词集合 Jaccard 相似度
    3. 语义相似度 (可选，使用 embeddings)
    """

    for entry in existing_entries:
        # 1. 精确匹配
        if normalize(new_item.content) == normalize(entry.value):
            return entry

        # 2. Jaccard 相似度
        jaccard = calculate_jaccard_similarity(
            extract_keywords(new_item.content),
            extract_keywords(entry.value)
        )
        if jaccard > 0.8:
            return entry

        # 3. 语义相似度（高级）
        # if semantic_similarity(new_item.content, entry.value) > 0.9:
        #     return entry

    return None
```

### 4.3 智能合并算法

```python
def smart_merge(existing: MemoryEntry, new: KnowledgeItem) -> MemoryEntry:
    """
    智能合并新旧知识

    策略:
    - 保留更详细的版本
    - 合并上下文信息
    - 更新重要性（取最大值）
    - 保留时间戳历史
    """

    # 选择更详细的值
    if len(new.content) > len(existing.value):
        value = new.content
    else:
        value = existing.value

    # 合并上下文
    merged_context = {**existing.context, **new.context}
    merged_context["merge_history"] = existing.context.get("merge_history", []) + [
        {"merged_at": datetime.now().isoformat(), "source": new.context.get("session_id")}
    ]

    return MemoryEntry(
        key=existing.key,
        value=value,
        category=existing.category,
        importance=max(existing.importance, new.importance),
        created_at=existing.created_at,  # 保留原始时间
        context=merged_context
    )
```

---

## 5. 工作流设计

### 5.1 自动化流水线

```yaml
# session_to_memory_pipeline.yaml
name: 会话到记忆流水线
description: 自动将 DataClaw 导出的会话转化为共享记忆

steps:
  - name: export_sessions
    agent: dataclaw_exporter
    description: 导出指定时间范围的会话
    timeout: 300
    retries: 2

  - name: extract_knowledge
    agent: knowledge_extractor
    description: 从会话中提取知识
    depends_on: export_sessions

  - name: classify_knowledge
    agent: knowledge_classifier
    description: 对知识进行分类和重要性评估
    depends_on: extract_knowledge

  - name: merge_to_memory
    agent: memory_integrator
    description: 整合到共享记忆系统
    depends_on: classify_knowledge

  - name: generate_report
    agent: report_generator
    description: 生成整合报告
    depends_on: merge_to_memory
```

### 5.2 触发机制

| 触发方式 | 说明 | 配置 |
|----------|------|------|
| **定时触发** | 每天/每周自动执行 | `cron: "0 3 * * *"` |
| **手动触发** | 用户主动发起 | 技能命令 `"整理最近会话"` |
| **事件触发** | 会话数量达到阈值 | `threshold: 100 sessions` |
| **工作流触发** | 项目阶段结束时 | Phase Checkpoint 后 |

### 5.3 定时任务配置

```bash
# OpenClaw 定时任务配置
openclaw cron add \
  --name session_to_memory_daily \
  --cron "0 3 * * *" \
  --tz Asia/Shanghai \
  --system-event "session_memory_sync" \
  --agent leo-assistant

# 参数说明:
# - 每天凌晨 3 点执行
# - 导出前一天的新会话
# - 提取并整合到共享记忆
```

---

## 6. 价值集成架构

### 6.1 三层价值转化模型

```
┌─────────────────────────────────────────────────────────────────┐
│                      三层价值转化模型                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Layer 3: 智慧层 (Wisdom)                                        │
│  ┌──────────────────────────────────────────────────────┐      │
│  │  • 决策支持       • 模式识别      • 预测建议          │      │
│  │  • 个性化优化     • 自动化改进                          │      │
│  └──────────────────────────────────────────────────────┘      │
│                          ▲                                     │
│  Layer 2: 知识层 (Knowledge)                                     │
│  ┌──────────────────────────────────────────────────────┐      │
│  │  • 最佳实践       • 错误模式      • 用户画像          │      │
│  │  • 项目经验       • 技能效果评估                        │      │
│  └──────────────────────────────────────────────────────┘      │
│                          ▲                                     │
│  Layer 1: 数据层 (Data)                                          │
│  ┌──────────────────────────────────────────────────────┐      │
│  │  • 原始会话       • 消息内容      • 工具调用          │      │
│  │  • 统计数据       • 时间戳                            │      │
│  └──────────────────────────────────────────────────────┘      │
│                                                                  │
│  DataClaw 导出 ──► KnowledgeExtractor ──► MemoryIntegrator     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 6.2 价值场景详细设计

#### 场景 1: 个性化优化

```python
class PersonalizationEngine:
    """个性化引擎 - 基于记忆系统优化 AI 响应"""

    def optimize_prompt(self, user_input: str) -> str:
        """
        基于用户历史偏好优化提示词

        1. 检索相关用户偏好
        2. 调整输出风格
        3. 添加上下文参考
        """
        memory = get_shared_memory()

        # 检索用户偏好
        preferences = memory.search(
            query=user_input,
            category="user_profile"
        )

        # 构建个性化上下文
        context = self._build_persona_context(preferences)

        return f"""
{context}

用户当前输入: {user_input}

请根据以上用户偏好提供个性化响应。
"""
```

#### 场景 2: 智能错误预防

```python
class ErrorPreventionEngine:
    """错误预防引擎 - 基于历史错误避免重复踩坑"""

    def check_potential_errors(self, task_description: str) -> List[ErrorWarning]:
        """
        检查任务是否与历史错误模式匹配

        1. 语义检索相似错误
        2. 匹配错误模式
        3. 返回预警和建议
        """
        memory = get_shared_memory()

        # 检索相关错误记录
        errors = memory.search(
            query=task_description,
            category="learned_errors"
        )

        warnings = []
        for error in errors:
            similarity = calculate_similarity(task_description, error.value)
            if similarity > 0.7:
                warnings.append(ErrorWarning(
                    pattern=error.value,
                    similarity=similarity,
                    solution=error.context.get("solution")
                ))

        return warnings
```

#### 场景 3: 项目知识沉淀

```python
class ProjectKnowledgeBase:
    """项目知识库 - 自动沉淀项目决策和经验"""

    def get_relevant_decisions(self, current_task: str) -> List[ProjectDecision]:
        """
        获取与当前任务相关的项目决策

        1. 按项目过滤
        2. 语义检索相关决策
        3. 按时间排序
        """
        memory = get_shared_memory()

        decisions = memory.search(
            query=current_task,
            category="project_knowledge"
        )

        return [
            ProjectDecision(
                content=d.value,
                timestamp=d.created_at,
                context=d.context
            )
            for d in decisions
        ]
```

### 6.3 技能推荐系统

```python
class SkillRecommendationEngine:
    """技能推荐引擎 - 基于历史使用推荐最佳技能"""

    def recommend_skills(self, user_input: str) -> List[SkillRecommendation]:
        """
        基于历史会话推荐合适的技能

        1. 分析用户输入意图
        2. 检索相似历史场景
        3. 统计技能成功率
        4. 返回推荐列表
        """
        memory = get_shared_memory()

        # 检索技能使用记录
        skill_usage = memory.search(
            query=user_input,
            category="system_knowledge"
        )

        # 统计分析
        recommendations = self._analyze_skill_effectiveness(skill_usage)

        return recommendations
```

---

## 7. 接口设计

### 7.1 技能接口

```python
class SessionToMemorySkill:
    """
    会话转记忆技能

    将 DataClaw 导出的会话数据转化为共享记忆
    """

    def execute(
        self,
        source: str = "all",
        date_range: Optional[str] = None,
        auto_classify: bool = True,
        merge_strategy: str = "smart"
    ) -> SkillResult:
        """
        执行会话到记忆的转换

        Args:
            source: 数据源 (claude|codex|gemini|opencode|openclaw|all)
            date_range: 时间范围 (如 "last_7_days", "last_month")
            auto_classify: 是否自动分类
            merge_strategy: 合并策略 (overwrite|skip|smart)

        Returns:
            SkillResult with:
            - exported_count: 导出会话数
            - extracted_count: 提取知识点数
            - integrated_count: 整合到记忆数
            - duplicates_skipped: 跳过的重复数
            - report: 详细报告
        """
        pass
```

### 7.2 API 接口

```python
# leo_orchestrator/api.py 扩展

class DataClawMemoryAPI:
    """DataClaw 记忆联动 API"""

    @staticmethod
    def sync_sessions_to_memory(
        source: str = "all",
        since: Optional[datetime] = None
    ) -> SyncResult:
        """同步会话到记忆系统"""
        pass

    @staticmethod
    def extract_project_knowledge(project: str) -> List[KnowledgeItem]:
        """提取特定项目的知识"""
        pass

    @staticmethod
    def get_user_preferences() -> List[MemoryEntry]:
        """获取用户偏好"""
        pass

    @staticmethod
    def get_error_patterns() -> List[MemoryEntry]:
        """获取错误模式"""
        pass
```

---

## 8. 隐私与安全设计

### 8.1 隐私分级

| 级别 | 说明 | 处理方式 |
|------|------|----------|
| **公开** | 一般性技术知识 | 可直接存入记忆 |
| **内部** | 项目相关信息 | 路径匿名化后存入 |
| **敏感** | 用户偏好、业务逻辑 | 哈希处理关键词 |
| **机密** | API 密钥、密码 | 禁止存入，仅记录存在性 |

### 8.2 安全机制

```python
class PrivacyFilter:
    """隐私过滤器"""

    def filter_sensitive_content(self, content: str) -> FilteredContent:
        """
        过滤敏感内容

        1. 检测并 redact API 密钥
        2. 匿名化路径
        3. 哈希化用户名
        4. 标记敏感级别
        """
        # 复用 DataClaw 的隐私处理逻辑
        filtered = apply_dataclaw_privacy_filters(content)

        return FilteredContent(
            content=filtered,
            privacy_level=self._assess_privacy_level(filtered),
            can_store=self._can_store_in_memory(filtered)
        )
```

---

## 9. 实施路线图

### Phase 1: 基础联动 (1-2周)

| 任务 | 工作量 | 产出 |
|------|--------|------|
| DataClaw Exporter 封装 | 2天 | 导出接口 |
| Knowledge Extractor 基础版 | 3天 | 关键词提取 |
| Memory Integrator 基础版 | 2天 | 写入接口 |
| 基础工作流 | 1天 | 手动触发流程 |

### Phase 2: 智能提取 (2-3周)

| 任务 | 工作量 | 产出 |
|------|--------|------|
| 语义分析模块 | 3天 | 意图分类 |
| 重复检测优化 | 2天 | 相似度算法 |
| 智能合并 | 2天 | 知识融合 |
| 自动化流水线 | 3天 | 定时任务 |

### Phase 3: 价值集成 (2-3周)

| 任务 | 工作量 | 产出 |
|------|--------|------|
| 个性化引擎 | 3天 | 偏好应用 |
| 错误预防引擎 | 3天 | 预警系统 |
| 技能推荐引擎 | 3天 | 智能推荐 |
| 项目知识库 | 2天 | 决策检索 |

---

## 10. 预期效果

### 量化指标

| 指标 | 基准 | 目标 | 说明 |
|------|------|------|------|
| 会话转化率 | 0% | 30% | 有价值的会话转化为知识 |
| 知识复用率 | - | 60% | 被后续会话引用的知识 |
| 错误重复率 | - | -50% | 相同错误重复发生次数 |
| 技能匹配准确率 | 70% | 85% | 意图识别准确率提升 |

### 定性效果

1. **系统自我进化**: 积累的使用数据帮助 Leo 系统自我改进
2. **个性化体验**: 每个用户获得定制化的 AI 助手
3. **知识传承**: 项目经验在团队内沉淀和传承
4. **效率提升**: 减少重复性错误和探索成本

---

## 11. 风险与缓解

| 风险 | 可能性 | 影响 | 缓解措施 |
|------|--------|------|----------|
| 隐私泄露 | 低 | 高 | 多层隐私过滤、定期审计 |
| 知识质量低 | 中 | 中 | 重要性评分、人工审核机制 |
| 存储膨胀 | 中 | 低 | 过期清理、去重机制 |
| 集成复杂 | 低 | 中 | 分阶段实施、接口隔离 |

---

## 12. 结论

本设计提供了 DataClaw 与 Leo 共享记忆系统联动的完整技术方案，通过三层架构实现从原始会话数据到知识资产的价值转化。

**核心价值**:
- 自动化知识提取，降低人工成本
- 多维度知识分类，支持灵活检索
- 智能重复检测，保证知识质量
- 深度系统集成，实现价值最大化

**推荐实施策略**: Phase 1 快速验证 → Phase 2 能力增强 → Phase 3 价值最大化
