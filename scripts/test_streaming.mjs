/**
 * 流式输出测试脚本
 * 运行方式: node d:\桌面\leo_ai_system\scripts\test_streaming.mjs
 */
import fs from "fs";
import { sendStreamingText } from "file:///D:/moltbot/extensions/feishu/dist/src/streaming.js";

async function test() {
  console.log("🚀 开始测试流式输出...\n");

  // 加载配置
  const configPath = "C:\\Users\\刘方林\\.openclaw\\openclaw.json";
  const config = JSON.parse(fs.readFileSync(configPath, "utf-8"));

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
    console.log("📤 发送流式消息中...");
    await sendStreamingText({
      cfg: config,
      to: "ou_099438b3924bd34e5f9445bc8220a460",
      fullText: testMessage,
      config: { chunkInterval: 60, chunkSize: 8 }
    });
    console.log("✅ 流式消息已发送！请查看飞书");
  } catch (error) {
    console.error("❌ 错误:", error.message);
  }
}

test();
