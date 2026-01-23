"""
Skill适配器
============
将Claude Skills适配为Subagent可调用的接口
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass


@dataclass
class SkillMetadata:
    """Skill元数据"""
    name: str
    path: str
    description: str = ""
    version: str = "1.0.0"
    author: str = ""
    category: str = ""
    actions: List[str] = None
    enabled: bool = True

    def __post_init__(self):
        if self.actions is None:
            self.actions = []


class SkillAdapter:
    """
    Skill适配器
    ===========
    负责将Claude Skill目录适配为可调用的接口
    """

    def __init__(self, skill_path: str, skill_name: str):
        """
        初始化适配器

        Args:
            skill_path: Skill目录路径
            skill_name: Skill名称
        """
        self.skill_path = Path(skill_path)
        self.skill_name = skill_name
        self.metadata: Optional[SkillMetadata] = None
        self.config: Dict[str, Any] = {}

        # 加载Skill配置
        self._load_skill_config()

    def _load_skill_config(self):
        """加载Skill配置文件"""
        # 查找SKILL.md
        skill_md = self.skill_path / "SKILL.md"
        if skill_md.exists():
            self._parse_skill_md(skill_md)

        # 查找skill_config.json
        config_file = self.skill_path / "skill_config.json"
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)

        # 如果没有元数据，创建默认的
        if not self.metadata:
            self.metadata = SkillMetadata(
                name=self.skill_name,
                path=str(self.skill_path),
                description=f"{self.skill_name}技能",
                actions=self._discover_actions()
            )

    def _parse_skill_md(self, skill_md_path: Path):
        """解析SKILL.md文件"""
        with open(skill_md_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 简单解析（实际可以更复杂）
        description = ""
        for line in content.split('\n'):
            if line.startswith('# Description:'):
                description = line.replace('# Description:', '').strip()
            elif line.startswith('# 描述:'):
                description = line.replace('# 描述:', '').strip()
            elif line.startswith('# Version:'):
                version = line.replace('# Version:', '').strip()
            elif line.startswith('# Author:'):
                author = line.replace('# Author:', '').strip()

        self.metadata = SkillMetadata(
            name=self.skill_name,
            path=str(self.skill_path),
            description=description or f"{self.skill_name}技能",
            actions=self._discover_actions()
        )

    def _discover_actions(self) -> List[str]:
        """
        自动发现Skill支持的操作

        通过分析skill.md中的指令来推断支持的操作
        """
        actions = []
        skill_md = self.skill_path / "skill.md"

        if skill_md.exists():
            with open(skill_md, 'r', encoding='utf-8') as f:
                content = f.read()

            # 查找指令定义
            if '<command_name>' in content:
                # 提取命令名称
                import re
                commands = re.findall(r'<command_name>([^<]+)</command_name>', content)
                actions = [cmd.strip() for cmd in commands]

        # 如果没找到，返回默认操作
        if not actions:
            actions = ["execute"]

        return actions

    def get_available_actions(self) -> List[str]:
        """获取可用的操作列表"""
        return self.metadata.actions if self.metadata else []

    def get_action_prompt(self, action: str) -> str:
        """
        获取执行某个操作的提示词

        Args:
            action: 操作名称

        Returns:
            操作的提示词模板
        """
        # 这里可以读取skill.md并返回相应的指令模板
        # 简化实现，返回基本信息
        if self.metadata:
            return f"""
请使用{self.metadata.name}执行'{action}'操作。

Skill路径: {self.metadata.path}
描述: {self.metadata.description}
"""
        return f"请执行{action}操作"

    def validate_action(self, action: str) -> bool:
        """
        验证操作是否有效

        Args:
            action: 操作名称

        Returns:
            是否有效
        """
        available = self.get_available_actions()
        return action in available or "execute" in available

    def get_skill_info(self) -> Dict[str, Any]:
        """
        获取Skill信息

        Returns:
            包含Skill详细信息的字典
        """
        return {
            "name": self.skill_name,
            "path": str(self.skill_path),
            "metadata": {
                "description": self.metadata.description if self.metadata else "",
                "version": self.metadata.version if self.metadata else "1.0.0",
                "category": self.metadata.category if self.metadata else "",
                "actions": self.get_available_actions(),
                "enabled": self.metadata.enabled if self.metadata else True
            },
            "config": self.config
        }

    def __repr__(self):
        return f"SkillAdapter({self.skill_name})"


# ==================== 全局适配器缓存 ====================

_adapters: Dict[str, SkillAdapter] = {}


def get_skill_adapter(skill_name: str, skill_path: str = None) -> SkillAdapter:
    """
    获取Skill适配器（带缓存）

    Args:
        skill_name: Skill名称
        skill_path: Skill路径（可选，首次创建时需要）

    Returns:
        Skill适配器实例
    """
    if skill_name not in _adapters:
        if not skill_path:
            raise ValueError(f"Skill '{skill_name}' 未缓存，需要提供path参数")
        _adapters[skill_name] = SkillAdapter(skill_path, skill_name)

    return _adapters[skill_name]


def clear_adapter_cache():
    """清空适配器缓存"""
    global _adapters
    _adapters = {}


# ==================== 使用示例 ====================

if __name__ == "__main__":
    # 示例：创建适配器
    adapter = SkillAdapter(
        skill_path="leo-skills/content-creation/content-layout-leo-cskill",
        skill_name="content-layout-leo-cskill"
    )

    # 获取信息
    info = adapter.get_skill_info()
    print(f"Skill信息: {json.dumps(info, indent=2, ensure_ascii=False)}")

    # 获取可用操作
    actions = adapter.get_available_actions()
    print(f"可用操作: {actions}")

    # 获取操作提示
    if actions:
        prompt = adapter.get_action_prompt(actions[0])
        print(f"操作提示: {prompt}")
