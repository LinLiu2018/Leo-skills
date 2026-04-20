---
name: test-driven-development-skill
description: 【测试技能】测试驱动开发（TDD）实践。实现任何功能或修复bug时，在编写实现代码之前使用。
核心理念：先写测试，观察失败，编写最少代码通过。不先看测试失败，就不知道是否测试了正确的东西。
基于 obra/superpowers 的 test-driven-development 技能。
 [优化第5轮：提升了触发准确率]

  核心理念：先写测试，观察失败，编写最少代码通过。不先看测试失败，就不知道是否测试了正确的东西。

  基于 obra/superpowers 的 test-driven-development 技能。

  '
category: testing
author: Leo AI System (基于 obra/superpowers)
metadata:
  version: 1.0.0
  user-invocable: true
  priority: 1
  activation_keywords:
  - TDD
  - 测试驱动
  - 测试优先
  - 先写测试
  - test-driven
  allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
license: MIT
---

# 测试驱动开发（Test-Driven Development, TDD）

## 概述

先写测试。观察它失败。编写最少代码通过。

**核心理念**：如果没看到测试失败，就不知道是否测试了正确的东西。

**违反规则字面要求就是违反规则精神。**

## 铁律

```
没有失败的测试就不能写生产代码
```

先写代码？删除它。重新开始。

**没有例外**：
- 不要保留作为"参考"
- 不要在写测试时"适应"它
- 不要看它
- 删除意味着删除

从测试全新实现。就是这样。

## 红-绿-重构（Red-Green-Refactor）

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   RED       │ →   │   GREEN     │ →   │  REFACTOR   │
│ 写失败测试  │     │ 最少代码    │     │   清理      │
└─────────────┘     └─────────────┘     └─────────────┘
       ↓                  ↓                   ↓
   验证失败            验证通过            保持绿色
```

### RED - 编写失败的测试

写一个最小的测试，显示应该发生什么。

**好**：
```typescript
test('重试失败操作3次', async () => {
  let attempts = 0;
  const operation = () => {
    attempts++;
    if (attempts < 3) throw new Error('fail');
    return 'success';
  };

  const result = await retryOperation(operation);

  expect(result).toBe('success');
  expect(attempts).toBe(3);
});
```
清晰的名称，测试真实行为，一次一件事

**坏**：
```typescript
test('重试有效', async () => {
  const mock = jest.fn()
    .mockRejectedValueOnce(new Error())
    .mockRejectedValueOnce(new Error())
    .mockResolvedValueOnce('success');
  await retryOperation(mock);
  expect(mock).toHaveBeenCalledTimes(3);
});
```
模糊的名称，测试模拟而非代码

**要求**：
- 一个行为
- 清晰的名称
- 真实代码（除非不可避免，否则不用模拟）

### 验证 RED - 观察它失败

**强制。从不跳过。**

```bash
npm test path/to/test.test.ts
```

确认：
- 测试失败（不是错误）
- 失败消息是预期的
- 因为功能缺失而失败（不是拼写错误）

**测试通过？** 你在测试现有行为。修复测试。

**测试错误？** 修复错误，重新运行直到正确失败。

### GREEN - 最少代码

编写最简单的代码来通过测试。

**好**：
```typescript
async function retryOperation<T>(fn: () => Promise<T>): Promise<T> {
  for (let i = 0; i < 3; i++) {
    try {
      return await fn();
    } catch (e) {
      if (i === 2) throw e;
    }
  }
  throw new Error('unreachable');
}
```
刚好通过测试

**坏**：
```typescript
async function retryOperation<T>(
  fn: () => Promise<T>,
  options?: {
    maxRetries?: number;
    backoff?: 'linear' | 'exponential';
    onRetry?: (attempt: number) => void;
  }
): Promise<T> {
  // YAGNI
}
```
过度工程

不要添加功能、重构其他代码，或在测试之外"改进"。

### 验证 GREEN - 观察它通过

**强制。**

```bash
npm test path/to/test.test.ts
```

确认：
- 测试通过
- 其他测试仍然通过
- 输出干净（没有错误、警告）

**测试失败？** 修复代码，不是测试。

**其他测试失败？** 立即修复。

### REFACTOR - 清理

仅在绿色之后：
- 移除重复
- 改进名称
- 提取辅助函数

保持测试绿色。不要添加行为。

### 重复

下一个功能的下一个失败测试。

## 什么时候使用

**总是**：
- 新功能
- Bug 修复
- 重构
- 行为变更

**例外（询问人类伙伴）**：
- 一次性原型
- 生成代码
- 配置文件

想"就跳过 TDD 这一次"？停止。这是合理化。

## 好测试的标准

| 质量 | 好 | 坏 |
|------|----|----|
| **最小化** | 一件事。名称中有"和"？分开它。 | `test('验证邮箱和域名和空格')` |
| **清晰** | 名称描述行为 | `test('test1')` |
| **展示意图** | 展示期望的 API | 掩盖代码应该做什么 |

## 为什么顺序重要

**"我之后写测试来验证它是否有效"**

代码之后写的测试立即通过。立即通过不能证明什么：
- 可能测试了错误的东西
- 可能测试了实现，而非行为
- 可能错过了忘记的边缘情况
- 从没见过它捕获 bug

测试优先迫使你看到测试失败，证明它确实测试了什么东西。

**"我已经手动测试了所有边缘情况"**

手动测试是临时的。你认为测试了所有东西但：
- 没有记录测试了什么
- 代码变更时无法重新运行
- 在压力下容易忘记情况
- "我试的时候有效" ≠ 全面

自动化测试是系统性的。它们每次以相同方式运行。

**"删除 X 小时的工作是浪费"**

沉没成本谬论。时间已经过去了。你现在的选择：
- 删除并用 TDD 重写（再 X 小时，高置信度）
- 保留它并之后添加测试（30 分钟，低置信度，可能有 bug）

"浪费"是保留你无法信任的代码。没有真正测试的工作代码是技术债务。

**"TDD 是教条的，务实意味着适应"**

TDD 是务实的：
- 在提交之前发现 bug（比之后调试快）
- 防止回归（测试立即捕获破坏）
- 记录行为（测试显示如何使用代码）
- 启用重构（自由更改，测试捕获破坏）

"务实"捷径 = 生产环境调试 = 更慢。

## 常见借口

| 借口 | 现实 |
|------|------|
| "太简单了不用测试" | 简单代码也会坏。测试只需 30 秒。 |
| "我之后测试" | 测试立即通过不能证明任何事。 |
| "之后测试达到相同目标" | 之后测试 = "这做什么？" 测试优先 = "这应该做什么？" |
| "已经手动测试了" | 临时的 ≠ 系统性的。没有记录，无法重新运行。 |
| "删除 X 小时是浪费" | 沉没成本谬论。保留未验证代码是技术债务。 |
| "保留作为参考，先写测试" | 你会适应它。那是之后测试。删除意味着删除。 |
| "需要先探索" | 好的。抛弃探索，从 TDD 开始。 |
| "测试难 = 设计不清晰" | 听测试。难测试 = 难使用。 |
| "TDD 会拖慢我" | TDD 比调试快。务实 = 测试优先。 |
| "手动测试更快" | 手动不能证明边缘情况。每次变更你会重新测试。 |
| "现有代码没有测试" | 你在改进它。为现有代码添加测试。 |

## 红旗 - 停止并重新开始

- 代码在测试之前
- 测试在实现之后
- 测试立即通过
- 无法解释为什么测试失败
- 之后添加测试
- 合理化"就这一次"
- "我已经手动测试了"
- "之后测试达到相同目的"
- "这是关于精神不是仪式"
- "保留作为参考"或"适应现有代码"
- "已经花了 X 小时，删除是浪费"
- "TDD 是教条的，我务实"
- "这不同因为..."

**所有这些意味着：删除代码。用 TDD 重新开始。**

## 示例：Bug 修复

**Bug**：接受空邮箱

**RED**
```typescript
test('拒绝空邮箱', async () => {
  const result = await submitForm({ email: '' });
  expect(result.error).toBe('邮箱必填');
});
```

**验证 RED**
```bash
$ npm test
FAIL: 期望 '邮箱必填'，得到 undefined
```

**GREEN**
```typescript
function submitForm(data: FormData) {
  if (!data.email?.trim()) {
    return { error: '邮箱必填' };
  }
  // ...
}
```

**验证 GREEN**
```bash
$ npm test
PASS
```

**REFACTOR**
如果需要，为多个字段提取验证逻辑。

## 验证清单

在标记工作完成之前：

- [ ] 每个新函数/方法都有测试
- [ ] 在实现之前看到每个测试失败
- [ ] 每个测试因预期原因失败（功能缺失，不是拼写错误）
- [ ] 编写最少代码通过每个测试
- [ ] 所有测试通过
- [ ] 输出干净（没有错误、警告）
- [ ] 测试使用真实代码（除非不可避免，否则不用模拟）
- [ ] 覆盖边缘情况和错误

不能勾选所有框？你跳过了 TDD。重新开始。

## 当卡住时

| 问题 | 解决方案 |
|------|----------|
| 不知道如何测试 | 写期望的 API。先写断言。询问人类伙伴。 |
| 测试太复杂 | 设计太复杂。简化接口。 |
| 必须模拟一切 | 代码太耦合。使用依赖注入。 |
| 测试设置巨大 | 提取辅助函数。还是复杂？简化设计。 |

## 调试集成

发现 bug？写失败测试复现它。遵循 TDD 循环。测试证明修复并防止回归。

永远不要在没有测试的情况下修复 bug。

## 测试反模式

当添加模拟或测试工具时，阅读 `@testing-anti-patterns.md` 避免常见陷阱：
- 测试模拟行为而非真实行为
- 向生产类添加仅测试方法
- 不理解依赖就模拟

## 最终规则

```
生产代码 → 测试存在且首先失败
否则 → 不是 TDD
```

没有人类伙伴的许可不能有例外。

## 相关技能

- **systematic_debugging_skill** - 发现 bug 时写失败测试复现它
- **code_verification_skill** - 代码验收标准验证

## 致谢

基于 [obra/superpowers](https://github.com/obra/superpowers) 项目