# 更新日志

本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/) 规范。

## [1.0.0] - 2026-01-23

### 新增

- **Agents**
  - ArchitectAgent - 架构设计代理
  - MobileAgent - 移动开发代理
  - ProductManagerAgent - 产品经理代理
  - ResearchAgent - 研究代理
  - CreativeAgent - 创作代理
  - AnalysisAgent - 分析代理
  - RealestateAgent - 房产代理
  - TaskAgent - 任务执行代理

- **Workflows**
  - analysis-pipeline - 数据分析工作流
  - content-pipeline - 内容创作工作流
  - research-pipeline - 研究调研工作流

- **基础设施**
  - `.pre-commit-config.yaml` - 代码质量钩子
  - `.github/workflows/ci.yml` - CI/CD 流程
  - 扩展单元测试覆盖

### 变更

- 统一目录命名为 snake_case
- 全局语言设置为简体中文 (zh-CN)
