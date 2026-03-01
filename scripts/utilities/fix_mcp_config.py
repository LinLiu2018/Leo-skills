#!/usr/bin/env python3
"""修复 OpenClaw MCP 配置"""
import json
from pathlib import Path

config_path = Path.home() / ".openclaw" / "openclaw.json"
project_root = Path(__file__).parent.parent.resolve()

# 读取配置
with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)

# 移除旧的 plugins.entries.leo-system (OpenClaw 自动管理)
if 'plugins' in config and 'entries' in config['plugins']:
    entries = config['plugins']['entries']
    if 'leo-system' in entries:
        del entries['leo-system']
        print("已移除: plugins.entries.leo-system")

# 添加正确的 mcpServers 配置
config['mcpServers'] = {
    'leo-system': {
        'command': 'python',
        'args': [str(project_root / '.mcp' / 'leo_mcp_server.py')],
        'env': {
            'PYTHONPATH': str(project_root / 'src'),
            'PYTHONIOENCODING': 'utf-8'
        }
    }
}
print("已添加: mcpServers.leo-system")

# 保存配置
with open(config_path, 'w', encoding='utf-8') as f:
    json.dump(config, f, ensure_ascii=False, indent=2)

print(f"\n配置已保存到: {config_path}")
