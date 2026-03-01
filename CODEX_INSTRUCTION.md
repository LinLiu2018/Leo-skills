# Codex 执行指令：Leo Skills 执行器化改造

## 任务目标
将5个数据监测类技能改造为支持 OpenClaw 系统事件直接调用，无需经过 Agent 推理。

## 执行步骤（按顺序）

### Step 1: 创建脚本文件

创建 `scripts/run_skill_direct.py`：
- 从 `leo_orchestrator.registry` 导入 `UnifiedRegistry`
- 动态导入 skill 类，检查 `supports_direct_execution` 属性
- 构建 `ExecutionContext`，调用 `skill.run(context)`
- 输出 JSON 格式结果

创建 `scripts/sync_skill_schedules.py`：
- 扫描所有 skill，检查 `default_schedule` 类属性
- 读取 `~/.openclaw/cron/jobs.json`
- 为支持直接执行的 skill 创建定时任务（payload kind=systemEvent）
- 保存回 jobs.json

### Step 2: 修改 leo-system 插件

编辑 `~/.openclaw/extensions/leo-system/index.js`：
- 添加 `api.onSystemEvent(/^skill:(\w+):execute$/, async (event, payload) => {...})`
- 在 handler 中调用 `executeSkillScript(skillName, payload)` 函数
- `executeSkillScript` 使用 spawn 运行 `python scripts/run_skill_direct.py --skill {name} --payload {...}`
- 返回 `{content, markdown, data}` 格式

### Step 3: 改造 5 个技能

每个技能添加类属性：
```python
supports_direct_execution = True
default_schedule = "cron表达式"
```

改造 `execute(self, context=None, **kwargs)` 方法：
- 从 context/params 获取参数
- 复用原有业务逻辑
- 返回 `SkillResult.ok(data=..., content=..., markdown=...)`

技能列表：
1. `src/leo_skills/business/video_monitor_skill/video_monitor_skill.py` - `0 8 * * *`
2. `src/leo_skills/business/competitor_scraper_skill/competitor_scraper_skill.py` - `0 10 * * 2`
3. `src/leo_skills/automation/auto_logger_skill/auto_logger_skill.py` - `0 * * * *`
4. `src/leo_skills/intelligence/twitter_monitor_skill/twitter_monitor_skill.py` - `0 */6 * * *`
5. `src/leo_skills/core/evolution/evolution_skill.py` 或其他 health check 技能 - `0 */4 * * *`

### Step 4: 测试

1. 运行 `python scripts/run_skill_direct.py --skill video_monitor_skill --payload '{"city":"宁波"}'`
2. 运行 `python scripts/sync_skill_schedules.py`
3. 运行 `openclaw cron list` 确认任务已添加
4. 在飞书测试 Agent 调用是否仍可用

## 关键要求

- 保持向后兼容：skill 原有调用方式不变
- 不要删除现有定时任务，只添加新的
- 所有错误返回 JSON 格式，不要抛出异常
- 备份 `~/.openclaw/cron/jobs.json` 后再修改

## 参考文件

完整计划见：`C:\Users\刘方林\.claude\plans\scalable-zooming-kitten.md`
