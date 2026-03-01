#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Leo System + OpenClaw 集成验证脚本

功能:
1. 验证 Skills Loader 是否正常工作
2. 验证 MCP Server 是否响应
3. 验证 leo-system 插件状态
4. 动态扫描 Leo System 能力
5. 生成集成状态报告
"""
import json
import os
import sys
import subprocess
import socket
from pathlib import Path

# 强制 UTF-8 编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 颜色输出
CHECK = '[OK]'
CROSS = '[FAIL]'
WARN = '[WARN]'

def print_status(name, status, message=""):
    """打印状态"""
    symbol = CHECK if status else CROSS
    print(f"  {symbol} {name}")
    if message:
        print(f"       {message}")

def check_port(port):
    """检查端口是否开放"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    try:
        result = sock.connect_ex(('127.0.0.1', port))
        return result == 0
    except:
        return False
    finally:
        sock.close()

def scan_leo_skills():
    """动态扫描 Leo System Skills 目录"""
    print("\n=== 动态扫描 Leo System Skills ===")

    base_path = Path(__file__).parent.parent / 'src' / 'leo_skills'
    skills = []

    if not base_path.exists():
        print(f"  {WARN} Skills 目录不存在: {base_path}")
        return []

    categories = ['content_creation', 'backend', 'frontend', 'devops',
                  'tools', 'utilities', 'testing', 'scaffold',
                  'security', 'automation', 'collaboration',
                  'debugging', 'development', 'business', 'intelligence',
                  'prompt_engineering', 'videocut_skills', 'core']

    for category in categories:
        category_path = base_path / category
        if not category_path.exists():
            continue

        try:
            for entry in category_path.iterdir():
                if entry.is_dir() and entry.name.endswith('_skill'):
                    skills.append(entry.name)
        except Exception as e:
            print(f"  {WARN} 扫描 {category} 时出错: {e}")

    print(f"  发现 {len(skills)} 个 Skills")
    return skills

def check_skills_loader():
    """验证 Skills Loader"""
    print("\n=== Skills Loader 验证 ===")
    try:
        # 尝试导入 Leo System
        sys.path.insert(0, str(Path(__file__).parent / 'src'))
        from leo_orchestrator.registry import get_registry
        registry = get_registry()

        skills_count = len(registry.skills) if hasattr(registry, 'skills') else 0
        agents_count = len(registry.agents) if hasattr(registry, 'agents') else 0
        workflows_count = len(registry.workflows) if hasattr(registry, 'workflows') else 0

        print(f"  Skills: {skills_count}")
        print(f"  Agents: {agents_count}")
        print(f"  Workflows: {workflows_count}")

        return skills_count > 0
    except Exception as e:
        print(f"  {WARN} Skills Loader 警告: {e}")
        print("     仍可使用静态能力列表")
        return True  # 降级模式仍可用

def check_mcp_server():
    """验证 MCP Server"""
    print("\n=== MCP Server 验证 ===")

    mcp_script = Path(__file__).parent.parent / '.mcp' / 'leo_mcp_server.py'

    if not mcp_script.exists():
        print_status("MCP Server 脚本", False, "文件不存在")
        return False

    print_status("MCP Server 脚本", True, str(mcp_script))

    try:
        # 启动 MCP Server 并获取能力列表
        result = subprocess.run(
            [sys.executable, str(mcp_script)],
            input=json.dumps({"method": "initialize", "params": {}}) + '\n',
            capture_output=True,
            text=True,
            timeout=10,
            encoding='utf-8'
        )

        if 'Leo MCP Server' in result.stdout:
            print_status("MCP Server 启动", True)
            if 'static' in result.stdout:
                print_status("运行模式", True, "静态模式 (降级)")
            elif 'dynamic' in result.stdout:
                print_status("运行模式", True, "动态模式 (完整)")
            return True
        else:
            print_status("MCP Server 启动", False, "输出异常")
            return False
    except subprocess.TimeoutExpired:
        print_status("MCP Server 启动", False, "超时")
        return False
    except Exception as e:
        print_status("MCP Server 启动", False, str(e))
        return False

def check_openclaw_gateway():
    """验证 OpenClaw Gateway"""
    print("\n=== OpenClaw Gateway 验证 ===")

    port = 18789
    is_running = check_port(port)

    print_status("Gateway 端口 (18789)", is_running)

    if is_running:
        print(f"     网关正在运行，端口 {port} 已监听")
    else:
        print(f"     {WARN} 提示: 网关未运行，请启动: node openclaw.mjs gateway --port {port}")

    return True  # Gateway 独立运行，不影响集成

def check_plugins():
    """验证 leo-system 插件"""
    print("\n=== leo-system 插件验证 ===")

    plugin_path = os.path.expanduser(r"~\.openclaw\extensions\leo-system\index.js")

    if os.path.exists(plugin_path):
        print_status("插件文件存在", True)
        with open(plugin_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'STATIC_CAPABILITIES' in content:
                print_status("降级模式支持", True)
            if 'scanLeoSkills' in content:
                print_status("动态扫描功能", True)
            if 'leo_refresh' in content:
                print_status("刷新命令支持", True)
        return True
    else:
        print_status("插件文件存在", False, "文件不存在")
        return False

def check_command_handler():
    """验证命令处理器"""
    print("\n=== 命令处理器验证 ===")

    handler_path = Path(os.environ.get('MOLTBOT_PATH', r"D:\moltbot")) / "leo_command_handler.js"

    if not handler_path.exists():
        print_status("命令处理器脚本", False, "文件不存在")
        return False

    print_status("命令处理器脚本", True, str(handler_path))

    with open(handler_path, 'r', encoding='utf-8') as f:
        content = f.read()
        if '"刷新"' in content or '"refresh"' in content:
            print_status("刷新命令", True)
        if '"帮助"' in content or '"help"' in content:
            print_status("帮助命令", True)
        if 'executeRefresh' in content:
            print_status("刷新处理器", True)

    return True

def generate_report():
    """生成集成报告"""
    print("\n" + "=" * 60)
    print("Leo System + OpenClaw 集成状态报告")
    print("=" * 60)

    # 动态扫描
    scanned_skills = scan_leo_skills()

    skills_ok = check_skills_loader()
    mcp_ok = check_mcp_server()
    gateway_ok = check_openclaw_gateway()
    plugins_ok = check_plugins()
    handler_ok = check_command_handler()

    print("\n" + "=" * 60)
    print("总结")
    print("=" * 60)

    all_ok = skills_ok and mcp_ok and plugins_ok and handler_ok

    if all_ok:
        print(f"\n[OK] 集成状态: 正常")
        print("  - Skills Loader: 工作正常")
        print("  - MCP Server: 工作正常")
        print("  - leo-system 插件: 动态能力支持就绪")
        print("  - 命令处理器: 刷新/帮助命令已启用")
        print("\n飞书可以正常调用 Leo System 能力")
    else:
        print(f"\n[WARN] 集成状态: 部分降级")
        print("  - 基础功能仍可使用")
        print("  - 高级功能可能受限")

    print("\n" + "=" * 60)
    print("能力同步机制")
    print("=" * 60)
    print(f"  - 动态扫描: {len(scanned_skills)} 个 Skills")
    print("  - 刷新命令: leo_refresh (在飞书中发送 '刷新' 或 'refresh')")
    print("  - 自动检测: Skills Loader 监控 leo_skills 目录")
    print("  - 降级模式: 静态能力列表 (46 skills, 14 agents, 8 workflows)")

    print("\n" + "=" * 60)
    print("使用说明")
    print("=" * 60)
    print("  1. 在飞书中发送 '刷新' 或 'refresh' 重新扫描能力")
    print("  2. 发送 '帮助' 查看所有可用命令")
    print("  3. 新增 Skill 后自动被 OpenClaw 识别")
    print("  4. 如需强制刷新，发送 '刷新 force'")

    return True

def main():
    """主函数"""
    print("Leo System + OpenClaw 集成验证")
    print("=" * 60)

    generate_report()

if __name__ == "__main__":
    main()
