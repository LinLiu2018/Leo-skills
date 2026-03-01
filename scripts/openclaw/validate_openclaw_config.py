#!/usr/bin/env python3
"""
OpenClaw 配置验证和修复脚本

功能:
1. 验证配置文件格式
2. 检测废弃/无效的配置键
3. 自动修复常见问题

用法:
    python scripts/validate_openclaw_config.py [--fix]
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# 配置路径
CONFIG_PATH = os.path.expanduser(r"~\.openclaw\openclaw.json")

# 必需的配置键
REQUIRED_KEYS = ["meta", "agents", "channels", "gateway"]

# 废弃的配置键（会导致验证失败）
DEPRECATED_KEYS = ["mcpTools", "systemPrompt"]

# 不被识别的根级键
INVALID_ROOT_KEYS = ["cron", "mcp"]

# identity 的有效 kind 值
VALID_IDENTITY_KINDS = ["inline", "file", "url"]


def load_config(config_path: str) -> dict:
    """加载配置文件"""
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def validate_config(config: dict) -> tuple[list, list]:
    """
    验证配置文件
    返回: (errors, warnings)
    """
    errors = []
    warnings = []

    # 检查必需键
    for key in REQUIRED_KEYS:
        if key not in config:
            errors.append(f"缺少必需键: {key}")

    # 检查无效根级键
    for key in INVALID_ROOT_KEYS:
        if key in config:
            errors.append(f"发现无效根级键: {key} (不被 OpenClaw 2026.1.30 识别)")

    # 递归检查废弃键
    def check_deprecated(obj, path=""):
        if isinstance(obj, dict):
            for key, value in obj.items():
                current_path = f"{path}.{key}" if path else key
                if key in DEPRECATED_KEYS:
                    errors.append(f"发现废弃键: {current_path}")
                check_deprecated(value, current_path)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                check_deprecated(item, f"{path}[{i}]")

    check_deprecated(config)

    # 检查 agents.list.identity 格式
    agents_list = config.get("agents", {}).get("list", [])
    for i, agent in enumerate(agents_list):
        identity = agent.get("identity")
        if identity:
            if isinstance(identity, str):
                errors.append(f"agents.list[{i}].identity 格式错误: 应为对象，实际为字符串")
            elif isinstance(identity, dict):
                kind = identity.get("kind")
                if kind and kind not in VALID_IDENTITY_KINDS:
                    warnings.append(f"agents.list[{i}].identity.kind 值 '{kind}' 可能无效")

    # 检查 channels.feishu
    feishu = config.get("channels", {}).get("feishu", {})
    if not feishu:
        warnings.append("channels.feishu 未配置")
    elif not feishu.get("enabled"):
        warnings.append("channels.feishu.enabled 为 false")

    # 检查 gateway
    gateway = config.get("gateway", {})
    if not gateway.get("mode"):
        warnings.append("gateway.mode 未设置")

    return errors, warnings


def fix_config(config: dict) -> dict:
    """修复配置文件"""
    fixed = config.copy()

    # 移除无效根级键
    for key in INVALID_ROOT_KEYS:
        if key in fixed:
            del fixed[key]
            print(f"  已移除: {key}")

    # 移除 agents.defaults 中的废弃键
    if "agents" in fixed and "defaults" in fixed["agents"]:
        for key in DEPRECATED_KEYS:
            if key in fixed["agents"]["defaults"]:
                del fixed["agents"]["defaults"][key]
                print(f"  已移除: agents.defaults.{key}")

    # 修复 agents.list 中的问题
    if "agents" in fixed and "list" in fixed["agents"]:
        for i, agent in enumerate(fixed["agents"]["list"]):
            # 移除废弃键
            for key in DEPRECATED_KEYS:
                if key in agent:
                    del agent[key]
                    print(f"  已移除: agents.list[{i}].{key}")

            # 修复 identity 格式
            identity = agent.get("identity")
            if isinstance(identity, str):
                agent["identity"] = {}
                print(f"  已修复: agents.list[{i}].identity (字符串 -> 空对象)")

    # 确保 gateway.mode 存在
    if "gateway" in fixed and "mode" not in fixed["gateway"]:
        fixed["gateway"]["mode"] = "local"
        print("  已添加: gateway.mode = local")

    return fixed


def main():
    """主函数"""
    fix_mode = "--fix" in sys.argv

    print("=" * 60)
    print("OpenClaw 配置验证工具")
    print("=" * 60)
    print(f"配置文件: {CONFIG_PATH}")
    print(f"模式: {'修复' if fix_mode else '验证'}")
    print()

    # 检查文件是否存在
    if not os.path.exists(CONFIG_PATH):
        print(f"错误: 配置文件不存在: {CONFIG_PATH}")
        sys.exit(1)

    # 加载配置
    try:
        config = load_config(CONFIG_PATH)
    except json.JSONDecodeError as e:
        print(f"错误: JSON 解析失败: {e}")
        sys.exit(1)

    # 验证配置
    errors, warnings = validate_config(config)

    # 输出结果
    if errors:
        print("[ERROR] 发现错误:")
        for error in errors:
            print(f"  - {error}")
        print()

    if warnings:
        print("[WARN] 警告:")
        for warning in warnings:
            print(f"  - {warning}")
        print()

    if not errors and not warnings:
        print("[OK] 配置验证通过!")
        sys.exit(0)

    # 修复模式
    if fix_mode and errors:
        print("正在修复配置...")

        # 备份
        backup_path = CONFIG_PATH + f".backup.{datetime.now().strftime('%Y%m%d%H%M%S')}"
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        print(f"已备份到: {backup_path}")

        # 修复
        fixed_config = fix_config(config)

        # 保存
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(fixed_config, f, ensure_ascii=False, indent=2)
        print(f"\n已保存修复后的配置到: {CONFIG_PATH}")

        # 重新验证
        errors2, warnings2 = validate_config(fixed_config)
        if errors2:
            print("\n[WARN] 仍有错误需要手动修复:")
            for error in errors2:
                print(f"  - {error}")
            print(f"\n建议运行: cd {os.environ.get('MOLTBOT_PATH', 'D:\\\\moltbot')} && node openclaw.mjs doctor --fix")
        else:
            print("\n[OK] 配置已修复!")
    elif errors:
        print("提示: 使用 --fix 参数自动修复")
        print(f"或运行: cd {os.environ.get('MOLTBOT_PATH', 'D:\\\\moltbot')} && node openclaw.mjs doctor --fix")
        sys.exit(1)


if __name__ == "__main__":
    main()

