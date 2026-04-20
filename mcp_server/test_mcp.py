#!/usr/bin/env python3
"""
测试 Leo System MCP Server
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, r"E:\桌面\leo_ai_system\src")

print("="*60)
print("Leo System MCP Server 测试")
print("="*60)

# 测试 1: 导入测试
print("\n[测试 1] 导入 MCP Server...")
try:
    from mcp.server import Server
    print("  ✅ MCP 库已安装")
except ImportError:
    print("  ❌ MCP 库未安装")
    print("  解决：pip install mcp")
    sys.exit(1)

# 测试 2: Leo System 路径
print("\n[测试 2] Leo System 路径...")
leo_path = Path(r"E:\桌面\leo_ai_system")
if leo_path.exists():
    print(f"  ✅ Leo System 路径：{leo_path}")
else:
    print(f"  ❌ Leo System 路径不存在：{leo_path}")
    sys.exit(1)

# 测试 3: Skills 目录
print("\n[测试 3] Skills 目录...")
skills_dir = leo_path / "src" / "leo_skills"
if skills_dir.exists():
    skill_count = len(list(skills_dir.rglob("*_skill")))
    print(f"  ✅ Skills 目录存在：{skill_count} 个技能")
else:
    print(f"  ❌ Skills 目录不存在")
    sys.exit(1)

# 测试 4: 导入 skill-creator
print("\n[测试 4] 导入 skill-creator...")
try:
    from leo_skills.development.skill_creator.skill_creator import SkillCreator
    print("  ✅ skill-creator 已导入")
    
    # 测试创建技能
    creator = SkillCreator()
    result = creator.execute(action="list_templates")
    print(f"  ✅ skill-creator 可用，模板数：{len(result.get('templates', []))}")
except Exception as e:
    print(f"  ❌ skill-creator 导入失败：{e}")

# 测试 5: MCP Server 代码
print("\n[测试 5] MCP Server 代码...")
mcp_server_file = leo_path / "mcp_server" / "server.py"
if mcp_server_file.exists():
    print(f"  ✅ MCP Server 代码存在：{mcp_server_file}")
    print(f"     文件大小：{mcp_server_file.stat().st_size} 字节")
else:
    print(f"  ❌ MCP Server 代码不存在")
    sys.exit(1)

# 测试 6: 配置文件
print("\n[测试 6] 配置文件...")
config_file = leo_path / "mcp_server" / "openclaw_mcp_config.json"
if config_file.exists():
    config = json.loads(config_file.read_text(encoding='utf-8'))
    print(f"  ✅ 配置文件存在")
    print(f"     MCP Server: {config.get('mcp', {}).get('servers', {}).get('leo-system', {}).get('enabled', False)}")
else:
    print(f"  ❌ 配置文件不存在")

# 总结
print("\n" + "="*60)
print("测试完成！")
print("="*60)
print("\n下一步:")
print("1. 安装 MCP 库：pip install mcp")
print("2. 配置 OpenClaw: 复制 openclaw_mcp_config.json 到 openclaw.json")
print("3. 重启 OpenClaw Gateway: openclaw gateway restart")
print("4. 测试连接：openclaw mcp status")
print("5. 调用技能：openclaw mcp call leo-system skills_list")
print("="*60)
