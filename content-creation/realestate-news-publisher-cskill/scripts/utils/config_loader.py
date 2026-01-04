# Configuration Loader Module
# 配置加载模块

import os
import yaml
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv


class ConfigLoader:
    """加载和管理配置文件"""

    def __init__(self, config_dir: str = None):
        """
        初始化配置加载器

        Args:
            config_dir: 配置文件目录路径
        """
        if config_dir is None:
            # 默认配置目录
            current_dir = Path(__file__).parent.parent.parent
            config_dir = current_dir / "config"

        self.config_dir = Path(config_dir)
        self.config = {}
        self.sources = {}
        self.keywords = {}

        # 加载环境变量
        load_dotenv()

        # 加载所有配置
        self._load_all_configs()

    def _load_yaml(self, file_path: Path) -> Dict[str, Any]:
        """加载 YAML 文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            print(f"警告: 配置文件不存在: {file_path}")
            return {}
        except yaml.YAMLError as e:
            print(f"错误: YAML 解析失败 {file_path}: {e}")
            return {}

    def _substitute_env_vars(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """替换环境变量"""
        if isinstance(config, dict):
            return {k: self._substitute_env_vars(v) for k, v in config.items()}
        elif isinstance(config, list):
            return [self._substitute_env_vars(item) for item in config]
        elif isinstance(config, str) and config.startswith("${") and config.endswith("}"):
            env_var = config[2:-1]
            return os.getenv(env_var, config)
        return config

    def _load_all_configs(self):
        """加载所有配置文件"""
        # 主配置文件
        main_config = self._load_yaml(self.config_dir / "config.yaml")
        self.config = self._substitute_env_vars(main_config)

        # 数据源配置
        self.sources = self._load_yaml(self.config_dir / "sources.yaml")

        # 关键词配置
        self.keywords = self._load_yaml(self.config_dir / "keywords.yaml")

    @property
    def ai_config(self) -> Dict[str, Any]:
        """获取 AI 配置"""
        return self.config.get("ai", {})

    @property
    def schedule_config(self) -> Dict[str, Any]:
        """获取调度配置"""
        return self.config.get("schedule", {})

    @property
    def content_config(self) -> Dict[str, Any]:
        """获取内容配置"""
        return self.config.get("content", {})

    @property
    def wechat_config(self) -> Dict[str, Any]:
        """获取微信配置"""
        return self.config.get("wechat", {})

    @property
    def database_config(self) -> Dict[str, Any]:
        """获取数据库配置"""
        return self.config.get("database", {})

    @property
    def logging_config(self) -> Dict[str, Any]:
        """获取日志配置"""
        return self.config.get("logging", {})

    @property
    def http_config(self) -> Dict[str, Any]:
        """获取 HTTP 配置"""
        return self.config.get("http", {})

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        keys = key.split(".")
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default
