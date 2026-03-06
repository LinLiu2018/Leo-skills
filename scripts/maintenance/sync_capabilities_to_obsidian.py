"""
同步 Leo 能力清单到 Obsidian
将完整的能力清单文档同步到 Obsidian 知识库
"""

import sys
from pathlib import Path
from datetime import datetime
import shutil

def sync_capabilities_to_obsidian():
    """同步能力清单到 Obsidian"""

    print("=" * 60)
    print("Leo 能力清单同步到 Obsidian")
    print("=" * 60)
    print()

    # 配置路径
    project_root = Path(__file__).parent.parent.parent
    vault_path = Path("d:/桌面/Leo-Outputs")
    target_folder = vault_path / "10-Projects" / "Leo-System"

    # 确保目标文件夹存在
    target_folder.mkdir(parents=True, exist_ok=True)

    # 要同步的文档列表
    docs_to_sync = [
        {
            "source": project_root / "docs" / "reference" / "LEO_SYSTEM_CAPABILITIES.md",
            "target": target_folder / "Leo-System-完整能力清单.md",
            "name": "完整能力清单"
        },
        {
            "source": project_root / ".claude" / "SKILLS_SUMMARY.md",
            "target": target_folder / "Leo-System-技能摘要.md",
            "name": "技能摘要"
        },
        {
            "source": project_root / "docs" / "reference" / "LEO_SYSTEM_ARCHITECTURE_REPORT.md",
            "target": target_folder / "Leo-System-架构报告.md",
            "name": "系统架构报告"
        },
        {
            "source": project_root / "CLAUDE.md",
            "target": target_folder / "Leo-System-项目记忆.md",
            "name": "项目记忆"
        },
        {
            "source": project_root / "README.md",
            "target": target_folder / "Leo-System-README.md",
            "name": "README"
        }
    ]

    # 同步文档
    synced_count = 0
    skipped_count = 0

    for doc in docs_to_sync:
        source = doc["source"]
        target = doc["target"]
        name = doc["name"]

        if not source.exists():
            print(f"⚠️  跳过: {name} (源文件不存在)")
            skipped_count += 1
            continue

        try:
            # 复制文件
            shutil.copy2(source, target)
            print(f"✅ 已同步: {name}")
            print(f"   源: {source}")
            print(f"   目标: {target}")
            synced_count += 1
        except Exception as e:
            print(f"❌ 失败: {name} - {e}")
            skipped_count += 1

        print()

    # 创建索引文件
    print("创建索引文件...")
    index_content = f"""# Leo AI System - 文档索引

> 最后更新：{datetime.now().strftime('%Y-%m-%d %H:%M')}

## 📚 核心文档

### 能力清单
- [[Leo-System-完整能力清单]] - 完整的系统能力清单 (v3.0)
- [[Leo-System-技能摘要]] - 249个技能快速索引
- [[Leo-System-架构报告]] - 系统架构分析报告

### 项目文档
- [[Leo-System-项目记忆]] - CLAUDE.md 项目记忆
- [[Leo-System-README]] - 项目 README

## 📊 系统概览

| 类别 | 数量 |
|------|------|
| **核心架构模块** | 6个 |
| **技能 (Skills)** | 249个 |
| **代理 (Agents)** | 37个 |
| **插件 (Plugins)** | 1个 |
| **MCP 工具** | 7个 |
| **Hooks** | 3个 |
| **工作流** | 14个 |
| **脚本工具** | 99个 |
| **MVP 项目** | 1个 |
| **集成系统** | 3个 |

## 🎯 快速导航

### 按业务场景
- **房产业务**: realestate_agent, villa_agent, auction_agent
- **电商运营**: ecommerce_agent, amazon_skill, shopify_skill
- **内容营销**: content_agent, creative_agent, social-auto-publish
- **技术开发**: architect_agent, mobile_agent, fullstack_scaffold

### 按功能类型
- **核心架构**: Leo Gateway, Orchestrator, Memory, Config
- **业务技能**: 26个房产、电商、金融技能
- **开发工具**: 96个前后端、测试、DevOps工具
- **自动化**: 99个维护、业务、开发脚本

## 🔗 相关链接

- 项目路径: `d:\\桌面\\leo_ai_system`
- 技能注册表: `.claude/skill_registry.json`
- 代理配置: `src/leo_subagents/config/agents.yaml`

---

*自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""

    index_path = target_folder / "Leo-System-文档索引.md"
    try:
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(index_content)
        print(f"✅ 已创建: 文档索引")
        print(f"   路径: {index_path}")
        synced_count += 1
    except Exception as e:
        print(f"❌ 创建索引失败: {e}")

    print()

    # 总结
    print("=" * 60)
    print("同步完成！")
    print("=" * 60)
    print()
    print(f"✅ 成功同步: {synced_count} 个文档")
    print(f"⚠️  跳过: {skipped_count} 个文档")
    print()
    print("📂 Obsidian 位置:")
    print(f"   {target_folder}")
    print()
    print("📖 查看方式:")
    print("   1. 打开 Obsidian")
    print("   2. 进入 10-Projects/Leo-System/ 文件夹")
    print("   3. 打开 Leo-System-文档索引.md")
    print()


if __name__ == "__main__":
    try:
        sync_capabilities_to_obsidian()
    except Exception as e:
        print(f"❌ 同步过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
