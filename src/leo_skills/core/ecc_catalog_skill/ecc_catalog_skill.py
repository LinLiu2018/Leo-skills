# -*- coding: utf-8 -*-
"""
ECC Catalog Skill
=================

ECC Skills目录浏览和导入
参考 everything-claude-code (156K stars)

Author: Leo AI System
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from base import BaseSkill, SkillResult


# ECC Skills 目录结构
ECC_CATALOG = {
    "core": {
        "name": "Core Skills",
        "description": "核心技能",
        "skills": [
            {"id": "coding-standards", "name": "Coding Standards", "desc": "代码规范"},
            {"id": "configure-ecc", "name": "Configure ECC", "desc": "ECC配置"},
            {"id": "continuous-learning-v1", "name": "Continuous Learning v1", "desc": "持续学习v1"},
            {"id": "continuous-learning-v2", "name": "Continuous Learning v2", "desc": "持续学习v2"},
            {"id": "strategic-compact", "name": "Strategic Compact", "desc": "战略契约"},
            {"id": "verification-loop", "name": "Verification Loop", "desc": "验证循环"},
        ]
    },
    "workflow": {
        "name": "Workflow",
        "description": "工作流",
        "skills": [
            {"id": "tdd-workflow", "name": "TDD Workflow", "desc": "测试驱动开发"},
            {"id": "eval-harness", "name": "Eval Harness", "desc": "评估工具"},
            {"id": "deployment-patterns", "name": "Deployment Patterns", "desc": "部署模式"},
            {"id": "database-migrations", "name": "Database Migrations", "desc": "数据库迁移"},
            {"id": "docker-patterns", "name": "Docker Patterns", "desc": "Docker模式"},
            {"id": "dmux-workflows", "name": "dmux Workflows", "desc": "dmux工作流"},
            {"id": "blueprint", "name": "Blueprint", "desc": "蓝图"},
            {"id": "content-hash-cache", "name": "Content Hash Cache", "desc": "内容哈希缓存"},
        ]
    },
    "security": {
        "name": "Security",
        "description": "安全扫描",
        "skills": [
            {"id": "security-review", "name": "Security Review", "desc": "安全审查"},
            {"id": "security-scan", "name": "Security Scan", "desc": "安全扫描"},
            {"id": "django-security", "name": "Django Security", "desc": "Django安全"},
            {"id": "spring-boot-security", "name": "Spring Boot Security", "desc": "Spring安全"},
        ]
    },
    "research": {
        "name": "Research",
        "description": "研究搜索",
        "skills": [
            {"id": "deep-research", "name": "Deep Research", "desc": "深度研究"},
            {"id": "market-research", "name": "Market Research", "desc": "市场研究"},
            {"id": "search-first", "name": "Search First", "desc": "搜索优先"},
            {"id": "iterative-retrieval", "name": "Iterative Retrieval", "desc": "迭代检索"},
            {"id": "exa-search", "name": "Exa Search", "desc": "Exa搜索"},
        ]
    },
    "frontend": {
        "name": "Frontend",
        "description": "前端开发",
        "skills": [
            {"id": "frontend-patterns", "name": "Frontend Patterns", "desc": "前端模式"},
            {"id": "frontend-slides", "name": "Frontend Slides", "desc": "前端幻灯片"},
            {"id": "liquid-glass-design", "name": "Liquid Glass Design", "desc": "玻璃拟态设计"},
            {"id": "swiftui-patterns", "name": "SwiftUI Patterns", "desc": "SwiftUI模式"},
        ]
    },
    "backend": {
        "name": "Backend",
        "description": "后端开发",
        "skills": [
            {"id": "backend-patterns", "name": "Backend Patterns", "desc": "后端模式"},
            {"id": "api-design", "name": "API Design", "desc": "API设计"},
            {"id": "postgres-patterns", "name": "Postgres Patterns", "desc": "Postgres模式"},
            {"id": "clickhouse", "name": "ClickHouse", "desc": "ClickHouse"},
        ]
    },
    "python": {
        "name": "Python",
        "description": "Python生态",
        "skills": [
            {"id": "python-patterns", "name": "Python Patterns", "desc": "Python模式"},
            {"id": "python-testing", "name": "Python Testing", "desc": "Python测试"},
            {"id": "django-patterns", "name": "Django Patterns", "desc": "Django模式"},
            {"id": "django-tdd", "name": "Django TDD", "desc": "Django TDD"},
        ]
    },
    "go": {
        "name": "Go",
        "description": "Go生态",
        "skills": [
            {"id": "go-patterns", "name": "Go Patterns", "desc": "Go模式"},
            {"id": "go-testing", "name": "Go Testing", "desc": "Go测试"},
        ]
    },
    "jvm": {
        "name": "JVM",
        "description": "Java/Kotlin生态",
        "skills": [
            {"id": "java-coding-standards", "name": "Java Coding Standards", "desc": "Java规范"},
            {"id": "jpa-patterns", "name": "JPA Patterns", "desc": "JPA模式"},
            {"id": "kotlin-patterns", "name": "Kotlin Patterns", "desc": "Kotlin模式"},
            {"id": "kotlin-testing", "name": "Kotlin Testing", "desc": "Kotlin测试"},
            {"id": "spring-boot-patterns", "name": "Spring Boot Patterns", "desc": "Spring模式"},
        ]
    },
    "industry": {
        "name": "Industry",
        "description": "行业解决方案",
        "skills": [
            {"id": "carrier-management", "name": "Carrier Management", "desc": "运营商管理"},
            {"id": "trade-compliance", "name": "Trade Compliance", "desc": "贸易合规"},
            {"id": "energy-procurement", "name": "Energy Procurement", "desc": "能源采购"},
            {"id": "logistics-exceptions", "name": "Logistics Exceptions", "desc": "物流异常"},
            {"id": "quality-nonconformance", "name": "Quality Nonconformance", "desc": "质量不合规"},
        ]
    },
    "content": {
        "name": "Content",
        "description": "内容创作",
        "skills": [
            {"id": "article-writing", "name": "Article Writing", "desc": "文章写作"},
            {"id": "content-engine", "name": "Content Engine", "desc": "内容引擎"},
            {"id": "investor-materials", "name": "Investor Materials", "desc": "投资者材料"},
            {"id": "x-api", "name": "X API", "desc": "X平台API"},
        ]
    }
}


class EccCatalogSkill(BaseSkill):
    """
    ECC Catalog Skill

    提供ECC Skills目录浏览和导入
    """

    @property
    def name(self) -> str:
        return "ecc_catalog"

    @property
    def description(self) -> str:
        return "ECC Skills目录浏览 - 156+ Skills参考"

    def execute(self, action: str = "default", **kwargs) -> SkillResult:
        """
        执行操作

        Actions:
            list: 列出所有分类
            category: 列出某分类的skills
            show: 显示skill详情
            search: 搜索skill
            recommend: 推荐适合的skill
        """
        if action == "list":
            return self._list_categories()
        elif action == "category":
            return self._list_category(kwargs.get("category", ""))
        elif action == "show":
            return self._show_skill(kwargs.get("skill_id", ""))
        elif action == "search":
            return self._search_skill(kwargs.get("query", ""))
        elif action == "recommend":
            return self._recommend_skill(kwargs.get("context", ""))
        else:
            return self._list_categories()

    def _list_categories(self) -> SkillResult:
        """列出所有分类"""
        categories = []
        total_skills = 0

        for cat_id, cat in ECC_CATALOG.items():
            count = len(cat["skills"])
            total_skills += count
            categories.append({
                "id": cat_id,
                "name": cat["name"],
                "description": cat["description"],
                "skill_count": count
            })

        return SkillResult.ok(
            data={"categories": categories, "total_skills": total_skills},
            message=f"共 {total_skills} Skills，{len(categories)} 个分类"
        )

    def _list_category(self, category: str) -> SkillResult:
        """列出某分类的skills"""
        if category not in ECC_CATALOG:
            return SkillResult.fail(f"未知分类: {category}")

        cat = ECC_CATALOG[category]
        return SkillResult.ok(
            data={
                "category": cat["name"],
                "description": cat["description"],
                "skills": cat["skills"]
            },
            message=f"{cat['name']} - {len(cat['skills'])} Skills"
        )

    def _show_skill(self, skill_id: str) -> SkillResult:
        """显示skill详情"""
        for cat in ECC_CATALOG.values():
            for skill in cat["skills"]:
                if skill["id"] == skill_id:
                    return SkillResult.ok(
                        data={
                            "skill": skill,
                            "import_command": f"/skill import {skill_id}",
                            "ecc_repo": "https://github.com/affaan-m/everything-claude-code"
                        },
                        message=f"显示 {skill['name']}"
                    )

        return SkillResult.fail(f"未找到 Skill: {skill_id}")

    def _search_skill(self, query: str) -> SkillResult:
        """搜索skill"""
        if not query:
            return SkillResult.fail("请提供搜索关键词")

        query_lower = query.lower()
        results = []

        for cat_id, cat in ECC_CATALOG.items():
            for skill in cat["skills"]:
                if (query_lower in skill["name"].lower() or
                    query_lower in skill["desc"].lower() or
                    query_lower in skill["id"].lower()):
                    results.append({
                        "id": skill["id"],
                        "name": skill["name"],
                        "desc": skill["desc"],
                        "category": cat["name"]
                    })

        return SkillResult.ok(
            data={"results": results, "query": query, "count": len(results)},
            message=f"搜索 '{query}' 找到 {len(results)} 个结果"
        )

    def _recommend_skill(self, context: str) -> SkillResult:
        """基于上下文推荐skill"""
        if not context:
            context = ""

        context_lower = context.lower()
        recommendations = []

        # 简单关键词匹配
        keywords_map = {
            "python": ["python-patterns", "python-testing", "django-patterns"],
            "web": ["frontend-patterns", "api-design"],
            "测试": ["tdd-workflow", "python-testing", "go-testing"],
            "安全": ["security-scan", "security-review", "django-security"],
            "数据库": ["database-migrations", "postgres-patterns"],
            "前端": ["frontend-patterns", "frontend-slides"],
            "后端": ["backend-patterns", "api-design"],
            "java": ["java-coding-standards", "spring-boot-patterns"],
            "kotlin": ["kotlin-patterns", "kotlin-testing"],
            "go": ["go-patterns", "go-testing"],
            "部署": ["deployment-patterns", "docker-patterns"],
            "研究": ["deep-research", "market-research", "search-first"],
            "内容": ["article-writing", "content-engine"],
        }

        for keyword, skill_ids in keywords_map.items():
            if keyword in context_lower:
                for skill_id in skill_ids:
                    for cat in ECC_CATALOG.values():
                        for skill in cat["skills"]:
                            if skill["id"] == skill_id and skill not in recommendations:
                                recommendations.append(skill)

        return SkillResult.ok(
            data={
                "context": context,
                "recommendations": recommendations[:5]
            },
            message=f"基于 '{context}' 推荐 {len(recommendations)} 个Skills"
        )

    def get_actions(self) -> List[str]:
        return ["default", "list", "category", "show", "search", "recommend"]


# 快捷函数
def list_ecc_categories() -> List[Dict]:
    """列出所有分类"""
    skill = EccCatalogSkill()
    result = skill.execute(action="list")
    return result.data.get("categories", []) if result.success else []


def recommend_skill(context: str) -> List[Dict]:
    """推荐适合的skill"""
    skill = EccCatalogSkill()
    result = skill.execute(action="recommend", context=context)
    return result.data.get("recommendations", []) if result.success else []


if __name__ == "__main__":
    skill = EccCatalogSkill()
    print(skill.execute("list"))
