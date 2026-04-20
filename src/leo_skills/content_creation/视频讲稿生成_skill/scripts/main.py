#!/usr/bin/env python3
import argparse
import sys
from 视频讲稿生成_skill import 视频讲稿生成Skill

def main():
    parser = argparse.ArgumentParser(description="视频讲稿生成")
    parser.add_argument("command", choices=["run", "status"])
    args = parser.parse_args()
    
    skill = 视频讲稿生成Skill()
    result = skill.execute(action=args.command)
    print(result)
    return 0 if result.get("status") == "success" else 1

if __name__ == "__main__":
    sys.exit(main())
