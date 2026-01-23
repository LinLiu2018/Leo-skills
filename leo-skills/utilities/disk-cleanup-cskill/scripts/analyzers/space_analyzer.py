#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
硬盘空间分析器
Space Analyzer - Analyze disk usage and identify storage issues
"""

import psutil
from pathlib import Path
from typing import Dict, List, Any, Optional
import os


class SpaceAnalyzer:
    """硬盘空间分析器"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.thresholds = config.get("thresholds", {
            "critical": 90,
            "warning": 75,
            "normal": 50
        })

    def analyze(self, drives: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        分析指定驱动器的空间使用情况

        Args:
            drives: 驱动器列表，如 ["C:", "D:"]，None 则分析所有驱动器

        Returns:
            分析结果字典
        """
        if drives is None:
            drives = self._get_all_drives()

        result = {
            "drives": {},
            "summary": {},
            "recommendations": []
        }

        critical_drives = []
        warning_drives = []
        normal_drives = []

        for drive in drives:
            try:
                # 确保驱动器路径格式正确
                drive_path = drive if drive.endswith("\\") else f"{drive}\\"

                usage = psutil.disk_usage(drive_path)

                drive_info = {
                    "total_bytes": usage.total,
                    "used_bytes": usage.used,
                    "free_bytes": usage.free,
                    "usage_percent": round(usage.percent, 2),
                    "total_gb": round(usage.total / (1024**3), 2),
                    "used_gb": round(usage.used / (1024**3), 2),
                    "free_gb": round(usage.free / (1024**3), 2),
                    "status": self._get_drive_status(usage.percent)
                }

                result["drives"][drive] = drive_info

                # 分类驱动器状态
                if usage.percent >= self.thresholds["critical"]:
                    critical_drives.append(drive)
                elif usage.percent >= self.thresholds["warning"]:
                    warning_drives.append(drive)
                else:
                    normal_drives.append(drive)

            except Exception as e:
                result["drives"][drive] = {
                    "error": str(e),
                    "status": "error"
                }

        # 生成摘要
        result["summary"] = {
            "total_drives": len(drives),
            "critical_drives": critical_drives,
            "warning_drives": warning_drives,
            "normal_drives": normal_drives,
            "overall_status": self._get_overall_status(critical_drives, warning_drives)
        }

        # 生成建议
        result["recommendations"] = self._generate_recommendations(result["drives"])

        return result

    def _get_all_drives(self) -> List[str]:
        """获取所有可用的驱动器"""
        drives = []
        for partition in psutil.disk_partitions():
            # 只包含固定磁盘（排除光驱、网络驱动器等）
            if 'fixed' in partition.opts.lower() or partition.fstype:
                drives.append(partition.device.rstrip("\\"))
        return drives

    def _get_drive_status(self, usage_percent: float) -> str:
        """根据使用率获取驱动器状态"""
        if usage_percent >= self.thresholds["critical"]:
            return "critical"
        elif usage_percent >= self.thresholds["warning"]:
            return "warning"
        else:
            return "normal"

    def _get_overall_status(self, critical_drives: List[str], warning_drives: List[str]) -> str:
        """获取整体状态"""
        if critical_drives:
            return "critical"
        elif warning_drives:
            return "warning"
        else:
            return "normal"

    def _generate_recommendations(self, drives_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成清理建议"""
        recommendations = []

        for drive, info in drives_info.items():
            if "error" in info:
                continue

            usage_percent = info.get("usage_percent", 0)
            free_gb = info.get("free_gb", 0)

            if usage_percent >= self.thresholds["critical"]:
                recommendations.append({
                    "priority": "high",
                    "drive": drive,
                    "message": f"{drive} 使用率 {usage_percent}%，剩余空间仅 {free_gb}GB，建议立即清理",
                    "actions": [
                        "clean_temp",
                        "scan_large_files",
                        "find_duplicates",
                        "clean_recycle_bin"
                    ],
                    "estimated_recoverable_gb": self._estimate_recoverable_space(drive)
                })
            elif usage_percent >= self.thresholds["warning"]:
                recommendations.append({
                    "priority": "medium",
                    "drive": drive,
                    "message": f"{drive} 使用率 {usage_percent}%，剩余空间 {free_gb}GB，建议定期清理",
                    "actions": [
                        "clean_temp",
                        "clean_browser_cache"
                    ],
                    "estimated_recoverable_gb": self._estimate_recoverable_space(drive)
                })

        return recommendations

    def _estimate_recoverable_space(self, drive: str) -> float:
        """估算可回收空间（GB）"""
        # 简单估算：临时文件通常占用1-5GB
        # 实际实现中可以扫描临时目录获取准确值
        return 2.5

    def get_directory_size(self, path: str) -> int:
        """
        获取目录大小（递归）

        Args:
            path: 目录路径

        Returns:
            目录大小（字节）
        """
        total = 0
        try:
            for entry in Path(path).rglob('*'):
                if entry.is_file():
                    try:
                        total += entry.stat().st_size
                    except (PermissionError, OSError):
                        pass
        except (PermissionError, OSError):
            pass
        return total

    def analyze_top_directories(self, drive: str, top_n: int = 10) -> List[Dict[str, Any]]:
        """
        分析占用空间最大的目录

        Args:
            drive: 驱动器路径
            top_n: 返回前N个最大目录

        Returns:
            目录列表，按大小排序
        """
        drive_path = drive if drive.endswith("\\") else f"{drive}\\"
        directories = []

        try:
            # 扫描根目录下的一级子目录
            for entry in os.scandir(drive_path):
                if entry.is_dir():
                    try:
                        size = self.get_directory_size(entry.path)
                        directories.append({
                            "path": entry.path,
                            "name": entry.name,
                            "size_bytes": size,
                            "size_gb": round(size / (1024**3), 2)
                        })
                    except (PermissionError, OSError):
                        pass
        except (PermissionError, OSError):
            pass

        # 按大小排序
        directories.sort(key=lambda x: x["size_bytes"], reverse=True)

        return directories[:top_n]

    def format_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"

    def get_drive_info(self, drive: str) -> Dict[str, Any]:
        """获取单个驱动器的详细信息"""
        try:
            drive_path = drive if drive.endswith("\\") else f"{drive}\\"
            usage = psutil.disk_usage(drive_path)

            # 获取分区信息
            partition_info = None
            for partition in psutil.disk_partitions():
                if partition.device.rstrip("\\") == drive:
                    partition_info = partition
                    break

            return {
                "drive": drive,
                "total": self.format_size(usage.total),
                "used": self.format_size(usage.used),
                "free": self.format_size(usage.free),
                "percent": usage.percent,
                "filesystem": partition_info.fstype if partition_info else "Unknown",
                "mount_point": partition_info.mountpoint if partition_info else drive,
                "status": self._get_drive_status(usage.percent)
            }
        except Exception as e:
            return {
                "drive": drive,
                "error": str(e)
            }
