# Leo Skills 进化框架使用指南

## 概述

Leo Skills 进化框架（Evolution Framework）为技能提供自我学习、优化和进化的能力。技能可以从执行历史中学习，自动发现最佳实践，并持续优化自身配置。

## 核心特性

- ✅ **自动学习**：从执行历史中自动分析模式和最佳实践
- ✅ **智能优化**：基于数据生成优化建议和规则
- ✅ **安全可控**：支持配置快照、回滚和人工审批
- ✅ **透明可见**：完整的学习和优化记录
- ✅ **低侵入性**：通过继承基类实现，不破坏现有代码

## 快速开始

### 1. 创建可进化技能

```python
from leo_skills.core.evolution import EvolvableSkill

class MySkill(EvolvableSkill):
    """你的技能类"""

    def __init__(self):
        # 初始化父类
        super().__init__(
            skill_name="my-skill",
            config_path="path/to/config.yaml"
        )

    def _execute_core(self, *args, **kwargs):
        """
        实现核心执行逻辑

        必须返回包含以下字段的字典：
        - success: bool - 是否成功
        - quality_score: float (0-1) - 输出质量评分（可选）
        - output_metrics: dict - 输出指标（可选）
        """
        # 你的业务逻辑
        result = self.do_something(*args, **kwargs)

        return {
            'success': True,
            'result': result,
            'quality_score': 0.85,
            'output_metrics': {
                'items_processed': 10,
                'avg_score': 0.9
            }
        }
```

### 2. 配置进化参数

复制配置模板到你的技能目录：

```bash
cp leo-skills/core/evolution/config/evolution_config_template.yaml \
   your-skill/config/evolution_config.yaml
```

编辑配置文件，根据你的需求调整参数：

```yaml
evolution:
  enabled: true

  learning:
    min_executions_for_learning: 10  # 最少执行次数
    analysis_window: 100              # 分析窗口

  optimization:
    auto_optimize: false              # 是否自动应用优化
    require_approval: true            # 是否需要人工审批
```

### 3. 使用技能

```python
# 创建技能实例
skill = MySkill()

# 执行技能（自动收集数据）
result = skill.execute(param1="value1", param2="value2")

if result.success:
    print(f"成功: {result.data}")
else:
    print(f"失败: {result.error}")

# 查看进化状态
status = skill.get_evolution_status()
print(f"总执行次数: {status['total_executions']}")
print(f"最佳实践数: {status['best_practices_count']}")

# 手动触发学习（可选）
skill.trigger_manual_learning()
```

## 核心概念

### 1. 执行指标（ExecutionMetrics）

每次技能执行都会收集以下指标：

- **success**: 是否成功
- **duration**: 执行时长
- **quality_score**: 输出质量评分（0-1）
- **parameters**: 输入参数
- **output_metrics**: 输出指标
- **error_message**: 错误信息（如果失败）

### 2. 学习流程

当执行次数达到阈值（默认10次）时，自动触发学习流程：

```
执行历史 → 模式分析 → 知识提取 → 规则生成 → 知识存储
```

**分析内容：**
- 成功率和质量趋势
- 最优参数组合
- 失败模式识别
- 性能瓶颈发现

### 3. 最佳实践（BestPractice）

从成功案例中提取的知识：

```python
BestPractice(
    name="optimal_threshold",
    description="使用最优阈值0.75",
    conditions={'context': 'general'},
    actions={'threshold': 0.75},
    expected_improvement=0.1,
    success_rate=0.92
)
```

### 4. 优化规则（OptimizationRule）

具体的优化动作：

```python
OptimizationRule(
    name="optimize_threshold",
    type="parameter",
    target="threshold",
    action="adjust",
    value=0.75,
    confidence=0.85,
    expected_gain=0.1
)
```

### 5. 配置适配（Adapter）

安全地应用优化规则：

- 创建配置快照
- 应用参数调整
- 支持回滚恢复

## 高级功能

### 手动触发学习

```python
result = skill.trigger_manual_learning()
if result['success']:
    print(f"分析了 {result['analyzed_count']} 条记录")
```

### 查看学习结果

```python
# 加载最佳实践
practices = skill.evolver.load_best_practices()
for practice in practices:
    print(f"{practice.name}: {practice.description}")

# 加载优化规则
rules = skill.evolver.load_optimization_rules()
for rule in rules:
    print(f"{rule.name}: {rule.target} -> {rule.value}")
```

### 配置快照管理

```python
# 创建快照
version = skill.adapter.create_version_snapshot()

# 列出所有快照
snapshots = skill.adapter.list_snapshots()

# 回滚到指定版本
skill.adapter.rollback_to_snapshot(version)
```

### 自定义质量评分

在 `_execute_core` 中实现自定义的质量评分逻辑：

```python
def _execute_core(self, *args, **kwargs):
    result = self.process(*args, **kwargs)

    # 自定义质量评分
    quality_score = self._calculate_quality(result)

    return {
        'success': True,
        'result': result,
        'quality_score': quality_score
    }

def _calculate_quality(self, result):
    """根据业务逻辑计算质量分数"""
    score = 0.0

    # 示例：基于多个维度
    if result.get('accuracy') > 0.9:
        score += 0.4
    if result.get('completeness') > 0.8:
        score += 0.3
    if result.get('timeliness') < 60:
        score += 0.3

    return score
```

## 数据存储

进化数据存储在 `leo-skills/.evolution_data/{skill_name}/` 目录下：

```
.evolution_data/
└── my-skill/
    ├── execution_history.jsonl      # 执行历史（JSONL格式）
    ├── best_practices.json          # 最佳实践
    ├── optimization_rules.json      # 优化规则
    └── .snapshots/                  # 配置快照
        ├── my-skill_20260110_120000
        └── my-skill_20260110_130000
```

## 运行示例

```bash
# 运行简单示例
cd leo-skills
python core/evolution/examples/simple_skill_demo.py
```

输出示例：

```
============================================================
技能进化框架 - 简单示例
============================================================

执行测试案例...

[1/10] 处理: 'hello world' (mode=upper)
  ✓ 成功: HELLO WORLD
  质量评分: 0.11

[2/10] 处理: 'HELLO WORLD' (mode=lower)
  ✓ 成功: hello world
  质量评分: 0.11

...

============================================================
进化状态
============================================================
进化能力: 已启用
总执行次数: 10
最佳实践数: 2
优化规则数: 1
配置快照数: 0

============================================================
手动触发学习流程
============================================================
✓ 学习完成，分析了 10 条记录
```

## 最佳实践

### 1. 渐进式启用

- 初期设置 `auto_optimize: false`
- 人工审查优化建议
- 验证效果后再启用自动优化

### 2. 合理设置阈值

- `min_executions_for_learning`: 10-20次（确保数据充足）
- `analysis_window`: 50-100次（平衡历史和当前）
- `min_confidence`: 0.7-0.8（避免低置信度优化）

### 3. 定义清晰的质量指标

```python
def _execute_core(self, *args, **kwargs):
    # 明确的质量评分标准
    quality_score = (
        accuracy * 0.4 +
        completeness * 0.3 +
        efficiency * 0.3
    )

    return {
        'success': True,
        'quality_score': quality_score,
        'output_metrics': {
            'accuracy': accuracy,
            'completeness': completeness,
            'efficiency': efficiency
        }
    }
```

### 4. 定期审查学习结果

```python
# 定期检查进化状态
status = skill.get_evolution_status()

# 审查最佳实践
practices = skill.evolver.load_best_practices()

# 审查优化规则
rules = skill.evolver.load_optimization_rules()
```

## 故障排查

### 问题1：进化能力未启用

**症状**：`get_evolution_status()` 返回 `enabled: false`

**解决**：
1. 检查 `evolution_config.yaml` 中 `evolution.enabled` 是否为 `true`
2. 确认配置文件路径正确

### 问题2：学习未触发

**症状**：执行多次后仍无最佳实践和优化规则

**解决**：
1. 检查执行次数是否达到 `min_executions_for_learning`
2. 手动触发学习：`skill.trigger_manual_learning()`
3. 查看日志确认是否有错误

### 问题3：优化规则未应用

**症状**：生成了优化规则但配置未改变

**解决**：
1. 检查 `auto_optimize` 是否为 `true`
2. 如果需要人工审批，手动应用：
   ```python
   rules = skill.evolver.load_optimization_rules()
   skill.adapter.apply_optimizations(rules, auto_apply=True)
   ```

## 下一步

- 查看 [examples/simple_skill_demo.py](examples/simple_skill_demo.py) 了解完整示例
- 参考 [evolution_config_template.yaml](config/evolution_config_template.yaml) 配置你的技能
- 改造现有技能以支持进化能力

## 技术支持

如有问题，请查看：
- 代码注释和文档字符串
- 日志输出（设置 `logging.DEBUG` 查看详细信息）
- 示例代码
