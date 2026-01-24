import { z } from "zod";
import { createTRPCRouter, publicProcedure } from "@/server/api/trpc";
import { db } from "@/server/db";

export const accountRouter = createTRPCRouter({
  // 获取所有账号
  getAll: publicProcedure.query(async () => {
    return db.benchmarkAccount.findMany({
      include: { _count: { select: { contents: true } } },
      orderBy: { createdAt: "desc" },
    });
  }),

  // 获取单个账号详情
  getById: publicProcedure
    .input(z.object({ id: z.string() }))
    .query(async ({ input }) => {
      return db.benchmarkAccount.findUnique({
        where: { id: input.id },
        include: { contents: { orderBy: { likes: "desc" } } },
      });
    }),

  // 创建账号
  create: publicProcedure
    .input(z.object({
      platform: z.string().min(1),
      accountName: z.string().min(1),
      accountId: z.string().optional(),
      followers: z.number().optional(),
      category: z.string().min(1),
      style: z.string().optional(),
      notes: z.string().optional(),
    }))
    .mutation(async ({ input }) => {
      return db.benchmarkAccount.create({ data: input });
    }),

  // 删除账号
  delete: publicProcedure
    .input(z.object({ id: z.string() }))
    .mutation(async ({ input }) => {
      return db.benchmarkAccount.delete({ where: { id: input.id } });
    }),
});
