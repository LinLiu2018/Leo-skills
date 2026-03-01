"""
Skill加载器
===========
负责发现、加载和管理所有Skills
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional

import yaml

# 添加父目录到路径
parent_path = Path(__file__).parent.parent.parent
if str(parent_path) not in sys.path:
    sys.path.insert(0, str(parent_path))

from leo_system.logger import get_logger
from leo_system.metrics import track_time
from .skill_adapter import SkillAdapter, get_skill_adapter

# 创建日志记录器
logger = get_logger(__name__)


class SkillLoader:
    """
    Skill加载器
    ===========
    自动发现并加载所有可用的Skills
    """

    def __init__(self, base_path: str = None):
        """
        初始化加载器

        Args:
            base_path: leo_skills的基础路径
        """
        if base_path is None:
            # 默认路径：项目根目录/leo_skills
            current_file = Path(__file__)
            base_path = current_file.parent.parent.parent / "leo_skills"

        self.base_path = Path(base_path)
        self.skills: Dict[str, SkillAdapter] = {}
        self.categories: Dict[str, List[str]] = {}

    @track_time
    def discover_and_load(self) -> int:
        """
        自动发现并加载所有Skills

        Returns:
            加载的Skill数量
        """
        if not self.base_path.exists():
            logger.warning(f"Skills路径不存在: {self.base_path}")
            return 0

        count = 0

        # 遍历所有分类目录
        for category_dir in self.base_path.iterdir():
            if not category_dir.is_dir() or category_dir.name.startswith("."):
                continue

            category = category_dir.name
            self.categories[category] = []

            # 遍历该分类下的所有Skills
            for skill_dir in category_dir.iterdir():
                if skill_dir.is_dir() and (skill_dir.name.endswith("_skill") or skill_dir.name.endswith("-cskill")):
                    skill_name = skill_dir.name

                    # 加载Skill
                    adapter = self._load_skill(str(skill_dir), skill_name, category)
                    if adapter:
                        self.skills[skill_name] = adapter
                        self.categories[category].append(skill_name)
                        count += 1

        logger.info(f"加载了 {count} 个Skills")
        return count

    def _load_skill(
        self, skill_path: str, skill_name: str, category: str
    ) -> Optional[SkillAdapter]:
        """
        加载单个Skill

        Args:
            skill_path: Skill路径
            skill_name: Skill名称
            category: 分类名称

        Returns:
            Skill适配器或None
        """
        try:
            adapter = get_skill_adapter(skill_name, skill_path)

            # 更新分类信息
            if adapter.metadata:
                adapter.metadata.category = category

            return adapter
        except Exception as e:
            logger.error(f"加载Skill '{skill_name}' 失败: {e}")
            return None

    def load_from_config(self, config_path: str) -> int:
        """
        从配置文件加载Skills

        Args:
            config_path: 配置文件路径

        Returns:
            加载的Skill数量
        """
        config_file = Path(config_path)
        if not config_file.exists():
            logger.warning(f"配置文件不存在: {config_path}")
            return 0

        with open(config_file, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        count = 0
        if "skills" in config:
            for skill_config in config["skills"]:
                if not skill_config.get("enabled", True):
                    continue

                skill_name = skill_config["name"]
                skill_path = self.base_path.parent / skill_config["path"]
                category = skill_config.get("category", "general")

                adapter = self._load_skill(str(skill_path), skill_name, category)
                if adapter:
                    self.skills[skill_name] = adapter
                    if category not in self.categories:
                        self.categories[category] = []
                    self.categories[category].append(skill_name)
                    count += 1

        logger.info(f"从配置加载了 {count} 个Skills")
        return count

    def get_skill(self, skill_name: str) -> Optional[SkillAdapter]:
        """
        获取指定Skill

        Args:
            skill_name: Skill名称

        Returns:
            Skill适配器或None
        """
        return self.skills.get(skill_name)

    def list_skills(self, category: Optional[str] = None) -> List[str]:
        """
        列出Skills

        Args:
            category: 分类筛选（可选）

        Returns:
            Skill名称列表
        """
        if category:
            return self.categories.get(category, [])
        return list(self.skills.keys())

    def list_categories(self) -> List[str]:
        """
        列出所有分类

        Returns:
            分类名称列表
        """
        return list(self.categories.keys())

    def get_skills_by_category(self, category: str) -> List[SkillAdapter]:
        """
        获取指定分类的所有Skills

        Args:
            category: 分类名称

        Returns:
            Skill适配器列表
        """
        skill_names = self.categories.get(category, [])
        return [self.skills[name] for name in skill_names if name in self.skills]

    def get_skill_info(self, skill_name: str) -> Optional[dict]:
        """
        获取Skill详细信息

        Args:
            skill_name: Skill名称

        Returns:
            Skill信息字典或None
        """
        adapter = self.get_skill(skill_name)
        if adapter:
            return adapter.get_skill_info()
        return None

    def print_summary(self):
        """打印加载摘要"""
        logger.info("=" * 60)
        logger.info("Skills加载摘要")
        logger.info("=" * 60)
        logger.info(f"总计: {len(self.skills)} 个Skills")

        for category, skills in self.categories.items():
            logger.info(f"{category} ({len(skills)}个):")
            for skill_name in skills:
                adapter = self.skills.get(skill_name)
                if adapter and adapter.metadata:
                    status = "enabled" if adapter.metadata.enabled else "disabled"
                    logger.info(f"  {status} {skill_name}")
                    if adapter.metadata.description:
                        logger.info(f"      {adapter.metadata.description}")

        logger.info("=" * 60)


# ==================== 全局加载器实例 ====================

_global_loader: Optional[SkillLoader] = None


def get_loader() -> SkillLoader:
    """
    获取全局加载器实例（线程安全）

    Returns:
        Skill加载器实例
    """
    global _global_loader
    if _global_loader is None:
        from leo_system.singleton import thread_safe_singleton
        def _create_loader():
            loader = SkillLoader()
            loader.discover_and_load()
            return loader
        _global_loader = thread_safe_singleton(
            "skill_loader", _global_loader, _create_loader
        )
    return _global_loader


def load_skill(skill_name: str) -> Optional[SkillAdapter]:
    """
    便捷函数：加载单个Skill

    Args:
        skill_name: Skill名称

    Returns:
        Skill适配器或None
    """
    loader = get_loader()
    return loader.get_skill(skill_name)


# ==================== 使用示例 ====================

if __name__ == "__main__":
    # 创建加载器
    loader = SkillLoader()

    # 自动发现并加载
    loader.discover_and_load()

    # 打印摘要
    loader.print_summary()

    # 查询Skills
    logger.info("查询示例:")
    logger.info(f"所有分类: {loader.list_categories()}")
    logger.info(f"内容创作类Skills: {loader.list_skills('content-creation')}")

    # 获取特定Skill
    skill = loader.get_skill("content_layout_leo_skill")
    if skill:
        info = skill.get_skill_info()
        logger.info(f"Skill详情: {info}")
