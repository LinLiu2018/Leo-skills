---
name: executing_plans_skill
version: "1.0.0"
description: |
  【协作技能】执行实施计划。在单独会话中有书面实施计划要执行时使用，带有审查检查点。
  核心理念：批量执行，架构师审查检查点。与 writing_plans_skill 配对使用。
  基于 obra/superpowers 的 executing-plans 技能。
category: collaboration
author: Leo AI System (基于 obra/superpowers)
user-invocable: true
priority: 1
activation_keywords:
  - 执行计划
  - 实施计划
  - 执行任务
  - executing-plans
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - TodoWrite
---

# 执行计划（Executing Plans）

## 概述

加载计划，批判性地审查，批量执行任务，批次之间报告审查。

**核心理念**：批量执行，架构师审查检查点。

**开始时宣布**："我正在使用 executing-plans 技能来实施此计划。"

## 流程

### 步骤 1：加载和审查计划

1. 阅读计划文件
2. 批判性地审查 - 识别计划的任何问题或顾虑
3. 如果有顾虑：在开始之前向人类伙伴提出
4. 如果没有顾虑：创建 TodoWrite 并继续

### 步骤 2：执行批次

**默认：前 3 个任务**

对于每个任务：
1. 标记为 in_progress
2. 完全按照每个步骤（计划有小型步骤）
3. 按指定运行验证
4. 标记为完成

### 步骤 3：报告

当批次完成时：
- 显示实施了什么
- 显示验证输出
- 说："准备接受反馈。"

### 步骤 4：继续

基于反馈：
- 如需要应用更改
- 执行下一个批次
- 重复直到完成

### 步骤 5：完成开发

所有任务完成并验证后：
- 宣布："我正在使用 finishing-a-development-branch 技能来完成这项工作。"
- **必需子技能**：使用 finishing_a_development_branch_skill
- 遵循该技能验证测试、呈现选项、执行选择

## 何时停止并寻求帮助

**立即停止执行当**：
- 批次中途遇到阻塞（缺少依赖、测试失败、指令不清晰）
- 计划有阻止开始的严重缺口
- 不理解指令
- 验证反复失败

**寻求澄清而不是猜测。**

## 何时重新访问早期步骤

**返回审查（步骤 1）当**：
- 合作伙伴根据反馈更新计划
- 基本方法需要重新思考

**不要强行通过阻塞** - 停止并询问。

## 记住

- 首先批判性地审查计划
- 完全按照计划步骤
- 不要跳过验证
- 计划说引用技能时引用技能
- 批次之间：只报告并等待
- 阻塞时停止，不要猜测

## 与 writing-plans 配对使用

```
写作计划 (writing_plans_skill)          执行计划 (executing_plans_skill)
      ↓                                        ↓
创建 EXECUTION_PAN.md              加载计划 → 审查 → 执行批次
      ↓                                        ↓
      └────────── 批量执行 ──────────────────┘
                        ↓
              finishing-a-development-branch
```

## 示例流程

**用户说**："执行 docs/plans/2026-01-29-user-auth.md 中的计划"

**AI 执行**：

1. **加载和审查**
   ```
   读取 docs/plans/2026-01-29-user-auth.md
   审查计划...
   没有顾虑，继续执行
   ```

2. **执行批次（任务 1-3）**
   ```
   执行任务 1：用户模型
   - 步骤 1：编写失败的测试
   - 步骤 2：运行测试验证失败
   - 步骤 3：编写最少实现
   - 步骤 4：运行测试验证通过
   - 步骤 5：提交

   执行任务 2：密码加密
   ...

   执行任务 3：登录接口
   ...
   ```

3. **报告**
   ```
   批次 1 完成（任务 1-3）

   已实现：
   - 用户模型类
   - 密码加密函数
   - 登录 API 端点

   验证输出：
   - 所有测试通过
   - 代码已提交到 phase-1 分支

   准备接受反馈。
   ```

4. **继续或完成**
   - 用户反馈后继续执行下一批次
   - 所有任务完成后调用 finishing-a-development-branch

## 相关技能

- **writing_plans_skill** - 创建计划（配对使用）
- **test_driven_development_skill** - TDD 实践
- **phase_start_skill** - 阶段执行
- **finishing_a_development_branch_skill** - 完成开发分支
- **phase_checkpoint_skill** - 阶段检查点

## 致谢

基于 [obra/superpowers](https://github.com/obra/superpowers) 项目
