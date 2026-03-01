"""
T3 Stack 脚手架技能

快速创建 T3 Stack 项目（Next.js + tRPC + Prisma/Drizzle + Tailwind + NextAuth）。
支持在线 CLI 模式和离线模板模式。
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

from leo_skills.core.base_executor import BaseExecutor


class T3StackScaffold(BaseExecutor):
    """T3 Stack 项目脚手架生成器。

    支持的操作：
        - create:   创建项目（在线或离线）
        - options:  查看可用选项
    """

    DB_PROVIDERS = ["sqlite", "mysql", "postgres", "planetscale"]

    def __init__(self) -> None:
        self.name = "t3_stack_scaffold_skill"

    # ------------------------------------------------------------------ #
    #  BaseExecutor 接口
    # ------------------------------------------------------------------ #

    def execute(
        self,
        action: str = "create",
        context: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = dict(context or {})
        params.update(kwargs)

        if action in ("create", "run"):
            return self._action_create(params)
        elif action == "options":
            return {"status": "success", "options": self.get_options()}
        else:
            return {"status": "error", "message": f"未知操作: {action}"}

    # ------------------------------------------------------------------ #
    #  动作方法
    # ------------------------------------------------------------------ #

    def _action_create(self, params: Dict[str, Any]) -> Dict[str, Any]:
        project_name = params.get("project_name", "my-t3-app")
        result = self.create_project(
            project_name=project_name,
            use_trpc=params.get("use_trpc", True),
            use_prisma=params.get("use_prisma", False),
            use_drizzle=params.get("use_drizzle", False),
            use_next_auth=params.get("use_next_auth", False),
            use_tailwind=params.get("use_tailwind", True),
            db_provider=params.get("db_provider", "sqlite"),
            use_app_router=params.get("use_app_router", True),
            offline=params.get("offline", False),
            output_dir=params.get("output_dir", "."),
        )
        return result

    def get_options(self) -> Dict[str, Any]:
        """获取所有可用选项。"""
        return {
            "use_trpc": {"type": "bool", "default": True, "description": "使用 tRPC 类型安全 API"},
            "use_prisma": {"type": "bool", "default": False, "description": "使用 Prisma ORM"},
            "use_drizzle": {"type": "bool", "default": False, "description": "使用 Drizzle ORM"},
            "use_next_auth": {"type": "bool", "default": False, "description": "使用 NextAuth.js 认证"},
            "use_tailwind": {"type": "bool", "default": True, "description": "使用 Tailwind CSS"},
            "db_provider": {"type": "choice", "choices": self.DB_PROVIDERS, "default": "sqlite", "description": "数据库类型"},
            "use_app_router": {"type": "bool", "default": True, "description": "使用 Next.js App Router"},
        }

    # ------------------------------------------------------------------ #
    #  核心逻辑
    # ------------------------------------------------------------------ #

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
        output_dir: str = ".",
    ) -> Dict[str, Any]:
        """创建 T3 Stack 项目。"""
        if offline:
            return self._scaffold_template(
                project_name, use_trpc, use_prisma, use_drizzle,
                use_next_auth, use_tailwind, db_provider, use_app_router, output_dir,
            )
        return self._scaffold_cli(
            project_name, use_trpc, use_prisma, use_drizzle,
            use_next_auth, use_tailwind, db_provider, use_app_router, output_dir,
        )

    def _scaffold_cli(self, name: str, trpc: bool, prisma: bool, drizzle: bool,
                      auth: bool, tailwind: bool, db: str, app_router: bool,
                      output_dir: str) -> Dict[str, Any]:
        """通过 create-t3-app CLI 创建项目。"""
        cmd = ["npm", "create", "t3-app@latest", name, "--CI"]
        if trpc: cmd.append("--trpc")
        if prisma: cmd.append("--prisma")
        if drizzle: cmd.append("--drizzle")
        if auth: cmd.append("--nextAuth")
        if tailwind: cmd.append("--tailwind")
        if db in self.DB_PROVIDERS: cmd.extend(["--dbProvider", db])
        if app_router: cmd.append("--appRouter")

        try:
            result = subprocess.run(
                cmd, cwd=output_dir, capture_output=True, text=True, shell=True,
            )
            return {
                "success": result.returncode == 0,
                "method": "cli",
                "project_path": str(Path(output_dir) / name),
                "command": " ".join(cmd),
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
        except Exception as e:
            return {"success": False, "method": "cli", "error": str(e)}

    def _scaffold_template(self, name: str, trpc: bool, prisma: bool, drizzle: bool,
                           auth: bool, tailwind: bool, db: str, app_router: bool,
                           output_dir: str) -> Dict[str, Any]:
        """通过内置模板创建项目。"""
        project_dir = Path(output_dir) / name
        files: Dict[str, str] = {}

        # package.json
        files["package.json"] = self._gen_package_json(name, trpc, prisma, drizzle, auth, tailwind)
        # tsconfig.json
        files["tsconfig.json"] = self._gen_tsconfig()
        # next.config.js
        files["next.config.js"] = self._gen_next_config()

        if tailwind:
            files["tailwind.config.ts"] = self._gen_tailwind_config()
            files["src/styles/globals.css"] = "@tailwind base;\n@tailwind components;\n@tailwind utilities;\n"

        if app_router:
            files["src/app/layout.tsx"] = self._gen_app_layout(name, tailwind)
            files["src/app/page.tsx"] = self._gen_app_page(name)
        else:
            files["src/pages/_app.tsx"] = self._gen_pages_app(tailwind)
            files["src/pages/index.tsx"] = self._gen_pages_index(name)

        if trpc:
            files["src/server/api/trpc.ts"] = self._gen_trpc_init()
            files["src/server/api/root.ts"] = self._gen_trpc_root()
            files["src/server/api/routers/example.ts"] = self._gen_trpc_example()
            if app_router:
                files["src/trpc/react.tsx"] = self._gen_trpc_react()

        if prisma:
            files["prisma/schema.prisma"] = self._gen_prisma_schema(db)
            files["src/server/db.ts"] = self._gen_prisma_client()
        if drizzle:
            files["src/server/db/schema.ts"] = self._gen_drizzle_schema()
            files["src/server/db/index.ts"] = self._gen_drizzle_client()
            files["drizzle.config.ts"] = self._gen_drizzle_config()

        if auth:
            if app_router:
                files["src/app/api/auth/[...nextauth]/route.ts"] = (
                    'import NextAuth from "next-auth";\n'
                    'import { authOptions } from "@/server/auth";\n\n'
                    "const handler = NextAuth(authOptions);\n"
                    "export { handler as GET, handler as POST };\n"
                )
            files["src/server/auth.ts"] = self._gen_nextauth_config()

        files[".env.example"] = self._gen_env_example(prisma, drizzle, auth, db)
        files[".gitignore"] = self._gen_gitignore()

        # 写入文件
        saved = self._save_files(project_dir, files)
        return {
            "success": True,
            "method": "template",
            "project_path": str(project_dir),
            "files_created": len(saved),
            "files": list(saved.keys()),
        }

    def _save_files(self, project_dir: Path, files: Dict[str, str]) -> Dict[str, Path]:
        saved: Dict[str, Path] = {}
        for fp, content in files.items():
            full = project_dir / fp
            full.parent.mkdir(parents=True, exist_ok=True)
            full.write_text(content, encoding="utf-8")
            saved[fp] = full
        return saved

    # ------------------------------------------------------------------ #
    #  模板生成方法
    # ------------------------------------------------------------------ #

    def _gen_package_json(self, name: str, trpc: bool, prisma: bool,
                          drizzle: bool, auth: bool, tailwind: bool) -> str:
        deps = {"next": "^14.0.0", "react": "^18.2.0", "react-dom": "^18.2.0"}
        dev = {"typescript": "^5.3.0", "@types/node": "^20.10.0",
               "@types/react": "^18.2.0", "@types/react-dom": "^18.2.0"}
        if trpc:
            deps.update({"@trpc/client": "^10.45.0", "@trpc/server": "^10.45.0",
                         "@trpc/react-query": "^10.45.0", "@tanstack/react-query": "^5.17.0",
                         "superjson": "^2.2.0", "zod": "^3.22.0"})
        if prisma:
            deps["@prisma/client"] = "^5.8.0"
            dev["prisma"] = "^5.8.0"
        if drizzle:
            deps["drizzle-orm"] = "^0.29.0"
            dev["drizzle-kit"] = "^0.20.0"
        if auth:
            deps["next-auth"] = "^4.24.0"
        if tailwind:
            dev.update({"tailwindcss": "^3.4.0", "postcss": "^8.4.0", "autoprefixer": "^10.4.0"})

        scripts = {"dev": "next dev", "build": "next build", "start": "next start", "lint": "next lint"}
        if prisma:
            scripts.update({"db:push": "prisma db push", "db:studio": "prisma studio"})
        if drizzle:
            scripts.update({"db:push": "drizzle-kit push", "db:studio": "drizzle-kit studio"})

        return json.dumps({
            "name": name.lower().replace(" ", "-"),
            "version": "0.1.0", "private": True,
            "scripts": scripts, "dependencies": deps, "devDependencies": dev,
        }, indent=2, ensure_ascii=False)

    def _gen_tsconfig(self) -> str:
        return json.dumps({
            "compilerOptions": {
                "target": "ES2017", "lib": ["dom", "dom.iterable", "esnext"],
                "strict": True, "noEmit": True, "module": "esnext",
                "moduleResolution": "bundler", "jsx": "preserve", "incremental": True,
                "plugins": [{"name": "next"}], "paths": {"@/*": ["./src/*"]},
            },
            "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx"],
            "exclude": ["node_modules"],
        }, indent=2)

    def _gen_next_config(self) -> str:
        return "/** @type {import('next').NextConfig} */\nconst nextConfig = { reactStrictMode: true };\nmodule.exports = nextConfig;\n"

    def _gen_tailwind_config(self) -> str:
        return 'import type { Config } from "tailwindcss";\n\nconst config: Config = {\n  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],\n  theme: { extend: {} },\n  plugins: [],\n};\n\nexport default config;\n'

    def _gen_app_layout(self, name: str, tailwind: bool) -> str:
        css = 'import "@/styles/globals.css";\n' if tailwind else ""
        return f'''import type {{ Metadata }} from "next";
{css}
export const metadata: Metadata = {{
  title: "{name}",
  description: "Created with T3 Stack",
}};

export default function RootLayout({{ children }}: {{ children: React.ReactNode }}) {{
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
        css = 'import "@/styles/globals.css";\n' if tailwind else ""
        return f'''import type {{ AppType }} from "next/app";
{css}
const MyApp: AppType = ({{ Component, pageProps }}) => {{
  return <Component {{...pageProps}} />;
}};

export default MyApp;
'''

    def _gen_pages_index(self, name: str) -> str:
        return self._gen_app_page(name)

    def _gen_trpc_init(self) -> str:
        return '''import { initTRPC } from "@trpc/server";
import superjson from "superjson";
import { ZodError } from "zod";

const t = initTRPC.create({
  transformer: superjson,
  errorFormatter({ shape, error }) {
    return { ...shape, data: { ...shape.data, zodError: error.cause instanceof ZodError ? error.cause.flatten() : null } };
  },
});

export const createTRPCRouter = t.router;
export const publicProcedure = t.procedure;
'''

    def _gen_trpc_root(self) -> str:
        return '''import { createTRPCRouter } from "@/server/api/trpc";
import { exampleRouter } from "@/server/api/routers/example";

export const appRouter = createTRPCRouter({ example: exampleRouter });
export type AppRouter = typeof appRouter;
'''

    def _gen_trpc_example(self) -> str:
        return '''import { z } from "zod";
import { createTRPCRouter, publicProcedure } from "@/server/api/trpc";

export const exampleRouter = createTRPCRouter({
  hello: publicProcedure
    .input(z.object({ text: z.string() }))
    .query(({ input }) => ({ greeting: `Hello ${input.text}` })),
});
'''

    def _gen_trpc_react(self) -> str:
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

    def _gen_prisma_schema(self, db: str) -> str:
        prov = {"sqlite": "sqlite", "mysql": "mysql", "postgres": "postgresql", "planetscale": "mysql"}.get(db, "sqlite")
        return f'''generator client {{
  provider = "prisma-client-js"
}}

datasource db {{
  provider = "{prov}"
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

    def _gen_drizzle_client(self) -> str:
        return '''import { drizzle } from "drizzle-orm/better-sqlite3";
import Database from "better-sqlite3";
import * as schema from "./schema";

const sqlite = new Database("sqlite.db");
export const db = drizzle(sqlite, { schema });
'''

    def _gen_drizzle_config(self) -> str:
        return '''import type { Config } from "drizzle-kit";

export default {
  schema: "./src/server/db/schema.ts",
  driver: "better-sqlite3",
  dbCredentials: { url: "./sqlite.db" },
} satisfies Config;
'''

    def _gen_nextauth_config(self) -> str:
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

    def _gen_env_example(self, prisma: bool, drizzle: bool, auth: bool, db: str) -> str:
        lines = ["# 环境变量配置"]
        if prisma or drizzle:
            urls = {"sqlite": "file:./dev.db", "mysql": "mysql://root:password@localhost:3306/mydb",
                    "postgres": "postgresql://user:password@localhost:5432/mydb"}
            lines.append(f'DATABASE_URL="{urls.get(db, "file:./dev.db")}"')
        if auth:
            lines.extend(['NEXTAUTH_SECRET="your-secret-key"', 'NEXTAUTH_URL="http://localhost:3000"'])
        return "\n".join(lines) + "\n"

    def _gen_gitignore(self) -> str:
        return "node_modules/\n.next/\ndist/\n.env\n.env.local\n*.db\n.idea/\n.vscode/\n.DS_Store\n*.log\n"


__all__ = ["T3StackScaffold"]
