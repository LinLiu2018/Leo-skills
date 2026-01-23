"""
T3 Stack Scaffold Skill
=======================
快速创建 T3 Stack 项目（Next.js + tRPC + Prisma/Drizzle + Tailwind + NextAuth）
"""

import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional, Any


class T3StackScaffold:
    """T3 Stack 项目脚手架生成器"""

    DB_PROVIDERS = ["sqlite", "mysql", "postgres", "planetscale"]

    def __init__(self, output_dir: str = "."):
        self.output_dir = Path(output_dir)

    def get_options(self) -> Dict[str, Any]:
        """获取所有可用选项"""
        return {
            "use_trpc": {"type": "bool", "default": True, "description": "使用 tRPC 类型安全 API"},
            "use_prisma": {"type": "bool", "default": False, "description": "使用 Prisma ORM"},
            "use_drizzle": {"type": "bool", "default": False, "description": "使用 Drizzle ORM"},
            "use_next_auth": {"type": "bool", "default": False, "description": "使用 NextAuth.js 认证"},
            "use_tailwind": {"type": "bool", "default": True, "description": "使用 Tailwind CSS"},
            "db_provider": {"type": "choice", "choices": self.DB_PROVIDERS, "default": "sqlite", "description": "数据库类型"},
            "use_app_router": {"type": "bool", "default": True, "description": "使用 Next.js App Router"},
        }

    def create_project(
        self,
        project_name: str,
        use_trpc: bool = True,
        use_prisma: bool = False,
        use_drizzle: bool = False,
        use_next_auth: bool = False,
        use_tailwind: bool = True,
        db_provider: str = "sqlite",
        use_app_router: bool = True,
        offline: bool = False,
    ) -> Dict[str, Any]:
        """
        创建 T3 Stack 项目

        Args:
            project_name: 项目名称
            use_trpc: 使用 tRPC
            use_prisma: 使用 Prisma ORM
            use_drizzle: 使用 Drizzle ORM
            use_next_auth: 使用 NextAuth
            use_tailwind: 使用 Tailwind CSS
            db_provider: 数据库类型
            use_app_router: 使用 App Router
            offline: 离线模式（使用内置模板）

        Returns:
            创建结果
        """
        if offline:
            return self._scaffold_via_template(
                project_name, use_trpc, use_prisma, use_drizzle,
                use_next_auth, use_tailwind, db_provider, use_app_router
            )
        return self._scaffold_via_cli(
            project_name, use_trpc, use_prisma, use_drizzle,
            use_next_auth, use_tailwind, db_provider, use_app_router
        )

    def _scaffold_via_cli(
        self,
        project_name: str,
        use_trpc: bool,
        use_prisma: bool,
        use_drizzle: bool,
        use_next_auth: bool,
        use_tailwind: bool,
        db_provider: str,
        use_app_router: bool,
    ) -> Dict[str, Any]:
        """通过 CLI 创建项目"""
        cmd = ["npm", "create", "t3-app@latest", project_name, "--CI"]

        if use_trpc:
            cmd.append("--trpc")
        if use_prisma:
            cmd.append("--prisma")
        if use_drizzle:
            cmd.append("--drizzle")
        if use_next_auth:
            cmd.append("--nextAuth")
        if use_tailwind:
            cmd.append("--tailwind")
        if db_provider and db_provider in self.DB_PROVIDERS:
            cmd.extend(["--dbProvider", db_provider])
        if use_app_router:
            cmd.append("--appRouter")

        try:
            result = subprocess.run(
                cmd,
                cwd=str(self.output_dir),
                capture_output=True,
                text=True,
                shell=True,
            )
            return {
                "success": result.returncode == 0,
                "method": "cli",
                "project_path": str(self.output_dir / project_name),
                "command": " ".join(cmd),
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
        except Exception as e:
            return {"success": False, "method": "cli", "error": str(e)}

    def _scaffold_via_template(
        self,
        project_name: str,
        use_trpc: bool,
        use_prisma: bool,
        use_drizzle: bool,
        use_next_auth: bool,
        use_tailwind: bool,
        db_provider: str,
        use_app_router: bool,
    ) -> Dict[str, Any]:
        """通过内置模板创建项目"""
        project_dir = self.output_dir / project_name
        files = {}

        # package.json
        files["package.json"] = self._gen_package_json(
            project_name, use_trpc, use_prisma, use_drizzle, use_next_auth, use_tailwind
        )

        # tsconfig.json
        files["tsconfig.json"] = self._gen_tsconfig()

        # next.config.js
        files["next.config.js"] = self._gen_next_config()

        # tailwind.config.ts
        if use_tailwind:
            files["tailwind.config.ts"] = self._gen_tailwind_config()
            files["src/styles/globals.css"] = self._gen_globals_css()

        # App Router 结构
        if use_app_router:
            files["src/app/layout.tsx"] = self._gen_app_layout(project_name, use_tailwind)
            files["src/app/page.tsx"] = self._gen_app_page(project_name)
        else:
            files["src/pages/_app.tsx"] = self._gen_pages_app(use_tailwind)
            files["src/pages/index.tsx"] = self._gen_pages_index(project_name)

        # tRPC
        if use_trpc:
            files["src/server/api/trpc.ts"] = self._gen_trpc_init()
            files["src/server/api/root.ts"] = self._gen_trpc_root()
            files["src/server/api/routers/example.ts"] = self._gen_trpc_example_router()
            if use_app_router:
                files["src/trpc/react.tsx"] = self._gen_trpc_react_client()

        # Prisma
        if use_prisma:
            files["prisma/schema.prisma"] = self._gen_prisma_schema(db_provider)
            files["src/server/db.ts"] = self._gen_prisma_client()

        # Drizzle
        if use_drizzle:
            files["src/server/db/schema.ts"] = self._gen_drizzle_schema()
            files["src/server/db/index.ts"] = self._gen_drizzle_client(db_provider)
            files["drizzle.config.ts"] = self._gen_drizzle_config(db_provider)

        # NextAuth
        if use_next_auth:
            if use_app_router:
                files["src/app/api/auth/[...nextauth]/route.ts"] = self._gen_nextauth_route()
            else:
                files["src/pages/api/auth/[...nextauth].ts"] = self._gen_nextauth_api()
            files["src/server/auth.ts"] = self._gen_nextauth_config(use_prisma, use_drizzle)

        # .env.example
        files[".env.example"] = self._gen_env_example(use_prisma, use_drizzle, use_next_auth, db_provider)

        # .gitignore
        files[".gitignore"] = self._gen_gitignore()

        # 保存文件
        saved = self._save_files(project_dir, files)

        return {
            "success": True,
            "method": "template",
            "project_path": str(project_dir),
            "files_created": len(saved),
            "files": list(saved.keys()),
        }

    def _save_files(self, project_dir: Path, files: Dict[str, str]) -> Dict[str, Path]:
        """保存生成的文件"""
        saved = {}
        for file_path, content in files.items():
            full_path = project_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content, encoding="utf-8")
            saved[file_path] = full_path
        return saved

    # ==================== 模板生成方法 ====================

    def _gen_package_json(self, name: str, trpc: bool, prisma: bool, drizzle: bool, auth: bool, tailwind: bool) -> str:
        deps = {
            "next": "^14.0.0",
            "react": "^18.2.0",
            "react-dom": "^18.2.0",
        }
        dev_deps = {
            "typescript": "^5.3.0",
            "@types/node": "^20.10.0",
            "@types/react": "^18.2.0",
            "@types/react-dom": "^18.2.0",
        }

        if trpc:
            deps["@trpc/client"] = "^10.45.0"
            deps["@trpc/server"] = "^10.45.0"
            deps["@trpc/react-query"] = "^10.45.0"
            deps["@tanstack/react-query"] = "^5.17.0"
            deps["superjson"] = "^2.2.0"
            deps["zod"] = "^3.22.0"

        if prisma:
            deps["@prisma/client"] = "^5.8.0"
            dev_deps["prisma"] = "^5.8.0"

        if drizzle:
            deps["drizzle-orm"] = "^0.29.0"
            dev_deps["drizzle-kit"] = "^0.20.0"

        if auth:
            deps["next-auth"] = "^4.24.0"
            deps["@auth/core"] = "^0.18.0"

        if tailwind:
            dev_deps["tailwindcss"] = "^3.4.0"
            dev_deps["postcss"] = "^8.4.0"
            dev_deps["autoprefixer"] = "^10.4.0"

        return json.dumps({
            "name": name.lower().replace(" ", "-"),
            "version": "0.1.0",
            "private": True,
            "scripts": {
                "dev": "next dev",
                "build": "next build",
                "start": "next start",
                "lint": "next lint",
                **({"db:push": "prisma db push", "db:studio": "prisma studio"} if prisma else {}),
                **({"db:push": "drizzle-kit push", "db:studio": "drizzle-kit studio"} if drizzle else {}),
            },
            "dependencies": deps,
            "devDependencies": dev_deps,
        }, indent=2, ensure_ascii=False)

    def _gen_tsconfig(self) -> str:
        return json.dumps({
            "compilerOptions": {
                "target": "ES2017",
                "lib": ["dom", "dom.iterable", "esnext"],
                "allowJs": True,
                "skipLibCheck": True,
                "strict": True,
                "noEmit": True,
                "esModuleInterop": True,
                "module": "esnext",
                "moduleResolution": "bundler",
                "resolveJsonModule": True,
                "isolatedModules": True,
                "jsx": "preserve",
                "incremental": True,
                "plugins": [{"name": "next"}],
                "paths": {"@/*": ["./src/*"]},
            },
            "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
            "exclude": ["node_modules"],
        }, indent=2)

    def _gen_next_config(self) -> str:
        return """/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
};

module.exports = nextConfig;
"""

    def _gen_tailwind_config(self) -> str:
        return """import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {},
  },
  plugins: [],
};

export default config;
"""

    def _gen_globals_css(self) -> str:
        return """@tailwind base;
@tailwind components;
@tailwind utilities;
"""

    def _gen_app_layout(self, name: str, tailwind: bool) -> str:
        css_import = 'import "@/styles/globals.css";' if tailwind else ""
        return f'''import type {{ Metadata }} from "next";
{css_import}

export const metadata: Metadata = {{
  title: "{name}",
  description: "Created with T3 Stack",
}};

export default function RootLayout({{
  children,
}}: {{
  children: React.ReactNode;
}}) {{
  return (
    <html lang="zh-CN">
      <body>{{children}}</body>
    </html>
  );
}}
'''

    def _gen_app_page(self, name: str) -> str:
        return f'''export default function Home() {{
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <h1 className="text-4xl font-bold">{name}</h1>
      <p className="mt-4 text-gray-600">Created with T3 Stack</p>
    </main>
  );
}}
'''

    def _gen_pages_app(self, tailwind: bool) -> str:
        css_import = 'import "@/styles/globals.css";' if tailwind else ""
        return f'''import type {{ AppType }} from "next/app";
{css_import}

const MyApp: AppType = ({{ Component, pageProps }}) => {{
  return <Component {{...pageProps}} />;
}};

export default MyApp;
'''

    def _gen_pages_index(self, name: str) -> str:
        return f'''export default function Home() {{
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <h1 className="text-4xl font-bold">{name}</h1>
      <p className="mt-4 text-gray-600">Created with T3 Stack</p>
    </main>
  );
}}
'''

    def _gen_trpc_init(self) -> str:
        return '''import { initTRPC } from "@trpc/server";
import superjson from "superjson";
import { ZodError } from "zod";

const t = initTRPC.create({
  transformer: superjson,
  errorFormatter({ shape, error }) {
    return {
      ...shape,
      data: {
        ...shape.data,
        zodError: error.cause instanceof ZodError ? error.cause.flatten() : null,
      },
    };
  },
});

export const createTRPCRouter = t.router;
export const publicProcedure = t.procedure;
'''

    def _gen_trpc_root(self) -> str:
        return '''import { createTRPCRouter } from "@/server/api/trpc";
import { exampleRouter } from "@/server/api/routers/example";

export const appRouter = createTRPCRouter({
  example: exampleRouter,
});

export type AppRouter = typeof appRouter;
'''

    def _gen_trpc_example_router(self) -> str:
        return '''import { z } from "zod";
import { createTRPCRouter, publicProcedure } from "@/server/api/trpc";

export const exampleRouter = createTRPCRouter({
  hello: publicProcedure
    .input(z.object({ text: z.string() }))
    .query(({ input }) => {
      return { greeting: `Hello ${input.text}` };
    }),
});
'''

    def _gen_trpc_react_client(self) -> str:
        return '''"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { httpBatchLink, loggerLink } from "@trpc/client";
import { createTRPCReact } from "@trpc/react-query";
import { useState } from "react";
import superjson from "superjson";
import type { AppRouter } from "@/server/api/root";

export const api = createTRPCReact<AppRouter>();

export function TRPCReactProvider(props: { children: React.ReactNode }) {
  const [queryClient] = useState(() => new QueryClient());
  const [trpcClient] = useState(() =>
    api.createClient({
      links: [
        loggerLink({ enabled: () => process.env.NODE_ENV === "development" }),
        httpBatchLink({ url: "/api/trpc", transformer: superjson }),
      ],
    })
  );

  return (
    <QueryClientProvider client={queryClient}>
      <api.Provider client={trpcClient} queryClient={queryClient}>
        {props.children}
      </api.Provider>
    </QueryClientProvider>
  );
}
'''

    def _gen_prisma_schema(self, db_provider: str) -> str:
        provider_map = {
            "sqlite": "sqlite",
            "mysql": "mysql",
            "postgres": "postgresql",
            "planetscale": "mysql",
        }
        provider = provider_map.get(db_provider, "sqlite")
        return f'''generator client {{
  provider = "prisma-client-js"
}}

datasource db {{
  provider = "{provider}"
  url      = env("DATABASE_URL")
}}

model User {{
  id        String   @id @default(cuid())
  email     String   @unique
  name      String?
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
}}
'''

    def _gen_prisma_client(self) -> str:
        return '''import { PrismaClient } from "@prisma/client";

const globalForPrisma = globalThis as unknown as { prisma: PrismaClient };

export const db = globalForPrisma.prisma ?? new PrismaClient();

if (process.env.NODE_ENV !== "production") globalForPrisma.prisma = db;
'''

    def _gen_drizzle_schema(self) -> str:
        return '''import { sql } from "drizzle-orm";
import { text, sqliteTable } from "drizzle-orm/sqlite-core";

export const users = sqliteTable("users", {
  id: text("id").primaryKey(),
  email: text("email").notNull().unique(),
  name: text("name"),
  createdAt: text("created_at").default(sql`CURRENT_TIMESTAMP`),
});
'''

    def _gen_drizzle_client(self, db_provider: str) -> str:
        return '''import { drizzle } from "drizzle-orm/better-sqlite3";
import Database from "better-sqlite3";
import * as schema from "./schema";

const sqlite = new Database("sqlite.db");
export const db = drizzle(sqlite, { schema });
'''

    def _gen_drizzle_config(self, db_provider: str) -> str:
        return '''import type { Config } from "drizzle-kit";

export default {
  schema: "./src/server/db/schema.ts",
  driver: "better-sqlite3",
  dbCredentials: { url: "./sqlite.db" },
  tablesFilter: ["*"],
} satisfies Config;
'''

    def _gen_nextauth_route(self) -> str:
        return '''import NextAuth from "next-auth";
import { authOptions } from "@/server/auth";

const handler = NextAuth(authOptions);
export { handler as GET, handler as POST };
'''

    def _gen_nextauth_api(self) -> str:
        return '''import NextAuth from "next-auth";
import { authOptions } from "@/server/auth";

export default NextAuth(authOptions);
'''

    def _gen_nextauth_config(self, prisma: bool, drizzle: bool) -> str:
        return '''import type { NextAuthOptions } from "next-auth";
import CredentialsProvider from "next-auth/providers/credentials";

export const authOptions: NextAuthOptions = {
  providers: [
    CredentialsProvider({
      name: "Credentials",
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" },
      },
      async authorize(credentials) {
        // TODO: 实现认证逻辑
        return null;
      },
    }),
  ],
  session: { strategy: "jwt" },
};
'''

    def _gen_env_example(self, prisma: bool, drizzle: bool, auth: bool, db_provider: str) -> str:
        lines = ["# 环境变量配置"]
        if prisma or drizzle:
            db_urls = {
                "sqlite": "file:./dev.db",
                "mysql": "mysql://root:password@localhost:3306/mydb",
                "postgres": "postgresql://user:password@localhost:5432/mydb",
                "planetscale": "mysql://user:password@host/db?ssl={\"rejectUnauthorized\":true}",
            }
            lines.append(f"DATABASE_URL=\"{db_urls.get(db_provider, 'file:./dev.db')}\"")
        if auth:
            lines.append("NEXTAUTH_SECRET=\"your-secret-key\"")
            lines.append("NEXTAUTH_URL=\"http://localhost:3000\"")
        return "\n".join(lines) + "\n"

    def _gen_gitignore(self) -> str:
        return """# Dependencies
node_modules/
.pnp/
.pnp.js

# Build
.next/
out/
dist/
build/

# Environment
.env
.env.local
.env.*.local

# Database
*.db
prisma/migrations/

# IDE
.idea/
.vscode/
*.swp

# OS
.DS_Store
Thumbs.db

# Logs
*.log
npm-debug.log*
"""
