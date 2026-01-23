import { z } from "zod";
import { createTRPCRouter, publicProcedure } from "@/server/api/trpc";
import { db } from "@/server/db";

export const analysisRouter = createTRPCRouter({
  // 创建拆解分析
  create: publicProcedure
    .input(z.object({
      contentId: z.string(),
      hookAnalysis: z.string().optional(),
      structureAnalysis: z.string().optional(),
      emotionAnalysis: z.string().optional(),
      ctaAnalysis: z.string().optional(),
      keyTakeaways: z.string().optional(),
    }))
    .mutation(async ({ input }) => {
      return db.analysis.create({ data: input });
    }),

  // 获取内容的拆解
  getByContentId: publicProcedure
    .input(z.object({ contentId: z.string() }))
    .query(async ({ input }) => {
      return db.analysis.findFirst({
        where: { contentId: input.contentId },
        orderBy: { createdAt: "desc" },
      });
    }),
});

export const rewriteRouter = createTRPCRouter({
  // 获取所有仿写
  getAll: publicProcedure.query(async () => {
    return db.rewrite.findMany({
      include: { content: { include: { account: true } } },
      orderBy: { createdAt: "desc" },
    });
  }),

  // 创建仿写
  create: publicProcedure
    .input(z.object({
      contentId: z.string(),
      title: z.string().min(1),
      body: z.string().min(1),
      angle: z.string().optional(),
      targetAudience: z.string().optional(),
    }))
    .mutation(async ({ input }) => {
      return db.rewrite.create({ data: input });
    }),

  // 更新状态
  updateStatus: publicProcedure
    .input(z.object({ id: z.string(), status: z.enum(["draft", "published"]) }))
    .mutation(async ({ input }) => {
      return db.rewrite.update({
        where: { id: input.id },
        data: { status: input.status },
      });
    }),

  // 删除仿写
  delete: publicProcedure
    .input(z.object({ id: z.string() }))
    .mutation(async ({ input }) => {
      return db.rewrite.delete({ where: { id: input.id } });
    }),
});
