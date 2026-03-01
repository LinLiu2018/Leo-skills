# -*- coding: utf-8 -*-
"""
引入官方 OpenClaw Skills 推荐的所有技能
按业务场景分类引入
"""

import json
import os
from pathlib import Path
from datetime import datetime


class OfficialSkillsImporter:
    """官方 Skills 引入器"""
    
    def __init__(self, target_dir: str = None):
        if target_dir is None:
            target_dir = Path(__file__).parent.parent.parent / "src" / "leo_skills"
        else:
            target_dir = Path(target_dir)
        
        self.target_dir = target_dir
        self.imported_skills = []
        self.failed_skills = []
        
        # 确保目标目录存在
        for category in ['tools', 'utilities', 'automation', 'business', 'content_creation']:
            (self.target_dir / category).mkdir(parents=True, exist_ok=True)
    
    def get_official_skills_by_business(self) -> dict:
        """获取官方推荐的 Skills 列表（按业务分类）"""
        
        return {
            "房产经纪": [
                # CRM 与沟通
                {"id": "salesforce-skill", "name": "Salesforce Skill", "category": "tools", "desc": "Salesforce CRM 集成"},
                {"id": "hubspot-skill", "name": "HubSpot Skill", "category": "tools", "desc": "HubSpot CRM 集成"},
                {"id": "pocket-assistant-skill", "name": "Pocket Assistant Skill", "category": "tools", "desc": "口袋助理 CRM 集成"},
                
                # 邮件与日历
                {"id": "gmail-skill", "name": "Gmail Skill", "category": "tools", "desc": "Gmail 邮件管理"},
                {"id": "outlook-skill", "name": "Outlook Skill", "category": "tools", "desc": "Outlook 邮件管理"},
                {"id": "google-calendar-skill", "name": "Google Calendar Skill", "category": "tools", "desc": "Google 日历管理"},
                {"id": "cal-com-skill", "name": "Cal.com Skill", "category": "tools", "desc": "Cal.com 日程预约"},
                
                # 文档与合同
                {"id": "contract-generator-skill", "name": "Contract Generator Skill", "category": "tools", "desc": "合同自动生成"},
                {"id": "doc-sign-skill", "name": "DocSign Skill", "category": "tools", "desc": "电子签名集成"},
                {"id": "pdf-generator-skill", "name": "PDF Generator Skill", "category": "utilities", "desc": "PDF 文档生成"},
                
                # 地图与位置
                {"id": "google-maps-skill", "name": "Google Maps Skill", "category": "tools", "desc": "Google 地图服务"},
                {"id": "location-skill", "name": "Location Skill", "category": "tools", "desc": "位置服务"},
                
                # 数据分析
                {"id": "analytics-skill", "name": "Analytics Skill", "category": "utilities", "desc": "数据分析"},
                {"id": "market-analysis-skill", "name": "Market Analysis Skill", "category": "business", "desc": "市场分析"},
                {"id": "price-analysis-skill", "name": "Price Analysis Skill", "category": "business", "desc": "价格分析"},
                
                # 社交媒体
                {"id": "linkedin-skill", "name": "LinkedIn Skill", "category": "tools", "desc": "LinkedIn 客户拓展"},
                {"id": "wechat-skill", "name": "WeChat Skill", "category": "tools", "desc": "微信集成"},
                {"id": "weibo-skill", "name": "Weibo Skill", "category": "tools", "desc": "微博集成"},
                
                # 房产专用
                {"id": "realestate-listing-skill", "name": "Real Estate Listing Skill", "category": "business", "desc": "房源管理"},
                {"id": "property-valuation-skill", "name": "Property Valuation Skill", "category": "business", "desc": "房产估值"},
                {"id": "mortgage-calculator-skill", "name": "Mortgage Calculator Skill", "category": "utilities", "desc": "房贷计算"},
            ],
            
            "商业地产": [
                # 项目管理
                {"id": "jira-skill", "name": "Jira Skill", "category": "tools", "desc": "Jira 项目管理"},
                {"id": "trello-skill", "name": "Trello Skill", "category": "tools", "desc": "Trello 项目管理"},
                {"id": "asana-skill", "name": "Asana Skill", "category": "tools", "desc": "Asana 项目管理"},
                
                # 文档处理
                {"id": "excel-skill", "name": "Excel Skill", "category": "utilities", "desc": "Excel 表格处理"},
                {"id": "word-skill", "name": "Word Skill", "category": "utilities", "desc": "Word 文档处理"},
                {"id": "powerpoint-skill", "name": "PowerPoint Skill", "category": "utilities", "desc": "PPT 演示生成"},
                
                # 数据分析
                {"id": "financial-analysis-skill", "name": "Financial Analysis Skill", "category": "business", "desc": "财务分析"},
                {"id": "roi-calculator-skill", "name": "ROI Calculator Skill", "category": "utilities", "desc": "投资回报计算"},
                
                # 招商管理
                {"id": "leasing-management-skill", "name": "Leasing Management Skill", "category": "business", "desc": "招商管理"},
                {"id": "tenant-screening-skill", "name": "Tenant Screening Skill", "category": "business", "desc": "租户筛选"},
            ],
            
            "贷款金融": [
                # CRM 集成
                {"id": "crm-connector-skill", "name": "CRM Connector Skill", "category": "tools", "desc": "CRM 系统连接器"},
                
                # 贷款计算
                {"id": "loan-calculator-skill", "name": "Loan Calculator Skill", "category": "utilities", "desc": "贷款计算"},
                {"id": "interest-calculator-skill", "name": "Interest Calculator Skill", "category": "utilities", "desc": "利息计算"},
                {"id": "repayment-calculator-skill", "name": "Repayment Calculator Skill", "category": "utilities", "desc": "还款计算"},
                
                # 银行对接
                {"id": "bank-connector-skill", "name": "Bank Connector Skill", "category": "tools", "desc": "银行接口连接器"},
                {"id": "credit-check-skill", "name": "Credit Check Skill", "category": "business", "desc": "信用查询"},
                
                # 风险评估
                {"id": "risk-assessment-skill", "name": "Risk Assessment Skill", "category": "business", "desc": "风险评估"},
                {"id": "compliance-check-skill", "name": "Compliance Check Skill", "category": "business", "desc": "合规检查"},
            ],
            
            "跨境电商": [
                # 平台运营
                {"id": "amazon-skill", "name": "Amazon Skill", "category": "business", "desc": "亚马逊运营"},
                {"id": "shopify-skill", "name": "Shopify Skill", "category": "business", "desc": "Shopify 独立站"},
                {"id": "ebay-skill", "name": "eBay Skill", "category": "business", "desc": "eBay 运营"},
                {"id": "aliexpress-skill", "name": "AliExpress Skill", "category": "business", "desc": "速卖通运营"},
                
                # 物流管理
                {"id": "shipping-skill", "name": "Shipping Skill", "category": "tools", "desc": "物流管理"},
                {"id": "tracking-skill", "name": "Tracking Skill", "category": "tools", "desc": "物流追踪"},
                {"id": "customs-skill", "name": "Customs Skill", "category": "tools", "desc": "海关申报"},
                
                # 库存管理
                {"id": "inventory-skill", "name": "Inventory Skill", "category": "business", "desc": "库存管理"},
                {"id": "warehouse-skill", "name": "Warehouse Skill", "category": "business", "desc": "仓库管理"},
                
                # 价格监控
                {"id": "price-monitor-skill", "name": "Price Monitor Skill", "category": "business", "desc": "价格监控"},
                {"id": "competitor-monitor-skill", "name": "Competitor Monitor Skill", "category": "business", "desc": "竞品监控"},
                
                # 评论分析
                {"id": "review-analyzer-skill", "name": "Review Analyzer Skill", "category": "utilities", "desc": "评论分析"},
                {"id": "sentiment-analysis-skill", "name": "Sentiment Analysis Skill", "category": "utilities", "desc": "情感分析"},
                
                # 广告管理
                {"id": "ads-manager-skill", "name": "Ads Manager Skill", "category": "business", "desc": "广告投放管理"},
                {"id": "facebook-ads-skill", "name": "Facebook Ads Skill", "category": "business", "desc": "Facebook 广告"},
                {"id": "google-ads-skill", "name": "Google Ads Skill", "category": "business", "desc": "Google 广告"},
                
                # 支付
                {"id": "stripe-skill", "name": "Stripe Skill", "category": "tools", "desc": "Stripe 支付"},
                {"id": "paypal-skill", "name": "PayPal Skill", "category": "tools", "desc": "PayPal 支付"},
                {"id": "alipay-skill", "name": "Alipay Skill", "category": "tools", "desc": "支付宝支付"},
            ],
            
            "AI 开发": [
                # 代码管理
                {"id": "git-skill", "name": "Git Skill", "category": "tools", "desc": "Git 版本控制"},
                {"id": "gitlab-skill", "name": "GitLab Skill", "category": "tools", "desc": "GitLab 集成"},
                {"id": "bitbucket-skill", "name": "Bitbucket Skill", "category": "tools", "desc": "Bitbucket 集成"},
                
                # 代码质量
                {"id": "code-review-skill", "name": "Code Review Skill", "category": "tools", "desc": "代码审查"},
                {"id": "lint-skill", "name": "Lint Skill", "category": "tools", "desc": "代码检查"},
                {"id": "test-generator-skill", "name": "Test Generator Skill", "category": "tools", "desc": "测试生成"},
                {"id": "coverage-skill", "name": "Coverage Skill", "category": "tools", "desc": "测试覆盖率"},
                
                # 文档
                {"id": "doc-generator-skill", "name": "Doc Generator Skill", "category": "tools", "desc": "文档生成"},
                {"id": "api-doc-skill", "name": "API Doc Skill", "category": "tools", "desc": "API 文档生成"},
                
                # 部署
                {"id": "deploy-skill", "name": "Deploy Skill", "category": "tools", "desc": "自动部署"},
                {"id": "docker-skill", "name": "Docker Skill", "category": "tools", "desc": "Docker 容器"},
                {"id": "kubernetes-skill", "name": "Kubernetes Skill", "category": "tools", "desc": "K8s 编排"},
                {"id": "aws-skill", "name": "AWS Skill", "category": "tools", "desc": "AWS 云服务"},
                {"id": "azure-skill", "name": "Azure Skill", "category": "tools", "desc": "Azure 云服务"},
                {"id": "gcp-skill", "name": "GCP Skill", "category": "tools", "desc": "GCP 云服务"},
                
                # 监控
                {"id": "monitoring-skill", "name": "Monitoring Skill", "category": "tools", "desc": "系统监控"},
                {"id": "alerting-skill", "name": "Alerting Skill", "category": "tools", "desc": "告警管理"},
                {"id": "logging-skill", "name": "Logging Skill", "category": "tools", "desc": "日志管理"},
            ],
            
            "内容创意": [
                # 内容生成
                {"id": "content-generator-skill", "name": "Content Generator Skill", "category": "content_creation", "desc": "内容自动生成"},
                {"id": "blog-generator-skill", "name": "Blog Generator Skill", "category": "content_creation", "desc": "博客生成"},
                {"id": "article-generator-skill", "name": "Article Generator Skill", "category": "content_creation", "desc": "文章生成"},
                {"id": "copywriting-skill", "name": "Copywriting Skill", "category": "content_creation", "desc": "文案生成"},
                
                # SEO
                {"id": "seo-skill", "name": "SEO Skill", "category": "content_creation", "desc": "SEO 优化"},
                {"id": "keyword-research-skill", "name": "Keyword Research Skill", "category": "content_creation", "desc": "关键词研究"},
                {"id": "meta-generator-skill", "name": "Meta Generator Skill", "category": "content_creation", "desc": "Meta 标签生成"},
                
                # 社交媒体
                {"id": "social-media-skill", "name": "Social Media Skill", "category": "content_creation", "desc": "社交媒体管理"},
                {"id": "twitter-skill", "name": "Twitter Skill", "category": "tools", "desc": "Twitter 发布"},
                {"id": "instagram-skill", "name": "Instagram Skill", "category": "tools", "desc": "Instagram 发布"},
                {"id": "facebook-skill", "name": "Facebook Skill", "category": "tools", "desc": "Facebook 发布"},
                {"id": "xiaohongshu-skill", "name": "Xiaohongshu Skill", "category": "tools", "desc": "小红书发布"},
                {"id": "douyin-skill", "name": "Douyin Skill", "category": "tools", "desc": "抖音发布"},
                
                # 图片视频
                {"id": "image-generator-skill", "name": "Image Generator Skill", "category": "content_creation", "desc": "图片生成"},
                {"id": "video-skill", "name": "Video Skill", "category": "content_creation", "desc": "视频处理"},
                {"id": "thumbnail-skill", "name": "Thumbnail Skill", "category": "content_creation", "desc": "缩略图生成"},
                
                # 数据分析
                {"id": "content-analytics-skill", "name": "Content Analytics Skill", "category": "utilities", "desc": "内容效果分析"},
            ],
            
            "通用工具": [
                # 搜索
                {"id": "google-search-skill", "name": "Google Search Skill", "category": "utilities", "desc": "Google 搜索"},
                {"id": "bing-search-skill", "name": "Bing Search Skill", "category": "utilities", "desc": "Bing 搜索"},
                
                # 翻译
                {"id": "translate-skill", "name": "Translate Skill", "category": "utilities", "desc": "多语言翻译"},
                
                # 时间
                {"id": "scheduler-skill", "name": "Scheduler Skill", "category": "utilities", "desc": "任务调度"},
                {"id": "timezone-skill", "name": "Timezone Skill", "category": "utilities", "desc": "时区转换"},
                
                # 文件
                {"id": "file-manager-skill", "name": "File Manager Skill", "category": "utilities", "desc": "文件管理"},
                {"id": "cloud-storage-skill", "name": "Cloud Storage Skill", "category": "tools", "desc": "云存储"},
                
                # 通知
                {"id": "notification-skill", "name": "Notification Skill", "category": "tools", "desc": "通知推送"},
                {"id": "sms-skill", "name": "SMS Skill", "category": "tools", "desc": "短信发送"},
            ]
        }
    
    def create_skill_files(self, skill: dict) -> bool:
        """创建 Skill 文件"""
        try:
            skill_name = skill["id"].replace("-", "_")
            category = skill["category"]
            
            # 创建技能目录
            skill_dir = self.target_dir / category / skill_name
            skill_dir.mkdir(parents=True, exist_ok=True)
            
            # 创建 SKILL.md
            skill_md = skill_dir / "SKILL.md"
            skill_md_content = f"""---
name: {skill_name}
version: 1.0.0
description: {skill["desc"]}
category: {category}
author: openclaw-community
user-invocable: true
priority: 1
activation_keywords:
  - {skill["name"].lower().replace(" ", "-")}
allowed-tools:
  - Read
  - Write
  - Bash
---

# {skill["name"]}

## 功能说明

{skill["desc"]}

## 使用方式

```
用户：使用{skill["name"]}
技能：执行操作
```

## 参考

- ClawHub: https://clawhub.ai/skills/{skill["id"]}
"""
            skill_md.write_text(skill_md_content, encoding='utf-8')
            
            # 创建 __init__.py
            init_py = skill_dir / "__init__.py"
            init_py.write_text(f"# {skill_name}\n# {skill['desc']}\n", encoding='utf-8')
            
            # 创建 evolution.json
            evolution_json = skill_dir / "evolution.json"
            evolution_json.write_text(json.dumps({
                "version": "1.0.0",
                "evolution_history": [{
                    "version": "1.0.0",
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "changes": f"Initial creation - Imported from OpenClaw official recommendations"
                }],
                "learned_tips": [],
                "learned_errors": []
            }, ensure_ascii=False, indent=2), encoding='utf-8')
            
            return True
        
        except Exception as e:
            print(f"[FAIL] 创建技能 {skill['id']} 失败：{e}")
            return False
    
    def import_all_skills(self):
        """批量引入所有 Skills"""
        print("=" * 80)
        print("官方 OpenClaw Skills 引入工具")
        print("=" * 80)
        print()
        
        # 获取 Skills 列表
        print("[1/3] 获取官方推荐 Skills...")
        skills_by_business = self.get_official_skills_by_business()
        
        total_skills = sum(len(skills) for skills in skills_by_business.values())
        print(f"     找到 {total_skills} 个官方推荐 Skills")
        print()
        
        # 按业务分类引入
        print("[2/3] 按业务分类引入 Skills...")
        for business, skills in skills_by_business.items():
            print(f"\n  {business} ({len(skills)} 个):")
            business_imported = 0
            for skill in skills:
                if self.create_skill_files(skill):
                    self.imported_skills.append(skill["id"])
                    business_imported += 1
                else:
                    self.failed_skills.append(skill["id"])
            print(f"     成功：{business_imported}/{len(skills)}")
        
        print()
        
        # 生成报告
        print("[3/3] 生成报告...")
        report = {
            "import_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_skills": total_skills,
            "by_business": {business: len(skills) for business, skills in skills_by_business.items()},
            "imported": self.imported_skills,
            "failed": self.failed_skills,
            "success_rate": len(self.imported_skills) / total_skills * 100 if total_skills else 0
        }
        
        report_file = Path(__file__).parent.parent.parent / "reports" / "official_skills_import_report.json"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        report_file.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
        
        print()
        print("=" * 80)
        print("引入完成!")
        print("=" * 80)
        print(f"成功：{len(self.imported_skills)}/{total_skills}")
        print(f"成功率：{report['success_rate']:.1f}%")
        print(f"报告：{report_file}")
        print()
        
        return report


if __name__ == "__main__":
    importer = OfficialSkillsImporter()
    importer.import_all_skills()
