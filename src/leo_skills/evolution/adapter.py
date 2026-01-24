#!/usr/bin/env python3
"""
适配器模块 - 应用优化规则到技能配置
"""

import json
import yaml
import shutil
import logging
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

from .metrics import OptimizationRule

logger = logging.getLogger(__name__)


class SkillAdapter:
    """技能适配器 - 应用优化规则"""

    def __init__(self, skill_name: str, config_path: str):
        self.skill_name = skill_name
        self.config_path = Path(config_path)
        self.snapshots_dir = self.config_path.parent / ".snapshots"
        self.snapshots_dir.mkdir(exist_ok=True)

    def apply_optimizations(self, rules: List[OptimizationRule],
                          auto_apply: bool = False) -> Dict[str, Any]:
        """应用优化规则"""
        if not auto_apply:
            logger.info(f"自动应用已禁用，需要人工审批 {len(rules)} 条规则")
            return {
                'applied': False,
                'reason': 'auto_apply_disabled',
                'pending_rules': [r.to_dict() for r in rules]
            }

        # 创建快照
        snapshot_version = self.create_version_snapshot()

        applied_rules = []
        failed_rules = []

        for rule in rules:
            try:
                if rule.type == "parameter":
                    success = self._adjust_parameter(rule)
                elif rule.type == "config":
                    success = self._update_config(rule)
                else:
                    logger.warning(f"未知规则类型: {rule.type}")
                    success = False

                if success:
                    applied_rules.append(rule.name)
                else:
                    failed_rules.append(rule.name)

            except Exception as e:
                logger.error(f"应用规则 {rule.name} 失败: {e}")
                failed_rules.append(rule.name)

        return {
            'applied': len(applied_rules) > 0,
            'snapshot_version': snapshot_version,
            'applied_rules': applied_rules,
            'failed_rules': failed_rules,
            'total': len(rules)
        }

    def _adjust_parameter(self, rule: OptimizationRule) -> bool:
        """调整配置参数"""
        try:
            # 读取配置文件
            config = self._load_config()

            # 解析参数路径（支持嵌套，如 "content.min_relevance_score"）
            keys = rule.target.split('.')
            current = config

            # 导航到目标位置
            for key in keys[:-1]:
                if key not in current:
                    current[key] = {}
                current = current[key]

            # 记录旧值
            old_value = current.get(keys[-1])

            # 设置新值
            current[keys[-1]] = rule.value

            # 保存配置
            self._save_config(config)

            logger.info(f"参数 {rule.target} 已更新: {old_value} -> {rule.value}")
            return True

        except Exception as e:
            logger.error(f"调整参数失败: {e}")
            return False

    def _update_config(self, rule: OptimizationRule) -> bool:
        """更新配置项"""
        try:
            config = self._load_config()

            if rule.action == "add":
                config[rule.target] = rule.value
            elif rule.action == "remove":
                if rule.target in config:
                    del config[rule.target]
            elif rule.action == "replace":
                config[rule.target] = rule.value

            self._save_config(config)
            logger.info(f"配置 {rule.target} 已{rule.action}: {rule.value}")
            return True

        except Exception as e:
            logger.error(f"更新配置失败: {e}")
            return False

    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if self.config_path.suffix == '.yaml' or self.config_path.suffix == '.yml':
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        elif self.config_path.suffix == '.json':
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            raise ValueError(f"不支持的配置文件格式: {self.config_path.suffix}")

    def _save_config(self, config: Dict[str, Any]):
        """保存配置文件"""
        if self.config_path.suffix == '.yaml' or self.config_path.suffix == '.yml':
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
        elif self.config_path.suffix == '.json':
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

    def create_version_snapshot(self) -> str:
        """创建配置快照"""
        version = datetime.now().strftime('%Y%m%d_%H%M%S')
        snapshot_path = self.snapshots_dir / f"{self.skill_name}_{version}"

        try:
            # 复制配置文件
            shutil.copy2(self.config_path, snapshot_path)
            logger.info(f"已创建快照: {snapshot_path}")
            return version
        except Exception as e:
            logger.error(f"创建快照失败: {e}")
            return ""

    def rollback_to_snapshot(self, version: str) -> bool:
        """回滚到指定快照"""
        snapshot_path = self.snapshots_dir / f"{self.skill_name}_{version}"

        if not snapshot_path.exists():
            logger.error(f"快照不存在: {snapshot_path}")
            return False

        try:
            shutil.copy2(snapshot_path, self.config_path)
            logger.info(f"已回滚到快照: {version}")
            return True
        except Exception as e:
            logger.error(f"回滚失败: {e}")
            return False

    def list_snapshots(self) -> List[Dict[str, Any]]:
        """列出所有快照"""
        snapshots = []
        for snapshot_file in self.snapshots_dir.glob(f"{self.skill_name}_*"):
            version = snapshot_file.name.replace(f"{self.skill_name}_", "")
            snapshots.append({
                'version': version,
                'path': str(snapshot_file),
                'created_at': datetime.fromtimestamp(snapshot_file.stat().st_mtime).isoformat()
            })
        return sorted(snapshots, key=lambda x: x['version'], reverse=True)
