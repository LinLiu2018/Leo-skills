# 最佳实践标准速查表

> **Leo AI System 文件架构标准** | 参考: [system_architecture.md](src/leo_knowledge/context/system_architecture.md#6-最佳实践标准-best-practice-standards)

---

## 1. 技能结构（Skill）

```
{skill_name}_skill/
├── SKILL.md              ✅ 必需
├── __init__.py           ✅ 推荐
├── {skill_name}_skill.py ✅ 推荐
├── config/
│   └── config.yaml       ✅ 推荐
├── evolution.json        ✅ 进阶
└── scripts/
    └── main.py           ⬜ 可选
```

### SKILL.md Frontmatter 模板

```yaml
---
name: my_skill
version: "1.0.0"
description: |
  一句话描述技能功能
category: tools
author: Leo AI System
user-invocable: true
priority: 1
activation_keywords:
  - 激活词1
  - 激活词2
allowed-tools:
  - Read
  - Write
---
```

### config/config.yaml 模板

```yaml
skill:
  name: my_skill
  version: 1.0.0
  category: tools

execution:
  timeout: 300
  retry: 3

evolution:
  enabled: true
  learn_on_failure: true
  max_tips: 100
```

### evolution.json 模板

```json
{
  "version": "1.0.0",
  "evolution_history": [
    {
      "version": "1.0.0",
      "date": "2026-02-01",
      "changes": "Initial creation"
    }
  ],
  "learned_tips": [],
  "learned_errors": []
}
```

---

## 2. 代理结构（Agent）

```
{domain}_agent/
├── AGENT.md              ✅ 必需
├── {domain}_agent.py     ✅ 必需
├── __init__.py           ✅ 推荐
└── evolution.json        ✅ 进阶
```

### AGENT.md 模板

```markdown
# {Agent Name}

## 代理描述
一句话说明代理的职责

## 能力范围
- 能力1
- 能力2

## 使用示例
```python
# 示例代码
```

## 依赖的Skills
- skill1
- skill2
```

---

## 3. 工作流结构（Workflow）

```
{pipeline_name}_pipeline/
├── workflow.yaml             ✅ 必需
├── {pipeline_name}_pipeline.py  ✅ 必需
├── README.md                 ✅ 推荐
└── __init__.py               ✅ 推荐
```

---

## 4. 命名规范速查

| 类型 | 格式 | 示例 |
|-----|------|------|
| 技能目录 | `{功能}_{类型}_skill` | `github_to_skills_skill` |
| 代理目录 | `{领域}_agent` | `research_agent` |
| 工作流目录 | `{业务}_pipeline` | `content_pipeline` |
| Python类 | `PascalCase` | `ResearchAgent` |
| Python函数/变量 | `snake_case` | `execute_task` |
| 配置文件 | `snake_case.yaml` | `config.yaml` |

**禁止使用**：
- `-` 连字符
- 空格
- 大写字母开头的目录/文件名

---

## 5. 快速验证

```bash
# 验证所有技能结构
python scripts/validate_skills.py

# 验证命名规范
python scripts/validate_naming.py

# 创建新技能模板
python scripts/create_skill.py --name my_new_skill --category tools
```

---

## 6. 完整度检查清单

### 新建技能前检查

- [ ] SKILL.md frontmatter 完整
- [ ] 命名符合 snake_case
- [ ] 已规划必需文件

### 新建技能后检查

- [ ] SKILL.md 存在且有效
- [ ] __init__.py 正确导出
- [ ] config/config.yaml 存在（推荐）
- [ ] evolution.json 存在（进阶）
- [ ] 通过命名验证

---

## 7. 参考资源

| 资源 | 位置 |
|------|------|
| 完整标准 | [system_architecture.md#6](../src/leo_knowledge/context/system_architecture.md#6-最佳实践标准-best-practice-standards) |
| 开发规范 | [development_guide.md](../src/leo_knowledge/context/development_guide.md) |
| 用户配置 | [user_profile.md](../src/leo_knowledge/context/user_profile.md) |

---

*最后更新: 2026-02-01*
