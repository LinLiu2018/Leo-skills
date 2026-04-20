---
name: skill-creator
description: 官方 Anthropic Skill 创建器，通过交互式对话创建和优化 Skills。当用户需要创建新技能、优化现有技能、评估技能质量、调整技能描述或进行技能基准测试时使用。提供评估系统、基准测试、多代理并行测试和描述自动调优功能。
license: MIT
metadata:
  version: "2.0.0"
  category: development
  author: Anthropic (官方)
  source: "https://github.com/anthropics/skills/tree/main/skills/skill-creator"
  features:
    - 评估系统
    - 基准测试
    - 多代理并行测试
    - 描述自动调优
  updated: "2026-03-13"
---

# Skill Creator - 官方 Skill 创建器

Anthropic 官方 Skill 创建工具，支持交互式技能创建、评估和优化。

## 核心功能

### 1. 交互式技能创建
- 通过自然语言对话确认需求
- 自动设计技能结构和功能
- 生成完整的技能文件（SKILL.md、代码、配置、测试）
- 3-5 分钟完成一个技能创建

### 2. 评估系统（新增）
- 自动生成测试查询（应触发 10 条 + 不应触发 10 条）
- 交互式网页界面确认触发逻辑
- 导出评估集
- 后台跑 5 轮迭代优化（10-20 分钟）
- 最优描述自动写回 SKILL.md

### 3. 基准测试（新增）
- 量化指标：通过率、耗时、token 用量
- 有 skill vs 无 skill 对比
- A/B 盲评测试
- 自动生成评估报告

### 4. 多代理并行测试（新增）
- 4 个独立子代理同时测试
- 每个代理在干净环境运行
- 独立的 token 计数和时间指标
- 零交叉污染

### 5. 描述自动调优（新增）
- 自动优化 skill 描述
- 该触发的触发，不该触发的别乱触发
- 基于测试结果自动改进
- 防止过拟合（60% 训练集 +40% 测试集）

## 使用方法

### 基本用法

```python
from skill_creator import SkillCreator

creator = SkillCreator()

# 创建新技能
result = creator.execute(
    action="create",
    description="我想创建一个技能，能够根据视频链接生成文字版讲稿"
)

# 优化现有技能
result = creator.execute(
    action="optimize",
    skill_path="./my-skill"
)

# 评估技能
result = creator.execute(
    action="evaluate",
    skill_path="./my-skill",
    eval_type="comprehensive"
)

# 基准测试
result = creator.execute(
    action="benchmark",
    skill_path="./my-skill"
)
```

### 使用示例

#### 示例 1：创建视频讲稿生成技能

```
用户：我想创建一个 skill，我希望能够实现我给了一个视频链接，它能够把文字版的讲稿发给我，如果是别的语言，最好是把原语言版和中文版的讲稿文档给我。

技能：好的，我来帮你创建这个技能。先确认几个问题：
      1. 支持哪些视频平台？（YouTube、B 站等）
      2. 需要保留时间戳吗？
      3. 输出格式偏好？（Markdown、Word 等）
      
      [用户回答后]
      
      正在设计技能...
      [OK] 技能创建完成：video-transcript-skill
      📁 文件结构：
      - SKILL.md
      - video_transcript_skill.py
      - scripts/transcribe.py
      - config/config.yaml
      - tests/test_transcript.py
      预计时间：3-5 分钟
```

#### 示例 2：评估技能触发准确率

```
用户：评估这个技能的触发准确率

技能：正在读取技能文件...
      正在生成测试查询...
      [OK] 生成 20 条测试查询：
      - 10 条应该触发
      - 10 条不应触发
      
      请在网页界面确认触发逻辑：
      http://localhost:8080/eval
      
      [用户确认后]
      
      正在运行优化循环...
      进度：3/5 轮迭代
      [OK] 优化完成！
      触发准确率：95% → 98%
      最优描述已写入 SKILL.md
```

#### 示例 3：基准测试

```
用户：对这个技能进行基准测试

技能：正在设计测试场景...
      正在启动 4 个独立代理...
      
      [测试结果]
      
      [STATS] 基准测试报告：
      通过率：100% vs 9%（无 skill 基线）
      提升：91.5%
      
      Token 消耗：
      - 有 skill: 4000 tokens/次
      - 无 skill: 1750 tokens/次
      - 差值：2250 tokens
      
      耗时：
      - 有 skill: 45 秒
      - 无 skill: 120 秒
      - 节省：62.5%
      
      结论：值得使用
```

#### 示例 4：优化技能描述

```
用户：优化这个技能的描述，避免和其他技能冲突

技能：正在分析当前描述...
      正在生成边界测试用例...
      
      发现潜在冲突：
      - video-downloader-skill（下载视频）
      - video-transcript-skill（生成讲稿）
      
      建议优化：
      - 明确触发条件：包含"讲稿"、"文字版"、"转录"
      - 排除触发：包含"下载"、"保存视频"
      
      正在应用优化...
      [OK] 描述已优化，冲突已解决
```

## 支持的 Actions

| Action | 说明 | 参数 |
|--------|------|------|
| `create` | 创建新技能 | description, category, interactive |
| `optimize` | 优化现有技能 | skill_path, optimization_type |
| `evaluate` | 评估技能质量 | skill_path, eval_type |
| `benchmark` | 基准测试 | skill_path, metrics |
| `tune_description` | 调优描述 | skill_path, test_queries |
| `list_templates` | 列出模板 | - |

## 评估流程

### 1. 生成测试集
```
自动生成 20 条测试查询：
- 10 条应该触发（包含边界情况）
- 10 条不应触发（包含易混淆场景）
```

### 2. 交互式确认
```
网页界面展示所有查询：
- 每条右边有开关（应触发/不应触发）
- 可以逐条查看和调整
- 支持批量操作
```

### 3. 导出评估集
```
确认无误后导出：
- 训练集（60%）
- 测试集（40%）
- 防止过拟合
```

### 4. 优化循环
```
后台跑 5 轮迭代：
每轮做三件事：
1. 生成候选描述
2. 在训练集上测试
3. 在测试集上验证

每轮汇报进度，10-20 分钟完成
```

### 5. 应用最优描述
```
跑完后：
- 自动生成巨型表格（每列一个查询，每行一个版本）
- 绿色✓表示触发成功，红色✗表示失败
- 最优描述自动写回 SKILL.md
```

## 两种 Skill 类型

### 能力提升型
**说明**: 教 Claude 做它本来不擅长的事

**示例**: 
- 前端设计 skill
- 文档创建 skill
- PDF 处理 skill

**测试重点**: 
- 对比有 skill 和无 skill 的表现
- 如果差不多，skill 可以退休

### 编码偏好型
**说明**: 告诉 Claude 按你的规矩来（Workflow）

**示例**:
- 会议纪要整理 skill
- 周报生成 skill
- 销售 SOP skill

**测试重点**:
- 是否按流程走
- 有无漏步骤
- 有无自作主张

## 文件结构

```
skill-creator/
├── SKILL.md              # 技能定义
├── skill_creator.py      # 主实现
├── agents/               # 多代理测试
│   ├── evaluator.py     # 评估代理
│   ├── benchmark.py     # 基准测试代理
│   └── optimizer.py     # 优化代理
├── eval-viewer/          # 评估查看器
│   └── index.html       # 网页界面
├── references/           # 参考文档
│   ├── evaluation-guide.md
│   └── best-practices.md
└── scripts/             # 脚本工具
    ├── run_eval.py
    └── tune_description.py
```

## 配置

在 `config/config.yaml` 中配置：

```yaml
# Skill Creator 配置
eval:
  num_test_queries: 20
  num_iterations: 5
  train_split: 0.6
  
benchmark:
  parallel_agents: 4
  metrics:
    - pass_rate
    - token_usage
    - duration
    
optimization:
  auto_apply: false
  require_approval: true
```

## 依赖

- Python 3.8+
- Leo Skills Core
- Anthropic API
- 浏览器（用于评估界面）

## 版本历史

| 版本 | 日期 | 更新内容 |
|------|------|----------|
| 2.0.0 | 2026-03-13 | 添加评估系统、基准测试、多代理测试、描述调优 |
| 1.0.0 | 2026-01-24 | 初始版本（仅支持基础创建） |

## 官方数据

Anthropic 官方在 6 个文档类 skill 上测试：
- **5 个触发率有提升**
- 平均提升：15-25%
- 最优案例：95% → 98%

## 相关技能

- [skill-code-generator-skill](../development/skill_code_generator_skill) - 代码生成器
- [agent-skill-creator-skill](../tools/agent_skill_creator_skill) - 代理创建器
- [skill-evolution-assistant](../tools/skill_evolution_assistant_skill) - 进化助手

---
*基于 Anthropic 官方 skill-creator 创建 | 最后更新：2026-03-13*
