# Leo System 重构与标准化实施计划

## 1. 目标与愿景

打造一个**结构清晰、易于扩展、符合工程标准**的 AI 智能体系统。解决当前文件命名混乱（横杠与下划线混用）、模块导入困难、顶层目录臃肿的问题，为系统的"自我进化"和"复利增长"奠定坚实的架构基础。

## 2. 核心重构策略

采用标准的 Python 包结构，将核心逻辑、业务数据、前端界面和配置分层管理。

### 2.1 目录结构标准化

我们将从当前的混合结构迁移到以下标准结构：

```text
AI_claude_skills/
├── leo_system/                 # [核心] 系统核心逻辑包 (原 leo-system.py 拆分)
│   ├── __init__.py            # 暴露 get_system()
│   ├── core.py                # LeoSystem 主类
│   └── config.py              # 配置加载逻辑
├── leo_orchestrator/          # [核心] 编排层 (保持)
├── leo_subagents/             # [核心] 子代理与执行层 (保持)
│   ├── core/                  # 核心组件 (TaskExecutor, MetaSkills)
│   ├── agents/                # 具体的 Agent 实现
│   └── skills_bridge/         # Skill 加载与适配
├── leo_interface/             # [界面] 前端界面包 (新)
│   ├── web/                   # Streamlit Web UI
│   │   ├── app.py             # 主入口 (原 leo_web_ui_v4.py)
│   │   ├── components/        # UI 组件拆分
│   │   └── utils/             # 前端工具函数
│   └── cli/                   # 命令行工具
├── leo_skills/                # [资产] 技能库 (原 leo_skills 重命名)
│   ├── development/
│   ├── tools/
│   └── ...
├── leo_workflows/             # [资产] 工作流 (原 leo_workflows 重命名)
├── config/                    # [配置] 全局配置
│   ├── settings.yaml
│   └── secrets.yaml
├── projects/                  # [数据] 用户项目数据
├── tests/                     # [测试] 单元与集成测试
├── pyproject.toml             # [元数据] 项目依赖与构建配置
└── README.md
```

### 2.2 关键变更点

1. **模块化核心**：废弃单文件 `leo-system.py`，转为 `leo_system` 包，支持 `import leo_system`。
2. **统一命名规范**：所有 Python 模块目录统一使用 `snake_case` (下划线)，资源目录（如技能）若包含代码也建议用下划线，或者建立明确的映射机制。建议将 `leo_skills` 重命名为 `leo_skills` 以便未来支持 Python 动态加载。
3. **UI 独立化**：将散落在根目录的 `leo_web_ui_v*.py` 整合进 `leo_interface/web`，保持根目录整洁。
4. **环境隔离**：确保 VS Code (Claude Code) 和 Web UI 运行在同一上下文，通过 `pyproject.toml` 统一管理依赖。

## 3. 实施步骤

### 阶段一：核心重组 (Foundation)

- [ ] 创建 `leo_system` 包目录，迁移 `leo-system.py` 逻辑。
- [ ] 创建 `leo_interface` 包目录。
- [ ] 更新 `pyproject.toml`，将 `leo_system` 等注册为可安装包。
- [ ] 验证：`pip install -e .` 后可以在任意位置导入 `leo_system`。

### 阶段二：资产迁移 (Migration)

- [ ] 重命名 `leo_skills` -> `leo_skills` (需要批量更新 SKILL.md 中的引用路径，如果不重命名，则需在加载器中做特殊处理。**建议：为保持现有 Skills 兼容性，暂时保留 `leo_skills` 目录名，但在内部映射为模块时处理，或者逐步迁移。考虑到"复利"，长痛不如短痛，建议标准化为 `leo_skills`**)。
- [ ] 重命名 `leo_workflows` -> `leo_workflows`。
- [ ] 修复 `SkillLoader` 和 `AgentDiscovery` 中的路径依赖。

### 阶段三：前端集成 (Integration)

- [ ] 将 `leo_web_ui_v4.py` 迁移至 `leo_interface/web/app.py`。
- [ ] 拆分 UI 组件到 `leo_interface/web/components/`。
- [ ] 创建根目录启动脚本 `run_leo.py` 或 `leo.exe` (通过 entry_points)。

### 阶段四：验证与文档 (Verification)

- [ ] 运行全套测试：`pytest tests/`。
- [ ] 启动新版 Web UI 验证功能。
- [ ] 更新项目 README 和开发文档。

## 4. 关于 VS Code 协作

- **互不干扰**：文件重组后，VS Code 中的 Claude Code 插件只需重新索引（或感知文件变动）。
- **统一视图**：重构后的结构更符合 IDE 的解析习惯，不论是 VS Code 还是其他编辑器，都能更好地支持代码跳转和补全。

## 5. 待确认事项

- 是否同意将 `leo_skills` 目录重命名为 `leo_skills`？(这可能涉及修改大量现有 Skill 文件中的路径引用，或者我们可以保留文件夹名为横杠，但在 Python 代码中统一处理)。
  - *建议方案*：代码包用下划线 (`leo_subagents`)，资源目录保留现有习惯 (`leo_skills`) 以免破坏外部链接，但在加载器中增强兼容性。
