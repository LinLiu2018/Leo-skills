"""
Markdown 工具类
处理 Markdown 文件的读写和格式化
"""

import os
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime


class MarkdownUtils:
    """Markdown 工具类"""

    @staticmethod
    def create_frontmatter(data: Dict[str, Any]) -> str:
        """
        创建 YAML frontmatter

        Args:
            data: frontmatter 数据字典

        Returns:
            格式化的 frontmatter 字符串
        """
        lines = ["---"]

        for key, value in data.items():
            if isinstance(value, list):
                lines.append(f"{key}:")
                for item in value:
                    lines.append(f"  - {item}")
            elif isinstance(value, dict):
                lines.append(f"{key}:")
                for k, v in value.items():
                    lines.append(f"  {k}: {v}")
            else:
                # 处理字符串中的特殊字符
                if isinstance(value, str) and (':' in value or '#' in value):
                    value = f'"{value}"'
                lines.append(f"{key}: {value}")

        lines.append("---")
        lines.append("")  # 空行

        return "\n".join(lines)

    @staticmethod
    def parse_frontmatter(content: str) -> tuple[Dict[str, Any], str]:
        """
        解析 frontmatter

        Args:
            content: Markdown 文件内容

        Returns:
            (frontmatter 字典, 正文内容)
        """
        import yaml

        if not content.startswith("---"):
            return {}, content

        # 找到第二个 ---
        parts = content.split("---", 2)
        if len(parts) < 3:
            return {}, content

        try:
            frontmatter = yaml.safe_load(parts[1])
            body = parts[2].strip()
            return frontmatter or {}, body
        except Exception as e:
            print(f"解析 frontmatter 失败：{e}")
            return {}, content

    @staticmethod
    def create_wikilink(text: str, alias: Optional[str] = None) -> str:
        """
        创建 Obsidian wikilink

        Args:
            text: 链接文本
            alias: 别名（可选）

        Returns:
            wikilink 字符串
        """
        if alias:
            return f"[[{text}|{alias}]]"
        return f"[[{text}]]"

    @staticmethod
    def create_tag(tag: str) -> str:
        """
        创建标签

        Args:
            tag: 标签名

        Returns:
            标签字符串
        """
        # 移除特殊字符
        tag = re.sub(r'[^\w\-]', '', tag)
        return f"#{tag}"

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        清理文件名，移除非法字符

        Args:
            filename: 原始文件名

        Returns:
            清理后的文件名
        """
        # 移除或替换非法字符
        filename = re.sub(r'[<>:"/\|?*]', '-', filename)
        # 移除前后空格
        filename = filename.strip()
        # 限制长度
        if len(filename) > 200:
            filename = filename[:200]
        return filename

    @staticmethod
    def ensure_directory(path: Path):
        """
        确保目录存在

        Args:
            path: 目录路径
        """
        path.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def backup_file(file_path: Path):
        """
        备份文件

        Args:
            file_path: 文件路径
        """
        if not file_path.exists():
            return

        backup_dir = file_path.parent / ".backup"
        backup_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
        backup_path = backup_dir / backup_name

        import shutil
        shutil.copy2(file_path, backup_path)
        print(f"已备份文件：{backup_path}")

    @staticmethod
    def read_file(file_path: Path) -> Optional[str]:
        """
        读取文件内容

        Args:
            file_path: 文件路径

        Returns:
            文件内容或 None
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"读取文件失败 ({file_path})：{e}")
            return None

    @staticmethod
    def write_file(file_path: Path, content: str, backup: bool = True):
        """
        写入文件

        Args:
            file_path: 文件路径
            content: 文件内容
            backup: 是否备份
        """
        try:
            # 确保目录存在
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # 备份现有文件
            if backup and file_path.exists():
                MarkdownUtils.backup_file(file_path)

            # 写入文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"已写入文件：{file_path}")

        except Exception as e:
            print(f"写入文件失败 ({file_path})：{e}")
