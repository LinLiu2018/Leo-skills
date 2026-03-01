# Leo AI System 目录与接口改造计划

> 制定者：Claude Code（大脑）| 执行者：Codex（脚手架）
> 日期：2026-02-25
> 基于分支：`refactor/standardize-structure`

---

## 评估总结

Codex 审查了系统现状并给出 7 大改造方向。Claude Code 独立验证后，确认大部分结论正确，
同时纠正了 1 处误判，补充了 3 处新发现。

### Codex 结论验证表

| 问题 | Codex 说法 | Claude Code 验证 | 结论 |
|------|-----------|-----------------|------|
| scripts/src/ 污染 | 存在 | ✅ 确认，34KB 临时文件 | 需删除 |
| web_v2 产物泄漏 | node_modules/.env/.db | ✅ 确认，161MB | 需清理+补 gitignore |
| 脚本路径计算错误 | 需要修复 | ❌ 实际正确（parent.parent） | **不需要修** |
| pyproject.toml 入口错误 | 指向旧目标 | ✅ 确认 | 需修复 |
| Web 接口绕过 LeoAPI | 需要 adapter | ✅ 确认，3 个入口都没用 | 需改造 |
| 文档路径过时 | 需要统一 | ✅ 确认，7+ 文件有旧路径 | 需批量替换 |
| SKILLS_MANIFEST 损坏 | 需修复 | ✅ 确认，内容挤在一行 | 需重新生成 |

### Claude Code 补充发现

| 新发现 | 说明 | 严重程度 |
|--------|------|---------|
| 根目录 leo_system.db | 72KB 数据库文件遗留在根目录 | 🟡 中 |
| 3 个缺失脚本 | validate_naming.py、check_duplicates.py、scaffold_skills.py 被文档引用但不存在 | 🟡 中 |
| LeoSystem 核心类未被使用 | src/leo_system/core.py 的 LeoSystem 类没有任何地方调用 | 🟢 低（暂不处理） |

---

## 阶段 0：保护措施（Codex 执行前必须先做）

### 任务 0.1：记录基线状态
```bash
cd d:/桌面/leo_ai_system
git status --short > docs/progress/refactor_baseline_status.txt
```

### 任务 0.2：备份关键配置
```bash
cp .gitignore .gitignore.backup
cp pyproject.toml pyproject.toml.backup
```

---

## 阶段 1：清理目录污染

### 任务 1.1：删除 scripts/src/ 临时目录
```bash
rm -rf scripts/src/
```

### 任务 1.2：删除根目录数据库文件
```bash
rm -f leo_system.db
```

### 任务 1.3：清理 web_v2 数据库产物
```bash
rm -f src/leo_interface/web_v2/api/leo_system.db
```

### 任务 1.4：补充 .gitignore 规则
在 `.gitignore` 文件末尾追加：
```gitignore

# === 2026-02-25 改造补充 ===
# 数据库文件
*.db
*.sqlite
*.sqlite3

# 输出目录
output/

# 临时生成的源码
scripts/src/

# Web 前端产物（双重保险）
src/leo_interface/web_v2/node_modules/
src/leo_interface/web_v2/.env
src/leo_interface/web_v2/api/.env
src/leo_interface/web_v2/api/*.db
```

### 验收
```bash
git status --short
# 不应再出现 scripts/src/、*.db、output/ 等文件
```

---

## 阶段 2：修复打包入口

### 任务 2.1：修改 pyproject.toml 第 50 行
```
旧：leo = "leo_system:main"
新：leo = "leo_system.cli:main"
```

### 验收
```bash
pip install -e .
leo --help
# 应该正常显示帮助信息
```

---

## 阶段 3：统一 Web 接口到 LeoAPI

### 任务 3.1：新建统一适配器
文件：`src/leo_interface/web_v2/api/leo_api_adapter.py`

```python
"""
Leo API 统一适配器
所有 Web 请求通过此适配器转发到 LeoAPI，确保入口唯一
"""
from pathlib import Path
from leo_orchestrator.api import LeoAPI

_api_instance = None

def get_leo_api() -> LeoAPI:
    """获取 LeoAPI 单例"""
    global _api_instance
    if _api_instance is None:
        project_root = Path(__file__).parent.parent.parent.parent.parent
        _api_instance = LeoAPI(str(project_root / "src"))
    return _api_instance
```

### 任务 3.2：新建统一请求/响应模型
文件：`src/leo_interface/web_v2/api/schemas.py`

```python
"""
统一请求/响应模型
"""
from pydantic import BaseModel, Field
from typing import Optional, Any
from uuid import uuid4

class LeoRequest(BaseModel):
    """统一请求"""
    intent: str = Field(..., description="用户意图")
    target: Optional[str] = Field(None, description="目标技能/代理")
    params: dict = Field(default_factory=dict, description="额外参数")
    trace_id: str = Field(
        default_factory=lambda: str(uuid4())[:8],
        description="追踪ID"
    )

class LeoResponse(BaseModel):
    """统一响应"""
    trace_id: str
    status: str  # "ok" 或 "error"
    intent: Optional[str] = None
    target: Optional[str] = None
    data: Any = None
    error_code: Optional[str] = None
    message: str = ""

class ErrorCode:
    E_VALIDATION = "E_VALIDATION"
    E_ROUTE = "E_ROUTE"
    E_SKILL = "E_SKILL"
    E_WORKFLOW = "E_WORKFLOW"
    E_INTERNAL = "E_INTERNAL"
```

### 任务 3.3：在 main.py 中新增统一入口端点
在 `src/leo_interface/web_v2/api/main.py` 中追加：

```python
from .leo_api_adapter import get_leo_api
from .schemas import LeoRequest, LeoResponse, ErrorCode

@app.post("/api/v2/execute", response_model=LeoResponse)
async def execute_unified(request: LeoRequest):
    """统一执行入口"""
    api = get_leo_api()
    try:
        routing = api.registry.intent_recognizer.route(request.intent)
        if routing["action"] == "delegate_to_agent":
            result = api.run_agent(routing["target"], request.intent)
        elif routing["action"] == "call_skill":
            result = api.call(routing["target"], "execute", **request.params)
        else:
            result = {"message": routing.get("response", "未识别的意图")}
        return LeoResponse(
            trace_id=request.trace_id,
            status="ok",
            intent=routing.get("intent_type"),
            target=routing.get("target"),
            data=result,
            message="执行成功"
        )
    except Exception as e:
        return LeoResponse(
            trace_id=request.trace_id,
            status="error",
            error_code=ErrorCode.E_INTERNAL,
            message=str(e)
        )
```

### 验收
启动 FastAPI 后，用 curl 测试：
```bash
curl -X POST http://localhost:8000/api/v2/execute \
  -H "Content-Type: application/json" \
  -d '{"intent": "查看系统状态"}'
# 应返回包含 trace_id、status、data 的 JSON
```

---

## 阶段 4：创建缺失脚本

### 任务 4.1：创建 scripts/development/validate_naming.py
功能：扫描 src/leo_skills/、src/leo_subagents/、src/leo_workflows/ 下所有目录名
检查规则：
- 不允许连字符 `-`
- 不允许空格
- 不允许大写字母开头
- 技能目录必须以 `_skill` 结尾
- 代理目录必须以 `_agent` 结尾
- 工作流目录必须以 `_pipeline` 结尾

输出格式：
```
✅ 通过: web_search_skill
❌ 违规: Web-Search-Skill (包含连字符和大写)
总计: 107 个技能, 9 个代理, 5 个工作流
违规: 0 个
```

### 任务 4.2：创建 scripts/development/check_duplicates.py
功能：读取所有 SKILL.md 的 description 和 activation_keywords 字段
用简单的关键词匹配检测功能重复（相似度 > 70% 报警）

### 任务 4.3：创建 scripts/development/scaffold_skills.py
功能：根据模板生成技能骨架
用法：`python scripts/development/scaffold_skills.py --name weekly_report --category content_creation`
生成：
```
src/leo_skills/content_creation/weekly_report_skill/
├── SKILL.md          （含标准 YAML frontmatter）
├── __init__.py
├── weekly_report_skill.py
├── config/config.yaml
├── evolution.json
└── scripts/main.py
```

### 验收
```bash
python scripts/development/validate_naming.py
python scripts/development/check_duplicates.py
python scripts/development/scaffold_skills.py --help
# 三个脚本都能正常运行
```

---

## 阶段 5：修复文档路径引用

### 任务 5.1：批量替换旧路径
在以下文件中执行全局替换：

| 旧路径 | 新路径 |
|--------|--------|
| `python scripts/update_capability_index.py` | `python scripts/maintenance/update_capability_index.py` |
| `python scripts/validate_structure.py` | `python scripts/development/validate_structure.py` |
| `python scripts/validate_skills.py` | `python scripts/development/validate_skills.py` |
| `python scripts/standardize_skills.py` | `python scripts/development/standardize_skills.py` |
| `python scripts/quick_test.py` | `python scripts/testing/quick_test.py` |
| `python scripts/manage_skills.py` | `python scripts/development/manage_skills.py` |
| `python scripts/create_skill.py` | `python scripts/development/create_skill.py` |
| `python scripts/validate_naming.py` | `python scripts/development/validate_naming.py` |
| `python scripts/check_duplicates.py` | `python scripts/development/check_duplicates.py` |

需要修改的文件：
1. `AGENTS.md`
2. `README.md`
3. `.github/copilot-instructions.md`
4. `docs/guides/CONTRIBUTING.md`
5. `docs/BEST_PRACTICE_CHECKLIST.md`
6. `docs/planning/PATH_NAMING_PREVENTION.md`
7. `leo_knowledge/context/user_profile.md`
8. `leo_knowledge/context/system_architecture.md`
9. `leo_knowledge/context/development_guide.md`

### 任务 5.2：重新生成 SKILLS_MANIFEST.md
运行 `python scripts/maintenance/update_capability_index.py` 重新生成
或手动修复 `docs/reference/SKILLS_MANIFEST.md` 的格式（确保每行一条）

### 验收
```bash
# 搜索所有 .md 文件中的旧路径引用
# 排除已知正确的子目录路径后，应该返回空
rg "python scripts/(update_capability|validate_structure|validate_skills|standardize_skills|quick_test|manage_skills|create_skill|validate_naming|check_duplicates)" --glob "*.md"
# 上面的结果中不应出现缺少子目录的旧路径
```

---

## 阶段 6：防复发门禁

### 任务 6.1：更新 CI 配置
在 `.github/workflows/ci.yml` 中增加：
```yaml
- name: 结构校验
  run: python scripts/development/validate_structure.py

- name: 命名校验
  run: python scripts/development/validate_naming.py

- name: 敏感文件检查
  run: |
    if git diff --cached --name-only | grep -E '\.(env|db|sqlite)$'; then
      echo "错误：检测到敏感文件"
      exit 1
    fi
```

### 任务 6.2：更新 PR 模板
在 `.github/PULL_REQUEST_TEMPLATE.md` 中增加勾选项：
```markdown
## 改造检查清单
- [ ] 文档中的命令路径已同步更新
- [ ] 新增文件符合 snake_case 命名规范
- [ ] 没有提交敏感文件（.env、.db、node_modules）
- [ ] 所有 Web 接口通过 LeoAPI 调用
```

---

## 执行顺序与时间估算

```
阶段 0（保护）  →  阶段 1（清理）  →  阶段 2（入口）  →  阶段 3（接口）  →  阶段 4（脚本）  →  阶段 5（文档）  →  阶段 6（门禁）
   5 分钟           10 分钟           2 分钟           30 分钟           20 分钟           15 分钟           10 分钟
```

每个阶段完成后单独 git commit，提交信息格式：
```
refactor: 阶段N - 简要说明
```

## 回滚方案

```bash
# 查看提交历史
git log --oneline -10

# 撤销最近一次提交（保留文件修改）
git reset --soft HEAD~1

# 恢复备份
cp .gitignore.backup .gitignore
cp pyproject.toml.backup pyproject.toml
```
