/**
 * 创建定时任务脚本
 */
const fs = require("fs");

// 读取当前配置
const configPath = "C:\\Users\\刘方林\\.openclaw\\openclaw.json";
const config = JSON.parse(fs.readFileSync(configPath, "utf-8"));

// 初始化 cron.jobs 数组
if (!config.cron) {
  config.cron = {};
}
if (!config.cron.jobs) {
  config.cron.jobs = [];
}

// 定义定时任务
const jobs = [
  {
    name: "每日市场情报任务",
    description: "每日8:00收集市场情报并推送到飞书",
    schedule: { kind: "cron", expr: "0 8 * * *", tz: "Asia/Shanghai" },
    sessionTarget: "isolated",
    wakeMode: "next-heartbeat",
    payload: {
      kind: "agentTurn",
      message: "请执行每日市场情报收集任务：\n1. 搜索最新的房地产市场动态\n2. 收集政策变化信息\n3. 汇总关键数据\n4. 生成简报并通过飞书发送",
      deliver: true,
      channel: "feishu",
      to: "ou_099438b3924bd34e5f9445bc8220a460",
      bestEffortDeliver: true
    },
    isolation: { postToMainPrefix: "Cron", postToMainMode: "summary" },
    enabled: true
  },
  {
    name: "每日内容生成任务",
    description: "每日9:00生成营销内容并推送到飞书",
    schedule: { kind: "cron", expr: "0 9 * * *", tz: "Asia/Shanghai" },
    sessionTarget: "isolated",
    wakeMode: "next-heartbeat",
    payload: {
      kind: "agentTurn",
      message: "请执行每日内容生成任务：\n1. 根据最新的市场动态生成营销文案\n2. 创作适合社交媒体发布的内容\n3. 准备房产推广素材\n4. 通过飞书发送生成的内容",
      deliver: true,
      channel: "feishu",
      to: "ou_099438b3924bd34e5f9445bc8220a460",
      bestEffortDeliver: true
    },
    isolation: { postToMainPrefix: "Cron", postToMainMode: "summary" },
    enabled: true
  },
  {
    name: "竞品监控任务",
    description: "每4小时监控竞争对手动态",
    schedule: { kind: "cron", expr: "0 */4 * * *", tz: "Asia/Shanghai" },
    sessionTarget: "isolated",
    wakeMode: "next-heartbeat",
    payload: {
      kind: "agentTurn",
      message: "请执行竞品监控任务：\n1. 监控主要竞争对手的营销活动\n2. 收集竞品价格和促销信息\n3. 分析市场趋势变化\n4. 生成竞品分析简报并通过飞书发送",
      deliver: true,
      channel: "feishu",
      to: "ou_099438b3924bd34e5f9445bc8220a460",
      bestEffortDeliver: true
    },
    isolation: { postToMainPrefix: "Cron", postToMainMode: "summary" },
    enabled: true
  },
  {
    name: "周报生成任务",
    description: "每周五18:00生成工作周报",
    schedule: { kind: "cron", expr: "0 18 * * 5", tz: "Asia/Shanghai" },
    sessionTarget: "isolated",
    wakeMode: "next-heartbeat",
    payload: {
      kind: "agentTurn",
      message: "请生成本周工作周报：\n1. 汇总本周市场情报收集情况\n2. 统计内容发布数量和效果\n3. 分析竞品动态和市场份额变化\n4. 总结关键数据和洞察\n5. 提出下周工作计划\n6. 通过飞书发送完整周报",
      deliver: true,
      channel: "feishu",
      to: "ou_099438b3924bd34e5f9445bc8220a460",
      bestEffortDeliver: true
    },
    isolation: { postToMainPrefix: "Cron", postToMainMode: "summary" },
    enabled: true
  }
];

// 添加到配置
config.cron.jobs = [...(config.cron.jobs || []), ...jobs];

// 保存配置
fs.writeFileSync(configPath, JSON.stringify(config, null, 2));
console.log("✅ 已添加 4 个定时任务到配置\n");
console.log("任务列表：");
jobs.forEach((job, i) => {
  console.log(`${i + 1}. ${job.name}`);
  console.log(`   调度: ${job.schedule.expr} (${job.schedule.tz})`);
});
