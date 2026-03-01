# Leo AI System - 自动进化架构设计 (Auto-Evolution Architecture)

> 版本：v1.0 | 设计目标：用户只需给出远景，系统自动完成技能/代理/工作流的进化

---

## 一、核心问题诊断

### 1.1 现状痛点

| 问题 | 影响 | 根因 |
|------|------|------|
| 进化框架闲置 | 230个技能只有1个有真实进化记录 | 需要显式调用learn()，无自动触发 |
| 进化=记日志 | 经验无法转化为实际改进 | 只有数据层，无执行层 |
| 人工闭环 | 需要人读经验、手动改代码 | 缺少AI驱动的代码生成 |
| 无验证机制 | 改了不知道好不好 | 缺少自动化测试和对比 |

### 1.2 设计目标

```
用户输入: "我要一个自动把营销文档转PDF的系统"
          ↓
系统输出: [自动生成的技能] + [自动部署] + [自动优化迭代]
          ↓
用户反馈: "字体太小了"
          ↓
系统自动: 诊断 → 修改代码 → 测试 → 部署 → 验证效果
```

---

## 二、架构设计 (4层架构)

```
┌─────────────────────────────────────────────────────────────────┐
│                     Layer 1: 意图层 (Intent)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ 远景解析器   │  │ 目标分解器   │  │ 优先级排序   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                    用户说: "我要..." → 系统理解                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Layer 2: 感知层 (Perception)                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ 性能监控     │  │ 错误追踪     │  │ 用户反馈     │          │
│  │ (Metrics)    │  │ (Errors)     │  │ (Feedback)   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                    实时收集: 运行数据、异常、用户输入              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Layer 3: 认知层 (Cognition)                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ 异常诊断     │  │ 策略生成     │  │ 代码规划     │          │
│  │ (Diagnosis)  │  │ (Strategy)   │  │ (Planning)   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                    AI驱动: 分析问题、生成改进方案                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Layer 4: 执行层 (Execution)                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ 代码生成     │  │ 自动测试     │  │ 灰度部署     │          │
│  │ (Codegen)    │  │ (Testing)    │  │ (Deploy)     │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                    自动执行: 改代码、验证、上线                    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                        [效果验证] ← 回到 Layer 2
```

---

## 三、核心组件设计

### 3.1 意图层 - 远景解析器 (Vision Parser)

**功能**：把用户的自然语言需求转化为系统可执行的目标

```python
# 示例
用户: "我要一个能把营销文档自动转成PDF的工具"
↓
VisionParser 输出:
{
    "goal_type": "create_skill",           # 创建新技能
    "skill_category": "content_creation",  # 分类
    "inputs": ["markdown_files"],          # 输入
    "outputs": ["pdf_files"],              # 输出
    "constraints": ["chinese_support", "table_formatting"],
    "success_criteria": ["readable_font", "proper_pagination"],
    "priority": "high"
}
```

**触发条件**：
- 用户明确说："我要..." / "帮我做个..." / "能不能自动..."
- 检测到重复性人工操作（3次以上）
- 当前系统无匹配技能

---

### 3.2 感知层 - 全链路监控 (Unified Monitor)

**监控指标**：

| 维度 | 指标 | 阈值触发 |
|------|------|----------|
| 性能 | 执行耗时、内存占用、成功率 | 耗时 > 平均200% |
| 质量 | 输出文件大小、格式正确性 | PDF打不开、乱码 |
| 用户 | 满意度反馈、修改次数 | 同一文件修改 > 3次 |
| 异常 | 报错类型、频率 | 同类型错误 > 5次/天 |

**自动触发进化**：
```python
# 伪代码
if execution_time > baseline * 2:
    trigger_evolution(skill_id, "performance_regression")

if user_feedback == "negative":
    trigger_evolution(skill_id, "quality_issue")

if error_count > 5 and time_window < "1h":
    trigger_evolution(skill_id, "stability_issue")
```

---

### 3.3 认知层 - AI策略引擎 (Strategy Engine)

**核心能力**：

#### 3.3.1 异常诊断 (Auto-Diagnosis)
```python
def diagnose_issue(execution_logs, user_feedback):
    """
    分析日志和反馈，定位问题根因
    """
    # 示例输出
    {
        "problem": "PDF字体过小导致表格内容截断",
        "root_cause": "CSS主题中font-size: 22px对于密集表格过大",
        "affected_components": ["theme-lecheng.css", "table_rendering"],
        "severity": "high",
        "confidence": 0.87
    }
```

#### 3.3.2 策略生成 (Strategy Generation)
```python
def generate_strategy(diagnosis):
    """
    基于诊断生成改进方案
    """
    # 示例输出
    {
        "approach": "adjust_css_font_size",
        "changes": [
            {
                "file": "theme-lecheng.css",
                "line": 6,
                "old": "font-size: 22px;",
                "new": "font-size: 17px;"
            }
        ],
        "test_plan": ["regression_test", "visual_validation"],
        "rollback_plan": "git revert"
    }
```

#### 3.3.3 代码规划 (Code Planning)
```python
def plan_implementation(strategy):
    """
    规划具体的代码实现步骤
    """
    # 生成类似之前我写的 task_plan.md 的结构
    return {
        "steps": [
            {"action": "modify_file", "file": "xxx", "content": "..."},
            {"action": "run_test", "test_suite": "..."},
            {"action": "deploy", "method": "git_commit"}
        ]
    }
```

---

### 3.4 执行层 - 自动化流水线 (Auto-Pipeline)

#### 3.4.1 代码生成与修改 (Aider Integration)

使用 [Aider](https://github.com/paul-gauthier/aider) 或类似工具实现AI代码编辑：

```python
class CodeModifier:
    def modify(self, file_path, instruction):
        """
        使用AI编辑代码
        """
        # 调用 Claude API / OpenAI API
        # 支持多种修改模式：
        # - edit: 精确修改指定位置
        # - refactor: 重构代码结构
        # - add: 新增功能
        # - fix: 修复bug
        pass
```

#### 3.4.2 自动化测试 (Auto-Testing)

```python
class AutoTester:
    def run_tests(self, skill_id):
        """
        自动化测试套件
        """
        tests = {
            "unit_test": run_unit_tests(skill_id),
            "integration_test": run_integration_tests(skill_id),
            "regression_test": compare_with_baseline(skill_id),
            "user_simulation": simulate_user_interaction(skill_id)
        }
        return tests

    def validate_change(self, before_metrics, after_metrics):
        """
        验证改动是否有效
        """
        # 性能不下降
        # 错误率降低
        # 用户满意度提升
        pass
```

#### 3.4.3 灰度部署 (Canary Deploy)

```python
class DeploymentManager:
    def deploy(self, skill_id, strategy="canary"):
        """
        部署策略：
        1. shadow: 影子模式，并行运行但不使用结果
        2. canary: 5%流量使用新版本
        3. rollback: 自动回滚到上一版本
        """
        pass
```

---

## 四、工作流程：从需求到进化

### 4.1 首次创建技能 (Create Mode)

```
用户: "我要自动把营销文档转PDF"
    ↓
[意图解析] → 识别为"创建新技能"
    ↓
[代码生成] → AI生成初始版本
    - 脚本结构
    - 依赖分析
    - 错误处理
    ↓
[自动测试] → 验证基础功能
    - 用样本数据测试
    - 检查输出格式
    ↓
[用户试用] → 用户提供真实数据
    ↓
[反馈收集] → 记录问题和满意度
```

### 4.2 持续进化模式 (Evolve Mode)

```
[监控] 检测到问题 / 用户反馈
    ↓
[诊断] AI分析根因
    ↓
[规划] 生成改进方案
    ↓
[执行] 自动修改代码
    ↓
[测试] 验证改进效果
    ↓
[部署] 灰度上线
    ↓
[验证] 对比改进前后指标
    ↓
[学习] 记录有效策略到evolution.json
    ↓
[反馈] 通知用户改进完成
```

---

## 五、关键技术实现

### 5.1 触发器系统 (Trigger System)

```python
# src/leo_orchestrator/evolution_triggers.py

TRIGGERS = {
    # 性能触发
    "performance_degradation": {
        "condition": "execution_time > baseline * 1.5",
        "cooldown": "1h",
        "action": "optimize_performance"
    },

    # 错误触发
    "error_spike": {
        "condition": "error_rate > 5% in 10min",
        "cooldown": "30min",
        "action": "fix_stability"
    },

    # 反馈触发
    "negative_feedback": {
        "condition": "user_feedback == 'negative'",
        "cooldown": "immediate",
        "action": "address_feedback"
    },

    # 定期进化
    "scheduled_optimization": {
        "condition": "cron: 0 2 * * 0",  # 每周日凌晨2点
        "action": "proactive_optimization"
    }
}
```

### 5.2 进化决策树 (Evolution Decision Tree)

```python
def decide_evolution_strategy(issue_type, context):
    """
    基于问题类型选择进化策略
    """
    strategies = {
        "performance": [
            "profile_code",           # 性能分析
            "optimize_algorithm",     # 算法优化
            "add_caching",           # 添加缓存
            "parallel_processing"    # 并行处理
        ],

        "quality": [
            "adjust_parameters",      # 调整参数
            "improve_prompt",        # 优化提示词
            "add_validation",        # 增加验证
            "refine_output_format"   # 细化输出格式
        ],

        "stability": [
            "add_error_handling",    # 增强错误处理
            "add_retry_logic",       # 添加重试
            "limit_resource_usage",  # 限制资源
            "add_timeout"            # 添加超时
        ],

        "feature": [
            "extend_functionality",  # 扩展功能
            "add_new_option",        # 添加选项
            "support_new_format"     # 支持新格式
        ]
    }

    return strategies.get(issue_type, ["generic_improvement"])
```

### 5.3 经验知识库 (Experience Knowledge Base)

超越简单的evolution.json，建立真正的知识库：

```json
{
    "version": "2.0",
    "patterns": [
        {
            "pattern_id": "pdf_font_sizing",
            "description": "PDF中文字体大小优化模式",
            "trigger": "用户反馈字体太小/太大",
            "solution": {
                "css_selector": "section",
                "font_size": "17px",
                "table_font_size": "15px"
            },
            "success_rate": 0.95,
            "applied_count": 12,
            "created_at": "2026-02-27"
        }
    ],
    "strategies": [
        {
            "strategy": "reduce_font_for_dense_content",
            "when": "table_rows > 8 and content_type == 'dense'",
            "then": "reduce_font_size_by(5)",
            "verified": true
        }
    ]
}
```

---

## 六、实施路线图

### Phase 1: 基础进化 (1-2周)

目标：让现有进化系统真正跑起来

- [ ] 修复evolution.json的读写逻辑
- [ ] 在关键技能中添加learn()调用
- [ ] 建立基础的性能监控
- [ ] 创建简单的触发器（错误率、耗时）

### Phase 2: AI驱动 (2-3周)

目标：引入AI诊断和代码生成

- [ ] 集成Claude API用于代码修改
- [ ] 实现自动诊断器
- [ ] 建立自动化测试框架
- [ ] 实现Git工作流集成

### Phase 3: 闭环进化 (3-4周)

目标：完整的自动进化闭环

- [ ] 实现代码→测试→部署流水线
- [ ] 建立效果验证机制
- [ ] 实现灰度发布
- [ ] 建立知识库积累有效模式

### Phase 4: 自举进化 (4-6周)

目标：系统能自我改进进化系统本身

- [ ] 进化系统能改进自己的触发器
- [ ] 自动发现新的优化机会
- [ ] 模式识别和自动抽象

---

## 七、用户交互示例

### 场景1：首次创建
```
用户: "我要自动把营销文档转PDF"

系统:
"正在为您创建 [md_to_pdf_skill]...
✓ 分析需求：Markdown → PDF，中文支持，表格处理
✓ 生成初始代码：scripts/skills/md_to_pdf_skill/
✓ 自动安装依赖：marp-cli
✓ 创建测试用例：5个样本文件
✓ 基础验证通过

请提供1-2个真实文档用于优化："

[用户上传文档]

系统:
"✓ 处理完成
✓ 检测到问题：表格行过多导致截断
✓ 自动优化：调整CSS字体大小 22px → 17px
✓ 验证通过

技能已部署。后续我会持续监控并自动优化。"
```

### 场景2：自动进化
```
用户: [使用几次后] "这个PDF字体太小了"

系统:
"收到反馈。正在自动优化...

[分析] 检测到表格密集场景下字体过大
[诊断] 根因：默认22px在复杂表格中不适用
[方案] 调整为17px正文 + 15px表格
[测试] 使用历史文档验证，排版改善95%
[部署] 已自动更新

✓ 优化完成，请再试试。
（此类问题已记录，下次遇到类似文档会自动处理）"
```

### 场景3：自主发现
```
系统: [凌晨自动运行]
"检测到 md_to_pdf_skill 在处理大文件(>1MB)时耗时增加300%

[自动诊断] 发现内存泄漏：每次转换未释放临时文件
[自动修复] 添加临时文件清理逻辑
[自动测试] 大文件处理耗时恢复正常
[已部署] 灰度发布中，无异常则全量

无需您操作，问题已自动解决。"
```

---

## 八、风险控制

### 8.1 安全机制

| 风险 | 控制措施 |
|------|----------|
| 代码改坏 | 必须测试通过才能部署 |
| 无限循环进化 | 设置每日进化上限（如3次） |
| 用户不知情 | 所有改动通知用户，可一键回滚 |
| 数据泄露 | 敏感数据脱敏后才用于AI分析 |

### 8.2 回滚机制

```python
class RollbackManager:
    def auto_rollback(self, skill_id):
        """
        自动回滚条件：
        1. 错误率比进化前上升
        2. 用户明确说"改坏了"
        3. 监控到异常崩溃
        """
        pass

    def one_click_rollback(self, skill_id, version):
        """
        用户一键回滚到任意版本
        """
        pass
```

---

## 九、总结

### 关键区别

| 维度 | 旧系统 | 新架构 |
|------|--------|--------|
| 触发 | 手动调用 | 自动监控触发 |
| 进化内容 | 记文本日志 | 实际改代码 |
| 验证 | 无 | 自动化测试 |
| 部署 | 人工 | 灰度自动 |
| 学习 | 人读经验 | AI抽象模式 |

### 用户价值

- **0到1**：说需求，系统自动创建可用技能
- **1到N**：使用过程中自动优化，越用越好用
- **无人值守**：半夜发现问题，凌晨自动修复，早上通知你

---

下一步：开始Phase 1实施？还是你想调整某些设计？
