import { createTRPCRouter } from "@/server/api/trpc";
import { accountRouter } from "@/server/api/routers/account";
import { contentRouter } from "@/server/api/routers/content";
import { analysisRouter, rewriteRouter } from "@/server/api/routers/analysis";

export const appRouter = createTRPCRouter({
  account: accountRouter,
  content: contentRouter,
  analysis: analysisRouter,
  rewrite: rewriteRouter,
});

export type AppRouter = typeof appRouter;
