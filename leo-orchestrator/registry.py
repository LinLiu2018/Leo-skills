"""
Leo统一注册表
===================
全局Skills和Subagents注册系统

提供统一的注册、发现和调用接口
"""

import os
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class SkillRegistration:
    """Skill注册信息"""
    name: str
    path: str
    category: str
    enabled: bool = True
    metadata: dict = field(default_factory=dict)
    registered_at: datetime = field(default_factory=datetime.now)

    def __repr__(self):
        status = "🟢" if self.enabled else "⚫"
        return f"{status} {self.name} ({self.category})"


@dataclass
class AgentRegistration:
    """Subagent注册信息"""
    name: str
    type: str
    priority: int
    skills: List[str] = field(default_factory=list)
    enabled: bool = True
    metadata: dict = field(default_factory=dict)
    registered_at: datetime = field(default_factory=datetime.now)

    def __repr__(self):
        status = "🟢" if self.enabled else "⚫"
        return f"{status} {self.name} ({self.type}) - Priority: {self.priority}"


class UnifiedRegistry:
    """
    统一注册表
    ============
    管理所有Skills和Subagents的注册、发现和调用
    """

    def __init__(self, config_path: Optional[str] = None):
        self.skills: Dict[str, SkillRegistration] = {}
        self.agents: Dict[str, AgentRegistration] = {}
        self.workflows: Dict[str, dict] = {}

        if config_path:
            self.load_from_config(config_path)
        else:
            # 默认配置路径
            base_path = Path(__file__).parent.parent
            self.load_from_config(base_path / "leo-config" / "settings" / "config.yaml")

    # ==================== Skills注册 ====================

    def register_skill(self,
                       name: str,
                       path: str,
                       category: str,
                       enabled: bool = True,
                       **metadata) -> bool:
        """
        注册一个Skill

        用法:
            registry.register_skill(
                name="content-layout-leo-cskill",
                path="leo-skills/content-creation/content-layout-leo-cskill",
                category="content-creation"
            )
        """
        if name in self.skills:
            print(f"⚠️  Skill '{name}' 已存在，跳过注册")
            return False

        registration = SkillRegistration(
            name=name,
            path=path,
            category=category,
            enabled=enabled,
            metadata=metadata
        )
        self.skills[name] = registration
        print(f"✅ 注册Skill: {registration}")
        return True

    def unregister_skill(self, name: str) -> bool:
        """注销一个Skill"""
        if name in self.skills:
            del self.skills[name]
            print(f"❌ 注销Skill: {name}")
            return True
        return False

    def get_skill(self, name: str) -> Optional[SkillRegistration]:
        """获取Skill注册信息"""
        return self.skills.get(name)

    def list_skills(self, category: Optional[str] = None) -> List[SkillRegistration]:
        """列出所有Skills（可按分类筛选）"""
        skills = list(self.skills.values())
        if category:
            skills = [s for s in skills if s.category == category]
        return sorted(skills, key=lambda x: x.name)

    def enable_skill(self, name: str) -> bool:
        """启用Skill"""
        if name in self.skills:
            self.skills[name].enabled = True
            return True
        return False

    def disable_skill(self, name: str) -> bool:
        """禁用Skill"""
        if name in self.skills:
            self.skills[name].enabled = False
            return True
        return False

    # ==================== Subagents注册 ====================

    def register_agent(self,
                       name: str,
                       type: str,
                       priority: int = 10,
                       skills: List[str] = None,
                       enabled: bool = True,
                       **metadata) -> bool:
        """
        注册一个Subagent

        用法:
            registry.register_agent(
                name="task-agent",
                type="executor",
                priority=1,
                skills=["content-layout-leo-cskill", "realestate-news-publisher-cskill"]
            )
        """
        if name in self.agents:
            print(f"⚠️  Agent '{name}' 已存在，跳过注册")
            return False

        registration = AgentRegistration(
            name=name,
            type=type,
            priority=priority,
            skills=skills or [],
            enabled=enabled,
            metadata=metadata
        )
        self.agents[name] = registration
        print(f"✅ 注册Agent: {registration}")
        return True

    def unregister_agent(self, name: str) -> bool:
        """注销一个Agent"""
        if name in self.agents:
            del self.agents[name]
            print(f"❌ 注销Agent: {name}")
            return True
        return False

    def get_agent(self, name: str) -> Optional[AgentRegistration]:
        """获取Agent注册信息"""
        return self.agents.get(name)

    def list_agents(self, type: Optional[str] = None) -> List[AgentRegistration]:
        """列出所有Agents（可按类型筛选）"""
        agents = list(self.agents.values())
        if type:
            agents = [a for a in agents if a.type == type]
        return sorted(agents, key=lambda x: x.priority)

    # ==================== Workflows注册 ====================

    def register_workflow(self, name: str, workflow: dict) -> bool:
        """注册一个Workflow"""
        if name in self.workflows:
            print(f"⚠️  Workflow '{name}' 已存在，跳过注册")
            return False

        self.workflows[name] = workflow
        print(f"✅ 注册Workflow: {name}")
        return True

    def get_workflow(self, name: str) -> Optional[dict]:
        """获取Workflow定义"""
        return self.workflows.get(name)

    def list_workflows(self) -> List[str]:
        """列出所有Workflow名称"""
        return list(self.workflows.keys())

    # ==================== 批量操作 ====================

    def auto_discover_skills(self, base_path: str = "leo-skills") -> int:
        """
        自动发现并注册所有Skills

        扫描leo-skills目录，自动注册所有*-cskill目录
        """
        base = Path(base_path)
        discovered = 0

        # 扫描所有分类目录
        for category_dir in base.iterdir():
            if not category_dir.is_dir() or category_dir.name.startswith('.'):
                continue

            category = category_dir.name

            # 扫描该分类下的所有Skills
            for skill_dir in category_dir.iterdir():
                if skill_dir.is_dir() and skill_dir.name.endswith('-cskill'):
                    skill_name = skill_dir.name

                    # 检查是否已注册
                    if skill_name not in self.skills:
                        self.register_skill(
                            name=skill_name,
                            path=str(skill_dir.relative_to(base.parent)),
                            category=category
                        )
                        discovered += 1

        print(f"🔍 自动发现并注册了 {discovered} 个Skills")
        return discovered

    # ==================== 配置加载 ====================

    def load_from_config(self, config_path: str):
        """从配置文件加载注册信息"""
        config_file = Path(config_path)

        if not config_file.exists():
            print(f"⚠️  配置文件不存在: {config_path}")
            return

        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        # 加载Skills配置
        if 'skills' in config:
            for skill_config in config['skills']:
                self.register_skill(**skill_config)

        # 加载Agents配置
        if 'agents' in config:
            for agent_config in config['agents']:
                self.register_agent(**agent_config)

        # 加载Workflows配置
        if 'workflows' in config:
            for workflow_name, workflow_config in config['workflows'].items():
                self.register_workflow(workflow_name, workflow_config)

    # ==================== 统计信息 ====================

    def print_stats(self):
        """打印注册统计信息"""
        print("\n" + "="*60)
        print("📊 Leo统一注册表统计")
        print("="*60)

        # Skills统计
        enabled_skills = [s for s in self.skills.values() if s.enabled]
        print(f"\n🎯 Skills: {len(enabled_skills)}/{len(self.skills)} 已启用")

        by_category = {}
        for skill in self.skills.values():
            if skill.category not in by_category:
                by_category[skill.category] = []
            by_category[skill.category].append(skill)

        for category, skills in sorted(by_category.items()):
            print(f"\n  📁 {category}:")
            for skill in skills:
                print(f"     {skill}")

        # Agents统计
        enabled_agents = [a for a in self.agents.values() if a.enabled]
        print(f"\n🤖 Agents: {len(enabled_agents)}/{len(self.agents)} 已启用")

        for agent in sorted(self.agents.values(), key=lambda x: x.priority):
            print(f"     {agent}")

        # Workflows统计
        print(f"\n🔄 Workflows: {len(self.workflows)} 个")
        for workflow in self.workflows:
            print(f"     • {workflow}")

        print("\n" + "="*60 + "\n")


# ==================== 全局单例 ====================

_global_registry: Optional[UnifiedRegistry] = None


def get_registry() -> UnifiedRegistry:
    """获取全局注册表单例"""
    global _global_registry
    if _global_registry is None:
        _global_registry = UnifiedRegistry()
    return _global_registry


# ==================== 便捷装饰器 ====================

def register_skill(**kwargs):
    """
    Skill注册装饰器

    用法:
        @register_skill(
            name="my-skill",
            category="content-creation"
        )
        class MySkill:
            pass
    """
    def decorator(cls):
        registry = get_registry()
        registry.register_skill(**kwargs)
        cls._registry = registry
        return cls
    return decorator


def register_agent(**kwargs):
    """
    Agent注册装饰器

    用法:
        @register_agent(
            name="my-agent",
            type="executor",
            priority=5
        )
        class MyAgent:
            pass
    """
    def decorator(cls):
        registry = get_registry()
        registry.register_agent(**kwargs)
        cls._registry = registry
        return cls
    return decorator


# ==================== 使用示例 ====================

if __name__ == "__main__":
    # 创建注册表
    registry = UnifiedRegistry()

    # 方式1：手动注册Skills
    registry.register_skill(
        name="content-layout-leo-cskill",
        path="leo-skills/content-creation/content-layout-leo-cskill",
        category="content-creation"
    )

    # 方式2：自动发现Skills
    registry.auto_discover_skills("leo-skills")

    # 注册Agents
    registry.register_agent(
        name="task-agent",
        type="executor",
        priority=1,
        skills=["content-layout-leo-cskill", "realestate-news-publisher-cskill"]
    )

    # 打印统计
    registry.print_stats()

    # 查询
    print("\n🔍 查询示例:")
    print(f"content-layout-leo-cskill: {registry.get_skill('content-layout-leo-cskill')}")
    print(f"task-agent: {registry.get_agent('task-agent')}")
