# Contributing to Leo AI Agent System

感谢你对 Leo AI Agent System 的兴趣！我们欢迎各种形式的贡献。

## 🚀 快速开始

### 开发环境设置

```bash
# 1. Clone 项目
git clone https://github.com/LinLiu2018/Leo-skills.git
cd Leo-skills

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安装开发依赖
pip install -e ".[dev]"

# 4. 安装 pre-commit hooks
pip install pre-commit
pre-commit install
```

## 📋 贡献流程

### 1. Fork & Clone

```bash
# Fork 项目到你的 GitHub 账户
# 然后 clone 你的 fork
git clone https://github.com/YOUR_USERNAME/Leo-skills.git
```

### 2. 创建分支

```bash
# 从 main 分支创建特性分支
git checkout -b feature/your-feature-name

# 或者修复 bug
git checkout -b fix/bug-description
```

### 3. 开发

- 遵循代码规范（Black + isort + flake8）
- 添加必要的测试
- 更新相关文档

### 4. 提交

```bash
# pre-commit 会自动运行代码检查
git add .
git commit -m "feat: 添加新功能描述"

# 提交类型:
# feat: 新功能
# fix: Bug 修复
# docs: 文档更新
# style: 代码格式
# refactor: 重构
# test: 测试相关
# chore: 其他
```

### 5. 推送 & PR

```bash
git push origin feature/your-feature-name
```

然后在 GitHub 上创建 Pull Request。

## 📁 代码规范

### Python 代码

- **格式化**: Black (line-length=100)
- **导入排序**: isort (profile=black)
- **代码检查**: flake8
- **类型注解**: 推荐使用

### 文件命名

- Python 模块: `snake_case.py`
- Skills 目录: `kebab-case-cskill/`
- 配置文件: `config.yaml`

### 目录结构

```
src/
├── leo_skills/       # Skill 能力库
├── leo_subagents/    # Agent 执行层
├── leo_orchestrator/ # 编排器
├── leo_workflows/    # 工作流
└── leo_system/       # 系统核心
```

## 🧪 测试

```bash
# 运行所有测试
pytest tests/ -v

# 带覆盖率
pytest tests/ --cov=src --cov-report=html

# 运行特定测试
pytest tests/test_agents.py -v
```

## 📝 添加新 Skill

1. 在 `src/leo_skills/<category>/` 创建目录
2. 添加必需文件:
   - `SKILL.md` - Skill 定义
   - `README.md` - 使用说明
   - `scripts/main.py` - 入口脚本

3. 运行发现系统验证:
   ```bash
   python scripts/manage_skills.py update
   ```

## 🤖 添加新 Agent

1. 在 `src/leo_subagents/agents/` 创建目录
2. 继承 `BaseAgent` 类
3. 实现 `can_handle()` 和 `execute()` 方法
4. 在 `agents.yaml` 中注册

## ❓ 问题反馈

- **Bug 报告**: 使用 Bug Report Issue 模板
- **功能请求**: 使用 Feature Request Issue 模板
- **问题讨论**: 在 Discussions 中提问

## 📜 许可证

贡献的代码将在 MIT 许可证下发布。

---

感谢你的贡献！🎉
