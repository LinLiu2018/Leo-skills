#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM API 密钥自动配置脚本
========================

自动配置各 LLM 提供商的 API 密钥到 .env 文件

支持的提供商:
- kimi (Moonshot)
- qwen (通义千问/DashScope)
- minimax
- deepseek
- claude (Anthropic)
- openai

用法:
    python configure_llm_keys.py

或直接运行配置向导:
    python configure_llm_keys.py --wizard
"""

import os
import sys
from pathlib import Path
from typing import Dict, Optional


def get_project_root() -> Path:
    """获取项目根目录"""
    return Path(__file__).parent.parent.parent


def read_env_file() -> Dict[str, str]:
    """读取现有的 .env 文件"""
    env_path = get_project_root() / ".env"
    env_vars = {}

    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    env_vars[key] = value

    return env_vars


def write_env_file(env_vars: Dict[str, str]):
    """写入 .env 文件"""
    env_path = get_project_root() / ".env"

    # 保留注释和格式
    lines = ["# Leo System Environment Configuration", "# =================================================", ""]

    # AI Provider Keys
    lines.extend([
        "# 1. AI Provider Keys (Fill ONE or MORE)",
        "# 国内模型（推荐）",
        ""
    ])

    providers = [
        ("KIMI_API_KEY", "Kimi (Moonshot) - https://platform.moonshot.cn/"),
        ("QWEN_API_KEY", "通义千问 - https://dashscope.aliyun.com/"),
        ("MINIMAX_API_KEY", "Minimax - https://www.minimaxi.com/"),
        ("DEEPSEEK_API_KEY", "DeepSeek - https://platform.deepseek.com/"),
        ("", ""),
        ("# 国际模型", ""),
        ("ANTHROPIC_API_KEY", "Claude - https://console.anthropic.com/"),
        ("OPENAI_API_KEY", "OpenAI - https://platform.openai.com/"),
    ]

    for key, comment in providers:
        if key.startswith("#"):
            lines.append(key)
        elif key:
            value = env_vars.get(key, "")
            lines.append(f"# {comment}")
            lines.append(f"{key}={value}")
            lines.append("")

    # System Settings
    lines.extend([
        "# 2. System Settings",
        f"LEO_ENV={env_vars.get('LEO_ENV', 'development')}",
        f"LOG_LEVEL={env_vars.get('LOG_LEVEL', 'INFO')}",
        "",
        "# 3. LLM Router Settings",
        "# 优先级设置（数字越小优先级越高）",
        f"LLM_PRIORITY_KIMI={env_vars.get('LLM_PRIORITY_KIMI', '1')}",
        f"LLM_PRIORITY_QWEN={env_vars.get('LLM_PRIORITY_QWEN', '2')}",
        f"LLM_PRIORITY_DEEPSEEK={env_vars.get('LLM_PRIORITY_DEEPSEEK', '3')}",
        f"LLM_PRIORITY_MINIMAX={env_vars.get('LLM_PRIORITY_MINIMAX', '4')}",
        "",
        "# 默认提供商（单模型模式）",
        f"DEFAULT_LLM_PROVIDER={env_vars.get('DEFAULT_LLM_PROVIDER', 'kimi')}",
    ])

    with open(env_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"✅ 配置已保存到: {env_path}")


def configure_key(provider: str, api_key: str):
    """配置单个提供商的 API 密钥"""
    env_vars = read_env_file()

    key_mapping = {
        "kimi": "KIMI_API_KEY",
        "moonshot": "KIMI_API_KEY",
        "qwen": "QWEN_API_KEY",
        "dashscope": "QWEN_API_KEY",
        "minimax": "MINIMAX_API_KEY",
        "deepseek": "DEEPSEEK_API_KEY",
        "claude": "ANTHROPIC_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "openai": "OPENAI_API_KEY",
    }

    key_name = key_mapping.get(provider.lower())
    if not key_name:
        print(f"❌ 未知的提供商: {provider}")
        print(f"支持的提供商: {list(key_mapping.keys())}")
        return False

    env_vars[key_name] = api_key
    write_env_file(env_vars)
    print(f"✅ {provider} API 密钥已配置")
    return True


def configure_multiple_keys(keys: Dict[str, str]):
    """批量配置多个 API 密钥"""
    success = []
    failed = []

    for provider, api_key in keys.items():
        if configure_key(provider, api_key):
            success.append(provider)
        else:
            failed.append(provider)

    print("\n" + "=" * 60)
    print("配置结果:")
    print(f"✅ 成功: {len(success)} 个 - {', '.join(success) if success else '无'}")
    print(f"❌ 失败: {len(failed)} 个 - {', '.join(failed) if failed else '无'}")
    print("=" * 60)

    return len(failed) == 0


def wizard():
    """交互式配置向导"""
    print("=" * 60)
    print("LLM API 密钥配置向导")
    print("=" * 60)
    print()
    print("请输入您的 API 密钥（直接回车跳过）:")
    print()

    keys = {}

    providers = [
        ("kimi", "Kimi (Moonshot)"),
        ("qwen", "通义千问 (DashScope)"),
        ("minimax", "Minimax"),
        ("deepseek", "DeepSeek"),
        ("claude", "Claude (Anthropic)"),
        ("openai", "OpenAI"),
    ]

    for key, name in providers:
        value = input(f"{name}: ").strip()
        if value:
            keys[key] = value

    if keys:
        print()
        configure_multiple_keys(keys)
    else:
        print("\n未输入任何密钥，退出配置")


def auto_configure():
    """从环境变量自动配置"""
    env_vars = read_env_file()

    # 检查现有的密钥
    keys_found = []
    for key in ["KIMI_API_KEY", "QWEN_API_KEY", "MINIMAX_API_KEY",
                "DEEPSEEK_API_KEY", "ANTHROPIC_API_KEY", "OPENAI_API_KEY"]:
        if env_vars.get(key):
            keys_found.append(key.replace("_API_KEY", "").lower())

    if keys_found:
        print(f"✅ 已配置的密钥: {', '.join(keys_found)}")
    else:
        print("⚠️ 未找到任何已配置的 API 密钥")
        print("请运行: python configure_llm_keys.py --wizard")

    return keys_found


def main():
    import argparse

    parser = argparse.ArgumentParser(description="LLM API 密钥配置工具")
    parser.add_argument("--wizard", "-w", action="store_true", help="启动交互式配置向导")
    parser.add_argument("--provider", "-p", help="提供商名称")
    parser.add_argument("--key", "-k", help="API 密钥")
    parser.add_argument("--auto", "-a", action="store_true", help="自动检查现有配置")

    args = parser.parse_args()

    if args.wizard:
        wizard()
    elif args.provider and args.key:
        configure_key(args.provider, args.key)
    elif args.auto:
        auto_configure()
    else:
        # 默认显示状态
        auto_configure()
        print("\n使用方式:")
        print("  交互式配置: python configure_llm_keys.py --wizard")
        print("  单密钥配置: python configure_llm_keys.py -p kimi -k your_api_key")


if __name__ == "__main__":
    main()
