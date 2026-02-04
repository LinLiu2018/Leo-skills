/**
 * 流式输出测试脚本
 * 运行方式: cd D:\moltbot && npx tsx d:\桌面\leo_ai_system\scripts\test_streaming.ts
 */
import { sendStreamingText } from "../extensions/feishu/dist/src/streaming.js";
import * as fs from "fs";

// 加载配置
const configPath = "C:\\Users\\刘方林\\.openclaw\\openclaw.json";
const config = JSON.parse(fs.readFileSync(configPath, "utf-8"));

async function test() {
  console.log("🚀 开始测试流式输出...\n");

  const testMessage = `✨ **流式输出测试**

这是一个打字机效果的消息。

\`\`\`python
def stream_example():
    print("逐字显示的效果")
\`\`\`

✅ 如果你看到消息逐字出现，说明流式输出功能正常！

---
测试时间: ${new Date().toLocaleString("zh-CN")}`;

  try {
    await sendStreamingText({
      cfg: config,
      to: "ou_099438b3924bd34e5f9445bc8220a460",  // Leo 的飞书 ID
      fullText: testMessage,
      config: { chunkInterval: 60, chunkSize: 8 }
    });
    console.log("✅ 流式消息已发送！");
  } catch (error) {
    console.error("❌ 错误:", error.message);
  }
}

test();
