# Leo AI System - 项目优化实施计划

> **制定时间**: 2026-01-24
> **优化原则**: 务实优先，小步快跑，能用>完美

---

## 🎯 优化目标

1. **清理冗余**：将883M的leo_skills精简到<100M
2. **规范结构**：统一目录命名和组织方式
3. **提升质量**：建立基础的测试和CI流程
4. **明确协作**：理清Orchestrator-Subagents-Skills调用链

---

## 📋 优化任务清单

### 阶段一：清理与规范（优先级：🔥 高）

#### 1.1 技能库大扫除
**目标**：从38个技能定义精简到7-10个真正有效的技能

```bash
# 执行清理脚本
python scripts/cleanup_skills.py --dry-run  # 先预览
python scripts/cleanup_skills.py --execute  # 确认后执行
```

**清理规则**：
- ✅ 保留：有SKILL.md + main.py + README.md + 最近3个月有使用记录
- ❌ 删除：.backup目录、重复技能、未完成的半成品
- 📦 归档：有价值但暂不使用的技能 → `archive/skills/`

**预期结果**：
- leo_skills从883M降到<100M
- 保留7-10个核心技能
- 清理率：>85%

---

#### 1.2 目录结构标准化
**问题**：同时存在leo_skills和leo-skills，命名不统一

**解决方案**：

```bash
# 1. 删除leo-skills空目录
rm -rf leo-skills/

# 2. 统一使用下划线命名（已完成大部分）
# 确认所有目录都是 leo_* 格式

# 3. 清理未跟踪文件
git clean -fd --dry-run  # 预览
git clean -fd             # 执行
```

**标准目录结构**：
```
leo_skills/          # 能力库（原子功能）
leo_subagents/       # 代理库（专业执行者）
leo_workflows/       # 工作流（业务流程）
leo_orchestrator/    # 编排器（任务调度）
leo_knowledge/       # 知识库（静态上下文）
leo_interface/       # 接口层（CLI/Web）
leo_config/          # 配置管理
leo_system/          # 系统核心
```

---

#### 1.3 文档整合
**问题**：文档分散在docs/和leo_knowledge/，职责不清

**解决方案**：

| 目录 | 职责 | 内容 |
|------|------|------|
| `leo_knowledge/context/` | **运行时上下文** | user_profile.md, system_architecture.md, capability_index.md |
| `docs/guides/` | **用户文档** | 快速开始、使用教程 |
| `docs/reference/` | **技术参考** | API文档、架构设计 |
| `docs/planning/` | **项目管理** | 优化计划、实施进度 |

**清理动作**：
- 删除重复文档（如docs/profile/leo-profile.md已有user_profile.md）
- 合并分散的架构文档
- 归档过时的计划文档

---

### 阶段二：质量提升（优先级：🟡 中）

#### 2.1 建立测试框架

**当前状态**：
- 有pytest.ini和requirements-test.txt
- 有tests/目录但覆盖率未知

**优化动作**：

```bash
# 1. 运行现有测试，评估覆盖率
pytest --cov=leo_skills --cov=leo_subagents --cov=leo_orchestrator --cov-report=html

# 2. 为核心模块补充测试
# 优先级：Orchestrator > Subagents > Skills

# 3. 设置最低覆盖率要求
# 目标：核心模块 >60%，整体 >40%
```

**测试策略**：
- **单元测试**：每个Skill的main.py必须有对应测试
- **集成测试**：Orchestrator调度Subagent的完整流程
- **端到端测试**：至少1个完整的业务场景（如房产新闻发布）

---

#### 2.2 代码质量检查

**工具链**：
```bash
# 1. 代码格式化
pip install black isort
black leo_skills/ leo_subagents/ leo_orchestrator/
isort leo_skills/ leo_subagents/ leo_orchestrator/

# 2. 代码检查
pip install flake8 pylint
flake8 leo_skills/ --max-line-length=120
pylint leo_skills/ --disable=C0111  # 暂时忽略文档字符串

# 3. 类型检查
pip install mypy
mypy leo_orchestrator/ --ignore-missing-imports
```

**Pre-commit配置**（已有.pre-commit-config.yaml）：
```yaml
repos:
  - repo: https://github.com/psf/black
    hooks:
      - id: black
  - repo: https://github.com/pycqa/isort
    hooks:
      - id: isort
  - repo: https://github.com/pycqa/flake8
    hooks:
      - id: flake8
```

---

#### 2.3 CI/CD流程

**GitHub Actions配置**（已有.github/workflows/ci.yml）：

```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.13'
      - run: pip install -r requirements.txt -r requirements-test.txt
      - run: pytest --cov --cov-report=xml
      - run: black --check .
      - run: flake8 .
```

---

### 阶段三：架构优化（优先级：🟢 低）

#### 3.1 明确协作机制

**当前问题**：Orchestrator、Subagents、Skills的调用关系不清晰

**优化方案**：

```python
# leo_orchestrator/api.py
class LeoOrchestrator:
    """统一入口：接收任务 → 识别意图 → 调度执行"""

    def dispatch(self, task: str) -> Result:
        # 1. 意图识别
        intent = self.intent_classifier.classify(task)

        # 2. 选择Subagent
        agent = self.registry.get_agent(intent.agent_type)

        # 3. 执行任务
        return agent.execute(task, context=self.context)

# leo_subagents/agents/base_agent.py
class BaseAgent:
    """Subagent基类：专精某领域，按需加载Skills"""

    def execute(self, task: str, context: dict) -> Result:
        # 1. 加载所需Skills
        skills = self.skill_loader.load(self.required_skills)

        # 2. 执行任务
        return self._do_work(task, skills, context)

# leo_skills/*/scripts/main.py
def main(input_data: dict) -> dict:
    """Skill标准接口：输入→处理→输出"""
    # 原子功能实现
    return {"status": "success", "data": result}
```

**调用链示例**：
```
User: "帮我发布一篇房产新闻"
  ↓
Orchestrator: 识别为"内容发布"任务
  ↓
Creative Agent: 调用realestate-news-publisher-cskill
  ↓
Skill: 执行新闻采集→分析→生成→发布
  ↓
返回结果给User
```

---

#### 3.2 统一日志和错误处理

**问题**：各模块日志格式不统一，错误处理分散

**解决方案**：

```python
# leo_system/logger.py
import logging
from pathlib import Path

def get_logger(name: str) -> logging.Logger:
    """统一日志配置"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # 文件处理器
    fh = logging.FileHandler(Path("logs") / f"{name}.log")
    fh.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    logger.addHandler(fh)

    return logger

# leo_system/errors.py
class LeoError(Exception):
    """基础异常类"""
    pass

class SkillExecutionError(LeoError):
    """Skill执行失败"""
    pass

class AgentDispatchError(LeoError):
    """Agent调度失败"""
    pass
```

**使用示例**：
```python
from leo_system.logger import get_logger
from leo_system.errors import SkillExecutionError

logger = get_logger(__name__)

try:
    result = skill.execute(data)
    logger.info(f"Skill executed successfully: {result}")
except Exception as e:
    logger.error(f"Skill execution failed: {e}")
    raise SkillExecutionError(f"Failed to execute skill: {e}")
```

---

#### 3.3 性能监控

**目标**：了解系统瓶颈，优化慢速操作

**实现方案**：

```python
# leo_system/metrics.py
import time
from functools import wraps

def track_time(func):
    """装饰器：记录函数执行时间"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start

        # 记录到日志或监控系统
        logger.info(f"{func.__name__} took {duration:.2f}s")
        return result
    return wrapper

# 使用示例
@track_time
def execute_skill(skill_name: str, data: dict):
    # 执行逻辑
    pass
```

---

## 🚀 实施步骤

### Week 1: 清理与规范
- [ ] Day 1-2: 执行技能库大扫除
- [ ] Day 3: 标准化目录结构
- [ ] Day 4-5: 整合文档

**验收标准**：
- leo_skills < 100M
- 无.backup目录
- 文档职责清晰

---

### Week 2: 质量提升
- [ ] Day 1-2: 建立测试框架，补充核心测试
- [ ] Day 3: 配置代码质量检查工具
- [ ] Day 4-5: 完善CI/CD流程

**验收标准**：
- 测试覆盖率 >40%
- CI流程正常运行
- Pre-commit hooks生效

---

### Week 3: 架构优化
- [ ] Day 1-2: 明确Orchestrator-Subagents-Skills协作机制
- [ ] Day 3: 统一日志和错误处理
- [ ] Day 4-5: 添加性能监控

**验收标准**：
- 调用链清晰可追踪
- 日志格式统一
- 关键操作有性能数据

---

## 📊 优化效果预期

| 指标 | 优化前 | 优化后 | 提升 |
|------|--------|--------|------|
| leo_skills大小 | 883M | <100M | -88% |
| 有效技能数 | 7/38 | 7-10/10 | 100%有效 |
| 测试覆盖率 | 未知 | >40% | +40% |
| 代码质量 | 无检查 | 自动化检查 | ✅ |
| 文档清晰度 | 分散 | 结构化 | ✅ |

---

## ⚠️ 风险与应对

### 风险1：清理时误删有用文件
**应对**：
- 先执行--dry-run预览
- 重要文件先备份到archive/
- 使用git，随时可回滚

### 风险2：测试补充耗时过长
**应对**：
- 优先核心模块（Orchestrator）
- 采用MVP思维，先有再好
- 设置合理的覆盖率目标（40%而非80%）

### 风险3：架构调整影响现有功能
**应对**：
- 小步迭代，每次只改一个模块
- 充分测试后再合并
- 保持向后兼容

---

## 🎯 成功标准

### 必须达成（Must Have）
- ✅ leo_skills精简到<100M
- ✅ 目录结构统一规范
- ✅ 核心模块有基础测试
- ✅ CI流程正常运行

### 期望达成（Should Have）
- ✅ 测试覆盖率>40%
- ✅ 代码质量自动检查
- ✅ 文档结构清晰

### 可选达成（Nice to Have）
- ✅ 性能监控系统
- ✅ 完整的调用链追踪
- ✅ 自动化部署流程

---

## 📝 后续维护

### 日常维护
- 每周运行一次`python scripts/update_manifests.py`更新索引
- 每月检查一次技能使用情况，清理无用技能
- 每季度review一次架构，优化瓶颈

### 持续改进
- 根据实际使用反馈调整Skill分类
- 优化Orchestrator的意图识别准确率
- 扩展Subagents的专业能力

---

**制定人**: Claude Opus 4.5
**审核人**: Leo Liu
**版本**: v1.0
**最后更新**: 2026-01-24
