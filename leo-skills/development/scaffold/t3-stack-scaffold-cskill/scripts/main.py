#!/usr/bin/env python3
"""
T3 Stack Scaffold Skill - CLI 入口
==================================
快速创建 T3 Stack 项目
"""

import argparse
import sys
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from t3_stack_skill import T3StackScaffold


def main():
    parser = argparse.ArgumentParser(
        description="T3 Stack 项目脚手架 - 快速创建 Next.js + tRPC + Prisma/Drizzle 项目"
    )
    parser.add_argument("--name", "-n", required=True, help="项目名称")
    parser.add_argument("--output", "-o", default=".", help="输出目录")
    parser.add_argument("--trpc", action="store_true", default=True, help="使用 tRPC")
    parser.add_argument("--no-trpc", action="store_false", dest="trpc", help="不使用 tRPC")
    parser.add_argument("--prisma", action="store_true", help="使用 Prisma ORM")
    parser.add_argument("--drizzle", action="store_true", help="使用 Drizzle ORM")
    parser.add_argument("--next-auth", action="store_true", help="使用 NextAuth.js")
    parser.add_argument("--tailwind", action="store_true", default=True, help="使用 Tailwind CSS")
    parser.add_argument("--no-tailwind", action="store_false", dest="tailwind", help="不使用 Tailwind")
    parser.add_argument(
        "--db",
        choices=["sqlite", "mysql", "postgres", "planetscale"],
        default="sqlite",
        help="数据库类型",
    )
    parser.add_argument("--app-router", action="store_true", default=True, help="使用 App Router")
    parser.add_argument("--pages-router", action="store_false", dest="app_router", help="使用 Pages Router")
    parser.add_argument("--offline", action="store_true", help="离线模式（使用内置模板）")
    parser.add_argument("--options", action="store_true", help="显示所有可用选项")

    args = parser.parse_args()

    scaffold = T3StackScaffold(output_dir=args.output)

    if args.options:
        print("\n可用选项:")
        for key, info in scaffold.get_options().items():
            print(f"  --{key.replace('_', '-')}: {info['description']} (默认: {info['default']})")
        return

    print(f"\n创建 T3 Stack 项目: {args.name}")
    print(f"  tRPC: {'Yes' if args.trpc else 'No'}")
    print(f"  Prisma: {'Yes' if args.prisma else 'No'}")
    print(f"  Drizzle: {'Yes' if args.drizzle else 'No'}")
    print(f"  NextAuth: {'Yes' if args.next_auth else 'No'}")
    print(f"  Tailwind: {'Yes' if args.tailwind else 'No'}")
    print(f"  Database: {args.db}")
    print(f"  Router: {'App Router' if args.app_router else 'Pages Router'}")
    print(f"  Mode: {'Offline (Template)' if args.offline else 'Online (CLI)'}")
    print()

    result = scaffold.create_project(
        project_name=args.name,
        use_trpc=args.trpc,
        use_prisma=args.prisma,
        use_drizzle=args.drizzle,
        use_next_auth=args.next_auth,
        use_tailwind=args.tailwind,
        db_provider=args.db,
        use_app_router=args.app_router,
        offline=args.offline,
    )

    if result["success"]:
        print("[OK] 项目创建成功!")
        print(f"  路径: {result['project_path']}")
        if result["method"] == "template":
            print(f"  文件数: {result['files_created']}")
        print("\n下一步:")
        print(f"  cd {args.name}")
        print("  npm install")
        print("  npm run dev")
    else:
        print("[FAIL] 项目创建失败!")
        print(f"  错误: {result.get('error', result.get('stderr', 'Unknown error'))}")
        sys.exit(1)


# 便捷函数
def create_t3_project(name: str, **kwargs) -> dict:
    """便捷函数：创建 T3 Stack 项目"""
    scaffold = T3StackScaffold(output_dir=kwargs.pop("output_dir", "."))
    return scaffold.create_project(project_name=name, **kwargs)


if __name__ == "__main__":
    main()
