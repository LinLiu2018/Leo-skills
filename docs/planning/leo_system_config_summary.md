# Leo AI System 配置总览

> 从飞书对话历史中自动提取

---

## 1. 定时任务 (Cron Jobs)

| 任务名称 | 来源会话 |
|---------|---------|
| 5278d3c1-9437-4334-bcb1-fb84867e44e0 AI与OpenClaw_每日报告 | 0778b0a3 |
| 1c77af71-dd8b-481a-a21a-8a6a95f03ed1 宁波别墅_每日内容策略 | 0bbd49c5 |
| 8737fa6f-4d9c-45a9-9ce6-3b065e521783 视频号公众号_内容收集 | 24e7b203 |
| a41b8755-f2f1-4610-be50-50977032d1e7 优质内容_每日OpenClaw | 3c039303 |
| 5f621277-7750-4cd4-af56-006da86fbfab 房产资讯_每日8点_v2 | 3c1fe593 |
| f87cdf9d-1df2-4267-a136-2374040dbeab X 平台博主_每日检查 | 77f6a10f |
| a88f32fd-ecc8-48fd-b8c0-db9c38bedb74 房产资讯_每日8点_v3 | 7a1bc59d |
| 6b75c20d-279c-4768-a620-e4f58546a115 竞品监控_每日 9 点 | a0741c92 |
| 158efa7e-30a9-433a-b926-202b4a65ebcd 宁波别墅_抖音_每日监控 | a08ccd25 |
| 49899550-2afb-4316-97f4-27e7be4a8481 房产内容创意_每日早 | a2fb153a |
| ee99b6b9-78e7-4403-b6d4-fc584885bb28 X 平台监控_周报 | ac86f929 |
| 86b92a15-0412-4eef-b67e-cd9f3ad796a8 X 平台内容_学习转化 | d00308ce |
| fef0abb0-8a37-4374-aff0-0171c3a6a176 宁波别墅_小红书_每日监控 | de9499f2 |
| c5e55bac-63b3-41b0-9c76-c12091e3e65b AI财经资讯_每日8点_v2 | e91c0777 |
| 0bd8bb7b-2f6b-40ef-b448-0556de9868fa AI财经政治_每日8点_v3 | eeb8662e |

---

## 2. 技能 (Skills)

```
- 人工智能与OpenClaw每日内容收集与报告生成
- subagent_creator_skill:execute
- skill_manager_skill:execute
- business_research_skill:execute
- weui_miniprogram_skill:execute
- evolution_skill:execute
- skill_evolution_manager_skill:execute
- skill_orchestrator_skill:execute
- video_monitor_skill:execute
- github_to_skills_skill:execute
- competitor_scraper_skill:execute
- 视频号和公众号相关内容收集
- auto_logger_skill:execute
- web_search_skill:execute
- vant_weapp_skill:execute
- 今日的定时
- github_skills_monitor_skill:execute
- twitter_monitor_skill:execute
- image_generator_skill:execute
- github_skills_updater_skill:execute
```

---

## 3. AI 人格设定


---

## 4. 用户偏好

> <think>
用户要求搜索过去24小时关于OpenClaw、AI创业、流量运营、商业地产、房产经纪、AI眼镜等领域的优质公众号文章。但是从搜索结果来看，大部分是B站视频、36氪文章、Wikipedia等来源，并没有直接找到公众号的文章。

让我分析搜索结果中可用的内容：

1. OpenClaw相关：
- Wikipedia文章 - OpenClaw发展历史（8小时前）
- 阿里云部署教程（17小时前）
- 36氪 - OpenClaw最佳工具榜（12小时前）
- Crypto.com介绍（19小时前）
- 阿里云百炼文档（1天前）

2. AI创业相关：
- 36氪 - 2026国产AI芯


---

## 5. OpenClaw 配置

> Hey! Another scheduled trigger came through — this one is for **auto_logger_skill** again (same as the 14:00 one).

This skill doesn't appear in my available skills list. It might be:
- A custom skill you set up somewhere
- An internal system skill
- Or perhaps the skill name got misconfigured somew

> No auto_logger skill found on this system. 

**Summary for you:**
- 🔔 **Trigger:** `skill:auto_logger_skill:execute` 
- 📭 **Result:** Skill not found

This might be:
1. A leftover from a previous setup
2. A skill defined elsewhere I can't access
3. Something that needs to be installed/set up

Would 

> 🔔 **Hourly Health Check** — 15:00

Same issue as before — the OpenClaw config needs fixing before the health check can run properly.

**Problem:** `commands.ownerDisplay` is not a valid config key

**Fix:**
```bash
npx openclaw doctor --fix
```

Want me to run that fix now so the health checks can p

> 🔔 **16:00** — `skill:github_skills_updater_skill:execute`

Also not found ❌

**Today's total of missing skills:**
- `auto_logger_skill` (14:00, 15:00, 16:00) — 3x
- `github_skills_monitor_skill` (16:00)
- `github_skills_updater_skill` (16:00)
- `evolution_skill` (16:00)

These scheduled tasks seem t

> 🔔 **16:01** — `skill:github_to_skills_skill:execute`

Also not found ❌

That's **10+ invalid skill triggers** in the past 2 hours. Something's definitely misconfigured in your scheduler.

Want me to find and disable these phantom scheduled tasks?


---

## 统计信息

- 定时任务: 15 个
- 技能: 20 个
- AI人格设定: 0 条
- 用户偏好: 1 条
- OpenClaw配置: 19 条
