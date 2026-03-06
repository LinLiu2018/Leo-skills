#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Skill 同步脚本 - 将 Leo Skills 同步到 Claude Code

功能:
1. 扫描 src/leo_skills 目录，发现所有 skill
2. 解析 SKILL.md 元数据
3. 生成 .claude/skill_registry.json
4. 同步到 .claude/skills/ 目录 (软链接或复制)

用法:
    python scripts/sync/sync_skills_to_claude.py
    python scripts/sync/sync_skills_to_claude.py --watch  # 监听模式
"""

import argparse
import json
import logging
import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set

import yaml

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SkillSync:
    """Skill 同步管理器"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.skills_dir = self.project_root / "src" / "leo_skills"
        self.claude_dir = self.project_root / ".claude"
        self.registry_file = self.claude_dir / "skill_registry.json"

        # 统计
        self.stats = {
            "scanned": 0,
            "parsed": 0,
            "registered": 0,
            "errors": 0,
        }

    def discover_skills(self) -> List[Dict[str, any]]:
        """
        发现所有 skills

        Returns:
            技能列表，每个技能包含元数据
        """
        skills = []

        if not self.skills_dir.exists():
            logger.error(f"Skills directory not found: {self.skills_dir}")
            return skills

        # 遍历分类目录
        for category_dir in self.skills_dir.iterdir():
            if not category_dir.is_dir() or category_dir.name.startswith((".", "_")):
                continue

            category = category_dir.name

            # 遍历技能目录
            for skill_dir in category_dir.iterdir():
                if not skill_dir.is_dir():
                    continue

                skill_name = skill_dir.name

                # 检查是否是 skill 目录 (以 _skill 或 -cskill 结尾)
                if not (skill_name.endswith("_skill") or skill_name.endswith("-cskill")):
                    continue

                self.stats["scanned"] += 1

                # 解析 skill 元数据
                skill_info = self._parse_skill(skill_dir, category)
                if skill_info:
                    skills.append(skill_info)
                    self.stats["parsed"] += 1

        logger.info(f"Discovered {len(skills)} skills from {self.stats['scanned']} directories")
        return skills

    def _parse_skill(self, skill_dir: Path, category: str) -> Optional[Dict[str, any]]:
        """
        解析单个 skill 的元数据

        Args:
            skill_dir: Skill 目录路径
            category: 分类名称

        Returns:
            Skill 元数据字典，或 None 如果解析失败
        """
        skill_name = skill_dir.name

        # 基础信息
        skill_info = {
            "name": skill_name,
            "category": category,
            "path": str(skill_dir.relative_to(self.project_root)),
            "registered_at": datetime.now().isoformat(),
            "triggers": [],
            "description": "",
            "version": "1.0.0",
            "author": "Leo System",
            "compatibility": ["claude-code", "openclaw"],
            "metadata": {},
        }

        # 1. 解析 SKILL.md
        skill_md = skill_dir / "SKILL.md"
        if skill_md.exists():
            try:
                metadata = self._parse_skill_md(skill_md)
                skill_info["metadata"].update(metadata)

                # 提取关键字段
                if "name" in metadata:
                    skill_info["name"] = metadata["name"]
                if "description" in metadata:
                    skill_info["description"] = metadata["description"]
                if "version" in metadata:
                    skill_info["version"] = metadata["version"]
                if "triggers" in metadata:
                    skill_info["triggers"] = metadata["triggers"]

            except Exception as e:
                logger.warning(f"Failed to parse {skill_md}: {e}")
                self.stats["errors"] += 1

        # 2. 如果没有触发词，生成默认触发词
        if not skill_info["triggers"]:
            default_trigger = skill_name.replace("_skill", "").replace("-", " ")
            skill_info["triggers"] = [default_trigger]

        # 3. 检查 scripts/main.py 是否存在
        main_script = skill_dir / "scripts" / "main.py"
        skill_info["has_main_script"] = main_script.exists()

        # 4. 检查 evolution.json
        evolution_file = skill_dir / "evolution.json"
        if evolution_file.exists():
            try:
                with open(evolution_file, "r", encoding="utf-8") as f:
                    skill_info["evolution"] = json.load(f)
            except Exception as e:
                logger.debug(f"Failed to load evolution.json for {skill_name}: {e}")

        return skill_info

    def _parse_skill_md(self, skill_md_path: Path) -> Dict[str, any]:
        """
        从 SKILL.md 解析 YAML frontmatter

        Args:
            skill_md_path: SKILL.md 文件路径

        Returns:
            元数据字典
        """
        import datetime

        content = skill_md_path.read_text(encoding="utf-8")

        # 检查是否有 YAML frontmatter
        if not content.startswith("---"):
            # 尝试从内容中提取描述
            lines = content.strip().split("\n")
            description = ""
            for line in lines:
                line = line.strip()
                if line and not line.startswith("#"):
                    description = line
                    break
            return {"description": description}

        # 解析 frontmatter
        parts = content.split("---", 2)
        if len(parts) < 3:
            return {}

        try:
            frontmatter = yaml.safe_load(parts[1])
            if isinstance(frontmatter, dict):
                # 将 date 对象转换为字符串，使其可 JSON 序列化
                def convert_dates(obj):
                    if isinstance(obj, datetime.date):
                        return obj.isoformat()
                    elif isinstance(obj, dict):
                        return {k: convert_dates(v) for k, v in obj.items()}
                    elif isinstance(obj, list):
                        return [convert_dates(i) for i in obj]
                    return obj

                return convert_dates(frontmatter)
        except yaml.YAMLError as e:
            logger.warning(f"YAML parse error in {skill_md_path}: {e}")

        return {}

    def generate_registry(self, skills: List[Dict[str, any]]) -> Dict[str, any]:
        """
        生成技能注册表

        Args:
            skills: 技能列表

        Returns:
            注册表字典
        """
        # 按分类组织
        by_category = {}
        for skill in skills:
            cat = skill["category"]
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(skill)

        # 构建触发词索引
        trigger_index = {}
        for skill in skills:
            for trigger in skill.get("triggers", []):
                trigger_lower = trigger.lower()
                if trigger_lower not in trigger_index:
                    trigger_index[trigger_lower] = []
                trigger_index[trigger_lower].append(skill["name"])

        registry = {
            "version": "2.0",
            "generated_at": datetime.now().isoformat(),
            "stats": {
                "total_skills": len(skills),
                "categories": len(by_category),
                "total_triggers": len(trigger_index),
            },
            "skills": {s["name"]: s for s in skills},
            "by_category": by_category,
            "trigger_index": trigger_index,
            "quick_lookup": {
                "房产": ["realestate", "villa", "auction", "leasing"],
                "贷款": ["loan", "mortgage", "credit"],
                "电商": ["amazon", "shopify", "aliexpress", "ebay"],
                "内容": ["content", "article", "publish", "seo"],
                "开发": ["code", "api", "database", "test"],
            }
        }

        return registry

    def save_registry(self, registry: Dict[str, any]) -> bool:
        """
        保存注册表到文件

        Args:
            registry: 注册表字典

        Returns:
            是否成功
        """
        try:
            # 确保目录存在
            self.claude_dir.mkdir(parents=True, exist_ok=True)

            # 保存注册表
            with open(self.registry_file, "w", encoding="utf-8") as f:
                json.dump(registry, f, ensure_ascii=False, indent=2)

            logger.info(f"Saved registry to {self.registry_file}")
            self.stats["registered"] = registry["stats"]["total_skills"]
            return True

        except Exception as e:
            logger.error(f"Failed to save registry: {e}")
            self.stats["errors"] += 1
            return False

    def sync_to_claude_skills(self, skills: List[Dict[str, any]], copy: bool = False) -> int:
        """
        同步 skills 到 .claude/skills/ 目录

        Args:
            skills: 技能列表
            copy: 是否复制文件，否则创建软链接

        Returns:
            同步的技能数量
        """
        claude_skills_dir = self.claude_dir / "skills"
        claude_skills_dir.mkdir(parents=True, exist_ok=True)

        synced = 0

        for skill in skills:
            skill_name = skill["name"]
            src_dir = self.project_root / skill["path"]

            # 修复 Windows 无效字符 (如 : )
            safe_skill_name = re.sub(r'[<>:"/\\|?*]', '_', skill_name)
            dst_dir = claude_skills_dir / safe_skill_name

            try:
                if dst_dir.exists() or dst_dir.is_symlink():
                    if dst_dir.is_symlink():
                        dst_dir.unlink()
                    else:
                        shutil.rmtree(dst_dir)

                # Windows 下默认使用复制，软链接需要管理员权限
                if copy or os.name == 'nt':
                    shutil.copytree(src_dir, dst_dir, ignore=shutil.ignore_patterns('node_modules', '__pycache__', '.git'))
                    logger.debug(f"Copied {skill_name} to {dst_dir}")
                else:
                    # 创建相对路径的软链接
                    rel_path = os.path.relpath(src_dir, claude_skills_dir)
                    dst_dir.symlink_to(rel_path, target_is_directory=True)
                    logger.debug(f"Linked {skill_name} -> {rel_path}")

                synced += 1

            except Exception as e:
                logger.error(f"Failed to sync {skill_name}: {e}")
                self.stats["errors"] += 1

        logger.info(f"Synced {synced} skills to {claude_skills_dir}")
        return synced

    def generate_skill_summary(self, registry: Dict[str, any]) -> str:
        """
        生成技能摘要 Markdown

        Args:
            registry: 注册表字典

        Returns:
            Markdown 字符串
        """
        lines = [
            "# Leo Skills 注册表",
            "",
            f"> 生成时间: {registry['generated_at']}",
            f"> 总技能数: {registry['stats']['total_skills']}",
            f"> 分类数: {registry['stats']['categories']}",
            "",
            "## 快速查找",
            "",
        ]

        for keyword, related in registry["quick_lookup"].items():
            lines.append(f"- **{keyword}**: {', '.join(related)}")

        lines.extend(["", "## 分类目录", ""])

        for category, skills in sorted(registry["by_category"].items()):
            lines.append(f"### {category} ({len(skills)})")
            lines.append("")

            for skill in sorted(skills, key=lambda x: x["name"]):
                desc = skill.get("description", "")[:50]
                triggers = ", ".join(skill.get("triggers", [])[:3])
                lines.append(f"- **{skill['name']}** - {desc}")
                if triggers:
                    lines.append(f"  - 触发词: `{triggers}`")

            lines.append("")

        return "\n".join(lines)

    def run(self, sync_to_claude: bool = True, generate_summary: bool = True) -> Dict[str, any]:
        """
        执行完整同步流程

        Args:
            sync_to_claude: 是否同步到 .claude/skills/
            generate_summary: 是否生成摘要文档

        Returns:
            统计信息
        """
        logger.info("=" * 60)
        logger.info("Leo Skills 同步开始")
        logger.info("=" * 60)

        # 1. 发现 skills
        skills = self.discover_skills()

        if not skills:
            logger.warning("No skills found!")
            return self.stats

        # 2. 生成注册表
        registry = self.generate_registry(skills)

        # 3. 保存注册表
        if self.save_registry(registry):
            logger.info(f"✅ Registered {self.stats['registered']} skills")

        # 4. 同步到 Claude skills 目录
        if sync_to_claude:
            synced = self.sync_to_claude_skills(skills, copy=False)
            logger.info(f"✅ Synced {synced} skills to .claude/skills/")

        # 5. 生成摘要
        if generate_summary:
            summary = self.generate_skill_summary(registry)
            summary_file = self.claude_dir / "SKILLS_SUMMARY.md"
            with open(summary_file, "w", encoding="utf-8") as f:
                f.write(summary)
            logger.info(f"✅ Generated summary: {summary_file}")

        logger.info("=" * 60)
        logger.info("同步完成")
        logger.info(f"  - 扫描: {self.stats['scanned']}")
        logger.info(f"  - 解析: {self.stats['parsed']}")
        logger.info(f"  - 注册: {self.stats['registered']}")
        logger.info(f"  - 错误: {self.stats['errors']}")
        logger.info("=" * 60)

        return self.stats


def watch_mode(syncer: SkillSync, interval: int = 30):
    """监听模式，自动检测变化并同步"""
    import time

    logger.info(f"Watch mode started (interval: {interval}s)")
    logger.info("Press Ctrl+C to stop")

    last_mtime = {}

    try:
        while True:
            changed = False

            # 检查所有 SKILL.md 文件
            for skill_md in syncer.skills_dir.rglob("SKILL.md"):
                try:
                    mtime = skill_md.stat().st_mtime
                    if skill_md not in last_mtime or last_mtime[skill_md] != mtime:
                        changed = True
                        last_mtime[skill_md] = mtime
                except Exception:
                    pass

            if changed:
                logger.info("Changes detected, syncing...")
                syncer.run()

            time.sleep(interval)

    except KeyboardInterrupt:
        logger.info("Watch mode stopped")


def main():
    parser = argparse.ArgumentParser(description="Sync Leo Skills to Claude Code")
    parser.add_argument("--watch", action="store_true", help="Watch mode")
    parser.add_argument("--interval", type=int, default=30, help="Watch interval (seconds)")
    parser.add_argument("--no-sync", action="store_true", help="Don't sync to .claude/skills/")
    parser.add_argument("--copy", action="store_true", help="Copy files instead of symlinks")

    args = parser.parse_args()

    syncer = SkillSync()

    if args.watch:
        watch_mode(syncer, args.interval)
    else:
        syncer.run(sync_to_claude=not args.no_sync)


if __name__ == "__main__":
    main()
