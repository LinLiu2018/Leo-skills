#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
硬盘清理技能 - 主类
Disk Cleanup Skill - Main Class
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import sys
import yaml

# 导入子模块
sys.path.insert(0, str(Path(__file__).parent))
from analyzers.space_analyzer import SpaceAnalyzer
from cleaners.temp_cleaner import TempCleaner
from safety.safety_checker import SafetyChecker


class DiskCleanupSkill:
    """
    硬盘清理技能 - Windows 磁盘空间管理和优化

    功能：
    - 硬盘空间分析
    - 临时文件清理
    - 大文件扫描
    - 重复文件检测
    - 回收站清理
    - 系统日志清理
    - 安全性保障
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        初始化技能

        Args:
            config_path: 配置文件路径，None 则使用默认路径
        """
        self.skill_name = "disk-cleanup-cskill"
        self.version = "1.0.0"

        # 加载配置
        if config_path is None:
            config_path = str(Path(__file__).parent.parent / "config" / "config.yaml")

        self.config = self._load_config(config_path)

        # 初始化子模块
        self.space_analyzer = SpaceAnalyzer(self.config)
        self.temp_cleaner = TempCleaner(self.config)
        self.safety_checker = SafetyChecker(self.config)

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"警告: 无法加载配置文件 {config_path}: {e}")
            return {}

    def execute(self, action: str = "analyze", **kwargs) -> Dict[str, Any]:
        """
        执行技能操作

        Args:
            action: 操作类型
            **kwargs: 操作参数

        Returns:
            执行结果
        """
        # 路由到对应的功能模块
        action_map = {
            "analyze_space": self.analyze_disk_space,
            "scan_large_files": self.scan_large_files,
            "find_duplicates": self.find_duplicate_files,
            "clean_temp": self.clean_temp_files,
            "clean_recycle_bin": self.clean_recycle_bin,
            "clean_logs": self.clean_system_logs,
            "full_cleanup": self.full_cleanup,
            "get_recommendations": self.get_cleanup_recommendations,
            "get_temp_size": self.get_temp_size
        }

        handler = action_map.get(action)
        if not handler:
            return {
                "success": False,
                "error": f"Unknown action: {action}",
                "available_actions": list(action_map.keys())
            }

        try:
            result = handler(**kwargs)
            return {
                "success": True,
                "action": action,
                "data": result,
                "skill": self.skill_name,
                "version": self.version
            }
        except Exception as e:
            return {
                "success": False,
                "action": action,
                "error": str(e),
                "skill": self.skill_name
            }

    def analyze_disk_space(self, drives: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        分析硬盘空间使用情况

        Args:
            drives: 驱动器列表，如 ["C:", "D:"]

        Returns:
            分析结果
        """
        return self.space_analyzer.analyze(drives)

    def scan_large_files(self,
                        drive: str = "C:",
                        min_size_mb: int = 100,
                        max_results: int = 50) -> Dict[str, Any]:
        """
        扫描大文件

        Args:
            drive: 驱动器
            min_size_mb: 最小文件大小（MB）
            max_results: 最大结果数

        Returns:
            大文件列表
        """
        # 简化实现：返回占用空间最大的目录
        return self.space_analyzer.analyze_top_directories(drive, max_results)

    def find_duplicate_files(self,
                            paths: List[str],
                            min_size_mb: int = 1) -> Dict[str, Any]:
        """
        查找重复文件

        Args:
            paths: 搜索路径列表
            min_size_mb: 最小文件大小（MB）

        Returns:
            重复文件列表
        """
        # 简化实现：返回提示信息
        return {
            "message": "重复文件检测功能开发中",
            "paths": paths,
            "min_size_mb": min_size_mb
        }

    def clean_temp_files(self,
                        dry_run: bool = True,
                        confirm: bool = True) -> Dict[str, Any]:
        """
        清理临时文件

        Args:
            dry_run: 仅模拟，不实际删除
            confirm: 是否需要用户确认

        Returns:
            清理结果
        """
        # 安全检查
        if not dry_run:
            # 如果不需要用户确认，则认为已经确认
            confirmed = not confirm
            if not self.safety_checker.verify_operation("clean_temp", dry_run=dry_run, confirmed=confirmed):
                return {
                    "success": False,
                    "error": "Safety check failed"
                }

        return self.temp_cleaner.clean(dry_run=dry_run, confirm=confirm)

    def clean_recycle_bin(self,
                         dry_run: bool = True,
                         confirm: bool = True) -> Dict[str, Any]:
        """
        清空回收站

        Args:
            dry_run: 仅模拟，不实际删除
            confirm: 是否需要用户确认

        Returns:
            清理结果
        """
        if not dry_run:
            if not self.safety_checker.verify_operation("clean_recycle_bin", dry_run=dry_run):
                return {
                    "success": False,
                    "error": "Safety check failed"
                }

        # 简化实现
        return {
            "message": "回收站清理功能开发中",
            "dry_run": dry_run
        }

    def clean_system_logs(self,
                         dry_run: bool = True,
                         confirm: bool = True) -> Dict[str, Any]:
        """
        清理系统日志

        Args:
            dry_run: 仅模拟，不实际删除
            confirm: 是否需要用户确认

        Returns:
            清理结果
        """
        if not dry_run:
            if not self.safety_checker.verify_operation("clean_logs", dry_run=dry_run):
                return {
                    "success": False,
                    "error": "Safety check failed"
                }

        # 简化实现
        return {
            "message": "系统日志清理功能开发中",
            "dry_run": dry_run
        }

    def full_cleanup(self,
                    profile: str = "standard",
                    dry_run: bool = True) -> Dict[str, Any]:
        """
        完整清理流程

        Args:
            profile: 清理配置（conservative, standard, aggressive）
            dry_run: 是否为 dry-run 模式

        Returns:
            清理结果
        """
        results = {
            "profile": profile,
            "dry_run": dry_run,
            "operations": []
        }

        # 1. 分析当前状态
        print("📊 分析磁盘空间...")
        analysis = self.analyze_disk_space()
        results["initial_state"] = analysis

        # 2. 根据配置文件执行清理
        profile_config = self.config.get("cleanup_profiles", {}).get(profile, {})

        if profile_config.get("clean_temp", True):
            print("\n🧹 清理临时文件...")
            temp_result = self.clean_temp_files(dry_run=dry_run, confirm=False)
            results["operations"].append({
                "type": "temp",
                "result": temp_result
            })

        if profile_config.get("clean_browser_cache", False):
            print("\n🌐 清理浏览器缓存...")
            browser_result = self.temp_cleaner.clean_browser_cache(dry_run=dry_run)
            results["operations"].append({
                "type": "browser_cache",
                "result": browser_result
            })

        if profile_config.get("clean_recycle_bin", False):
            print("\n🗑️  清空回收站...")
            recycle_result = self.clean_recycle_bin(dry_run=dry_run, confirm=False)
            results["operations"].append({
                "type": "recycle_bin",
                "result": recycle_result
            })

        if profile_config.get("clean_logs", False):
            print("\n📝 清理系统日志...")
            log_result = self.clean_system_logs(dry_run=dry_run, confirm=False)
            results["operations"].append({
                "type": "logs",
                "result": log_result
            })

        # 3. 再次分析
        if not dry_run:
            print("\n📊 重新分析磁盘空间...")
            final_analysis = self.analyze_disk_space()
            results["final_state"] = final_analysis
            results["space_freed"] = self._calculate_space_freed(
                analysis, final_analysis
            )

        return results

    def get_cleanup_recommendations(self) -> Dict[str, Any]:
        """
        获取清理建议

        Returns:
            清理建议
        """
        analysis = self.analyze_disk_space()
        return {
            "analysis": analysis,
            "recommendations": analysis.get("recommendations", []),
            "estimated_recoverable": self._estimate_total_recoverable_space()
        }

    def get_temp_size(self) -> Dict[str, Any]:
        """
        获取临时文件总大小

        Returns:
            临时文件大小统计
        """
        return self.temp_cleaner.get_temp_size()

    def _calculate_space_freed(self, before: Dict, after: Dict) -> Dict[str, int]:
        """计算释放的空间"""
        freed = {}
        before_drives = before.get("drives", {})
        after_drives = after.get("drives", {})

        for drive in before_drives:
            if drive in after_drives:
                before_free = before_drives[drive].get("free_bytes", 0)
                after_free = after_drives[drive].get("free_bytes", 0)
                freed[drive] = after_free - before_free

        return freed

    def _estimate_total_recoverable_space(self) -> Dict[str, Any]:
        """估算总可回收空间"""
        temp_size = self.temp_cleaner.get_temp_size()

        return {
            "temp_files_gb": temp_size.get("total_size_gb", 0),
            "total_estimated_gb": temp_size.get("total_size_gb", 0),
            "breakdown": {
                "temp_files": temp_size.get("total_size_gb", 0),
                "browser_cache": 0.5,  # 估算
                "recycle_bin": 1.0,  # 估算
                "logs": 0.2  # 估算
            }
        }

    def get_status(self) -> Dict[str, Any]:
        """获取技能状态"""
        return {
            "skill_name": self.skill_name,
            "version": self.version,
            "status": "active",
            "modules": {
                "space_analyzer": "active",
                "temp_cleaner": "active",
                "safety_checker": "active"
            },
            "config_loaded": bool(self.config)
        }


# 兼容旧接口的函数
def analyze_disk_space(drives: Optional[List[str]] = None) -> Dict[str, Any]:
    """分析磁盘空间（兼容函数）"""
    skill = DiskCleanupSkill()
    return skill.analyze_disk_space(drives)


def clean_temp_files(dry_run: bool = True) -> Dict[str, Any]:
    """清理临时文件（兼容函数）"""
    skill = DiskCleanupSkill()
    return skill.clean_temp_files(dry_run=dry_run)


def full_cleanup(profile: str = "standard", dry_run: bool = True) -> Dict[str, Any]:
    """完整清理（兼容函数）"""
    skill = DiskCleanupSkill()
    return skill.full_cleanup(profile=profile, dry_run=dry_run)
