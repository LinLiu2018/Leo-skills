"""
AI 技术情报系统 - 完整演示脚本
模拟从 Twitter 采集到 Obsidian 知识沉淀的完整流程
"""

import sys
from pathlib import Path
from datetime import datetime

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 导入 Obsidian Sync
sys.path.insert(0, str(project_root / "leo_skills" / "utilities" / "obsidian-sync-cskill"))
from scripts.main import ObsidianSync


def demo_complete_workflow():
    """演示完整的技术情报工作流"""

    print("=" * 60)
    print("AI 技术情报系统 - 完整演示")
    print("=" * 60)
    print()

    # 初始化 Obsidian Sync
    vault_path = "d:/桌面/Leo-Outputs"
    sync = ObsidianSync(vault_path=vault_path)

    print("[SUCCESS] Obsidian Sync 初始化完成")
    print(f"📁 Vault 路径: {vault_path}")
    print()

    # ========== 步骤 1：模拟 Twitter 采集结果 ==========
    print("步骤 1: 模拟 Twitter 采集结果")
    print("-" * 60)

    mock_tweets = [
        {
            "author": "OpenAI",
            "content": "Excited to announce GPT-4 Turbo with improved reasoning and longer context windows! [LAUNCH]",
            "url": "https://twitter.com/OpenAI/status/123456",
            "likes": 15000,
            "retweets": 3000
        },
        {
            "author": "AnthropicAI",
            "content": "Claude Opus 4.5 is now available! Enhanced performance on complex reasoning tasks.",
            "url": "https://twitter.com/AnthropicAI/status/123457",
            "likes": 12000,
            "retweets": 2500
        },
        {
            "author": "LangChainAI",
            "content": "New LangChain release: Better integration with vector databases and improved streaming support.",
            "url": "https://twitter.com/LangChainAI/status/123458",
            "likes": 5000,
            "retweets": 800
        }
    ]

    print(f"[SUCCESS] 模拟采集到 {len(mock_tweets)} 条推文")
    for tweet in mock_tweets:
        print(f"   - @{tweet['author']}: {tweet['content'][:50]}...")
    print()

    # ========== 步骤 2：模拟技术提取结果 ==========
    print("步骤 2: 模拟技术提取结果")
    print("-" * 60)

    extracted_technologies = [
        {
            "name": "GPT-4 Turbo",
            "category": "大模型",
            "description": "OpenAI 最新发布的大语言模型，具有改进的推理能力和更长的上下文窗口",
            "source": "@OpenAI",
            "url": "https://twitter.com/OpenAI/status/123456",
            "why_important": "更长的上下文窗口意味着可以处理更复杂的任务，改进的推理能力提升了模型的实用性"
        },
        {
            "name": "Claude Opus 4.5",
            "category": "大模型",
            "description": "Anthropic 最新的大语言模型，在复杂推理任务上性能显著提升",
            "source": "@AnthropicAI",
            "url": "https://twitter.com/AnthropicAI/status/123457",
            "why_important": "在复杂推理任务上的性能提升，使其更适合专业领域应用"
        },
        {
            "name": "LangChain",
            "category": "AI框架",
            "description": "用于构建 LLM 应用的开发框架，新版本改进了向量数据库集成和流式支持",
            "source": "@LangChainAI",
            "url": "https://twitter.com/LangChainAI/status/123458",
            "why_important": "更好的向量数据库集成简化了 RAG 应用开发，流式支持改善了用户体验"
        }
    ]

    print(f"[SUCCESS] 提取到 {len(extracted_technologies)} 个技术")
    for tech in extracted_technologies:
        print(f"   - {tech['name']} ({tech['category']})")
    print()

    # ========== 步骤 3：创建每日技术情报笔记 ==========
    print("步骤 3: 创建每日技术情报笔记")
    print("-" * 60)

    today = datetime.now().strftime("%Y-%m-%d")

    # 构建每日情报内容
    daily_content = f"""## [DATA] 今日概览

- 采集推文：{len(mock_tweets)} 条
- 识别技术：{len(extracted_technologies)} 个
- 重点关注：{len(extracted_technologies)} 项

## [HOT] 重点技术

"""

    for i, tech in enumerate(extracted_technologies, 1):
        daily_content += f"""### {i}. [[{tech['name']}]]

**来源**：[@{tech['source'].replace('@', '')}]({tech['url']})
**分类**：{tech['category']}
**描述**：{tech['description']}

**为什么重要**：
{tech['why_important']}

**相关技术**：[[大语言模型]], [[AI应用开发]]

---

"""

    daily_content += """## [NOTE] 全部技术

"""

    for tech in extracted_technologies:
        daily_content += f"- [[{tech['name']}]] - {tech['description']}\n"

    daily_content += """
## 🔗 相关笔记

- [[AI-Technology-Map]] ← 技术地图
- [[2026-W04]] ← 本周汇总

## [IDEA] 思考与行动

### 值得深入研究
- [ ] 研究 GPT-4 Turbo 的上下文窗口扩展技术
- [ ] 对比 Claude Opus 4.5 和 GPT-4 Turbo 的性能差异
- [ ] 学习 LangChain 的向量数据库集成最佳实践

### 可以尝试的项目
- [ ] 使用 Claude Opus 4.5 构建一个复杂推理应用
- [ ] 用 LangChain 实现一个 RAG 系统
- [ ] 测试 GPT-4 Turbo 的长上下文能力

---

*由 AI 技术情报系统自动生成*
*最后更新：{datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""

    result = sync.create_note(
        title=f"{today}-AI技术情报",
        content=daily_content,
        template="default",
        folder="01-Daily",
        tags=["tech-intelligence", "daily", "ai", "auto-generated"]
    )

    if result['success']:
        print(f"[SUCCESS] 每日情报笔记已创建: {result['path']}")
    else:
        print(f"[ERROR] 创建失败: {result.get('error')}")
    print()

    # ========== 步骤 4：创建技术卡片 ==========
    print("步骤 4: 创建技术卡片")
    print("-" * 60)

    for tech in extracted_technologies:
        tech_content = f"""## 📌 基本信息

- **分类**：{tech['category']}
- **首次发现**：{today}
- **来源**：[@{tech['source'].replace('@', '')}]({tech['url']})

## [NOTE] 技术描述

{tech['description']}

## [IDEA] 为什么重要

{tech['why_important']}

## 🔗 相关技术

- [[大语言模型]]
- [[AI应用开发]]

## 📚 学习资源

- [官方公告]({tech['url']})

## 🤔 个人思考

这项技术的出现标志着 AI 领域的又一次重要进展。值得深入研究其技术细节和应用场景。

## [DATA] 发展历程

- **{today}**：首次发现，来自 {tech['source']}

---

*首次创建：{datetime.now().strftime('%Y-%m-%d %H:%M')}*
*最后更新：{datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""

        # 确定子文件夹
        subfolder_map = {
            "大模型": "AI-Models",
            "AI框架": "Frameworks",
            "AI工具": "Tools"
        }
        subfolder = subfolder_map.get(tech['category'], '')
        folder = f"02-Tech/{subfolder}" if subfolder else "02-Tech"

        result = sync.create_note(
            title=tech['name'],
            content=tech_content,
            template="default",
            folder=folder,
            tags=["tech", tech['category'].lower(), "ai"]
        )

        if result['success']:
            print(f"[SUCCESS] 技术卡片已创建: {tech['name']}")
        else:
            print(f"[WARNING]  {tech['name']}: {result.get('error', '已存在')}")

    print()

    # ========== 步骤 5：创建/更新 MOC（知识地图）==========
    print("步骤 5: 更新知识地图 (MOC)")
    print("-" * 60)

    tech_names = [tech['name'] for tech in extracted_technologies]
    result = sync.update_moc(
        moc_name="AI-Technology-Map",
        add_links=tech_names
    )

    if result['success']:
        print(f"[SUCCESS] 知识地图已更新: {result['moc_name']}")
        print(f"   添加了 {len(tech_names)} 个技术链接")
    else:
        print(f"[ERROR] 更新失败: {result.get('error')}")
    print()

    # ========== 步骤 6：创建今日日记 ==========
    print("步骤 6: 创建今日日记")
    print("-" * 60)

    result = sync.create_daily_note(
        plan=[
            "学习 GPT-4 Turbo 的新特性",
            "测试 Claude Opus 4.5 的推理能力",
            "研究 LangChain 的向量数据库集成"
        ],
        notes=f"""今天通过 AI 技术情报系统发现了 {len(extracted_technologies)} 个重要技术更新。

重点关注：
- GPT-4 Turbo 的上下文窗口扩展
- Claude Opus 4.5 的复杂推理能力提升
- LangChain 的新版本改进

这些技术都值得深入研究和实践。
""",
        links=tech_names + ["AI-Technology-Map"],
        tags=["tech-learning", "ai"]
    )

    if result['success']:
        print(f"[SUCCESS] 今日日记已创建: {result['date']}")
    else:
        print(f"[ERROR] 创建失败: {result.get('error')}")
    print()

    # ========== 总结 ==========
    print("=" * 60)
    print("🎉 演示完成！")
    print("=" * 60)
    print()
    print("已创建的笔记：")
    print(f"1. 📅 每日情报: 01-Daily/{today}-AI技术情报.md")
    print(f"2. [NOTE] 技术卡片: 02-Tech/AI-Models/GPT-4 Turbo.md")
    print(f"3. [NOTE] 技术卡片: 02-Tech/AI-Models/Claude Opus 4.5.md")
    print(f"4. [NOTE] 技术卡片: 02-Tech/Frameworks/LangChain.md")
    print(f"5. 🗺️  知识地图: 05-MOC/AI-Technology-Map.md")
    print(f"6. 📔 今日日记: 01-Daily/{today}.md")
    print()
    print("[IDEA] 下一步：")
    print("1. 在 Obsidian 中打开 Leo-Outputs vault")
    print("2. 查看生成的笔记和双向链接")
    print("3. 体验知识图谱的可视化效果")
    print("4. 开始积累您的 AI 技术知识库！")
    print()


if __name__ == "__main__":
    try:
        demo_complete_workflow()
    except Exception as e:
        print(f"[ERROR] 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
