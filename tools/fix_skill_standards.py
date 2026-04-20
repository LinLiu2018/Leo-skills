#!/usr/bin/env python3
"""
Leo Skills 标准化脚本 - 按照 Anthropic 官方 Skill 标准修复所有 SKILL.md 文件

Anthropic 官方标准要求：
1. YAML 前置元数据必须有 --- 分隔符
2. name 字段：短横线命名法 (kebab-case)，无空格，无大写
3. description 字段：必须包含 WHAT(做什么) + WHEN(何时使用/触发条件)
4. 可选字段：license, compatibility, metadata
5. 禁止：XML 尖括号 < >，名称中包含 claude/anthropic
"""

import os
import re
import yaml
from pathlib import Path
from typing import Dict, List, Tuple, Optional

SKILLS_DIR = Path(r"E:\桌面\leo_ai_system\src\leo_skills")

# 描述字段增强映射（根据技能名称/类别自动补充触发条件）
DESCRIPTION_ENHANCEMENTS = {
    'ads_manager': '广告投放管理和优化。当用户需要创建广告计划、调整出价、分析广告效果或优化 ROI 时使用。',
    'aliexpress': '速卖通电商运营技能。当用户需要管理速卖通店铺、处理订单、优化 listing 或分析销售数据时使用。',
    'amazon': '亚马逊电商运营技能。当用户需要管理亚马逊店铺、FBA 发货、PPC 广告或产品调研时使用。',
    'competitor_monitor': '竞品监控分析技能。当用户需要监控竞争对手动态、价格变化、新品上架或营销策略时使用。',
    'competitor_content_crawler': '竞品内容爬取技能。当用户需要抓取竞品网站内容、社交媒体帖子或营销素材时使用。',
    'compliance_check': '合规检查技能。当用户需要检查业务合规性、审核合同条款或验证资质文件时使用。',
    'credit_check': '信用核查技能。当用户需要查询客户信用记录、评估信用风险或生成信用报告时使用。',
    'customer_portrait': '客户画像分析技能。当用户需要分析客户特征、行为模式或生成分群报告时使用。',
    'ebay': 'eBay 电商运营技能。当用户需要管理 eBay 店铺、处理订单或优化 listing 时使用。',
    'facebook_ads': 'Facebook 广告投放技能。当用户需要创建 FB 广告、管理广告组或分析广告数据时使用。',
    'financial_analysis': '财务分析技能。当用户需要分析财务报表、计算关键指标或生成财务洞察时使用。',
    'google_ads': 'Google 广告投放技能。当用户需要创建 Google 广告、管理关键词或优化 SEM 效果时使用。',
    'inventory': '库存管理技能。当用户需要跟踪库存水平、预测补货需求或处理库存预警时使用。',
    'leasing_management': '租赁管理技能。当用户需要管理租赁合同、跟踪租期或处理租户事务时使用。',
    'market_analysis': '市场分析技能。当用户需要分析市场趋势、竞争格局或行业数据时使用。',
    'pocket_crm': '口袋助理 CRM 集成技能。当用户需要同步客户数据、分析通话录音或生成跟进策略时使用。',
    'price_analysis': '价格分析技能。当用户需要分析定价策略、比价或优化价格体系时使用。',
    'price_monitor': '价格监控技能。当用户需要监控价格变化、追踪竞品定价或接收价格预警时使用。',
    'property_valuation': '房产估值技能。当用户需要评估房产价值、分析市场成交价或生成估值报告时使用。',
    'realestate_listing': '房产房源管理技能。当用户需要发布房源、管理房源信息或优化房源展示时使用。',
    'risk_assessment': '风险评估技能。当用户需要评估业务风险、生成风险报告或制定风控策略时使用。',
    'sales_sop': '销售 SOP 执行技能。当用户需要执行销售流程、跟进销售线索或管理销售管道时使用。',
    'shopify': 'Shopify 电商运营技能。当用户需要管理 Shopify 店铺、处理订单或优化转化率时使用。',
    'tenant_screening': '租户筛选技能。当用户需要筛选租户、验证资质或生成租户评估报告时使用。',
    'video_monitor': '视频内容监控技能。当用户需要监控视频平台、分析视频数据或追踪热门内容时使用。',
    'warehouse': '仓储管理技能。当用户需要管理仓库库存、处理出入库或优化仓储布局时使用。',
    'auto_logger': '自动日志记录技能。当系统需要自动记录运行日志、追踪执行历史或生成日志报告时使用。',
    'email_automation': '邮件自动化技能。当用户需要批量发送邮件、设置邮件模板或自动化邮件营销时使用。',
    'zapier_webhook': 'Zapier Webhook 集成技能。当用户需要配置 Zapier 自动化、设置 webhook 触发或集成第三方服务时使用。',
    'api_doc_generator': 'API 文档生成技能。当用户需要为代码生成 API 文档、创建接口说明或更新文档时使用。',
    'database_model_generator': '数据库模型生成技能。当用户需要创建数据库模型、生成 ORM 代码或设计表结构时使用。',
    'fastapi_endpoint_generator': 'FastAPI 端点生成技能。当用户需要创建 FastAPI 接口、生成路由代码或设计 API 结构时使用。',
    'flask_auth_generator': 'Flask 认证生成技能。当用户需要为 Flask 应用添加认证、生成登录模块或实现权限控制时使用。',
}

# 类别映射
CATEGORY_DESCRIPTIONS = {
    'automation': '自动化任务执行',
    'backend': '后端开发支持',
    'business': '业务运营支持',
    'collaboration': '协作与沟通',
    'content_creation': '内容创作生成',
    'core': '核心功能',
    'debugging': '调试与排错',
    'development': '开发辅助',
    'devops': '运维与部署',
    'evolution': '技能进化学习',
    'frontend': '前端开发支持',
    'intelligence': '智能分析',
    'prompt_engineering': '提示词工程',
    'scaffold': '项目脚手架',
    'security': '安全与防护',
    'testing': '测试与验证',
    'tools': '工具集成',
    'utilities': '实用工具',
}


def extract_yaml_frontmatter(content: str) -> Tuple[Optional[Dict], str]:
    """提取 YAML 前置元数据和正文内容"""
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)', content, re.DOTALL)
    if match:
        try:
            frontmatter = yaml.safe_load(match.group(1))
            body = match.group(2).strip()
            return frontmatter, body
        except yaml.YAMLError:
            return None, content
    return None, content


def normalize_name(name: str) -> str:
    """将名称转换为短横线命名法"""
    # 替换空格和下划线为短横线
    name = re.sub(r'[\s_]+', '-', name)
    # 转换为小写
    name = name.lower()
    # 移除连续短横线
    name = re.sub(r'-+', '-', name)
    # 移除首尾短横线
    name = name.strip('-')
    return name


def enhance_description(name: str, current_desc: str, category: str) -> str:
    """增强描述字段，确保包含 WHAT + WHEN"""
    # 如果已有触发条件关键词，保留原描述
    trigger_keywords = ['当', '时', '用于', '触发', '需要', '时候']
    if any(kw in current_desc for kw in trigger_keywords):
        return current_desc
    
    # 尝试从映射中获取增强描述
    name_key = name.lower().replace('-skill', '').replace('_', '-')
    for key, enhanced in DESCRIPTION_ENHANCEMENTS.items():
        if key in name_key or name_key in key:
            return enhanced
    
    # 尝试从类别生成通用描述
    if category in CATEGORY_DESCRIPTIONS:
        return f"{current_desc}。当用户需要{CATEGORY_DESCRIPTIONS[category]}相关帮助时使用。"
    
    # 默认增强
    return f"{current_desc}。当用户提及相关任务或明确请求使用此技能时使用。"


def fix_skill_file(file_path: Path) -> Dict:
    """修复单个 SKILL.md 文件"""
    result = {
        'path': str(file_path),
        'status': 'unchanged',
        'changes': []
    }
    
    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception as e:
        result['status'] = 'error'
        result['error'] = str(e)
        return result
    
    # 提取 YAML 前置元数据
    frontmatter, body = extract_yaml_frontmatter(content)
    
    if frontmatter is None:
        # 没有有效的前置元数据，需要创建
        result['status'] = 'created_frontmatter'
        result['changes'].append('Added YAML frontmatter')
        
        # 从文件名推断技能名称
        skill_name = file_path.parent.name.replace('_', '-').lower()
        frontmatter = {
            'name': skill_name,
            'description': f'{skill_name.replace("-", " ").title()} 技能。当用户需要相关帮助时使用。'
        }
    
    changes_made = []
    
    # 修复 name 字段
    if 'name' not in frontmatter:
        skill_name = file_path.parent.name.replace('_', '-').lower()
        frontmatter['name'] = skill_name
        changes_made.append(f"Added name: {skill_name}")
    else:
        original_name = frontmatter['name']
        normalized_name = normalize_name(original_name)
        if original_name != normalized_name:
            frontmatter['name'] = normalized_name
            changes_made.append(f"Normalized name: {original_name} -> {normalized_name}")
    
    # 修复 description 字段
    if 'description' not in frontmatter:
        frontmatter['description'] = f"{file_path.parent.name} 技能。当用户需要相关功能时使用。"
        changes_made.append("Added description")
    else:
        original_desc = frontmatter['description']
        category = frontmatter.get('category', file_path.parent.parent.name)
        enhanced_desc = enhance_description(frontmatter['name'], original_desc, category)
        if enhanced_desc != original_desc:
            frontmatter['description'] = enhanced_desc
            changes_made.append("Enhanced description with trigger conditions")
    
    # 清理非标准字段（保留但标记）
    non_standard_fields = ['version', 'user-invocable', 'priority', 'activation_keywords', 'allowed-tools']
    for field in non_standard_fields:
        if field in frontmatter:
            # 移到 metadata 中
            if 'metadata' not in frontmatter:
                frontmatter['metadata'] = {}
            frontmatter['metadata'][field] = frontmatter.pop(field)
            changes_made.append(f"Moved {field} to metadata")
    
    # 检查是否有需要移除的内容
    if 'license' not in frontmatter:
        frontmatter['license'] = 'MIT'
        changes_made.append("Added license: MIT")
    
    if changes_made:
        result['status'] = 'updated'
        result['changes'] = changes_made
        
        # 重新构建文件内容
        new_frontmatter = yaml.dump(frontmatter, allow_unicode=True, default_flow_style=False, sort_keys=False)
        new_content = f"---\n{new_frontmatter}---\n\n{body}"
        
        # 写入文件
        file_path.write_text(new_content, encoding='utf-8')
    
    return result


def main():
    """主函数"""
    print("=" * 60)
    print("Leo Skills 标准化修复工具")
    print("按照 Anthropic 官方 Skill 标准修复所有 SKILL.md 文件")
    print("=" * 60)
    print()
    
    # 查找所有 SKILL.md 文件
    skill_files = list(SKILLS_DIR.rglob("SKILL.md"))
    print(f"找到 {len(skill_files)} 个 SKILL.md 文件")
    print()
    
    # 统计结果
    stats = {
        'unchanged': 0,
        'updated': 0,
        'created_frontmatter': 0,
        'error': 0
    }
    
    # 处理每个文件
    for i, file_path in enumerate(skill_files, 1):
        result = fix_skill_file(file_path)
        stats[result['status']] += 1
        
        if result['status'] != 'unchanged':
            print(f"[{i}/{len(skill_files)}] {result['status'].upper()}: {file_path.relative_to(SKILLS_DIR)}")
            for change in result.get('changes', []):
                print(f"    - {change}")
    
    print()
    print("=" * 60)
    print("修复完成!")
    print("=" * 60)
    print(f"总计：{len(skill_files)} 个文件")
    print(f"  - 已更新：{stats['updated']}")
    print(f"  - 创建前置元数据：{stats['created_frontmatter']}")
    print(f"  - 无变更：{stats['unchanged']}")
    print(f"  - 错误：{stats['error']}")


if __name__ == '__main__':
    main()
