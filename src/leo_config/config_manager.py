# -*- coding: utf-8 -*-
"""
配置管理器 (Config Manager)

集中管理 Leo System 的所有配置，支持：
- YAML 配置文件加载
- 点号分隔键访问 (如 'gateway.port')
- 环境变量覆盖
- 配置热重载
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional, Union

import yaml


class ConfigManager:
    """
    配置管理器 (单例模式)

    用法:
        from leo_config.config_manager import config
        port = config.get("gateway.port", 18789)
    """

    _instance = None
    _config: Dict[str, Any] = {}
    _config_path: Optional[Path] = None

    def __new__(cls, config_path: Optional[Union[str, Path]] = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_config(config_path)
        return cls._instance

    def _init_config(self, config_path: Optional[Union[str, Path]] = None):
        """初始化配置"""
        if config_path is None:
            # 默认配置路径
            self._config_path = Path(__file__).parent / "settings.yaml"
        else:
            self._config_path = Path(config_path)

        self._load_config()
        self._apply_env_overrides()

    def _load_config(self):
        """从 YAML 文件加载配置"""
        if self._config_path.exists():
            try:
                with open(self._config_path, "r", encoding="utf-8") as f:
                    self._config = yaml.safe_load(f) or {}
            except Exception as e:
                print(f"Warning: Failed to load config from {self._config_path}: {e}")
                self._config = {}
        else:
            print(f"Warning: Config file not found: {self._config_path}")
            self._config = {}

    def _apply_env_overrides(self):
        """应用环境变量覆盖"""
        # 支持 LEO_ 前缀的环境变量
        # 例如: LEO_GATEWAY_PORT=8080 会覆盖 gateway.port
        for key, value in os.environ.items():
            if key.startswith("LEO_"):
                config_key = key[4:].lower().replace("_", ".")
                self._set_nested_value(config_key, self._parse_env_value(value))

    def _parse_env_value(self, value: str) -> Any:
        """解析环境变量值"""
        # 尝试转换为数字
        try:
            if "." in value:
                return float(value)
            return int(value)
        except ValueError:
            pass

        # 尝试转换为布尔值
        if value.lower() in ("true", "yes", "1"):
            return True
        if value.lower() in ("false", "no", "0"):
            return False

        # 保持字符串
        return value

    def _set_nested_value(self, key: str, value: Any):
        """设置嵌套值"""
        keys = key.split(".")
        config = self._config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值

        Args:
            key: 配置键，支持点号分隔 (如 'gateway.port')
            default: 默认值

        Returns:
            配置值或默认值
        """
        keys = key.split(".")
        value = self._config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def get_int(self, key: str, default: int = 0) -> int:
        """获取整数配置"""
        value = self.get(key, default)
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    def get_float(self, key: str, default: float = 0.0) -> float:
        """获取浮点数配置"""
        value = self.get(key, default)
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    def get_bool(self, key: str, default: bool = False) -> bool:
        """获取布尔配置"""
        value = self.get(key, default)
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ("true", "yes", "1", "on")
        return bool(value)

    def get_str(self, key: str, default: str = "") -> str:
        """获取字符串配置"""
        value = self.get(key, default)
        return str(value) if value is not None else default

    def get_dict(self, key: str, default: Optional[Dict] = None) -> Dict:
        """获取字典配置"""
        value = self.get(key, default or {})
        if isinstance(value, dict):
            return value
        return default or {}

    def reload(self):
        """重新加载配置"""
        self._load_config()
        self._apply_env_overrides()

    def set(self, key: str, value: Any):
        """
        设置配置值 (运行时，不持久化到文件)

        Args:
            key: 配置键
            value: 配置值
        """
        self._set_nested_value(key, value)

    def dump(self) -> str:
        """导出当前配置为 YAML 字符串"""
        return yaml.dump(self._config, allow_unicode=True, sort_keys=False)


# 全局配置实例
config = ConfigManager()


# 便捷函数
def get_config() -> ConfigManager:
    """获取配置管理器实例"""
    return config


def reload_config():
    """重新加载配置"""
    config.reload()


if __name__ == "__main__":
    # 测试配置加载
    print("=" * 60)
    print("配置管理器测试")
    print("=" * 60)

    print(f"\nGateway 端口: {config.get('gateway.port')}")
    print(f"Session 超时: {config.get('session.timeout')} 秒")
    print(f"SmartRouter 启用: {config.get_bool('gateway.use_smart_router')}")

    print("\n完整配置预览:")
    print(config.dump()[:500] + "...")
