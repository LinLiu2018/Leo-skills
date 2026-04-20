---
name: t3-stack-scaffold-skill
description: T3 Stack Scaffold Skill 技能。当用户需要相关帮助时使用。 [优化第5轮：提升了触发准确率]
license: MIT
---

# T3 Stack Scaffold Skill

快速创建 T3 Stack 项目（Next.js + tRPC + Prisma/Drizzle + Tailwind + NextAuth）

## 技术栈

T3 Stack 是一个现代全栈开发框架，包含：

| 技术 | 说明 |
|------|------|
| Next.js | React 全栈框架 |
| TypeScript | 类型安全 |
| tRPC | 端到端类型安全 API |
| Prisma / Drizzle | ORM 数据库操作 |
| NextAuth.js | 认证解决方案 |
| Tailwind CSS | 原子化 CSS 框架 |

## 使用方法

### CLI 方式

```bash
# 基础项目
python scripts/main.py --name my-app

# 完整配置
python scripts/main.py --name my-app --trpc --prisma --next-auth --tailwind --db postgres

# 使用 Drizzle 替代 Prisma
python scripts/main.py --name my-app --trpc --drizzle --tailwind

# 离线模式（使用内置模板）
python scripts/main.py --name my-app --offline
```

### Python API

```python
from scripts.t3_stack_skill import T3StackScaffold

scaffold = T3StackScaffold(output_dir="./projects")

# 创建项目
result = scaffold.create_project(
    project_name="my-app",
    use_trpc=True,
    use_prisma=True,
    use_next_auth=True,
    use_tailwind=True,
    db_provider="postgres",
    use_app_router=True,
)

print(result)
```

## 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| project_name | str | 必填 | 项目名称 |
| use_trpc | bool | True | 使用 tRPC |
| use_prisma | bool | False | 使用 Prisma ORM |
| use_drizzle | bool | False | 使用 Drizzle ORM |
| use_next_auth | bool | False | 使用 NextAuth.js |
| use_tailwind | bool | True | 使用 Tailwind CSS |
| db_provider | str | "sqlite" | 数据库类型 |
| use_app_router | bool | True | 使用 App Router |
| offline | bool | False | 离线模式 |

## 数据库选项

- `sqlite` - 轻量级本地数据库
- `mysql` - MySQL 数据库
- `postgres` - PostgreSQL 数据库
- `planetscale` - PlanetScale Serverless MySQL

## 预设配置

在 `config/templates.yaml` 中定义了常用预设：

- `minimal` - 最小配置（仅 Next.js + TypeScript）
- `standard` - 标准配置（+ tRPC + Tailwind）
- `full_prisma` - 完整配置（Prisma 版）
- `full_drizzle` - 完整配置（Drizzle 版）

## 生成的项目结构

```
my-app/
├── src/
│   ├── app/                 # App Router 页面
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── server/
│   │   ├── api/             # tRPC API
│   │   │   ├── trpc.ts
│   │   │   ├── root.ts
│   │   │   └── routers/
│   │   ├── db.ts            # 数据库客户端
│   │   └── auth.ts          # NextAuth 配置
│   ├── styles/
│   │   └── globals.css
│   └── trpc/
│       └── react.tsx        # tRPC React 客户端
├── prisma/
│   └── schema.prisma        # Prisma Schema
├── package.json
├── tsconfig.json
├── next.config.js
├── tailwind.config.ts
└── .env.example
```

## 创建后的下一步

```bash
cd my-app
npm install
npm run dev
```

如果使用了 Prisma：
```bash
npx prisma db push
npx prisma studio
```

如果使用了 Drizzle：
```bash
npm run db:push
npm run db:studio
```

## 相关链接

- [create-t3-app](https://github.com/t3-oss/create-t3-app)
- [T3 Stack 文档](https://create.t3.gg/)
- [Next.js](https://nextjs.org/)
- [tRPC](https://trpc.io/)
- [Prisma](https://www.prisma.io/)
- [Drizzle](https://orm.drizzle.team/)
