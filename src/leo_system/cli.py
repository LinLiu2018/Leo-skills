"""
Leo System Command Line Interface
==================================
提供命令行接口来调用 Leo System 的 Agents
"""
import sys
import json
import argparse
from pathlib import Path

# 添加 src 目录到路径
src_path = Path(__file__).parent.parent
sys.path.insert(0, str(src_path))

from leo_orchestrator.api import LeoAPI


def main():
    parser = argparse.ArgumentParser(description="Leo System CLI")
    parser.add_argument("--agent", "-a", required=True, help="Agent name (e.g., realestate_agent)")
    parser.add_argument("--task", "-t", required=True, help="Task description")
    parser.add_argument("--output", "-o", default="json", choices=["json", "text"], help="Output format")
    
    args = parser.parse_args()
    
    # 初始化 Leo API
    api = LeoAPI(str(src_path))
    
    try:
        # 调用 Agent
        result = api.run_agent(args.agent, args.task)
        
        if args.output == "json":
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(result)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
