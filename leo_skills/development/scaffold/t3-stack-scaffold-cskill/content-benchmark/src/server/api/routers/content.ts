import { z } from "zod";
import { createTRPCRouter, publicProcedure } from "@/server/api/trpc";
import { db } from "@/server/db";

export const contentRouter = createTRPCRouter({
  // 获取所有内容
  getAll: publicProcedure
    .input(z.object({ accountId: z.string().optional() }).optional())
    .query(async ({ input }) => {
      return db.content.findMany({
        where: input?.accountId ? { accountId: input.accountId } : undefined,
        include: { account: true, _count: { select: { analyses: true, rewrites: true } } },
        orderBy: { likes: "desc" },
      });
    }),

  // 获取单个内容详情
  getById: publicProcedure
    .input(z.object({ id: z.string() }))
    .query(async ({ input }) => {
      return db.content.findUnique({
        where: { id: input.id },
        include: { account: true, analyses: true, rewrites: true },
      });
    }),

  // 创建内容
  create: publicProcedure
    .input(z.object({
      accountId: z.string(),
      title: z.string().min(1),
      content: z.string().optional(),
      contentType: z.string(),
      likes: z.number().optional(),
      comments: z.number().optional(),
      shares: z.number().optional(),
      sourceUrl: z.string().optional(),
    }))
    .mutation(async ({ input }) => {
      return db.content.create({ data: input });
    }),

  // 删除内容
  delete: publicProcedure
    .input(z.object({ id: z.string() }))
    .mutation(async ({ input }) => {
      return db.content.delete({ where: { id: input.id } });
    }),
});
