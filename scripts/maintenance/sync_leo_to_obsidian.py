"""
Leo 项目文档同步到 Obsidian
将 Leo AI Agent System 的项目文档同步到 Obsidian 知识库
"""

import sys
from pathlib import Path
from datetime import datetime

# 添加路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "leo_skills" / "utilities" / "obsidian_sync_skill"))
from scripts.main import ObsidianSync


def sync_leo_project_to_obsidian():
    """同步 Leo 项目文档到 Obsidian"""

    print("=" * 60)
    print("Leo 项目文档同步到 Obsidian")
    print("=" * 60)
    print()

    # 初始化
    vault_path = "d:/桌面/Leo-Outputs"
    sync = ObsidianSync(vault_path=vault_path)

    project_root = Path(__file__).parent

    # ========== 1. 同步 CLAUDE.md（项目记忆）==========
    print("1. 同步项目记忆 (CLAUDE.md)")
    print("-" * 60)

    claude_md_path = project_root / "CLAUDE.md"
    if claude_md_path.exists():
        with open(claude_md_path, 'r', encoding='utf-8') as f:
            claude_content = f.read()

        result = sync.create_note(
            title="Leo-AI-Agent-System-项目记忆",
            content=claude_content,
            folder="10-Projects/Leo-System",
            tags=["leo-system", "project", "documentation"],
            template="default"
        )

        if result['success']:
            print(f"   已同步: {result['title']}")
        else:
            print(f"   跳过: {result.get('error', '已存在')}")
    print()

    # ========== 2. 同步主 README ==========
    print("2. 同步项目 README")
    print("-" * 60)

    readme_path = project_root / "README.md"
    if readme_path.exists():
        with open(readme_path, 'r', encoding='utf-8') as f:
            readme_content = f.read()

        result = sync.create_note(
            title="Leo-System-README",
            content=readme_content,
            folder="10-Projects/Leo-System",
            tags=["leo-system", "readme"],
            template="default"
        )

        if result['success']:
            print(f"   已同步: {result['title']}")
        else:
            print(f"   跳过: {result.get('error', '已存在')}")
    print()

    # ========== 3. 同步 Skills 文档 ==========
    print("3. 同步 Skills 文档")
    print("-" * 60)

    skills_dir = project_root / "leo_skills"
    skill_count = 0

    # 遍历所有 Skills
    for skill_dir in skills_dir.rglob("*-cskill"):
        skill_md = skill_dir / "SKILL.md"
        if skill_md.exists():
            skill_name = skill_dir.name

            with open(skill_md, 'r', encoding='utf-8') as f:
                skill_content = f.read()

            result = sync.create_note(
                title=f"Skill-{skill_name}",
                content=skill_content,
                folder="10-Projects/Leo-System/Skills",
                tags=["leo-system", "skill", skill_name],
                template="default"
            )

            if result['success']:
                print(f"   已同步: {skill_name}")
                skill_count += 1
            else:
                print(f"   跳过: {skill_name}")

    print(f"   共同步 {skill_count} 个 Skills")
    print()

    # ========== 4. 创建项目概览 MOC ==========
    print("4. 创建项目概览 MOC")
    print("-" * 60)

    project_overview = f"""# Leo AI Agent System - 项目概览

> 最后更新：{datetime.now().strftime('%Y-%m-%d %H:%M')}

## 项目简介

Leo AI Agent System 是一个 Skills + Subagents 协同工作的 AI 智能体系统。

## 核心组件

### Skills（能力库）
- [[Skill-twitter_monitor_skill]] - Twitter 监控
- [[Skill-obsidian_sync_skill]] - Obsidian 同步
- [[Skill-content_layout_leo_skill]] - 内容排版
- [[Skill-research_assistant_skill]] - 研究助手

### Subagents（执行者）
- Task Agent - 通用任务执行
- Research Agent - 研究调研
- Creative Agent - 内容创作
- Analysis Agent - 数据分析

### Workflows（工作流）
- Content Pipeline - 内容创作工作流
- Research Pipeline - 研究调研工作流
- Analysis Pipeline - 数据分析工作流

## 项目文档

- [[Leo-AI-Agent-System-项目记忆]] - 完整的项目记忆
- [[Leo-System-README]] - 项目 README

## 技术栈

- Python 3.13+
- Claude API
- Twitter API
- Obsidian

## 开发日志

### 2026-01-23
- 实现 twitter_monitor_skill
- 实现 obsidian_sync_skill
- 打通技术情报到知识库的完整流程

## 下一步计划

- [ ] 实现 tech_extractor_skill
- [ ] 实现 skill_code_generator_skill
- [ ] 创建 3 个新 Agents
- [ ] 完善工作流引擎

---

*自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""

    result = sync.create_note(
        title="Leo-AI-Agent-System-概览",
        content=project_overview,
        folder="10-Projects/Leo-System",
        tags=["leo-system", "moc", "project-overview"],
        template="default"
    )

    if result['success']:
        print(f"   已创建: 项目概览 MOC")
    else:
        print(f"   跳过: {result.get('error', '已存在')}")
    print()

    # ========== 5. 创建待办事项笔记 ==========
    print("5. 创建项目待办事项")
    print("-" * 60)

    todo_content = f"""# Leo System - 待办事项

> 最后更新：{datetime.now().strftime('%Y-%m-%d %H:%M')}

## 进行中 🚧

- [x] 实现 twitter_monitor_skill
- [x] 实现 obsidian_sync_skill
- [x] 打通 Obsidian 知识复利流程

## 待实现 📋

### 阶段 2：技术提取
- [ ] 创建 tech_extractor_skill
- [ ] 实现关键词提取器
- [ ] 实现 LLM 提取器
- [ ] 实现技术分类器

### 阶段 3：代码生成
- [ ] 创建 skill_code_generator_skill
- [ ] 实现 Skill 生成器
- [ ] 实现 Agent 生成器
- [ ] 实现 Workflow 生成器

### 阶段 4：Agents
- [ ] 创建 tech-intelligence-agent
- [ ] 创建 tech-analyzer-agent
- [ ] 创建 code-generator-agent
- [ ] 更新 agents.yaml 配置

### 阶段 5：工作流
- [ ] 创建 tech-intelligence-pipeline
- [ ] 集成所有组件
- [ ] 实现定时调度

### 阶段 6：测试和优化
- [ ] 创建测试脚本
- [ ] 端到端测试
- [ ] 性能优化
- [ ] 文档完善

## 已完成 [SUCCESS]

- [x] 项目架构设计
- [x] 目录结构标准化
- [x] Twitter 监控功能
- [x] Obsidian 集成
- [x] 知识复利机制

## 相关笔记

- [[Leo-AI-Agent-System-概览]]
- [[Leo-AI-Agent-System-项目记忆]]

---

*自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""

    result = sync.create_note(
        title="Leo-System-待办事项",
        content=todo_content,
        folder="10-Projects/Leo-System",
        tags=["leo-system", "todo", "project-management"],
        template="default"
    )

    if result['success']:
        print(f"   已创建: 项目待办事项")
    else:
        print(f"   跳过: {result.get('error', '已存在')}")
    print()

    # ========== 总结 ==========
    print("=" * 60)
    print("同步完成！")
    print("=" * 60)
    print()
    print("已同步到 Obsidian:")
    print("1. 项目记忆 (CLAUDE.md)")
    print("2. 项目 README")
    print(f"3. {skill_count} 个 Skills 文档")
    print("4. 项目概览 MOC")
    print("5. 项目待办事项")
    print()
    print("在 Obsidian 中查看:")
    print("- 打开 10-Projects/Leo-System/ 文件夹")
    print("- 查看 Leo-AI-Agent-System-概览.md")
    print("- 浏览所有项目文档和 Skills")
    print()


if __name__ == "__main__":
    try:
        sync_leo_project_to_obsidian()
    except Exception as e:
        print(f"同步过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
