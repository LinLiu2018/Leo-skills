#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安全检查器
Safety Checker - Prevent accidental deletion of critical files
"""

from pathlib import Path
from typing import Dict, List, Any, Set
import yaml
import os
import fnmatch


class SafetyChecker:
    """安全检查器 - 防止误删系统关键文件"""

    # 系统关键目录（绝对不能删除）
    CRITICAL_PATHS = {
        "C:\\Windows\\System32",
        "C:\\Windows\\SysWOW64",
        "C:\\Windows\\WinSxS",
        "C:\\Windows\\Boot",
        "C:\\Windows\\Fonts",
        "C:\\Program Files",
        "C:\\Program Files (x86)",
        "C:\\ProgramData\\Microsoft",
        "C:\\Users\\Default",
    }

    # 受保护的文件扩展名
    PROTECTED_EXTENSIONS = {
        ".sys", ".dll", ".exe", ".ini", ".reg",
        ".bat", ".cmd", ".ps1", ".vbs", ".drv",
        ".ocx", ".cpl", ".scr"
    }

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.safety_config = config.get("safety", {})
        self.load_safety_rules()

    def load_safety_rules(self):
        """加载安全规则配置"""
        safety_config_path = Path(__file__).parent.parent.parent / "config" / "safety_rules.yaml"

        if safety_config_path.exists():
            with open(safety_config_path, 'r', encoding='utf-8') as f:
                rules = yaml.safe_load(f)
                self.whitelist = set(rules.get("whitelist", []))
                self.blacklist = set(rules.get("blacklist", []))
                self.protected_file_types = rules.get("protected_file_types", {})
                self.safety_rules = rules.get("safety_rules", {})
        else:
            self.whitelist = set()
            self.blacklist = set()
            self.protected_file_types = {}
            self.safety_rules = {}

    def verify_operation(self, operation: str, **kwargs) -> bool:
        """
        验证操作是否安全

        Args:
            operation: 操作类型（clean_temp, clean_recycle_bin等）
            **kwargs: 操作参数

        Returns:
            True 如果操作安全，False 否则
        """
        # 检查操作类型
        if operation in ["analyze_space", "scan_large_files", "find_duplicates"]:
            # 只读操作，总是安全的
            return True

        # 检查是否启用 dry-run
        if kwargs.get("dry_run", True):
            # Dry-run 模式总是安全的
            return True

        # 检查是否需要确认
        if self.safety_config.get("confirm_before_delete", True):
            if not kwargs.get("confirmed", False):
                return False

        return True

    def is_safe_to_delete(self, file_path: str) -> bool:
        """
        检查文件是否可以安全删除

        Args:
            file_path: 文件路径

        Returns:
            True 如果可以安全删除，False 否则
        """
        path = Path(file_path)

        # 检查是否在关键路径中
        for critical_path in self.CRITICAL_PATHS:
            if self._is_subpath(file_path, critical_path):
                return False

        # 检查黑名单（支持通配符）
        for blacklist_pattern in self.blacklist:
            if self._match_path_pattern(file_path, blacklist_pattern):
                return False

        # 检查白名单（白名单优先）
        for whitelist_pattern in self.whitelist:
            if self._match_path_pattern(file_path, whitelist_pattern):
                return True

        # 检查扩展名
        if path.suffix.lower() in self.PROTECTED_EXTENSIONS:
            return False

        # 检查文件大小限制
        try:
            file_size_mb = path.stat().st_size / (1024 * 1024)
            max_size_mb = self.safety_rules.get("max_single_file_size_mb", 1024)
            if file_size_mb > max_size_mb:
                # 超大文件需要额外确认
                return False
        except (OSError, FileNotFoundError):
            pass

        # 检查文件年龄
        try:
            import time
            file_age_days = (time.time() - path.stat().st_mtime) / (24 * 3600)
            min_age_days = self.safety_rules.get("min_file_age_days", 7)
            if file_age_days < min_age_days:
                # 太新的文件不删除
                return False
        except (OSError, FileNotFoundError):
            pass

        return True

    def _is_subpath(self, path: str, parent: str) -> bool:
        """检查路径是否是父路径的子路径"""
        try:
            path_obj = Path(path).resolve()
            parent_obj = Path(parent).resolve()
            return str(path_obj).lower().startswith(str(parent_obj).lower())
        except Exception:
            return False

    def _match_path_pattern(self, path: str, pattern: str) -> bool:
        """
        匹配路径模式（支持通配符）

        Args:
            path: 文件路径
            pattern: 模式（支持 * 通配符）

        Returns:
            True 如果匹配，False 否则
        """
        # 标准化路径
        path = path.replace("/", "\\").lower()
        pattern = pattern.replace("/", "\\").lower()

        # 使用 fnmatch 进行模式匹配
        return fnmatch.fnmatch(path, pattern)

    def get_confirmation(self, operation: str, details: Dict) -> bool:
        """
        获取用户确认

        Args:
            operation: 操作类型
            details: 操作详情

        Returns:
            True 如果用户确认，False 否则
        """
        print(f"\n⚠️  即将执行操作: {operation}")
        print(f"详情:")
        for key, value in details.items():
            print(f"  {key}: {value}")

        response = input("\n确认执行？(yes/no): ").strip().lower()
        return response in ["yes", "y", "是", "确认"]

    def validate_batch_operation(self, files: List[str], total_size_bytes: int) -> Dict[str, Any]:
        """
        验证批量操作

        Args:
            files: 文件列表
            total_size_bytes: 总大小（字节）

        Returns:
            验证结果
        """
        result = {
            "valid": True,
            "warnings": [],
            "errors": []
        }

        # 检查文件数量
        max_files = self.safety_rules.get("max_files_per_batch", 10000)
        if len(files) > max_files:
            result["valid"] = False
            result["errors"].append(f"文件数量 ({len(files)}) 超过限制 ({max_files})")

        # 检查总大小
        total_size_gb = total_size_bytes / (1024**3)
        max_size_gb = self.safety_rules.get("max_total_size_gb", 50)
        if total_size_gb > max_size_gb:
            result["valid"] = False
            result["errors"].append(f"总大小 ({total_size_gb:.2f}GB) 超过限制 ({max_size_gb}GB)")

        # 检查是否包含受保护的文件
        protected_files = []
        for file_path in files:
            if not self.is_safe_to_delete(file_path):
                protected_files.append(file_path)

        if protected_files:
            result["warnings"].append(f"包含 {len(protected_files)} 个受保护的文件")
            result["protected_files"] = protected_files[:10]  # 只显示前10个

        return result

    def check_file_in_use(self, file_path: str) -> bool:
        """
        检查文件是否正在被使用

        Args:
            file_path: 文件路径

        Returns:
            True 如果文件正在被使用，False 否则
        """
        try:
            # 尝试以独占模式打开文件
            with open(file_path, 'a'):
                pass
            return False
        except (PermissionError, OSError):
            return True

    def get_safe_temp_locations(self) -> List[str]:
        """获取安全的临时文件位置"""
        safe_locations = []

        # 从白名单中提取临时文件位置
        for pattern in self.whitelist:
            # 展开环境变量
            expanded = os.path.expandvars(pattern)
            if os.path.exists(expanded):
                safe_locations.append(expanded)

        return safe_locations

    def create_backup_list(self, files: List[str]) -> Dict[str, Any]:
        """
        创建备份列表

        Args:
            files: 要删除的文件列表

        Returns:
            备份信息
        """
        import time
        timestamp = time.strftime("%Y%m%d_%H%M%S")

        backup_info = {
            "timestamp": timestamp,
            "files": files,
            "total_files": len(files),
            "total_size_bytes": sum(Path(f).stat().st_size for f in files if Path(f).exists()),
            "backup_location": f"outputs/backups/backup_{timestamp}.json"
        }

        return backup_info

    def log_operation(self, operation: str, details: Dict[str, Any]):
        """
        记录操作日志

        Args:
            operation: 操作类型
            details: 操作详情
        """
        import json
        import time

        log_entry = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "operation": operation,
            "details": details
        }

        log_file = Path(__file__).parent.parent.parent / "outputs" / "operation_log.json"
        log_file.parent.mkdir(parents=True, exist_ok=True)

        # 追加日志
        logs = []
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                try:
                    logs = json.load(f)
                except json.JSONDecodeError:
                    logs = []

        logs.append(log_entry)

        # 保留最近1000条日志
        logs = logs[-1000:]

        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)
