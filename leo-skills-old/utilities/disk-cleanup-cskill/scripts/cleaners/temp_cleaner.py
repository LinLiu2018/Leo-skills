#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
临时文件清理器
Temp Cleaner - Clean temporary files safely
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Any
import send2trash
import time


class TempCleaner:
    """临时文件清理器"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.temp_config = config.get("temp_cleanup", {})
        self.safety_config = config.get("safety", {})
        self.temp_locations = self._get_temp_locations()

    def _get_temp_locations(self) -> List[str]:
        """获取临时文件位置"""
        locations = []

        # 从配置中获取位置
        config_locations = self.temp_config.get("locations", [])
        for location in config_locations:
            # 展开环境变量
            expanded = os.path.expandvars(location)
            if os.path.exists(expanded):
                locations.append(expanded)

        # 添加浏览器缓存路径
        browser_cache = self.temp_config.get("browser_cache_paths", {})
        for browser, path_pattern in browser_cache.items():
            expanded = os.path.expandvars(path_pattern)
            # 处理通配符路径（如 Firefox profiles）
            if "*" in expanded:
                parent = Path(expanded).parent
                if parent.exists():
                    pattern = Path(expanded).name
                    for item in parent.glob(pattern):
                        if item.is_dir():
                            locations.append(str(item))
            elif os.path.exists(expanded):
                locations.append(expanded)

        # Windows Update 缓存
        windows_update = self.temp_config.get("windows_update_cache")
        if windows_update and os.path.exists(windows_update):
            locations.append(windows_update)

        return locations

    def clean(self, dry_run: bool = True, confirm: bool = True) -> Dict[str, Any]:
        """
        清理临时文件

        Args:
            dry_run: 仅模拟，不实际删除
            confirm: 是否需要用户确认

        Returns:
            清理结果统计
        """
        result = {
            "dry_run": dry_run,
            "files_found": 0,
            "files_deleted": 0,
            "files_skipped": 0,
            "space_freed_bytes": 0,
            "errors": [],
            "locations": []
        }

        # 如果需要确认且不是 dry-run
        if confirm and not dry_run:
            print(f"\n将清理以下位置的临时文件:")
            for loc in self.temp_locations:
                print(f"  - {loc}")
            response = input("\n确认继续？(yes/no): ").strip().lower()
            if response not in ["yes", "y", "是", "确认"]:
                result["cancelled"] = True
                return result

        for location in self.temp_locations:
            if not os.path.exists(location):
                continue

            location_result = self._clean_location(location, dry_run)
            result["files_found"] += location_result["files_found"]
            result["files_deleted"] += location_result["files_deleted"]
            result["files_skipped"] += location_result["files_skipped"]
            result["space_freed_bytes"] += location_result["space_freed"]
            result["errors"].extend(location_result["errors"])
            result["locations"].append({
                "path": location,
                "files_found": location_result["files_found"],
                "files_deleted": location_result["files_deleted"],
                "space_freed_mb": round(location_result["space_freed"] / (1024**2), 2)
            })

        result["space_freed_gb"] = round(result["space_freed_bytes"] / (1024**3), 2)
        result["space_freed_mb"] = round(result["space_freed_bytes"] / (1024**2), 2)

        return result

    def _clean_location(self, location: str, dry_run: bool) -> Dict[str, Any]:
        """清理单个位置"""
        result = {
            "files_found": 0,
            "files_deleted": 0,
            "files_skipped": 0,
            "space_freed": 0,
            "errors": []
        }

        max_file_age_days = self.temp_config.get("max_file_age_days", 30)
        current_time = time.time()

        try:
            for root, dirs, files in os.walk(location):
                for file in files:
                    file_path = os.path.join(root, file)

                    try:
                        # 检查文件年龄
                        file_mtime = os.path.getmtime(file_path)
                        file_age_days = (current_time - file_mtime) / (24 * 3600)

                        # 只处理超过指定天数的文件
                        if file_age_days < max_file_age_days:
                            result["files_skipped"] += 1
                            continue

                        # 安全检查
                        if not self._is_safe_to_delete(file_path):
                            result["files_skipped"] += 1
                            continue

                        file_size = os.path.getsize(file_path)
                        result["files_found"] += 1

                        if not dry_run:
                            # 使用 send2trash 而非直接删除（更安全）
                            if self.safety_config.get("use_send2trash", True):
                                send2trash.send2trash(file_path)
                            else:
                                os.remove(file_path)

                            result["files_deleted"] += 1
                            result["space_freed"] += file_size
                        else:
                            # Dry-run 模式：只统计
                            result["space_freed"] += file_size

                    except Exception as e:
                        result["errors"].append({
                            "file": file_path,
                            "error": str(e)
                        })

        except Exception as e:
            result["errors"].append({
                "location": location,
                "error": str(e)
            })

        return result

    def _is_safe_to_delete(self, file_path: str) -> bool:
        """检查文件是否可以安全删除"""
        path = Path(file_path)

        # 检查文件扩展名
        protected_extensions = self.safety_config.get("protected_extensions", [])
        if path.suffix.lower() in protected_extensions:
            return False

        # 检查文件是否被占用
        try:
            with open(file_path, 'a'):
                pass
            return True
        except (PermissionError, OSError):
            return False

    def get_temp_size(self) -> Dict[str, Any]:
        """获取临时文件总大小"""
        total_size = 0
        total_files = 0
        location_sizes = {}

        for location in self.temp_locations:
            if not os.path.exists(location):
                continue

            location_size = 0
            location_files = 0

            try:
                for root, dirs, files in os.walk(location):
                    for file in files:
                        try:
                            file_path = os.path.join(root, file)
                            file_size = os.path.getsize(file_path)
                            location_size += file_size
                            location_files += 1
                        except (OSError, PermissionError):
                            pass
            except (OSError, PermissionError):
                pass

            location_sizes[location] = {
                "size_bytes": location_size,
                "size_mb": round(location_size / (1024**2), 2),
                "size_gb": round(location_size / (1024**3), 2),
                "files": location_files
            }

            total_size += location_size
            total_files += location_files

        return {
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024**2), 2),
            "total_size_gb": round(total_size / (1024**3), 2),
            "total_files": total_files,
            "locations": location_sizes
        }

    def clean_browser_cache(self, browser: str = "all", dry_run: bool = True) -> Dict[str, Any]:
        """
        清理浏览器缓存

        Args:
            browser: 浏览器名称（chrome, edge, firefox, all）
            dry_run: 是否为 dry-run 模式

        Returns:
            清理结果
        """
        result = {
            "browser": browser,
            "dry_run": dry_run,
            "cleaned": []
        }

        browser_cache = self.temp_config.get("browser_cache_paths", {})

        if browser == "all":
            browsers_to_clean = browser_cache.keys()
        else:
            browsers_to_clean = [browser] if browser in browser_cache else []

        for browser_name in browsers_to_clean:
            cache_path = os.path.expandvars(browser_cache[browser_name])

            if "*" in cache_path:
                # 处理通配符路径
                parent = Path(cache_path).parent
                if parent.exists():
                    pattern = Path(cache_path).name
                    for item in parent.glob(pattern):
                        if item.is_dir():
                            clean_result = self._clean_location(str(item), dry_run)
                            result["cleaned"].append({
                                "browser": browser_name,
                                "path": str(item),
                                "result": clean_result
                            })
            elif os.path.exists(cache_path):
                clean_result = self._clean_location(cache_path, dry_run)
                result["cleaned"].append({
                    "browser": browser_name,
                    "path": cache_path,
                    "result": clean_result
                })

        return result

    def clean_windows_update_cache(self, dry_run: bool = True) -> Dict[str, Any]:
        """
        清理 Windows Update 缓存

        Args:
            dry_run: 是否为 dry-run 模式

        Returns:
            清理结果
        """
        windows_update_path = self.temp_config.get("windows_update_cache")

        if not windows_update_path or not os.path.exists(windows_update_path):
            return {
                "success": False,
                "error": "Windows Update cache path not found"
            }

        result = self._clean_location(windows_update_path, dry_run)

        return {
            "success": True,
            "path": windows_update_path,
            "files_deleted": result["files_deleted"],
            "space_freed_mb": round(result["space_freed"] / (1024**2), 2)
        }
