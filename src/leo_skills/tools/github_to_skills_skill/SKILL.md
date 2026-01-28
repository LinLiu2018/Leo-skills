# GitHub to Skills Skill (GitHub仓库转AI技能工具)

## 技能描述

将GitHub仓库自动转换为专业化AI技能。支持获取仓库元数据、创建标准化技能目录结构、生成带生命周期管理的SKILL.md文件。

## 核心能力

- **元数据获取**: 自动提取仓库README、文件结构、依赖关系
- **结构创建**: 生成标准化的技能目录结构（snake_case命名）
- **文档生成**: 创建完整的SKILL.md生命周期管理文档
- **一键转换**: 批量将多个GitHub仓库转换为技能

## 使用方法

```python
from github_to_skills_skill import GitHubToSkillsSkill

skill = GitHubToSkillsSkill(
    skill_name="github_to_skills",
    config_path="github_to_skills_skill/config/config.yaml"
)

# 转换单个仓库
result = skill.execute(
    action="convert",
    repo_url="https://github.com/owner/repo",
    output_dir="src/leo_skills/my_skills"
)

# 批量转换
result = skill.execute(
    action="batch_convert",
    repo_list=["owner/repo1", "owner/repo2"]
)
```

## 配置文件

参考 `config/config.yaml`

## 进化机制

本技能支持自我进化能力：
- 根据转换失败经验优化解析逻辑
- 自动学习最佳目录结构实践
- 持续改进SKILL.md模板质量
