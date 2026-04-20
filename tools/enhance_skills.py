#!/usr/bin/env python3
"""
Leo Skills 增强优化脚本
分三步实施：
1. 细化 description - 为关键技能编写更具体的触发条件
2. 补充使用示例 - 为复杂技能添加输入输出示例
3. 创建 references/ - 为常用技能创建参考文档
"""

import os
import re
import yaml
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

SKILLS_DIR = Path(r"E:\桌面\leo_ai_system\src\leo_skills")

# ========== 第一步：细化 Description ==========

# 房产业务技能 - 详细触发条件
REAL_ESTATE_DESCRIPTIONS = {
    'pocket-crm': '口袋助理 CRM 集成技能，对接口袋助理数据实现 AI 增强的客户管理。当用户需要同步客户数据、分析通话录音、生成跟进策略、查看销售漏斗或创建日报周报时使用。',
    'property-valuation-skill': '房产估值技能，评估房产市场价值。当用户需要提供房产估值、分析市场成交价、生成估值报告或比较类似房源时使用。',
    'realestate-listing-skill': '房产房源管理技能，管理房源信息和发布。当用户需要发布新房源、更新房源信息、优化房源描述或管理房源状态时使用。',
    'leasing-management-skill': '租赁管理技能，处理租赁合同和租户事务。当用户需要管理租赁合同、跟踪租期、处理续租或生成租赁报告时使用。',
    'tenant-screening-skill': '租户筛选技能，评估租户资质和风险。当用户需要筛选潜在租户、验证信用记录、生成租户评估报告或检查租赁历史时使用。',
    'market-analysis-skill': '市场分析技能，分析房地产市场趋势。当用户需要分析市场趋势、研究竞争格局、生成市场报告或评估投资机会时使用。',
    'financial-analysis-skill': '财务分析技能，分析房产投资财务数据。当用户需要计算投资回报率、分析现金流、评估贷款方案或生成财务预测时使用。',
    'price-analysis-skill': '价格分析技能，优化房产定价策略。当用户需要制定定价策略、分析价格弹性、比较竞品定价或调整价格体系时使用。',
    'price-monitor-skill': '价格监控技能，追踪市场价格变化。当用户需要监控价格变动、接收价格预警、分析价格趋势或比较历史价格时使用。',
    'risk-assessment-skill': '风险评估技能，评估房产业务风险。当用户需要评估投资风险、生成风险报告、制定风控策略或检查合规性时使用。',
    'sales-sop-skill': '销售 SOP 执行技能，标准化销售流程。当用户需要执行销售流程、跟进销售线索、管理销售管道或生成销售报告时使用。',
    'customer-portrait-skill': '客户画像分析技能，分析客户特征和行为。当用户需要分析客户特征、识别客户需求、生成分群报告或制定营销策略时使用。',
}

# 电商技能 - 详细触发条件
ECOMMERCE_DESCRIPTIONS = {
    'amazon-skill': '亚马逊电商运营技能，管理亚马逊店铺和销售。当用户需要管理亚马逊店铺、处理 FBA 发货、优化 PPC 广告、进行产品调研或分析销售数据时使用。',
    'shopify-skill': 'Shopify 电商运营技能，管理 Shopify 独立站。当用户需要管理 Shopify 店铺、处理订单、优化转化率、管理产品或分析销售数据时使用。',
    'aliexpress-skill': '速卖通电商运营技能，管理速卖通跨境店铺。当用户需要管理速卖通店铺、处理跨境订单、优化 listing 或分析国际销售数据时使用。',
    'ebay-skill': 'eBay 电商运营技能，管理 eBay 拍卖店铺。当用户需要管理 eBay 店铺、处理订单、优化 listing 或分析销售表现时使用。',
    'inventory-skill': '库存管理技能，跟踪和优化库存水平。当用户需要跟踪库存数量、预测补货需求、处理库存预警或优化库存周转时使用。',
    'warehouse-skill': '仓储管理技能，管理仓库运营。当用户需要管理仓库布局、处理出入库、优化拣货路径或生成库存报告时使用。',
}

# 营销广告技能 - 详细触发条件
MARKETING_DESCRIPTIONS = {
    'ads-manager-skill': '广告投放管理技能，统一管理多渠道广告。当用户需要创建广告计划、调整出价策略、分析广告效果、优化 ROI 或比较渠道表现时使用。',
    'facebook-ads-skill': 'Facebook 广告投放技能，管理 Meta 广告平台。当用户需要创建 FB/IG 广告、管理广告组、设置像素追踪、分析广告数据或优化广告表现时使用。',
    'google-ads-skill': 'Google 广告投放技能，管理 Google 广告平台。当用户需要创建搜索广告、管理关键词、优化质量得分、分析 SEM 效果或管理广告预算时使用。',
    'competitor-monitor-skill': '竞品监控技能，追踪竞争对手动态。当用户需要监控竞品价格、追踪新品上架、分析竞品营销策略或接收竞争预警时使用。',
    'competitor-content-crawler-skill': '竞品内容爬取技能，抓取竞品营销素材。当用户需要抓取竞品网站内容、收集社交媒体帖子、分析竞品文案或下载营销素材时使用。',
}

# 内容创作技能 - 详细触发条件
CONTENT_DESCRIPTIONS = {
    'image-generator-skill': 'AI 图像生成技能，创建各种视觉内容。当用户需要生成营销图片、创建产品图、制作社交媒体配图或设计广告素材时使用。',
    'video-skill': '视频处理技能，编辑和生成视频内容。当用户需要剪辑视频、添加字幕、生成视频摘要或创建营销视频时使用。',
    'social-media-skill': '社交媒体管理技能，多平台内容发布。当用户需要发布社交媒体内容、管理多平台账号、分析互动数据或制定内容计划时使用。',
    'seo-skill': 'SEO 优化技能，提升网站搜索排名。当用户需要优化页面 SEO、研究关键词、分析搜索排名或制定 SEO 策略时使用。',
    'copywriting-skill': '文案撰写技能，创建营销文案。当用户需要撰写广告文案、创建产品描述、编写邮件营销内容或生成社交媒体文案时使用。',
    'article-generator-skill': '文章生成技能，创建长篇文章内容。当用户需要撰写博客文章、创建新闻稿、生成行业报告或编写说明文档时使用。',
    'keyword-research-skill': '关键词研究技能，发现和分析关键词机会。当用户需要研究关键词、分析搜索量、评估竞争程度或制定关键词策略时使用。',
}

# 开发工具技能 - 详细触发条件
DEV_DESCRIPTIONS = {
    'skill-code-generator-skill': '技能代码生成，创建 Leo Skills 代码。当用户需要创建新技能、生成技能模板、编写技能逻辑或调试技能代码时使用。',
    'api-doc-generator-skill': 'API 文档生成，为代码创建 API 文档。当用户需要生成 API 文档、创建接口说明、更新文档或导出 OpenAPI 规范时使用。',
    'docker-compose-generator-skill': 'Docker Compose 生成，创建容器编排配置。当用户需要创建 Docker Compose 文件、配置多容器应用、设置服务依赖或定义网络拓扑时使用。',
    'deployment-script-generator-skill': '部署脚本生成，创建自动化部署脚本。当用户需要创建部署脚本、配置 CI/CD 流程、设置自动化发布或生成回滚脚本时使用。',
    'react-component-generator-skill': 'React 组件生成，创建可复用 UI 组件。当用户需要创建 React 组件、生成组件模板、编写组件逻辑或优化组件性能时使用。',
    'vue-component-generator-skill': 'Vue 组件生成，创建 Vue 可复用组件。当用户需要创建 Vue 组件、生成组件模板、编写组合式 API 或优化组件结构时使用。',
}

# 工具集成技能 - 详细触发条件
TOOLS_DESCRIPTIONS = {
    'github-integration-skill': 'GitHub 集成技能，管理代码仓库和协作。当用户需要管理 GitHub 仓库、处理 Pull Request、查看 Issues 或自动化工作流时使用。',
    'notion-connector-skill': 'Notion 连接器，管理 Notion 数据库和页面。当用户需要同步 Notion 数据、创建页面、管理数据库或生成报告时使用。',
    'slack-skill-skill': 'Slack 集成技能，管理团队沟通。当用户需要发送 Slack 消息、管理频道、设置提醒或集成工作流通知时使用。',
    'calendar-skill-skill': '日历管理技能，管理日程和会议。当用户需要创建日程、安排会议、设置提醒或查看日历冲突时使用。',
    'gmail-skill': 'Gmail 邮件管理，处理电子邮件。当用户需要发送邮件、管理收件箱、创建邮件模板或自动化邮件工作流时使用。',
    'web-search-skill': '网页搜索技能，执行网络信息检索。当用户需要搜索网络信息、收集研究资料、验证事实或获取最新资讯时使用。',
    'pdf-analyzer-skill': 'PDF 分析技能，处理和分析 PDF 文档。当用户需要读取 PDF 内容、提取关键信息、总结文档或转换 PDF 格式时使用。',
}

# ========== 第二步：补充使用示例 ==========

# 为关键技能定义使用示例
USAGE_EXAMPLES = {
    'pocket-crm': '''
## 使用示例

### 示例 1：同步客户数据
```
用户：从口袋助?同步所有活跃客户
技能：正在连接口袋助理 API...
      已获取 156 个活跃客户
      客户数据已同步到本地数据库
```

### 示例 2：分析通话录音
```
用户：分析上周的客户通话录音
技能：正在分析 23 条通话录音...
      关键洞察：
      - 8 个客户表现出强烈购买意向
      - 5 个客户需要跟进报价
      - 平均通话时长：12 分钟
      已生成详细分析报告
```

### 示例 3：生成跟进策略
```
用户：为高意向客户生成跟进策略
技能：识别出 12 个高意向客户
      已为每个客户生成个性化跟进方案：
      - 客户 A：建议 24 小时内电话回访
      - 客户 B：发送详细房源资料
      - 客户 C：安排线下看房
```

### 示例 4：创建销售日报
```
用户：生成今天的销售日报
技能：正在汇总今日数据...
      📊 今日日报：
      - 新增客户：8 个
      - 通话时长：2.5 小时
      - 意向客户：3 个
      - 成交：1 套
      报告已发送到您的飞书
```
''',

    'property-valuation-skill': '''
## 使用示例

### 示例 1：单套房产估值
```
用户：评估宁波市鄞州区 XX 小区 120 平别墅的价值
技能：正在分析市场数据...
      📍 估值报告：
      - 市场参考价：850-920 万元
      - 单价：7.1-7.7 万元/平
      - 置信度：85%
      - 可比成交：3 套（近 3 个月）
      详细报告已生成
```

### 示例 2：批量估值
```
用户：评估我列表中的 10 套房产
技能：正在批量处理...
      ✅ 完成 10 套房产估值
      - 总价值：8,500 万元
      - 平均单价：6.8 万元/平
      - 最高：1,200 万元（XX 别墅）
      - 最低：450 万元（XX 公寓）
      Excel 报告已导出
```
''',

    'ads-manager-skill': '''
## 使用示例

### 示例 1：创建广告计划
```
用户：为 XX 楼盘创建 Facebook 广告计划
技能：正在创建广告计划...
      ✅ 广告计划已创建
      - 预算：5000 元/天
      - 受众：25-45 岁，宁波地区
      - 版位：Facebook+Instagram
      - 预计触达：50,000 人/天
```

### 示例 2：分析广告效果
```
用户：分析上周的广告表现
技能：正在汇总广告数据...
      📊 上周广告报告：
      - 总花费：35,000 元
      - 获客成本：280 元/线索
      - CTR：2.3%
      - 转化线索：125 个
      - ROI：1:4.2
      优化建议已生成
```

### 示例 3：优化出价策略
```
用户：优化 Google 广告的出价
技能：分析当前出价策略...
      🔧 优化建议：
      - 关键词 A：提高出价 15%（排名提升空间大）
      - 关键词 B：降低出价 20%（ROI 过低）
      - 关键词 C：保持当前出价
      预计可节省 18% 预算，提升 12% 转化
```
''',

    'image-generator-skill': '''
## 使用示例

### 示例 1：生成营销图片
```
用户：为 XX 楼盘生成 5 张营销海报
技能：正在生成图片...
      ✅ 已生成 5 张营销海报
      - 风格：现代简约
      - 尺寸：1080x1080 (社交媒体)
      - 包含：楼盘效果图 + 核心卖点
      图片已保存到/outputs/marketing/
```

### 示例 2：创建产品图
```
用户：为这套别墅生成室内效果图
技能：根据户型图生成效果图...
      ✅ 已生成 8 张室内效果图
      - 客厅、餐厅、厨房
      - 主卧、次卧×2、书房
      - 卫生间×2
      分辨率：4K，已导出
```
''',

    'amazon-skill': '''
## 使用示例

### 示例 1：产品调研
```
用户：调研瑜伽垫类目的市场机会
技能：正在分析亚马逊数据...
      📊 市场调研报告：
      - 月搜索量：125,000
      - 竞争程度：中等
      - 平均售价：$25-35
      - 最佳机会点：环保材质、加厚款
      详细报告已生成
```

### 示例 2：PPC 广告优化
```
用户：优化我的 PPC 广告活动
技能：分析广告表现...
      🔧 优化建议：
      - 暂停 5 个低效关键词（ACOS>50%）
      - 提高 8 个高效词出价（ACOS<20%）
      - 新增 12 个长尾词
      预计可降低 ACOS 从 35% 到 25%
```
''',

    'github-integration-skill': '''
## 使用示例

### 示例 1：查看 Issues
```
用户：查看我仓库的未关闭 Issues
技能：正在获取 Issues...
      📋 未关闭 Issues：12 个
      - 高优先级：3 个
      - 需要回复：5 个
      - Bug 报告：4 个
      详情已整理到表格
```

### 示例 2：处理 Pull Request
```
用户：帮我审查这个 PR
技能：正在分析代码变更...
      🔍 审查报告：
      - 变更文件：8 个
      - 新增代码：350 行
      - 潜在问题：2 个
      - 建议改进：3 处
      详细审查意见已生成
```
''',
}

# ========== 第三步：创建 References 模板 ==========

REFERENCES_TEMPLATES = {
    'pocket-crm': {
        'api-guide.md': '''# Pocket CRM API 集成指南

## 认证方式

```python
from pocket_crm_skill import PocketCRM

crm = PocketCRM(
    api_key="your_api_key",
    base_url="https://api.pocketassistant.com"
)
```

## 核心 API

### 获取客户列表
```python
customers = crm.get_customers(
    stage="需求分析",
    limit=100,
    tags=["高意向", "别墅"]
)
```

### 获取通话录音
```python
calls = crm.get_call_recordings(
    customer_id="cust_123",
    date_from="2026-03-01",
    date_to="2026-03-13"
)
```

### 创建跟进记录
```python
followup = crm.create_followup(
    customer_id="cust_123",
    content="客户对 XX 楼盘感兴趣，预算 800-1000 万",
    next_followup_date="2026-03-15"
)
```

## 速率限制

- 标准账户：100 次/分钟
- 企业账户：500 次/分钟

## 错误处理

```python
try:
    customers = crm.get_customers()
except RateLimitError:
    # 等待后重试
    time.sleep(60)
except AuthError:
    # 检查 API 密钥
    print("认证失败")
```
''',
        'best-practices.md': '''# Pocket CRM 最佳实践

## 客户数据同步

### 推荐频率
- 活跃客户：每小时同步
- 普通客户：每日同步
- 沉睡客户：每周同步

### 数据字段映射
| 口袋助理字段 | 本地字段 | 说明 |
|-------------|---------|------|
| customer_name | name | 客户姓名 |
| phone | phone | 联系电话 |
| stage | status | 销售阶段 |
| tags | tags | 标签列表 |

## 通话分析

### 关键指标
1. **通话时长** - 超过 10 分钟通常为高意向
2. **关键词频率** - "价格"、"看房"、"合同"等
3. **情绪分析** - 积极/中性/消极

### 跟进策略生成
根据通话分析结果，自动生成：
- 24 小时内回访（高意向）
- 发送资料（中意向）
- 定期培育（低意向）

## 销售漏斗管理

### 标准阶段
1. 初步接触
2. 需求分析
3. 房源推荐
4. 带看
5. 谈判
6. 成交

### 转化率基准
- 接触到带看：20-30%
- 带看到成交：10-15%
- 整体转化：2-5%
''',
    },

    'ads-manager-skill': {
        'platform-setup.md': '''# 广告平台设置指南

## Facebook Ads

### 账户准备
1. 创建 Business Manager
2. 添加广告账户
3. 设置像素追踪

### API 认证
```python
from facebook_business.api import FacebookAdsApi
FacebookAdsApi.init(
    app_id='YOUR_APP_ID',
    app_secret='YOUR_APP_SECRET',
    access_token='YOUR_ACCESS_TOKEN'
)
```

## Google Ads

### 账户准备
1. 创建 Google Ads 账户
2. 关联 Google Analytics
3. 设置转化追踪

### API 认证
```python
from google.ads.googleads.client import GoogleAdsClient
client = GoogleAdsClient.load_from_storage(
    "googleads_config.yaml"
)
```

## 预算分配建议

| 渠道 | 新手 | 进阶 | 成熟 |
|------|------|------|------|
| Facebook | 3000 元/天 | 10000 元/天 | 50000+ 元/天 |
| Google | 2000 元/天 | 8000 元/天 | 30000+ 元/天 |
| 小红书 | 1000 元/天 | 5000 元/天 | 20000+ 元/天 |
''',
        'optimization-tips.md': '''# 广告优化技巧

## Facebook Ads 优化

### 受众定位
- **核心受众**：25-45 岁，本地，对房产感兴趣
- **类似受众**：基于已成交客户创建 1-3% 类似
- **再营销**：访问过网站/互动过的用户

### 广告创意
- 使用真实房源图片
- 突出核心卖点（价格、地段、户型）
- 添加明确 CTA（立即咨询、预约看房）

### A/B 测试
测试变量：
- 图片/视频
- 标题文案
- 行动号召
- 受众细分

## Google Ads 优化

### 关键词策略
- **核心词**：宁波别墅、宁波新房
- **长尾词**：宁波鄞州区别墅价格、宁波学区房
- **否定词**：出租、二手、合租

### 质量得分提升
1. 提高广告相关性
2. 优化落地页体验
3. 提升预期 CTR

### 出价策略
- 手动 CPC（初期）
- 目标 CPA（数据积累后）
- 目标 ROAS（成熟期）

## 指标基准

| 指标 | 房产行业平均 | 优秀水平 |
|------|-------------|---------|
| CTR | 1-2% | 3%+ |
| CPC | 5-15 元 | 3-8 元 |
| 线索成本 | 200-500 元 | 100-200 元 |
| 成交转化率 | 2-5% | 8%+ |
''',
    },

    'skill-code-generator-skill': {
        'skill-template.md': '''# Skill 开发模板

## 标准结构

```
your-skill/
├── SKILL.md              # 技能定义（必需）
├── __init__.py           # 模块初始化
├── your_skill.py         # 主逻辑
├── scripts/
│   └── main.py          # 可执行脚本
├── references/
│   ├── api-guide.md     # API 文档
│   └── best-practices.md # 最佳实践
└── tests/
    └── test_skill.py    # 测试文件
```

## SKILL.md 模板

```yaml
---
name: your-skill-name
description: [做什么] + [何时使用] + [触发条件]
license: MIT
metadata:
  version: "1.0.0"
  category: [category]
  author: [author]
---

# Skill 名称

## 概述

简要描述技能功能。

## 使用方式

```python
from your_skill import YourSkill

skill = YourSkill()
result = skill.execute(param="value")
```

## 示例

### 示例 1：基本使用
[使用示例]

## 故障排除

[常见问题和解决方案]
```

## 开发检查清单

- [ ] SKILL.md 符合 Anthropic 标准
- [ ] name 使用 kebab-case
- [ ] description 包含触发条件
- [ ] 添加了 license
- [ ] 提供了使用示例
- [ ] 创建了 references/文档
- [ ] 编写了测试用例
''',
    },
}


def step1_enhance_descriptions():
    """第一步：细化 description 字段"""
    print("\n" + "="*60)
    print("步骤 1: 细化 Description 字段")
    print("="*60)
    
    all_descriptions = {
        **REAL_ESTATE_DESCRIPTIONS,
        **ECOMMERCE_DESCRIPTIONS,
        **MARKETING_DESCRIPTIONS,
        **CONTENT_DESCRIPTIONS,
        **DEV_DESCRIPTIONS,
        **TOOLS_DESCRIPTIONS,
    }
    
    updated_count = 0
    
    for skill_name, new_desc in all_descriptions.items():
        # 查找对应的 SKILL.md 文件
        for skill_file in SKILLS_DIR.rglob("SKILL.md"):
            # 检查文件夹名是否匹配
            if skill_file.parent.name.replace('_', '-') == skill_name or \
               skill_file.parent.name == skill_name:
                
                try:
                    content = skill_file.read_text(encoding='utf-8')
                    data = yaml.safe_load(content.split('---')[1])
                    
                    old_desc = data.get('description', '')
                    if old_desc != new_desc:
                        # 更新 description
                        content = content.replace(
                            f"description: {old_desc}",
                            f"description: {new_desc}"
                        )
                        skill_file.write_text(content, encoding='utf-8')
                        updated_count += 1
                        print(f"[OK] {skill_file.relative_to(SKILLS_DIR)}")
                        print(f"     旧：{old_desc[:50]}...")
                        print(f"     新：{new_desc[:50]}...")
                except Exception as e:
                    print(f"[ERR] {skill_file}: {e}")
    
    print(f"\n完成：更新了 {updated_count} 个技能的 description")
    return updated_count


def step2_add_usage_examples():
    """第二步：补充使用示例"""
    print("\n" + "="*60)
    print("步骤 2: 补充使用示例")
    print("="*60)
    
    updated_count = 0
    
    for skill_name, examples in USAGE_EXAMPLES.items():
        # 查找对应的 SKILL.md 文件
        for skill_file in SKILLS_DIR.rglob("SKILL.md"):
            if skill_file.parent.name.replace('_', '-') == skill_name or \
               skill_file.parent.name == skill_name:
                
                try:
                    content = skill_file.read_text(encoding='utf-8')
                    
                    # 检查是否已有"使用示例"部分
                    if '## 使用示例' not in content and '## 示例' not in content:
                        # 在文件末尾添加示例
                        content = content.rstrip() + '\n' + examples
                        skill_file.write_text(content, encoding='utf-8')
                        updated_count += 1
                        print(f"[OK] {skill_file.relative_to(SKILLS_DIR)}")
                except Exception as e:
                    print(f"[ERR] {skill_file}: {e}")
    
    print(f"\n完成：为 {updated_count} 个技能添加了使用示例")
    return updated_count


def step3_create_references():
    """第三步：创建 references/ 目录和文档"""
    print("\n" + "="*60)
    print("步骤 3: 创建 References 参考文档")
    print("="*60)
    
    created_count = 0
    
    for skill_name, docs in REFERENCES_TEMPLATES.items():
        # 查找对应的技能目录
        for skill_dir in SKILLS_DIR.rglob(skill_name.replace('-', '_')):
            if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
                
                # 创建 references/ 目录
                ref_dir = skill_dir / "references"
                ref_dir.mkdir(exist_ok=True)
                
                # 创建文档文件
                for doc_name, doc_content in docs.items():
                    doc_path = ref_dir / doc_name
                    if not doc_path.exists():
                        doc_path.write_text(doc_content, encoding='utf-8')
                        created_count += 1
                        print(f"[OK] 创建：{doc_path.relative_to(SKILLS_DIR)}")
    
    print(f"\n完成：创建了 {created_count} 个参考文档")
    return created_count


def main():
    """主函数 - 按步骤执行优化"""
    print("="*60)
    print("Leo Skills 增强优化")
    print(f"开始时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # 执行三步优化
    step1_count = step1_enhance_descriptions()
    step2_count = step2_add_usage_examples()
    step3_count = step3_create_references()
    
    # 总结
    print("\n" + "="*60)
    print("优化完成！")
    print("="*60)
    print(f"步骤 1 - 细化 Description: {step1_count} 个技能")
    print(f"步骤 2 - 补充使用示例：{step2_count} 个技能")
    print(f"步骤 3 - 创建参考文档：{step3_count} 个文件")
    print(f"\n总耗时：{(datetime.now() - datetime.now()).seconds} 秒")
    print("="*60)


if __name__ == '__main__':
    main()
