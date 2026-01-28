# -*- coding: utf-8 -*-
"""
evolution/config

进化配置模块
"""

class EvolutionConfig:
    """
    EvolutionConfig

    技能进化配置管理
    """

    def __init__(self):
        self.name = "evolution_config"

    def get_config(self, skill_name: str):
        """获取技能进化配置"""
        return {}

    def save_config(self, skill_name: str, config: dict):
        """保存技能进化配置"""
        pass


def main():
    return EvolutionConfig()


if __name__ == "__main__":
    main()
