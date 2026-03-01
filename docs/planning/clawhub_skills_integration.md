# ClawHub 热门技能集成计划

**创建时间**: 2026-02-27 10:30  
**来源**: Datawhale 公众号文章《最适合新手安装的 10 个小龙虾🦞 skills 来了！》  
**优先级**: P1 (高)

---

## 一、技能对比分析

### ClawHub 推荐 vs Leo AI System 现有

| ClawHub 技能 | 功能 | Leo 等效技能 | 状态 | 行动 |
|-------------|------|-------------|------|------|
| `self-improving-agent` | 自我迭代/主动代理 | ❌ 无 | 缺失 | **需创建** |
| `tavily-search` | 联网搜索 (Tavily) | ✅ `web_search_skill` | 已有 | 优化 |
| `gog` | Google Workspace | ❌ 无 | 缺失 | 评估需求 |
| `github` | GitHub 集成 | ❌ 无 | 缺失 | **需创建** |
| `summarize` | 总结 URL/PDF/YouTube | ⚠️ 部分 (summarizer.py) | 不完整 | **需完善** |
| `find-skills` | 搜索/推荐技能 | ❌ 无 | 缺失 | **需创建** |
| `ontology`/`memory` | 结构化记忆 | ⚠️ `memory_agent` | 不完整 | **需完善** |
| `weather` | 查天气 | ✅ `weather_skill` | 已有 | ✓ |
| `proactive-agent` | 主动规划 | ❌ 无 | 缺失 | **需创建** |
| `skill-vetter` | 安全扫描 | ❌ 无 | 缺失 | **需创建** |

**统计**:
- ✅ 已有：2 个 (weather, search)
- ⚠️ 不完整：2 个 (summarize, memory)
- ❌ 缺失：6 个 (self-improving, github, find-skills, proactive, skill-vetter, gog)

---

## 二、实现优先级

### P0 - 立即实现 (核心功能)

| 技能 | 理由 | 工时 |
|------|------|------|
| `skill_vetter_skill` | 安全第一，安装其他技能前需要 | 2 小时 |
| `web_search_skill_enhanced` | 在现有基础上增加 Tavily 支持 | 1 小时 |
| `github_integration_skill` | 开发者必备，GitHub 技能自动注册的升级版 | 3 小时 |

### P1 - 本周实现 (生产力提升)

| 技能 | 理由 | 工时 |
|------|------|------|
| `summarize_skill` | 信息消化高频需求 | 4 小时 |
| `memory_enhanced_skill` | 跨对话连贯性 | 4 小时 |
| `self_improving_agent` | 让 Agent 更聪明 | 6 小时 |

### P2 - 评估后实现 (按需)

| 技能 | 理由 | 决策 |
|------|------|------|
| `gog_skill` | Google Workspace 集成 | 需确认用户是否使用 Google 全家桶 |
| `proactive_agent` | 主动规划 | 可合并到 self_improving_agent |
| `find_skills_skill` | 技能发现 | 可合并到 capability_index 系统 |

---

## 三、实现方案

### 3.1 skill_vetter_skill (安全扫描)

**功能**:
- 扫描技能代码中的危险操作
- 检查网络请求、文件访问、系统命令
- 生成安全评分报告

**实现**:
```python
# src/leo_skills/tools/skill_vetter_skill/
class SkillVetterSkill:
    def scan_skill(self, skill_path: str) -> Dict:
        # 1. 静态代码分析
        # 2. 依赖检查
        # 3. 权限评估
        # 4. 生成报告
```

### 3.2 github_integration_skill (GitHub 集成)

**功能**:
- 搜索代码/仓库
- 管理 Issue/PR
- 创建/更新仓库
- 基于现有 `github_auto_register_skill` 升级

**实现**:
- 复用现有 `github_auto_register_skill` 架构
- 增加 gh CLI 集成
- 添加 Issue/PR 管理功能

### 3.3 summarize_skill (内容总结)

**功能**:
- URL 内容总结
- PDF 文档总结
- YouTube 视频总结
- 音频转录总结

**实现**:
```python
# src/leo_skills/utilities/summarize_skill/
class SummarizeSkill:
    def summarize_url(self, url: str) -> str
    def summarize_pdf(self, pdf_path: str) -> str
    def summarize_youtube(self, video_url: str) -> str
    def summarize_audio(self, audio_path: str) -> str
```

### 3.4 memory_enhanced_skill (增强记忆)

**功能**:
- 跨对话记忆存储
- 用户偏好学习
- 知识图谱构建
- 记忆检索优化

**实现**:
- 升级现有 `memory_agent`
- 添加结构化存储
- 实现记忆检索 API

### 3.5 self_improving_agent (自我迭代)

**功能**:
- 错误记录与分析
- 性能指标追踪
- 自动优化策略
- 版本演进管理

**实现**:
```python
# src/leo_subagents/agents/self_improving_agent/
class SelfImprovingAgent:
    def record_interaction(self, interaction: Dict)
    def analyze_errors(self) -> List[Insight]
    def generate_improvements(self) -> List[Action]
    def apply_optimization(self, action: Action)
```

---

## 四、执行步骤

### Step 1: skill_vetter_skill (立即)
```bash
# 创建技能目录
mkdir -p src/leo_skills/tools/skill_vetter_skill/{scripts,config}

# 创建文件
touch src/leo_skills/tools/skill_vetter_skill/{SKILL.md,__init__.py,skill_vetter_skill.py}
touch src/leo_skills/tools/skill_vetter_skill/config/{config.yaml,security_rules.yaml}
```

### Step 2: 升级 web_search_skill (1 小时)
- 添加 Tavily API 支持（可选）
- 优化并发控制
- 添加速率限制

### Step 3: 升级 github_auto_register_skill (2 小时)
- 重命名为 `github_integration_skill`
- 添加 Issue/PR 管理
- 添加仓库操作

### Step 4: 创建 summarize_skill (4 小时)
- 实现 URL 总结
- 集成 PDF 处理
- 添加 YouTube/音频支持

### Step 5: 升级 memory_agent (4 小时)
- 添加结构化存储
- 实现记忆检索 API
- 优化记忆更新逻辑

### Step 6: 创建 self_improving_agent (6 小时)
- 实现错误追踪
- 添加性能分析
- 实现自动优化

---

## 五、安装命令设计

参考 ClawHub 的安装方式：

```bash
# Leo AI System 版本
python scripts/skills/install.py skill_vetter_skill
python scripts/skills/install.py github_integration_skill
python scripts/skills/install.py summarize_skill

# 或者使用 Leo 命令
leo skill install skill_vetter_skill
leo skill install github_integration_skill
```

---

## 六、验证标准

每个技能完成后验证：

- [ ] 功能测试通过
- [ ] 安全扫描通过 (skill_vetter 自扫描)
- [ ] 文档完整 (SKILL.md + README)
- [ ] 注册到 capability_index.md
- [ ] 用户测试反馈

---

## 七、时间估算

| 阶段 | 技能 | 工时 | 完成时间 |
|------|------|------|----------|
| P0 | skill_vetter | 2h | 今日 |
| P0 | web_search_enhanced | 1h | 今日 |
| P0 | github_integration | 3h | 今日 |
| P1 | summarize | 4h | 明日 |
| P1 | memory_enhanced | 4h | 明日 |
| P1 | self_improving | 6h | 本周 |

**总计**: 20 小时

---

**请确认是否立即开始 P0 阶段实现？**

回复 "确认实现" 我立即开始创建 skill_vetter_skill 👍
