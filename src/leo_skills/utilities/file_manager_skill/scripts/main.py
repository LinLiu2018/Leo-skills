# -*- coding: utf-8 -*-
"""
file_manager_skill - 磁盘清理和文件管理技能 (v2.0)

功能：
1. 大文件扫描 - 查找占用空间大的文件
2. 重复文件查找 - 查找重复文件
3. 临时文件清理 - 清理系统临时文件
4. 空目录清理 - 查找并删除空目录
5. 桌面文件整理 - PARA方法 + 按类型/日期分类
"""

import hashlib
import os
import shutil
import logging
import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class FileInfo:
    """文件信息"""
    path: str
    size: int
    modified: str


@dataclass
class DuplicateGroup:
    """重复文件组"""
    hash: str
    files: List[str]
    size: int
    total_waste: int


@dataclass
class OrganizeRule:
    """整理规则"""
    name: str
    source_ext: List[str]  # 源扩展名
    target_folder: str     # 目标文件夹


# 默认文件类型分类规则
DEFAULT_TYPE_RULES = {
    "图片": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".ico", ".tiff", ".raw", ".psd"],
    "视频": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm", ".m4v", ".mpeg"],
    "音频": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a", ".opus"],
    "文档": [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt", ".md", ".rtf", ".odt"],
    "压缩包": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz"],
    "代码": [".py", ".js", ".ts", ".java", ".cpp", ".c", ".h", ".html", ".css", ".json", ".xml", ".yaml", ".yml", ".go", ".rs", ".php", ".rb", ".swift", ".kt"],
    "数据": [".sql", ".db", ".sqlite", ".csv", ".json", ".xml", ".xlsx"],
    "可执行": [".exe", ".msi", ".dmg", ".app", ".deb", ".rpm", ".apk"],
}

# PARA 方法分类规则
PARA_CATEGORIES = {
    "Projects": "项目 - 正在进行的具体项目",
    "Areas": "领域 - 责任范围",
    "Resources": "资源 - 参考资料",
    "Archive": "归档 - 已完成的项目",
}


class FileManagerSkill:
    """
    file_manager_skill 技能实现 (v2.0)

    提供磁盘清理和文件管理功能：
    - scan_large_files: 扫描大文件
    - find_duplicates: 查找重复文件
    - clean_temp: 清理临时文件
    - clean_empty_dirs: 清理空目录
    - organize_by_type: 按类型整理文件
    - organize_by_date: 按日期整理文件
    - organize_para: PARA方法整理
    - inbox_workflow: 收件箱工作流
    """

    def __init__(self):
        self.name = "file_manager_skill"
        self.version = "2.0.0"
        self.category = "utilities"
        self.type_rules = DEFAULT_TYPE_RULES.copy()

    def execute(self, action: str = "run", **kwargs) -> Dict[str, Any]:
        """
        执行技能

        Args:
            action: 动作名称
            **kwargs: 动作参数

        Returns:
            执行结果字典
        """
        try:
            if action == "run":
                return self._do_execute(**kwargs)
            elif action == "scan_large_files":
                return self._scan_large_files(**kwargs)
            elif action == "find_duplicates":
                return self._find_duplicates(**kwargs)
            elif action == "clean_temp":
                return self._clean_temp(**kwargs)
            elif action == "clean_empty_dirs":
                return self._clean_empty_dirs(**kwargs)
            elif action == "organize_by_type":
                return self._organize_by_type(**kwargs)
            elif action == "organize_by_date":
                return self._organize_by_date(**kwargs)
            elif action == "organize_para":
                return self._organize_para(**kwargs)
            elif action == "inbox_workflow":
                return self._inbox_workflow(**kwargs)
            elif action == "preview_organize":
                return self._preview_organize(**kwargs)
            elif action == "info":
                return self._get_info()
            elif action == "help":
                return self._get_help()
            else:
                return {"status": "error", "error": f"未知动作: {action}"}
        except Exception as e:
            logger.error(f"执行失败: {e}")
            return {"status": "error", "error": str(e)}

    def _do_execute(self, **kwargs) -> Dict[str, Any]:
        """默认执行：显示帮助"""
        return self._get_help()

    def _format_size(self, size: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} PB"

    def _get_file_category(self, ext: str) -> Optional[str]:
        """根据扩展名获取文件类别"""
        ext = ext.lower()
        for category, extensions in self.type_rules.items():
            if ext in extensions:
                return category
        return None

    def _scan_large_files(
        self,
        path: str = ".",
        min_size_mb: int = 100,
        top_n: int = 20,
        extensions: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """扫描大文件"""
        min_size = min_size_mb * 1024 * 1024
        files: List[FileInfo] = []

        scan_path = Path(path)
        if not scan_path.exists():
            return {"status": "error", "error": f"路径不存在: {path}"}

        logger.info(f"扫描大文件: {path}, 最小大小: {self._format_size(min_size)}")

        for root, _, filenames in os.walk(scan_path):
            for filename in filenames:
                filepath = Path(root) / filename
                try:
                    if filepath.is_file():
                        size = filepath.stat().st_size
                        if size >= min_size:
                            if extensions and filepath.suffix.lower() not in extensions:
                                continue
                            mtime = datetime.fromtimestamp(filepath.stat().st_mtime)
                            files.append(FileInfo(
                                path=str(filepath),
                                size=size,
                                modified=mtime.strftime("%Y-%m-%d %H:%M")
                            ))
                except (PermissionError, OSError) as e:
                    logger.warning(f"无法访问: {filepath} - {e}")
                    continue

        files.sort(key=lambda x: x.size, reverse=True)
        files = files[:top_n]
        total_size = sum(f.size for f in files)

        return {
            "status": "success",
            "action": "scan_large_files",
            "scan_path": str(path),
            "min_size_mb": min_size_mb,
            "total_found": len(files),
            "total_size": self._format_size(total_size),
            "files": [
                {
                    "path": f.path,
                    "size": self._format_size(f.size),
                    "size_bytes": f.size,
                    "modified": f.modified
                }
                for f in files
            ]
        }

    def _find_duplicates(
        self,
        path: str = ".",
        min_size_kb: int = 10,
        **kwargs
    ) -> Dict[str, Any]:
        """查找重复文件"""
        min_size = min_size_kb * 1024
        hash_map: Dict[str, List[str]] = {}

        scan_path = Path(path)
        if not scan_path.exists():
            return {"status": "error", "error": f"路径不存在: {path}"}

        size_map: Dict[int, List[Path]] = {}
        for root, _, filenames in os.walk(scan_path):
            for filename in filenames:
                filepath = Path(root) / filename
                try:
                    if filepath.is_file():
                        size = filepath.stat().st_size
                        if size >= min_size:
                            size_map.setdefault(size, []).append(filepath)
                except (PermissionError, OSError):
                    continue

        for size, files in size_map.items():
            if len(files) < 2:
                continue
            for filepath in files:
                try:
                    with open(filepath, 'rb') as f:
                        file_hash = hashlib.md5(f.read()).hexdigest()
                    hash_map.setdefault(file_hash, []).append(str(filepath))
                except (PermissionError, OSError):
                    continue

        duplicates = []
        for file_hash, files in hash_map.items():
            if len(files) > 1:
                size = Path(files[0]).stat().st_size
                duplicates.append(DuplicateGroup(
                    hash=file_hash,
                    files=files,
                    size=size,
                    total_waste=size * (len(files) - 1)
                ))

        duplicates.sort(key=lambda x: x.total_waste, reverse=True)
        total_waste = sum(d.total_waste for d in duplicates)

        return {
            "status": "success",
            "action": "find_duplicates",
            "scan_path": str(path),
            "min_size_kb": min_size_kb,
            "duplicate_groups": len(duplicates),
            "total_waste": self._format_size(total_waste),
            "duplicates": [
                {
                    "hash": d.hash,
                    "count": len(d.files),
                    "size": self._format_size(d.size),
                    "waste": self._format_size(d.total_waste),
                    "files": d.files
                }
                for d in duplicates[:50]
            ]
        }

    def _clean_temp(
        self,
        path: str = None,
        dry_run: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """清理临时文件"""
        temp_patterns = [
            '*.tmp', '*.temp', '*.bak', '*.old',
            '*.log', '*.cache', '*.swp', '*.swo',
            '~*', '.~*', '*.pyc', '__pycache__',
            'node_modules', '.git'
        ]

        if path is None:
            path = os.environ.get('TEMP', '/tmp')

        scan_path = Path(path)
        if not scan_path.exists():
            return {"status": "error", "error": f"路径不存在: {path}"}

        files_to_delete = []
        dirs_to_delete = []
        total_size = 0

        for root, dirs, filenames in os.walk(scan_path):
            for dirname in dirs[:]:
                dirpath = Path(root) / dirname
                if dirname in ['node_modules', '__pycache__', '.git', '.cache']:
                    try:
                        size = sum(f.stat().st_size for f in dirpath.rglob('*') if f.is_file())
                        dirs_to_delete.append((str(dirpath), size))
                        total_size += size
                    except:
                        pass

            for filename in filenames:
                filepath = Path(root) / filename
                should_delete = False
                for pattern in temp_patterns:
                    if '*' in pattern:
                        ext = pattern.replace('*', '')
                        if filename.endswith(ext):
                            should_delete = True
                            break
                    elif filename.startswith(pattern.replace('*', '')):
                        should_delete = True
                        break

                if should_delete:
                    try:
                        size = filepath.stat().st_size
                        files_to_delete.append((str(filepath), size))
                        total_size += size
                    except:
                        pass

        deleted_count = 0
        freed_space = 0

        if not dry_run:
            for filepath, size in files_to_delete:
                try:
                    os.remove(filepath)
                    deleted_count += 1
                    freed_space += size
                except:
                    pass
            for dirpath, size in dirs_to_delete:
                try:
                    shutil.rmtree(dirpath)
                    deleted_count += 1
                    freed_space += size
                except:
                    pass

        return {
            "status": "success",
            "action": "clean_temp",
            "scan_path": str(path),
            "dry_run": dry_run,
            "files_found": len(files_to_delete),
            "dirs_found": len(dirs_to_delete),
            "total_size": self._format_size(total_size),
            "deleted_count": deleted_count,
            "freed_space": self._format_size(freed_space),
            "files_preview": [f[0] for f in files_to_delete[:20]],
            "dirs_preview": [d[0] for d in dirs_to_delete[:10]]
        }

    def _clean_empty_dirs(
        self,
        path: str = ".",
        dry_run: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """清理空目录"""
        scan_path = Path(path)
        if not scan_path.exists():
            return {"status": "error", "error": f"路径不存在: {path}"}

        empty_dirs = []

        for root, dirs, files in os.walk(scan_path, topdown=False):
            for dirname in dirs:
                dirpath = Path(root) / dirname
                try:
                    if not any(dirpath.iterdir()):
                        empty_dirs.append(str(dirpath))
                except:
                    continue

        deleted_count = 0

        if not dry_run:
            for dirpath in empty_dirs:
                try:
                    os.rmdir(dirpath)
                    deleted_count += 1
                except:
                    pass

        return {
            "status": "success",
            "action": "clean_empty_dirs",
            "scan_path": str(path),
            "dry_run": dry_run,
            "empty_dirs_found": len(empty_dirs),
            "deleted_count": deleted_count,
            "empty_dirs": empty_dirs
        }

    def _organize_by_type(
        self,
        path: str = ".",
        dry_run: bool = True,
        create_subdirs: bool = True,
        custom_rules: Optional[Dict[str, List[str]]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        按文件类型整理

        Args:
            path: 整理路径
            dry_run: 模拟运行
            create_subdirs: 是否创建子目录
            custom_rules: 自定义规则
        """
        scan_path = Path(path)
        if not scan_path.exists():
            return {"status": "error", "error": f"路径不存在: {path}"}

        # 合并规则
        rules = self.type_rules.copy()
        if custom_rules:
            rules.update(custom_rules)

        # 统计
        organize_plan: Dict[str, List[Dict]] = {}
        files_moved = 0
        total_size = 0

        for root, dirs, filenames in os.walk(scan_path):
            for filename in filenames:
                filepath = Path(root) / filename
                if not filepath.is_file():
                    continue

                ext = filepath.suffix.lower()
                category = self._get_file_category(ext)

                if category is None:
                    category = "其他"

                # 构建目标路径
                target_dir = scan_path / category if create_subdirs else scan_path
                target_path = target_dir / filename

                # 处理重名
                counter = 1
                original_target = target_path
                while target_path.exists():
                    stem = original_target.stem
                    suffix = original_target.suffix
                    target_path = target_dir / f"{stem}_{counter}{suffix}"
                    counter += 1

                size = filepath.stat().st_size

                if category not in organize_plan:
                    organize_plan[category] = []

                organize_plan[category].append({
                    "source": str(filepath),
                    "target": str(target_path),
                    "size": size
                })

                files_moved += 1
                total_size += size

        # 执行移动
        moved_count = 0
        if not dry_run:
            for category, files in organize_plan.items():
                target_dir = scan_path / category if create_subdirs else scan_path
                target_dir.mkdir(parents=True, exist_ok=True)

                for file_info in files:
                    try:
                        shutil.move(file_info["source"], file_info["target"])
                        moved_count += 1
                    except Exception as e:
                        logger.warning(f"移动失败: {file_info['source']} - {e}")

        return {
            "status": "success",
            "action": "organize_by_type",
            "scan_path": str(path),
            "dry_run": dry_run,
            "files_found": files_moved,
            "files_moved": moved_count if not dry_run else 0,
            "total_size": self._format_size(total_size),
            "categories": {
                cat: len(files) for cat, files in organize_plan.items()
            },
            "plan": organize_plan if dry_run else None,
            "categories_order": list(organize_plan.keys())
        }

    def _organize_by_date(
        self,
        path: str = ".",
        dry_run: bool = True,
        date_format: str = "%Y-%m",  # 年-月
        **kwargs
    ) -> Dict[str, Any]:
        """
        按日期整理文件

        Args:
            path: 整理路径
            dry_run: 模拟运行
            date_format: 日期文件夹格式
        """
        scan_path = Path(path)
        if not scan_path.exists():
            return {"status": "error", "error": f"路径不存在: {path}"}

        organize_plan: Dict[str, List[Dict]] = {}
        files_moved = 0
        total_size = 0

        for root, dirs, filenames in os.walk(scan_path):
            for filename in filenames:
                filepath = Path(root) / filename
                if not filepath.is_file():
                    continue

                try:
                    mtime = datetime.fromtimestamp(filepath.stat().st_mtime)
                    date_folder = mtime.strftime(date_format)
                except:
                    date_folder = "未知"

                target_dir = scan_path / date_folder
                target_path = target_dir / filename

                # 处理重名
                counter = 1
                original_target = target_path
                while target_path.exists():
                    stem = original_target.stem
                    suffix = original_target.suffix
                    target_path = target_dir / f"{stem}_{counter}{suffix}"
                    counter += 1

                size = filepath.stat().st_size

                if date_folder not in organize_plan:
                    organize_plan[date_folder] = []

                organize_plan[date_folder].append({
                    "source": str(filepath),
                    "target": str(target_path),
                    "size": size,
                    "date": mtime.strftime("%Y-%m-%d")
                })

                files_moved += 1
                total_size += size

        # 执行移动
        moved_count = 0
        if not dry_run:
            for date_folder, files in organize_plan.items():
                target_dir = scan_path / date_folder
                target_dir.mkdir(parents=True, exist_ok=True)

                for file_info in files:
                    try:
                        shutil.move(file_info["source"], file_info["target"])
                        moved_count += 1
                    except Exception as e:
                        logger.warning(f"移动失败: {file_info['source']} - {e}")

        return {
            "status": "success",
            "action": "organize_by_date",
            "scan_path": str(path),
            "dry_run": dry_run,
            "date_format": date_format,
            "files_found": files_moved,
            "files_moved": moved_count if not dry_run else 0,
            "total_size": self._format_size(total_size),
            "date_groups": {
                date: len(files) for date, files in organize_plan.items()
            },
            "plan": organize_plan if dry_run else None,
            "dates_order": sorted(organize_plan.keys(), reverse=True)
        }

    def _organize_para(
        self,
        path: str = ".",
        dry_run: bool = True,
        custom_mapping: Optional[Dict[str, List[str]]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        PARA 方法整理文件

        - Projects: 正在进行的项目
        - Areas: 责任领域
        - Resources: 参考资源
        - Archive: 归档内容
        """
        scan_path = Path(path)
        if not scan_path.exists():
            return {"status": "error", "error": f"路径不存在: {path}"}

        # 默认 PARA 映射
        default_mapping = {
            "Projects": [".py", ".js", ".ts", ".java", ".cpp", ".go", ".rs", ".md", ".json", ".yaml"],
            "Areas": [".doc", ".docx", ".xls", ".xlsx", ".pdf", ".ppt", ".pptx"],
            "Resources": [".jpg", ".png", ".gif", ".svg", ".mp4", ".mp3", ".wav"],
            "Archive": [".zip", ".rar", ".7z", ".tar", ".gz", ".bak", ".old", ".tmp"]
        }

        mapping = custom_mapping or default_mapping

        # 构建扩展名到类别的映射
        ext_to_category = {}
        for category, exts in mapping.items():
            for ext in exts:
                ext_to_category[ext.lower()] = category

        organize_plan: Dict[str, List[Dict]] = {cat: [] for cat in PARA_CATEGORIES.keys()}
        organize_plan["其他"] = []

        for root, dirs, filenames in os.walk(scan_path):
            for filename in filenames:
                filepath = Path(root) / filename
                if not filepath.is_file():
                    continue

                ext = filepath.suffix.lower()
                category = ext_to_category.get(ext, "其他")

                target_dir = scan_path / category
                target_path = target_dir / filename

                # 处理重名
                counter = 1
                original_target = target_path
                while target_path.exists():
                    stem = original_target.stem
                    suffix = original_target.suffix
                    target_path = target_dir / f"{stem}_{counter}{suffix}"
                    counter += 1

                size = filepath.stat().st_size

                organize_plan[category].append({
                    "source": str(filepath),
                    "target": str(target_path),
                    "size": size,
                    "type": ext
                })

        # 统计
        total_files = sum(len(files) for files in organize_plan.values())
        total_size = sum(f["size"] for files in organize_plan.values() for f in files)

        # 执行移动
        moved_count = 0
        if not dry_run:
            for category, files in organize_plan.items():
                if category == "其他":
                    continue
                target_dir = scan_path / category
                target_dir.mkdir(parents=True, exist_ok=True)

                for file_info in files:
                    try:
                        shutil.move(file_info["source"], file_info["target"])
                        moved_count += 1
                    except Exception as e:
                        logger.warning(f"移动失败: {file_info['source']} - {e}")

        return {
            "status": "success",
            "action": "organize_para",
            "scan_path": str(path),
            "dry_run": dry_run,
            "description": "PARA方法整理",
            "categories": PARA_CATEGORIES,
            "files_found": total_files,
            "files_moved": moved_count if not dry_run else 0,
            "total_size": self._format_size(total_size),
            "summary": {
                cat: len(files) for cat, files in organize_plan.items()
            },
            "plan": organize_plan if dry_run else None
        }

    def _inbox_workflow(
        self,
        path: str = ".",
        dry_run: bool = True,
        inbox_name: str = "Inbox",
        **kwargs
    ) -> Dict[str, Any]:
        """
        收件箱工作流

        1. 创建 Inbox 文件夹
        2. 将所有文件移动到 Inbox
        3. 用户处理后可以按类型/日期/PARA 再次整理
        """
        scan_path = Path(path)
        if not scan_path.exists():
            return {"status": "error", "error": f"路径不存在: {path}"}

        inbox_dir = scan_path / inbox_name
        inbox_dir.mkdir(parents=True, exist_ok=True)

        files_to_move = []
        total_size = 0

        # 收集根目录下的文件
        for item in scan_path.iterdir():
            if item.is_file() and item.name != ".DS_Store":
                size = item.stat().st_size
                files_to_move.append({
                    "source": str(item),
                    "target": str(inbox_dir / item.name),
                    "size": size
                })
                total_size += size

        # 处理重名
        for file_info in files_to_move:
            target = Path(file_info["target"])
            counter = 1
            while target.exists():
                stem = target.stem
                suffix = target.suffix
                file_info["target"] = str(inbox_dir / f"{stem}_{counter}{suffix}")
                counter += 1
                target = Path(file_info["target"])

        moved_count = 0
        if not dry_run:
            for file_info in files_to_move:
                try:
                    shutil.move(file_info["source"], file_info["target"])
                    moved_count += 1
                except Exception as e:
                    logger.warning(f"移动失败: {file_info['source']} - {e}")

        return {
            "status": "success",
            "action": "inbox_workflow",
            "scan_path": str(path),
            "inbox_path": str(inbox_dir),
            "dry_run": dry_run,
            "files_found": len(files_to_move),
            "files_moved": moved_count if not dry_run else 0,
            "total_size": self._format_size(total_size),
            "next_steps": [
                "organize_by_type: 按类型整理",
                "organize_by_date: 按日期整理",
                "organize_para: PARA方法整理"
            ],
            "files": files_to_move if dry_run else None
        }

    def _preview_organize(
        self,
        path: str = ".",
        mode: str = "type",
        **kwargs
    ) -> Dict[str, Any]:
        """预览整理效果"""
        if mode == "type":
            return self._organize_by_type(path, dry_run=True, **kwargs)
        elif mode == "date":
            return self._organize_by_date(path, dry_run=True, **kwargs)
        elif mode == "para":
            return self._organize_para(path, dry_run=True, **kwargs)
        else:
            return {"status": "error", "error": f"未知模式: {mode}"}

    def _get_info(self) -> Dict[str, Any]:
        """获取技能信息"""
        return {
            "name": self.name,
            "version": self.version,
            "category": self.category,
            "description": "磁盘清理和文件管理 (v2.0 - 增强桌面整理)",
            "actions": [
                "scan_large_files",
                "find_duplicates",
                "clean_temp",
                "clean_empty_dirs",
                "organize_by_type",
                "organize_by_date",
                "organize_para",
                "inbox_workflow",
                "preview_organize",
                "info",
                "help"
            ]
        }

    def _get_help(self) -> Dict[str, Any]:
        """获取帮助信息"""
        return {
            "usage": "execute(action='action_name', **params)",
            "actions": {
                "scan_large_files": {
                    "description": "扫描大文件",
                    "params": {
                        "path": "扫描路径（默认当前目录）",
                        "min_size_mb": "最小文件大小 MB（默认100）",
                        "top_n": "返回文件数量（默认20）"
                    },
                    "example": "execute(action='scan_large_files', path='D:\\\\', min_size_mb=50)"
                },
                "find_duplicates": {
                    "description": "查找重复文件",
                    "params": {
                        "path": "扫描路径",
                        "min_size_kb": "最小文件大小 KB（默认10）"
                    },
                    "example": "execute(action='find_duplicates', path='D:\\\\图片')"
                },
                "clean_temp": {
                    "description": "清理临时文件",
                    "params": {
                        "path": "清理路径（默认系统临时目录）",
                        "dry_run": "模拟运行（默认True）"
                    },
                    "example": "execute(action='clean_temp', path='D:\\\\temp', dry_run=False)"
                },
                "clean_empty_dirs": {
                    "description": "清理空目录",
                    "params": {
                        "path": "扫描路径",
                        "dry_run": "模拟运行（默认True）"
                    },
                    "example": "execute(action='clean_empty_dirs', path='D:\\\\项目')"
                },
                "organize_by_type": {
                    "description": "按文件类型整理（图片/视频/文档等）",
                    "params": {
                        "path": "整理路径",
                        "dry_run": "模拟运行（默认True）",
                        "create_subdirs": "创建子目录（默认True）"
                    },
                    "example": "execute(action='organize_by_type', path='D:\\\\下载', dry_run=False)"
                },
                "organize_by_date": {
                    "description": "按修改日期整理（年-月）",
                    "params": {
                        "path": "整理路径",
                        "dry_run": "模拟运行（默认True）",
                        "date_format": "日期格式（默认%Y-%m）"
                    },
                    "example": "execute(action='organize_by_date', path='D:\\\\整理')"
                },
                "organize_para": {
                    "description": "PARA方法整理（项目/领域/资源/归档）",
                    "params": {
                        "path": "整理路径",
                        "dry_run": "模拟运行（默认True）",
                        "custom_mapping": "自定义扩展名映射"
                    },
                    "example": "execute(action='organize_para', path='D:\\\\资料', dry_run=False)"
                },
                "inbox_workflow": {
                    "description": "收件箱工作流 - 先集中到Inbox",
                    "params": {
                        "path": "整理路径",
                        "dry_run": "模拟运行（默认True）",
                        "inbox_name": "收件箱名称（默认Inbox）"
                    },
                    "example": "execute(action='inbox_workflow', path='D:\\\\桌面')"
                },
                "preview_organize": {
                    "description": "预览整理效果",
                    "params": {
                        "path": "整理路径",
                        "mode": "模式（type/date/para）"
                    },
                    "example": "execute(action='preview_organize', path='D:\\\\下载', mode='type')"
                }
            }
        }


# 全局实例
_skill_instance = None


def get_skill() -> FileManagerSkill:
    """获取技能实例"""
    global _skill_instance
    if _skill_instance is None:
        _skill_instance = FileManagerSkill()
    return _skill_instance


def execute(action: str = "run", **kwargs) -> Dict[str, Any]:
    """便捷执行函数"""
    return get_skill().execute(action, **kwargs)


def get_info() -> Dict[str, Any]:
    """获取技能信息"""
    return get_skill().execute("info")


if __name__ == "__main__":
    skill = get_skill()
    print("=" * 60)
    print(f"技能: {get_info()['name']} v{get_info()['version']}")
    print("=" * 60)

    # 测试预览
    print("\n[预览] 按类型整理:")
    result = execute(action="preview_organize", path=".", mode="type")
    print(f"状态: {result['status']}")
    if result['status'] == 'success':
        print(f"分类: {result.get('categories', {})}")
