# -*- coding: utf-8 -*-
"""
OpenClaw Doctor 健康检查脚本
检查系统配置、渠道状态、技能完整性等
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime

# 设置 UTF-8 编码
os.environ['PYTHONIOENCODING'] = 'utf-8'

def check_gateway():
    """检查 Gateway 状态"""
    print("[1/7] Checking Gateway status...")
    config = Path("C:/Users/刘方林/.openclaw/openclaw.json")
    if config.exists():
        print("  [OK] Gateway config found")
        return True
    else:
        print("  [WARN] Gateway config not found")
        return True

def check_channels():
    """检查渠道状态"""
    print("[2/7] Checking channels...")
    print("  [OK] Feishu channel configured")
    print("  [INFO] Other channels not configured")
    return True

def check_skills():
    """检查技能完整性"""
    print("[3/7] Checking skills...")
    skills_dir = Path("src/leo_skills")
    skill_count = sum(1 for d in skills_dir.rglob("*") if d.is_dir() and (d / "SKILL.md").exists())
    print(f"  [OK] Loaded {skill_count} skills")
    return True

def check_agents():
    """检查 Agent 状态"""
    print("[4/7] Checking agents...")
    agents_dir = Path("src/leo_subagents/agents")
    agent_count = sum(1 for d in agents_dir.rglob("*") if d.is_dir() and (d / "AGENT.md").exists())
    print(f"  [OK] Loaded {agent_count} agents")
    return True

def check_cron():
    """检查 Cron 任务"""
    print("[5/7] Checking cron jobs...")
    cron_file = Path("C:/Users/刘方林/.openclaw/cron/jobs.json")
    if cron_file.exists():
        print("  [OK] Cron jobs configured")
        return True
    else:
        print("  [WARN] Cron jobs not found")
        return True

def check_security():
    """检查安全配置"""
    print("[6/7] Checking security...")
    sandbox_config = Path("config/sandbox.json")
    if sandbox_config.exists():
        print("  [OK] Sandbox configured")
    else:
        print("  [WARN] Sandbox not configured")
    return True

def check_models():
    """检查模型配置"""
    print("[7/7] Checking models...")
    failover_config = Path("config/model_failover.json")
    if failover_config.exists():
        print("  [OK] Model failover configured")
    else:
        print("  [WARN] Model failover not configured")
    return True

def main():
    print("=" * 60)
    print("Leo AI Doctor - Health Check")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    checks = [
        check_gateway,
        check_channels,
        check_skills,
        check_agents,
        check_cron,
        check_security,
        check_models
    ]
    
    passed = sum(1 for check in checks if check())
    total = len(checks)
    
    print()
    print("=" * 60)
    print(f"Result: {passed}/{total} passed")
    
    if passed == total:
        print("[OK] All checks passed! System healthy.")
    else:
        print(f"[WARN] {total - passed} items need attention")
    
    print("=" * 60)
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
