"""
链接工具类
处理 Obsidian 双向链接和关联
"""

from typing import List, Dict, Set
import re


class LinkUtils:
    """链接工具类"""

    @staticmethod
    def extract_links(content: str) -> List[str]:
        """
        从内容中提取所有 wikilinks

        Args:
            content: Markdown 内容

        Returns:
            链接列表
        """
        pattern = r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]'
        matches = re.findall(pattern, content)
        return matches

    @staticmethod
    def create_bidirectional_link(source: str, target: str) -> str:
        """
        创建双向链接

        Args:
            source: 源笔记名称
            target: 目标笔记名称

        Returns:
            链接字符串
        """
        return f"[[{target}]] ← [[{source}]]"

    @staticmethod
    def find_related_techs(tech_name: str, all_techs: List[str]) -> List[str]:
        """
        查找相关技术（基于名称相似度）

        Args:
            tech_name: 技术名称
            all_techs: 所有技术列表

        Returns:
            相关技术列表
        """
        related = []
        tech_lower = tech_name.lower()

        for tech in all_techs:
            if tech == tech_name:
                continue

            tech_l = tech.lower()

            # 简单的相关性判断
            if (tech_lower in tech_l or tech_l in tech_lower or
                any(word in tech_l for word in tech_lower.split() if len(word) > 3)):
                related.append(tech)

        return related[:5]  # 最多返回 5 个

    @staticmethod
    def create_tech_links(technologies: List[Dict]) -> str:
        """
        为技术列表创建链接

        Args:
            technologies: 技术列表

        Returns:
            链接字符串
        """
        if not technologies:
            return ""

        links = []
        for tech in technologies:
            name = tech.get('name', '')
            if name:
                links.append(f"[[{name}]]")

        return ", ".join(links)
