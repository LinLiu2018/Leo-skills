# GitHub 技能自动集成实现计划

**创建时间**: 2026-02-26  
**优先级**: P1 (能力建设)  
**预计工时**: 1 天

---

## 一、现状分析

### 现有能力
- ✅ `github_skills_monitor_skill` - 每日扫描 GitHub
- ✅ `github_to_skills_skill` - GitHub 项目转技能
- ✅ `github_skills_updater_skill` - 技能更新

### 痛点
- ❌ 扫描后需要手动确认是否加载
- ❌ 技能注册需要手动操作
- ❌ 没有自动去重机制

---

## 二、目标能力

### 全自动流程
```
GitHub 扫描 → 质量评估 → 自动下载 → 自动注册 → 能力索引更新
```

### 关键改进
1. **自动质量评估**: Star 数 > 50, 最近更新 < 3 个月
2. **自动去重**: 检查现有技能，避免功能重复
3. **自动注册**: 添加到技能加载目录
4. **自动索引**: 更新 capability_index.md

---

## 三、实现方案

### 方案 A：升级现有技能（推荐）
- 修改 `github_skills_monitor_skill` 添加自动模式
- 新增 `github_auto_register_skill` 负责自动注册

### 方案 B：新建独立流程
- 创建 `github_auto_integration_pipeline` 工作流
- 定时任务触发

---

## 四、文件结构

```
src/leo_skills/tools/github_auto_register_skill/
├── SKILL.md
├── github_auto_register_skill.py
├── __init__.py
├── config/config.yaml
└── evolution.json
```

---

## 五、验收标准

- [ ] 能自动扫描 GitHub 热门技能
- [ ] 能自动评估质量（Star/更新时间）
- [ ] 能自动去重（检查功能重复）
- [ ] 能自动下载并注册到技能目录
- [ ] 能自动更新 capability_index.md
- [ ] 支持手动确认模式（安全模式）

---

## 六、风险控制

| 风险 | 应对 |
|------|------|
| 下载恶意代码 | 只扫描高星项目 + 人工审核模式 |
| 技能重复 | 自动去重检查 |
| 命名冲突 | 自动重命名 + 前缀 |
| 质量参差 | 质量阈值过滤 |

---

*进度更新：2026-02-26 开始开发*
