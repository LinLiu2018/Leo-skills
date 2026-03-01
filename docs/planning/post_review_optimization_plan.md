# 审查后优化计划（Claude Code 审查 → Codex 执行）

> 基于 Claude Code 对阶段0-6的审查结论，以下为需要 Codex 执行的修复任务。
> 按优先级排列：P0 必须修、P1 应该修、P2 建议修。

---

## P0：必须修（影响 CI 或运行时）

### 任务 1：修复 7 个技能目录命名违规

validate_naming.py 报出 8 个违规，其中 `stock-analyzer-cskill` 是第三方参考示例不动，`agents` 目录是结构性的不动。剩余 6 个需要重命名：

| 当前目录名 | 新目录名 | 位置 |
|-----------|---------|------|
| `video_monitor` | `video_monitor_skill` | `src/leo_skills/business/` |
| `chain_of_thought_prompter` | `chain_of_thought_prompter_skill` | `src/leo_skills/prompt_engineering/` |
| `long_context_handler` | `long_context_handler_skill` | `src/leo_skills/prompt_engineering/` |
| `prompt_chaining_orchestrator` | `prompt_chaining_orchestrator_skill` | `src/leo_skills/prompt_engineering/` |
| `prompt_optimizer` | `prompt_optimizer_skill` | `src/leo_skills/prompt_engineering/` |
| `xml_structure_builder` | `xml_structure_builder_skill` | `src/leo_skills/prompt_engineering/` |

**操作步骤**：
1. `git mv` 重命名每个目录
2. 更新每个目录内 `__init__.py` 的 import 路径（如果有相对引用）
3. 更新每个目录内 `SKILL.md` 的 `name` 字段
4. 更新 `.py` 主文件名（如 `video_monitor.py` → `video_monitor_skill.py`）
5. 全局搜索旧路径引用并替换

**提交信息**：`refactor: 修复6个技能目录命名违规，统一 _skill 后缀`

---

### 任务 2：将 .trash 目录加入 .gitignore

`.trash/` 目录是阶段1的可回滚清理区，但没有被 gitignore，会被误提交。

**操作**：在 `.gitignore` 的 `# === 2026-02-25 改造补充 ===` 段落中追加：

```
# 可回滚清理区
.trash/
```

**提交信息**：`chore: 将 .trash 目录加入 gitignore`

---

### 任务 3：移除 main.py 中的 DEBUG 打印

文件：`src/leo_interface/web_v2/api/main.py`

**删除第 23-27 行**：
```python
# 调试: 打印环境变量          ← 删除
print(f"[DEBUG] Loading .env from: {env_path}")          ← 删除
print(f"[DEBUG] AI_PROVIDER: {os.getenv('AI_PROVIDER', 'NOT SET')}")  ← 删除
print(f"[DEBUG] AI_MODEL: {os.getenv('AI_MODEL', 'NOT SET')}")        ← 删除
print(f"[DEBUG] MINIMAX_API_KEY exists: {bool(os.getenv('MINIMAX_API_KEY'))}")  ← 删除
```

替换为（可选，用 logging）：
```python
import logging
logger = logging.getLogger(__name__)
logger.debug("Loading .env from: %s", env_path)
```

或者直接删除，不加 logging 也行（这些信息不是必需的）。

**提交信息**：`fix: 移除 web_v2 main.py 中的调试打印语句`

---

## P1：应该修（代码健壮性）

### 任务 4：加固 leo_api_adapter.py 的路径计算

文件：`src/leo_interface/web_v2/api/leo_api_adapter.py`

当前第 17 行用 5 层 `.parent` 定位项目根目录，太脆弱。

**替换为**：
```python
def _find_project_root() -> Path:
    """从当前文件向上查找包含 pyproject.toml 的目录作为项目根。"""
    current = Path(__file__).resolve().parent
    for _ in range(10):
        if (current / "pyproject.toml").exists():
            return current
        current = current.parent
    raise RuntimeError("无法定位项目根目录（未找到 pyproject.toml）")


def get_leo_api() -> LeoAPI:
    """获取 LeoAPI 单例。"""
    global _api_instance
    if _api_instance is None:
        project_root = _find_project_root()
        _api_instance = LeoAPI(str(project_root / "src"))
    return _api_instance
```

**提交信息**：`fix: 加固 leo_api_adapter 路径查找逻辑`

---

### 任务 5：清理根目录 leo-skills-old

validate_structure.py 报告根目录存在 `leo-skills-old/`（使用了连字符，且是旧版遗留）。

**操作**：
1. 检查 `leo-skills-old/` 内容是否已迁移到 `src/leo_skills/`
2. 如果已迁移，`git mv leo-skills-old .trash/leo-skills-old`
3. 如果未迁移，先标记待处理

**提交信息**：`chore: 移除根目录遗留的 leo-skills-old`

---

## P2：建议修（锦上添花）

### 任务 6：validate_naming.py 增加排除规则

当前脚本会误报第三方参考目录（如 `stock-analyzer-cskill`）和结构性目录（如 `agents`）。

**操作**：在 `validate_naming.py` 中增加排除列表：

```python
# 排除第三方参考和结构性目录
EXCLUDE_PATTERNS = {
    "stock-analyzer-cskill",  # 第三方参考示例
    "agents",                  # leo_subagents 结构性目录
}
```

在 `collect_*_dirs()` 函数返回前过滤掉这些目录。

**提交信息**：`fix: validate_naming 增加排除规则，避免误报`

---

### 任务 7：capability_index.md 瘦身

阶段5将 `capability_index.md` 从 0 行膨胀到 766 行。这个文件是自动生成的（由 `scripts/maintenance/update_capability_index.py` 生成），不应手动编辑。

**操作**：
1. 运行 `python scripts/maintenance/update_capability_index.py` 重新生成
2. 如果生成结果比 766 行短很多，用生成结果替换
3. 如果脚本报错，保持现状

**提交信息**：`chore: 重新生成 capability_index.md`

---

## 执行顺序建议

```
任务2（.gitignore）→ 任务3（DEBUG打印）→ 任务1（命名修复）→ 任务4（路径加固）→ 任务5（leo-skills-old）→ 任务6（排除规则）→ 任务7（索引瘦身）
```

每个任务单独提交，提交信息已给出。
