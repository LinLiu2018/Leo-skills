#!/usr/bin/env python3
"""修复 OpenClaw 配置 - 移除不支持的配置"""
import json
import os

config_path = os.path.expanduser(r"C:\Users\刘方林\.openclaw\openclaw.json")

# 读取配置
with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)

changes = []

# 移除不支持的 mcpServers
if 'mcpServers' in config:
    del config['mcpServers']
    changes.append("已移除: mcpServers (OpenClaw 2026.1.30 不支持)")

# 移除有问题的 leo-system 插件
if 'plugins' in config and 'entries' in config['plugins']:
    entries = config['plugins']['entries']
    if 'leo-system' in entries:
        del entries['leo-system']
        changes.append("已移除: plugins.entries.leo-system (插件有错误)")

# 确保 Skills Loader 配置正确
skills_config = config.get('skills', {}).get('load', {})
if 'extraDirs' in skills_config:
    # 修复路径中的乱码
    dirs = skills_config['extraDirs']
    fixed_dirs = []
    for d in dirs:
        # 尝试修复中文路径问题
        if '妗岄潰' in d:
            d = d.replace('妗岄潰', '桌面')
        if '桌面' in d:
            fixed_dirs.append(d.replace('\\', '\\\\'))
    if fixed_dirs:
        skills_config['extraDirs'] = fixed_dirs
        changes.append(f"已修复 Skills 路径: {fixed_dirs}")

# 保存配置
with open(config_path, 'w', encoding='utf-8') as f:
    json.dump(config, f, ensure_ascii=False, indent=2)

print("配置修复完成:")
for change in changes:
    print(f"  - {change}")
print(f"\n配置文件: {config_path}")
