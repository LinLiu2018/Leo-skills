#!/usr/bin/env python3
"""
Obsidian Sync Skill - Main Entry Point

将Claude对话、Leo System输出与Obsidian第二大脑无缝集成的同步技能。

Author: Claude Code
Version: 1.0.0
"""

import os
import re
import sys
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ObsidianSync:
    """
    Obsidian Sync Skill
    ===================
    将Claude/Leo输出同步到Obsidian知识库的核心类。

    功能:
    - 快速捕获内容到Inbox
    - 使用模板创建结构化笔记
    - 自动添加元数据、标签、链接
    - 保存Leo Skill输出
    - 管理日记和MOC
    """

    def __init__(self, vault_path: Optional[str] = None, config_path: Optional[str] = None):
        """
        初始化Obsidian Sync Skill。

        Args:
            vault_path: Obsidian Vault路径，如不提供则从配置读取
            config_path: 配置文件路径
        """
        # 加载配置
        self.config = self._load_config(config_path)

        # 设置Vault路径
        self.vault_path = Path(vault_path or self.config.get('vault_path', ''))
        if not self.vault_path or not self.vault_path.exists():
            logger.warning(f"Vault路径不存在或未配置: {self.vault_path}")
            logger.info("请在config.yaml中配置vault_path或初始化时传入")

        # 初始化文件夹结构
        if self.vault_path.exists() and self.config.get('auto_create_folders', True):
            self._init_folder_structure()

        # 加载模板
        self.templates = self._load_templates()

        logger.info(f"Obsidian Sync初始化完成，Vault: {self.vault_path}")

    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """加载配置文件。"""
        if config_path is None:
            config_path = Path(__file__).parent.parent / 'config' / 'config.yaml'

        config_path = Path(config_path)

        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}

        # 默认配置
        return {
            'vault_path': '',
            'default_folder': '00-Inbox',
            'template_folder': 'Templates',
            'auto_create_folders': True,
            'auto_add_metadata': True,
            'default_tags': ['claude生成'],
            'leo_output_folder': 'Leo-Outputs',
            'daily_folder': '01-Daily',
            'daily_format': '%Y-%m-%d',
            'moc_folder': 'MOCs'
        }

    def _init_folder_structure(self):
        """初始化推荐的文件夹结构。"""
        folders = [
            '00-Inbox',
            '01-Daily',
            '10-Projects',
            '20-Areas',
            '30-Resources',
            '40-Archives',
            'Leo-Outputs/content-layout',
            'Leo-Outputs/research',
            'Leo-Outputs/marketing',
            'Leo-Outputs/analysis',
            'Claude-Notes',
            'MOCs',
            'Templates'
        ]

        for folder in folders:
            folder_path = self.vault_path / folder
            folder_path.mkdir(parents=True, exist_ok=True)

    def _load_templates(self) -> Dict[str, str]:
        """加载内置模板。"""
        return {
            'default': '''---
created: {{datetime}}
tags: [{{tags}}]
aliases: []
---

# {{title}}

{{content}}

## 相关链接
{{links}}
''',
            'daily': '''---
created: {{datetime}}
tags: [日记, {{tags}}]
---

# {{date}} {{weekday}}

## 今日计划
{{plan}}

## 记录
{{content}}

## 复盘
- 今日最大收获：
- 明天改进：

## 相关链接
{{links}}
''',
            'research': '''---
created: {{datetime}}
source: {{source}}
tags: [研究, {{tags}}]
---

# {{title}}

## 核心观点
{{summary}}

## 详细内容
{{content}}

## 我的思考


## 行动项
- [ ]

## 相关链接
{{links}}
''',
            'claude': '''---
created: {{datetime}}
source: Claude对话
tags: [claude笔记, {{tags}}]
---

# {{title}}

## 问题/需求
{{question}}

## Claude回答摘要
{{content}}

## 我的思考


## 行动项
- [ ]

## 相关链接
{{links}}
''',
            'leo-output': '''---
created: {{datetime}}
source: Leo-System
skill: {{skill_name}}
tags: [leo-output, {{skill_name}}, {{tags}}]
---

# {{title}}

{{content}}

---
*由 Leo System {{skill_name}} 自动生成*
''',
            'project': '''---
created: {{datetime}}
status: active
tags: [项目, {{tags}}]
---

# {{title}}

## 项目概述
{{content}}

## 目标
-

## 进度
- [ ]

## 关键决策


## 相关链接
{{links}}
''',
            'moc': '''---
created: {{datetime}}
tags: [MOC, 索引]
---

# {{title}} MOC

## 概述
这是关于{{title}}的内容地图。

## 核心概念
{{links}}

## 延伸阅读


---
*最后更新: {{datetime}}*
'''
        }

    def _render_template(self, template_name: str, variables: Dict[str, Any]) -> str:
        """渲染模板。"""
        template = self.templates.get(template_name, self.templates['default'])

        # 添加时间变量
        now = datetime.now()
        variables.setdefault('date', now.strftime('%Y-%m-%d'))
        variables.setdefault('time', now.strftime('%H:%M'))
        variables.setdefault('datetime', now.strftime('%Y-%m-%d %H:%M'))
        variables.setdefault('weekday', ['周一', '周二', '周三', '周四', '周五', '周六', '周日'][now.weekday()])

        # 处理标签
        tags = variables.get('tags', [])
        if isinstance(tags, list):
            variables['tags'] = ', '.join(tags)

        # 处理链接
        links = variables.get('links', [])
        if isinstance(links, list):
            variables['links'] = '\n'.join([f'- [[{link}]]' for link in links]) if links else ''

        # 处理计划列表
        plan = variables.get('plan', [])
        if isinstance(plan, list):
            variables['plan'] = '\n'.join([f'- [ ] {item}' for item in plan]) if plan else '- [ ] '

        # 渲染模板
        result = template
        for key, value in variables.items():
            result = result.replace('{{' + key + '}}', str(value) if value else '')

        # 清理未替换的变量
        result = re.sub(r'\{\{\w+\}\}', '', result)

        return result

    def _sanitize_filename(self, filename: str) -> str:
        """清理文件名，移除非法字符。"""
        # 移除非法字符
        illegal_chars = '<>:"/\\|?*'
        for char in illegal_chars:
            filename = filename.replace(char, '')
        return filename.strip()

    def _ensure_folder(self, folder: str) -> Path:
        """确保文件夹存在。"""
        folder_path = self.vault_path / folder
        folder_path.mkdir(parents=True, exist_ok=True)
        return folder_path

    # ==================== 核心功能 ====================

    def quick_capture(
        self,
        content: str,
        title: Optional[str] = None,
        tags: Optional[List[str]] = None,
        folder: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        快速捕获内容到Inbox。

        Args:
            content: 要保存的内容
            title: 笔记标题，如不提供则自动生成
            tags: 标签列表
            folder: 目标文件夹，默认为Inbox

        Returns:
            操作结果字典
        """
        if not self.vault_path.exists():
            return {'success': False, 'error': 'Vault路径不存在'}

        # 生成标题
        if not title:
            title = f"快速笔记_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        title = self._sanitize_filename(title)

        # 合并标签
        all_tags = list(self.config.get('default_tags', []))
        if tags:
            all_tags.extend(tags)
        all_tags = list(set(all_tags))  # 去重

        # 渲染内容
        note_content = self._render_template('default', {
            'title': title,
            'content': content,
            'tags': all_tags,
            'links': []
        })

        # 确定保存路径
        target_folder = folder or self.config.get('default_folder', '00-Inbox')
        folder_path = self._ensure_folder(target_folder)
        file_path = folder_path / f"{title}.md"

        # 保存文件
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(note_content)

            logger.info(f"快速捕获成功: {file_path}")
            return {
                'success': True,
                'path': str(file_path),
                'title': title,
                'folder': target_folder
            }
        except Exception as e:
            logger.error(f"保存失败: {e}")
            return {'success': False, 'error': str(e)}

    def create_note(
        self,
        title: str,
        content: str,
        template: str = 'default',
        folder: Optional[str] = None,
        tags: Optional[List[str]] = None,
        links: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        创建结构化笔记。

        Args:
            title: 笔记标题
            content: 笔记内容
            template: 模板名称
            folder: 目标文件夹
            tags: 标签列表
            links: 相关链接列表
            **kwargs: 传递给模板的其他变量

        Returns:
            操作结果字典
        """
        if not self.vault_path.exists():
            return {'success': False, 'error': 'Vault路径不存在'}

        title = self._sanitize_filename(title)

        # 准备模板变量
        variables = {
            'title': title,
            'content': content,
            'tags': tags or [],
            'links': links or [],
            **kwargs
        }

        # 渲染内容
        note_content = self._render_template(template, variables)

        # 确定保存路径
        target_folder = folder or self.config.get('default_folder', '00-Inbox')
        folder_path = self._ensure_folder(target_folder)
        file_path = folder_path / f"{title}.md"

        # 保存文件
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(note_content)

            logger.info(f"笔记创建成功: {file_path}")
            return {
                'success': True,
                'path': str(file_path),
                'title': title,
                'folder': target_folder,
                'template': template
            }
        except Exception as e:
            logger.error(f"创建笔记失败: {e}")
            return {'success': False, 'error': str(e)}

    def create_daily_note(
        self,
        date: Optional[str] = None,
        plan: Optional[List[str]] = None,
        notes: str = '',
        links: Optional[List[str]] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        创建日记。

        Args:
            date: 日期字符串，默认今天
            plan: 今日计划列表
            notes: 笔记内容
            links: 相关链接
            tags: 额外标签

        Returns:
            操作结果字典
        """
        if not self.vault_path.exists():
            return {'success': False, 'error': 'Vault路径不存在'}

        # 确定日期
        if date:
            try:
                note_date = datetime.strptime(date, '%Y-%m-%d')
            except ValueError:
                note_date = datetime.now()
        else:
            note_date = datetime.now()

        date_str = note_date.strftime('%Y-%m-%d')
        weekday = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'][note_date.weekday()]

        # 准备变量
        variables = {
            'title': date_str,
            'date': date_str,
            'weekday': weekday,
            'plan': plan or [],
            'content': notes,
            'links': links or [],
            'tags': tags or []
        }

        # 渲染内容
        note_content = self._render_template('daily', variables)

        # 确定保存路径
        daily_folder = self.config.get('daily_folder', '01-Daily')
        folder_path = self._ensure_folder(daily_folder)
        file_path = folder_path / f"{date_str}.md"

        # 保存文件
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(note_content)

            logger.info(f"日记创建成功: {file_path}")
            return {
                'success': True,
                'path': str(file_path),
                'date': date_str
            }
        except Exception as e:
            logger.error(f"创建日记失败: {e}")
            return {'success': False, 'error': str(e)}

    def save_leo_output(
        self,
        content: Union[str, Dict, Any],
        skill_name: str,
        title: Optional[str] = None,
        folder: Optional[str] = None,
        tags: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        保存Leo Skill输出。

        Args:
            content: Leo输出内容（字符串或字典）
            skill_name: Skill名称
            title: 笔记标题
            folder: 目标文件夹
            tags: 额外标签
            **kwargs: 其他参数（如topic, project等）

        Returns:
            操作结果字典
        """
        if not self.vault_path.exists():
            return {'success': False, 'error': 'Vault路径不存在'}

        # 处理内容
        if isinstance(content, dict):
            content_str = yaml.dump(content, allow_unicode=True, default_flow_style=False)
        elif not isinstance(content, str):
            content_str = str(content)
        else:
            content_str = content

        # 生成标题
        if not title:
            topic = kwargs.get('topic', '')
            project = kwargs.get('project', '')
            date_str = datetime.now().strftime('%Y-%m-%d')

            if topic:
                title = f"{date_str}_{topic}_{skill_name}"
            elif project:
                title = f"{project}_{skill_name}_{date_str}"
            else:
                title = f"{skill_name}_{date_str}"

        title = self._sanitize_filename(title)

        # 确定文件夹
        if not folder:
            leo_folder = self.config.get('leo_output_folder', 'Leo-Outputs')
            skill_folders = self.config.get('skill_folders', {})
            sub_folder = skill_folders.get(skill_name, skill_name.replace('-cskill', ''))
            folder = f"{leo_folder}/{sub_folder}"

        # 准备变量
        variables = {
            'title': title,
            'content': content_str,
            'skill_name': skill_name,
            'tags': tags or [],
            **kwargs
        }

        # 渲染内容
        note_content = self._render_template('leo-output', variables)

        # 保存
        folder_path = self._ensure_folder(folder)
        file_path = folder_path / f"{title}.md"

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(note_content)

            logger.info(f"Leo输出保存成功: {file_path}")
            return {
                'success': True,
                'path': str(file_path),
                'title': title,
                'skill': skill_name,
                'folder': folder
            }
        except Exception as e:
            logger.error(f"保存Leo输出失败: {e}")
            return {'success': False, 'error': str(e)}

    def save_claude_note(
        self,
        content: str,
        title: str,
        question: str = '',
        tags: Optional[List[str]] = None,
        links: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        保存Claude对话笔记。

        Args:
            content: Claude回答内容
            title: 笔记标题
            question: 原始问题
            tags: 标签列表
            links: 相关链接

        Returns:
            操作结果字典
        """
        return self.create_note(
            title=title,
            content=content,
            template='claude',
            folder='Claude-Notes',
            tags=tags,
            links=links,
            question=question,
            source='Claude对话'
        )

    def update_moc(
        self,
        moc_name: str,
        add_links: Optional[List[str]] = None,
        remove_links: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        更新MOC（内容地图）。

        Args:
            moc_name: MOC名称
            add_links: 要添加的链接列表
            remove_links: 要移除的链接列表

        Returns:
            操作结果字典
        """
        if not self.vault_path.exists():
            return {'success': False, 'error': 'Vault路径不存在'}

        moc_folder = self.config.get('moc_folder', 'MOCs')
        moc_path = self.vault_path / moc_folder / f"{moc_name}.md"

        # 读取现有MOC或创建新的
        if moc_path.exists():
            with open(moc_path, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            # 创建新MOC
            content = self._render_template('moc', {
                'title': moc_name,
                'links': add_links or []
            })
            self._ensure_folder(moc_folder)
            with open(moc_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return {
                'success': True,
                'path': str(moc_path),
                'action': 'created',
                'moc_name': moc_name
            }

        # 更新链接
        if add_links:
            for link in add_links:
                link_str = f'- [[{link}]]'
                if link_str not in content:
                    # 在"## 核心概念"后添加
                    if '## 核心概念' in content:
                        content = content.replace(
                            '## 核心概念\n',
                            f'## 核心概念\n{link_str}\n'
                        )
                    else:
                        content += f'\n{link_str}'

        if remove_links:
            for link in remove_links:
                content = content.replace(f'- [[{link}]]\n', '')
                content = content.replace(f'- [[{link}]]', '')

        # 更新时间戳
        content = re.sub(
            r'\*最后更新: .*\*',
            f'*最后更新: {datetime.now().strftime("%Y-%m-%d %H:%M")}*',
            content
        )

        # 保存
        try:
            with open(moc_path, 'w', encoding='utf-8') as f:
                f.write(content)

            return {
                'success': True,
                'path': str(moc_path),
                'action': 'updated',
                'moc_name': moc_name,
                'added': add_links,
                'removed': remove_links
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def add_links_to_note(
        self,
        note_path: str,
        links: List[str]
    ) -> Dict[str, Any]:
        """
        向现有笔记添加链接。

        Args:
            note_path: 笔记相对路径
            links: 要添加的链接列表

        Returns:
            操作结果字典
        """
        full_path = self.vault_path / note_path

        if not full_path.exists():
            return {'success': False, 'error': '笔记不存在'}

        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 添加链接到"相关链接"部分
            links_section = '\n'.join([f'- [[{link}]]' for link in links])

            if '## 相关链接' in content:
                content = content.replace(
                    '## 相关链接\n',
                    f'## 相关链接\n{links_section}\n'
                )
            else:
                content += f'\n\n## 相关链接\n{links_section}'

            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)

            return {
                'success': True,
                'path': str(full_path),
                'added_links': links
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def search_notes(
        self,
        query: str,
        folder: Optional[str] = None,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        搜索笔记。

        Args:
            query: 搜索关键词
            folder: 限定搜索的文件夹
            limit: 最大结果数

        Returns:
            搜索结果
        """
        if not self.vault_path.exists():
            return {'success': False, 'error': 'Vault路径不存在'}

        results = []
        search_path = self.vault_path / folder if folder else self.vault_path

        for md_file in search_path.rglob('*.md'):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                if query.lower() in content.lower():
                    # 提取匹配的上下文
                    idx = content.lower().find(query.lower())
                    start = max(0, idx - 50)
                    end = min(len(content), idx + len(query) + 50)
                    context = content[start:end]

                    results.append({
                        'path': str(md_file.relative_to(self.vault_path)),
                        'title': md_file.stem,
                        'context': f'...{context}...'
                    })

                    if len(results) >= limit:
                        break
            except Exception:
                continue

        return {
            'success': True,
            'query': query,
            'results': results,
            'total': len(results)
        }

    def get_recent_notes(self, limit: int = 10, folder: Optional[str] = None) -> Dict[str, Any]:
        """
        获取最近修改的笔记。

        Args:
            limit: 返回数量
            folder: 限定文件夹

        Returns:
            最近笔记列表
        """
        if not self.vault_path.exists():
            return {'success': False, 'error': 'Vault路径不存在'}

        search_path = self.vault_path / folder if folder else self.vault_path

        notes = []
        for md_file in search_path.rglob('*.md'):
            notes.append({
                'path': str(md_file.relative_to(self.vault_path)),
                'title': md_file.stem,
                'modified': md_file.stat().st_mtime
            })

        # 按修改时间排序
        notes.sort(key=lambda x: x['modified'], reverse=True)

        # 格式化时间
        for note in notes[:limit]:
            note['modified'] = datetime.fromtimestamp(
                note['modified']
            ).strftime('%Y-%m-%d %H:%M')

        return {
            'success': True,
            'notes': notes[:limit],
            'total': len(notes)
        }

    def get_help(self) -> str:
        """获取帮助信息。"""
        return """
Obsidian Sync Skill 帮助
========================

功能:
1. quick_capture(content, title) - 快速保存到Inbox
2. create_note(title, content, template, folder, tags, links) - 创建结构化笔记
3. create_daily_note(plan, notes, links) - 创建日记
4. save_leo_output(content, skill_name, **kwargs) - 保存Leo输出
5. save_claude_note(content, title, question) - 保存Claude对话
6. update_moc(moc_name, add_links) - 更新MOC索引
7. search_notes(query) - 搜索笔记
8. get_recent_notes(limit) - 获取最近笔记

模板:
- default: 通用笔记
- daily: 日记
- research: 研究笔记
- claude: Claude对话记录
- leo-output: Leo输出
- project: 项目笔记
- moc: 内容地图

使用示例:
```python
sync = ObsidianSync(vault_path="D:/Obsidian/MyVault")
sync.quick_capture("重要内容...", title="学习笔记")
sync.create_daily_note(plan=["任务1", "任务2"])
```
"""


# ==================== 便捷函数 ====================

def get_sync(vault_path: Optional[str] = None) -> ObsidianSync:
    """获取ObsidianSync实例的便捷函数。"""
    return ObsidianSync(vault_path=vault_path)


# ==================== 命令行接口 ====================

def main():
    """命令行入口。"""
    import argparse

    parser = argparse.ArgumentParser(description="Obsidian Sync Skill CLI")
    parser.add_argument(
        "command",
        choices=["capture", "daily", "search", "recent", "help"],
        help="命令"
    )
    parser.add_argument("--vault", help="Vault路径")
    parser.add_argument("--content", help="内容")
    parser.add_argument("--title", help="标题")
    parser.add_argument("--query", help="搜索关键词")
    parser.add_argument("--limit", type=int, default=10, help="限制数量")

    args = parser.parse_args()

    sync = ObsidianSync(vault_path=args.vault)

    if args.command == "capture":
        if args.content:
            result = sync.quick_capture(args.content, args.title)
            print(f"保存结果: {result}")
        else:
            print("请提供 --content 参数")

    elif args.command == "daily":
        result = sync.create_daily_note()
        print(f"日记创建: {result}")

    elif args.command == "search":
        if args.query:
            result = sync.search_notes(args.query, limit=args.limit)
            print(f"搜索结果: {result}")
        else:
            print("请提供 --query 参数")

    elif args.command == "recent":
        result = sync.get_recent_notes(limit=args.limit)
        for note in result.get('notes', []):
            print(f"{note['modified']} - {note['title']}")

    elif args.command == "help":
        print(sync.get_help())


if __name__ == "__main__":
    main()
